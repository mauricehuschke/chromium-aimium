# Aimium repository guidance

This repository is a Chromium fork, not a browser extension or an Electron app.
Preserve upstream licensing, directory conventions and applicable local guidance.

## Start here

For Aimium work read `aimium/docs/codex-handoff.md`, the assigned task, and the
relevant parts of `aimium/docs/product-vision.md` and
`aimium/docs/development-plan.md`. `aimium/docs/current-state.md` is a dated
evidence snapshot: verify the actual branch/commit and CI before relying on it.
The agreed product clarification and phase ordering supersede the old roadmap;
`aimium/docs/architecture.md` still describes the intended technical boundaries.
Do not confuse a proposed architecture, a schema or a mock with implemented
runtime behavior. Keep summaries to the owner in German; code identifiers and
upstream-facing comments may remain English.

## Product invariants

- A product tab is always a saved pair: agent/context on the left, real website
  or workflow view on the right. No separate conventional browsing mode.
- Switching the right view must not replace the authenticated website with an
  iframe or an unrelated automation session. Closing a tab is not deleting its
  workspace, workflows or history.
- Browser identity is independent of connector/model selection. Multiple
  workspaces and multiple workflows per workspace are required.
- Browser actions, monitoring and workflow execution run locally in the user's
  browser context. Initially Aimium must be open. Local headless execution comes
  later. Local inference stays local; explicitly selected remote providers
  receive only approved context. No silent provider fallback.
- Optional subscription models, email services and later sync supplement the
  product. They are not a prerequisite for local core functionality.
- Workflow activation/trigger waiting is distinct from a concrete run. The
  monitor must show actual node position, waiting reason and execution history.
- Keep one checked browser-action boundary for manual workflows and AI actions.
  Enforce authority, stale observation rejection, human takeover and cancellation
  in native code, not only in a prompt. Unknown external outcomes require
  reconciliation, never an unconditional retry.

## Public repository boundary

This repository is public. Before staging or pushing, review the actual diff
and every added artifact for private or machine-specific information. Never
commit real local absolute paths, user or machine names, host inventories,
installation/admin history, local environment files, trust-store exports,
credentials, browser profiles, raw logs, build manifests or session diagnostics.
Keep detailed execution evidence outside the versioned source tree. Public
documentation uses repository-relative paths, environment variables and clearly
synthetic fixtures; publish only reviewed project-level status and results.
An ignore rule or a simple secret-pattern scan does not replace this review.
If private data was published, removing it from the latest tree is insufficient;
coordinate an explicitly authorized history cleanup and account for other refs,
caches and clones. Do not reintroduce pre-cleanup history by merging old clones.

## Local execution

Tests and builds stay local. GitHub Actions
is disabled for this repository; preserve the existing completed runs and logs.
Do not enable, dispatch or rerun Actions without a new explicit owner request.
The owner starts native builds from VS Code when needed. Agents must not start
or restart native builds, GN generation, compilers or linkers on their own.
Lightweight local unit/contract checks remain available for relevant changes.
Preserve the existing Ninja output directory and valid intermediate results;
never clean them merely to restart a build. Record unexecuted native checks as
NOT_RUN and hand the actual build execution to the owner.

Use one reviewable work package at a time. Start with AIM-001 unless the latest
verified state proves its gates already satisfied. Record evidence and blockers;
do not silently skip a native acceptance gate to report a later phase as done.
Independent contract/test design may proceed while a runner is blocked, but
native integration remains unaccepted until tested.

Keep upstream edits narrow. Do not remove Chromium subsystems in a foundation
or session ticket. Never weaken sandboxing, certificate validation or site
isolation to make a test pass. Do not use real personal accounts for fixtures.
Secrets, cookies, profiles, provider keys and raw browsing data do not belong in
commits, exported templates or diagnostic attachments.

Do not reset user work, force-push, merge the foundation PR, change the default
branch, purchase infrastructure, enable paid providers, or publish/sign a release
without appropriate owner authorization. New implementation work goes on a
branch based on the latest handoff branch. No background coding task is implied
by the presence of this file.

## Validation

From the source root, with Python 3.11+:

```sh
python -m unittest discover -s aimium/tests -p 'test_*.py' -v
python aimium/contracts/validate.py --examples
python aimium/tools/build.py plan --target linux-x64
```

Use the target appropriate to the host for `check` and `build`. See
`aimium/docs/development.md`. A sparse checkout is suitable for lightweight
checks, not native compilation. Native builds need a full gclient workspace,
matching dependencies/toolchains and enough resources. A build must retain its
exact source identity and use a separate development profile. Test output must
prove tests were discovered and executed; an empty filter is not success.

A green Python workflow does not prove C++ compilation, WebUI resource generation,
TypeScript compilation, browser startup, packaging or support on other platforms.
The Python contract validator is a reference/development tool, not a production
workflow backend to ship in Aimium.

## Completion report

For each package report task ID, base/head SHA, changed files, implemented
behavior, portable commands, passed/failed/not-run results per platform, blockers,
remaining acceptance criteria, and the next eligible package. Update the task
status with a public-safe summary; keep host-specific evidence outside Git.
Do not convert historical results into fresh
claims. Preserve `release_eligible: false` until actual release gates pass.
