import os
import argparse

import github


def build_github_client(env):
    token = env.get('GITHUB_TOKEN')
    if token:
        return github.Github(token)
    username = env['GITHUB_USERNAME']
    password = env['GITHUB_PASSWORD']
    return github.Github(username, password)


def main(repo_name, version, asset_path):
    print(f'Releasing {repo_name} at version {version} with {asset_path}')
    g = build_github_client(os.environ)

    repo = g.get_repo(repo_name)

    project_name = repo_name.split('/')[-1]

    print(f'Creating release {version}')
    new_release = repo.create_git_release(
        version, version, f'{project_name} {version} release',
    )

    new_release.upload_asset(asset_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--repo_name', required=True, help='Name of the repo to release',
    )
    parser.add_argument('--version', required=True, help='Version of release')
    parser.add_argument(
        '--asset_path', required=True, help='Path to release artifact',
    )
    args = vars(parser.parse_args())
    main(**args)
