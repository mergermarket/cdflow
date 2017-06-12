#!/usr/bin/env python
from __future__ import print_function

import atexit
import os
from io import BytesIO
import json
import sys
import logging
from subprocess import check_output, CalledProcessError

from boto3.session import Session
import docker
from docker.errors import DockerException
from requests.exceptions import ReadTimeout
import yaml


CDFLOW_IMAGE_ID = 'mergermarket/cdflow-commands:latest'
MANIFEST_PATH = 'cdflow.yml'


class CDFlowWrapperException(Exception):
    pass


class GitRemoteError(CDFlowWrapperException):
    pass


def fetch_release_metadata(s3_resource, bucket_name, component_name, version):
    key = _get_release_storage_key(component_name, version)
    release_object = s3_resource.Object(bucket_name, key)
    return release_object.metadata


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
        atexit.register(_remove_container, container)
        _print_logs(container)
        return handle_finished_container(container)
    except DockerException as error:
        exit_status = 1
        output = str(error)
    return exit_status, output


def handle_finished_container(container):
    container.reload()
    exit_status = container.attrs['State']['ExitCode']
    output = 'Done'
    if exit_status != 0:
        output = 'Error'
    return exit_status, output


def _print_logs(container):
    for message in container.logs(
        stream=True, follow=True, stdout=True, stderr=True
    ):
        print(message, end='')


def _remove_container(container):
    try:
        container.stop()
    except ReadTimeout:
        pass
    container.remove()


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


def get_account_prefix():
    with open(MANIFEST_PATH) as config_file:
        config = yaml.load(config_file.read())
        return config['account_prefix']


def get_image_id(environment):
    if 'CDFLOW_IMAGE_ID' in environment:
        return environment['CDFLOW_IMAGE_ID']
    return CDFLOW_IMAGE_ID


def find_image_id_from_release(component_name, version):
    session = Session()
    s3_resource = session.resource('s3')
    account_prefix = get_account_prefix()
    account_scheme = fetch_account_scheme(s3_resource, account_prefix)
    release_metadata = fetch_release_metadata(
        s3_resource, account_scheme['release-bucket'], component_name, version
    )
    return release_metadata['cdflow_image_digest']


def fetch_account_scheme(s3_resource, account_prefix):
    s3_object = s3_resource.Object(
        '{}-account-resources'.format(account_prefix), 'account-scheme.json'
    )
    with BytesIO() as f:
        s3_object.download_fileobj(f)
        f.seek(0)
        return json.loads(f.read())


def main(argv):
    docker_client = docker.from_env()
    environment_variables = get_environment()
    image_id = get_image_id(os.environ)
    command = _command(argv)

    if command == 'release':
        image_digest = get_image_sha(docker_client, image_id)
        environment_variables['CDFLOW_IMAGE_DIGEST'] = image_digest
    elif command == 'deploy':
        component_name = get_component_name(argv)
        version = get_version(argv)
        image_id = find_image_id_from_release(component_name, version)

    exit_status, output = docker_run(
        docker_client, image_id, argv,
        os.path.abspath(os.path.curdir), environment_variables
    )

    print(output, file=sys.stderr if exit_status else sys.stdout)
    return exit_status


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
