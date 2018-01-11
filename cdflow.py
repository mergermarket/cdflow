#!/usr/bin/env python
from __future__ import print_function

import atexit
from copy import copy
from contextlib import contextmanager
import json
import logging
import os
import sys
from io import BytesIO
from subprocess import CalledProcessError, check_output

import docker
import yaml
from boto3.session import Session
from docker.errors import DockerException, ImageNotFound
from requests.exceptions import ReadTimeout

CDFLOW_IMAGE_ID = 'mergermarket/cdflow-commands:latest'
MANIFEST_PATH = 'cdflow.yml'


logging.basicConfig(format='[%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CDFlowWrapperException(Exception):
    def __str__(self):
        return self.message or self.__class__.message


class GitRemoteError(CDFlowWrapperException):
    pass


class InvalidURLError(CDFlowWrapperException):
    pass


class MissingPlatformConfigError(CDFlowWrapperException):
    message = 'error: --platform-config parameter is required'


def fetch_release_metadata(s3_resource, bucket_name, component_name, version):
    key = _get_release_storage_key(component_name, version)
    release_object = s3_resource.Object(bucket_name, key)
    return release_object.metadata


def get_version(argv):
    local_argv = remove_argv_options(argv)
    command = local_argv[0]
    if command == 'deploy':
        version_index = 2
    elif command == 'release':
        version_index = 1
    try:
        return local_argv[version_index]
    except IndexError:
        pass


def remove_argv_options(argv):
    local_argv = copy(argv)
    for flag in ('-p', '-v', '--plan-only', '--verbose'):
        with _suppress(ValueError):
            local_argv.remove(flag)
    for option in ('-c', '--component', '--platform-config'):
        with _suppress(ValueError):
            option_index = local_argv.index(option)
            del local_argv[option_index:option_index+2]
    return local_argv


@contextmanager
def _suppress(*exceptions):
    try:
        yield
    except tuple(exceptions):
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
            component_flag_index = argv.index(flag)
        except ValueError:
            pass
    if component_flag_index > -1:
        return argv[component_flag_index + 1]


def _get_component_name_from_git_remote():
    try:
        remote = check_output(['git', 'config', 'remote.origin.url'])
    except CalledProcessError:
        raise GitRemoteError(
            'error: could not get remote from git repo '
            ' (git config remote.origin.url)'
        )
    name = remote.decode('utf-8').strip('\t\n /').split('/')[-1]
    if name.endswith('.git'):
        return name[:-4]
    return name


def _get_platform_config_path_arg(iterator):
    try:
        return next(iterator)
    except StopIteration:
        raise MissingPlatformConfigError()


def get_platform_config_paths(argv):
    paths = []
    iterator = iter(argv)
    for arg in iterator:
        if arg == '--platform-config':
            paths.append(_get_platform_config_path_arg(iterator))
        elif arg.startswith('--platform-config='):
            paths.append(arg.split('=', 1)[1])
    if len(paths) == 0:
        raise MissingPlatformConfigError()
    return paths


def _get_release_storage_key(component_name, version):
    return '{}/{}-{}.zip'.format(component_name, component_name, version)


def get_image_sha(docker_client, image_id):
    if os.getenv('CDFLOW_NO_IMAGE_PULL', False):
        image = docker_client.images.get(image_id)
    else:
        logger.info('Pulling image {}'.format(image_id))
        try:
            image = docker_client.images.pull(image_id)
        except ImageNotFound as e:
            logger.exception(e)
            image = docker_client.images.get(image_id)
    digests = image.attrs['RepoDigests']
    return digests[0] if len(digests) else image_id


def docker_run(
    docker_client, image_id, command, project_root,
    environment_variables, platform_config_paths=[],
):
    exit_status = 0
    output = 'Done'
    try:
        volumes = {
            project_root: {
                'bind': project_root,
                'mode': 'rw',
            },
            '/var/run/docker.sock': {
                'bind': '/var/run/docker.sock',
                'mode': 'ro',
            }
        }
        for platform_config_path in platform_config_paths:
            volumes[platform_config_path] = {
                'bind': platform_config_path,
                'mode': 'ro',
            }
        container = docker_client.containers.run(
            image_id,
            command=command,
            environment=environment_variables,
            detach=True,
            volumes=volumes,
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
    output = ''
    if exit_status != 0:
        output = ''
    return exit_status, output


def _print_logs(container):
    for message in container.logs(
        stream=True, follow=True, stdout=True, stderr=True
    ):
        print(message.decode('utf-8'), end='')


def _remove_container(container):
    try:
        container.stop()
    # An HTTP timeout is thrown until this issue is addressed, then we can
    # stop catching any exception:
    # https://github.com/docker/docker-py/issues/1374
    except ReadTimeout:
        pass
    container.remove()


def get_environment():
    return {
        'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_SESSION_TOKEN': os.environ.get('AWS_SESSION_TOKEN'),
        'FASTLY_API_KEY': os.environ.get('FASTLY_API_KEY'),
        'LOGENTRIES_ACCOUNT_KEY': os.environ.get('LOGENTRIES_ACCOUNT_KEY'),
        'DATADOG_APP_KEY': os.environ.get('DATADOG_APP_KEY'),
        'DATADOG_API_KEY': os.environ.get('DATADOG_API_KEY'),
    }


def _command(argv):
    try:
        return argv[0]
    except IndexError:
        pass


def get_account_scheme_url():
    with open(MANIFEST_PATH) as config_file:
        config = yaml.load(config_file.read())
        return config['account-scheme-url']


def get_image_id(environment):
    if 'CDFLOW_IMAGE_ID' in environment:
        return environment['CDFLOW_IMAGE_ID']
    return CDFLOW_IMAGE_ID


def find_image_id_from_release(component_name, version):
    session = Session()
    s3_resource = session.resource('s3')
    account_scheme_url = get_account_scheme_url()
    bucket, key = parse_s3_url(account_scheme_url)
    account_scheme = fetch_account_scheme(s3_resource, bucket, key)
    release_metadata = fetch_release_metadata(
        s3_resource, account_scheme['release-bucket'], component_name, version
    )
    return release_metadata['cdflow_image_digest']


def parse_s3_url(s3_url):
    if not s3_url.startswith('s3://'):
        raise InvalidURLError('URL must start with s3://')
    bucket_and_key = s3_url[5:].split('/', 1)
    if len(bucket_and_key) != 2:
        raise InvalidURLError('URL must contain a bucket and a key')
    return bucket_and_key


def fetch_account_scheme(s3_resource, bucket, key):
    s3_object = s3_resource.Object(bucket, key)
    with BytesIO() as f:
        s3_object.download_fileobj(f)
        f.seek(0)
        return json.loads(f.read())


def main(argv):
    docker_client = docker.from_env()
    environment_variables = get_environment()
    image_id = get_image_id(os.environ)
    command = _command(argv)

    kwargs = {
        'docker_client': docker_client,
        'image_id': image_id,
        'command': argv,
        'project_root': os.getcwd(),
        'environment_variables': environment_variables,
    }

    try:
        if command == 'release':
            image_digest = get_image_sha(docker_client, image_id)
            environment_variables['CDFLOW_IMAGE_DIGEST'] = image_digest
            kwargs['platform_config_paths'] = [
                os.path.abspath(path)
                for path in get_platform_config_paths(argv)
            ]
        elif command == 'deploy':
            component_name = get_component_name(argv)
            version = get_version(argv)
            kwargs['image_id'] = find_image_id_from_release(
                component_name, version
            )
    except CDFlowWrapperException as e:
        print(str(e), file=sys.stderr)
        return 1

    exit_status, output = docker_run(**kwargs)

    print(output, file=sys.stderr if exit_status else sys.stdout)
    return exit_status


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
