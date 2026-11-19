# Assumptions and intake answers

The intake batch was sent on 2026-11-14. The owner's reply was, verbatim: "Resume". No item was answered individually, so every item adopts its proposed default (protocol 0.3.6 item 3). Each record states the default adopted and its consequence. On 2026-11-19 the owner confirmed explicitly that A-002, A-003, A-006, A-007, A-008, A-010, A-011, A-013, A-014 and A-017 are correct (answer "All correct" to a question listing each of them).

## Restated task (0.3.1)

- **Goal.** A plan, executable by a separate implementing agent without questions, to build physically modelled VST3 instruments for harmonica, accordion, melodion (melodica), mandolin and bouzouki, with the construction variants described in the owner's research file.
- **Input file.** `F_lk_instrument_synthesis` (uploaded by the owner; "Acoustic Physics and Construction Variants of Free-Reed and Double-Course Plucked String Instruments for Physical Modeling"). The owner's instruction: "Consider the file as uncorroborated research." See A-019.
- **In scope.** Five instrument plugins sharing one DSP core; the variants named in the input file as switchable models; headless rendering; CI on three operating systems; blind-listening validation.
- **Out of scope.** Sample playback; AU, AAX and CLAP formats; installers; code signing and notarisation; any public release or package publication; MPE; custom artwork.
- **Success criteria.** Fixed as `SC-###` in `plan/TRACEABILITY.md` after research; all measurable.
- **Constraints.** C++; JUCE 8.0 line (A-004); CMake; AGPL-3.0; GitHub-hosted CI runners only; no paid services.

## Records

| ID | Topic | Adopted value | Consequence |
|---|---|---|---|
| A-001 | Empty repository and branches | One initial commit on `main` (README and licence, commit `375f650`), then all planning on `gen-20261114T004707Z-folk-instruments-vst`. Nothing is pushed to `skills`, `Lessons` or `knowledge` during planning. | `main` is the default branch and exists; the generation branch never becomes the default. |
| A-002 | Integration route | `pull-request`: the implementer opens a pull request from `impl-<run_id>` to `main`; the owner merges. | No `G-INT`. |
| A-003 | Scope and order | One plan for all five instruments, as five separate plugins sharing one DSP core. Order: core; harmonica and mandolin as pilots for each family, each with its own listening gate; then accordion, melodion, bouzouki. All variants of the input file are switchable models. | Five plugin targets; listening gates per instrument. |
| A-004 | Framework and licence | JUCE on the 8.0 line under AGPLv3; repository licence AGPL-3.0. Exact tag pinned in research (1.3.6). | No JUCE commercial licence needed; all source is AGPL. |
| A-005 | Formats and platforms | VST3 plus a Standalone build for headless rendering; Windows x64, macOS universal (arm64 and x86_64) and Linux x64, all built and validated in CI. Assumed host: Ableton Live. | Three-OS CI matrix (3.9). |
| A-006 | Modelling depth | The physical models the input file describes (reed oscillator with nonlinear flow; stiff-string waveguides with bridge coupling and a modal body), subject to corroboration. Where a mechanism cannot be corroborated or makes no audible difference, a decision rule simplifies it. | Decision rules in `plan/DECISIONS.md`. |
| A-007 | Control | Standard MIDI; velocity; CC2 or CC11 for breath and bellows pressure; pitch wheel for bends; mod wheel for tremolo or vibrato. No MPE. | Parameter and MIDI map in `plan/DECISIONS.md`. |
| A-008 | Interface | A plain functional editor with labelled controls, and presets per variant; no custom artwork. | No design assets. |
| A-009 | Performance target | Each plugin at full polyphony renders at least 4 times faster than real time at 48 kHz, block size 256, on one core of the Linux x64 CI runner; sample rates 44.1 kHz to 96 kHz supported. | One gating performance test (T-013) that checks each of the five instruments. |
| A-010 | Reference recordings | Redistributable first (owner's recordings, CC0, CC BY); private references allowed where that pool falls short (Rule 15). If no usable reference exists for an instrument, its listening gate uses demos only. The owner did not say whether they own any of the instruments; the plan assumes no owner recordings. | Reference search in research; `D-###` per instrument. |
| A-011 | Listener | The owner, on their own headphones; 12 blind pairs per instrument; pass at no more than 8 of 12 correct; at most 3 rounds per gate. | Frozen pass condition in `S-LISTEN` steps. |
| A-012 | Paywalled papers | Open-access versions only; a claim that cannot be read at its source stays below `corroborated` and becomes a risk. | Risks in `premortem/RISK_REGISTER.md`. |
| A-013 | Rigour | `standard`. | Loop bounds of Rule 0.6. |
| A-014 | Project nature | `hobby`. | Private-reference route available. |
| A-015 | Stores | Lessons to `qualitycoding/Lessons` (read at `9934bb5`); knowledge to `qualitycoding/knowledge` (read at `f3d176d`); written only by the implementer after gate `G-003`. | Probed readable on 2026-11-14. |
| A-016 | Subagents | Fresh-context subagents are spawned where the protocol requires them (adversarial research pass, cold reads, pre-mortems, assumption audit) and for parallel research. | Tier map in `plan/PROFILE.md`. |
| A-017 | Names | Manufacturer "QualityCoding"; plugins "Folk Harmonica", "Folk Accordion", "Folk Melodion", "Folk Mandolin", "Folk Bouzouki". | Plugin codes fixed in `plan/DECISIONS.md`. |
| A-018 | Binaries | No release. CI artefacts of a public repository are a distribution, so builds are short-retention artefacts only, and nothing that is not AGPL-compatible is bundled. | `software.deploys = false`; `G-002` guards any later release. |
| A-019 | Status of the input file | Every statement in the input file enters `research/claims.json` with the input file as a Tier 4 source that counts as zero sources towards `corroborated`. Its equations were lost in export and are re-derived from primary sources. Its tables of computed values are re-computed in spikes. | No design decision or test rests on the file alone. |
| A-020 | Planner network | Direct HTTPS from the sandbox to paper and recording hosts is blocked; literature is read through the web search and fetch tools; public git and package registries are reachable. | Recorded as `D-###` (alternative channel, 0.1). |
| A-021 | Wound strings | No maker's figures for wound strings were read. Wound strings are given a linear density from their pitch and a nominal tension of 100 N, and a core diameter of 0.4 of the outer diameter. | Preset data (D-072); affects inharmonicity and decay of the bass courses only; calibrated against references where they exist (DR-07). |
| A-022 | Reed proportions | Reeds are scaled by similarity from one measured harmonica reed (D-012), not from the proportions of real reeds of each instrument. | All reeds of a rank sound alike until calibrated; judged by T-200 and the listening gates. |

## Software intake (0.3.2)

- **Users and platforms.** The owner, playing the plugins in a DAW (assumed Ableton Live, A-005) on Windows x64, macOS (arm64 and x86_64) or Linux x64.
- **Runtime and deployment.** A VST3 host loads the plugin; no service, no deployment (`software.deploys = false`).
- **Performance and scale.** A-009.
- **Threat model and data sensitivity.** The plugins handle no personal data, credentials or payments. Inputs crossing a trust boundary: MIDI and parameter automation from the host, and plugin state blobs (presets and session state) that a host hands back, which may be malformed. The render tool reads event files from disk. No network access by any deliverable.
- **Data handling and retention.** Plugin state only (parameter values, preset name); stored by the host.
- **Release channel and versioning.** None published. Semantic version `0.1.0` in the CMake project; any release goes through `G-002`.
- **Maintenance.** Hobby; best effort; pinned dependencies so the build is reproducible.

## Audio intake (module `audio`)

- **Reference recordings, licences and routes.** Not yet known; found in research (question branch "References") and recorded with link records under `references/` on the implementation branch. A-010 applies.
- **Who listens.** The owner (A-011).
