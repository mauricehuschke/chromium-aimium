# Aimium v1 contracts

These files establish exchange formats and executable reference checks for the
planned browser. They do not connect a model, open a profile, run a workflow or
authorize a real browser action. The native P0 screen does not consume these
contracts yet.

## Files and boundaries

| Contract | Meaning | Intended storage |
| --- | --- | --- |
| `connector.schema.json` | Provider, endpoint and opaque credential reference | Local configuration |
| `workspace.schema.json` | Website, browser profile identity, agent origin scope and selected model | Local configuration |
| `workflow.schema.json` | One immutable process version with symbolic browser/model slots | Reviewed reusable template |
| `run.schema.json` | Execution snapshot pinned to a process version and resolved bindings | Local execution store |
| `action.schema.json` | Request tied to one run, tab, document, observation and lease | Transient/local execution record |
| `common.schema.json` | Shared structural definitions | Schema registry |

The JSON Schemas use Draft 2020-12. Register the six files by their `$id` URNs in
an offline schema registry. All `$ref` targets are contained in this set; schema
validation does not need network retrieval. A standards-compliant schema
validator remains the appropriate tool for generic JSON Schema validation.

`validate.py` is a dependency-free validator for these specific contracts. It
checks their concrete v1 shapes and selected domain invariants. It is **not a
general JSON Schema implementation**. The test suite checks example behavior,
domain failures and offline reference integrity; it does not claim independent
Draft 2020-12 metaschema conformance testing.

Run from the repository root with Python 3.11 or newer:

```sh
python aimium/contracts/validate.py --examples
python aimium/contracts/validate.py workflow aimium/examples/contracts/workflow.task.json
python -m unittest discover -s aimium/tests -p 'test_*.py'
```

The CLI returns 0 for valid documents, 1 for document/validation errors and 2 for
invalid command arguments. Duplicate object keys, nonfinite numbers and unknown
fields are rejected rather than silently interpreted. Diagnostics identify the
relevant field or graph node.

## Identity, configuration and credential references

A workspace has its own `workspace_id`, a separate `profile_id`, and a
`model_binding`. Changing `model_binding` must preserve `profile_id`. A future
profile service must resolve that opaque ID to Chromium-owned browser state;
the field is not a filesystem path and does not create a profile today.

A model binding names a connector, a provider-specific model ID and required
capabilities. A workflow uses named model slots; a run resolves every slot once.
Required capabilities are requirements, not verified provider claims. P0 has no
connector registry, model discovery or capability negotiation. Do not silently
fall back to another provider when a request fails.

A connector stores a `secret:opaque-id` reference when authentication is needed.
The actual credential belongs in a future local credential service and must not
be stored in a contract, workflow template or source file. P0 never resolves the
reference. Connector endpoints cannot embed credentials, queries or fragments;
cleartext HTTP is limited to loopback endpoints. `local_device` requires a
loopback endpoint, but this is **not proof that the service keeps data local**:
a process listening on loopback may forward traffic elsewhere.

The examples use synthetic identities, a reserved example website and a
placeholder model name. They cannot be executed against a real website. The
remote connector example names an endpoint to illustrate configuration only;
no request is sent during validation.

### Export and sensitive data

The workflow contract has symbolic browser/model slots and has no cookie,
profile, connector-secret or execution-history field. Importing a workflow will
require the user to bind its slots and accept its declared origin/action scope.
Local workspace, connector, run and action records are not portable templates.

The reference validator recursively rejects known credential/cookie field names
such as `api_key`, `authorization`, `cookies` and `refresh_token`. This is a
structural guard, **not a secret or personal-data scanner**. Free-form prompts,
fill text, names, URLs and other string values can still contain sensitive data.
Passing validation is not evidence that a document is safe to share. A future
exporter must construct an explicit template projection, omit runtime artifacts,
and provide a review of the actual text being exported. P0 has no exporter.

## Workflow semantics

`schema_version` versions the exchange format. `(workflow_id, version)` identifies
one saved process definition. Editing a saved definition must create a new
workflow version. The shape requires a version number; immutability itself needs
a future store that rejects a different body under an existing ID/version.

The outer control-flow graph is acyclic. Every node must be reachable from the
entry, and each source port has at most one successor. This v1 graph is
sequential; converging edges do not imply concurrent workers or an asynchronous
join. Ordinary nodes have a `success` edge and may have an `error` edge. A
`condition` has exactly `true` and `false` edges. A `return_result` is terminal.
An unhandled node failure ends execution; an ambiguous external action outcome
must instead stop for reconciliation before following any retry path.

| Node | Declared role |
| --- | --- |
| `observe_page` | Capture a permitted page observation |
| `extract_data` | Select named fields from an available observation/result |
| `ask_model` | Request one declared output type from a named model slot |
| `browser_action` | Propose one allowed browser action using an available value |
| `assert_state` | Require a named observable condition |
| `condition` | Choose a branch using a scalar comparison |
| `for_each` | Sequentially invoke a pinned body workflow with a fixed iteration cap |
| `call_workflow` | Invoke a pinned reusable workflow |
| `wait_for_condition` | Wait for an observable condition with a timeout |
| `delay` | Wait for a bounded duration |
| `request_input` | Pause for explicit user input |
| `return_result` | Finish the current workflow with available values |

There is no arbitrary node implementation, JavaScript evaluator, shell command
or extension-loading node in v1. A prompt containing code is still text; it does
not become an executable node.

Every output key is assigned once. A node may read only initial inputs and
outputs guaranteed to exist on **every** path reaching it. A failed node does
not produce its success output. This prevents a branch join or error route from
reading a result that might never have been created.

`for_each` names an immutable body workflow and `max_iterations`. The intended
body input convention is `item` and `index`; results are collected into the
declared output. `call_workflow` passes its named inputs. The future loader must
resolve those workflows, validate their input/model bindings and effective
permissions, reject indirect recursion across the full dependency graph, and
apply parent budgets to all nested work. P0 validates each document and rejects
direct recursive calls, but does not implement that registry-wide loader.

The action, step, iteration and duration limits are declarations. Enforcing them
requires an executor that persists consumed budgets, including nested calls and
retries. Structural validation is not enforcement. Runtime value typing,
provider output validation, selection semantics for extracted fields, schema
migrations and dependency-registry checks remain later implementation work.

## Run and action invariants

`validate_run_binding(run, workflow, workspace)` checks an execution snapshot
against the exact workflow version and workspace. It verifies profile identity,
node references, model-slot coverage, required capability declarations and
origin-scope containment. The supplied objects are reference inputs; this does
not establish that a credential, connector, model, tab or saved workflow exists.

Run timestamps use an explicit RFC3339 subset: uppercase `T`/`Z`, seconds,
optional one to six fractional digits, and a timezone. Leap seconds are not
accepted. The update time cannot precede creation. `event_sequence` is a
snapshot field; a durable store must enforce monotonic changes between records.
The validator does not validate a history of state transitions.

An action request carries an `action_id` and binds to:

- The run, workspace and browser profile.
- The exact visible tab, current origin and document generation.
- The observation that supplied its element references.
- The current action-lease generation.

`validate_action_binding(action, ActionAuthority(...))` rejects a mismatched or
inactive scope and navigation beyond the permitted destination origins. In a
real implementation, the browser process must create this authority from
trusted state. Neither a model nor a webpage may supply or overwrite it. This
Python dataclass is a reference/test input, not an authorization token.

The current allowlist is `observe_page`, `click`, `fill`, `select`, `scroll`,
`navigate` and `download`. Element actions require an observation-bound target;
mutating actions require an expected result. Downloads use an opaque artifact
name, not an arbitrary destination path. The future broker must resolve those
names, enforce frame/document identity, reject stale elements, account for
redirects/popups and validate observed postconditions. None of that browser
execution exists in P0.

An action ID alone does not deduplicate execution. The future executor needs a
durable action journal and a reconciliation policy. A postcondition such as
visible text can already have been true before an action; it is not a universal
proof of a uniquely completed remote write.

### Unknown external outcomes

The example `run.unknown-outcome.json` represents a request that may have taken
effect before its result became unavailable. It keeps the original
`pending_action_id`, marks `last_action_outcome` as `unknown`, and requires the
run state `needs_reconciliation`.

Such a snapshot cannot be labeled completed, failed or cancelled merely to
clear an in-flight action. Cancellation must revoke future action authority;
it cannot undo a remote write that already happened. Reconciliation inspects
the external state or asks the user before another attempt. No exactly-once
guarantee is implied by these contracts.

## Scope of the checks

The tests exercise meaningful reference behavior: profile/model separation,
graph reachability and branches, bounded repetition, declared capabilities and
permissions, stale document/lease rejection, cross-profile isolation, navigation
scope, uncertain outcomes and strict JSON/timestamp handling.

They are not browser integration tests, provider conformance tests, cryptographic
credential tests, a security audit or evidence of a functioning scheduler.
See the [architecture](../docs/architecture.md) and
[roadmap](../docs/roadmap.md) for the implementation sequence.
