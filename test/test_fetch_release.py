import unittest

from hypothesis import assume, given
from hypothesis.strategies import text, fixed_dictionaries
from mock import patch, Mock, PropertyMock

from botocore.exceptions import ClientError

from strategies import VALID_ALPHABET

from cdflow import (
    get_component_name, get_version, find_bucket, fetch_release_metadata,
    MultipleBucketError, MissingBucketError, TAG_NAME
)


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

    @given(text(alphabet=VALID_ALPHABET, min_size=1))
    def test_find_bucket_based_on_tag(self, tag_name):
        assume(tag_name != TAG_NAME)
        s3_resource = Mock()
        bucket = self._create_bucket([
            {u'Value': 'team-rocket', u'Key': 'Project'},
            {u'Value': 'true', u'Key': tag_name},
        ])
        buckets = [self._create_bucket(t) for t in ([], [], [], [])]
        buckets.insert(2, bucket)
        s3_resource.buckets.all.return_value = buckets
        found_bucket = find_bucket(s3_resource, tag_name)

        assert found_bucket == bucket

    @given(text(alphabet=VALID_ALPHABET, min_size=1))
    def test_multiple_buckets_causes_an_exception(self, tag_name):
        assume(tag_name != TAG_NAME)
        s3_resource = Mock()
        tag_sets = (
            [{u'Value': 'true', u'Key': tag_name}],
            [{u'Value': 'true', u'Key': tag_name}],
            [], [], [], []
        )
        buckets = [self._create_bucket(t) for t in tag_sets]
        s3_resource.buckets.all.return_value = buckets

        self.assertRaises(
            MultipleBucketError, find_bucket, s3_resource, tag_name
        )

    @given(text(alphabet=VALID_ALPHABET, min_size=1))
    def test_missing_bucket_causes_an_exception(self, tag_name):
        assume(tag_name != TAG_NAME)
        s3_resource = Mock()
        buckets = [self._create_bucket(t) for t in ([], [], [], [])]
        s3_resource.buckets.all.return_value = buckets

        self.assertRaises(
            MissingBucketError, find_bucket, s3_resource, tag_name
        )


class TestFetchReleaseMetadata(unittest.TestCase):

    @given(fixed_dictionaries({
        'component_name': text(alphabet=VALID_ALPHABET, min_size=1),
        'version': text(alphabet=VALID_ALPHABET, min_size=1),
        'bucket_name': text(alphabet=VALID_ALPHABET, min_size=1),
    }))
    def test_get_metadata_from_release_key(self, fixtures):
        component_name = fixtures['component_name']
        version = fixtures['version']
        bucket_name = fixtures['bucket_name']
        expected_metadata = {
            'cdflow_image_digest': 'sha:12345asdfg'
        }

        s3_resource = Mock()
        key = Mock()
        key.metadata = expected_metadata
        s3_resource.Object.return_value = key

        metadata = fetch_release_metadata(
            s3_resource, bucket_name, component_name, version
        )

        assert metadata == expected_metadata

        s3_resource.Object.assert_called_once_with(
            bucket_name, '{}/release-{}.zip'.format(component_name, version)
        )
