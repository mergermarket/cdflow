import unittest
from string import printable

from cdflow import (
    CDFLOW_IMAGE_ID, InvalidURLError, fetch_account_scheme, get_image_id,
    parse_s3_url
)
from hypothesis import assume, given
from hypothesis.strategies import dictionaries, fixed_dictionaries, text
from mock import Mock, patch
from strategies import VALID_ALPHABET, image_id, s3_bucket_and_key


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


class TestParseS3Url(unittest.TestCase):

    @given(s3_bucket_and_key())
    def test_gets_bucket_name_and_key(self, s3_bucket_and_key):
        expected_bucket = s3_bucket_and_key[0]
        expected_key = s3_bucket_and_key[1]
        s3_url = 's3://{}/{}'.format(expected_bucket, expected_key)

        bucket, key = parse_s3_url(s3_url)

        assert bucket == expected_bucket
        assert key == expected_key

    @given(text())
    def test_invalid_url_protocol_throws_exception(self, invalid_url):
        assume(not invalid_url.startswith('s3://'))

        self.assertRaises(InvalidURLError, parse_s3_url, invalid_url)

    @given(text(alphabet=VALID_ALPHABET))
    def test_invalid_url_format_throws_exception(self, invalid_url):
        assume('/' not in invalid_url)

        self.assertRaises(
            InvalidURLError, parse_s3_url, 's3://{}'.format(invalid_url)
        )


class TestFetchAccountScheme(unittest.TestCase):

    @given(fixed_dictionaries({
        's3_bucket_and_key': s3_bucket_and_key(),
        'account_prefix': text(alphabet=VALID_ALPHABET, min_size=1),
    }))
    def test_fetch_account_scheme(self, fixtures):
        s3_resource = Mock()

        account_prefix = fixtures['account_prefix']
        bucket = fixtures['s3_bucket_and_key'][0]
        key = fixtures['s3_bucket_and_key'][1]

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

            account_scheme = fetch_account_scheme(s3_resource, bucket, key)

        expected_keys = sorted([
            'accounts', 'release-account', 'release-bucket', 'environments',
            'default-region', 'ecr-registry', 'lambda-bucket'
        ])

        assert list(sorted(account_scheme.keys())) == expected_keys

        release_bucket = '{}-account-resources'.format(account_prefix)

        assert account_scheme['release-bucket'] == release_bucket

        s3_resource.Object.assert_called_once_with(bucket, key)
