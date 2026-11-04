# Aimium

Aimium is a Chromium-based desktop browser project for Windows, Linux and macOS.
Every planned product tab is a persistent pair: an agent/context area on the
left and a real website or workflow view on the right. Multiple configurable
model connectors and reusable local workflows are part of the product goal.

## Project continuation / Codex handoff

The owner clarified the vision and implementation priorities on 2026-11-04.
Start with [the complete handoff](docs/codex-handoff.md),
[product vision](docs/product-vision.md),
[verified baseline](docs/current-state.md) and
[phased development plan](docs/development-plan.md).
The first three executable work packages are
[AIM-001](docs/tasks/AIM-001-native-baseline.md),
[AIM-002](docs/tasks/AIM-002-session-pairs.md) and
[AIM-003](docs/tasks/AIM-003-workflows-and-monitor.md).
Repository-wide agent guidance is in [AGENTS.md](../AGENTS.md).

These files are a durable handoff, not evidence that a separate Codex/Work task
has been started. The foundation remains on `codex/aimium-foundation` while its
PR is open; verify current refs before continuing.

## Current milestone: P0 foundation

This milestone establishes the development foundation. It is **not a usable
AI browser release**. The imported Chromium snapshot is a development revision,
not a verified Stable release. Its identity is recorded in [upstream.json](upstream.json).

Included in this milestone:

- A feature-gated native `chrome://aimium` WebUI entry point.
- Versioned contracts and examples for workspaces, connector bindings, workflows,
  runs and browser actions, with executable validation of domain invariants.
- Build planning and environment checks for the three desktop operating systems.
- Lightweight foundation checks and a separately invoked native build path.
- Architecture, implementation sequence and native validation requirements.

The native WebUI is a foundation screen. It does not yet implement the proposed
left sidebar, connector credentials, model requests, persistent workspaces,
website actions, a graph editor or scheduling. The contracts describe these
future capabilities; passing their checks does not implement the capabilities.

## Development entry points

- [Development and validation](docs/development.md)
- [Technical architecture](docs/architecture.md)
- [Roadmap index](docs/roadmap.md)
- [Contracts](contracts/)
- [Examples](examples/)
- [Build tools](tools/)

After a complete Chromium build, launch the development browser with
`--enable-features=Aimium` and open `chrome://aimium`. The feature is disabled
by default. No provider key or external service is required for this screen.

## Product boundaries

The workspace, browser identity, connector binding, workflow activation and
workflow run are distinct objects. A model change must not change the user's
website login. Browser actions target the same Chromium tab the user sees and
must be validated against the current document and the run's authority.

Closing a workspace tab does not delete saved definitions. Website, explorer and
graph views belong to the same pair. Definitions are versioned; running processes
retain their version, bindings and observed outcomes. Unknown external writes
require reconciliation before another attempt.

Browser control, monitoring and workflow execution are local. Initially Aimium
must remain open; later a local headless runtime may work without a window.
Inference is local or remote according to the explicitly chosen model. Optional
subscription models, email services and future definition sync supplement the
product without making local core functionality depend on a cloud account.
See the confirmed vision for the full scope.

These are implementation requirements, not claims about P0 runtime behavior.

## Release status

The inherited Chromium build, names and installer behavior remain the development
baseline. Aimium product branding, separate production profile/install identity,
signing, notarization and automatic product updates are later release gates.
Do not distribute P0 as a production Aimium browser or point a development build
at an existing Chrome profile.

A release requires a verified Stable base, passing native builds and tests on
the supported platforms, and tested installation/update behavior. See the
[development guide](docs/development.md) for the distinction between lightweight
checks and native verification.

## Licensing

The Chromium license and all third-party notices remain applicable. This
directory does not replace or relicense upstream components. See [LICENSE](../LICENSE)
and Chromium's [third-party dependency guidance](../docs/adding_to_third_party.md).
