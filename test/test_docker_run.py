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
    }))
    def test_run_args(self, run_arguments):
        docker_client = MagicMock(spec=DockerClient)
        image_id = run_arguments['image_id']
        project_root = run_arguments['project_root']
        environment_variables = run_arguments['environment_variables']
        docker_run(
            docker_client, image_id, project_root, environment_variables
        )

        docker_client.containers.run.assert_called_once_with(
            image_id,
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
