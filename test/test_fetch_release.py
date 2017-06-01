import unittest

from string import ascii_letters, digits

from hypothesis import given
from hypothesis.strategies import text
from mock import patch, MagicMock, Mock

import boto3

from cdflow import (
    get_component_name, get_version, find_bucket,
    TAG_NAME, MultipleBucketError, MissingBucketError
)

class TestGetComponentName(unittest.TestCase):

    def setUp(self):
        self.argv = ['deploy', '42']

    @given(text(
        alphabet=ascii_letters + digits + '-._', min_size=1, max_size=100
    ))
    def test_get_component_name_passed_in(self, component_name):
        argv = ['deploy', '42', '-c', component_name]
        component_name = get_component_name(argv)

        assert component_name == component_name

    @given(text(
        alphabet=ascii_letters + digits + '-._', min_size=1, max_size=100
    ))
    def test_get_component_name_passed_in_with_long_flag(self, component_name):
        argv = ['deploy', '42', '--component', component_name]
        component_name = get_component_name(argv)

        assert component_name == component_name

    @given(text(
        alphabet=ascii_letters + digits + '-._', min_size=1, max_size=100
    ))
    def test_component_not_passed_as_argument(self, component_name):
        with patch('cdflow.check_output') as check_output:
            check_output.return_value = 'git@github.com:org/{}.git\n'.format(
                component_name
            )
            extraced_component_name = get_component_name(self.argv)

            assert extraced_component_name == component_name

    @given(text(
        alphabet=ascii_letters + digits + '-._', min_size=1, max_size=100
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
        alphabet=ascii_letters + digits + '-._', min_size=1, max_size=100
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
        alphabet=ascii_letters + digits + '-._', min_size=1, max_size=100
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
        alphabet=ascii_letters + digits + '-._', min_size=1, max_size=100
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

    @given(text(alphabet=ascii_letters + digits + '-._', min_size=1))
    def test_get_version(self, version):
        argv = ['deploy', version]
        found_version = get_version(argv)

        assert found_version == version


class TestFindBucket(unittest.TestCase):

    def _create_bucket(self, tag_set):
        bucket = Mock()
        tags = Mock()
        bucket.Tagging.return_value = tags
        tags.tag_set = tag_set
        return bucket

    def test_find_bucket_based_on_tag(self):
        s3_resource = Mock()
        bucket = self._create_bucket(
            [{u'Value': 'team-rocket', u'Key': 'Project'},
            {u'Value': 'true', u'Key': TAG_NAME},],
        )
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
