import unittest

from string import ascii_letters, digits

from hypothesis import given
from hypothesis.strategies import text
from mock import patch

from cdflow import get_component_name

class TestFetchRelease(unittest.TestCase):

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
