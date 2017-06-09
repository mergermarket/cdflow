import unittest
from string import printable

from mock import patch, Mock
from hypothesis import given, assume
from hypothesis.strategies import dictionaries, fixed_dictionaries, text

from strategies import image_id, VALID_ALPHABET

from cdflow import get_image_id, fetch_account_scheme, CDFLOW_IMAGE_ID


class TestGetReleaseCommandsImage(unittest.TestCase):

    @given(dictionaries(
        keys=text(alphabet=printable), values=text(alphabet=printable)
    ))
    def test_get_default_image_id(self, environment):
        assume('CDFLOW_IMAGE_ID' not in environment)

        image_id = get_image_id(environment)

        assert image_id == CDFLOW_IMAGE_ID

    @given(fixed_dictionaries({
        'environment': dictionaries(
            keys=text(alphabet=printable), values=text(alphabet=printable)
        ),
        'image_id': image_id(),
    }))
    def test_get_image_id_from_environment(self, fixtures):
        environment = fixtures['environment']
        environment['CDFLOW_IMAGE_ID'] = fixtures['image_id']

        image_id = get_image_id(environment)

        assert image_id == fixtures['image_id']


class TestFetchAccountScheme(unittest.TestCase):

    @given(text(alphabet=VALID_ALPHABET, min_size=1))
    def test_fetch_account_scheme(self, account_prefix):
        s3_resource = Mock()

        with patch('cdflow.BytesIO') as BytesIO:
            BytesIO.return_value.__enter__.return_value.read.return_value = '''
                {{
                  "accounts": {{
                    "{0}dev": {{
                      "id": "222222222222",
                      "role": "admin"
                    }},
                    "{0}prod": {{
                      "id": "111111111111",
                      "role": "admin"
                    }}
                  }},
                  "release-account": "{0}dev",
                  "release-bucket": "{0}-account-resources",
                  "environments": {{
                    "live": "{0}prod",
                    "*": "{0}dev"
                  }},
                  "default-region": "eu-west-12",
                  "ecr-registry": "1234567.dkr.ecr.eu-west-1.amazonaws.com",
                  "lambda-bucket": "cdflow-lambda-releases"
                }}
            '''.format(account_prefix)

            account_scheme = fetch_account_scheme(s3_resource, account_prefix)

        expected_keys = sorted([
            'accounts', 'release-account', 'release-bucket', 'environments',
            'default-region', 'ecr-registry', 'lambda-bucket'
        ])

        assert map(str, sorted(account_scheme.keys())) == expected_keys

        release_bucket = '{}-account-resources'.format(account_prefix)

        assert account_scheme['release-bucket'] == release_bucket

        s3_resource.Object.assert_called_once_with(
            '{}-account-resources'.format(account_prefix),
            'account-scheme.json'
        )
