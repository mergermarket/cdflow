import unittest 
from string import printable, ascii_letters, digits

from mock import MagicMock
from hypothesis import given
from hypothesis.strategies import composite, lists, text, fixed_dictionaries
from docker.client import DockerClient

from cdflow import docker_run
from strategies import image_id, filepath


class TestDockerRun(unittest.TestCase):

    @given(fixed_dictionaries({
        'environment_variables': fixed_dictionaries({
            'AWS_ACCESS_KEY_ID': text(alphabet=printable, min_size=10),
            'AWS_SECRET_ACCESS_KEY': text(alphabet=printable, min_size=10),
            'AWS_SESSION_TOKEN': text(alphabet=printable, min_size=10),
            'FASTLY_API_KEY': text(alphabet=printable, min_size=10),
            'CDFLOW_IMAGE_DIGEST': text(min_size=12),
        }),
        'image_id': image_id(),
        'project_root': filepath(),
        'command': lists(text(alphabet=printable)),
    }))
    def test_run_args(self, fixtures):
        docker_client = MagicMock(spec=DockerClient)
        docker_client.containers.run.return_value = 'docker output'
        image_id = fixtures['image_id']
        command = fixtures['command']
        project_root = fixtures['project_root']
        environment_variables = fixtures['environment_variables']
        output = docker_run(
            docker_client,
            image_id,
            command,
            project_root,
            environment_variables
        )

        assert output == docker_client.containers.run.return_value

        docker_client.containers.run.assert_called_once_with(
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
                },
            },
            working_dir=project_root,
        )
