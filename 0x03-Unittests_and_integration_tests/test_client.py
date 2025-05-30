#!/usr/bin/env python3
"""A github org client"""

import unittest
from unittest.mock import PropertyMock, patch, Mock
from client import GithubOrgClient
from parameterized import parameterized, parameterized_class
from fixtures import TEST_PAYLOAD


# Test class for GithubOrgClient
class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand(  # type: ignore
        [
            ("google",),
            ("abc",),
        ]
    )
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """
        Parameterize and patch as decorators
        Test the org method
        """
        org_url = f"https://api.github.com/orgs/{org_name}"

        # Mock the return value of get_json
        org_json = {"name": org_url}
        mock_get_json.return_value = org_json

        # Create an instance of GithubOrgClient and call the org method
        client = GithubOrgClient(org_name)

        # Check that the org method returns the expected value

        self.assertEqual(client.org, org_json)

        # Check that get_json was called with the correct URL
        mock_get_json.assert_called_once_with(org_url)

    def test_public_repos_url(self):
        """
        Test for mocking a property
        """

        # Mock the org method to return a specific value
        # org is a method of GithubOrgClient
        # that returns a dictionary with a "repos_url" key
        # use PropertyMock to mock the org as a property
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_client:
            # set the expected mock value
            mock_client.return_value = {
                "repos_url": "https://api.github.com/orgs/google"
            }

            # Create an instance of GithubOrgClient
            # and check the _public_repos_url property
            # matches the expected URL
            self.assertEqual(
                GithubOrgClient("google")._public_repos_url,
                "https://api.github.com/orgs/google",
            )

            # Check that the mock was called once
            mock_client.assert_called_once()

    @patch("client.get_json")
    def test_public_repos(self, mock_json):
        """
        Use @patch as a decorator to mock get_json
        and make it return a payload of your choice.
        Use patch as a context manager to mock
        GithubOrgClient._public_repos_url and
        return a value of your choice.
        """
        # Payload returned by get_json (list of repo dicts)
        payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]

        mock_json.return_value = payload
        base_url = "https://api.github.com/orgs/test"

        # Patch _public_repos_url property
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = base_url

            client = GithubOrgClient("test")
            repos = client.public_repos()

            # The expected list of repo names
            self.assertEqual(repos, ["repo1", "repo2", "repo3"])

            # _public_repos_url property called once
            mock_url.assert_called_once()

            # get_json called once with the mocked URL
            mock_json.assert_called_once_with(base_url)

    @parameterized.expand(  # type: ignore
        [
            ({"license": {"key": "my_license"}}, "my_license", True),
            ({"license": {"key": "other_license"}}, "my_license", False),
        ]
    )
    def test_has_license(self, repo_name, license_key, expected):
        """
        Test the has_license static method
        with different repo names and license keys.
        """

        result = GithubOrgClient.has_license(repo_name, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    [
        {
            "org_payload": org,
            "repos_payload": repos,
            "expected_repos": expected,
            "apache2_repos": apache2,
        }
        for org, repos, expected, apache2 in TEST_PAYLOAD
    ]
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Start patcher for requests.get and set up side_effect for .json()"""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            # Return a mock with .json() returning the correct payload
            mock_resp = Mock()
            payload = None

            if url == GithubOrgClient.ORG_URL.format(org="google"):
                payload = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                payload = cls.repos_payload

            mock_resp.json.return_value = payload

            return mock_resp

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher for requests.get"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test for public_repos method"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)
