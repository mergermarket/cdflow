#!/usr/bin/env python
from __future__ import print_function

import atexit
from copy import copy
from contextlib import contextmanager
import json
import logging
import os
from os.path import abspath
import sys
from io import BytesIO
from subprocess import CalledProcessError, check_output

import docker
import dockerpty
import yaml
from boto3.session import Session
from docker.errors import DockerException, ImageNotFound
from requests.exceptions import ReadTimeout

CDFLOW_IMAGE_NAME = 'mergermarket/cdflow-commands'
CDFLOW_IMAGE_TAG = 'latest'
CDFLOW_IMAGE_ID = '{}:{}'.format(CDFLOW_IMAGE_NAME, CDFLOW_IMAGE_TAG)

MANIFEST_PATH = 'cdflow.yml'

logging.basicConfig(format='[%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def toggle_verbose_logging(argv):
    if {'-v', '--verbose'} & set(argv):
        logger.setLevel(logging.DEBUG)
        logger.debug('Debug logging enabled')


class CDFlowWrapperException(Exception):
    def __str__(self):
        return self.message or self.__class__.message


class GitRemoteError(CDFlowWrapperException):
    pass


class InvalidURLError(CDFlowWrapperException):
    pass


class MissingPlatformConfigError(CDFlowWrapperException):
    message = 'error: --platform-config parameter is required'


def fetch_release_metadata(
    s3_resource, bucket_name, component_name, version, team_name=None,
):
    if team_name:
        key = _get_release_storage_key(team_name, component_name, version)
    else:
        key = _get_release_storage_key_classic(component_name, version)
    logger.debug(
        'Getting metadata on {} from {} bucket'.format(key, bucket_name)
    )
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
    component_flag_index = -1
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
            paths.append(abspath(_get_platform_config_path_arg(iterator)))
        elif arg.startswith('--platform-config='):
            paths.append(abspath(arg.split('=', 1)[1]))
    if len(paths) == 0:
        raise MissingPlatformConfigError()
    return paths


def _get_release_storage_key_classic(component_name, version):
    return '{}/{}-{}.zip'.format(component_name, component_name, version)


def _get_release_storage_key(team_name, component_name, version):
    return '{}/{}/{}-{}.zip'.format(
        team_name, component_name, component_name, version
    )


def get_image_sha(docker_client, image_id):
    logger.info('Pulling image {}'.format(image_id))
    try:
        image = docker_client.images.pull(image_id)
    except ImageNotFound as e:
        logger.debug(e)
        logger.info(
            'Could not pull image {}, trying to get it locally'.format(
                image_id,
            )
        )
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
        if _command(command) == 'shell':
            columns = int(check_output(['tput', 'cols']))
            lines = int(check_output(['tput', 'lines']))
            environment_variables['COLUMNS'] = columns
            environment_variables['LINES'] = lines
            container = docker_client.containers.create(
                image_id,
                command=command,
                environment=environment_variables,
                volumes=volumes,
                working_dir=project_root,
                tty=True,
                stdin_open=True,
            )
            dockerpty.start(docker_client.api, container.id)
            output = 'Shell end'
        else:
            container = docker_client.containers.run(
                image_id,
                command=command,
                environment=environment_variables,
                detach=True,
                volumes=volumes,
                working_dir=project_root,
            )
            _print_logs(container)
            return handle_finished_container(container)
    except DockerException as error:
        exit_status = 1
        output = str(error)
    return exit_status, output


def handle_finished_container(container):
    atexit.register(_remove_container, container)
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
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN'),
        'LOGENTRIES_ACCOUNT_KEY': os.environ.get('LOGENTRIES_ACCOUNT_KEY'),
        'DATADOG_APP_KEY': os.environ.get('DATADOG_APP_KEY'),
        'DATADOG_API_KEY': os.environ.get('DATADOG_API_KEY'),
    }


def _command(argv):
    try:
        return argv[0]
    except IndexError:
        pass


def get_manifest_data():
    if not os.path.exists(MANIFEST_PATH):
        return {}

    with open(MANIFEST_PATH) as config_file:
        return yaml.safe_load(config_file.read())


def get_image_id(environment, config):
    if 'CDFLOW_IMAGE_ID' in environment:
        return environment['CDFLOW_IMAGE_ID']

    if 'terraform-version' in config:
        return "{}:terraform{}".format(
            CDFLOW_IMAGE_NAME,
            config['terraform-version']
        )

    return CDFLOW_IMAGE_ID


def find_image_id_from_release(component_name, version, config):
    session = Session()
    s3_resource = session.resource('s3')
    account_scheme_url = config['account-scheme-url']
    bucket, key = parse_s3_url(account_scheme_url)
    team = config['team']
    account_scheme = fetch_account_scheme(
        s3_resource, bucket, key, team, component_name,
    )
    kwargs = {}
    if not account_scheme.get('classic-metadata-handling'):
        kwargs['team_name'] = team
    release_metadata = fetch_release_metadata(
        s3_resource, account_scheme['release-bucket'], component_name, version,
        **kwargs
    )
    return release_metadata['cdflow_image_digest']


def parse_s3_url(s3_url):
    if not s3_url.startswith('s3://'):
        raise InvalidURLError('URL must start with s3://')
    bucket_and_key = s3_url[5:].split('/', 1)
    if len(bucket_and_key) != 2:
        raise InvalidURLError('URL must contain a bucket and a key')
    return bucket_and_key


def download_json_from_s3(s3_resource, bucket, key):
    s3_object = s3_resource.Object(bucket, key)
    with BytesIO() as f:
        s3_object.download_fileobj(f)
        f.seek(0)
        return json.loads(f.read())


def fetch_account_scheme(s3_resource, bucket, key, team, component):
    account_scheme = download_json_from_s3(s3_resource, bucket, key)
    upgrade = account_scheme.get('upgrade-account-scheme')

    def whitelisted(team, component):
        team_whitelist = upgrade.get('team-whitelist', [])
        component_whitelist = upgrade.get('component-whitelist', [])
        logger.debug(
            'Checking whitelists: {}, {}'.format(
                team_whitelist, component_whitelist,
            )
        )
        return team in team_whitelist or component in component_whitelist

    component_flag_passed = _get_component_name_from_cli_args(sys.argv)

    if not component_flag_passed and upgrade and whitelisted(team, component):
        bucket, key = parse_s3_url(upgrade['new-url'])
        logger.debug(
            'Account scheme forwarded, fetching from {}/{}'.format(
                bucket, key,
            )
        )
        account_scheme = download_json_from_s3(s3_resource, bucket, key)

    return account_scheme


def get_deploy_image_id(argv, config):
    component_name = get_component_name(argv)
    version = get_version(argv)
    return find_image_id_from_release(
        component_name, version, config
    )


def main(argv):
    toggle_verbose_logging(argv)
    docker_client = docker.from_env()
    environment_variables = get_environment()
    config = get_manifest_data()
    image_id = get_image_id(os.environ, config)
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
            kwargs['platform_config_paths'] = get_platform_config_paths(argv)
            environment_variables['CDFLOW_IMAGE_DIGEST'] = \
                get_image_sha(docker_client, image_id)
        elif command == 'deploy':
            kwargs['image_id'] = get_deploy_image_id(argv, config)
    except CDFlowWrapperException as e:
        print(str(e), file=sys.stderr)
        return 1

    exit_status, output = docker_run(**kwargs)

    print(output, file=sys.stderr if exit_status else sys.stdout)
    return exit_status


def run():
    sys.exit(main(sys.argv[1:]))


if __name__ == '__main__':
    run()
