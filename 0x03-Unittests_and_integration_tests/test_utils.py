#!/usr/bin/env python3
"""
This script contains utility functions for testing purposes.
It includes function for Unittests and Integration Tests
"""

from unittest.mock import Mock, patch
import unittest
from urllib import response
from parameterized import parameterized

access_nested_map = __import__("utils").access_nested_map
get_json = __import__("utils").get_json
memoize = __import__("utils").memoize


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

    def url_get(self, url):
        """Return a mock response object with a .json() method
        for the given URL."""
        url_list = {
            "http://example.com": {"payload": True},
            "http://holberton.io": {"payload": False},
        }

        # create a mock response object
        mock_resp = Mock()

        # set the .json() method to return the corresponding value
        mock_resp.json.return_value = url_list[url]

        # return the mock response object
        return mock_resp

    @parameterized.expand(  # type: ignore
        [
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ]
    )
    def test_get_json(self, url, expected_value):
        """
        Test getting JSON from a URL.
        """

        with patch("utils.requests.get", side_effect=self.url_get) as mock:
            # Call the get_json function with the URL
            json_response = get_json(url)

            # Check that the mock was called with the correct URL
            mock.assert_called_once_with(url)

            # Check that the JSON response matches the expected value
            self.assertEqual(json_response, expected_value)


class TestMemoize(unittest.TestCase):
    """
    Test case for the memoize decorator.
    """

    def test_memoize(self):
        """
        Test that the memoize decorator caches the result of a method.
        """

        class TestClass:
            """
            A simple class to test the memoize decorator.
            """

            def a_method(self):
                """
                A method that returns a value.
                This method is decorated with memoize.
                """
                return 42

            @memoize
            def a_property(self):
                """
                A property that calls a_method.
                This property is decorated with memoize.
                """
                return self.a_method()

        # Create an instance of TestClass
        usecase = TestClass()

        # Call the memoized method
        with patch.object(usecase, "a_method", return_value=42) as mock_get:
            # Call the memoized property
            result1 = usecase.a_property
            result2 = usecase.a_property

            # Check that the method was called only once
            mock_get.assert_called_once()

            # Check that the result is cached
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
