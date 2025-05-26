#!/usr/bin/env python3
"""
This script contains utility functions for testing purposes.
It includes function for Unittests and Integration Tests
"""

import unittest
from typing import Any, Union
from parameterized import parameterized

access_nested_map = __import__("utils").access_nested_map


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
        nested_map: dict[str, Any],
        path: tuple[str, ...],
        expected: Union[int, dict[str, int]],
    ) -> None:
        """
        Test accessing a nested map with valid keys.
        """
        result: Any = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

    @parameterized.expand(  # type: ignore
        [({}, ("a",)), ({"a": 1}, ("a", "b"))]
    )
    def test_access_nested_map_exception(
        self, nested_map: dict[str, Any], path: tuple[str, ...]
    ) -> None:
        """
        Test exception when accessing a nested map with a missing key.
        """
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)
