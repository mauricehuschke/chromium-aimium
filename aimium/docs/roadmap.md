# Aimium implementation roadmap

This sequence makes each milestone demonstrable before the next subsystem is
added. It describes acceptance criteria, not a delivery-date commitment. Native
Windows, Linux and macOS validation stays part of the project throughout;
progress on one host is not evidence that the other targets work.

## P0 — Source foundation

**Current status: source foundation implemented; native build and browser-test
acceptance pending. No usable AI browser is delivered by P0.**

Included source and lightweight checks:

- A default-disabled `Aimium` feature and native `chrome://aimium` foundation
  page, with source for enabled/disabled browser smoke tests.
- Versioned workspace, connector, workflow, run and action schemas with examples.
- Dependency-free reference checks for concrete shapes, graph/data dependencies,
  scope/generation binding and unknown external outcomes.
- Build plans/preflight tooling and separate lightweight/native CI paths.
- A recorded Chromium base and a clear separation between architecture and
  implemented functionality.

The native acceptance gate requires complete Chromium toolchains and dependencies
on the target platforms. Build the browser and browser-test target, execute the
feature-on and feature-off smoke tests, and verify ordinary browser startup and
navigation. Record exact source revisions and results. The lightweight checks
do not compile C++, generate WebUI resources or execute native browser tests.

The imported base is Chromium main development code. Transition to a **verified
Stable release** and preserve a small, reviewable Aimium patch set before any
public product build. The native runner/workflow definition itself is not proof
that a native build has run.

## P1 — Persistent workspace and native left panel

Implement native browser layout and a panel bound to the real visible tab.
Create the workspace/profile service, explicit model-binding settings and local
workspace persistence. Establish a distinct development/product profile identity
before opening real accounts. Add scope controls and lifecycle events for tab
switching, navigation, login changes and profile shutdown.

Acceptance:

- A workspace reopens the intended site/profile after restart.
- Separate workspace identities can deliberately share or isolate profiles;
  sharing is explicit and visible.
- Changing the selected connector/model preserves the website session.
- The panel follows the intended tab and never silently attaches to another
  account or tab after navigation, tab closure or restart.
- Windows, Linux and macOS exercise the same workspace scenarios.

Use this milestone to measure a baseline for startup, memory and storage before
removing optional features. Each later slimming change has its own measured
benefit and compatibility test.

## P2 — Connector service and read-only assistance

Add the native connector/credential services and context projection. Implement
one remote adapter and one local adapter first, then add OpenRouter/Replicate
and other declared providers through the same tested capability boundary. The
adapter order is an implementation choice; the final product supports multiple
simultaneously configured connectors and explicit selection per workspace/run.

Acceptance:

- Two configured connectors can be selected without changing browser identity.
- Credentials never enter page scripts, prompts, diagnostic payloads or exported
  templates; storage behavior is verified on each platform.
- The UI shows the provider destination and exact categories of context sent.
- Cancellation, streaming, errors, usage limits and unsupported capabilities are
  tested with deterministic fixtures and provider-specific integration tests.
- No implicit provider fallback sends data to a different destination.

Read-only page explanation and extraction precede external website mutations.

## P3 — Controlled actions on the visible tab

Implement the observation service, typed action broker, trusted authority checks,
per-tab lease and postcondition observation. Start on a controlled fixture site
with login, navigation, dynamic content and intentionally stale targets. Add
human takeover, pause/cancel, origin restrictions and confirmation policy before
external-site action testing.

Acceptance:

- The assistant acts on the same tab the user sees and only within its scope.
- A stale model response after navigation, cancellation or lease transfer is
  rejected. Same-URL content changes and stale element references are covered.
- Page text cannot widen authority, change provider destinations or cause
  privileged JavaScript/shell execution.
- Action IDs, intent and observed outcomes survive interruption. An uncertain
  external effect stops for reconciliation rather than blind repetition.
- Downloads are confined to managed artifact handling. Redirects, frames,
  popups, login expiry and human interactions have explicit behavior.

Site-knowledge revisions can begin here after observation semantics are stable.
Knowledge changes remain inspectable and do not silently retrain a provider.

## P4 — Durable reusable workflows and graph editor

Build the native workflow store and executor before relying on a visual editor.
Implement immutable versions, schema migrations, registry-wide dependency and
recursion checks, typed runtime values and effective budgets for nested calls.
Then add graph editing, templates, bindings, run inspection and debugging.

Acceptance:

- The editor saves valid workflow documents, shows validation failures at the
  relevant node and can reopen a saved process without losing meaning.
- Branches, bounded loops, subworkflows, input pauses, errors and timeouts behave
  deterministically against controlled fixtures.
- Restart resumes from durable state; event sequences and action identities
  cannot be duplicated or rewritten by a late response.
- A running process retains its workflow and model bindings when the user edits
  the next process version.
- Export constructs a reviewed template without cookies, credentials, local
  account identity or run artifacts. Free text is reviewed separately; passing
  a field-name validator is not treated as proof of secrecy.

## P5 — Time and event triggers

Add local scheduling and defined event sources on top of durable execution.
Choose the runtime availability model, implement timezone handling, missed-run
rules, overlap/resource locks, backlog limits and event deduplication. Specify
the trigger schema after these semantics are decided.

Acceptance:

- Restart, sleep/wake, clock changes and duplicate events do not silently create
  duplicate external effects.
- The UI states whether the runtime must be open and what happens to missed
  triggers.
- Disabling a schedule prevents new runs; cancellation revokes future action
  authority while retaining any unresolved external outcome.
- Runs sharing a tab or remote account obey the selected overlap policy.

An unattended remote runner would be a separate product/deployment scope; local
scheduling does not imply a cloud service or execution while a device is off.

## P6 — Release engineering and supported distribution

Complete product branding, separate application/profile identities, installation,
signing, macOS notarization, update delivery and rollback/recovery behavior.
Review Chromium and third-party notices and verify functionality tied to
upstream services before making distribution claims.

The initial build target set is Windows x64, Linux x64, macOS arm64 and macOS
x64. Additional architectures need an explicit support decision and their own
native evidence. The target list is not a compatibility certification.

Release acceptance requires:

- A verified Stable base, reproducible source/build identity and a rehearsed
  Chromium security-update process.
- Passing native tests and representative website/session workflows across all
  supported targets.
- Tested installer, profile migration, automatic update and recovery paths with
  real signed artifacts.
- Provider, workflow and security-boundary regression suites, plus measured
  resource usage and justified slimming decisions.

Do not equate a successful build with a tested installer, a working updater or
an approved production release. Track those outcomes independently in the
release record.
