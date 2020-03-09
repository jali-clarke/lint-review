from __future__ import absolute_import
import json
from mock import call, Mock, patch
from unittest import TestCase

import lintreview.github as github

from . import load_fixture
from tests import conditionally_return
import github3
from github3 import GitHub
from github3.session import GitHubSession
from github3.orgs import Organization, OrganizationHook
from github3.repos import Repository
from github3.repos.hook import Hook


config = {
    'GITHUB_URL': 'https://api.github.com/',
}
session = GitHubSession()


class TestGithub(TestCase):

    def test_get_client(self):
        conf = config.copy()
        conf['GITHUB_OAUTH_TOKEN'] = 'an-oauth-token'
        gh = github.get_client(conf)
        assert isinstance(gh, GitHub)

    def test_get_client__retry_opts(self):
        conf = config.copy()
        conf['GITHUB_OAUTH_TOKEN'] = 'an-oauth-token'
        conf['GITHUB_CLIENT_RETRY_OPTIONS'] = {'backoff_factor': 42}
        gh = github.get_client(conf)

        for proto in ('https://', 'http://'):
            actual = gh.session.get_adapter(proto).max_retries.backoff_factor
            self.assertEqual(actual, 42)

    def test_get_lintrc(self):
        repo = Mock(spec=Repository)
        github.get_lintrc(repo, 'HEAD')
        repo.file_contents.assert_called_with('.lintrc', 'HEAD')

    def test_register_hook(self):
        repo = Mock(spec=Repository,
                    full_name='mark/lint-review')
        repo.hooks.return_value = []

        url = 'http://example.com/review/start'
        github.register_hook(repo, url)

        assert repo.create_hook.called, 'Create not called'
        calls = repo.create_hook.call_args_list
        expected = call(
            name='web',
            active=True,
            config={
                'content_type': 'json',
                'url': url,
            },
            events=['pull_request']
        )
        self.assertEqual(calls[0], expected)

    def test_register_hook__already_exists(self):
        repo = Mock(spec=Repository,
                    full_name='mark/lint-review')
        repo.hooks.return_value = [
            Hook(f, session)
            for f in json.loads(load_fixture('webhook_list.json'))
        ]
        url = 'http://example.com/review/start'

        github.register_hook(repo, url)
        assert repo.create_hook.called is False, 'Create called'

    def test_unregister_hook__success(self):
        repo = Mock(spec=Repository,
                    full_name='mark/lint-review')
        hooks = [
            github3.repos.hook.Hook(f, session)
            for f in json.loads(load_fixture('webhook_list.json'))
        ]
        repo.hooks.return_value = hooks
        url = 'http://example.com/review/start'
        github.unregister_hook(repo, url)
        assert repo.hook().delete.called, 'Delete not called'

    def test_unregister_hook__not_there(self):
        repo = Mock(spec=Repository,
                    full_name='mark/lint-review')
        repo.hooks.return_value = []
        url = 'http://example.com/review/start'

        self.assertRaises(Exception,
                          github.unregister_hook,
                          repo,
                          url)

    def test_register_org_hook(self):
        org = Mock(spec=Organization)
        org.name = 'mark'
        org.hooks.return_value = []

        url = 'http://example.com/review/start'
        github.register_org_hook(org, url)

        assert org.create_hook.called, 'Create not called'
        calls = org.create_hook.call_args_list
        expected = call(
            name='web',
            active=True,
            config={
                'content_type': 'json',
                'url': url,
            },
            events=['pull_request']
        )
        self.assertEqual(calls[0], expected)

    def test_register_org_hook__already_exists(self):
        org = Mock(spec=Organization)
        org.name = 'mark'
        org.hooks.return_value = [
            OrganizationHook(f, session)
            for f in json.loads(load_fixture('webhook_list.json'))
        ]
        url = 'http://example.com/review/start'

        github.register_org_hook(org, url)
        assert org.create_hook.called is False, 'Create called'

    def test_unregister_org_hook__success(self):
        org = Mock(spec=Organization)
        org.name = 'mark'
        org.hooks.return_value = [
            OrganizationHook(f, session)
            for f in json.loads(load_fixture('webhook_list.json'))
        ]
        url = 'http://example.com/review/start'
        github.unregister_org_hook(org, url)
        assert org.hook().delete.called, 'Delete not called'

    def test_unregister_org_hook__not_there(self):
        org = Mock(spec=Organization)
        org.name = 'mark'
        org.hooks.return_value = []
        url = 'http://example.com/review/start'

        self.assertRaises(Exception,
                          github.unregister_org_hook,
                          org,
                          url)

    def test_get_repository_uses_credentials_with_client_to_produce_repo(self):
        mock_client = Mock()
        mock_config = Mock()
        mock_repo = Mock()

        mock_get_client = conditionally_return(mock_client, mock_config)
        mock_client.repository = conditionally_return(mock_repo, owner='user', repository='repo')

        with patch('lintreview.github.get_client', mock_get_client):
            self.assertEqual(github.get_repository(mock_config, 'user', 'repo'), mock_repo)

    def test_get_organization_uses_credentials_with_client_to_produce_org(self):
        mock_client = Mock()
        mock_config = Mock()
        mock_org = Mock()

        mock_get_client = conditionally_return(mock_client, mock_config)
        mock_client.organization = conditionally_return(mock_org, username='org_name')

        with patch('lintreview.github.get_client', mock_get_client):
            self.assertEqual(github.get_organization(mock_config, 'org_name'), mock_org)