import unittest

from hypothesis import given
from mock import patch, ANY

from strategies import filepath

from cdflow import main


class TestIntegration(unittest.TestCase):

    @given(filepath())
    def test_release(self, project_root):
        argv = ['release', '42']
        with patch('cdflow.docker') as docker, patch('cdflow.path') as path:
            path.abspath.return_value = project_root
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
                'CDFLOW_IMAGE_DIGEST': ANY,
            },
            remove=True,
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
