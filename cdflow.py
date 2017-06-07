#!/usr/bin/env python
from __future__ import print_function

import atexit
import os
from io import BytesIO
import sys
import logging
from subprocess import check_output, CalledProcessError

import botocore
from boto3.session import Session
import docker
from docker.errors import APIError, ContainerError
import yaml


CDFLOW_IMAGE_ID = 'mergermarket/cdflow-commands:latest'
RELEASES_TAG_NAME = 'cdflow-releases'
ACCOUNT_MAPPING_TAG_NAME = 'account_mapping'
MANIFEST_PATH = 'cdflow.yml'


class CDFlowWrapperException(Exception):
    pass


class MultipleBucketError(CDFlowWrapperException):
    pass


class MissingBucketError(CDFlowWrapperException):
    pass


class GitRemoteError(CDFlowWrapperException):
    pass


def get_release_metadata(s3_resource, component_name, version):
    s3_bucket = find_bucket(s3_resource, RELEASES_TAG_NAME)
    return fetch_release_metadata(
        s3_resource, s3_bucket.name, component_name, version
    )


def fetch_release_metadata(s3_resource, bucket_name, component_name, version):
    key = _get_release_storage_key(component_name, version)
    release_object = s3_resource.Object(bucket_name, key)
    return release_object.metadata


def find_bucket(s3_resource, tag_name):
    buckets = [b for b in s3_resource.buckets.all()]
    tagged_buckets = [b for b in buckets if is_tagged(b, tag_name)]
    if len(tagged_buckets) > 1:
        raise MultipleBucketError
    if len(tagged_buckets) < 1:
        raise MissingBucketError
    return tagged_buckets[0]


def is_tagged(bucket, tag_name):
    for tag in get_bucket_tags(bucket):
        if tag['Key'] == tag_name:
            return True
    return False


def get_bucket_tags(bucket):
    try:
        return bucket.Tagging().tag_set
    except botocore.exceptions.ClientError:
        return []


def get_version(argv):
    command = argv[0]
    if command == 'deploy':
        version_index = 2
    elif command == 'release':
        version_index = 1
    try:
        return argv[version_index]
    except IndexError:
        pass


def get_component_name(argv):
    component_name = _get_component_name_from_cli_args(argv)
    if component_name:
        return component_name
    else:
        return _get_component_name_from_git_remote()


def _get_component_name_from_cli_args(argv):
    component_flag_index = None
    for flag in ('-c', '--component'):
        try:
            component_flag_index = argv.index('-c')
        except ValueError:
            pass
    if component_flag_index > -1:
        return argv[component_flag_index + 1]


def _get_component_name_from_git_remote():
    try:
        remote = check_output(['git', 'config', 'remote.origin.url'])
    except CalledProcessError:
        raise GitRemoteError
    name = remote.decode('utf-8').strip('\t\n /').split('/')[-1]
    if name.endswith('.git'):
        return name[:-4]
    return name


def _get_release_storage_key(component_name, version):
    return '{}/release-{}.zip'.format(component_name, version)


def get_image_sha(docker_client, image_id):
    logging.info('Pulling image', image_id)
    image = docker_client.images.pull(image_id)
    return image.attrs['RepoDigests'][0]


def docker_run(
    docker_client, image_id, command, project_root, environment_variables
):
    exit_status = 0
    output = 'Done'
    try:
        container = docker_client.containers.run(
            image_id,
            command=command,
            environment=environment_variables,
            detach=True,
            volumes={
                project_root: {
                    'bind': project_root,
                    'mode': 'rw',
                },
                '/var/run/docker.sock': {
                    'bind': '/var/run/docker.sock',
                    'mode': 'ro',
                }
            },
            working_dir=project_root,
        )
        atexit.register(_kill_container, container)
        _print_logs(container)
    except ContainerError as error:
        exit_status = 1
        output = error.stderr
    return exit_status, output


def _print_logs(container):
    for message in container.logs(
        stream=True, follow=True, stdout=True, stderr=True
    ):
        print(message, end='')


def _kill_container(container):
    try:
        container.kill()
    except APIError:
        pass


def get_environment():
    return {
        'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_SESSION_TOKEN': os.environ.get('AWS_SESSION_TOKEN'),
        'FASTLY_API_KEY': os.environ.get('FASTLY_API_KEY'),
        'ROLE_SESSION_NAME': os.environ.get('ROLE_SESSION_NAME'),
    }


def _command(argv):
    try:
        return argv[0]
    except IndexError:
        pass


def assume_role(root_session, account_id, session_name):
    sts = root_session.client('sts')
    response = sts.assume_role(
        RoleArn='arn:aws:iam::{}:role/admin'.format(account_id),
        RoleSessionName=session_name,
    )
    return Session(
        response['Credentials']['AccessKeyId'],
        response['Credentials']['SecretAccessKey'],
        response['Credentials']['SessionToken'],
        root_session.region_name,
    )


def get_account_prefix():
    with open(MANIFEST_PATH) as config_file:
        config = yaml.load(config_file.read())
        return config['account_prefix']


def get_account_id(s3_bucket):
    account_prefix = get_account_prefix()
    with BytesIO() as f:
        s3_bucket.download_fileobj('{}dev'.format(account_prefix), f)
        f.seek(0)
        return f.read()


def find_image_id_from_release(component_name, version, role_session_name):
    root_session = Session()
    s3_bucket = find_bucket(
        root_session.resource('s3'), ACCOUNT_MAPPING_TAG_NAME
    )
    account_id = get_account_id(s3_bucket)
    session = assume_role(root_session, account_id, role_session_name)
    release_metadata = get_release_metadata(
        session.resource('s3'), component_name, version
    )
    return release_metadata['cdflow_image_digest']


def main(argv):
    docker_client = docker.from_env()
    environment_variables = get_environment()
    image_id = CDFLOW_IMAGE_ID
    command = _command(argv)

    if command == 'release':
        image_digest = get_image_sha(docker_client, CDFLOW_IMAGE_ID)
        environment_variables['CDFLOW_IMAGE_DIGEST'] = image_digest
    elif command == 'deploy':
        component_name = get_component_name(argv)
        version = get_version(argv)
        image_id = find_image_id_from_release(
            component_name, version, environment_variables['ROLE_SESSION_NAME']
        )

    exit_status, output = docker_run(
        docker_client, image_id, argv,
        os.path.abspath(os.path.curdir), environment_variables
    )

    print(output, file=sys.stderr if exit_status else sys.stdout)
    return exit_status


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
