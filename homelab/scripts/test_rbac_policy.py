#!/usr/bin/env python3
"""Verify the effective RBAC committed for agents-shared/frack-ops."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from typing import Any

import yaml


Resource = dict[str, Any]
Request = dict[str, str]
REPO_ROOT = Path(__file__).resolve().parents[2]
RBAC_PATH = REPO_ROOT / "homelab" / "k8s" / "rbac.yaml"
SERVICE_ACCOUNT = {
    "kind": "ServiceAccount",
    "name": "frack-ops",
    "namespace": "agents-shared",
}
SERVICE_ACCOUNT_USER = "system:serviceaccount:agents-shared:frack-ops"
SERVICE_ACCOUNT_GROUPS = {
    "system:authenticated",
    "system:serviceaccounts",
    "system:serviceaccounts:agents-shared",
}
BUSINESS_NAMESPACES = {
    "ae",
    "authorworks",
    "blink-platform",
    "chimera",
    "githired",
    "hyvapaska",
    "lunasea",
    "omnilemma",
    "potluck",
    "trade",
    "ursulai",
}


class FrackRbacPolicyTest(unittest.TestCase):
    """Exercise both structural and effective-permission invariants."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the exact multi-document manifest proposed for GitOps."""
        cls.manifest_path = Path(os.environ.get("FRACK_RBAC_MANIFEST", RBAC_PATH))
        with cls.manifest_path.open(encoding="utf-8") as manifest:
            cls.objects = [item for item in yaml.safe_load_all(manifest) if item]
        cls.roles = {
            f"{item['metadata']['namespace']}/{item['metadata']['name']}": item
            for item in cls.objects
            if item["kind"] == "Role"
        }
        cls.cluster_roles = {
            item["metadata"]["name"]: item
            for item in cls.objects
            if item["kind"] == "ClusterRole"
        }

    @staticmethod
    def includes_subject(binding: Resource) -> bool:
        """Return whether a binding grants Frack through any standard identity."""
        for subject in binding.get("subjects", []):
            is_service_account = (
                subject.get("kind") == SERVICE_ACCOUNT["kind"]
                and subject.get("name") == SERVICE_ACCOUNT["name"]
                and subject.get("namespace") == SERVICE_ACCOUNT["namespace"]
            )
            is_user = (
                subject.get("kind") == "User"
                and subject.get("name") == SERVICE_ACCOUNT_USER
            )
            is_group = (
                subject.get("kind") == "Group"
                and subject.get("name") in SERVICE_ACCOUNT_GROUPS
            )
            if is_service_account or is_user or is_group:
                return True
        return False

    def effective_rules(self, namespace: str) -> list[Resource]:
        """Resolve namespaced and cluster rules granted to Frack."""
        rules: list[Resource] = []
        for binding in self.objects:
            if (
                binding["kind"] != "RoleBinding"
                or binding["metadata"]["namespace"] != namespace
                or not self.includes_subject(binding)
            ):
                continue
            role_kind = binding["roleRef"]["kind"]
            role_name = binding["roleRef"]["name"]
            if role_kind == "Role":
                key = f"{namespace}/{role_name}"
                self.assertIn(key, self.roles)
                rules.extend(self.roles[key].get("rules", []))
            else:
                self.assertEqual(role_kind, "ClusterRole")
                self.assertIn(role_name, self.cluster_roles)
                rules.extend(self.cluster_roles[role_name].get("rules", []))

        for binding in self.objects:
            if binding["kind"] != "ClusterRoleBinding" or not self.includes_subject(
                binding
            ):
                continue
            self.assertEqual(binding["roleRef"]["kind"], "ClusterRole")
            name = binding["roleRef"]["name"]
            self.assertIn(name, self.cluster_roles)
            rules.extend(self.cluster_roles[name].get("rules", []))
        return rules

    def is_allowed(self, request: Request) -> bool:
        """Evaluate the subset of Kubernetes RBAC used by this manifest."""
        for rule in self.effective_rules(request["namespace"]):
            if request.get("apiGroup", "") not in rule.get("apiGroups", []):
                continue
            if request["resource"] not in rule.get("resources", []):
                continue
            if request["verb"] not in rule.get("verbs", []):
                continue
            names = rule.get("resourceNames", [])
            if names and request.get("resourceName") not in names:
                continue
            return True
        return False

    def assert_allowed(self, **request: str) -> None:
        """Assert that the synthetic authorization request is allowed."""
        self.assertTrue(self.is_allowed(request), f"expected allow: {request}")

    def assert_denied(self, **request: str) -> None:
        """Assert that the synthetic authorization request is denied."""
        self.assertFalse(self.is_allowed(request), f"expected deny: {request}")

    def test_service_account_and_business_namespace_inventory(self) -> None:
        service_accounts = [
            item
            for item in self.objects
            if item["kind"] == "ServiceAccount"
            and item["metadata"]["name"] == SERVICE_ACCOUNT["name"]
        ]
        self.assertEqual(
            [item["metadata"]["namespace"] for item in service_accounts],
            [SERVICE_ACCOUNT["namespace"]],
        )
        business_roles = [
            item
            for item in self.objects
            if item["kind"] == "Role"
            and item["metadata"]["name"] == "frack-business-ops"
        ]
        self.assertEqual(
            {item["metadata"]["namespace"] for item in business_roles},
            BUSINESS_NAMESPACES,
        )

    def test_standard_service_account_identities_are_modeled(self) -> None:
        direct_subjects = [
            SERVICE_ACCOUNT,
            {"kind": "User", "name": SERVICE_ACCOUNT_USER},
            *(
                {"kind": "Group", "name": group}
                for group in sorted(SERVICE_ACCOUNT_GROUPS)
            ),
        ]
        for subject in direct_subjects:
            self.assertTrue(self.includes_subject({"subjects": [subject]}), subject)
        self.assertFalse(
            self.includes_subject(
                {"subjects": [{"kind": "Group", "name": "system:unauthenticated"}]}
            )
        )

    def test_group_bindings_feed_the_effective_permission_model(self) -> None:
        role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": "fixture-secret-reader",
                "namespace": "agents-shared",
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["secrets"],
                    "verbs": ["get"],
                }
            ],
        }
        role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": "fixture-serviceaccounts",
                "namespace": "agents-shared",
            },
            "subjects": [
                {
                    "kind": "Group",
                    "name": "system:serviceaccounts:agents-shared",
                }
            ],
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "Role",
                "name": "fixture-secret-reader",
            },
        }
        cluster_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {"name": "fixture-exec"},
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods/exec"],
                    "verbs": ["create"],
                }
            ],
        }
        cluster_role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {"name": "fixture-authenticated"},
            "subjects": [{"kind": "Group", "name": "system:authenticated"}],
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",
                "name": "fixture-exec",
            },
        }

        self.objects = [
            *self.objects,
            role,
            role_binding,
            cluster_role,
            cluster_role_binding,
        ]
        self.roles = {**self.roles, "agents-shared/fixture-secret-reader": role}
        self.cluster_roles = {**self.cluster_roles, "fixture-exec": cluster_role}

        self.assert_allowed(
            namespace="agents-shared",
            resource="secrets",
            resourceName="frick-subagent-client",
            verb="get",
        )
        self.assert_allowed(
            namespace="blink-platform",
            resource="pods/exec",
            resourceName="blink-platform-example",
            verb="create",
        )

    def test_no_secret_exec_wildcard_or_unexpected_mutation_rules(self) -> None:
        for role in [*self.roles.values(), *self.cluster_roles.values()]:
            for rule in role.get("rules", []):
                self.assertNotIn(
                    "*", rule.get("apiGroups", []), role["metadata"]["name"]
                )
                self.assertNotIn(
                    "*", rule.get("resources", []), role["metadata"]["name"]
                )
                self.assertNotIn("*", rule.get("verbs", []), role["metadata"]["name"])
                self.assertNotIn(
                    "secrets", rule.get("resources", []), role["metadata"]["name"]
                )
                self.assertNotIn(
                    "pods/exec", rule.get("resources", []), role["metadata"]["name"]
                )

                for verb in rule.get("verbs", []):
                    if verb not in {
                        "create",
                        "delete",
                        "deletecollection",
                        "patch",
                        "update",
                    }:
                        continue
                    is_business_pod_restart = (
                        role["kind"] == "Role"
                        and role["metadata"]["namespace"] in BUSINESS_NAMESPACES
                        and rule.get("apiGroups") == [""]
                        and rule.get("resources") == ["pods"]
                        and verb == "delete"
                    )
                    self.assertTrue(
                        is_business_pod_restart,
                        f"{role['metadata']['name']} has unexpected mutation access",
                    )

    def test_shared_namespace_access_is_named_and_read_only(self) -> None:
        shared_roles = [
            role
            for role in self.roles.values()
            if role["metadata"]["namespace"] == "agents-shared"
        ]
        self.assertEqual(
            [role["metadata"]["name"] for role in shared_roles],
            ["frack-self-observer"],
        )
        for rule in shared_roles[0]["rules"]:
            self.assertTrue(rule.get("resourceNames"))

        self.assert_allowed(
            namespace="agents-shared",
            apiGroup="apps",
            resource="deployments",
            resourceName="frack",
            verb="get",
        )
        self.assert_denied(
            namespace="agents-shared",
            apiGroup="apps",
            resource="deployments",
            resourceName="puck",
            verb="get",
        )
        self.assert_denied(
            namespace="agents-shared",
            apiGroup="apps",
            resource="deployments",
            verb="list",
        )
        self.assert_denied(
            namespace="agents-shared",
            apiGroup="apps",
            resource="deployments",
            resourceName="frack",
            verb="patch",
        )

    def test_broker_and_workload_secret_requests_are_denied(self) -> None:
        for secret_name in (
            "frack-secrets",
            "frack-subagent-client",
            "frick-subagent-client",
            "subagent-broker-auth",
        ):
            self.assert_denied(
                namespace="agents-shared",
                resource="secrets",
                resourceName=secret_name,
                verb="get",
            )
        for verb in ("get", "list", "watch", "create", "patch"):
            self.assert_denied(namespace="agents-shared", resource="secrets", verb=verb)
        self.assert_denied(
            namespace="inference",
            resource="secrets",
            resourceName="fleet-spend-auth",
            verb="get",
        )
        self.assert_denied(
            namespace="blink-platform",
            resource="secrets",
            resourceName="blink-secrets",
            verb="get",
        )

    def test_pod_exec_is_denied_in_shared_and_business_namespaces(self) -> None:
        for namespace, pod_name in (
            ("agents-shared", "frick-example"),
            ("blink-platform", "blink-platform-example"),
            ("potluck", "potluck-example"),
        ):
            self.assert_denied(
                namespace=namespace,
                resource="pods/exec",
                resourceName=pod_name,
                verb="create",
            )

    def test_required_observation_and_restart_access_remains(self) -> None:
        self.assert_allowed(namespace="blink-platform", resource="pods/log", verb="get")
        self.assert_denied(namespace="blink-platform", resource="pods/log", verb="list")
        self.assert_allowed(namespace="blink-platform", resource="pods", verb="delete")
        self.assert_allowed(
            namespace="blink-platform",
            apiGroup="apps",
            resource="deployments",
            verb="list",
        )
        self.assert_allowed(namespace="kube-system", resource="nodes", verb="list")


if __name__ == "__main__":
    unittest.main(verbosity=2)
