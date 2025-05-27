#!/usr/bin/env python3
"""A github org client"""

import unittest

from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


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
        """Test the org method"""
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
