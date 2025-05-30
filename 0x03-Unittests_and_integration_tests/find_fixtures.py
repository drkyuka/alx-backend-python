#!/usr/bin/env python3
# """Find fixtures in a Python file"""

import ast
from fixtures import TEST_PAYLOAD

with open("fixtures.py", "r", encoding="utf-8") as f:
    tree = ast.parse(f.read())

for node in tree.body:
    if isinstance(node, ast.Assign):
        target = node.targets[0]
        if isinstance(target, ast.Name):
            var_name = target.id
            print(f"Found fixture: {var_name}")


org_payload, repos_payload = TEST_PAYLOAD[0]

# Optionally create other derived fixtures
expected_repos = [repo["name"] for repo in repos_payload]
apache2_repos = [
    repo["name"]
    for repo in repos_payload
    if "apache-2.0" in repo.get("license", {}).get("key", "").lower()
]


print(f"Expected repos: {expected_repos}")
print(f"Apache 2.0 repos: {apache2_repos}")
