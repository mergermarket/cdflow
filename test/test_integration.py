import json
import unittest
from unittest.mock import ANY, MagicMock, Mock, patch
from string import printable
from _io import TextIOWrapper
import logging

import yaml
from docker.client import DockerClient
from docker.errors import ContainerError
from docker.models.images import Image

from cdflow import CDFLOW_IMAGE_ID, main, logger
from hypothesis import given
from hypothesis.strategies import dictionaries, fixed_dictionaries, lists, text

from test.strategies import (
    VALID_ALPHABET, filepath, image_id, s3_bucket_and_key
)


class TestIntegration(unittest.TestCase):

    @given(filepath())
    def test_release(self, project_root):
        argv = ['release', '--platform-config', '../path/to/config',
                '--release-data ami_id=ami-z9876', '42']
        with patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.abspath') as abspath, \
                patch('cdflow.open') as open_:
            abs_path_to_config = '/root/path/to/config'
            abspath.return_value = abs_path_to_config

            image = MagicMock(spec=Image)
            docker.from_env.return_value.images.pull.return_value = image
            image.attrs = {
                'RepoDigests': ['hash']
            }

            docker.from_env.return_value.containers.run.return_value.attrs = {
                'State': {
                    'ExitCode': 0,
                }
            }

            os.getcwd.return_value = project_root
            os.getenv.return_value = False

            config_file = MagicMock(spec=TextIOWrapper)
            config_file.read.return_value = yaml.dump({
                'team': 'a-team'
            })
            open_.return_value.__enter__.return_value = config_file

            exit_status = main(argv)

        assert exit_status == 0

        docker.from_env.assert_called_once()
        docker.from_env.return_value.images.pull.assert_called_once_with(
            'mergermarket/cdflow-commands:latest'
        )
        docker.from_env.return_value.containers.run.assert_called_once_with(
            'mergermarket/cdflow-commands:latest',
            command=argv,
            environment={
                'AWS_ACCESS_KEY_ID': ANY,
                'AWS_SECRET_ACCESS_KEY': ANY,
                'AWS_SESSION_TOKEN': ANY,
                'FASTLY_API_KEY': ANY,
                'GITHUB_TOKEN': ANY,
                'CDFLOW_IMAGE_DIGEST': 'hash',
                'LOGENTRIES_ACCOUNT_KEY': ANY,
                'DATADOG_APP_KEY': ANY,
                'DATADOG_API_KEY': ANY,
            },
            detach=True,
            volumes={
                project_root: {
                    'bind': project_root,
                    'mode': 'rw',
                },
                abs_path_to_config: {
                    'bind': abs_path_to_config,
                    'mode': 'ro',
                },
                '/var/run/docker.sock': {
                    'bind': '/var/run/docker.sock',
                    'mode': 'ro',
                },
            },
            working_dir=project_root
        )

        docker.from_env.return_value.containers.run.return_value.logs.\
            assert_called_once_with(
                stream=True,
                follow=True,
                stdout=True,
                stderr=True,
            )

    @given(fixed_dictionaries({
        'project_root': filepath(),
        'environment': dictionaries(
            keys=text(alphabet=printable, min_size=1, max_size=3),
            values=text(alphabet=printable, min_size=1, max_size=3),
            max_size=3,
        ),
        'image_id': image_id(),
    }))
    def test_release_with_pinned_command_image(self, fixtures):
        argv = ['release', '42', '--platform-config', 'path/to/config']
        project_root = fixtures['project_root']
        environment = fixtures['environment']
        pinned_image_id = fixtures['image_id']
        environment['CDFLOW_IMAGE_ID'] = pinned_image_id

        with patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.abspath') as abspath, \
                patch('cdflow.open') as open_:
            abs_path_to_config = '/root/path/to/config'
            abspath.return_value = abs_path_to_config

            image = MagicMock(spec=Image)
            docker.from_env.return_value.images.pull.return_value = image
            image.attrs = {
                'RepoDigests': ['hash']
            }

            docker.from_env.return_value.containers.run.return_value.attrs = {
                'State': {
                    'ExitCode': 0,
                }
            }

            os.getcwd.return_value = project_root
            os.getenv.return_value = False

            os.environ = environment

            config_file = MagicMock(spec=TextIOWrapper)
            config_file.read.return_value = yaml.dump({
                'team': 'a-team'
            })
            open_.return_value.__enter__.return_value = config_file

            exit_status = main(argv)

        assert exit_status == 0

        docker.from_env.return_value.images.pull.assert_called_once_with(
            pinned_image_id
        )
        docker.from_env.return_value.containers.run.assert_called_once_with(
            pinned_image_id,
            command=argv,
            environment={
                'AWS_ACCESS_KEY_ID': ANY,
                'AWS_SECRET_ACCESS_KEY': ANY,
                'AWS_SESSION_TOKEN': ANY,
                'FASTLY_API_KEY': ANY,
                'GITHUB_TOKEN': ANY,
                'CDFLOW_IMAGE_DIGEST': 'hash',
                'LOGENTRIES_ACCOUNT_KEY': ANY,
                'DATADOG_APP_KEY': ANY,
                'DATADOG_API_KEY': ANY,
            },
            detach=True,
            volumes={
                project_root: {
                    'bind': project_root,
                    'mode': 'rw',
                },
                abs_path_to_config: {
                    'bind': abs_path_to_config,
                    'mode': 'ro',
                },
                '/var/run/docker.sock': {
                    'bind': '/var/run/docker.sock',
                    'mode': 'ro',
                },
            },
            working_dir=project_root
        )

    @given(fixed_dictionaries({
        'project_root': filepath(),
        's3_bucket_and_key': s3_bucket_and_key(),
        'release_bucket': text(
            alphabet=VALID_ALPHABET,
            min_size=3,
            max_size=5,
        ),
    }))
    def test_classic_deploy(self, fixtures):
        argv = ['deploy', 'aslive', '42']

        with patch('cdflow.Session') as Session, \
                patch('cdflow.BytesIO') as BytesIO, \
                patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.open') as open_:

            s3_resource = Mock()

            image_digest = 'sha:12345asdfg'
            s3_resource.Object.return_value.metadata = {
                'cdflow_image_digest': image_digest
            }

            Session.return_value.resource.return_value = s3_resource

            BytesIO.return_value.__enter__.return_value.read.return_value = '''
                {{
                    "release-bucket": "{}",
                    "classic-metadata-handling": true
                }}
            '''.format(fixtures['release_bucket'])

            config_file = MagicMock(spec=TextIOWrapper)
            config_file.read.return_value = yaml.dump({
                'account-scheme-url': 's3://{}/{}'.format(
                    *fixtures['s3_bucket_and_key']
                ),
                'team': 'a-team',
            })
            open_.return_value.__enter__.return_value = config_file

            docker_client = MagicMock(spec=DockerClient)
            docker.from_env.return_value = docker_client
            docker.from_env.return_value.containers.run.return_value.attrs = {
                'State': {
                    'ExitCode': 0,
                }
            }

            project_root = fixtures['project_root']
            os.getcwd.return_value = project_root

            exit_status = main(argv)

            assert exit_status == 0

            s3_resource.Object.assert_any_call(
                fixtures['s3_bucket_and_key'][0],
                fixtures['s3_bucket_and_key'][1],
            )

            docker_client.containers.run.assert_called_once_with(
                image_digest,
                command=argv,
                environment=ANY,
                detach=True,
                volumes={
                    project_root: ANY,
                    '/var/run/docker.sock': ANY
                },
                working_dir=project_root,
            )

            docker.from_env.return_value.containers.run.return_value.logs.\
                assert_called_once_with(
                    stream=True,
                    follow=True,
                    stdout=True,
                    stderr=True,
                )

    @given(fixed_dictionaries({
        'project_root': filepath(),
        's3_bucket_and_key': s3_bucket_and_key(),
        'release_bucket': text(
            alphabet=VALID_ALPHABET,
            min_size=3,
            max_size=5,
        ),
        'team_name': text(
            alphabet=VALID_ALPHABET,
            min_size=3,
            max_size=5,
        ),
        'component_name': text(
            alphabet=VALID_ALPHABET,
            min_size=3,
            max_size=5,
        ),
    }))
    def test_deploy(self, fixtures):
        version = '42'
        component_name = fixtures['component_name']
        argv = ['deploy', 'aslive', version, '--component', component_name]

        with patch('cdflow.Session') as Session, \
                patch('cdflow.BytesIO') as BytesIO, \
                patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.open') as open_:

            s3_resource = Mock()

            image_digest = 'sha:12345asdfg'
            s3_resource.Object.return_value.metadata = {
                'cdflow_image_digest': image_digest
            }

            Session.return_value.resource.return_value = s3_resource

            BytesIO.return_value.__enter__.return_value.read.return_value = '''
                {{
                    "release-bucket": "{}"
                }}
            '''.format(fixtures['release_bucket'])

            config_file = MagicMock(spec=TextIOWrapper)
            config_file.read.return_value = yaml.dump({
                'account-scheme-url': 's3://{}/{}'.format(
                    *fixtures['s3_bucket_and_key']
                ),
                'team': fixtures['team_name'],
            })
            open_.return_value.__enter__.return_value = config_file

            docker_client = MagicMock(spec=DockerClient)
            docker.from_env.return_value = docker_client
            docker.from_env.return_value.containers.run.return_value.attrs = {
                'State': {
                    'ExitCode': 0,
                }
            }

            project_root = fixtures['project_root']
            os.getcwd.return_value = project_root

            exit_status = main(argv)

            assert exit_status == 0

            s3_resource.Object.assert_any_call(
                fixtures['s3_bucket_and_key'][0],
                fixtures['s3_bucket_and_key'][1],
            )

            s3_resource.Object.assert_any_call(
                fixtures['release_bucket'],
                '{}/{}/{}-{}.zip'.format(
                    fixtures['team_name'],
                    component_name,
                    component_name,
                    version,
                ),
            )

            docker_client.containers.run.assert_called_once_with(
                image_digest,
                command=argv,
                environment=ANY,
                detach=True,
                volumes={
                    project_root: ANY,
                    '/var/run/docker.sock': ANY
                },
                working_dir=project_root,
            )

            docker.from_env.return_value.containers.run.return_value.logs.\
                assert_called_once_with(
                    stream=True,
                    follow=True,
                    stdout=True,
                    stderr=True,
                )

    @given(lists(elements=text(alphabet=printable, max_size=3), max_size=3))
    def test_invalid_arguments_passed_to_container_to_handle(self, argv):
        with patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.open') as open_:

            account_id = '1234567890'
            config_file = MagicMock(spec=TextIOWrapper)
            config_file.read.return_value = json.dumps({
                'platform_config': {'account_id': account_id}
            })
            open_.return_value.__enter__.return_value = config_file

            error = ContainerError(
                container=CDFLOW_IMAGE_ID,
                exit_status=1,
                command=argv,
                image=CDFLOW_IMAGE_ID,
                stderr='help text'
            )
            docker.from_env.return_value.containers.run.side_effect = error
            os.path.abspath.return_value = '/'
            exit_status = main(argv)

        assert exit_status == 1

        docker.from_env.return_value.containers.run.assert_called_once_with(
            CDFLOW_IMAGE_ID,
            command=argv,
            environment=ANY,
            detach=True,
            volumes=ANY,
            working_dir=ANY
        )


@patch('cdflow.docker')
@patch('cdflow.os')
@patch('cdflow.abspath')
@patch('cdflow.open')
class TestVerboseLogging(unittest.TestCase):

    def setup_mocks(self, open_, abspath, os, docker):
        config_file = MagicMock(spec=TextIOWrapper)
        config_file.read.return_value = yaml.dump({
            'team': 'a-team'
        })
        open_.return_value.__enter__.return_value = config_file

        abs_path_to_config = '/root/path/to/config'
        abspath.return_value = abs_path_to_config

        image = MagicMock(spec=Image)
        docker.from_env.return_value.images.pull.return_value = image
        image.attrs = {
            'RepoDigests': ['hash']
        }

        docker.from_env.return_value.containers.run.return_value.attrs = {
            'State': {
                'ExitCode': 0,
            }
        }

        os.getcwd.return_value = '/tmp/project'
        os.getenv.return_value = False

    def test_short_flag(self, open_, abspath, os, docker):
        self.setup_mocks(open_, abspath, os, docker)

        argv = [
            'release', '--platform-config', '../path/to/config',
            '-v',
            '--release-data ami_id=ami-z9876', '42',
        ]

        with self.assertLogs(logger, logging.DEBUG) as logs:
            main(argv)

        assert 'DEBUG:cdflow:Debug logging enabled' in logs.output

    def test_long_flag(self, open_, abspath, os, docker):
        self.setup_mocks(open_, abspath, os, docker)

        argv = [
            'release', '--platform-config', '../path/to/config',
            '--verbose',
            '--release-data ami_id=ami-z9876', '42',
        ]

        with self.assertLogs(logger, logging.DEBUG) as logs:
            main(argv)

        assert 'DEBUG:cdflow:Debug logging enabled' in logs.output

    def test_no_flag(self, open_, abspath, os, docker):
        self.setup_mocks(open_, abspath, os, docker)

        argv = [
            'release', '--platform-config', '../path/to/config',
            '--release-data ami_id=ami-z9876', '42',
        ]

        with self.assertLogs(logger, logging.DEBUG) as logs:
            main(argv)

        assert 'DEBUG:cdflow:Debug logging enabled' not in logs.output
