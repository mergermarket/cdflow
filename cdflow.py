#!/usr/bin/env python
from __future__ import print_function

from os import environ, path
from io import BytesIO
import json
import sys
import logging
from subprocess import check_output, CalledProcessError
from zipfile import ZipFile

import boto3
import botocore
import docker
from docker.errors import ContainerError


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
    try:
        output = docker_client.containers.run(
            image_id,
            command=command,
            environment=environment_variables,
            remove=True,
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
    except ContainerError as error:
        exit_status = 1
        output = error.stderr
    return exit_status, output


def upload_release(s3_bucket, component_name, version):
    key = _get_release_storage_key(component_name, version)
    s3_bucket.upload_file('release-{}.zip'.format(version), key)


def _command(argv):
    try:
        return argv[0]
    except IndexError:
        pass


def main(argv):
    docker_client = docker.from_env()
    environment_variables = {
        'AWS_ACCESS_KEY_ID': environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_SESSION_TOKEN': environ.get('AWS_SESSION_TOKEN'),
        'FASTLY_API_KEY': environ.get('FASTLY_API_KEY'),
    }
    image_id = CDFLOW_IMAGE_ID
    command = _command(argv)

    if command == 'release':
        image_digest = get_image_sha(docker_client, CDFLOW_IMAGE_ID)
        environment_variables['CDFLOW_IMAGE_DIGEST'] = image_digest
    elif command == 'deploy':
        component_name = get_component_name(argv)
        version = get_version(argv)
        release_metadata = get_release_metadata(
            boto3.resource('s3'), component_name, version
        )
        image_id = release_metadata['cdflow_image_digest']

    exit_status, output = docker_run(
        docker_client, image_id, argv,
        path.abspath(path.curdir), environment_variables
    )

    if command == 'release' and exit_status == 0:
        component_name = get_component_name(argv)
        version = get_version(argv)
        s3_bucket = find_bucket(boto3.resource('s3'))
        upload_release(s3_bucket, component_name, version)

    print(output, file=sys.stderr if exit_status else sys.stdout)
    return exit_status


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
