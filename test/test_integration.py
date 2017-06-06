import unittest
import io
import json
from zipfile import ZipFile
from string import printable

from hypothesis import given
from hypothesis.strategies import lists, text
from mock import patch, ANY, MagicMock, Mock

from docker.client import DockerClient
from docker.errors import ContainerError
from docker.models.images import Image

from strategies import filepath

from cdflow import main, TAG_NAME, CDFLOW_IMAGE_ID


class TestIntegration(unittest.TestCase):

    @given(filepath())
    def test_release(self, project_root):
        argv = ['release', '42']
        with patch('cdflow.Session') as Session, \
                patch('cdflow.check_output') as check_output, \
                patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.open') as open_:

            image = MagicMock(spec=Image)
            docker.from_env.return_value.images.pull.return_value = image
            image.attrs = {
                'RepoDigests': ['hash']
            }

            os.path.abspath.return_value = project_root

            Session.return_value.client.return_value.assume_role.\
                return_value = {
                    'Credentials': {
                        'AccessKeyId': 'foo',
                        'SecretAccessKey': 'bar',
                        'SessionToken': 'baz',
                    }
                }

            s3_resource = Mock()
            s3_bucket = Mock()
            s3_bucket.Tagging.return_value.tag_set = [
                {'Key': TAG_NAME, 'Value': 'true'}
            ]

            s3_resource.buckets.all.return_value = [
                s3_bucket
            ]
            Session.return_value.resource.return_value = s3_resource

            check_output.return_value = \
                'git@github.com:organisation/dummy-component.git'

            account_id = "1234567890"
            config_file = MagicMock(spec=file)
            config_file.read.return_value = json.dumps({
                'platform_config': {'account_id': account_id}
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
            command=['release', '42'],
            environment={
                'AWS_ACCESS_KEY_ID': ANY,
                'AWS_SECRET_ACCESS_KEY': ANY,
                'AWS_SESSION_TOKEN': ANY,
                'FASTLY_API_KEY': ANY,
                'ROLE_SESSION_NAME': ANY,
                'CDFLOW_IMAGE_DIGEST': 'hash',
            },
            detach=True,
            volumes={
                project_root: {
                    'bind': project_root,
                    'mode': 'rw',
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

        s3_bucket.upload_file.assert_called_once_with(
            'release-42.zip',
            'dummy-component/release-42.zip',
        )

    def test_release_fail_does_not_call_upload(self):
        argv = ['release', 'something']

        with patch('cdflow.Session') as Session, \
                patch('cdflow.check_output') as check_output, \
                patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.open') as open_:

            image = MagicMock(spec=Image)
            docker.from_env.return_value.images.pull.return_value = image
            image.attrs = {
                'RepoDigests': ['hash']
            }

            os.path.abspath.return_value = '/'

            Session.return_value.client.return_value.assume_role.\
                return_value = {
                    'Credentials': {
                        'AccessKeyId': 'foo',
                        'SecretAccessKey': 'bar',
                        'SessionToken': 'baz',
                    }
                }

            s3_resource = Mock()
            s3_bucket = Mock()
            s3_bucket.Tagging.return_value.tag_set = [
                {'Key': TAG_NAME, 'Value': 'true'}
            ]

            s3_resource.buckets.all.return_value = [
                s3_bucket
            ]
            Session.return_value.resource.return_value = s3_resource

            check_output.return_value = \
                'git@github.com:organisation/dummy-component.git'

            account_id = "1234567890"
            config_file = MagicMock(spec=file)
            config_file.read.return_value = json.dumps({
                'platform_config': {'account_id': account_id}
            })
            open_.return_value.__enter__.return_value = config_file

            error = ContainerError(
                container=CDFLOW_IMAGE_ID,
                exit_status=1,
                command=argv,
                image=CDFLOW_IMAGE_ID,
                stderr='something went wrong'
            )
            docker.from_env.return_value.containers.run.side_effect = error

            exit_status = main(argv)

        assert exit_status == 1

        s3_bucket.upload_file.assert_not_called()

    @given(filepath())
    def test_deploy(self, project_root):
        argv = ['deploy', 'aslive', '42']

        with patch('cdflow.Session') as Session, \
                patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.open') as open_, \
                patch('cdflow.BytesIO') as BytesIO:

            s3_resource = Mock()
            s3_bucket = Mock()
            s3_bucket.Tagging.return_value.tag_set = [
                {'Key': TAG_NAME, 'Value': 'true'}
            ]

            image_digest = 'sha:12345asdfg'
            release_archive = io.BytesIO()
            release_archive_zip = ZipFile(release_archive, 'w')
            release_archive_zip.writestr(
                'release/release.json',
                '{{"cdflow_image_digest": "{}"}}'.format(image_digest)
            )
            release_archive_zip.close()
            release_archive.seek(0)

            BytesIO.return_value.__enter__.return_value = release_archive

            Session.return_value.client.return_value.assume_role.\
                return_value = {
                    'Credentials': {
                        'AccessKeyId': 'foo',
                        'SecretAccessKey': 'bar',
                        'SessionToken': 'baz',
                    }
                }

            s3_resource.buckets.all.return_value = [
                s3_bucket
            ]
            Session.return_value.resource.return_value = s3_resource

            account_id = "1234567890"
            config_file = MagicMock(spec=file)
            config_file.read.return_value = json.dumps({
                'platform_config': {'account_id': account_id}
            })
            open_.return_value.__enter__.return_value = config_file

            docker_client = MagicMock(spec=DockerClient)
            docker.from_env.return_value = docker_client

            os.path.abspath.return_value = project_root

            exit_status = main(argv)

            assert exit_status == 0

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

    @given(lists(elements=text(alphabet=printable)))
    def test_invalid_arguments_passed_to_container_to_handle(self, argv):
        with patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.open') as open_:

            account_id = "1234567890"
            config_file = MagicMock(spec=file)
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

    @given(filepath())
    def test_get_account_id(self, project_root):
        argv = ['release', '42']
        with patch('cdflow.Session') as Session, \
                patch('cdflow.check_output') as check_output, \
                patch('cdflow.docker') as docker, \
                patch('cdflow.os') as os, \
                patch('cdflow.open') as open_:

            image = MagicMock(spec=Image)
            docker.from_env.return_value.images.pull.return_value = image
            image.attrs = {
                'RepoDigests': ['hash']
            }

            os.path.abspath.return_value = project_root

            Session.return_value.client.return_value.assume_role.\
                return_value = {
                    'Credentials': {
                        'AccessKeyId': 'foo',
                        'SecretAccessKey': 'bar',
                        'SessionToken': 'baz',
                    }
                }

            s3_resource = Mock()
            s3_bucket = Mock()
            s3_bucket.Tagging.return_value.tag_set = [
                {'Key': TAG_NAME, 'Value': 'true'}
            ]

            s3_resource.buckets.all.return_value = [
                s3_bucket
            ]
            Session.return_value.resource.return_value = s3_resource

            check_output.return_value = \
                'git@github.com:organisation/dummy-component.git'

            account_id = "1234567890"
            config_file = MagicMock(spec=file)
            config_file.read.return_value = json.dumps({
                'platform_config': {'account_id': account_id}
            })
            open_.return_value.__enter__.return_value = config_file

            exit_status = main(argv)

        assert exit_status == 0

        Session.return_value.client.return_value.assume_role.\
            assert_called_once_with(
                RoleArn='arn:aws:iam::{}:role/admin'.format(account_id),
                RoleSessionName=ANY,
            )
