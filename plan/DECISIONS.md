# Decisions, interfaces and decision rules

Every decision has an ID `D-###`. Part 1 holds process and scope decisions, Part 2 the design, Part 3 the public interfaces, Part 4 the decision rules (`DR-##`) the implementer applies at a fork. Claims `C-###` are in `research/claims.json`; assumptions `A-###` in `plan/ASSUMPTIONS.md`; risks `R-###` in `premortem/RISK_REGISTER.md`; tests `T-###` in `tests/` and `plan/TRACEABILITY.md`.

Terms used throughout:

- **Core**: the C++ library `folkdsp` under `core/`, which contains all sound generation and has no dependency on JUCE.
- **Wrapper**: the JUCE code under `plugins/common/` that turns the core into a VST3 plugin and a standalone program.
- **Render tool**: the command-line program `folk-render` under `tools/folk-render/`, which drives the core from an event file and writes a WAV file. All audio tests go through it.
- **Preset data**: the tables of physical and tuning values in `presets/*.json`, each value carrying the claim it comes from and a confidence. Code reads them at build time (they are compiled in as generated headers by `tools/gen_presets.py`).
- **Reed**: one free-reed tongue with its cell. **Rank**: one full set of accordion reeds at one pitch level. **Course**: two strings played as one.

---

## Part 1. Process and scope

**D-001 Unreachable hosts (0.1).** The planning sandbox reaches package registries, public git over the git protocol, and the hosts the owner added to the environment's allowlist on 2026-11-14 (recorded in `research/rounds/round-1.md`). It does not reach `pubs.aip.org`, `www.mdpi.com` or `freesound.org` (HTTP 403 to automated requests), nor release downloads of repositories outside the session. Alternative channels: papers on those hosts are read from open author copies where they exist and are otherwise recorded as unread (A-012); dependencies are fetched by git at a pinned commit; release binaries (pluginval) are downloaded in CI, where their SHA-256 is checked before use. The implementer's sandbox may differ: `S-000` re-probes.

**D-002 Scope reductions.** (a) The accordion models the treble side only (ranks L, M-, M, M+, H); the Stradella bass side is not modelled. A MIDI keyboard plays single notes and the register switch selects the ranks. (b) The chromatic harmonica is the 12-hole instrument in C (C4 to C-sharp 7). (c) The melodion's bass range is a design value (C-024). (d) The input file's artefacts "slide-gap hiss", "sticky valves" and "valve buzz" are reduced to one `valve_buzz` control and the `airtightness` control; "moisture" is one control on the melodion. Reason: none of these has a source above Tier 4 (C-025, C-014 note), and each adds a control the listening gate must judge.

**D-003 Planning artifacts on the default branch (3.12).** Travel to `main` with the implementation: `HANDOFF.md`, `plan/`, `tests/`, `scripts/`, `EXECUTION_LOG.md`, `DEVIATIONS.md`, `reviews/`, `GATE-*.md`, `references/` (link records only). Stay on the generation and implementation branches only: `research/`, `premortem/`, `.checkpoints/`, `lessons/`, `knowledge/`, `RETROSPECTIVE.md`. `S-INTEGRATE` removes the second group from the pull-request branch in one commit made on a branch cut for the pull request (`pr-<run_id>`), so `impl-<run_id>` keeps everything.

**D-004 No mutation-testing step.** `S-MUTATE` is omitted. Reasons: (a) the correctness gates of this plan are behavioural audio tests through the render tool, reference metrics and listening gates, and Mull instruments C++ unit-test executables, which here cover only the closed-form helpers (tuning tables and string formulas, about 300 lines); (b) no code exists at planning time, so the measured baseline, mutant count and runtime estimate that the protocol requires for a mutation step cannot be recorded honestly. The adversarial review step `S-ADVERSARIAL` is told to try hand-made mutants of the formulas instead (plan step text).

**D-005 CI platform extras (3.9.3).** Supported platforms (A-005): Windows x64, macOS arm64 and x86_64, Linux x64. Waived: an ARM64 Linux job (the plugins are not offered for ARM Linux); a libc-variant job (JUCE does not support musl; the plugins target glibc desktops); an oldest-toolchain job (the supported toolchains are exactly those of the pinned runner images, recorded per run in the job log; a hobby project makes no promise for older ones).

**D-006 Integration route.** `pull-request` (A-002). The default branch `main` exists (commit `375f650`). It has no branch protection at planning time (a new repository); `S-000` reads the protection state again and `S-INTEGRATE` waits for whatever checks are required then, and in any case for the three CI workflows of this plan.

**D-007 Release.** Nothing is released (A-018). CI uploads plugin binaries as workflow artifacts with `retention-days: 3`, with the `LICENSE` file inside each archive; because the repository's visibility could not be read at planning time, the plan treats them as public distribution under AGPL-3.0, which the complete source in the same repository satisfies (C-044). Any tagged release, installer or upload elsewhere needs gate `G-002`.

---

## Part 2. Design

### 2.1 Free reeds (harmonica, accordion, melodion)

**D-010 Reed model.** Each sounding reed is the minimal model of C-001, one state vector `(x, v, p1, u)`:

- `x` (m): height of the tongue tip above the plate's upper face (positive on the supply side); `v = dx/dt`.
- `p1` (Pa): over-pressure in the reed cell; `u` (m3/s): volume flow from the cell through the inlet passage to the reed.
- Supply: a reservoir at over-pressure `p0` (bellows, mouth or plenum) feeds the cell through an inlet orifice of area `A_in`: `u0 = alpha * A_in * sign(p0 - p1) * sqrt(2 |p0 - p1| / rho)`.
- Cell: `dp1/dt = (rho * c0^2 / V1) * (u0 - u)`.
- Passage: `du/dt = (S2 / (rho * L2)) * (p1 - p2)`.
- Jet: `vj = (u + Sr * v) / (alpha * Su(x))`, `p2 = (rho / 2) * vj * |vj|`.
- Reed: `dv/dt = -(w0 / Q) * v - w0^2 * (x - x0) - mu * p2`, `mu = Sr * w0^2 / K`.
- Useful section `Su(x)`: the Debut/Millot law as coded in `research/spikes/s03-reed-minimal-model/reed_sim.py` (front area plus two side areas, zero local opening while the tongue is inside the plate thickness), tabulated per reed over `x` in [-4 x0, +4 x0] at 2048 points when the reed is created (never on the audio thread) and floored at its minimum value.
- Constants: `rho = 1.2`, `c0 = 343`, `alpha = 0.61`.
- Reference parameter set (C-001, a harmonica reed at 444 Hz): `Lr = 12.95 mm`, `Wr = 2.1 mm`, `er = 0.110 mm`, `es = 0.900 mm`, `x0 = 0.528 mm`, `hmin = 0.050 mm`, `K = 47.9 N/m`, `Q = 95`, `Sr = Wr * Lr * 0.3915`, `S2 = 25 mm2`, `L2 = 20 mm`, `V1 = 800 mm2 * 60 mm`, `A_in = 30 mm2`.

The model was run from a pressure supply in spike S03c (C-053) and re-run by a reviewer at several rates and with a second integrator (C-001).

**D-011 Integration.** Semi-implicit Euler in the order of the spike (`p1`, `u`, then `v`, then `x`), in double precision. The base rate is `R = 4` times the host sample rate. Each reed takes `m = ceil(110 * f_r / (R * fs))` equal sub-steps per base-rate sample, so that it always has at least 110 steps per period (C-060: fewer than about 100 diverge). The source signal of each reed is sampled at the base rate, all reeds of an instrument are summed there and decimated once per instrument by a linear-phase half-band FIR cascade (two stages of 2; stop-band 80 dB; the latency is reported to the host by the wrapper and is the same for every note). The reed states are reset to rest (`x = x0`, others 0) at note-on.

**D-012 Scaling a reed to a pitch.** Every reed is the reference reed scaled by similarity (C-059). For a reed whose natural frequency is `f_r`, with `k = f_r / 444`: `x0`, `hmin`, `er`, `es` and `Sr` are the reference values divided by `k`; `A_in` is divided by `k`; `V1` by `k^2`; `K`, `Q`, `Lr`, `Wr`, `S2`, `L2` are unchanged. Written in the variables `x / x0` and `w0 * t` the equations are then the same for every reed, so every reed starts at the same pressure, sounds the same number of cents below its natural frequency and has the same spectrum relative to its fundamental (spike S12, 55 Hz to 5.3 kHz). Scaling the reed like a real cantilever was tried by a reviewer and fails (C-053). The similarity law makes all reeds of a rank sound alike; the differences a real instrument shows along its keyboard are introduced only by step `S-330` under rule DR-07, through three per-instrument curves over pitch stored in `presets/reeds.json`: a factor on `Q` (0.3 to 3), a factor on `x0` (0.5 to 2) and a factor on `hmin` (0.5 to 2), each a piecewise-linear function of MIDI note with at most 6 points, all equal to 1 until calibrated.

**D-013 Radiated sound.** The source signal of a reed is the time derivative of its total flow `u` (a simple source radiates as the derivative of volume flow). The literature attributes the far field of an accordion reed mainly to a dipole (C-009, abstract only); that is not modelled. The sum of the reeds passes through the instrument's body filter (D-024, D-032, D-040), a per-instrument gain, and the safety stage of D-015.

**D-014 Oversampling, polyphony and cost.** `R = 4` with the sub-steps of D-011. Spike S05b (C-054) measured 64 sounding reeds at 4 x 48 kHz rendering 5.6 times faster than real time on the planning sandbox, reeds only. Polyphony limits (voices are stolen oldest-first beyond them): accordion 16 keys (up to 64 reeds in the Master register), melodion 10 keys, harmonica 4 notes. The target of A-009 is tested by T-013 on the Linux x64 CI runner; DR-06 covers a miss.

**D-015 Real-time safety.** No allocation, lock or system call in any method the audio thread calls (T-011). State variables whose magnitude falls below 1e-20 are set to zero and a silent voice is switched off; the wrapper additionally enables flush-to-zero with `juce::ScopedNoDenormals`. The division by `alpha * Su(x)` uses the floored table. `x` is confined to the tabulated range by a stiff spring beyond it. If any state becomes non-finite the voice is reset and stays silent until its next note-on. The last stage of every instrument is a soft limiter `y = tanh(g * s) / tanh(g)` with fixed `g` chosen so that a default note peaks between -30 and -1 dBFS (T-162) and no input can exceed full scale (T-009).

**D-016 Breath, bellows and tuning.** A breath value `b` in [0, 1] comes from the note velocity (`breath_source` 0), CC 2 (1) or CC 11 (2), is smoothed with a 15 ms one-pole filter, and sets the reservoir pressure `p0 = 1500 Pa * b^1.5` (b = 0.25 gives 188 Pa, above the model's onset; b = 0.02 gives 4 Pa, below it; 1500 Pa is the top of the range in which the model sounds, C-053). Because a sounding reed keeps sounding below its onset pressure (C-002), tests of the threshold start from rest. Vibrato multiplies `p0` by `1 + 0.2 * depth * sin(2 pi rate t)`, with `depth = clamp(vibrato_depth + CC 1, 0, 1)`. Tuning: the model sounds 20 to 23 cents below a reed's natural frequency, by the same amount at every pitch under D-012 (C-059). `tools/calibrate_reeds.py` (step `S-201`) runs the engine's own reed code offline at `b = 0.6` for every MIDI note from 16 to 124 with the current curves of D-012 and writes, per instrument, the offset in cents between natural and sounding frequency to `presets/reeds.json`; the engine sets `f_r = f_target * 2^(offset/1200)`. The tool is re-run whenever a curve of D-012 or the sample-rate handling changes, and `S-300` checks that the committed table matches a fresh run. Pitch then drifts with breath as the model dictates (T-103).

### 2.2 Harmonica

**D-020 Keys.** `key` 0 to 11 is C to B. Keys C to F-sharp (0 to 6) have hole 1 blow at MIDI `60 + key`; keys G to B (7 to 11) at MIDI `48 + key` (C-011: instruments labelled G to B start below middle C). The layout is the Richter table of C-011, transposed.

**D-021 Playing a MIDI note on a diatonic.** `diatonicNoteFor(key, note)` decides, in this order: (1) a natural note: the first match scanning holes 1 to 10, blow before draw; (2) a bend: the first match scanning holes 1 to 10, draw bends (depths 1 to `diatonicMaxBend`) before blow bends; (3) an overbend: an overblow on holes 1, 4, 5, 6 (one semitone above the draw note) or an overdraw on holes 7, 9, 10 (one semitone above the blow note); otherwise the note is not playable and makes no sound. Maximum bends (semitones): draw holes 1 to 6: 1, 2, 3, 1, 0, 1; blow holes 8 to 10: 1, 1, 2; all others 0 (C-012). On a C instrument this covers every semitone from C4 (60) to D-flat 7 (97). The pitch wheel below centre bends a natural note down by `wheel * maxBend` semitones; above centre it does nothing. The table is preset data (`presets/harmonica.json`), single-source (R-001).

**D-022 How a bend sounds.** Baseline (required): a bent or overbent note is played by one reed whose natural frequency is moved to the target pitch (through the calibration of D-016) and whose cell is the cell of the reed that physically sounds: for bends deeper than half the interval to the lower reed, and for every overbend, the cell and geometry are those of the other reed of the hole. During a wheel movement the natural frequency glides and the cell parameters cross-fade over 30 ms. Optional (step `S-212`, rule DR-04): a two-reed channel with a tunable upstream resonator, in which the bend emerges from the model (C-013). It replaces the baseline only if it passes every harmonica test.

**D-023 Chromatic.** `variant` 1 is a 12-hole solo-tuned instrument in C: per group of four holes, blow C E G C and draw D F A B, each group an octave above the last, hole 1 blow at MIDI 60; the slide raises a note by one semitone. `chromaticNoteFor(note)` scans holes 1 to 12 and, within a hole, blow slide-out, draw slide-out, blow slide-in, draw slide-in; the first match plays. Range MIDI 60 to 97. The wheel bends any note down by at most one semitone (C-014). `key` is ignored.

**D-024 Harmonica tone controls (design values).** `wah` moves a one-pole low-pass on the output from 6 kHz (0, hands open) to 900 Hz (1, hands closed). `air_noise` adds band-limited noise proportional to the jet velocity. `airtightness` below 1 leaks a share `(1 - airtightness) * 0.5` of the supply flow past the reed and raises the air noise by the same share. `valve_buzz` (chromatic only) adds a 150 Hz to 400 Hz amplitude flutter of depth `0.3 * valve_buzz` during the first 80 ms of a note.

### 2.3 Accordion

**D-030 Registers.** `register` 0 to 11 selects ranks, in this order: 0 Piccolo (H), 1 Clarinet (M), 2 Bassoon (L), 3 Oboe (M, H), 4 Violin (M, M+), 5 Musette (imitation) (M, M+, H), 6 Musette (authentic) (M-, M, M+), 7 Organ (L, H), 8 Harmonium (L, M, H), 9 Bandoneon (L, M), 10 Accordion (L, M, M+), 11 Master (L, M, M+, H) (C-017; names are labels, R-001). L sounds an octave below the key, H an octave above.

**D-031 Tremolo.** `musette_cents` (0 to 25, default 15) is the offset of M+ above and M- below M at A4. `musette_scaling` 0 keeps the offset constant in cents on every key; 1 keeps the beat rate in hertz equal on every key to the rate at A4, `440 * (2^(c/1200) - 1)` (C-018). The offset is applied to the calibrated sounding pitch (D-016), not to the natural frequency, so the beat rate is exact at `b = 0.6`.

**D-032 Cassotto and sordina (design values, C-019).** `cassotto` 1 routes ranks L and M through a filter: a peaking boost of 3 dB at 700 Hz (Q 0.9) and a high shelf of -9 dB above 1.6 kHz. `sordina` 1 adds a high shelf of -8 dB above 1.2 kHz on every rank. Both are judged at the listening gate.

**D-033 Bend.** The pitch wheel below centre lowers every rank by `wheel * bend_cents` cents (0 to 25, default 25; C-020), by moving the natural frequencies, and lowers the level by `3 dB * |wheel|`.

**Key noise.** `key_noise` adds a 15 ms noise burst (band 300 Hz to 3 kHz) at note-on and a weaker one at note-off, seeded per note for determinism.

### 2.4 Melodion

**D-040 Ranges and bodies (design values except where C-024 applies).** `range` 0: 32 keys, MIDI 53 to 84 (F3 to C6); 1: 37 keys, 53 to 89 (F3 to F6); 2: bass, 24 keys, 41 to 64 (F2 to E4, not confirmed by a maker's figure). Notes outside the range are silent. `body` 0 plastic: no filter; 1 wood: high shelf -5 dB above 2 kHz; 2 metal (Accordina): high shelf +3 dB above 3 kHz. `moisture` scales `Q` of every reed by `1 - 0.9 * moisture` and adds `moisture * 0.4 * x0` to `hmin`.

**D-041 Plenum.** All open reeds draw from one volume `Vp = 200 cm3` at pressure `pp`: `dpp/dt = (rho c0^2 / Vp) * (ub - sum of the reeds' inlet flows)`. `breath_mode` 0 (pressure-controlled): `ub` is whatever holds `pp` at `p0` of D-016 (the plenum is a pressure source). `breath_mode` 1 (flow-limited): `ub = b * 0.4 l/s`, so the pressure, and with it every reed's level, falls as more keys open (T-131).

### 2.5 Plucked strings (mandolin, bouzouki)

**D-060 String model.** Each string is a set of partials `n = 1 .. N` with frequencies `f_n = f_1 * n * sqrt((1 + B n^2) / (1 + B))`, where `f_1` is the equal-tempered pitch of the fretted note (so the first partial is in tune) and `B = pi^3 E d^4 / (64 T L_f^2)` (C-026) uses the core diameter `d`, the tension `T = mu (2 L f_open)^2` and the fretted length `L_f = L / 2^(fret/12)`. `N` is the number of partials below 18 kHz, at most 80. Each partial is one complex one-pole resonator (two real state variables). `E = 200 GPa`, steel density 7850 kg/m3.

**D-061 Losses.** The loss factor of partial `n` is `eta_air + eta_bend + eta_extra`, with `eta_air` and `eta_bend` as in C-027 (`eta_E = 1e-3` for plain strings, `4e-3` for wound strings; the outer diameter in `eta_air`), and `eta_extra = damping * 2e-3` (the `damping` control, default 0.3). The bridge loss `eta_b` is not a constant: it comes from the body's admittance at the partial's frequency (D-064).

**D-062 A course as coupled pairs.** For each partial of one string that lies within 60 cents of a partial of the other string of the course, the two are integrated together as a 2 x 2 block `da/dt = i * Omega * a`, `Omega = [[w1 (1 + i eta1/2) + z, z], [z, w2 (1 + i eta2/2) + z]]`, `z = i * 2 * f_ref * Y(w) / Y0` (C-028), stepped with the exact matrix exponential of the block computed at note-on (and recomputed when the pitch wheel or `body_coupling` changes, off the audio thread's per-sample path, on a control-rate tick of 64 samples). The pair is not expanded into its two eigenmodes (C-031). Partials with no partner are single resonators with `eta_b` added. The second string is mistuned by `pair_detune_cents` (default 1.5). In an octave course the partner of partial `m` of the high string is partial `2m` of the low string (C-042). `course_mode` 1 plays only the first string of each course. Only the polarisation normal to the soundboard is modelled.

**D-063 Pluck (partly a design assumption).** A stroke sets the amplitude of partial `n` of a string to `A * sin(n pi beta) / n * exp(-n * 0.15 * (1 - pick_stiffness)) * exp(-n * 0.1 * (1 - velocity))`, with `beta = pick_position` measured from the bridge and `A` proportional to `velocity^1.5` (the force form of C-030; the two exponential factors are the assumed low-pass effect of a soft plectrum and a soft stroke). The second string of the course is struck `1.2 ms * (1.5 - velocity)` after the first with 0.9 of its amplitude; `octave_order` 1 on the bouzouki swaps the order. Before a stroke, the amplitudes already on that course are multiplied by 0.15 (the plectrum touches the strings). `tremolo` 1, or CC 1 at 0.5 or more, repeats the stroke every `1 / tremolo_rate_hz` seconds while the note is held. A note-off multiplies the course's decay by a 30 ms damping unless CC 64 is at 0.5 or more. One note sounds per course: `courseForNote` picks the highest-pitched course whose lower open string is at or below the note and within `maxFret` frets (mandolin 24, Greek bouzouki 27, Irish 24).

**D-064 Body.** A body is a list of modes `(f_k, Q_k, g_k)` from `presets/bodies.json`. Its bridge admittance is `Y(w) = body_coupling * Y_ref * sum_k g_k * (i w / w_k) / (1 - (w/w_k)^2 + i w / (w_k Q_k))`, with `Y_ref` chosen per body so that `eta_b` of the open top course is 2e-3 at `body_coupling` 1. The sound output is the sum of the body modes' velocities, each mode driven by the total bridge force of all strings, plus a direct path of the bridge force high-passed at 1.5 kHz (the modes above the listed ones). With `body_coupling` 0 the bridge is rigid for the strings (`Y = 0` in D-062) and the body modes are still driven, so there is sound. A `tap` event drives every mode with an impulse and no string.

### 2.6 Instrument data

**D-070 Mandolin.** Four unison courses G3 D4 A4 E5 (MIDI 55, 62, 69, 76; C-034). `body` 0 f-hole archtop, 1 oval-hole archtop, 2 bowl-back.

**D-071 Body presets.** Mode frequencies in Hz; Q is 30 for every mode unless calibration (S-REF, DR-07) changes it; gains fall as 1/k in the order listed. Confidence is the confidence of the claim.

| Preset | Modes (Hz) | Source |
|---|---|---|
| Mandolin f-hole | 272 (air), 313, 464, 570, 824, 886, 1117 | C-035, single-source Tier 1 |
| Mandolin oval-hole | 209, 214 (air), 398, 482, 575, 775, 918, 1149 | C-035 |
| Mandolin bowl-back | 200, 550, 740 | C-036, text only; low confidence |
| Bouzouki trichordo and tetrachordo | 180, 445, 695 | C-041, a search-result snippet; low confidence (R-002) |
| Bouzouki Irish | 110, 205, 330 | no source; a guitar-like guess (R-002) |

**D-072 Strings.** Plain steel: linear density from the diameter. Wound strings: linear density from the pitch and a nominal tension of 100 N, core diameter 0.4 of the outer diameter (A-021; no maker's figures were read). Sets: mandolin f-hole and oval-hole 0.040w, 0.026w, 0.015, 0.011 in at 352.4 mm; bowl-back 0.038w, 0.024w, 0.014, 0.010 in at 330 mm (C-037).

**D-073 Bouzouki.** `variant` 0 trichordo: D3+D4 (0.022w, 0.011), A3 A3 (0.014), D4 D4 (0.011), scale 680 mm; 1 tetrachordo: C3+C4 (0.024w, 0.011), F3+F4 (0.020w, 0.010), A3 A3 (0.014), D4 D4 (0.011), 680 mm; 2 Irish: G2 G2 (0.040w), D3 D3 (0.028w), A3 A3 (0.016), D4 D4 (0.011), 650 mm (C-039, C-040, C-052). In an octave course the thick string is first.

### 2.7 References and listening

**D-050 Accordion reference.** TinySOL 6.0 accordion notes (C-021, C-055), redistributable under CC BY 4.0 with attribution. Test T-200 holds the thresholds. The candidate patch for the comparison is fixed: `register=1, cassotto=0, a4_hz=441.6, vibrato_depth=0`, velocities 0.3, 0.6 and 0.95 for pp, mf and ff.

**D-051 References for the other instruments.** Known at planning time: mandolin notes in the Philharmonia library, private reference (C-049); four Irish bouzouki open-course notes on Wikimedia Commons, CC BY-SA 4.0 (C-051); nothing for harmonica or melodion. Step `S-REF` runs a bounded search (the sources and queries are listed in the step) and writes `references/index.csv`. Per instrument: with 12 or more usable notes the listening gate uses blind pairs and T-201 applies; with fewer, the gate uses demos only and T-201 prints NOT-APPLICABLE. A private reference is used only where the redistributable pool for that instrument has fewer than 12 notes, and that shortfall is this decision's justification for the mandolin. No reference with an unknown licence, no named author or no source page is used.

**D-052 Link records and the publication guard.** `references/index.csv` has the columns `id, instrument, file, sha256, midi, velocity, sets, source_url, author, licence, licence_url, accessed, redistributable`; `sets` is `;`-separated `param=value` pairs for the candidate patch. Reference audio is never committed; it lives in a directory outside the working tree named by `FOLK_REF_ROOT`. `tools/evidence_guard.py` (contract in `tests/py/test_evidence_guard.py`, T-210) must pass on an evidence directory before it is pushed.

**D-053 Listening tools.** `tools/listening/make_blind_pairs.py` and `score_blind.py` are copied unchanged from `qualitycoding/skills` at commit `a20ed73` (Apache-2.0, compatible with AGPL-3.0). Pass condition per gate: no more than 8 of 12 pairs identified correctly, and no demo described by the listener as wrong.

### 2.8 Engineering

**D-080 Framework.** JUCE tag `8.0.17-security`, commit `dabd5ad13cd869cba41046947fffc8e5ce5cd662` (C-043). JUCE 9 is the current major release; JUCE 8 is chosen because the owner accepted that default (A-004), the stores hold verified JUCE 8 build knowledge, JUCE 9 changes the VST3 client API (knowledge item K-20261004T151500Z), and the 8.0.17 maintenance release carries the parser hardening that matters for untrusted plugin state.

**D-081 Licence.** The repository is AGPL-3.0 (`LICENSE`); JUCE is used under its AGPLv3 option; the bundled VST3 SDK is MIT; Catch2 is BSL-1.0 and is not distributed; the listening scripts are Apache-2.0 (C-044).

**D-082 Plugin validation.** pluginval v1.0.4 (C-045), strictness 10, on each of the three operating systems for each of the five VST3 bundles. Exit status alone is not accepted: the CI step also checks the log (T-300, defined in `S-003`).

**D-083 Pins.** `plan/ENVIRONMENT.md`.

**D-084 CI matrix.** `ubuntu-24.04` (x64), `windows-2025` (x64), `macos-15` (arm64; builds the universal binary and tests the arm64 slice), `macos-15-intel` (x64; tests the x86_64 slice of the universal binary built on it). `fail-fast: false`.

**D-085 Python.** 3.13, with `tests/requirements.txt` (numpy 2.5.3, scipy 1.18.1, soundfile 0.14.0, pytest 9.2.0; C-048).

**D-086 Performance gate.** T-013 gates only where `FOLK_PERF_GATE=1`, which only the `ubuntu-24.04` Release job sets. On other runners the figure is printed. Hosted runners vary in CPU model (knowledge item K-20261029T030800Z), so the test takes the best of three runs.

---

## Part 3. Interfaces

**D-090 Core API.** `core/include/folk/engine.h`, `tuning.h`, `strings.h`, as committed. Errors: functions with table arguments throw `std::out_of_range` for an index outside the table; physical formulas throw `std::invalid_argument` for non-positive lengths, diameters, tensions, densities or frequencies and for a partial number below 1; `Engine` methods called on the audio thread never throw: out-of-range notes, controllers, parameter indexes, offsets and non-finite values are ignored or clamped (T-009). `Engine::prepare` may be called again with another rate.

**D-091 Parameters.** The table in `tests/cpp/param_table.h` is the specification: order, ids, ranges, defaults, step counts. Common: `level`, `a4_hz`. Reeds add `breath`, `breath_source`, `vibrato_rate_hz`, `vibrato_depth`, `air_noise`. Plucked instruments add `pick_position`, `pick_stiffness`, `pair_detune_cents`, `course_mode`, `body_coupling`, `damping`, `tremolo`, `tremolo_rate_hz`, `bend_range`. Then the instrument's own parameters. `breath` is the starting breath for `breath_source` 1 and 2 until the first controller message arrives; with `breath_source` 0 the note velocity is the breath and `breath` is not used.

**D-092 Render tool.**

```
folk-render --instrument <harmonica|accordion|melodion|mandolin|bouzouki> --events <file> --out <file.wav>
            [--sr <44100..96000, default 48000>] [--block <1..8192, default 256>] [--set <id>=<value>]...
folk-render --instrument <name> --list-params
folk-render --instrument <name> --dump-model [--set <id>=<value>]...
folk-render --version | --help
```

- Event file: UTF-8 text, one event per line, `<time in seconds> <kind> <arguments>`; kinds `on <midi> <velocity 0..1>`, `off <midi>`, `cc <number> <value 0..1>`, `bend <-1..1>`, `set <id> <value>`, `tap <strength 0..1>` (plucked instruments; ignored by reeds), `end`. Times never decrease. The last event is `end`; rendering stops there (at most 600 s). Blank lines and lines starting with `#` are skipped. A line longer than 1000 characters is an error.
- Output: stereo, 32-bit float WAV at `--sr`, written by the tool's own writer with a plain `fmt ` and `data` chunk (format tag 3) and nothing else: no PEAK chunk, no time stamp, so two runs give identical bytes (C-056). The file is written to a temporary name and renamed, so a failed run leaves no output file.
- `--list-params`: one line per parameter, `id<TAB>min<TAB>max<TAB>default<TAB>steps`.
- `--dump-model`: JSON on standard output. For plucked instruments: `{"scale_length_m", "young_modulus_pa", "max_fret", "courses": [{"strings": [{"midi", "diameter_m", "wound", "linear_density", "core_m", "B"}]}], "body_modes": [{"hz", "q", "gain"}]}` with `B` the inharmonicity of the open string. For reeds: `{"instrument": "<name>"}`.
- `--version` prints `folk-render <project version>`.
- Exit status: 0 success; 2 usage error (unknown instrument, option or parameter, bad value, rate or block size out of range); 3 malformed event file (the message on standard error names the line as `line <n>`, or says the `end` event is missing); 4 input or output file error.

**D-093 MIDI.** Note-on and note-off; pitch wheel; CC 1 modulation (vibrato depth for reeds, tremolo switch for plucked instruments); CC 2 and CC 11 breath; CC 64 sustain (plucked instruments); CC 120 and CC 123 all notes off. Other messages are ignored. All channels are merged.

**D-094 Wrapper.** One source file `plugins/common/FolkProcessor.cpp` (the implementer may add files beside it) compiled once per plugin with `FOLK_INSTRUMENT` defined. It owns a `folk::Engine`; exposes each core parameter as a JUCE parameter with the same id (version hint 1) in the same order, discrete ones as choice or integer parameters; forwards MIDI with sample offsets; copies parameter values to the engine at the start of each block; has no audio input bus and one stereo output bus; reports the engine's latency and tail; saves state as the engine's state text and restores it only if `loadState` accepts it (then updates the JUCE parameters from the engine); returns a `juce::GenericAudioProcessorEditor` grouped under headings by the implementer's choice of layout (A-008), with a preset menu listing the variant presets of `presets/factory.json`. Plugin names "Folk Harmonica", "Folk Accordion", "Folk Melodion", "Folk Mandolin", "Folk Bouzouki"; manufacturer "QualityCoding", code `Qlcd`; plugin codes `Fhrm`, `Facc`, `Fmel`, `Fman`, `Fbzk`.

---

## Part 4. Decision rules

The default rule for anything not listed: choose the most reversible option that does not expand scope, log it in `DEVIATIONS.md` with the reason, and continue, unless it touches frozen tests, security, data integrity, a public interface (Part 3) or research integrity, in which case halt and write `BLOCKED.md`.

| ID | If | Then |
|---|---|---|
| DR-01 | A dependency fetch fails (git clone of JUCE or Catch2, pip install, pluginval download) | Retry 3 times with 30 s, 60 s, 120 s waits. If it still fails locally but succeeds in CI, record the step as "blocked locally, verified in CI" with the run URL. If it fails in CI too, halt with `BLOCKED.md`. Never change a pin to make a fetch succeed. |
| DR-02 | A pinned version has been withdrawn or a runner label has been retired | Halt with `BLOCKED.md` naming the pin, the evidence and the nearest replacement; the planner amends `plan/ENVIRONMENT.md`. Exception: a runner label marked deprecated but still served is used, and the deprecation is logged in `DEVIATIONS.md`. |
| DR-03 | Reed check (S-201): at one of the 12 check pitches (MIDI 28, 36, 45, 52, 60, 69, 76, 84, 93, 100, 108, 112) the C++ reed does not reproduce spike S12 (silent at 50 Pa; sounding at 100, 400 and 1500 Pa; offset within 1.5 cents of -20, -23, -23), or any state becomes non-finite | First raise the sub-step constant of D-011 from 110 to 160 and re-run. If the difference remains, the C++ code differs from `research/spikes/s12-reed-similarity-scaling/similarity.py`: find and fix the difference (the spike is the reference). Do not change the scaling law. If after that a pitch still fails, halt with `BLOCKED.md` and the table of results. |
| DR-04 | Optional two-reed bend (S-212) | Time-box: one implementation and at most three parameter adjustments. Adopt it only if every test in `tests/py/test_harmonica.py` and `test_reeds.py` passes with it and T-013 still passes. Otherwise delete its code path, keep the baseline of D-022, and record the attempt in `DEVIATIONS.md` and a knowledge item. Either outcome completes the step. |
| DR-05 | A frozen test looks wrong (it cannot be satisfied by any correct implementation, or it contradicts Part 2 or 3) | Do not edit it, skip it or mark it expected-failure. Write `TEST_CHALLENGE.md` (test ID, evidence, proposed fix) and halt that step; continue steps that do not depend on it. |
| DR-06 | T-013 misses 4 times real time on the Linux x64 CI runner for an instrument | First optimise without changing the model: single precision for the reed states if all reed tests still pass; process reeds in structure-of-arrays form; skip silent voices. If still below 4, reduce that instrument's polyphony limit of D-014 by a quarter, record it in `DEVIATIONS.md`, and raise it at the next listening gate as a known limit. Relaxing the factor 4 itself is the owner's decision at that gate, never the implementer's. On Windows and macOS runners there is no target; the printed figure is recorded. |
| DR-07 | T-200 or T-201 (reference metrics) fails after implementation | Calibrate preset data only, never per-note constants: for reeds the scaling exponents, `Q`, `x0` factor and the output filter; for strings the body mode Q and gains, `eta_E` and the plectrum factors. At most 5 calibration rounds, each recorded in `EXECUTION_LOG.md` with the metric table before and after. If it still fails, the step ends as failed, the listening gate for that instrument is opened with the failure stated in its evidence, and the owner chooses `iterate`, `proceed-with-rescope` or `stop`. |
| DR-08 | A security or dependency scan reports a vulnerability (`pip-audit`, or a JUCE security release newer than the pin) | For a Python test dependency: move to the nearest fixed version, re-run the whole Python suite, log a deviation. For JUCE: halt with `BLOCKED.md`; a framework pin change is an amendment. |
| DR-09 | pluginval fails or times out for a plugin on one operating system | Re-run once to rule out a runner fault. If it fails again, treat it as a defect of that plugin: fix it, add no exclusions, lower no strictness. The known pluginval 1.0.4 race in its plugin-information test (knowledge item K-20261104T005200Z) is handled only by the single re-run. |
| DR-10 | The implementer's sandbox cannot build JUCE within its time limits, or lacks the Linux packages | Build and test the core, the render tool and the Python suite locally (they need no JUCE); build the plugins in CI only, and record plugin steps as "verified in CI" with run URLs. Never report a local plugin build that did not run. |
| DR-11 | A reference file's sha256 no longer matches its link record, or its source page has changed its terms | Stop using that reference, record the event in `DEVIATIONS.md`, and treat the instrument as having that many fewer notes (D-051 thresholds apply again). |
| DR-12 | The listener answers `iterate` at a listening gate | Follow the iterate procedure in `HANDOFF.md` (analyse what the listener named, one general change per difference, re-run every frozen test, new seed, new round). After round 3, only `proceed`, `proceed-with-rescope`, `stop` or `override-round-limit` are accepted. |
| DR-13 | A step's `Done when` cannot be evaluated locally because of sandbox recycling or missing network | Record the dimension as blocked (environment limitation) and name the CI job that evaluates it; the step is done only when that job is green. |
| DR-14 | CI on Windows or macOS fails in configure or build for a reason unrelated to the plan's code (generator not found, SDK path) | Apply the fallback written in `plan/ENVIRONMENT.md` for that platform; if none applies, halt with `BLOCKED.md` including the full log excerpt. |
