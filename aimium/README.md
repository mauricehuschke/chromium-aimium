# Aimium

Aimium is a Chromium-based desktop browser project for Windows, Linux and macOS.
Its planned workspace combines a real browser tab with an AI context panel,
multiple user-configured model connectors, and reusable visual workflows.

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
- The architecture, implementation sequence and native validation requirements.

The native WebUI is a foundation screen. It does not yet implement the proposed
left sidebar, connector credentials, model requests, persistent workspaces,
website actions, a graph editor or scheduling. The contracts describe these
future capabilities; passing their checks does not implement the capabilities.

## Development entry points

- [Development and validation](docs/development.md)
- [Architecture](docs/architecture.md)
- [Roadmap and acceptance criteria](docs/roadmap.md)
- [Contracts](contracts/)
- [Examples](examples/)
- [Build tools](tools/)

After a complete Chromium build, launch the development browser with
`--enable-features=Aimium` and open `chrome://aimium`. The feature is disabled
by default. No provider key or external service is required for this screen.

## Product boundaries

The workspace, browser identity, connector binding and workflow run are distinct
objects. A model change must not change the user's website login. Browser
actions target the same Chromium tab the user sees and must be validated against
the current document and the run's authority.

Workflow definitions are versioned. Runs retain their definition, model binding
and observed outcomes. An interrupted external write with an unknown result is
reconciled before another attempt. Local scheduling requires an available local
runtime and an explicit policy for missed triggers.

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
