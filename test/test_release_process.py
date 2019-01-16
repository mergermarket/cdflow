import unittest
from unittest.mock import MagicMock, patch

from github import Github
from github.Repository import Repository
from github.GitRelease import GitRelease

import release


@patch.dict(release.os.environ, {'GITHUB_TOKEN': 'dummy'})
class TestReleaseProcess(unittest.TestCase):

    def setUp(self):
        self.github_client = MagicMock(spec=Github)
        self.repo = MagicMock(spec=Repository)
        self.new_release = MagicMock(spec=GitRelease)
        self.repo.create_git_release.return_value = self.new_release
        self.github_client.get_repo.return_value = self.repo

    def test_release_project(self):
        self.repo.create_git_release.return_value = self.new_release

        version = 42
        project_name = 'myproject'
        repo_name = f'thisorg/{project_name}'
        asset_path = './run.exe'

        with patch('release.github.Github') as gh:
            gh.return_value = self.github_client

            release.main(repo_name, version, asset_path)

        gh.assert_called_once_with('dummy')

        self.github_client.get_repo.assert_called_once_with(repo_name)

        self.repo.create_git_release.assert_called_once_with(
            version, version, f'{project_name} {version} release',
        )

        self.new_release.upload_asset.assert_called_with(asset_path)
