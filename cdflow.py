#!/usr/bin/env python
from __future__ import print_function

from os import environ, path
import sys
import logging
from subprocess import check_output

import docker

"""
Release:
    Find immutable reference to latest version?
    Run docker with latest cdflow-commands

*:
    Get component name
    Get version
    Find bucket
    Download release
    Unpack release
    Read cdflow-commands image version
    Run docker
"""

CDFLOW_IMAGE_ID = 'mergermarket/cdflow-commands:latest'


def get_component_name(argv):
    component_flag_index = None
    for flag in ('-c', '--component'):
        try:
            component_flag_index = argv.index('-c')
        except ValueError:
            pass
    if component_flag_index > -1:
        return argv[component_flag_index + 1]
    else:
         return _get_component_name_from_git_remote()


def _get_component_name_from_git_remote():
    try:
        remote = check_output(['git', 'config', 'remote.origin.url'])
    except CalledProcessError:
        raise NoGitRemoteError()
    name = remote.decode('utf-8').strip('\t\n /').split('/')[-1]
    if name.endswith('.git'):
        return name[:-4]
    return name


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
    except docker.errors.ContainerError as error:
        exit_status = 1
        output = error.stderr
    return exit_status, output


def main(argv):
    docker_client = docker.from_env()
    image_digest = get_image_sha(docker_client, CDFLOW_IMAGE_ID)
    environment_variables = {
        'AWS_ACCESS_KEY_ID': environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_SESSION_TOKEN': environ.get('AWS_SESSION_TOKEN'),
        'FASTLY_API_KEY': environ.get('FASTLY_API_KEY'),
        'CDFLOW_IMAGE_DIGEST': image_digest,
    }
    exit_status, output = docker_run(
        docker_client, CDFLOW_IMAGE_ID, argv,
        path.abspath(path.curdir), environment_variables
    )
    print(output)
    return exit_status


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
