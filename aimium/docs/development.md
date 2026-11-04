# Aimium development and validation

## Baseline and status

The initial fork contains Chromium `159.0.8142.0` at
`c80042ad683c5620adc9760ec7b5950c80f9d9ce` from Chromium `main`.
[The upstream manifest](../upstream.json) records this as a development snapshot
with `release_eligible: false`. It must not be described as Stable.

P0 introduces a feature-gated WebUI entry point and development contracts/tools.
It does not implement the agent browser product described in the architecture.
In particular, the left sidebar and its browser-session/backend integration are
not available yet.

## Two checkout types

### Foundation-only checkout

A sparse or ordinary Git checkout is sufficient to edit Aimium documentation,
contracts and Python tools and to run the lightweight foundation checks. Those
checks do not compile Chromium, generate GRIT resources, typecheck WebUI with
Chromium's toolchain or execute browser tests.

From the repository root, with Python 3.11 or newer:

```sh
python aimium/contracts/validate.py --examples
python -m unittest discover -s aimium/tests -v
python aimium/tools/build.py plan --target linux-x64
```

The last command prints a build plan without creating an output directory or
running a compiler. The same command supports `win-x64`, `mac-arm64` and
`mac-x64`; generating a plan for another platform is not cross-compilation.

### Complete Chromium development workspace

A native browser build requires a full checkout with the dependencies selected
by Chromium's `DEPS` and a configured `depot_tools` toolchain. Use the instructions
at the chosen source revision:

- [Windows](../../docs/windows_build_instructions.md)
- [Linux](../../docs/linux/build_instructions.md)
- [macOS](../../docs/mac_build_instructions.md)

Use a workspace containing `src/` and a sibling `.gclient`. The `src` solution
should be unmanaged (`"managed": False`), so Git selects the product revision
and `gclient sync` aligns its dependencies. Keep the upstream repository and the
Aimium fork as separate Git remotes. Do not replace a developer's existing
checkout or discard their local changes to make a build work.

Windows builds need the Windows toolchain described by the selected Chromium
revision; public builds must use the appropriate locally installed toolchain.
macOS builds require a Mac with Xcode and the selected SDK. Linux builds require
the documented system dependencies. The imported Windows and Linux instructions
call for at least 100 GB free disk space. A small hosted runner is not an adequate
full Chromium builder.

Provisioned runners may be hosted; owning physical servers is not required.
Build caches must be separated by platform, architecture, toolchain and relevant
build arguments. Credentials and signing material must never be cached with
build outputs.

For a prepared native Linux x64 workspace, use:

```sh
python aimium/tools/build.py check --target linux-x64
python aimium/tools/build.py build --target linux-x64 --dry-run
python aimium/tools/build.py build --target linux-x64
```

Choose the matching native target on Windows or macOS. `check` and the build
dry run perform preflight checks without changing the checkout. They return a
nonzero exit code if prerequisites are missing. A real build requires a clean,
committed source tree, generates its fixed development arguments beneath
`out/Aimium/<target>/`, and writes `aimium-build-manifest.json` there with the
source identity, arguments, commands and outcome. It refuses to overwrite
conflicting existing arguments. It does not fetch dependencies, install tools,
change branches or prepare an installer.

Preflight checks catch common missing prerequisites; GN and the compiler still
determine whether the selected dependencies and SDKs are compatible. A build
builds the `chrome` target by default. Add `--browser-tests` to also build and
run the focused Aimium native smoke tests; their result is recorded separately
under `native_tests`. A manifest with status `built` and native tests marked
`not_run` is not evidence that those tests passed. Neither mode performs
packaging or release validation.

## Reviewable development

Keep product work in short, focused commits on feature branches. Preserve
upstream files where possible, and prefer narrowly scoped registration points
over broad refactoring. Follow the checked-in Chromium style and build rules.

Do not amend commits or rewrite shared history. Integrate a new Chromium base on
a dedicated upgrade branch, resolve conflicts, synchronize dependencies, and
run the appropriate checks before merging the upgrade.

Each upgrade records the selected source SHA and version, channel, dependency
state, build arguments and validation results. The highest Git tag is not
necessarily a Stable release. Confirm the actual channel and platform release
before changing `release_eligible`.

## Native developer screen

The `Aimium` runtime feature is disabled by default. For development, enable it
with `--enable-features=Aimium` and navigate to `chrome://aimium` using a dedicated
development user-data directory. This shows the foundation screen only.

Treat both feature-disabled and feature-enabled behavior as native test cases.
A source review or a green Python job is not evidence that the WebUI compiled,
that GRIT/TypeScript registration succeeded, or that either browser test passed.

The two native smoke tests are registered in `//chrome/test:browser_tests`:
`AimiumUIDisabledBrowserTest.NotAvailable` and
`AimiumUIBrowserTest.LoadsFoundation`. In a prepared workspace, run them with:

```sh
python aimium/tools/build.py build --target linux-x64 --browser-tests
```

This also builds the `browser_tests` Ninja target. For manual invocation, the
focused filter is
`--gtest_filter=AimiumUIBrowserTest.*:AimiumUIDisabledBrowserTest.*`. The enabled
test checks the actual bundled Lit application, not just the page's static
title. Linux runners need the graphical test environment described by Chromium's
testing documentation and the tool's preflight output.

## Required evidence

Record the exact command, source SHA, target, operating system and outcome for
each performed check. A check which could not run is **not run**, never passed.

Before accepting the native milestone, require:

1. The selected desktop browser target builds on Windows, Linux and macOS.
2. The new native browser tests compile and pass in the relevant test binary.
3. `chrome://aimium` loads with the feature enabled and remains unavailable with
   the feature disabled.
4. The existing browser still starts and navigates normally.
5. No provider call, credential access or real website mutation occurs in P0.

The manual native workflow requires explicitly provisioned, suitable runners.
It is separate from ordinary pull-request checks and must not be represented as
a completed platform build simply because its configuration exists.

### GitHub Actions setup

[Foundation checks](../../.github/workflows/aimium-checks.yml) run the Python
tests and example validation on Ubuntu, Windows and macOS. They need neither
provider credentials nor a full Chromium toolchain.

[Native development builds](../../.github/workflows/aimium-native-build.yml)
have a manual trigger and an additional repository-variable gate:
`AIMIUM_NATIVE_BUILDS_ENABLED=true`. Configure the dedicated runner with
`AIMIUM_CHROMIUM_SOURCE` pointing to its complete, synchronized source solution.
The checkout must be clean and at the exact commit selected for the workflow.
Runner labels are `self-hosted`, `aimium`, the platform (`Linux`, `Windows` or
`macOS`) and the CPU (`X64` or `ARM64`), as listed in
[targets.json](../build/targets.json).

The workflow does not provision or synchronize a runner. Linux smoke tests also
require `vpython3`, Xvfb and Openbox. Chromium tools may populate their hermetic
runtime caches; prepare those environments on the runner as part of setup.
Select the optional `browser_tests` input to run the two Aimium tests after the
build. The build receipt stays in the prepared output directory. A skipped
workflow or an unused workflow definition supplies no native validation result.

## Later release gates

P0 is not signed, notarized, branded or packaged as a production Aimium release.
Before distributing the browser, implement and verify a separate application
and profile identity, license notices, the selected Stable baseline, native
integration, signing and installation/update paths. Supply signing identities
through the platform's protected secrets mechanism, never through source files.

Before testing real connectors, use a dedicated development credential with a
deliberate budget. Before testing browser actions on external sites, define the
test identity, target data and authorized operations. The first reproducible
action tests should use a controlled local fixture website.
