#!/usr/bin/env python3
"""
This script contains utility functions for testing purposes.
It includes function for Unittests and Integration Tests
"""

from unittest.mock import patch
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

    @parameterized.expand(  # type: ignore
        [
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ]
    )
    def test_get_json(self, url, expected_value) -> None:
        """
        Test getting JSON from a URL.
        """

        with patch("utils.requests.get") as mock_get:
            # Setup the mock to return a response with the expected JSON data
            mock_response = mock_get.return_value
            mock_response.json.return_value = expected_value
            # mock_response.status_code = 200

            # Call the function with our mocked response
            response = get_json(url)

            # Assert that the mock was called exactly once with the expected URL
            mock_get.assert_called_once_with(url)

            # Assert that our function returns the expected result
            self.assertEqual(response, expected_value)
