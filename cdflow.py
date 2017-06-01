#!/usr/bin/env python
from __future__ import print_function

from os import environ, path
import sys
import logging

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

logger = logging.getLogger(__name__)


def get_image_sha(docker_client, image_id):
    logger.info('Pulling image', image_id)
    image = docker_client.images.pull(image_id)
    return image.attrs['RepoDigests'][0]


def docker_run(
    docker_client, image_id, command, project_root, environment_variables
):
    return docker_client.containers.run(
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


def main(argv):
    docker_client = docker.from_env()
    image_digest = get_image_sha(docker_client, CDFLOW_IMAGE_ID)
    environment_variables = {
        'AWS_ACCESS_KEY_ID': environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_SESSION_TOKEN': environ.get('AWS_SESSION_TOKEN'),
        'FASTLY_API_KEY': environ.get('FASTLY_API_KEY'),
        'CDFLOW_IMAGE_DIGEST': environ.get('CDFLOW_IMAGE_DIGEST'),
    }
    print(docker_run(
        docker_client, CDFLOW_IMAGE_ID, argv,
        path.abspath(path.curdir), environment_variables
    ))


if __name__ == '__main__':
    main(sys.argv[1:])
