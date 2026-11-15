# Profile record

- Run: `gen-20261114T004707Z-folk-instruments-vst`
- Active profiles: `software`
- Mode flags: `audio = true`; `software.deploys = false`; `courseware = false`; `math.exploration` not applicable
- Rigour level: `standard` (A-013)
- Project nature: `hobby` (A-014)
- Environment class: `ephemeral` (worker process restarted twice during intake; see `.checkpoints/state.json`, `diagnostic.environment_class_evidence`)

## Protocol files read

| File | Version | Read because |
|---|---|---|
| `protocols/planning-protocol.md` (core) | v4.0 | always |
| `protocols/modules/software-ci.md` | v1.0 | `software` is active |
| `protocols/modules/audio.md` | v1.0 | `audio = true` |
| `protocols/modules/ephemeral.md` | v1.0 | environment class `ephemeral` |

Read from `qualitycoding/skills` at commit `a20ed73` (`origin/main` on 2026-11-14). Skills read: `create-plan`, `audio-blind-listening-validation`. The skills `mutation-testing-in-ci` and `mutation-sharding` are read when the `S-MUTATE` decision is taken (see `plan/DECISIONS.md`).

## Tier map

| Tier | Model |
|---|---|
| T1 | Fable (the planning session) |
| T2 | Opus |
| T3 | Sonnet |
| T4 | Haiku |

Tier substitution: from 2026-11-15 13:10 UTC the planning session (T1) ran on Opus after the owner changed the session model; the subagent tiers were unchanged. Recorded in `.checkpoints/state.json` (`tier_substitutions`).

## Sections not applicable

| Section | Reason |
|---|---|
| 0.3.3, 2A (mathematics), Rule 7, Rule 8 | `math` inactive |
| 0.3.4, 2B.2 provenance contract, 2B numerical V&V, 2B.4 | `computational` inactive |
| 2C figures | `computational` and `publication` inactive |
| 0.3.5, 2D, R2b novelty search | `publication` and `math` inactive |
| 3.11 learning-exercise pathway | `courseware` not set |
| `plan/OPERATIONS.md`, deployment tests | `software.deploys = false` |
| Gate `G-001` | `math` and `computational` inactive |
| Gate `G-INT` | integration route is `pull-request` (A-002) |

Artifacts not created because their sections are N/A: `research/NOVELTY.md`, `math/`, `figures/`, `manuscript/`, `plan/OPERATIONS.md`.
