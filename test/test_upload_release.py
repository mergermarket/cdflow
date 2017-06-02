import unittest

from hypothesis import given
from hypothesis.strategies import text, fixed_dictionaries
from mock import Mock

from strategies import VALID_ALPHABET

from cdflow import upload_release


class TestUploadRelease(unittest.TestCase):

    @given(fixed_dictionaries({
        'component_name': text(alphabet=VALID_ALPHABET, min_size=1),
        'version': text(alphabet=VALID_ALPHABET, min_size=1),
    }))
    def test_uploads_release_bundle(self, fixtures):
        component_name = fixtures['component_name']
        version = fixtures['version']
        s3_bucket = Mock()

        upload_release(s3_bucket, component_name, version)

        s3_bucket.upload_file.assert_called_once_with(
            'release-{}.zip'.format(version),
            '{}/release-{}.zip'.format(component_name, version),
        )
