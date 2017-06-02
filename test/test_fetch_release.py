import unittest

from string import ascii_letters, digits
import json

from hypothesis import given
from hypothesis.strategies import text, fixed_dictionaries
from mock import patch, Mock, ANY, PropertyMock

from botocore.exceptions import ClientError

from cdflow import (
    get_component_name, get_version, find_bucket, get_release_bundle,
    extract_release_metadata, TAG_NAME, MultipleBucketError, MissingBucketError
)


VALID_ALPHABET = ascii_letters + digits + '-._'


class TestGetComponentName(unittest.TestCase):

    def setUp(self):
        self.argv = ['deploy', '42']

    @given(text(
        alphabet=VALID_ALPHABET, min_size=1, max_size=100
    ))
    def test_get_component_name_passed_in(self, component_name):
        argv = ['deploy', '42', '-c', component_name]
        component_name = get_component_name(argv)

        assert component_name == component_name

    @given(text(
        alphabet=VALID_ALPHABET, min_size=1, max_size=100
    ))
    def test_get_component_name_passed_in_with_long_flag(self, component_name):
        argv = ['deploy', '42', '--component', component_name]
        component_name = get_component_name(argv)

        assert component_name == component_name

    @given(text(
        alphabet=VALID_ALPHABET, min_size=1, max_size=100
    ))
    def test_component_not_passed_as_argument(self, component_name):
        with patch('cdflow.check_output') as check_output:
            check_output.return_value = 'git@github.com:org/{}.git\n'.format(
                component_name
            )
            extraced_component_name = get_component_name(self.argv)

            assert extraced_component_name == component_name

    @given(text(
        alphabet=VALID_ALPHABET, min_size=1, max_size=100
    ))
    def test_component_not_passed_as_argument_without_extension(
        self, component_name
    ):
        with patch('cdflow.check_output') as check_output:
            check_output.return_value = 'git@github.com:org/{}\n'.format(
                component_name
            )
            extraced_component_name = get_component_name(self.argv)

            assert extraced_component_name == component_name

    @given(text(
        alphabet=VALID_ALPHABET, min_size=1, max_size=100
    ))
    def test_component_not_passed_as_argument_with_backslash(
        self, component_name
    ):
        with patch('cdflow.check_output') as check_output:
            check_output.return_value = 'git@github.com:org/{}/\n'.format(
                component_name
            )
            extraced_component_name = get_component_name(self.argv)

            assert extraced_component_name == component_name

    @given(text(
        alphabet=VALID_ALPHABET, min_size=1, max_size=100
    ))
    def test_component_not_passed_as_argument_with_https_origin(
        self, component_name
    ):
        with patch('cdflow.check_output') as check_output:
            repo_template = 'https://github.com/org/{}.git\n'
            check_output.return_value = repo_template.format(
                component_name
            )
            extraced_component_name = get_component_name(self.argv)

            assert extraced_component_name == component_name

    @given(text(
        alphabet=VALID_ALPHABET, min_size=1, max_size=100
    ))
    def test_component_not_passed_as_argument_with_https_without_extension(
        self, component_name
    ):
        with patch('cdflow.check_output') as check_output:
            check_output.return_value = 'https://github.com/org/{}\n'.format(
                component_name
            )
            extraced_component_name = get_component_name(self.argv)

            assert extraced_component_name == component_name


class TestGetVersion(unittest.TestCase):

    @given(text(alphabet=VALID_ALPHABET, min_size=1))
    def test_get_version_during_deploy(self, version):
        argv = ['deploy', 'test', version]
        found_version = get_version(argv)

        assert found_version == version

    @given(text(alphabet=VALID_ALPHABET, min_size=1))
    def test_get_version_during_release(self, version):
        argv = ['release', version]
        found_version = get_version(argv)

        assert found_version == version

    def test_missing_version_returns_nothing(self):
        argv = ['release']
        found_version = get_version(argv)

        assert found_version is None


class TestFindBucket(unittest.TestCase):

    def _create_bucket(self, tag_set):
        bucket = Mock()
        tags = Mock()
        bucket.Tagging.return_value = tags
        if tag_set:
            tags.tag_set = tag_set
        else:
            type(tags).tag_set = PropertyMock(side_effect=ClientError(
                {'Error': {
                    'Code': 'NoSuchTagSet',
                    'Message': 'The TagSet does not exist'
                }},
                'GetBucketTagging'
            ))
        return bucket

    def test_find_bucket_based_on_tag(self):
        s3_resource = Mock()
        bucket = self._create_bucket([
            {u'Value': 'team-rocket', u'Key': 'Project'},
            {u'Value': 'true', u'Key': TAG_NAME},
        ])
        buckets = [self._create_bucket(t) for t in ([], [], [], [])]
        buckets.insert(2, bucket)
        s3_resource.buckets.all.return_value = buckets
        found_bucket = find_bucket(s3_resource)

        assert found_bucket == bucket

    def test_multiple_buckets_causes_an_exception(self):
        s3_resource = Mock()
        tag_sets = (
            [{u'Value': 'true', u'Key': TAG_NAME}],
            [{u'Value': 'true', u'Key': TAG_NAME}],
            [], [], [], []
        )
        buckets = [self._create_bucket(t) for t in tag_sets]
        s3_resource.buckets.all.return_value = buckets

        self.assertRaises(MultipleBucketError, find_bucket, s3_resource)

    def test_missing_bucket_causes_an_exception(self):
        s3_resource = Mock()
        buckets = [self._create_bucket(t) for t in ([], [], [], [])]
        s3_resource.buckets.all.return_value = buckets

        self.assertRaises(MissingBucketError, find_bucket, s3_resource)


class TestFetchRelease(unittest.TestCase):

    @given(fixed_dictionaries({
        'component_name': text(alphabet=VALID_ALPHABET, min_size=1),
        'version': text(alphabet=VALID_ALPHABET, min_size=1),
    }))
    def test_get_release_bundle(self, fixtures):
        s3_bucket = Mock()

        component_name = fixtures['component_name']
        version = fixtures['version']
        with patch('cdflow.ZipFile') as ZipFile:
            zip_archive = Mock()
            ZipFile.return_value = zip_archive
            release_bundle = get_release_bundle(
                s3_bucket, component_name, version
            )

        s3_bucket.download_fileobj.assert_called_once_with(
            '{}/release-{}.zip'.format(component_name, version), ANY
        )

        assert release_bundle is zip_archive

    def test_get_metadata_from_release_bundle(self):
        expected_metadata = {
            'cdflow_image_digest': 'sha:12345asdfg'
        }
        zip_archive = Mock()
        zip_ext_file = Mock()
        zip_ext_file.read.return_value = json.dumps(expected_metadata)
        zip_archive.open.return_value = zip_ext_file
        metadata = extract_release_metadata(zip_archive)

        assert metadata == expected_metadata
