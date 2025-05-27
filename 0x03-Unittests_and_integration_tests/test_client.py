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
