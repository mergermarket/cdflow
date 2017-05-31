import unittest
from hashlib import sha256

from hypothesis import given
from mock import MagicMock

from docker.client import DockerClient
from docker.models.images import Image

from strategies import image_id

from cdflow import get_image_sha


class TestImage(unittest.TestCase):

    @given(image_id())
    def test_get_sha(self, image_id):
        docker_client = MagicMock(spec=DockerClient)

        image_sha = '{}@sha256:{}'.format(
            image_id, sha256(image_id.encode('utf-8')).hexdigest()
        )
        def get_image(image_id):
            image = MagicMock(spec=Image)
            image.attrs = {
                'RepoDigests': [image_sha]
            }
            return image
            
        docker_client.images.pull = get_image

        fetched_image_sha = get_image_sha(docker_client, image_id)

        assert fetched_image_sha == image_sha
        
