#!/usr/bin/env python3
# Copyright 2026 The Aimium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Validate Aimium contract shapes and selected product invariants.

This is a reference validator for the concrete contracts in this directory,
not a general JSON Schema interpreter and not a browser authorization service.
It has no network, browser, credential-store, or workflow execution access.
"""

import argparse
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import ipaddress
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$"
ID_RE = re.compile(ID_PATTERN)
TIMESTAMP_PATTERN = (
    r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])"
    r"T(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)
CAPABILITIES = {
    "text", "vision", "tool_calling", "structured_output", "streaming",
    "async_jobs",
}
VALUE_TYPES = {"string", "number", "boolean", "object", "array"}
ACTIONS = {
    "observe_page", "click", "fill", "select", "scroll", "navigate", "download",
}
RUN_STATES = {
    "queued", "running", "waiting_for_page", "waiting_for_login",
    "waiting_for_input", "paused", "needs_reconciliation", "completed",
    "failed", "cancelled",
}
SECRET_FIELDS = {
    "api_key", "apikey", "password", "cookies", "cookie", "authorization",
    "access_token", "refresh_token", "client_secret", "private_key",
}


class ValidationError(ValueError):
    """A contract violates its concrete shape or a checked domain invariant."""


def _fail(path, message):
    raise ValidationError(f"{path}: {message}")


def _record(value, path, required, optional=()):
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    if missing:
        _fail(path, f"missing fields: {', '.join(sorted(missing))}")
    if extra:
        _fail(path, f"unknown fields: {', '.join(sorted(extra))}")


def _text(value, path, maximum=256):
    if not isinstance(value, str) or not value or len(value) > maximum:
        _fail(path, f"must be nonempty text of at most {maximum} characters")


def _id(value, path):
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        _fail(path, "must be an opaque identifier (1-64 ASCII characters)")


def _integer(value, path, minimum=0, maximum=2**53 - 1):
    if type(value) is not int or not minimum <= value <= maximum:
        _fail(path, f"must be an integer between {minimum} and {maximum}")


def _choice(value, path, choices):
    if not isinstance(value, str) or value not in choices:
        _fail(path, f"must be one of: {', '.join(sorted(choices))}")


def _array(value, path, maximum=256):
    if not isinstance(value, list) or len(value) > maximum:
        _fail(path, f"must be an array with at most {maximum} entries")


def _ids(value, path):
    _array(value, path)
    for index, item in enumerate(value):
        _id(item, f"{path}[{index}]")
    if len(set(value)) != len(value):
        _fail(path, "contains duplicate identifiers")


def _version(document):
    _integer(document["schema_version"], "$.schema_version", 1, 1)


def _no_secret_fields(value, path="$"):
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                _fail(path, "JSON object keys must be strings")
            if key.lower() in SECRET_FIELDS:
                _fail(f"{path}.{key}", "secret payloads are not contract fields")
            _no_secret_fields(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _no_secret_fields(item, f"{path}[{index}]")
    elif isinstance(value, float) and not math.isfinite(value):
        _fail(path, "JSON numbers must be finite")


def _web_url(value, path):
    _text(value, path, 4096)
    if "\\" in value or any(ord(char) <= 32 or ord(char) == 127 for char in value):
        _fail(path, "must not contain whitespace, controls, or backslashes")
    try:
        parsed = urlsplit(value)
        port = parsed.port
        host = parsed.hostname
    except ValueError:
        _fail(path, "contains an invalid URL authority")
    if parsed.scheme not in {"http", "https"} or not host:
        _fail(path, "must be an absolute HTTP(S) URL")
    if parsed.username is not None or parsed.password is not None:
        _fail(path, "embedded credentials are forbidden")
    try:
        host.encode("ascii")
    except UnicodeEncodeError:
        _fail(path, "use a canonical ASCII/IDNA hostname")
    if ":" in host:
        try:
            canonical_host = ipaddress.IPv6Address(host).compressed
        except ValueError:
            _fail(path, "invalid IPv6 address")
        authority = f"[{canonical_host}]"
    else:
        if not re.fullmatch(r"[A-Za-z0-9.-]+", host):
            _fail(path, "invalid hostname")
        authority = host.lower()
    if port is not None and port != (443 if parsed.scheme == "https" else 80):
        authority += f":{port}"
    return parsed, f"{parsed.scheme}://{authority}"


def _origin(value, path):
    _, canonical = _web_url(value, path)
    if value != canonical:
        _fail(path, f"must be a canonical origin without path: {canonical}")


def _origins(value, path, minimum=1):
    _array(value, path, 32)
    if len(value) < minimum:
        _fail(path, "must contain at least one origin")
    for index, origin in enumerate(value):
        _origin(origin, f"{path}[{index}]")
    if len(set(value)) != len(value):
        _fail(path, "contains duplicate origins")


def _capabilities(value, path):
    _array(value, path, len(CAPABILITIES))
    for index, capability in enumerate(value):
        _choice(capability, f"{path}[{index}]", CAPABILITIES)
    if len(set(value)) != len(value):
        _fail(path, "contains duplicate capabilities")


def _binding(value, path):
    _record(value, path, {"connector_id", "model_id", "required_capabilities"})
    _id(value["connector_id"], f"{path}.connector_id")
    _text(value["model_id"], f"{path}.model_id")
    _capabilities(value["required_capabilities"],
                  f"{path}.required_capabilities")


def _workflow_ref(value, path):
    _record(value, path, {"workflow_id", "version"})
    _id(value["workflow_id"], f"{path}.workflow_id")
    _integer(value["version"], f"{path}.version", 1)


def _condition(value, path):
    _record(value, path, {"kind"}, {"value"})
    _choice(value["kind"], f"{path}.kind", {
        "url_equals", "text_present", "element_present",
        "download_completed", "viewport_changed",
    })
    if value["kind"] in {"download_completed", "viewport_changed"}:
        if "value" in value:
            _fail(path, "this condition does not take a value")
    else:
        if "value" not in value:
            _fail(path, "this condition requires a value")
        _text(value["value"], f"{path}.value", 4096)
        if value["kind"] == "url_equals":
            _web_url(value["value"], f"{path}.value")


def validate_connector(document):
    _record(document, "$", {
        "schema_version", "connector_id", "name", "provider", "endpoint",
        "authentication", "data_destination",
    })
    _version(document)
    _id(document["connector_id"], "$.connector_id")
    _text(document["name"], "$.name", 128)
    _choice(document["provider"], "$.provider", {
        "openai", "openrouter", "replicate", "ollama", "openai_compatible",
    })
    _choice(document["data_destination"], "$.data_destination", {
        "local_device", "remote_service", "unknown",
    })
    parsed, _ = _web_url(document["endpoint"], "$.endpoint")
    loopback = parsed.hostname == "localhost"
    try:
        loopback = loopback or ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:
        pass
    if parsed.scheme == "http" and not loopback:
        _fail("$.endpoint", "cleartext endpoints are limited to loopback")
    if parsed.query or parsed.fragment:
        _fail("$.endpoint", "connector endpoints must not contain query or fragment data")
    if document["data_destination"] == "local_device" and not loopback:
        _fail("$.data_destination", "local_device requires a loopback endpoint")
    auth = document["authentication"]
    _record(auth, "$.authentication", {"kind"}, {"secret_ref"})
    _choice(auth["kind"], "$.authentication.kind", {"none", "secret_ref"})
    if auth["kind"] == "secret_ref":
        ref = auth.get("secret_ref")
        if not isinstance(ref, str) or not re.fullmatch(
                r"secret:[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", ref):
            _fail("$.authentication.secret_ref", "must reference a secret-store ID")
    elif "secret_ref" in auth:
        _fail("$.authentication", "auth kind none must not contain a secret ref")
    if document["provider"] in {"openai", "openrouter", "replicate"}:
        if auth["kind"] != "secret_ref":
            _fail("$.authentication", "this provider requires a secret reference")


def _validate_workspace_v1(document):
    _record(document, "$", {
        "schema_version", "workspace_id", "name", "profile_id", "start_url",
        "allowed_origins", "model_binding",
    })
    _version(document)
    for name in ("workspace_id", "profile_id"):
        _id(document[name], f"$.{name}")
    _text(document["name"], "$.name", 128)
    _, start_origin = _web_url(document["start_url"], "$.start_url")
    _origins(document["allowed_origins"], "$.allowed_origins")
    if start_origin not in document["allowed_origins"]:
        _fail("$.start_url", "origin is outside the workspace's agent scope")
    _binding(document["model_binding"], "$.model_binding")


def _validate_workspace_v2(document):
    _record(document, "$", {
        "schema_version", "workspace_id", "name", "profile_id", "start_url",
        "associated_origins", "allowed_origins", "model_binding",
    })
    for name in ("workspace_id", "profile_id"):
        _id(document[name], f"$.{name}")
    _text(document["name"], "$.name", 128)
    _, start_origin = _web_url(document["start_url"], "$.start_url")
    _origins(document["associated_origins"], "$.associated_origins")
    if start_origin not in document["associated_origins"]:
        _fail("$.start_url", "origin is outside the workspace's website associations")
    _origins(document["allowed_origins"], "$.allowed_origins", minimum=0)
    if document["model_binding"] is not None:
        _binding(document["model_binding"], "$.model_binding")


def validate_workspace(document):
    """Dispatch only workspace versions; every other contract remains v1."""
    if not isinstance(document, dict):
        _fail("$", "must be an object")
    if "schema_version" not in document:
        _fail("$", "missing fields: schema_version")
    _integer(document["schema_version"], "$.schema_version", 1, 2)
    if document["schema_version"] == 1:
        _validate_workspace_v1(document)
    else:
        _validate_workspace_v2(document)


def upgrade_workspace(document):
    """Return an independent v2 reference record; never resolve a profile."""
    validate("workspace", document)
    upgraded = deepcopy(document)
    if upgraded["schema_version"] == 1:
        _, start_origin = _web_url(upgraded["start_url"], "$.start_url")
        upgraded["schema_version"] = 2
        # Agent grants can include SSO origins; they are not site suggestions.
        upgraded["associated_origins"] = [start_origin]
    return upgraded


def _node(node, path, model_slots, allowed_actions, current_workflow):
    _record(node, path, {"node_id", "type", "config"})
    _id(node["node_id"], f"{path}.node_id")
    kind, config = node["type"], node["config"]
    shapes = {
        "observe_page": ({"output_key"}, set()),
        "extract_data": ({"source_key", "fields", "output_key"}, set()),
        "ask_model": ({"model_slot", "prompt", "input_keys", "output_key",
                       "output_type"}, set()),
        "browser_action": ({"action", "arguments_key", "output_key"}, set()),
        "assert_state": ({"condition"}, set()),
        "condition": ({"input_key", "operator"}, {"value"}),
        "for_each": ({"items_key", "workflow", "max_iterations", "output_key"},
                     set()),
        "call_workflow": ({"workflow", "input_keys", "output_key"}, set()),
        "wait_for_condition": ({"condition", "timeout_seconds"}, set()),
        "delay": ({"seconds"}, set()),
        "request_input": ({"prompt", "output_key"}, set()),
        "return_result": ({"input_keys"}, set()),
    }
    _choice(kind, f"{path}.type", shapes.keys())
    required, optional = shapes[kind]
    _record(config, f"{path}.config", required, optional)
    for key in ("source_key", "output_key", "model_slot", "arguments_key",
                "input_key", "items_key"):
        if key in config:
            _id(config[key], f"{path}.config.{key}")
    if "input_keys" in config:
        _ids(config["input_keys"], f"{path}.config.input_keys")
    if "prompt" in config:
        _text(config["prompt"], f"{path}.config.prompt", 8192)
    if "condition" in config:
        _condition(config["condition"], f"{path}.config.condition")
    if "workflow" in config:
        _workflow_ref(config["workflow"], f"{path}.config.workflow")
        if config["workflow"]["workflow_id"] == current_workflow:
            _fail(path, "direct recursive workflow calls are not supported")
    if kind == "extract_data":
        _ids(config["fields"], f"{path}.config.fields")
        if not config["fields"]:
            _fail(path, "extraction requires at least one named field")
    elif kind == "ask_model":
        if config["model_slot"] not in model_slots:
            _fail(path, "references an undeclared model slot")
        _choice(config["output_type"], f"{path}.config.output_type", VALUE_TYPES)
    elif kind == "browser_action":
        _choice(config["action"], f"{path}.config.action", ACTIONS)
        if config["action"] not in allowed_actions:
            _fail(path, "action is outside the workflow's declared permissions")
    elif kind == "observe_page" and "observe_page" not in allowed_actions:
        _fail(path, "observe_page is outside the declared permissions")
    elif kind == "condition":
        _choice(config["operator"], f"{path}.config.operator",
                {"equals", "not_equals", "is_true"})
        if config["operator"] == "is_true":
            if "value" in config:
                _fail(path, "is_true does not take a comparison value")
        elif "value" not in config or type(config["value"]) not in {
                str, int, float, bool, type(None)}:
            _fail(path, "comparison requires a scalar value")
    elif kind == "for_each":
        _integer(config["max_iterations"], f"{path}.config.max_iterations",
                 1, 10000)
    elif kind == "wait_for_condition":
        _integer(config["timeout_seconds"], f"{path}.config.timeout_seconds",
                 1, 86400)
    elif kind == "delay":
        _integer(config["seconds"], f"{path}.config.seconds", 1, 604800)


def _inputs(node):
    config = node["config"]
    names = list(config.get("input_keys", []))
    names.extend(config[key] for key in (
        "source_key", "arguments_key", "input_key", "items_key") if key in config)
    return set(names)


def validate_workflow(document):
    _record(document, "$", {
        "schema_version", "workflow_id", "version", "name", "browser_slot",
        "model_slots", "input_keys", "entry_node_id", "permissions", "limits",
        "nodes", "edges",
    })
    _version(document)
    for key in ("workflow_id", "browser_slot", "entry_node_id"):
        _id(document[key], f"$.{key}")
    _integer(document["version"], "$.version", 1)
    _text(document["name"], "$.name", 128)
    _ids(document["input_keys"], "$.input_keys")
    slots = document["model_slots"]
    if not isinstance(slots, dict) or len(slots) > 16:
        _fail("$.model_slots", "must be an object with at most 16 model slots")
    for name, slot in slots.items():
        _id(name, "$.model_slots key")
        _record(slot, f"$.model_slots.{name}", {"required_capabilities"})
        _capabilities(slot["required_capabilities"],
                      f"$.model_slots.{name}.required_capabilities")
    permissions = document["permissions"]
    _record(permissions, "$.permissions",
            {"allowed_origins", "allowed_actions", "max_actions"})
    _origins(permissions["allowed_origins"], "$.permissions.allowed_origins")
    _array(permissions["allowed_actions"], "$.permissions.allowed_actions", 7)
    for item in permissions["allowed_actions"]:
        _choice(item, "$.permissions.allowed_actions", ACTIONS)
    if len(set(permissions["allowed_actions"])) != len(permissions["allowed_actions"]):
        _fail("$.permissions.allowed_actions", "contains duplicates")
    _integer(permissions["max_actions"], "$.permissions.max_actions", 0, 10000)
    limits = document["limits"]
    _record(limits, "$.limits", {"max_steps", "max_duration_seconds"})
    _integer(limits["max_steps"], "$.limits.max_steps", 1, 100000)
    _integer(limits["max_duration_seconds"],
             "$.limits.max_duration_seconds", 1, 604800)
    _array(document["nodes"], "$.nodes", 256)
    _array(document["edges"], "$.edges", 1024)
    if not document["nodes"]:
        _fail("$.nodes", "must not be empty")
    nodes = {}
    outputs = set(document["input_keys"])
    for index, node in enumerate(document["nodes"]):
        _node(node, f"$.nodes[{index}]", slots, permissions["allowed_actions"],
              document["workflow_id"])
        name = node["node_id"]
        if name in nodes:
            _fail("$.nodes", f"duplicate node ID {name}")
        nodes[name] = node
        output = node["config"].get("output_key")
        if output is not None:
            if output in outputs:
                _fail("$.nodes", f"output {output} is assigned more than once")
            outputs.add(output)
    if document["entry_node_id"] not in nodes:
        _fail("$.entry_node_id", "does not identify a node")
    outgoing = {name: {} for name in nodes}
    incoming = {name: [] for name in nodes}
    for index, edge in enumerate(document["edges"]):
        path = f"$.edges[{index}]"
        _record(edge, path, {"from", "port", "to"})
        for key in ("from", "to"):
            _id(edge[key], f"{path}.{key}")
            if edge[key] not in nodes:
                _fail(path, "edge references a missing node")
        _choice(edge["port"], f"{path}.port", {"success", "error", "true", "false"})
        if edge["port"] in outgoing[edge["from"]]:
            _fail(path, "an output port may have only one successor")
        outgoing[edge["from"]][edge["port"]] = edge["to"]
        incoming[edge["to"]].append(edge)
    if incoming[document["entry_node_id"]]:
        _fail("$.entry_node_id", "entry must not have incoming edges")
    for name, node in nodes.items():
        ports = set(outgoing[name])
        if node["type"] == "return_result":
            if ports:
                _fail(f"$.nodes.{name}", "terminal node has outgoing edges")
        elif node["type"] == "condition":
            if ports != {"true", "false"}:
                _fail(f"$.nodes.{name}", "condition requires true and false ports")
        elif "success" not in ports or ports - {"success", "error"}:
            _fail(f"$.nodes.{name}", "requires success and optional error ports")
    # An acyclic outer graph makes resume semantics explicit. Repetition uses
    # bounded for_each nodes calling an immutable subworkflow version.
    ready = [document["entry_node_id"]]
    available = {document["entry_node_id"]: set(document["input_keys"])}
    visited = set()
    while ready:
        name = ready.pop()
        if name in visited:
            continue
        visited.add(name)
        node = nodes[name]
        missing = _inputs(node) - available[name]
        if missing:
            _fail(f"$.nodes.{name}", f"inputs unavailable on every path: {sorted(missing)}")
        for target in outgoing[name].values():
            if all(edge["from"] in visited for edge in incoming[target]):
                paths = []
                for edge in incoming[target]:
                    parent = edge["from"]
                    produced = set(available[parent])
                    output = nodes[parent]["config"].get("output_key")
                    if output is not None and edge["port"] == "success":
                        produced.add(output)
                    paths.append(produced)
                available[target] = set.intersection(*paths)
                ready.append(target)
    if visited != nodes.keys():
        _fail("$.edges", "graph has a cycle or an unreachable node")


def validate_action(document):
    _record(document, "$", {
        "schema_version", "action_id", "run_id", "workspace_id", "profile_id",
        "tab_id", "document_generation", "observation_id", "lease_generation",
        "origin", "kind", "arguments",
    }, {"target", "expectation"})
    _version(document)
    for key in ("action_id", "run_id", "workspace_id", "profile_id", "tab_id",
                "observation_id"):
        _id(document[key], f"$.{key}")
    for key in ("document_generation", "lease_generation"):
        _integer(document[key], f"$.{key}", 1)
    _origin(document["origin"], "$.origin")
    kind, args = document["kind"], document["arguments"]
    _choice(kind, "$.kind", ACTIONS)
    arg_fields = {
        "observe_page": set(), "click": set(), "fill": {"text"},
        "select": {"value"}, "scroll": {"delta_x", "delta_y"},
        "navigate": {"url"}, "download": {"artifact_name"},
    }
    _record(args, "$.arguments", arg_fields[kind])
    needs_element = kind in {"click", "fill", "select", "download"}
    if needs_element != ("target" in document):
        _fail("$.target", "element target is required only for element actions")
    if needs_element:
        target = document["target"]
        _record(target, "$.target", {"element_id", "observation_id"})
        for key in target:
            _id(target[key], f"$.target.{key}")
        if target["observation_id"] != document["observation_id"]:
            _fail("$.target.observation_id", "does not match the action observation")
    if kind != "observe_page" and "expectation" not in document:
        _fail("$.expectation", "mutating actions require a postcondition")
    if "expectation" in document:
        _condition(document["expectation"], "$.expectation")
    if kind == "fill":
        if not isinstance(args["text"], str) or len(args["text"]) > 16384:
            _fail("$.arguments.text", "must be text of at most 16384 characters")
    elif kind == "select":
        _text(args["value"], "$.arguments.value", 4096)
    elif kind == "navigate":
        _web_url(args["url"], "$.arguments.url")
    elif kind == "scroll":
        for key in ("delta_x", "delta_y"):
            _integer(args[key], f"$.arguments.{key}", -10000, 10000)
        if not args["delta_x"] and not args["delta_y"]:
            _fail("$.arguments", "scroll must have a nonzero delta")
    elif kind == "download":
        name = args["artifact_name"]
        if not isinstance(name, str) or not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", name):
            _fail("$.arguments.artifact_name", "must be an opaque artifact name")


@dataclass(frozen=True)
class ActionAuthority:
    """Trusted test/reference inputs; production values must come from Chromium."""

    run_id: str
    workspace_id: str
    profile_id: str
    tab_id: str
    document_generation: int
    observation_id: str
    lease_generation: int
    origin: str
    allowed_origins: frozenset
    allowed_actions: frozenset
    active: bool = True


def validate_action_binding(document, authority):
    """Check a request against trusted current state, without executing it."""
    validate("action", document)
    if not authority.active:
        _fail("$", "the run no longer owns an active action lease")
    for key in ("run_id", "workspace_id", "profile_id", "tab_id",
                "document_generation", "observation_id", "lease_generation",
                "origin"):
        if document[key] != getattr(authority, key):
            _fail(f"$.{key}", "does not match the current browser authority")
    if document["origin"] not in authority.allowed_origins:
        _fail("$.origin", "origin is outside the action authority")
    if document["kind"] not in authority.allowed_actions:
        _fail("$.kind", "action is outside the action authority")
    if document["kind"] == "navigate":
        _, destination = _web_url(document["arguments"]["url"], "$.arguments.url")
        if destination not in authority.allowed_origins:
            _fail("$.arguments.url", "destination is outside the action authority")


def validate_run(document):
    _record(document, "$", {
        "schema_version", "run_id", "workflow", "workspace_id", "profile_id",
        "model_bindings", "status", "current_node_id", "completed_node_ids",
        "pending_action_id", "last_action_outcome", "event_sequence",
        "created_at", "updated_at",
    })
    _version(document)
    for key in ("run_id", "workspace_id", "profile_id"):
        _id(document[key], f"$.{key}")
    _workflow_ref(document["workflow"], "$.workflow")
    bindings = document["model_bindings"]
    if not isinstance(bindings, dict) or len(bindings) > 16:
        _fail("$.model_bindings", "must contain at most 16 model bindings")
    for name, binding in bindings.items():
        _id(name, "$.model_bindings key")
        _binding(binding, f"$.model_bindings.{name}")
    _choice(document["status"], "$.status", RUN_STATES)
    _ids(document["completed_node_ids"], "$.completed_node_ids")
    for key in ("current_node_id", "pending_action_id"):
        if document[key] is not None:
            _id(document[key], f"$.{key}")
    if document["current_node_id"] in document["completed_node_ids"]:
        _fail("$.current_node_id", "a completed node cannot also be current")
    _integer(document["event_sequence"], "$.event_sequence")
    _choice(document["last_action_outcome"], "$.last_action_outcome",
            {"none", "pending", "confirmed", "unknown"})
    outcome, status = document["last_action_outcome"], document["status"]
    if (outcome in {"pending", "unknown"}) != (document["pending_action_id"] is not None):
        _fail("$.pending_action_id", "must identify exactly a pending or unknown action")
    if (outcome == "unknown") != (status == "needs_reconciliation"):
        _fail("$.status", "unknown external outcomes require needs_reconciliation")
    if outcome == "pending" and status not in {"running", "waiting_for_page"}:
        _fail("$.status", "pending actions cannot be reported as stopped or finished")
    if status in {"queued", "completed"}:
        if document["current_node_id"] is not None:
            _fail("$.current_node_id", "queued/completed runs have no current node")
        if status == "queued" and (document["completed_node_ids"] or outcome != "none"):
            _fail("$.status", "a queued run cannot already have executed work")
    elif status not in {"failed", "cancelled"} and document["current_node_id"] is None:
        _fail("$.current_node_id", "active or paused runs require a current node")
    times = []
    for key in ("created_at", "updated_at"):
        _text(document[key], f"$.{key}", 64)
        if not re.fullmatch(TIMESTAMP_PATTERN, document[key]):
            _fail(f"$.{key}", "requires RFC3339 seconds and an explicit timezone")
        try:
            value = datetime.fromisoformat(document[key].replace("Z", "+00:00"))
        except ValueError:
            _fail(f"$.{key}", "must be an ISO 8601 timestamp with timezone")
        if value.tzinfo is None:
            _fail(f"$.{key}", "timestamp must include a timezone")
        times.append(value)
    if times[1] < times[0]:
        _fail("$.updated_at", "must not precede creation")


def validate_run_binding(run, workflow, workspace):
    """Validate references against the exact saved process and workspace."""
    validate("run", run)
    validate("workflow", workflow)
    validate("workspace", workspace)
    if run["workflow"] != {"workflow_id": workflow["workflow_id"],
                           "version": workflow["version"]}:
        _fail("$.workflow", "run does not reference this immutable workflow version")
    for key in ("workspace_id", "profile_id"):
        if run[key] != workspace[key]:
            _fail(f"$.{key}", "does not match the workspace")
    node_ids = {node["node_id"] for node in workflow["nodes"]}
    used = set(run["completed_node_ids"])
    if run["current_node_id"] is not None:
        used.add(run["current_node_id"])
    if not used <= node_ids:
        _fail("$.current_node_id", "run references nodes absent from this workflow")
    if set(run["model_bindings"]) != set(workflow["model_slots"]):
        _fail("$.model_bindings", "must resolve exactly the workflow's model slots")
    for name, slot in workflow["model_slots"].items():
        requested = set(slot["required_capabilities"])
        if not requested <= set(run["model_bindings"][name]["required_capabilities"]):
            _fail(f"$.model_bindings.{name}", "binding omits a required capability")
    if not set(workflow["permissions"]["allowed_origins"]) <= set(
            workspace["allowed_origins"]):
        _fail("$.workflow", "workflow origins exceed the workspace's agent scope")


VALIDATORS = {
    "connector": validate_connector, "workspace": validate_workspace,
    "workflow": validate_workflow, "action": validate_action, "run": validate_run,
}


def validate(kind, document):
    if kind not in VALIDATORS:
        _fail("$", f"unknown contract kind {kind!r}")
    _no_secret_fields(document)
    VALIDATORS[kind](document)


def _unique_object(pairs):
    """Reject ambiguous duplicate keys at the JSON file boundary."""
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("$", f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def load_document(source):
    """Read a JSON contract without silently overwriting duplicate keys."""
    return json.load(source, object_pairs_hook=_unique_object)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", nargs="?", choices=sorted(VALIDATORS))
    parser.add_argument("document", nargs="?", type=Path)
    parser.add_argument("--examples", action="store_true")
    args = parser.parse_args(argv)
    if args.examples:
        if args.kind or args.document:
            parser.error("--examples cannot be combined with a document")
        examples = Path(__file__).resolve().parents[1] / "examples" / "contracts"
        files = [(path.name.split(".")[0], path)
                 for path in sorted(examples.glob("*.json"))]
        if not files:
            parser.error("no contract examples found")
    else:
        if not args.kind or not args.document:
            parser.error("provide KIND DOCUMENT or --examples")
        files = [(args.kind, args.document)]
    try:
        for kind, path in files:
            with path.open(encoding="utf-8") as source:
                document = load_document(source)
            validate(kind, document)
            print(f"PASS {kind}: {path.name}")
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
