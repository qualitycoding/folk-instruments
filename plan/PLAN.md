# Plan

**Status: READY.** Planned on 2026-11-14 to 2026-11-19 under the planning protocol core v4.0 with modules `software-ci` v1.0, `audio` v1.0 and `ephemeral` v1.0 (`qualitycoding/skills` at `a20ed73`); rigour `standard`. Active profile: `software`, with mode flag `audio`; environment class `ephemeral`.

| Item | Count |
|---|---|
| Claims (65) by confidence | verified 31, corroborated 4, single-source 26, inferred 4; load-bearing below the bar: 7 (C-012, C-013, C-014, C-017, C-027, C-039, C-051), each carried as a risk |
| Tests by category (37 test IDs; a test can carry two categories) | integration 15, unit 10, security 9, operational 3, tool check 3, reference 2, performance 1, plugin validation 1 |
| Test cases at the freeze | Catch2: 27 (`folk-tests`), 2 (`folk-locale-tests`), 1 (`folk-perf`), 9 per host program (5 programs); pytest: 345 (`not reference`; 43 tool checks pass at the freeze, 302 fail against the stubs) and 16 reference tests; 36 frozen files |
| Steps | 28 (`S-000` to `S-KNOW`) |
| Gates | 10: G-P1, G-P2 (pilot listening), G-L1 to G-L5 (listening validation), G-002 (publishing; opened by no step), G-003 (stores), G-004 (owner acceptance of a review finding; only when needed) |
| Risks by severity (146) | Critical 11 (all mitigated); High 30 (29 mitigated, 1 accepted: R-010); Medium 59; Low 46; 5 speculative |
| Assumption audit (88 items) | confirmed 49, falsified 3 (resolved by D-095), unverifiable 36 (R-098 to R-133) |
| Review steps | `S-REVIEW`, `S-ADVERSARIAL`, `S-REVIEW-DELTA` (fresh-context reviewers); mutation testing not planned (D-004), so no mutation floor |
| Loops against their bounds | research 6 of 6 (ended at the limit, not saturated); cold read 5 of 5 plus 5 re-runs after plan changes; pre-mortem 5 of 5, then one round on the audit's changes (protocol 4.7.4); assumption audit 1 pass plus a re-audit of the changed set |

Pre-mortem note: round 5, the last of the loop, still found High risks; all were mitigated after the round and are not open (`premortem/CONVERGENCE.md`), but those mitigations were checked by a cold-read re-run and by running them in the planning sandbox, not by a further pre-mortem round of the loop.

Read `HANDOFF.md` first. Conventions used in every step:

- **Repository root** is the working directory unless a command says otherwise. `<run_id>` is `gen-20261114T004707Z-folk-instruments-vst`; the implementation branch is `impl-gen-20261114T004707Z-folk-instruments-vst`.
- **Build directories** live outside the repository: `B=$HOME/folk-build` (core) and `BP=$HOME/folk-build-plugins` (plugins). The commands are those of `plan/ENVIRONMENT.md` sections 3 and 4 with `build` replaced by `$B` and `build-plugins` by `$BP`.
- **CORE BUILD** means: `cmake -S . -B $B -G Ninja -DCMAKE_BUILD_TYPE=Release -DFOLK_BUILD_PLUGINS=OFF && cmake --build $B`.
- **CPP `<filter>`** means: `$B/folk-tests "<filter>"` exits with status 0 (the filter is a Catch2 test-name pattern; `*` is a wildcard).
- **PY `<expression>`** means: `cd tests && FOLK_RENDER=$B/folk-render python3 -m pytest -m "not reference" -k "<expression>"` exits with status 0 and reports no test skipped or deselected by anything other than `-k` and `-m`.
- **PUSH** means the push cadence of `HANDOFF.md`: commit, `git push origin impl-<run_id>`, then `git ls-remote origin impl-<run_id>` equals `git rev-parse HEAD`. Every push starts `ci.yml`, whose concurrency group cancels the run in progress; so while a step waits for a CI run (`S-003`, `S-320`, a gate-evidence run in `S-210`, `S-250` or `S-LISTEN`), the other steps commit without pushing and push once that run has finished.
- **LOG** means: append one line to `EXECUTION_LOG.md` (UTC time, step ID, attempt number, outcome, commit hash, note).
- Every step ends with LOG and PUSH, and its `Checkpoint` line says what to add to `.checkpoints/state.json`, which the implementer edits by hand (`completed` gains the step ID; other values go under a key named after the step, for example `"S-320": {"run_url": ...}`). `scripts/checkpoint.py` is the planner's helper; the implementer need not use it.
- Post-conditions (Rule 14) apply to every step even where not repeated: each file in `Outputs` exists, is non-empty, and passes the sanity check named in `Done when`.
- New source files are added to `CMakeLists.txt`; `core/src/stubs.cpp` shrinks as functions are implemented and is deleted in `S-300`.
- The frozen files are listed in `tests/FROZEN_MANIFEST.sha256`. Never edit them (rule DR-05).
- **GAIN `<name>`** means: `python3 tools/calibrate_gains.py --instrument <name> --render $B/folk-render` (reads the instrument's current `G_out` from `presets/gains.json`, 1 if absent, measures the default note of D-013 with the binary built from that value, and writes `G_out * target / measured peak`), then `python3 tools/gen_presets.py`, CORE BUILD, then `python3 tools/calibrate_gains.py --instrument <name> --render $B/folk-render --check`, which exits 0 when the measured peak is within 0.1 dB of -12 dBFS.
- **Tier** is advisory: T1 is the strongest model available to the implementer and T4 the cheapest (the planner's map is in `plan/PROFILE.md`); an implementer with one model uses it for every step. Only a step that asks for a fresh context (`HANDOFF.md` section 15) requires a different agent; any other output, `baseline/retro-digest.md` included, may be written by the implementer itself.
- **Lessons applied** lines cite `L-` and `K-` ids as provenance only: most of those files live in the stores, not in this repository, and the step text already states what each one requires.
- **Exclusive resource `generated presets`**: `presets/*.json`, `core/src/generated/presets_data.h` and `CMakeLists.txt`. Steps of the two tracks that list it never edit these files at the same time: one step commits and pushes its change (header regenerated, build green) before a step of the other track edits them.

Order of work at a glance (by track; the step headings below are not in this order): `S-000`, `S-002`, `S-003`; then two tracks that may run concurrently: reeds (`S-100`, `S-110`, `S-200`, `S-201`, `S-210`, gate `G-P1`, `S-212`, `S-220`, `S-230`) and strings (`S-101`, `S-240`, `S-250`, gate `G-P2`, `S-260`); then `S-300`, `S-310`, `S-320`, `S-REF`, `S-330`, `S-340`, `S-REVIEW`, `S-ADVERSARIAL`, `S-LISTEN`, `S-REVIEW-DELTA`, `S-INTEGRATE`, `S-RETRO`, `S-KNOW`.

---

### S-000 Environment and access verification
- Tier: T4
- Profile: software
- Depends on: none
- Inputs: `HANDOFF.md`, `plan/ENVIRONMENT.md`, `.checkpoints/state.json`
- Actions:
  1. Read every `GATE-*.md` in the repository root, if any; an `OPEN` gate blocks the steps it lists.
  2. `git fetch origin && git checkout -b impl-gen-20261114T004707Z-folk-instruments-vst origin/gen-20261114T004707Z-folk-instruments-vst` (if the branch already exists on the remote, check it out instead and continue from `EXECUTION_LOG.md`).
  3. Re-run the environment-class probe: note the time, create `$HOME/folk-probe.txt`, start `sleep 600 &`, and at the start of the next turn check whether the file and the process survive. Record `stable` only if both do; otherwise `ephemeral`. If no turn boundary occurs before `S-002` ends, record `ephemeral`. Under `ephemeral`, the section "Ephemeral environments" of `HANDOFF.md` applies to every later step.
  4. Run the setup commands of `plan/ENVIRONMENT.md` section 2. If `apt-get` is unavailable (no root), record it and apply rule DR-10.
  5. Check credentials and reachability from this environment, recording each result in `.checkpoints/state.json` under `diagnostic_impl`: `git ls-remote origin` (read); an empty commit pushed to `impl-<run_id>` and verified with `ls-remote` (write); `git ls-remote --tags https://github.com/juce-framework/JUCE 8.0.17-security` and the same for `https://github.com/catchorg/Catch2 v3.16.1` (dependencies); `python3 -m pip download --no-deps -d "$HOME/folk-pipcheck" numpy==2.5.3` (PyPI); `curl --fail --head https://zenodo.org/api/records/3685367` (reference data); whether a pull request can be opened (the available GitHub tool offers a create-pull-request operation and the write check above succeeded; no pull request is created here, so a refusal at creation is handled by `S-INTEGRATE`'s `On failure`); whether Actions results can be read (list the repository's workflow runs by a method of `HANDOFF.md` section 14; with no run yet, an empty list read without error counts as readable); whether a fresh-context agent can be started (start one by a method of `HANDOFF.md` section 15, ask it to return the first line of `HANDOFF.md`, and compare); the branch protection and required checks of `main` (read them if the tool allows; otherwise record "not readable"); the repository's visibility (D-084: if it is private, halt with `BLOCKED.md` asking the owner to confirm the Actions budget before `S-003`).
  6. Create `EXECUTION_LOG.md` with a header line and the entry for this step; create `DEVIATIONS.md` with a header and the line "No deviations yet."
- Outputs: `EXECUTION_LOG.md`, `DEVIATIONS.md`, updated `.checkpoints/state.json`
- Evidence produced: none
- Done when: every check of action 5 is recorded; read, write, JUCE, Catch2 and PyPI succeeded (a failed Actions-read or fresh-agent probe does not block here: it is recorded, and the steps that need it, `S-003` and `S-REVIEW`, apply their own `On failure`); `EXECUTION_LOG.md` and `DEVIATIONS.md` exist and are non-empty.
- Checkpoint: `diagnostic_impl`, `environment_class`, `branch`.
- On failure: halt and write `BLOCKED.md` listing exactly what is missing, before any delivery work. A failed Zenodo check does not block: record it; `S-REF` then relies on CI (rule DR-13).
- Gate: none
- Relevant decisions/claims: D-001, C-043, C-046
- Lessons applied: L-20261114T090000Z-fetch-tool-shares-sandbox-allowlist; group "sandbox-environment" and "git-and-push" of `research/PRIOR_KNOWLEDGE.md`
- Exclusive resources: none

### S-002 Baseline build and red run
- Tier: T4
- Profile: software
- Depends on: S-000
- Inputs: the repository as cut from the generation branch
- Actions:
  1. `sha256sum -c tests/FROZEN_MANIFEST.sha256`.
  2. CORE BUILD.
  3. Run `$B/folk-tests`, `$B/folk-locale-tests`, `$B/folk-perf`, and `cd tests && FOLK_RENDER=$B/folk-render python3 -m pytest -m "not reference"`; save to `baseline/red-run.txt` the last 30 lines of each Catch2 program and, for pytest run with `-q -rp`, every `PASSED` line and the final summary line.
  4. Compare with the counts in `plan/TRACEABILITY.md`, section "State at the freeze".
- Outputs: `baseline/red-run.txt`
- Evidence produced: T-090, T-091, T-092 (pass from the freeze)
- Done when: the manifest check passes; the three programs build; `baseline/red-run.txt` shows the Catch2 run with 27 failed test cases of 27 and the locale run with 2 of 2 failed, and the pytest run with exactly the tool-check tests passing (the tests in `test_metrics_selfcheck.py`, `test_pluginval_log_check.py` and `test_tsan_supp_check.py`) and every other test failing; the counts equal those in `plan/TRACEABILITY.md`; the tool checks T-090 (`tests/py/test_metrics_selfcheck.py`) , T-091 (`tests/py/test_pluginval_log_check.py`) and T-092 (`tests/py/test_tsan_supp_check.py`) are among the passing tests.
- Checkpoint: baseline counts.
- On failure: a manifest mismatch or a count that differs means the branch is not the frozen plan: halt with `BLOCKED.md`. A build failure caused by the local toolchain: record the compiler version and apply rule DR-10 (CI is the reference build).
- Gate: none
- Relevant decisions/claims: D-090, C-056
- Lessons applied: group "frozen-tests"
- Exclusive resources: none

### S-003 Continuous integration
- Tier: T3
- Profile: software
- Depends on: S-002
- Inputs: `plan/ci/ci.yml`, `plan/ENVIRONMENT.md` section 5
- Actions:
  1. `mkdir -p .github/workflows && cp plan/ci/ci.yml .github/workflows/ci.yml`. Add `.gitattributes` with the two lines `tests/** text eol=lf` and `*.events text eol=lf` (Windows checkouts must not change the hashed files). Append to the existing `.gitignore` the lines `build*/`, `refs/` and `refs-*/` (both workflows download references into `refs/` inside the checkout).
  2. Commit and PUSH. This first run is the spike for the unverified items of `plan/ENVIRONMENT.md` section 5.
  3. Read the run's results (job conclusions and failing step names) by the CI-reading method of `HANDOFF.md` section 14. Expected at this point: job `freeze` succeeds; job `audit` succeeds; jobs `core` and `plugins` and `host-tsan` fail in their test steps, not in checkout, configure, build or download steps; job `reference` fails at its step 'Fetch every indexed reference' (the fetch tool is still the stub that exits 64, and the index does not exist yet) after its TinySOL steps succeeded; `all-green` fails.
  4. For each unverified item in the table of `plan/ENVIRONMENT.md` section 5, record what the run showed in `EXECUTION_LOG.md`, and apply that table's "If it fails" column. Three items sit in steps after 'Host tests', which this run skips: the universal-binary check, the pluginval archive layout and the pluginval log markers. Record them as 'not observable at S-003, deferred to S-320'; `S-320` applies their 'If it fails' column. The gate-evidence item is observed at `S-210`.
- Outputs: `.github/workflows/ci.yml`, `.gitattributes`, `.gitignore` (later planned edits of `ci.yml`: none; `S-INTEGRATE` removes one step on the pull-request branch only)
- Evidence produced: none (T-300 and T-310 become runnable)
- Done when: the workflow file is byte-identical to `plan/ci/ci.yml` apart from deviations logged under action 4; the run exists; `freeze` and `audit` are green; on all four runners the `core` job reached its "C++ unit and engine tests" step and the `plugins` job reached its "Host tests" step (configure and build succeeded everywhere); the `host-tsan` job reached its test step; the `reference` job downloaded TinySOL and its step "Reference notes exist" passed.
- Checkpoint: CI run URL and per-job conclusions.
- On failure: rules DR-01, DR-02, DR-14. If CI results cannot be read by any method of `HANDOFF.md` section 14, halt and write `BLOCKED.md` asking the owner for read access to Actions results.
- Gate: none
- Relevant decisions/claims: D-005, D-007, D-082 to D-086, C-045 to C-047
- Lessons applied: groups "ci-github-actions" and "frozen-tests"
- Exclusive resources: the repository's CI concurrency group

### S-100 Tables: tuning, harmonica layout, accordion registers, string courses
- Tier: T3
- Profile: software
- Depends on: S-002
- Inputs: `core/include/folk/tuning.h`, `plan/DECISIONS.md` D-020 to D-023, D-030, D-070 to D-073
- Actions:
  1. Write `presets/harmonica.json`, `presets/accordion.json`, `presets/strings.json` holding the tables of those decisions, each value with `"claim"` and `"confidence"` fields copied from `research/claims.json`.
  2. Write `tools/gen_presets.py`, which turns `presets/*.json` into `core/src/generated/presets_data.h` (constant arrays) and also writes there the half-band coefficients of D-011 (from `scipy.signal.firwin`); commit the generated header, which every build uses as it is, so that a build without Python works. A CMake custom command that re-runs the generator when a preset file changes exists only behind the option `FOLK_REGENERATE_PRESETS` (default `OFF`); CI never runs the generator, and staleness is caught by `python3 tools/gen_presets.py --check` (this step and `S-300`). In `harmonica.json`, `accordion.json`, `strings.json` and `bodies.json` every value carries `claim` and `confidence`: the claim is the `C-###` named by the decision that defines the value (where the decision names several, the one whose statement contains the value), and a design value with no claim carries `"claim": "none"` and `"confidence": "design"`; `params.json`, `reeds.json`, `gains.json` and `factory.json` carry none. The tool exits non-zero on a missing field.
  3. Implement in `core/src/tuning.cpp` every function declared in `tuning.h`, reading the generated tables, with the error behaviour of D-090.
- Outputs: `presets/harmonica.json`, `presets/accordion.json`, `presets/strings.json`, `tools/gen_presets.py`, `core/src/generated/presets_data.h`, `core/src/tuning.cpp`
- Evidence produced: T-001, T-002, T-003, T-004, T-007
- Done when: CORE BUILD; CPP `T-001*`, CPP `T-002*`, CPP `T-003*`, CPP `T-004*`, CPP `T-007*`; `python3 tools/gen_presets.py --check` exits 0 (the committed header matches the JSON files: every integer and string exactly, every floating-point value within a relative 1e-12, so that last-bit differences of NumPy between CPUs do not fail it) and exits 1 after a temporary edit of one JSON value (try it, then revert).
- Checkpoint: step done.
- On failure: fix the code, never the test. A table value that contradicts a frozen test is a rule DR-05 case.
- Gate: none
- Relevant decisions/claims: D-020, D-021, D-023, D-030, D-070, D-072, D-073; C-011, C-012, C-014, C-017, C-034, C-039, C-040
- Lessons applied: L-20261007T150300Z-hand-typed-frozen-constant (tables are generated, not typed twice)
- Exclusive resources: generated presets

### S-101 String formulas
- Tier: T3
- Profile: software
- Depends on: S-002
- Inputs: `core/include/folk/strings.h`, D-060 to D-062
- Actions: implement in `core/src/strings.cpp` every function declared in `strings.h`. `solveCoupledPair` solves the 2 x 2 complex eigenproblem in closed form (quadratic formula), orders the modes by decreasing imaginary part, and normalises each shape to unit Euclidean norm; for a repeated eigenvalue it returns the limit shapes (1, 1)/sqrt(2) and (1, -1)/sqrt(2).
- Outputs: `core/src/strings.cpp`
- Evidence produced: T-005, T-006
- Done when: CORE BUILD; CPP `T-005*`; CPP `T-006*`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05 for a test that looks wrong.
- Gate: none
- Relevant decisions/claims: D-060 to D-062; C-026, C-027, C-028
- Lessons applied: none
- Exclusive resources: generated presets

### S-110 Engine frame and render tool
- Tier: T2
- Profile: software
- Depends on: S-100
- Inputs: `core/include/folk/engine.h`, D-090 to D-093, `tests/cpp/param_table.h`
- Actions:
  1. Implement `instrumentName`, `instrumentFromName` and `Engine::create` for all five instruments on a shared base class in `core/src/engine_base.cpp`: the parameter table of D-091 (copy the values from `tests/cpp/param_table.h` into `presets/params.json` and generate them with `tools/gen_presets.py`), clamping and rounding, an event queue of fixed capacity (256 events per block; further events in the same block are dropped) sorted by sample offset, sample-accurate dispatch inside `process`, `reset`, `saveState`, `loadState` (all checks of T-014), `tailSeconds`, and the output stage of D-015. At this step every instrument produces silence.
  2. Implement `tools/folk-render/main.cpp` to the contract of D-092, including its own WAV writer, atomic output (temporary file, then rename), and all exit statuses; `--dump-model` and the `tap` event are wired in `S-240` (until then `--dump-model` prints `{"instrument": "<name>"}` and `tap` is ignored).
- Outputs: `core/src/engine_base.cpp`, `core/src/engine_base.h`, `presets/params.json`, `tools/folk-render/main.cpp`
- Evidence produced: T-008, T-014, T-016, part of T-009, part of T-161
- Done when: CORE BUILD; CPP `T-008*`; CPP `T-014*`; CPP `T-009 out-of-range*`; `$B/folk-locale-tests` exits 0 (T-016; where the sandbox cannot generate `de_DE.UTF-8` without root, rule DR-13: the `core` job's locale step decides); PY `T161 and not event_file_features`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: none
- Relevant decisions/claims: D-015, D-090 to D-093; C-056
- Lessons applied: groups "cpp" and "dsp-correctness"; knowledge K-20261105T233000Z (no large objects on the stack: allocate voices on the heap in `prepare`)
- Exclusive resources: generated presets

### S-200 Reed voice
- Tier: T2
- Profile: software
- Depends on: S-110
- Inputs: D-010 to D-016; `research/spikes/s12-reed-similarity-scaling/similarity.py` (the reference for the equations, their order, the useful-section table `table()` and the measurement `analyse()`); `research/spikes/s05-reed-cost/reed_bench2.cpp` (for the loop structure and cost only: its useful-section formula is simplified and must not be copied)
- Actions:
  1. Implement `core/src/reed.h` and `reed.cpp`: a `Reed` (parameters from D-012 for a given natural frequency, useful-section table built outside the audio thread, sub-step count from D-011), its step function, the base-rate summing bus and the half-band decimator, the breath smoothing and pressure law of D-016, vibrato, the safety measures of D-015.
  2. Write `tools/calibrate_gains.py` (D-013) with the arguments and behaviour of GAIN in the conventions above (`--instrument`, `--render`, `--check`); it is first exercised in `S-210`, the first step with a sounding instrument. 3. Write `tools/reed_probe.cpp` (a small program built with the core, not shipped in the plugins): `reed_probe --freq <natural Hz> --pressure <Pa> --rate <host Hz> [--instrument <name>] [--undriven] [--time]`. It runs one reed of the core (with that instrument's curves of D-012) from rest for 450 periods of the natural frequency, the pressure rising linearly to its value over the first 9 periods, and prints one JSON line `{"state": "sounds"|"silent"|"diverged", "cents": ..., "amp_over_x0": ..., "source_rms": ...}`, the first three computed exactly as `analyse()` in `similarity.py` does over the last 30 % of the run, and `source_rms` the RMS over the same 30 % of the base-rate source signal of D-013 (`(u[k] - u[k-1]) * R * fs`, the flow difference between consecutive base-rate samples times the base rate): amplitude `(max(x) - min(x)) / 2 / x0`, `silent` below 0.02; frequency from the Hann-windowed spectrum of `x` zero-padded 4 times with log-parabolic interpolation of the highest bin above half the natural frequency; `cents = 1200 log2(f / natural)`; `diverged` if any state became non-finite or `|x| > 1 m`. `--undriven` instead displaces the tip by `x0`, holds the supply at 0 Pa and prints the amplitude in the first and the last 10 % of a 2 s run. Add it to `CMakeLists.txt` as target `reed_probe`.
- Outputs: `core/src/reed.h`, `core/src/reed.cpp`, `tools/reed_probe.cpp`, `tools/calibrate_gains.py`
- Evidence produced: none (verified in S-201)
- Done when: CORE BUILD including `reed_probe`; `reed_probe --undriven` shows the amplitude of the last 10 % smaller than that of the first 10 % (a model that gains energy with no supply is wrong); `reed_probe` for 444 Hz at 400 Pa and 48000 Hz host rate prints an offset between -24.5 and -21.5 cents and an amplitude between 4.4 and 4.9 times `x0` (spike S12: -23.1 cents, 4.63).
- Checkpoint: step done.
- On failure: compare with `similarity.py` line by line (order of updates, signs, units); the spike is the reference.
- Gate: none
- Relevant decisions/claims: D-010 to D-016; C-001 to C-004, C-053, C-054, C-059, C-060
- Lessons applied: group "dsp-correctness"
- Exclusive resources: generated presets

### S-201 Reed check across the range and tuning calibration
- Tier: T3
- Profile: software
- Depends on: S-200
- Inputs: `tools/reed_probe.cpp`, D-012, D-016, rule DR-03
- Actions:
  1. Write `tools/reed_check.py [--instrument <name>] [--calibrated]`, which runs `reed_probe` at the 12 check pitches of rule DR-03 at both host rates: without `--calibrated` at 50, 100, 400, 1500 and 1800 Pa with the targets of DR-03; with `--calibrated` (the calibrated-set check of D-012) at 28, 156, 400, 1500 and 1800 Pa, checking only silent, sounding and finite; it takes `--out <file>`, writes the CSV there and exits non-zero on any failing row; both `reed_check.py` and `calibrate_reeds.py` take `--probe <path>` (default `$HOME/folk-build/reed_probe`, that is `$B/reed_probe`). Run it: that is, run `reed_probe` at the 12 check pitches of rule DR-03 (natural frequency = equal-tempered frequency of the MIDI note), at 50, 100, 400, 1500 and 1800 Pa, at host rates 44100 and 48000; write the table to `baseline/reed-check.csv`.
  2. Apply rule DR-03 to any row that fails.
  3. Write `tools/calibrate_reeds.py` as D-016 describes (it calls `reed_probe`), run it, and commit `presets/reeds.json` with the offset table and the three curves of D-012 all equal to 1.
- Outputs: `baseline/reed-check.csv`, `tools/reed_check.py`, `tools/calibrate_reeds.py`, `presets/reeds.json`, `core/src/generated/presets_data.h` (regenerated)
- Evidence produced: none
- Done when: `baseline/reed-check.csv` has 120 rows; every 50 Pa row is silent (amplitude below 0.02 `x0`); every other row sounds with no non-finite state, and with an offset within 1.5 cents of -20.1 (100 Pa), -23.1 (400 Pa), -23.3 (1500 Pa) (no offset target at 1800 Pa); `presets/reeds.json` parses and holds, for each of the three reed instruments and each of the four host rates, 85 offsets (MIDI 28 to 112) between -27 and -17 cents, and the constant `source_rms_ref` (the three instruments' tables are equal while their curves are all 1).
- Checkpoint: step done; the sub-step constant in use; `ns_per_reed_sample` from `reed_probe --time` (444 Hz, 400 Pa, 48 kHz; the option runs the reed for 10 s of audio after the 450-period run, times the step loop only with a steady clock, best of 3, and prints `{"ns_per_reed_sample": ...}` per base-rate sample), in `state.json` and `EXECUTION_LOG.md`; a value above 20 ns (the budget that leaves 4 times real time for 64 reeds at a 192 kHz base rate on one core) is recorded as an early warning against A-009, not a failure; T-013 on the CI runner remains the gate.
- On failure: rule DR-03.
- Gate: none
- Relevant decisions/claims: D-011, D-012, D-016; C-059, C-060
- Lessons applied: L-20261007T150600Z-control-mapping-formulas-unverified (the mapping is measured, not assumed)
- Exclusive resources: generated presets

### S-210 Harmonica
- Tier: T2
- Profile: software
- Depends on: S-201
- Inputs: D-020 to D-024, `core/src/reed.h`, `presets/harmonica.json`
- Actions: implement the harmonica instrument in `core/src/harmonica.cpp`: note mapping through `diatonicNoteFor` and `chromaticNoteFor`, the baseline bend of D-022, breath sources, vibrato, `wah`, `air_noise`, `airtightness`, `valve_buzz`, polyphony 4 with oldest-first stealing, silence for unplayable notes.
- Outputs: `core/src/harmonica.cpp`; `presets/gains.json` (entry for the harmonica, by GAIN `harmonica`, run as soon as the instrument makes sound and before its `Done when` is evaluated: T-162 depends on the gain); for the gate: `.github/workflows/gate-evidence.yml`, `tools/evidence_guard.py`, a first version of `tools/build_evidence.py`, `references/index.csv` (header only), `tools/fetch_references.py`
- Evidence produced: T-100 (harmonica), T-101 to T-109 (harmonica), T-110 to T-114
- Done when: CORE BUILD; PY `harmonica`; PY `(T100 or T101 or T102 or T103 or T104 or T105 or T106 or T107 or T108 or T109) and harmonica`.
- Checkpoint: step done.
- On failure: fix the code. If a reed test fails only at the extreme notes, re-check S-201's table first. Rule DR-05 for a test that looks wrong.
- Gate: G-P1 (the gate is opened by this step; see `plan/GATES.md`)
- Relevant decisions/claims: D-020 to D-024; C-011 to C-014
- Lessons applied: group "dsp-correctness"
- Exclusive resources: generated presets

Gate actions of S-210 (after its tests pass): the pilot gate needs the evidence tooling early, so: (1) copy `plan/ci/gate-evidence.yml` to `.github/workflows/gate-evidence.yml`; (2) implement `tools/evidence_guard.py` to the contract of T-210 now (ahead of `S-REF`; PY `T210` must pass); (3) unless `references/index.csv` already exists (`S-REF` may have written it), write it with the header of D-052 and no rows; (4) implement `tools/fetch_references.py` to D-052 now (ahead of `S-REF`; with a header-only index it does nothing and exits 0; PY `T211` must pass), because the workflow calls it, and write `references/archives.csv` with its header and the TinySOL archive row of `plan/ENVIRONMENT.md` section 1; (5) write a first version of `tools/build_evidence.py` that accepts every argument of `S-340` (`--gate`, `--instrument`, `--seed`, `--out`, `--render`, `--ref-root`, `--private-out`, `--index`), renders the instrument's demos, writes `MANIFEST.json`, `SHA256SUMS` and `ATTRIBUTION.md`, and runs the guard (`S-340` completes it with pairs and metrics); (6) push a commit with the marker `[gate-evidence G-P1 harmonica seed=1]`; check the branch `evidence/G-P1`; write `GATE-G-P1.md` from the template in `HANDOFF.md` with the evidence and questions of `plan/GATES.md` (the demos to point the owner to: `harmonica-01-melody`, `-04-dynamics`, `-08-bend`, `-10-chromatic-on-diatonic`, `-203-variant`; paste into the record by hand the list of frozen tests that pass for the harmonica and the five `PERF` lines of `folk-perf`); PUSH; report in chat. While the gate is open, continue with the strings track and with `S-212`.

### S-212 Optional: two-reed bend
- Tier: T2
- Profile: software
- Depends on: S-210
- Inputs: D-022, rule DR-04, C-013
- Actions: follow rule DR-04. The experiment: one channel with a blow reed and a draw reed sharing the cell pressure, the draw reed mounted with the opposite orientation, and a second upstream volume and passage (the player's mouth) whose resonance frequency is the bend control; the wheel moves that resonance from 1.2 times the higher reed's frequency down to the lower reed's frequency. Keep it behind an internal build-time switch until the rule's conditions are met.
- Outputs: `baseline/s212-before.txt`; either an updated `core/src/harmonica.cpp` and `presets/gains.json` (adopted: GAIN `harmonica` is re-run after the change) or no code change (not adopted); in both cases an entry in `DEVIATIONS.md` and a knowledge item `knowledge/K-<time>-two-reed-bend-experiment.md` recording what was tried and measured
- Evidence produced: none new
- Done when: before starting, the list of frozen tests passing on `impl-<run_id>` is saved to `baseline/s212-before.txt`: one line per passing test, sorted, `cpp: <test case name>` for each `testcase` element without a `failure` or `error` child in the report written by `$B/folk-tests -r junit -o $HOME/folk-s212.xml` and `py: <node id>` from the `PASSED` lines of `cd tests && FOLK_RENDER=$B/folk-render python3 -m pytest -m "not reference" -q -rp`; the same commands after the change give a list that contains every line of the saved one; rule DR-04 has been applied and its outcome recorded (its performance condition is provisional here (the CI performance step cannot run until every instrument sounds) and is settled in `S-320` as DR-04 says; PY `harmonica` and PY `harmonica and (T100 or T101 or T102 or T103)` still pass; every test listed in `baseline/s212-before.txt` still passes.
- Checkpoint: adopted or not.
- On failure: not adopting is a valid outcome, not a failure.
- Gate: none
- Relevant decisions/claims: D-022; C-013
- Lessons applied: none
- Exclusive resources: generated presets

### S-220 Accordion
- Tier: T2
- Profile: software
- Depends on: S-201, and gate G-P1 answered `proceed` or `proceed-with-rescope`
- Inputs: D-030 to D-033, `core/src/reed.h`, `presets/accordion.json`
- Actions: implement the accordion in `core/src/accordion.cpp`: ranks per register, tremolo by D-031, cassotto and sordina filters, bend, key noise, bellows from velocity or controller, polyphony 16 keys, a change of `register` while keys are held taking effect within one block (ranks start or stop for held keys).
- Outputs: `core/src/accordion.cpp`; `presets/gains.json` (entry for the accordion, by GAIN `accordion`, run as soon as the instrument makes sound and before its `Done when` is evaluated: T-162 depends on the gain)
- Evidence produced: T-100 to T-109 (accordion), T-120 to T-125, T-161 event-file features
- Done when: CORE BUILD; PY `accordion`; PY `T161`; and, as an early probe of A-022, the accordion reference tests T-200 have been run once: `cd tests && FOLK_RENDER=$B/folk-render FOLK_TINYSOL=$HOME/folk-refs/tinysol python3 -m pytest -m reference -k T200 -s` with TinySOL downloaded as in `S-REF` action 2 (this step may do that download itself), or, where Zenodo is unreachable locally, the T-200 lines of the next CI `reference` job (DR-13 decides only where the probe runs: once that run's T-200 lines are recorded, red or green, this part of the step is done; the job turning green is not required before `S-330`); `EXECUTION_LOG.md` records the 11 T-200 outcomes by name (a run that collects no test does not count; a failing outcome does not fail this step: it starts DR-07 thinking early and is carried to `S-330`).
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: none
- Relevant decisions/claims: D-030 to D-033; C-017 to C-020
- Lessons applied: L-20261004T162220Z-beat-phase-biased-harmonic-levels (levels of beating sounds are measured over whole beat periods)
- Exclusive resources: generated presets

### S-230 Melodion
- Tier: T2
- Profile: software
- Depends on: S-201, and gate G-P1 answered `proceed` or `proceed-with-rescope`
- Inputs: D-040, D-041, `core/src/reed.h`
- Actions: implement the melodion in `core/src/melodion.cpp`: the plenum of D-041 in both breath modes, ranges, bodies, moisture, polyphony 10.
- Outputs: `core/src/melodion.cpp`; `presets/gains.json` (entry for the melodion, by GAIN `melodion`, run as soon as the instrument makes sound and before its `Done when` is evaluated: T-162 depends on the gain)
- Evidence produced: T-100 to T-109 (melodion), T-131 to T-134
- Done when: CORE BUILD; PY `melodion`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: none
- Relevant decisions/claims: D-040, D-041; C-023 to C-025
- Lessons applied: none
- Exclusive resources: generated presets

### S-240 String, course and body
- Tier: T2
- Profile: software
- Depends on: S-101, S-110
- Inputs: D-060 to D-064, `presets/strings.json`, `research/spikes/s17-string-body/pluck_ref.py` (the reference implementation)
- Actions:
  1. Add to `presets/strings.json` the constants `eta_E` of D-061 (plain and wound) and the two plectrum factors of D-063 (0.15 and 0.1), each with `"claim"` and `"confidence"` (the claim D-061 names for `eta_E`; `none` and `design` for the plectrum factors); `pluck.cpp` reads them from the generated header, never as literals (DR-07 calibrates them). Write `presets/bodies.json` from the table of D-071 (each mode with `hz`, `q`, `gain`, `claim`, `confidence`), generated into the header by `tools/gen_presets.py`.
  2. Implement `core/src/pluck.h` and `pluck.cpp`: the partial bank, the 2 x 2 pair blocks with their matrix exponential, the pluck of D-063, damping, tremolo, sustain, the body of D-064 with its admittance, the `tap` event (reached by `folk-render` through an internal header `core/src/pluck_api.h` declaring `bool folk::detail::tap(Engine&, float strength, int sampleOffset)`, which returns false for a reed engine; the public `engine.h` is not changed, and the plugins do not expose `tap`), the control-rate tick, and the `--dump-model` data (exposed to `folk-render` through an internal header under `core/src/`, not through the public headers).
- Outputs: `presets/bodies.json`, `presets/strings.json` (constants added), `core/src/pluck.h`, `core/src/pluck.cpp`, `core/src/pluck_api.h`, `tools/folk-render/main.cpp` (`tap` and `--dump-model` wired in)
- Evidence produced: none (verified in S-250)
- Done when: CORE BUILD; a unit program or Catch2 test of the implementer's own (not frozen, in a separate CMake target `folk-extra-tests` that is never added to `folk-tests`, so the 27-case count of `S-300` is unchanged) shows that the pair block reproduces `research/spikes/s04-coupled-pair/output.json`: for one pair with `f = 660 Hz`, `eta_i = 2e-4`, `eta_b = 2e-3` (purely resistive), first string plucked with amplitude 1 and the second with 0, mistuned by 1 cent, the decay rates of `|a1 + a2|` in dB/s fitted over 0 to 0.08 s and over 3 to 5 s are within 2 % of -75.3 and -5.14; and with no stroke after an initial one the sum of `|a|^2` over all partials of a course never grows from one control tick to the next, for `body_coupling` 0, 0.5 and 1 and mistunings of 0, 3.5 and 8 cents. And the core reproduces `pluck_ref.py`: for the f-hole mandolin, open E course, velocity 0.7, `pair_detune_cents` 0, the output of the body stage of `pluck.h` driven directly (course, body and `Y_ref` built as in `pluck_ref.py`'s `__main__`, the mandolin instrument of `S-250` not needed, taken before `G_out`, `level` and the limiter) and the spike's `render()` output, both normalised to their peaks, differ by at most 0.01 RMS over the first second (the implementer's own test, not frozen; the spike is the reference).
- Checkpoint: step done.
- On failure: compare with `research/spikes/s04-coupled-pair/pair.py`.
- Gate: none
- Relevant decisions/claims: D-060 to D-064; C-026 to C-031, C-042
- Lessons applied: knowledge K-20261009T120109Z (two-pole resonator with an input zero for a cosine start)
- Exclusive resources: generated presets

### S-250 Mandolin
- Tier: T2
- Profile: software
- Depends on: S-240, S-210 together with its gate actions 1 to 5 (`tools/calibrate_gains.py` and the evidence tooling; they are done when `GATE-G-P1.md` exists)
- Inputs: D-070 to D-072, `core/src/pluck.h`
- Actions: implement the mandolin in `core/src/mandolin.cpp`: three bodies, four courses, note-to-course rule, all plucked-instrument parameters.
- Outputs: `core/src/mandolin.cpp`; `presets/gains.json` (entry for the mandolin, by GAIN `mandolin`, run as soon as the instrument makes sound and before its `Done when` is evaluated: T-162 depends on the gain)
- Evidence produced: T-140 (mandolin), T-141 to T-146 (mandolin), T-148 to T-154 (mandolin)
- Done when: CORE BUILD; PY `strings and (mandolin or T141 or T142 or T143 or T144 or T145 or T148 or T149 or T150 or T151 or T153)`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: G-P2 (opened by this step)
- Relevant decisions/claims: D-070 to D-072; C-034 to C-038
- Lessons applied: L-20261004T162217Z-nonstationary-recording-analysed-as-one-note; knowledge K-20261004T162313Z (beat-period windows)
- Exclusive resources: generated presets

Gate actions of S-250: push a commit with the marker `[gate-evidence G-P2 mandolin seed=1]` (the tooling exists from `S-210`); check the branch `evidence/G-P2`; write `GATE-G-P2.md` (the demos to point the owner to: `mandolin-01-melody`, `-04-dynamics`, `-06-chords`, `-07-tremolo`, `-201-variant` to `-203-variant`; paste the passing tests and `PERF` lines by hand as for `G-P1`); PUSH; report. While the gate is open, continue with the reeds track.

### S-260 Bouzouki
- Tier: T2
- Profile: software
- Depends on: S-250, and gate G-P2 answered `proceed` or `proceed-with-rescope`
- Inputs: D-073, `core/src/pluck.h`
- Actions: implement the bouzouki in `core/src/bouzouki.cpp`: three variants, octave courses with `octave_order`, body presets.
- Outputs: `core/src/bouzouki.cpp`; `presets/gains.json` (entry for the bouzouki, by GAIN `bouzouki`, run as soon as the instrument makes sound and before its `Done when` is evaluated: T-162 depends on the gain)
- Evidence produced: T-140 (bouzouki), T-146 (bouzouki), T-147, T-152 (bouzouki), T-154 (bouzouki)
- Done when: CORE BUILD; PY `strings`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: none
- Relevant decisions/claims: D-073; C-039 to C-042, C-052
- Lessons applied: none
- Exclusive resources: generated presets

### S-300 Whole core
- Tier: T2
- Profile: software
- Depends on: S-212, S-220, S-230, S-260
- Inputs: the whole core
- Actions:
  1. Delete `core/src/stubs.cpp`; make sure no function throws `NotImplemented`. Re-run GAIN for all five instruments and commit `presets/gains.json` and the regenerated `core/src/generated/presets_data.h`.
  2. Run the complete Catch2 suite, `folk-perf`, and the complete Python suite except the reference tests.
  3. Run `python3 tools/calibrate_reeds.py --check` (the committed offsets match a fresh run with the committed curves within 0.2 cents) and `python3 tools/gen_presets.py --check`.
  4. Build once with `cmake -S . -B $HOME/folk-build-asan -G Ninja -DFOLK_BUILD_PLUGINS=OFF -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-sanitize-recover=undefined" && cmake --build $HOME/folk-build-asan` and run `folk-tests` there with `ASAN_OPTIONS=detect_leaks=0:halt_on_error=1` (the allocation-probe test T-011 replaces `operator new`; if the sanitiser build cannot link because of that, run it with the Catch2 filter `~"T-011*"` and record this in `EXECUTION_LOG.md`).
- Outputs: `presets/gains.json`, `core/src/generated/presets_data.h` (regenerated); removes `core/src/stubs.cpp`
- Evidence produced: T-001 to T-015, T-100 to T-114, T-120 to T-125, T-131 to T-134, T-140 to T-154 and T-160 to T-163, all complete
- Done when: `$B/folk-tests` exits 0 with 27 test cases passed; `$B/folk-locale-tests` exits 0; `cd tests && FOLK_RENDER=$B/folk-render python3 -m pytest -m "not reference"` exits 0 with no failure, error or skip; `$B/folk-perf` exits 0 and prints five `PERF` lines, each recorded in `EXECUTION_LOG.md`; both `--check` commands exit 0; the sanitiser run exits 0.
- Checkpoint: step done; the five local real-time factors.
- On failure: fix the code. A local real-time factor below 4 is not a failure of this step (the gate is on the CI runner, S-320) but is recorded; rule DR-06 applies if S-320 misses.
- Gate: none
- Relevant decisions/claims: D-014, D-015, D-086; C-054
- Lessons applied: groups "dsp-correctness", "frozen-tests"; knowledge K-20261029T030700Z (sanitiser flags)
- Exclusive resources: generated presets

### S-310 Wrapper, plugins and factory presets
- Tier: T2
- Profile: software
- Depends on: S-300
- Inputs: D-094, `plugins/CMakeLists.txt`, `tests/juce/host_test.cpp`
- Actions:
  1. Write `presets/factory.json` with these presets (each sets only the parameters named; everything else default). Harmonica: 'Diatonic C' (variant 0, key 0), 'Diatonic G' (variant 0, key 7), 'Chromatic' (variant 1). Accordion: one per register, named as in D-030 ('Piccolo' to 'Master'), plus 'Clarinet, cassotto' (register 1, cassotto 1), 'Violin, swing' (register 4, musette_cents 4), 'Violin, Scottish' (register 4, musette_cents 25). Melodion: 'Plastic' (range 1, body 0), 'Wooden' (range 1, body 1), 'Accordina' (range 1, body 2), 'Short breath' (range 1, breath_mode 1). Mandolin: 'F-hole archtop' (body 0), 'Oval-hole archtop' (body 1), 'Bowl-back' (body 2). Bouzouki: 'Greek trichordo' (variant 0), 'Greek tetrachordo' (variant 1), 'Irish' (variant 2).
  2. Implement `plugins/common/FolkProcessor.cpp` to D-094. A block larger than the prepared size is processed in chunks. Parameter changes reach the engine through atomics; `setStateInformation` runs on the caller's thread and never touches the engine while `processBlock` runs (validate the text with `loadState` on a temporary engine that has first been given the current parameter values, so that keys missing from the text keep their current values as D-090 says, off the audio thread and, if it is accepted, update the JUCE parameters at once, before `setStateInformation` returns, as T-302 reads them immediately; the audio engine takes the values over at the start of the next block through the same atomics).
  3. Build with the commands of `plan/ENVIRONMENT.md` section 3 (or rule DR-10).
- Outputs: `presets/factory.json`, `plugins/common/FolkProcessor.cpp` (and any files beside it), `README.md` (its sentence saying the repository holds no implementation is replaced, and it gains: what the five plugins are; install notes per OS, with the plugin folder and, on macOS, `xattr -dr com.apple.quarantine <bundle>` because the bundles are unsigned; the unsupported-rate behaviour of D-090; a 'Maintenance' section with one line per CI job saying why it can go red without a code change and which rule applies, R-028)
- Evidence produced: T-302, T-303, T-304
- Done when: the plugin build succeeds; `xvfb-run -a ctest --test-dir $BP --no-tests=error --output-on-failure -E folk-perf` exits 0 with exactly 7 tests passed (the five `...HostTest` programs, `folk-tests` and `folk-locale-tests`), the locale cases run under `de_DE.UTF-8` (ENVIRONMENT section 2); five `.vst3` bundles exist under `$BP/plugins`; `README.md` has the install notes for each OS and a section headed 'Maintenance' with one line per job of `plan/ci/ci.yml`. Under rule DR-10 the same is shown by the `plugins` job of CI instead.
- Checkpoint: step done; where it was verified (local or CI run URL).
- On failure: fix the code; rules DR-05, DR-10.
- Gate: none
- Relevant decisions/claims: D-094; C-057
- Lessons applied: group "juce-build" and "vst3-plugin"; knowledge K-20261104T004700Z (no APVTS state calls in `processBlock`), K-20261009T092101Z (`JUCE_VST3_CAN_REPLACE_VST2=0`), K-20261009T092103Z (no copy into system plugin folders)
- Exclusive resources: generated presets

### S-320 Green on every platform
- Tier: T3
- Profile: software
- Depends on: S-310, S-003
- Inputs: the CI workflow
- Actions:
  1. PUSH and wait for the CI run on the pushed commit.
  2. Read every job's conclusion; for the `plugins` job read the five `pluginval log check: passed` lines per runner; for the `core` job on `ubuntu-24.04` read the five `PERF` lines.
  3. Fix failures in the code and repeat. Apply rule DR-06 for T-013 and rule DR-09 for pluginval.
  4. Before applying DR-06 to any T-013 miss: if `S-212` adopted the two-reed bend provisionally, settle it by rule DR-04 from the harmonica `PERF` line of this run (turn the switch off and re-run if T-013 fails for the harmonica only because of it), and record the outcome in `DEVIATIONS.md`.
  5. Record the three items of `plan/ENVIRONMENT.md` section 5 that `S-003` deferred (universal binary, pluginval archive layout, pluginval log markers) from this run, applying that table's 'If it fails' column.
- Outputs: none new
- Evidence produced: T-013 (gating), T-300, T-310, the CI platform matrix of D-084
- Done when: one CI run on the head commit has `freeze`, `core` (4 runners), `plugins` (4 runners, each with its host-test count of 7 checked), `host-tsan` and `audit` green; job `reference` may still be red at this step and `all-green` with it; the 20 pluginval log checks passed; the five `PERF` lines on `ubuntu-24.04` show `realtime_factor` of 4.00 or more with `gate=1`; the run URL and those figures are in `EXECUTION_LOG.md`.
- Checkpoint: CI run URL.
- On failure: rules DR-06, DR-09, DR-14. Never lower the strictness, disable a pluginval test, or mark a job optional.
- Gate: none
- Relevant decisions/claims: D-082, D-084, D-086; C-045, C-047
- Lessons applied: group "ci-github-actions"; knowledge K-20261104T005300Z (exit status is not coverage proof)
- Exclusive resources: the repository's CI concurrency group

### S-REF Reference recordings and the publication guard
- Tier: T3
- Profile: software
- Depends on: S-110
- Inputs: D-050 to D-052; `tests/py/test_evidence_guard.py`; `tests/py/test_reference.py`
- Actions:
  1. Implement `tools/evidence_guard.py` to the contract in `tests/py/test_evidence_guard.py`, unless `S-210` has already done so.
  2. TinySOL: download and check it as the `reference` job of `plan/ci/ci.yml` does, into `$HOME/folk-refs/tinysol` (outside the repository). If Zenodo is unreachable locally, rely on the CI job (rule DR-13).
  3. Search for further references, in this order, and stop for an instrument as soon as 14 usable notes are indexed (12 for the pairs and 2 for the control pairs of D-053; a private note is never indexed only to serve as a control, so an instrument with 12 or 13 redistributable notes keeps redistributable pairs and the gate record says that two control clips repeat real-pair clips, R-071): (a) Wikimedia Commons, through `https://commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6&srsearch=<instrument>+filetype:audio`, for the five instrument names and for "mouth organ", "melodica", "mandoline", "bouzouki"; start from the four files `Tuning-Sound-G-Bouzouki.ogg`, `Tuning-Sound-d-Bouzouki.ogg`, `Tuning-Sound-a-Bouzouki.ogg`, `Tuning-Sound-dd-Bouzouki.ogg`; (b) Zenodo, through `https://zenodo.org/api/records?q=<instrument>&type=dataset`; (c) the Internet Archive item `GTownChurchSamplingProject`; (d) for the mandolin, first the archive.org item `mandolin-decent-sampler-1.1` ('Stella Mandolin Sample Library (Decent Sampler)', David Hilowitz, CC BY-ND 4.0: private reference under D-051, used for comparison only, never published or shared in any form), then the Philharmonia sample library, mandolin files only, as a private reference under D-051. A note is usable when it is a single isolated note at least 1.2 s long, its pitch is identified, its source page names an author and a licence, and the licence was read on that page. Record every source opened in the source register (`knowledge/K-*-source-register-*.md`), with licence and permitted use.
  4. Write `references/index.csv` with the header of D-052: first the 14 TinySOL accordion rows of `plan/ENVIRONMENT.md` section 1 (the 12 of D-050 and the 2 control notes of D-053), with `file` and `sha256` copied from the table in `plan/ENVIRONMENT.md` section 1 (so the index can be written even where Zenodo is unreachable locally) (MIDI 48, 52, 55, 59, 62, 65, 69, 72, 76, 79, 83, 86, then the control notes 57 and 64; velocity 0.6; `sets` `register=1;cassotto=0;a4_hz=441.6;vibrato_depth=0`; the take chosen by D-052's tie rule; `source_url`, `licence_url` and `accessed` from `plan/ENVIRONMENT.md` section 1; licence `CC-BY-4.0`; author `C.-E. Cella, D. Ghisi, V. Lostanlen, F. Levy, J. Fineberg, Y. Maresz`; `redistributable` `true`), then one row per usable note found by the search (none is a valid result; `velocity` from the source's dynamic marking, pp 0.3, p 0.45, mf 0.6, f 0.8, ff 0.95, otherwise 0.6; `sets` naming the variant that matches the recorded instrument where the source says what it is, for example `body=2` for a bowl-back mandolin or `variant=2` for an Irish bouzouki, otherwise empty; `author` as named on the source page), with `redistributable` `true` only for public-domain, CC0, CC BY and CC BY-SA material. A find under any other licence is indexed only if it is a mandolin note from one of the two private sources named in (d) (D-051); any other restrictive find, for the mandolin or any other instrument, is not indexed and is recorded in the source register as 'not used: not redistributable'. Row ids follow D-052. Store every file at `$HOME/folk-refs/<source>/<path>`, one folder per source as D-052 says (`tinysol`, `philharmonia`, `wikimedia`, `zenodo-<record>`, `archive-org`), whatever its licence (the `redistributable` flag, not the folder, records it); set `FOLK_REF_ROOT=$HOME/folk-refs` and use paths relative to it in the `file` column. Commit `references/index.csv` and `references/ATTRIBUTION.md` (author, title, URL and licence of every redistributable reference, and the TinySOL citation; for each licence what it requires of derived clips: CC BY 4.0 a statement that the clips were cut, resampled and level-matched; CC BY-SA 4.0 that derived clips are offered under CC BY-SA 4.0). Never commit audio.
  5. Implement `tools/fetch_references.py` to D-052 unless `S-210` has done so (`--index`, `--root`, `--archive-cache`, `--archives`, `--only-redistributable`; T-211): for each row, skip it if the file exists with the right hash; otherwise download `source_url` (an archive once into the cache, then extract the member named by `file` without its first path component), place the file at `<root>/<file>`, and check its sha256; refuse an archive larger than 2 GiB (counted while streaming, not trusted from headers); exit 1 on any mismatch or failed download after 3 attempts, naming the row (a cached archive whose hash does not match `references/archives.csv` is deleted and downloaded again; attempts are 5 s apart; `--archive-cache` defaults to `$HOME/folk-ref-archives`). The CI `reference` job already calls it (`plan/ci/ci.yml`), for every row, private ones included.
  6. Record in `EXECUTION_LOG.md`, per instrument, the number of redistributable and private notes indexed and whether D-051's threshold of 12 is met.
- Outputs: `tools/evidence_guard.py`, `tools/fetch_references.py`, `references/index.csv`, `references/archives.csv` (one row per archive, with its sha256 computed from the downloaded archive), `references/ATTRIBUTION.md`, an updated source register
- Evidence produced: T-210, T-211, T-201a
- Done when: PY `T210`; PY `T211`; `cd tests && python3 -m pytest -m reference -k "T201_index"` exits 0; `references/index.csv` has the exact header of D-052; `python3 tools/fetch_references.py --index references/index.csv --root $HOME/folk-refs` exits 0 (or, where a host is unreachable locally, the CI `reference` job's fetch step is green: DR-13); `git ls-files | grep -E "\.(wav|ogg|flac|mp3|aiff?)$"` prints nothing; every source opened is in the source register with a licence read from the source.
- Checkpoint: counts per instrument.
- On failure: an unreachable source is recorded as such in the register and skipped. A licence that cannot be read means the material is not used.
- Gate: none
- Relevant decisions/claims: D-050 to D-052; C-021, C-049 to C-051
- Lessons applied: group "licensing" and "audio-metrics-and-references"
- Exclusive resources: none

### S-330 Reference calibration
- Tier: T2
- Profile: software
- Depends on: S-300, S-REF
- Inputs: `tests/py/test_reference.py`, rule DR-07, D-012 (the three curves), D-071
- Actions:
  1. Run the reference tests locally (`plan/ENVIRONMENT.md` section 3) with `FOLK_TINYSOL` and `FOLK_REF_ROOT` set, or in CI under rule DR-13; save the output to `baseline/reference-before.txt` (pass and fail lines and the printed T-201 lines only; in this saved file, replace the limit value of a T-201 line for an instrument with private references by `<redacted>`; the same line in the CI log is accepted: risk R-016).
  2. If any reference test fails, calibrate by rule DR-07 (after each round also run `$B/folk-perf` without `FOLK_PERF_GATE`, which is informational off the runner (D-086), and record the five `PERF` lines in `EXECUTION_LOG.md`; the next CI run's `ubuntu-24.04` `PERF` lines confirm T-013 after the calibration), running `python3 tools/reed_check.py --instrument <name> --calibrated --out baseline/reed-check-calibrated.csv` and then `tools/calibrate_reeds.py` after any change to a reed curve, and re-running the whole of `S-300`'s `Done when` after each round.
  3. Save the final output to `baseline/reference-after.txt`.
- Outputs: `baseline/reference-before.txt`, `baseline/reference-after.txt`, possibly updated `presets/reeds.json`, `presets/bodies.json` and `presets/strings.json` (`eta_E` and the plectrum factors, DR-07)
- Evidence produced: T-200 (T-200a, T-200b, T-200c, T-200d, T-200e), T-201 (T-201b)
- Done when: `python3 -m pytest -m reference -s` exits 0 locally or in the CI `reference` job, and the `Done when` of `S-300` still holds; or rule DR-07's five rounds are used up, in which case the step is logged as failed, the failing tests are listed in `EXECUTION_LOG.md`, and the plan continues to `S-340` with that failure carried into the evidence of the listening gate of the instrument concerned. A step logged as failed this way counts as done for the `Depends on` lists of later steps (`HANDOFF.md` section 4).
- Checkpoint: rounds used; pass or fail per test.
- On failure: rule DR-07.
- Gate: none
- Relevant decisions/claims: D-050, D-051; C-055
- Lessons applied: L-20261007T150400Z-threshold-not-checked-against-reference-spread; L-20261004T162213Z-timbre-invariance-measured-on-whole-chain
- Exclusive resources: generated presets

### S-340 Demos and evidence tooling
- Tier: T3
- Profile: software
- Depends on: S-300, S-REF
- Inputs: `demos/*.events`, `tools/make_demos.py`, `tools/listening/make_blind_pairs.py`, `tools/evidence_guard.py`, D-052, D-053
- Actions:
  1. Write `tools/build_evidence.py --gate <gate id> --instrument <name> --seed <n> --out <dir> [--private-out <dir>] [--index <file>] [--demos-only]` (`--index` defaults to `references/index.csv`; `--demos-only` renders the demos and writes nothing else, for the confirmation rule of D-053). It (a) renders every `demos/<instrument>-*.events` file to `<dir>/demos/<same name>.wav` at 48 kHz; (b) if `references/index.csv` holds 12 or more notes of the instrument, picks the 12 whose ids (format of D-052) sort first as strings (for the accordion: its 12 TinySOL rows, `accordion-001` to `accordion-012`), converts each reference to a 48 kHz mono 24-bit WAV named `<row id>.wav` in a working folder (soundfile reads WAV, FLAC, Ogg and MP3), renders the candidate for each into a second folder under the same name with the row's `velocity` and `sets` for the reference's duration (at most 3 s), adds the two control pairs of D-053 (stems `control-1` and `control-2`: the 13th and 14th references by id, or the first two where fewer than 14 exist, D-053, against a pure sine at the note's fundamental with the reference's 10 ms RMS envelope), and runs `tools/listening/make_blind_pairs.py --ref <refs> --cand <cands> --out <pairs dir> --seed <n> --pairs 14 --window start`; it passes `--rms-db -23` for reeds and `--rms-db -32` for plucked instruments (short, peaky notes clip at the default level), and afterwards checks every pair file: peak below 0.99, and, for the side the decoded answer key names as the reference, the normalised correlation at lag 0 between that clip and the clip obtained by applying the script's own `prepare()` to the reference file is above 0.99, and likewise for the candidate side (so that a mislabelled or swapped pair is caught before anyone listens; the key is decoded only inside this check and never printed; the check covers all 28 clips); the pairs directory is `<dir>/pairs` when every one of the 14 references used (12 real pairs and 2 controls) is redistributable, otherwise `<private-out>/pairs` with only a file `PAIRS-SHA256SUMS` in `<dir>`; when a private reference is needed and `--private-out` is absent, it prints which and skips the pairs (demos only), exactly as for a missing reference; for the accordion the 12 references are the TinySOL mf notes at MIDI 48, 52, 55, 59, 62, 65, 69, 72, 76, 79, 83, 86 and the candidate patch is that of D-050; (c) writes `<dir>/MANIFEST.json` (every file with its `derived_from` list: a demo `[]`; every pair clip (both sides of every pair, controls included) the ids of all references used by the pair set, so the manifest reveals neither which side is real nor which pairs are controls; `SHA256SUMS` and `ATTRIBUTION.md` `[]`; the pair builder's `key.json.b64` and `sources.json.b64` the ids of all 14 references; `PAIRS-SHA256SUMS` and `METRICS.md` `[]` even when private references contributed, because they hold only digests, counts and the redistributable comparisons, no audio and no per-note values of a private reference; the guard therefore passes on them, and `ATTRIBUTION.md` says that private references were used and how many), `<dir>/SHA256SUMS`, `<dir>/ATTRIBUTION.md` and `<dir>/METRICS.md` (the pass or fail of each frozen test concerning the instrument, taken from a pytest run, and, when references exist, a table comparing references and candidates note by note: spectral centroid over fundamental, level, rise time for reeds or decay rate of the fundamental for plucked instruments, with the largest mismatches listed first; for private references only the count of notes inside and outside the reference spread, where inside means the T-201b criterion: harmonic-profile difference within max(6 dB, the 90th percentile of the set's own neighbour spread)); (d) runs `tools/evidence_guard.py` on `<dir>` and exits non-zero if it fails. The answer key written by the pair builder stays base64-encoded.
  2. Write `tools/listening/score_gate.py --key <key file> --answers <14 letters>`: it decodes the key, reports whether both control pairs were answered correctly, the longest run of one letter, the score over the 12 real pairs with `score_blind.py`'s p-value, and the verdict `void` (a control missed, or one letter for 10 or more of the 14 while the key has fewer than 10 of it) or `valid`; it identifies the controls from `sources.json.b64` (stems `control-1`, `control-2`). Copy `plan/ci/gate-evidence.yml` to `.github/workflows/gate-evidence.yml` unchanged. `tools/build_evidence.py` must accept the arguments that workflow passes (`--gate`, `--instrument`, `--seed`, `--out`, `--render`, `--ref-root`) as well as `--private-out`; `--render` defaults to the environment variable `FOLK_RENDER` and `--ref-root` to `FOLK_REF_ROOT`; it turns both into absolute paths and exports `FOLK_RENDER` to the pytest run behind `METRICS.md`. If any of the 14 references it needs (12 real pairs and 2 controls) is absent under the reference root, it prints which and skips the pairs (demos only). `METRICS.md` lists the non-reference tests only; the reference results are those of the latest CI `reference` job, whose URL the gate record names. `METRICS.md` lists the outcome of `cd tests && python3 -m pytest -m "not reference" -k <name>`, where `<name>` is the instrument's name (the shared reed and common tests carry it in their parameters), except for the plucked instruments, whose shared string tests carry no name: the mandolin uses the expression of `S-250`'s `Done when` and the bouzouki `strings and (bouzouki or T147)`.
  3. Dry run locally: `python3 tools/build_evidence.py --gate G-TEST --instrument accordion --seed 1 --out $HOME/folk-evidence/G-TEST --render $B/folk-render --ref-root $HOME/folk-refs` (with the TinySOL rows fetched into `$HOME/folk-refs` by `tools/fetch_references.py`).
- Outputs: `tools/build_evidence.py`, `tools/listening/score_gate.py`, `.github/workflows/gate-evidence.yml` (a copy of `plan/ci/gate-evidence.yml`)
- Evidence produced: none (tooling for S-LISTEN)
- Done when: the dry run exits 0, prints the pair check as passed for all 28 clips, and its output directory holds `MANIFEST.json`, `SHA256SUMS`, `ATTRIBUTION.md`, `METRICS.md`, at least 20 WAV files under `demos/`, and (TinySOL being available locally) 28 WAV files under `pairs/`; `score_gate.py` with the decoded key's own answers reports `valid` and 12 of 12, and with both controls answered wrongly reports `void`; a run with a seed whose 14-pair key is unbalanced (found by trying seeds 1 to 200 with the pair builder's own seeding) exits with status 3, prints only 'unbalanced key' and writes no file; `--demos-only` writes exactly the `demos/` folder that a full run with the same seed writes (compare the sha256 of every file); a second dry run with an index row's `redistributable` flag temporarily set to `false` for one of the 12 notes writes no `pairs/` directory into the output (try it with a copy of the index passed by `--index`, not the committed file).
- Checkpoint: step done.
- On failure: fix the tool. If TinySOL is not available locally, perform the dry run in CI by pushing a commit with `[gate-evidence G-TEST accordion seed=1]`, verify the branch `evidence/G-TEST`, then delete that branch.
- Gate: none
- Relevant decisions/claims: D-052, D-053
- Lessons applied: group "listening-gate"; knowledge K-20261105T223100Z (pair builder level)
- Exclusive resources: none

### S-REVIEW Code review
- Tier: T2 (a fresh-context agent that wrote none of the code: `HANDOFF.md` section 15)
- Profile: software
- Depends on: S-320, S-330, S-340
- Inputs: `git diff origin/gen-20261114T004707Z-folk-instruments-vst...HEAD`, the frozen tests (read only), `plan/DECISIONS.md`
- Actions: review the whole diff for: dead code, duplication, hidden mutation, unclear names, needless complexity; code paths no frozen test reaches (name them); unsafe memory or file handling, unchecked input at the boundaries (event files, state text, plugin state, command-line arguments), secrets; real-time violations (allocation, locks, I/O on the audio thread: list every match of `mutex|lock_guard|unique_lock|scoped_lock|condition_variable|CriticalSection|ScopedLock|SpinLock|malloc|new ` in `plugins/` and `core/src/` with whether `processBlock` can reach it, since ThreadSanitizer and T-304 do not see a lock that serialises correctly, R-051); each dependency compared with its current release and deprecation notices (JUCE 8.0.17-security, Catch2 v3.16.1, the four Python packages, the five actions, pluginval v1.0.4: compare version numbers, and record any that is behind; where the registry or release page is unreachable from the implementer's network, record that dependency as 'not checked' and add a `DEVIATIONS.md` entry). Classify each finding Critical, High, Medium or Low (the rubric in `HANDOFF.md`). Fix every Critical and High finding before any later step; the fresh-context reviewer verifies each fix. The implementer never accepts a Critical or High finding as a risk: one that cannot be fixed opens gate G-004. Medium and Low findings may be accepted as `R-###` by the reviewer. A fix that corrects the implementer's own mistake is recorded as a lesson. New tests a finding calls for go through a `TEST_CHALLENGE.md` amendment, never straight into the frozen files.
- Outputs: `reviews/CODE_REVIEW.md` (first line: the commit reviewed) (every finding with severity and either the fix commit or an `R-###` entry added to `premortem/RISK_REGISTER.md` with the reason for accepting it)
- Evidence produced: none
- Done when: `reviews/CODE_REVIEW.md` exists, lists the files reviewed, and every finding has a severity and a fix commit or risk ID; every Critical and High finding has a fix commit verified by the reviewer, or an owner's `accept` at G-004; the `Done when` of `S-300` and of `S-320` hold again on the head commit.
- Checkpoint: counts by severity.
- On failure: a Critical or High finding that cannot be fixed opens gate G-004; `BLOCKED.md` only if the owner answers `stop`.
- Gate: G-004 (only if a Critical or High finding cannot be fixed)
- Relevant decisions/claims: all of Part 2 and 3
- Lessons applied: group "planning-process" (review by a fresh context)
- Exclusive resources: none

### S-ADVERSARIAL Adversarial review
- Tier: T2 or T1 (a fresh-context agent that wrote none of the code: `HANDOFF.md` section 15)
- Profile: software
- Depends on: S-REVIEW
- Inputs: the built render tool and plugins, `plan/ASSUMPTIONS.md`, `plan/DECISIONS.md`
- Actions: try to break the product. At least: (1) event files: binary data, 1 GB of text, lines without newline, times as `nan`, `inf`, `1e308`, 10 million events, an `end` at 1e9 s; (2) state text and plugin state: truncated, repeated keys, 65 536 and 65 537 bytes, values `-0`, `1e-320`, locale-style decimal commas; (3) engine calls: 10 000 note-ons in one block, every controller number, parameter changes on every sample, `prepare` at 44 100, 96 000 and again 44 100 without `reset`, `process` with `n` of 0 and of a size above the prepared block; (4) sound: every instrument held for 10 minutes (no growth, no drift above 2 cents, no denormal slowdown: time the last minute against the first), extreme parameter corners (breath 1 with vibrato 1 and 16 keys; `pick_position` 0.5; `pair_detune_cents` 8 with `body_coupling` 1; mistuning at the locking boundary), sample rate 88 200; (5) hand-made mutants of the formulas in `strings.cpp` and `tuning.cpp` (change one constant or sign at a time, ten mutants): each must be caught by a frozen test; a survivor is a finding of severity Medium (High if it changes a result of D-060 to D-062 by more than 1 % and no frozen test notices); (6) every `A-###` that is expressed in code (A-005 formats, A-007 controllers, A-009 performance) checked against the build.
- Outputs: `reviews/ADVERSARIAL_REVIEW.md` (first line: the commit reviewed, which `S-REVIEW-DELTA` diffs from) (each attack, its result, and for each confirmed break either a fix commit, or a `TEST_CHALLENGE.md`-route proposal for a new frozen test, or an accepted `R-###` with severity)
- Evidence produced: none
- Done when: `reviews/ADVERSARIAL_REVIEW.md` exists and covers the six groups; every Critical and High break has a fix commit verified by the reviewer, or an owner's `accept` at G-004 (the implementer never accepts one); the `Done when` of `S-300` and `S-320` hold again on the head commit.
- Checkpoint: counts of attacks and confirmed breaks.
- On failure: Critical or High breaks block `S-LISTEN` until fixed or accepted by the owner at G-004.
- Gate: G-004 (only if a Critical or High break cannot be fixed)
- Relevant decisions/claims: D-015, D-090 to D-094; threat model in `plan/ASSUMPTIONS.md`
- Lessons applied: L-20261101T140000Z-intermittent-host-failure-needs-a-stress-test
- Exclusive resources: none

### S-LISTEN Listening validation
- Tier: T3
- Profile: software (audio)
- Depends on: S-ADVERSARIAL
- Inputs: `tools/build_evidence.py`, `.github/workflows/gate-evidence.yml`, `plan/GATES.md` (gates G-L1 to G-L5), `HANDOFF.md` sections "Listening gates" and "Delivering audio", `references/index.csv`, `demos/*.events`
- Reference sets (frozen at planning; table in `plan/GATES.md`): G-L3 accordion: the 12 TinySOL mf notes at MIDI 48, 52, 55, 59, 62, 65, 69, 72, 76, 79, 83, 86 (redistributable); G-L2 mandolin: the private mandolin notes of D-051 indexed by `S-REF` (the Stella library first, then Philharmonia) if there are 12 or more; G-L1 harmonica, G-L4 melodion, G-L5 bouzouki: whatever `S-REF` indexed, if 12 or more notes, otherwise demos only.
- Demo list: every `demos/<instrument>-*.events` file of the instrument (generated by `tools/make_demos.py`): `-01-melody`, `-02-fast`, `-03-slow`, `-04-dynamics`, `-05-extremes`, `-06-chords`, `-07-vibrato` or `-07-tremolo`, `-08-bend` (not the melodion, which ignores the pitch wheel: D-093), `-09-breath-swell` or `-09-pick-positions`, `-2NN-variant` (one per variant), and for the harmonica `-10-chromatic-on-diatonic`, for the melodion `-11-chords-limited-breath`.
- Pass condition (frozen): at most 8 of 12 real pairs identified correctly in a valid round (both control pairs right, no letter given for 10 or more of the 14; D-053) where pairs exist, and no demo reported as wrong. Round limit: 3 valid rounds per gate.
- Actions: for each instrument in the order harmonica (G-L1), mandolin (G-L2), accordion (G-L3), melodion (G-L4), bouzouki (G-L5); the five gates may be open at the same time, but push one marker commit at a time and wait for its evidence branch before pushing the next (runs of the workflow on one branch share a concurrency group, and only the head commit's message is read):
  1. Push an otherwise empty commit to `impl-<run_id>` with the message `[gate-evidence <gate id> <instrument> seed=<s>]`, where `s = 1000 * g + 100 * N + k` for attempt `k` of round `N` of gate G-L`g` (D-053; G-L1 round 1 starts with seed 1100).
  2. Wait for the `gate-evidence` workflow and read its conclusion. If the `evidence` job failed with 'unbalanced key' (exit status 3, D-053), push a new marker with the next attempt number `k` (the refused seed counts as no attempt); any other failure is fixed and the same marker pushed again. Then verify that branch `evidence/<gate id>` exists, holds `SHA256SUMS` and `MANIFEST.json`, and that its head commit's message names this gate, instrument and seed and the marker commit's hash (an older bundle from an earlier round is never used). For a gate whose pairs are private, the CI demos and the local pairs use the same seed.
  3. If the instrument's pairs use a private reference, the CI run builds demos only (its fetch is redistributable-only, so `tools/build_evidence.py` finds a reference missing, prints which, and skips pairs). Run `python3 tools/build_evidence.py --gate <gate id> --instrument <name> --seed <round seed> --out $HOME/folk-evidence/<gate id> --render $B/folk-render --ref-root $HOME/folk-refs --private-out $HOME/folk-private/<gate id>` locally, and add its `PAIRS-SHA256SUMS` to the gate record. If the private files cannot be downloaded in this environment, the gate record instead asks the owner to download them (Rule 15 (d)) and hand them to the implementer by the file-transfer means of the session (an upload to the session, or a path the owner names that the implementer can read), with the paths and sha256 values of `references/index.csv`; the implementer copies them under `$FOLK_REF_ROOT` and waits; once `tools/fetch_references.py` confirms the hashes, the pairs are built and delivered. `tools/build_evidence.py` is deterministic for a given seed, index and code, so after a container recycle the pairs are rebuilt with the same command and must reproduce the recorded hashes.
  4. Write `GATE-<gate id>.md` (round 1) or `GATE-<gate id>-r<N>.md` from the template, with: the commit the evidence was built from (for the confirmation rule of D-053); for G-L1, the URL of a CI run on the head commit less than 3 days old whose `vst3-*` artifacts the owner can download (if none is that recent, push an otherwise empty commit to `impl-<run_id>` to start one: `workflow_dispatch` works only once the workflow is on `main`; the run must have finished before the next marker commit is pushed, because a push cancels a run still in progress; if G-L1 stays open longer than the artifacts' 3 days, start a new run the same way and update the record; question 4), and the install notes of `README.md` (per OS: folder, and on macOS `xattr -dr com.apple.quarantine <bundle>` because the bundles are unsigned); the evidence branch URL `https://github.com/qualitycoding/folk-instruments/tree/evidence/<gate id>` and zip URL `https://github.com/qualitycoding/folk-instruments/archive/refs/heads/evidence/<gate id>.zip`; the reference set and how many references are redistributable and how many private; the frozen pass condition; the contents of `METRICS.md`; any failed reference test from `S-330`; the questions and allowed responses of `plan/GATES.md` (for an instrument with a reference test recorded as failed in `S-330`, the record names the failing tests and states that `proceed` is not accepted: the owner answers `iterate`, `proceed-with-rescope` naming that shortfall, or `stop`). Deliver private pairs by the delivery rule. PUSH; report the gate in chat.
  5. On a response: record it in the gate file; if pairs were judged, score them with `python3 tools/listening/score_gate.py --key <key file> --answers <the 14 letters>` and record seed, verdict, control results, score over the 12 real pairs, p-value and the listener's remarks verbatim in `listening/<gate id>-round-<N>-attempt-<k>.md` (create the directory); a `void` round is recorded and repeated with a new seed (D-053) and is not a round of the limit; apply the branch of `plan/GATES.md` for the response; for `iterate`, rule DR-12.
  6. Once all five gates are closed, run the comparison of D-053 for each against the head commit and hold a confirmation round where its demos differ.
- Outputs: `GATE-G-L1.md` to `GATE-G-L5.md` (and round files), `listening/*.md`
- Evidence produced: the listening records
- Done when: the comparison of D-053 has been run for every closed gate against the head commit and any confirmation round it started is closed; no gate is `OPEN`; and for each of the five gates its latest closure (a normal or a confirmation round, D-053) is one of: (a) `proceed` or `confirm`: the answer's last line is `wrong: none` (every gate, with or without pairs) and, where pairs exist, the score of the valid attempt it rests on is at most 8 of 12; (b) `confirm` of a gate closed earlier with `proceed-with-rescope`, stating that the recorded shortfall still describes the result; (c) `proceed-with-rescope: <text>` or `proceed-without-pairs: <text>`, the text copied into `DEVIATIONS.md` and naming any demo reported as wrong and, where pairs exist, the score; (d) `stop` (rule DR-15).
- Checkpoint: per gate: rounds, score, response.
- On failure: a `stop` response is handled by rule DR-15 (the instrument stays built and tested). No response: wait (`HANDOFF.md` section 5, "Waiting").
- Gate: G-L1, G-L2, G-L3, G-L4, G-L5 (each at most 3 rounds)
- Relevant decisions/claims: D-050 to D-053; C-055, C-056
- Lessons applied: group "listening-gate"; L-20261004T162210Z-user-premise-dismissed-instead-of-asked (act on the listener's words)
- Exclusive resources: the `gate-evidence` workflow

### S-REVIEW-DELTA Review of changes made after the reviews
- Tier: T2 (a fresh-context agent that wrote none of the code: `HANDOFF.md` section 15)
- Profile: software
- Depends on: S-LISTEN
- Inputs: `git diff <head reviewed by S-ADVERSARIAL>...HEAD` (on a repeat, from the head this step last reviewed) (the commit is in `reviews/ADVERSARIAL_REVIEW.md`), `plan/DECISIONS.md`, the frozen tests (read only)
- Actions: review every change made since the commit `S-ADVERSARIAL` reviewed (fixes for `iterate` responses, fixes from G-L1 question 4, anything else) with the checklist of `S-REVIEW`, and repeat the attacks of `S-ADVERSARIAL` that the changed files touch. Same severity rubric and the same rule: Critical and High are fixed and the fix verified by the reviewer, or accepted only by the owner at G-004. If `S-INTEGRATE` later merges a moved `main`, this step is repeated for the merged diff before the pull request is opened.
- Outputs: `reviews/DELTA_REVIEW.md` (one section per run, each naming its reviewed commit range; a repeat appends a section starting from the head the previous section reviewed; every finding with severity and fix commit or risk ID)
- Evidence produced: none
- Done when: `reviews/DELTA_REVIEW.md` names the range from the commit `S-ADVERSARIAL` reviewed to the head commit, or states that the range is empty; every Critical and High finding has a reviewer-verified fix commit or an owner's `accept` at G-004; the `Done when` of `S-300` and `S-320` hold on the head commit.
- Checkpoint: reviewed range; counts by severity.
- On failure: G-004 for a Critical or High finding that cannot be fixed.
- Gate: G-004 (only if needed)
- Relevant decisions/claims: all of Part 2 and 3
- Lessons applied: group "planning-process" (review by a fresh context)
- Exclusive resources: none

### S-INTEGRATE Integration
- Tier: T3
- Profile: software
- Depends on: S-REVIEW-DELTA
- Inputs: the implementation branch, D-003, D-006
- Actions:
  1. `git fetch origin main`. If `origin/main` has moved since commit `375f6508eb07d8dfe4176ba7b5391ae428471f8d`, merge it into `impl-<run_id>`, then re-run the `Done when` of `S-300` and the manifest check, and repeat `S-REVIEW-DELTA` for the merged diff (before action 3 opens the pull request). A conflict in a frozen file is a `TEST_CHALLENGE.md`, never resolved by editing the test.
  1b. Apply the confirmation rule of D-053 to every closed listening gate against the head commit and finish any confirmation round it starts; any fix made in this step or after a G-004 answer goes through `S-REVIEW-DELTA` again.
  2. Create branch `pr-<run_id>` from `impl-<run_id>` and, in one commit on it, remove `research/`, `premortem/`, `.checkpoints/`, `lessons/`, `knowledge/` (D-003). Re-run `sha256sum -c tests/FROZEN_MANIFEST.sha256` there. In `.github/workflows/ci.yml` on that branch, remove the "Schema of lessons and knowledge items" step of job `freeze` (its inputs no longer exist there); log this in `DEVIATIONS.md`.
  3. If anything was committed to `impl-<run_id>` after action 2 (fixes, records), recreate `pr-<run_id>` from the new head as in action 2. Then push `pr-<run_id>` and open a pull request from it to `main`. The description lists the steps completed, links the gate records, `DEVIATIONS.md`, `reviews/CODE_REVIEW.md`, `reviews/ADVERSARIAL_REVIEW.md` and `reviews/DELTA_REVIEW.md` with the commit range each review covered, and links both `impl-<run_id>` and the generation branch. Add the two closing lines required by the session's attribution rules, if any.
  4. Wait for the pull request's checks. Every check must finish green: the jobs of `ci.yml` including `all-green`, and any check `main`'s protection requires (read in `S-000`).
  5. Do not merge. Record the pull request URL in `EXECUTION_LOG.md` and report it. The description also lists, as owner actions before merging (they are repository settings, which the implementer does not change): the Actions setting 'Require approval for all external contributors' for fork pull requests (read it first where the API allows; the `reference` job fetches private references, R-023), protection of `main` requiring `all-green` (or, where DR-16 applied, requiring the other jobs by name until the shortfall is fixed: the owner chooses), and the 'Maintenance' section of `README.md` written in `S-310` (R-028).
- Outputs: branch `pr-<run_id>`, the pull request
- Evidence produced: none
- Done when: the pull request exists; every check on its head commit is green (none failing, pending or missing); its URL is in `EXECUTION_LOG.md`.
- Checkpoint: pull request URL, head commit.
- On failure: if the pull request cannot be created for lack of permission, halt and write `BLOCKED.md` naming the permission; rule DR-16 for a red `reference` job after a recorded DR-07 failure; otherwise a red check is fixed on `impl-<run_id>` and brought over by repeating actions 1b to 4 (the confirmation rule and `S-REVIEW-DELTA` for the fix, then the pull-request branch) (recreate `pr-<run_id>` from the new head; a force-push to `pr-<run_id>` is allowed because only this plan writes to it). Never force-push `main`, bypass protection, or merge with a check skipped or pending.
- Gate: none (route `pull-request`: the owner merges)
- Relevant decisions/claims: D-003, D-006, D-007
- Lessons applied: groups "git-and-push" and "ci-github-actions"
- Exclusive resources: none

### S-RETRO Retrospective
- Tier: T2 (fresh context: `HANDOFF.md` section 15), after the inputs have been collected into `baseline/retro-digest.md` (by a T4 agent or by the implementer)
- Profile: software
- Depends on: S-INTEGRATE, and every step before it
- Inputs: `EXECUTION_LOG.md`, the commit history of `impl-<run_id>`, `DEVIATIONS.md`, any `BLOCKED.md` and `TEST_CHALLENGE.md`, all `GATE-*.md`, CI run history, `research/PRIOR_KNOWLEDGE.md`, `lessons/`, `knowledge/`, `reviews/`
- Actions: one pass over the records; re-run nothing and change no deliverable. Answer the questions listed in `HANDOFF.md` section "Retrospective", fill its table "Protocol performance" by counting, diff the workflows and manifests of the implementation branch against `plan/ENVIRONMENT.md` and record every unexplained difference as a missing deviation and a lesson, write a lesson for every error or overlooked step not yet recorded and a knowledge item for every new fact, and amend the source register for every source checked after planning.
- Outputs: `baseline/retro-digest.md` (the inputs gathered into one file, by a T4 agent or the implementer), `RETROSPECTIVE.md` (opening with the implementation results header: code-review findings by severity and how many were fixed or accepted, adversarial breaks confirmed, the statement that no mutation step was planned (D-004), and the statement that the work is on `pr-<run_id>` awaiting the owner's merge); new files under `lessons/` and `knowledge/`
- Evidence produced: none
- Done when: every finding in `RETROSPECTIVE.md` links to an `L-` or `K-` file; `python3 scripts/check_knowledge_schema.py` exits 0.
- Checkpoint: counts of lessons and knowledge items.
- On failure: fix the schema errors and re-run the check.
- Gate: none
- Relevant decisions/claims: none
- Lessons applied: all of `research/PRIOR_KNOWLEDGE.md` (question 3 of the retrospective)
- Exclusive resources: none

### S-KNOW Lessons and knowledge push
- Tier: T4
- Profile: software
- Depends on: S-RETRO
- Inputs: `lessons/`, `knowledge/`, `plan/TEMPLATES.md`, `scripts/check_knowledge_schema.py`
- Actions:
  1. Write `GATE-G-003.md` listing every lesson and knowledge item to push (ID, title or statement, tags), the source register on its own line with its source count and the number of rows whose licence is `unknown` or `none stated`, the new tags to add to each store's `TAXONOMY.md`, and the proposed targets: lessons to `https://github.com/qualitycoding/Lessons`, knowledge to `https://github.com/qualitycoding/knowledge`. Allowed responses: `push-to-proposed`, `push-to: <lesson-target> [knowledge-target]`, `do-not-push`. PUSH, report, and halt.
  2. On sign-off: clone each target with `git clone <target>` (full history: the script check below diffs against the planning commits) into a directory outside the repository (if cloning or pushing is refused for lack of access, go to action 3's bundle fallback); copy each lesson to `lessons/<primary-tag>/` (its first `tech:` or `domain:` tag with `:` replaced by `-`, else `general`) and each knowledge item to `knowledge/<subject>/` (its first `subject:` tag without the prefix); add the new tags to `TAXONOMY.md`; run each store's own `python scripts/build_index.py` and `python scripts/check_knowledge_schema.py` (both scripts live in the stores, not in this repository) only after `git diff --stat 9934bb5 HEAD -- scripts/` (lessons) or `f3d176d` (knowledge) shows no change to `scripts/`, or the changed lines have been read and found harmless (record which); run them from a copy of the clone with its remote removed, in a shell with no credential variables and `GIT_TERMINAL_PROMPT=0`, and push from the original clone in a separate command (R-029); commit and push each store on the branch the response names (default: the store's default branch; if this session may only push to a designated branch of the stores, push there and say so in the report).
  3. If a push is rejected because the target moved, pull, rebuild the indexes, and retry, up to 3 times per store. If a push still fails, a target is unreachable, or no response arrives: build the bundles from this repository: copy `lessons/` (or `knowledge/`) into a new empty git repository outside the working tree in the Appendix C layout, commit, run `git bundle create lessons-<run_id>.bundle --all` (or `knowledge-<run_id>.bundle`) there, commit the bundle files to `impl-<run_id>` under `bundles/`, PUSH, and report their paths.
- Outputs: `GATE-G-003.md`; pushed stores or bundles
- Evidence produced: none
- Done when: the lesson store's index lists every pushed lesson ID and the knowledge store's index lists every pushed knowledge ID including the source register; or the response was `do-not-push`; or the bundles were written and reported.
- Checkpoint: response; store commits or bundle paths.
- On failure: action 3.
- Gate: G-003
- Relevant decisions/claims: A-015
- Lessons applied: group "git-and-push"
- Exclusive resources: none
