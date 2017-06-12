import unittest

from cdflow import fetch_release_metadata, get_component_name, get_version
from hypothesis import given
from hypothesis.strategies import fixed_dictionaries, text
from mock import Mock, patch
from strategies import VALID_ALPHABET


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
