# Copyright 2026 The Aimium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Behavioral tests for the reference contracts; no browser or network needed."""

from copy import deepcopy
from dataclasses import replace
import io
import json
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from aimium.contracts.validate import (  # noqa: E402
    ActionAuthority, ValidationError, load_document, validate,
    validate_action_binding, validate_run_binding,
)


EXAMPLES = REPO_ROOT / "aimium" / "examples" / "contracts"


def example(name):
    with (EXAMPLES / name).open(encoding="utf-8") as source:
        return load_document(source)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.workspace = example("workspace.portal.json")
        self.workflow = example("workflow.task.json")
        self.action = example("action.click.json")
        self.run = example("run.unknown-outcome.json")
        fields = {key: self.action[key] for key in (
            "run_id", "workspace_id", "profile_id", "tab_id",
            "document_generation", "observation_id", "lease_generation",
            "origin",
        )}
        self.authority = ActionAuthority(
            **fields,
            allowed_origins=frozenset(self.workspace["allowed_origins"]),
            allowed_actions=frozenset({"click", "navigate", "observe_page"}),
        )

    def test_all_examples_and_bound_references_are_valid(self):
        for path in sorted(EXAMPLES.glob("*.json")):
            with self.subTest(example=path.name):
                validate(path.name.split(".")[0], example(path.name))
        validate_run_binding(self.run, self.workflow, self.workspace)
        validate_action_binding(self.action, self.authority)

    def test_model_switch_does_not_change_profile_identity(self):
        original_profile = self.workspace["profile_id"]
        self.workspace["model_binding"] = {
            "connector_id": "connector-demo-local", "model_id": "example-local-model",
            "required_capabilities": ["text"],
        }
        validate("workspace", self.workspace)
        self.assertEqual(original_profile, self.workspace["profile_id"])
        self.assertNotIn("profile_id", self.workspace["model_binding"])

    def test_known_secret_payload_fields_are_rejected(self):
        connector = example("connector.remote.json")
        connector["authentication"]["api_key"] = "test-only-not-a-key"
        with self.assertRaisesRegex(ValidationError, "secret payloads"):
            validate("connector", connector)
        self.workspace["cookies"] = []
        with self.assertRaisesRegex(ValidationError, "secret payloads"):
            validate("workspace", self.workspace)

    def test_connector_rejects_embedded_credentials_and_unsafe_transport(self):
        for endpoint in (
            "https://user:password@provider.example.test/v1",
            "http://provider.example.test/v1", "https://provider.example.test/v1?token=x",
            "https://provider.example.test/v1#secret",
        ):
            with self.subTest(endpoint=endpoint):
                connector = example("connector.remote.json")
                connector["endpoint"] = endpoint
                with self.assertRaises(ValidationError):
                    validate("connector", connector)

    def test_local_classification_requires_loopback_but_is_not_attestation(self):
        connector = example("connector.local.json")
        connector["endpoint"] = "https://remote.example.test/v1"
        with self.assertRaisesRegex(ValidationError, "loopback"):
            validate("connector", connector)
        for endpoint in ("http://localhost:11434", "http://[::1]:11434"):
            connector["endpoint"] = endpoint
            validate("connector", connector)

    def test_remote_provider_requires_secret_reference(self):
        connector = example("connector.remote.json")
        connector["authentication"] = {"kind": "none"}
        with self.assertRaisesRegex(ValidationError, "requires a secret reference"):
            validate("connector", connector)

    def test_workspace_start_origin_must_be_in_agent_scope(self):
        self.workspace["start_url"] = "https://elsewhere.example.test/"
        with self.assertRaisesRegex(ValidationError, "agent scope"):
            validate("workspace", self.workspace)

    def test_origins_have_a_single_canonical_representation(self):
        for origin in ("https://portal.example.test/", "https://portal.example.test:443",
                       "https://portal.example.test/path", "https://PORTAL.example.test"):
            with self.subTest(origin=origin):
                self.workspace["allowed_origins"] = [origin]
                with self.assertRaisesRegex(ValidationError, "canonical origin"):
                    validate("workspace", self.workspace)

    def test_ipv6_origin_aliases_cannot_duplicate_scope_entries(self):
        self.workspace["start_url"] = "https://[::1]/tasks"
        self.workspace["allowed_origins"] = ["https://[::1]"]
        validate("workspace", self.workspace)
        self.workspace["allowed_origins"].append("https://[0:0:0:0:0:0:0:1]")
        with self.assertRaisesRegex(ValidationError, "canonical origin"):
            validate("workspace", self.workspace)
        self.workspace["allowed_origins"] = ["https://[::1]", "https://[::1]"]
        with self.assertRaisesRegex(ValidationError, "duplicate origins"):
            validate("workspace", self.workspace)

    def test_unknown_node_and_script_config_are_rejected(self):
        node = self.workflow["nodes"][0]
        node["type"] = "execute_javascript"
        node["config"] = {"script": "document.title"}
        with self.assertRaises(ValidationError):
            validate("workflow", self.workflow)
        self.workflow = example("workflow.task.json")
        self.workflow["nodes"][0]["config"]["script"] = "document.title"
        with self.assertRaisesRegex(ValidationError, "unknown fields"):
            validate("workflow", self.workflow)

    def test_duplicate_nodes_and_missing_edge_targets_are_rejected(self):
        self.workflow["nodes"].append(deepcopy(self.workflow["nodes"][0]))
        with self.assertRaisesRegex(ValidationError, "duplicate node"):
            validate("workflow", self.workflow)
        self.workflow = example("workflow.task.json")
        self.workflow["edges"][0]["to"] = "missing"
        with self.assertRaisesRegex(ValidationError, "missing node"):
            validate("workflow", self.workflow)

    def test_unreachable_nodes_and_implicit_cycles_are_rejected(self):
        self.workflow["nodes"].append({
            "node_id": "unreachable", "type": "return_result", "config": {"input_keys": []},
        })
        with self.assertRaisesRegex(ValidationError, "unreachable"):
            validate("workflow", self.workflow)
        self.workflow = example("workflow.task.json")
        self.workflow["edges"][3]["to"] = "plan"
        with self.assertRaisesRegex(ValidationError, "cycle or an unreachable"):
            validate("workflow", self.workflow)

    def test_error_path_cannot_use_success_only_output(self):
        self.workflow["edges"].append({"from": "plan", "port": "error", "to": "finish"})
        with self.assertRaisesRegex(ValidationError, "inputs unavailable on every path"):
            validate("workflow", self.workflow)

    def test_condition_requires_both_paths_and_valid_join_inputs(self):
        flow = example("workflow.item.json")
        flow["input_keys"] = ["decision"]
        flow["entry_node_id"] = "choose"
        flow["nodes"] = [
            {"node_id": "choose", "type": "condition", "config": {
                "input_key": "decision", "operator": "is_true"}},
            {"node_id": "observe", "type": "observe_page", "config": {"output_key": "page"}},
            {"node_id": "finish", "type": "return_result", "config": {"input_keys": ["decision"]}},
        ]
        flow["edges"] = [
            {"from": "choose", "port": "true", "to": "observe"},
            {"from": "choose", "port": "false", "to": "finish"},
            {"from": "observe", "port": "success", "to": "finish"},
        ]
        validate("workflow", flow)
        flow["nodes"][2]["config"]["input_keys"] = ["page"]
        with self.assertRaisesRegex(ValidationError, "inputs unavailable on every path"):
            validate("workflow", flow)
        flow["edges"].pop(1)
        with self.assertRaisesRegex(ValidationError, "true and false"):
            validate("workflow", flow)

    def test_model_and_action_references_must_be_declared(self):
        self.workflow["nodes"][1]["config"]["model_slot"] = "not_configured"
        with self.assertRaisesRegex(ValidationError, "undeclared model slot"):
            validate("workflow", self.workflow)
        self.workflow = example("workflow.task.json")
        self.workflow["permissions"]["allowed_actions"] = ["observe_page"]
        with self.assertRaisesRegex(ValidationError, "declared permissions"):
            validate("workflow", self.workflow)

    def test_loop_is_bounded_and_cannot_call_itself(self):
        flow = example("workflow.batch.json")
        flow["nodes"][0]["config"]["max_iterations"] = 0
        with self.assertRaises(ValidationError):
            validate("workflow", flow)
        flow["nodes"][0]["config"]["max_iterations"] = 10
        flow["nodes"][0]["config"]["workflow"]["workflow_id"] = flow["workflow_id"]
        with self.assertRaisesRegex(ValidationError, "recursive"):
            validate("workflow", flow)

    def test_data_outputs_cannot_overwrite_existing_variables(self):
        self.workflow["nodes"][1]["config"]["output_key"] = "page"
        with self.assertRaisesRegex(ValidationError, "assigned more than once"):
            validate("workflow", self.workflow)

    def test_action_cannot_cross_run_profile_tab_or_document_boundary(self):
        for field in ("run_id", "workspace_id", "profile_id", "tab_id", "origin",
                      "observation_id", "document_generation", "lease_generation"):
            with self.subTest(field=field):
                old_value = getattr(self.authority, field)
                new_value = old_value + 1 if isinstance(old_value, int) else old_value + "-new"
                stale_authority = replace(self.authority, **{field: new_value})
                with self.assertRaisesRegex(ValidationError, "current browser authority"):
                    validate_action_binding(self.action, stale_authority)

    def test_cancelled_lease_rejects_late_model_response(self):
        with self.assertRaisesRegex(ValidationError, "active action lease"):
            validate_action_binding(self.action, replace(self.authority, active=False))

    def test_element_reference_cannot_be_reused_from_an_old_observation(self):
        self.action["target"]["observation_id"] = "old-observation"
        with self.assertRaisesRegex(ValidationError, "does not match the action observation"):
            validate_action_binding(self.action, self.authority)

    def test_navigation_cannot_leave_action_authority(self):
        self.action["kind"] = "navigate"
        self.action.pop("target")
        self.action["arguments"] = {"url": "https://elsewhere.example.test/receive"}
        with self.assertRaisesRegex(ValidationError, "destination is outside"):
            validate_action_binding(self.action, self.authority)
        self.action["arguments"]["url"] = "https://portal.example.test/tasks/2"
        validate_action_binding(self.action, self.authority)

    def test_action_kind_requires_permission_and_cannot_be_script(self):
        authority = replace(self.authority, allowed_actions=frozenset({"observe_page"}))
        with self.assertRaisesRegex(ValidationError, "outside the action authority"):
            validate_action_binding(self.action, authority)
        self.action["kind"] = "evaluate_javascript"
        self.action["arguments"] = {"script": "document.title"}
        with self.assertRaises(ValidationError):
            validate("action", self.action)

    def test_mutating_actions_require_an_expected_result(self):
        self.action.pop("expectation")
        with self.assertRaisesRegex(ValidationError, "postcondition"):
            validate("action", self.action)

    def test_download_artifact_is_not_an_arbitrary_filesystem_path(self):
        self.action["kind"] = "download"
        self.action["arguments"] = {"artifact_name": "../../outside.txt"}
        with self.assertRaisesRegex(ValidationError, "opaque artifact name"):
            validate("action", self.action)

    def test_uncertain_external_outcome_cannot_be_called_finished_or_cancelled(self):
        for status in ("completed", "failed", "cancelled", "queued", "running"):
            with self.subTest(status=status):
                self.run["status"] = status
                with self.assertRaisesRegex(ValidationError, "needs_reconciliation"):
                    validate("run", self.run)

    def test_unknown_outcome_keeps_the_original_action_identity(self):
        self.run["pending_action_id"] = None
        with self.assertRaisesRegex(ValidationError, "pending or unknown action"):
            validate("run", self.run)

    def test_pending_action_cannot_be_marked_paused(self):
        self.run["last_action_outcome"] = "pending"
        self.run["status"] = "paused"
        with self.assertRaisesRegex(ValidationError, "stopped or finished"):
            validate("run", self.run)

    def test_run_pins_workflow_profile_and_model_requirements(self):
        cases = (
            (lambda run: run["workflow"].update(version=2), "immutable workflow version"),
            (lambda run: run.update(profile_id="different-profile"), "does not match the workspace"),
            (lambda run: run["model_bindings"]["assistant"].update(required_capabilities=["text"]), "required capability"),
            (lambda run: run.update(current_node_id="nonexistent"), "nodes absent"),
        )
        for mutate, message in cases:
            with self.subTest(invariant=message):
                run = deepcopy(self.run)
                mutate(run)
                with self.assertRaisesRegex(ValidationError, message):
                    validate_run_binding(run, self.workflow, self.workspace)

    def test_run_does_not_expand_workspace_origins(self):
        self.workflow["permissions"]["allowed_origins"].append("https://elsewhere.example.test")
        with self.assertRaisesRegex(ValidationError, "exceed the workspace"):
            validate_run_binding(self.run, self.workflow, self.workspace)

    def test_timestamps_are_unambiguous_and_ordered(self):
        for value in ("2026-11-03 09:00:20+00:00", "2026-11-03T09:00:20",
                      "2026-11-03T09:00:20.1234567Z", "2026-11-03T08:00:00Z"):
            with self.subTest(value=value):
                self.run["updated_at"] = value
                with self.assertRaises(ValidationError):
                    validate("run", self.run)
        self.run["updated_at"] = "2026-11-03T10:00:20.123456+01:00"
        validate("run", self.run)

    def test_out_of_range_timezone_components_are_not_normalized(self):
        for suffix in ("+00:99", "+01:60", "+24:00", "-00:99", "-01:60"):
            with self.subTest(offset=suffix):
                self.run["updated_at"] = "2026-11-03T13:00:20" + suffix
                with self.assertRaisesRegex(ValidationError, "RFC3339"):
                    validate("run", self.run)

    def test_ambiguous_json_and_nonfinite_numbers_are_rejected(self):
        with self.assertRaisesRegex(ValidationError, "duplicate JSON object key"):
            load_document(io.StringIO('{"version": 1, "version": 2}'))
        document = deepcopy(self.workflow)
        document["schema_version"] = float("nan")
        with self.assertRaisesRegex(ValidationError, "finite"):
            validate("workflow", document)
        document["schema_version"] = True
        with self.assertRaisesRegex(ValidationError, "integer"):
            validate("workflow", document)

    def test_schema_references_resolve_within_the_offline_schema_set(self):
        # Referential integrity only: this deliberately is not a JSON Schema engine.
        schemas = {}
        for path in (REPO_ROOT / "aimium" / "contracts").glob("*.schema.json"):
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn(document["$id"], schemas)
            schemas[document["$id"]] = document

        def check(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    schema_id, separator, pointer = value["$ref"].partition("#")
                    self.assertIn(schema_id, schemas)
                    target = schemas[schema_id]
                    if separator:
                        for part in pointer.split("/")[1:]:
                            target = target[part.replace("~1", "/").replace("~0", "~")]
                for child in value.values():
                    check(child)
            elif isinstance(value, list):
                for child in value:
                    check(child)

        for document in schemas.values():
            check(document)


if __name__ == "__main__":
    unittest.main()
