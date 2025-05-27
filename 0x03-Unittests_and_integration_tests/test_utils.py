#!/usr/bin/env python3
"""
This script contains utility functions for testing purposes.
It includes function for Unittests and Integration Tests
"""

from unittest.mock import Mock, patch
import unittest
from parameterized import parameterized

access_nested_map = __import__("utils").access_nested_map
get_json = __import__("utils").get_json


class TestAccessNestedMap(unittest.TestCase):
    """
    Test case for the access_nested_map function.
    """

    @parameterized.expand(  # type: ignore
        [
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
        ]
    )
    def test_access_nested_map(
        self,
        nested_map,
        path,
        expected,
    ) -> None:
        """
        Test accessing a nested map with valid keys.
        """
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

    @parameterized.expand(  # type: ignore
        [({}, ("a",)), ({"a": 1}, ("a", "b"))]
    )
    def test_access_nested_map_exception(self, nested_map, path) -> None:
        """
        Test exception when accessing a nested map with a missing key.
        """
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """
    Test case for the get_json function.
    """

    @staticmethod
    def url_search(url: str):
        """Return a mock response object with a .json() method
        for the given URL."""
        url_list = {
            "http://example.com": {"payload": True},
            "http://holberton.io": {"payload": False},
        }

        mock_resp = Mock()
        mock_resp.json.return_value = url_list[url]
        return mock_resp

    @parameterized.expand(  # type: ignore
        [
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ]
    )
    @patch("utils.requests.get", side_effect=url_search)
    def test_get_json(
        self, url: str, expected_value: dict[str, bool], mock_get: Mock
    ) -> None:
        """
        Test getting JSON from a URL.
        """
        response = get_json(url)
        mock_get.assert_called_once_with(url)
        self.assertEqual(response, expected_value)
