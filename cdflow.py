#!/usr/bin/env python
from __future__ import print_function

import atexit
import os
from io import BytesIO
import json
import sys
import logging
from subprocess import check_output, CalledProcessError
from zipfile import ZipFile

import botocore
from boto3.session import Session
import docker
from docker.errors import APIError, ContainerError


CDFLOW_IMAGE_ID = 'mergermarket/cdflow-commands:latest'
TAG_NAME = 'cdflow-releases'


class CDFlowWrapperException(Exception):
    pass


class MultipleBucketError(CDFlowWrapperException):
    pass


class MissingBucketError(CDFlowWrapperException):
    pass


class GitRemoteError(CDFlowWrapperException):
    pass


def get_release_metadata(s3_resource, component_name, version):
    s3_bucket = find_bucket(s3_resource)
    zip_archive = get_release_bundle(s3_bucket, component_name, version)
    return extract_release_metadata(zip_archive)


def extract_release_metadata(zip_archive):
    release_file_path = 'release/release.json'
    metadata_file = zip_archive.open(release_file_path)
    raw_metadata = metadata_file.read()
    metadata = json.loads(raw_metadata)
    zip_archive.close()
    return metadata


def get_release_bundle(s3_bucket, component_name, version):
    key = _get_release_storage_key(component_name, version)
    with BytesIO() as fileobj:
        s3_bucket.download_fileobj(key, fileobj)
        release_zip_archive = ZipFile(fileobj)
    return release_zip_archive


def find_bucket(s3_resource):
    buckets = [b for b in s3_resource.buckets.all()]
    tagged_buckets = [b for b in buckets if is_tagged(b, TAG_NAME)]
    if len(tagged_buckets) > 1:
        raise MultipleBucketError
    if len(tagged_buckets) < 1:
        raise MissingBucketError
    return tagged_buckets[0]


def is_tagged(bucket, tag_name):
    for tag in get_bucket_tags(bucket):
        if tag['Key'] == TAG_NAME:
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
        print(message)


def _kill_container(container):
    try:
        container.kill()
    except APIError:
        pass


def upload_release(s3_bucket, component_name, version):
    key = _get_release_storage_key(component_name, version)
    s3_bucket.upload_file('release-{}.zip'.format(version), key)


def get_environment():
    return {
        'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_SESSION_TOKEN': os.environ.get('AWS_SESSION_TOKEN'),
        'FASTLY_API_KEY': os.environ.get('FASTLY_API_KEY'),
        'JOB_NAME': os.environ.get('JOB_NAME'),
        'EMAIL': os.environ.get('EMAIL'),
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


def get_account_id(config_file_path='dev.json'):
    with open(config_file_path) as config_file:
        platform_config = json.loads(config_file.read())
        return platform_config['platform_config']['account_id']


def main(argv):
    docker_client = docker.from_env()
    environment_variables = get_environment()
    image_id = CDFLOW_IMAGE_ID
    command = _command(argv)
    account_id = get_account_id()

    if command == 'release':
        image_digest = get_image_sha(docker_client, CDFLOW_IMAGE_ID)
        environment_variables['CDFLOW_IMAGE_DIGEST'] = image_digest
    elif command == 'deploy':
        component_name = get_component_name(argv)
        version = get_version(argv)
        session = assume_role(
            Session(), account_id, environment_variables['JOB_NAME']
        )
        release_metadata = get_release_metadata(
            session.resource('s3'), component_name, version
        )
        image_id = release_metadata['cdflow_image_digest']

    exit_status, output = docker_run(
        docker_client, image_id, argv,
        os.path.abspath(os.path.curdir), environment_variables
    )

    if command == 'release' and exit_status == 0:
        component_name = get_component_name(argv)
        version = get_version(argv)
        session = assume_role(
            Session(), account_id, environment_variables['JOB_NAME']
        )
        s3_bucket = find_bucket(session.resource('s3'))
        upload_release(s3_bucket, component_name, version)

    print(output, file=sys.stderr if exit_status else sys.stdout)
    return exit_status


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
