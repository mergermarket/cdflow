import unittest
from unittest.mock import patch
from string import printable
import json

from cdflow import (
    CDFLOW_IMAGE_ID, InvalidURLError, fetch_account_scheme, get_image_id,
    parse_s3_url
)
import boto3
from moto import mock_s3
from hypothesis import assume, given
from hypothesis.strategies import dictionaries, fixed_dictionaries, text
from test.strategies import VALID_ALPHABET, image_id, s3_bucket_and_key


class TestGetReleaseCommandsImage(unittest.TestCase):

    @given(dictionaries(
        keys=text(alphabet=printable), values=text(alphabet=printable)
    ))
    def test_get_default_image_id(self, environment):
        assume('CDFLOW_IMAGE_ID' not in environment)

        image_id = get_image_id(environment, {})

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

        image_id = get_image_id(environment, {})

        assert image_id == fixtures['image_id']

    def test_get_image_id_from_config_file(self):
        terraform_version = '0.12.18'
        config = {
            'terraform-version': terraform_version
        }
        image_id = get_image_id({}, config)

        assert image_id == \
            f'mergermarket/cdflow-commands:terraform{terraform_version}'


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

    def setUp(self):
        self.mock_s3 = mock_s3()
        self.mock_s3.start()

    def tearDown(self):
        self.mock_s3.stop()

    @given(fixed_dictionaries({
        's3_bucket_and_key': s3_bucket_and_key(),
        'account_prefix': text(alphabet=VALID_ALPHABET, min_size=1),
    }))
    def test_fetches_without_forwarding_account_scheme(self, fixtures):
        s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')

        account_prefix = fixtures['account_prefix']
        bucket = fixtures['s3_bucket_and_key'][0]
        key = fixtures['s3_bucket_and_key'][1]

        s3_client.create_bucket(Bucket=bucket)

        account_scheme_content = {
          'accounts': {
            f'{account_prefix}dev': {
              'id': '222222222222',
              'role': 'admin'
            },
            f'{account_prefix}prod': {
              'id': '111111111111',
              'role': 'admin'
            }
          },
          'release-account': f'{account_prefix}dev',
          'release-bucket': f'{account_prefix}-account-resources',
          'environments': {
            'live': f'{account_prefix}prod',
            '*': f'{account_prefix}dev'
          },
          'default-region': 'eu-west-12',
          'ecr-registry': '1234567.dkr.ecr.eu-west-1.amazonaws.com',
          'lambda-bucket': 'cdflow-lambda-releases',
          'upgrade-account-scheme': {
              'team-whitelist': [],
              'component-whitelist': [],
              'new-url': 's3://new_bucket/new_key',
          }
        }

        account_scheme_object = s3_resource.Object(bucket, key)
        account_scheme_object.put(
            Body=json.dumps(account_scheme_content).encode('utf-8'),
        )

        team = 'a-team'
        component = 'a-component'

        account_scheme = fetch_account_scheme(
            s3_resource, bucket, key, team, component,
        )

        expected_keys = sorted(account_scheme_content.keys())

        assert list(sorted(account_scheme.keys())) == expected_keys

        release_bucket = account_scheme_content['release-bucket']

        assert account_scheme['release-bucket'] == release_bucket

    def test_fetches_forwarded_account_scheme_if_component_whitelisted(self):
        s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')

        team = 'a-team'
        component = 'a-component'

        old_bucket = 'releases'
        old_key = 'account-scheme.json'

        new_bucket = 'new-releases'
        new_key = 'upgraded-account-scheme.json'

        s3_client.create_bucket(Bucket=old_bucket)
        s3_client.create_bucket(Bucket=new_bucket)

        old_account_scheme_content = json.dumps({
          'accounts': {
            'orgdev': {
              'id': '222222222222',
              'role': 'admin'
            },
            'orgprod': {
              'id': '111111111111',
              'role': 'admin'
            }
          },
          'release-account': 'orgdev',
          'release-bucket': 'org-account-resources',
          'environments': {
            'live': 'orgprod',
            '*': 'orgdev'
          },
          'default-region': 'eu-west-12',
          'ecr-registry': '1234567.dkr.ecr.eu-west-1.amazonaws.com',
          'lambda-bucket': 'cdflow-lambda-releases',
          'upgrade-account-scheme': {
              'team-whitelist': [],
              'component-whitelist': [component],
              'new-url': f's3://{new_bucket}/{new_key}',
          }
        })

        new_account_scheme_content = {
            'accounts': {
                'orgprod': {
                    'id': '0987654321',
                    'role': 'admin-role',
                },
                'orgrelease': {
                    'id': '1234567890',
                    'role': 'test-role',
                    'region': 'region-override',
                },
            },
            'environments': {},
            'release-account': 'orgrelease',
            'release-bucket': new_bucket,
            'default-region': 'test-region-1',
            'terraform-backend-s3-bucket': 'backend-bucket',
            'terraform-backend-s3-dynamodb-table': 'backend-table',
            'lambda-buckets': {
                'test-region-1': 'test-bucket-1',
                'test-region-2': 'test-bucket-2'
            },
        }

        old_account_scheme_object = s3_resource.Object(old_bucket, old_key)
        old_account_scheme_object.put(
            Body=old_account_scheme_content.encode('utf-8'),
        )

        new_account_scheme_object = s3_resource.Object(new_bucket, new_key)
        new_account_scheme_object.put(
            Body=json.dumps(new_account_scheme_content).encode('utf-8'),
        )

        account_scheme = fetch_account_scheme(
            s3_resource, old_bucket, old_key, team, component,
        )

        expected_keys = sorted(new_account_scheme_content.keys())

        assert list(sorted(account_scheme.keys())) == expected_keys

        assert account_scheme['release-bucket'] == new_bucket

    def test_fetches_forwarded_account_scheme_if_team_whitelisted(self):
        s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')

        team = 'a-team'
        component = 'a-component'

        old_bucket = 'releases'
        old_key = 'account-scheme.json'

        new_bucket = 'new-releases'
        new_key = 'upgraded-account-scheme.json'

        s3_client.create_bucket(Bucket=old_bucket)
        s3_client.create_bucket(Bucket=new_bucket)

        old_account_scheme_content = json.dumps({
          'accounts': {
            'orgdev': {
              'id': '222222222222',
              'role': 'admin'
            },
            'orgprod': {
              'id': '111111111111',
              'role': 'admin'
            }
          },
          'release-account': 'orgdev',
          'release-bucket': 'org-account-resources',
          'environments': {
            'live': 'orgprod',
            '*': 'orgdev'
          },
          'default-region': 'eu-west-12',
          'ecr-registry': '1234567.dkr.ecr.eu-west-1.amazonaws.com',
          'lambda-bucket': 'cdflow-lambda-releases',
          'upgrade-account-scheme': {
              'team-whitelist': [team],
              'component-whitelist': [],
              'new-url': f's3://{new_bucket}/{new_key}',
          }
        })

        new_account_scheme_content = {
            'accounts': {
                'orgprod': {
                    'id': '0987654321',
                    'role': 'admin-role',
                },
                'orgrelease': {
                    'id': '1234567890',
                    'role': 'test-role',
                    'region': 'region-override',
                },
            },
            'environments': {},
            'release-account': 'orgrelease',
            'release-bucket': new_bucket,
            'default-region': 'test-region-1',
            'terraform-backend-s3-bucket': 'backend-bucket',
            'terraform-backend-s3-dynamodb-table': 'backend-table',
            'lambda-buckets': {
                'test-region-1': 'test-bucket-1',
                'test-region-2': 'test-bucket-2'
            },
        }

        old_account_scheme_object = s3_resource.Object(old_bucket, old_key)
        old_account_scheme_object.put(
            Body=old_account_scheme_content.encode('utf-8'),
        )

        new_account_scheme_object = s3_resource.Object(new_bucket, new_key)
        new_account_scheme_object.put(
            Body=json.dumps(new_account_scheme_content).encode('utf-8'),
        )

        account_scheme = fetch_account_scheme(
            s3_resource, old_bucket, old_key, team, component,
        )

        expected_keys = sorted(new_account_scheme_content.keys())

        assert list(sorted(account_scheme.keys())) == expected_keys

        assert account_scheme['release-bucket'] == new_bucket

    @patch('cdflow.sys')
    def test_does_not_forward_account_scheme_if_component_flag_passed(
        self, mock_sys,
    ):
        s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')

        team = 'a-team'
        component = 'a-component'

        mock_sys.argv = ['--component', component]

        old_bucket = 'releases'
        old_key = 'account-scheme.json'

        new_bucket = 'new-releases'
        new_key = 'upgraded-account-scheme.json'

        s3_client.create_bucket(Bucket=old_bucket)

        old_account_scheme_content = {
          'accounts': {
            'orgdev': {
              'id': '222222222222',
              'role': 'admin'
            },
            'orgprod': {
              'id': '111111111111',
              'role': 'admin'
            }
          },
          'release-account': 'orgdev',
          'release-bucket': old_bucket,
          'environments': {
            'live': 'orgprod',
            '*': 'orgdev'
          },
          'default-region': 'eu-west-12',
          'ecr-registry': '1234567.dkr.ecr.eu-west-1.amazonaws.com',
          'lambda-bucket': 'cdflow-lambda-releases',
          'upgrade-account-scheme': {
              'team-whitelist': [team],
              'component-whitelist': [],
              'new-url': f's3://{new_bucket}/{new_key}',
          }
        }

        old_account_scheme_object = s3_resource.Object(old_bucket, old_key)
        old_account_scheme_object.put(
            Body=json.dumps(old_account_scheme_content).encode('utf-8'),
        )

        account_scheme = fetch_account_scheme(
            s3_resource, old_bucket, old_key, team, component,
        )

        expected_keys = sorted(old_account_scheme_content.keys())

        assert list(sorted(account_scheme.keys())) == expected_keys

        assert account_scheme['release-bucket'] == old_bucket
