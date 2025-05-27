#!/usr/bin/env python3
"""A github org client"""

import unittest
from unittest.mock import PropertyMock, patch

from client import GithubOrgClient
from parameterized import parameterized


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

        # Patch _public_repos_url property
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "https://api.github.com/orgs/test"

            client = GithubOrgClient("test")
            repos = client.public_repos()

            # The expected list of repo names
            self.assertEqual(repos, ["repo1", "repo2", "repo3"])

            # _public_repos_url property called once
            mock_url.assert_called_once()

            # get_json called once with the mocked URL
            mock_json.assert_called_once_with("https://api.github.com/orgs/test")
