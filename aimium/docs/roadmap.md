# Aimium implementation roadmap

Updated 2026-11-04 after the owner clarified the product vision and prioritized
usable per-session workflows with a real execution monitor.

The authoritative phased plan is now
[development-plan.md](development-plan.md). It replaces the earlier ordering in
this file; older P2/P3/P4 phase numbers must not be reused without their titles.

Start with the [Codex handoff](codex-handoff.md),
[confirmed product vision](product-vision.md) and
[verified state snapshot](current-state.md).

| Phase | Outcome |
| --- | --- |
| P0 | Native build evidence and development baseline |
| P1 | Persistent mandatory agent + website session pairs |
| P2 | Saved manual workflows and real execution monitor; first usable milestone |
| P3 | Multiple connectors, agent actions and revisioned site knowledge |
| P4 | Complete visual workflow editor and prompt-to-workflow editing |
| P5 | Local time and website-event triggers, real waiting/active visibility |
| P6 | Measured slimming, security, Stable upgrades and desktop distribution |
| P7 | Later local headless execution without a browser window |
| P8 | Optional supporter subscription, provided models, email and specialized nodes |
| P9 | Optional definition sync with explicit device execution ownership |

P8 and P9 are optional tracks with their own dependencies, not mandatory gates
for the local core. Security, platform tests and upstream maintenance apply
throughout, not only in the release phase.

## First work packages

1. [AIM-001: native baseline](tasks/AIM-001-native-baseline.md).
2. [AIM-002: persistent session pairs](tasks/AIM-002-session-pairs.md).
3. [AIM-003: workflows and monitor](tasks/AIM-003-workflows-and-monitor.md).

P0 source exists, but native acceptance is still pending at the handoff baseline.
No subscription, provider, workflow executor or native platform certification is
created by this planning update. Keep the foundation PR a draft until its actual
acceptance gates are satisfied.
