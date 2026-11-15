# Plan

<!-- STATUS HEADER: written in Phase 5 -->

Read `HANDOFF.md` first. Conventions used in every step:

- **Repository root** is the working directory unless a command says otherwise. `<run_id>` is `gen-20261114T004707Z-folk-instruments-vst`; the implementation branch is `impl-gen-20261114T004707Z-folk-instruments-vst`.
- **Build directories** live outside the repository: `B=$HOME/folk-build` (core) and `BP=$HOME/folk-build-plugins` (plugins). The commands are those of `plan/ENVIRONMENT.md` sections 3 and 4 with `build` replaced by `$B` and `build-plugins` by `$BP`.
- **CORE BUILD** means: `cmake -S . -B $B -G Ninja -DCMAKE_BUILD_TYPE=Release -DFOLK_BUILD_PLUGINS=OFF && cmake --build $B`.
- **CPP `<filter>`** means: `$B/folk-tests "<filter>"` exits with status 0 (the filter is a Catch2 test-name pattern; `*` is a wildcard).
- **PY `<expression>`** means: `cd tests && FOLK_RENDER=$B/folk-render python3 -m pytest -m "not reference" -k "<expression>"` exits with status 0 and reports no test skipped or deselected by anything other than `-k` and `-m`.
- **PUSH** means the push cadence of `HANDOFF.md`: commit, `git push origin impl-<run_id>`, then `git ls-remote origin impl-<run_id>` equals `git rev-parse HEAD`.
- **LOG** means: append one line to `EXECUTION_LOG.md` (UTC time, step ID, attempt number, outcome, commit hash, note).
- Every step ends with LOG and PUSH, and its `Checkpoint` line says what to add to `.checkpoints/state.json` (`completed` gains the step ID).
- Post-conditions (Rule 14) apply to every step even where not repeated: each file in `Outputs` exists, is non-empty, and passes the sanity check named in `Done when`.
- New source files are added to `CMakeLists.txt`; `core/src/stubs.cpp` shrinks as functions are implemented and is deleted in `S-300`.
- The frozen files are listed in `tests/FROZEN_MANIFEST.sha256`. Never edit them (rule DR-05).

Order at a glance: `S-000`, `S-002`, `S-003`; then two tracks that may run concurrently: reeds (`S-100`, `S-110`, `S-200`, `S-201`, `S-210`, gate `G-P1`, `S-212`, `S-220`, `S-230`) and strings (`S-101`, `S-240`, `S-250`, gate `G-P2`, `S-260`); then `S-300`, `S-310`, `S-320`, `S-REF`, `S-330`, `S-340`, `S-REVIEW`, `S-ADVERSARIAL`, `S-LISTEN`, `S-INTEGRATE`, `S-RETRO`, `S-KNOW`.

---

### S-000 Environment and access verification
- Tier: T4
- Profile: software
- Depends on: none
- Inputs: `HANDOFF.md`, `plan/ENVIRONMENT.md`, `.checkpoints/state.json`
- Actions:
  1. Read every `GATE-*.md` in the repository root, if any; an `OPEN` gate blocks the steps it lists.
  2. `git fetch origin && git checkout -b impl-gen-20261114T004707Z-folk-instruments-vst origin/gen-20261114T004707Z-folk-instruments-vst` (if the branch already exists on the remote, check it out instead and continue from `EXECUTION_LOG.md`).
  3. Re-run the environment-class probe: note the time, create `$HOME/folk-probe.txt`, start `sleep 600 &`, and at the start of the next turn check whether the file and the process survive. Record `stable` only if both do; otherwise `ephemeral`. Under `ephemeral`, the section "Ephemeral environments" of `HANDOFF.md` applies to every later step.
  4. Run the setup commands of `plan/ENVIRONMENT.md` section 2. If `apt-get` is unavailable (no root), record it and apply rule DR-10.
  5. Check credentials and reachability from this environment, recording each result in `.checkpoints/state.json` under `diagnostic_impl`: `git ls-remote origin` (read); an empty commit pushed to `impl-<run_id>` and verified with `ls-remote` (write); `git ls-remote --tags https://github.com/juce-framework/JUCE 8.0.17-security` and the same for `https://github.com/catchorg/Catch2 v3.16.1` (dependencies); `python3 -m pip download --no-deps -d "$HOME/folk-pipcheck" numpy==2.5.3` (PyPI); `curl --fail --head https://zenodo.org/api/records/3685367` (reference data); whether a pull request can be opened (list open pull requests of the repository with the available GitHub tool); the branch protection and required checks of `main` (read them if the tool allows; otherwise record "not readable").
  6. Create `EXECUTION_LOG.md` with a header line and the entry for this step; create `DEVIATIONS.md` with a header and the line "No deviations yet."
- Outputs: `EXECUTION_LOG.md`, `DEVIATIONS.md`, updated `.checkpoints/state.json`
- Evidence produced: none
- Done when: every check of action 5 is recorded; read, write, JUCE, Catch2 and PyPI succeeded; `EXECUTION_LOG.md` and `DEVIATIONS.md` exist and are non-empty.
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
  3. Run `$B/folk-tests`, `$B/folk-perf`, and `cd tests && FOLK_RENDER=$B/folk-render python3 -m pytest -m "not reference"`; save the last 30 lines of each to `baseline/red-run.txt`.
  4. Compare with the counts in `plan/TRACEABILITY.md`, section "State at the freeze".
- Outputs: `baseline/red-run.txt`
- Evidence produced: none
- Done when: the manifest check passes; the three programs build; `baseline/red-run.txt` shows the Catch2 run with 27 failed test cases of 27, and the pytest run with exactly the tool-check tests passing (the tests in `test_metrics_selfcheck.py` and `test_pluginval_log_check.py`) and every other test failing; the counts equal those in `plan/TRACEABILITY.md`.
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
  1. `mkdir -p .github/workflows && cp plan/ci/ci.yml .github/workflows/ci.yml`. Add `.gitattributes` with the two lines `tests/** text eol=lf` and `*.events text eol=lf` (Windows checkouts must not change the hashed files). Add `.gitignore` with `build*/`, `__pycache__/`, `*.pyc`, `refs-private/`.
  2. Commit and PUSH. This first run is the spike for the unverified items of `plan/ENVIRONMENT.md` section 5.
  3. Read the run's results (job conclusions and failing step names through the available GitHub tool). Expected at this point: job `freeze` succeeds; job `audit` succeeds; jobs `core`, `plugins` and `reference` fail in their test steps, not in checkout, configure, build or download steps; `all-green` fails.
  4. For each unverified item in the table of `plan/ENVIRONMENT.md` section 5, record what the run showed in `EXECUTION_LOG.md`, and apply that table's "If it fails" column.
- Outputs: `.github/workflows/ci.yml`, `.gitattributes`, `.gitignore`
- Evidence produced: none (T-300 and T-310 become runnable)
- Done when: the workflow file is byte-identical to `plan/ci/ci.yml` apart from deviations logged under action 4; the run exists; `freeze` and `audit` are green; on all four runners the `core` job reached its "C++ unit and engine tests" step and the `plugins` job reached its "Host tests" step (configure and build succeeded everywhere); the `reference` job downloaded TinySOL and its step "Reference notes exist" passed.
- Checkpoint: CI run URL and per-job conclusions.
- On failure: rules DR-01, DR-02, DR-14. If CI logs cannot be read from this environment, add a final `if: failure()` step to the failing job that prints the last 200 lines of the failing command's captured output to the job summary (`$GITHUB_STEP_SUMMARY`), log the addition as a deviation, and read the summary.
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
  2. Write `tools/gen_presets.py`, which turns `presets/*.json` into `core/src/generated/presets_data.h` (constant arrays); add a CMake custom command that runs it when a preset file changes, and commit the generated header as well so that a build without Python works. The tool exits non-zero on a missing field.
  3. Implement in `core/src/tuning.cpp` every function declared in `tuning.h`, reading the generated tables, with the error behaviour of D-090.
- Outputs: `presets/harmonica.json`, `presets/accordion.json`, `presets/strings.json`, `tools/gen_presets.py`, `core/src/generated/presets_data.h`, `core/src/tuning.cpp`
- Evidence produced: T-001, T-002, T-003, T-004, T-007
- Done when: CORE BUILD; CPP `T-001*`, CPP `T-002*`, CPP `T-003*`, CPP `T-004*`, CPP `T-007*`; `python3 tools/gen_presets.py --check` exits 0 (the committed header matches the JSON files) and exits 1 after a temporary edit of one JSON value (try it, then revert).
- Checkpoint: step done.
- On failure: fix the code, never the test. A table value that contradicts a frozen test is a rule DR-05 case.
- Gate: none
- Relevant decisions/claims: D-020, D-021, D-023, D-030, D-070, D-072, D-073; C-011, C-012, C-014, C-017, C-034, C-039, C-040
- Lessons applied: L-20261007T150300Z-hand-typed-frozen-constant (tables are generated, not typed twice)
- Exclusive resources: none

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
- Exclusive resources: none

### S-110 Engine frame and render tool
- Tier: T2
- Profile: software
- Depends on: S-100
- Inputs: `core/include/folk/engine.h`, D-090 to D-093, `tests/cpp/param_table.h`
- Actions:
  1. Implement `instrumentName`, `instrumentFromName` and `Engine::create` for all five instruments on a shared base class in `core/src/engine_base.cpp`: the parameter table of D-091 (copy the values from `tests/cpp/param_table.h` into `presets/params.json` and generate them with `tools/gen_presets.py`), clamping and rounding, an event queue of fixed capacity (256 events per block; further events in the same block are dropped) sorted by sample offset, sample-accurate dispatch inside `process`, `reset`, `saveState`, `loadState` (all checks of T-014), `tailSeconds`, and the output stage of D-015. At this step every instrument produces silence.
  2. Implement `tools/folk-render/main.cpp` to the contract of D-092, including its own WAV writer, atomic output (temporary file, then rename), and all exit statuses.
- Outputs: `core/src/engine_base.cpp`, `core/src/engine_base.h`, `presets/params.json`, `tools/folk-render/main.cpp`
- Evidence produced: T-008, T-014, part of T-009, part of T-161
- Done when: CORE BUILD; CPP `T-008*`; CPP `T-014*`; CPP `T-009 out-of-range*`; PY `T161 and not event_file_features`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: none
- Relevant decisions/claims: D-015, D-090 to D-093; C-056
- Lessons applied: groups "cpp" and "dsp-correctness"; knowledge K-20261105T233000Z (no large objects on the stack: allocate voices on the heap in `prepare`)
- Exclusive resources: none

### S-200 Reed voice
- Tier: T2
- Profile: software
- Depends on: S-110
- Inputs: D-010 to D-016; `research/spikes/s12-reed-similarity-scaling/similarity.py` (the reference for the equations and their order); `research/spikes/s05-reed-cost/reed_bench2.cpp`
- Actions:
  1. Implement `core/src/reed.h` and `reed.cpp`: a `Reed` (parameters from D-012 for a given natural frequency, useful-section table built outside the audio thread, sub-step count from D-011), its step function, the base-rate summing bus and the half-band decimator, the breath smoothing and pressure law of D-016, vibrato, the safety measures of D-015.
  2. Write `tools/reed_probe.cpp` (a small program built with the core, not shipped in the plugins) that runs one reed at a given natural frequency and constant reservoir pressure for a given time at a given host rate and prints sounding frequency in cents relative to the natural frequency, tip amplitude over `x0`, and whether any state became non-finite.
- Outputs: `core/src/reed.h`, `core/src/reed.cpp`, `tools/reed_probe.cpp`
- Evidence produced: none (verified in S-201)
- Done when: CORE BUILD including `reed_probe`; `reed_probe` for 444 Hz at 400 Pa and 48000 Hz host rate prints an offset between -24.5 and -21.5 cents and an amplitude between 4.4 and 4.9 times `x0` (spike S12: -23.1 cents, 4.63).
- Checkpoint: step done.
- On failure: compare with `similarity.py` line by line (order of updates, signs, units); the spike is the reference.
- Gate: none
- Relevant decisions/claims: D-010 to D-016; C-001 to C-004, C-053, C-054, C-059, C-060
- Lessons applied: group "dsp-correctness"
- Exclusive resources: none

### S-201 Reed check across the range and tuning calibration
- Tier: T3
- Profile: software
- Depends on: S-200
- Inputs: `tools/reed_probe.cpp`, D-012, D-016, rule DR-03
- Actions:
  1. Run `reed_probe` at the 12 check pitches of rule DR-03 (natural frequency = equal-tempered frequency of the MIDI note), at 50, 100, 400, 1500 and 1800 Pa, at host rates 44100 and 48000; write the table to `baseline/reed-check.csv`.
  2. Apply rule DR-03 to any row that fails.
  3. Write `tools/calibrate_reeds.py` as D-016 describes (it calls `reed_probe`), run it, and commit `presets/reeds.json` with the offset table and the three curves of D-012 all equal to 1.
- Outputs: `baseline/reed-check.csv`, `tools/calibrate_reeds.py`, `presets/reeds.json`
- Evidence produced: none
- Done when: `baseline/reed-check.csv` has 120 rows; every 50 Pa row is silent (amplitude below 0.02 `x0`); every other row sounds with no non-finite state, and with an offset within 1.5 cents of -20.1 (100 Pa), -23.1 (400 Pa), -23.3 (1500 Pa) (no offset target at 1800 Pa); `presets/reeds.json` parses and holds, for each of the four host rates, 109 offsets (MIDI 16 to 124) between -27 and -17 cents.
- Checkpoint: step done; the sub-step constant in use.
- On failure: rule DR-03.
- Gate: none
- Relevant decisions/claims: D-011, D-012, D-016; C-059, C-060
- Lessons applied: L-20261007T150600Z-control-mapping-formulas-unverified (the mapping is measured, not assumed)
- Exclusive resources: none

### S-210 Harmonica
- Tier: T2
- Profile: software
- Depends on: S-201
- Inputs: D-020 to D-024, `core/src/reed.h`, `presets/harmonica.json`
- Actions: implement the harmonica instrument in `core/src/harmonica.cpp`: note mapping through `diatonicNoteFor` and `chromaticNoteFor`, the baseline bend of D-022, breath sources, vibrato, `wah`, `air_noise`, `airtightness`, `valve_buzz`, polyphony 4 with oldest-first stealing, silence for unplayable notes.
- Outputs: `core/src/harmonica.cpp`
- Evidence produced: T-100 (harmonica), T-101 to T-108 (harmonica), T-110 to T-114
- Done when: CORE BUILD; PY `harmonica`; PY `(T100 or T101 or T102 or T103 or T104 or T105 or T106 or T107 or T108) and harmonica`.
- Checkpoint: step done.
- On failure: fix the code. If a reed test fails only at the extreme notes, re-check S-201's table first. Rule DR-05 for a test that looks wrong.
- Gate: G-P1 (the gate is opened by this step; see `plan/GATES.md`)
- Relevant decisions/claims: D-020 to D-024; C-011 to C-014
- Lessons applied: group "dsp-correctness"
- Exclusive resources: none

Gate actions of S-210 (after its tests pass): render `demos/harmonica-01-melody.events`, `-04-dynamics`, `-08-bend`, `-10-chromatic-on-diatonic` and `-203-variant` to WAV with `folk-render` at 48 kHz into `$HOME/folk-pilot/G-P1/`; write `GATE-G-P1.md` from the template in `HANDOFF.md` with the evidence and questions of `plan/GATES.md`; deliver the five files to the owner by the delivery rule of `HANDOFF.md` (section "Delivering audio"); PUSH; report in chat. While the gate is open, continue with the strings track and with `S-212`.

### S-212 Optional: two-reed bend
- Tier: T2
- Profile: software
- Depends on: S-210
- Inputs: D-022, rule DR-04, C-013
- Actions: follow rule DR-04. The experiment: one channel with a blow reed and a draw reed sharing the cell pressure, the draw reed mounted with the opposite orientation, and a second upstream volume and passage (the player's mouth) whose resonance frequency is the bend control; the wheel moves that resonance from 1.2 times the higher reed's frequency down to the lower reed's frequency. Keep it behind an internal build-time switch until the rule's conditions are met.
- Outputs: either an updated `core/src/harmonica.cpp` (adopted) or no code change (not adopted); in both cases an entry in `DEVIATIONS.md` and a knowledge item `knowledge/K-<time>-two-reed-bend-experiment.md` recording what was tried and measured
- Evidence produced: none new
- Done when: rule DR-04 has been applied and its outcome recorded; PY `harmonica` and PY `harmonica and (T100 or T101 or T102 or T103)` still pass; CPP `T-0*` still passes for the tests that passed before the step.
- Checkpoint: adopted or not.
- On failure: not adopting is a valid outcome, not a failure.
- Gate: none
- Relevant decisions/claims: D-022; C-013
- Lessons applied: none
- Exclusive resources: none

### S-220 Accordion
- Tier: T2
- Profile: software
- Depends on: S-201, and gate G-P1 answered `proceed` or `proceed-with-rescope`
- Inputs: D-030 to D-033, `core/src/reed.h`, `presets/accordion.json`
- Actions: implement the accordion in `core/src/accordion.cpp`: ranks per register, tremolo by D-031, cassotto and sordina filters, bend, key noise, bellows from velocity or controller, polyphony 16 keys, a change of `register` while keys are held taking effect within one block (ranks start or stop for held keys).
- Outputs: `core/src/accordion.cpp`
- Evidence produced: T-100 to T-108 (accordion), T-120 to T-125, T-161 event-file features
- Done when: CORE BUILD; PY `accordion`; PY `T161`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: none
- Relevant decisions/claims: D-030 to D-033; C-017 to C-020
- Lessons applied: L-20261004T162220Z-beat-phase-biased-harmonic-levels (levels of beating sounds are measured over whole beat periods)
- Exclusive resources: none

### S-230 Melodion
- Tier: T2
- Profile: software
- Depends on: S-201, and gate G-P1 answered `proceed` or `proceed-with-rescope`
- Inputs: D-040, D-041, `core/src/reed.h`
- Actions: implement the melodion in `core/src/melodion.cpp`: the plenum of D-041 in both breath modes, ranges, bodies, moisture, polyphony 10.
- Outputs: `core/src/melodion.cpp`
- Evidence produced: T-100 to T-108 (melodion), T-131 to T-134
- Done when: CORE BUILD; PY `melodion`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: none
- Relevant decisions/claims: D-040, D-041; C-023 to C-025
- Lessons applied: none
- Exclusive resources: none

### S-240 String, course and body
- Tier: T2
- Profile: software
- Depends on: S-101, S-110
- Inputs: D-060 to D-064, `presets/strings.json`
- Actions:
  1. Write `presets/bodies.json` from the table of D-071 (each mode with `hz`, `q`, `gain`, `claim`, `confidence`), generated into the header by `tools/gen_presets.py`.
  2. Implement `core/src/pluck.h` and `pluck.cpp`: the partial bank, the 2 x 2 pair blocks with their matrix exponential, the pluck of D-063, damping, tremolo, sustain, the body of D-064 with its admittance, the `tap` event, the control-rate tick, and the `--dump-model` data.
- Outputs: `presets/bodies.json`, `core/src/pluck.h`, `core/src/pluck.cpp`
- Evidence produced: none (verified in S-250)
- Done when: CORE BUILD; a unit program or Catch2 test of the implementer's own (not frozen) shows that the pair block reproduces `research/spikes/s04-coupled-pair/output.json`: early and late decay rates of the 1-cent case within 2 % of -75.3 and -5.14 dB/s.
- Checkpoint: step done.
- On failure: compare with `research/spikes/s04-coupled-pair/pair.py`.
- Gate: none
- Relevant decisions/claims: D-060 to D-064; C-026 to C-031, C-042
- Lessons applied: knowledge K-20261009T120109Z (two-pole resonator with an input zero for a cosine start)
- Exclusive resources: none

### S-250 Mandolin
- Tier: T2
- Profile: software
- Depends on: S-240
- Inputs: D-070 to D-072, `core/src/pluck.h`
- Actions: implement the mandolin in `core/src/mandolin.cpp`: three bodies, four courses, note-to-course rule, all plucked-instrument parameters.
- Outputs: `core/src/mandolin.cpp`
- Evidence produced: T-140 (mandolin), T-141 to T-146 (mandolin), T-148 to T-153
- Done when: CORE BUILD; PY `strings and (mandolin or T141 or T142 or T143 or T144 or T145 or T148 or T149 or T150 or T151 or T153)`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: G-P2 (opened by this step)
- Relevant decisions/claims: D-070 to D-072; C-034 to C-038
- Lessons applied: L-20261004T162217Z-nonstationary-recording-analysed-as-one-note; knowledge K-20261004T162313Z (beat-period windows)
- Exclusive resources: none

Gate actions of S-250: render `demos/mandolin-01-melody.events`, `-04-dynamics`, `-06-chords`, `-07-tremolo` and the three `-20x-variant` files into `$HOME/folk-pilot/G-P2/`; write `GATE-G-P2.md`; deliver; PUSH; report. While the gate is open, continue with the reeds track.

### S-260 Bouzouki
- Tier: T2
- Profile: software
- Depends on: S-250, and gate G-P2 answered `proceed` or `proceed-with-rescope`
- Inputs: D-073, `core/src/pluck.h`
- Actions: implement the bouzouki in `core/src/bouzouki.cpp`: three variants, octave courses with `octave_order`, body presets.
- Outputs: `core/src/bouzouki.cpp`
- Evidence produced: T-140 (bouzouki), T-146 (bouzouki), T-147, T-152 (bouzouki)
- Done when: CORE BUILD; PY `strings`.
- Checkpoint: step done.
- On failure: fix the code; rule DR-05.
- Gate: none
- Relevant decisions/claims: D-073; C-039 to C-042, C-052
- Lessons applied: none
- Exclusive resources: none

### S-300 Whole core
- Tier: T2
- Profile: software
- Depends on: S-212, S-220, S-230, S-260
- Inputs: the whole core
- Actions:
  1. Delete `core/src/stubs.cpp`; make sure no function throws `NotImplemented`.
  2. Run the complete Catch2 suite, `folk-perf`, and the complete Python suite except the reference tests.
  3. Run `python3 tools/calibrate_reeds.py --check` (the committed offsets match a fresh run within 0.2 cents) and `python3 tools/gen_presets.py --check`.
  4. Build once with `-DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-sanitize-recover=undefined" -DCMAKE_BUILD_TYPE=RelWithDebInfo` into `$HOME/folk-build-asan` and run `folk-tests` there with `ASAN_OPTIONS=detect_leaks=0:halt_on_error=1` (the allocation-probe test T-011 replaces `operator new`; if the sanitiser build cannot link because of that, run it with the Catch2 filter `~"T-011*"` and record this in `EXECUTION_LOG.md`).
- Outputs: none new (removes `core/src/stubs.cpp`)
- Evidence produced: T-001 to T-015 complete, T-100 to T-163 complete
- Done when: `$B/folk-tests` exits 0 with 27 test cases passed; `cd tests && FOLK_RENDER=$B/folk-render python3 -m pytest -m "not reference"` exits 0 with no failure, error or skip; `$B/folk-perf` exits 0 and prints five `PERF` lines, each recorded in `EXECUTION_LOG.md`; both `--check` commands exit 0; the sanitiser run exits 0.
- Checkpoint: step done; the five local real-time factors.
- On failure: fix the code. A local real-time factor below 4 is not a failure of this step (the gate is on the CI runner, S-320) but is recorded; rule DR-06 applies if S-320 misses.
- Gate: none
- Relevant decisions/claims: D-014, D-015, D-086; C-054
- Lessons applied: groups "dsp-correctness", "frozen-tests"; knowledge K-20261029T030700Z (sanitiser flags)
- Exclusive resources: none

### S-310 Wrapper, plugins and factory presets
- Tier: T2
- Profile: software
- Depends on: S-300
- Inputs: D-094, `plugins/CMakeLists.txt`, `tests/juce/host_test.cpp`
- Actions:
  1. Write `presets/factory.json`: for each instrument one preset per variant listed in `tools/make_demos.py` (`INS[...]` last element), named after the variant (for example "Clarinet", "Musette (authentic)", "Bowl-back", "Irish").
  2. Implement `plugins/common/FolkProcessor.cpp` to D-094. A block larger than the prepared size is processed in chunks. Parameter changes reach the engine through atomics; `setStateInformation` runs on the caller's thread and never touches the engine while `processBlock` runs (swap a pending state under a spin-free try-lock or apply it at the start of the next block).
  3. Build with the commands of `plan/ENVIRONMENT.md` section 3 (or rule DR-10).
- Outputs: `presets/factory.json`, `plugins/common/FolkProcessor.cpp` (and any files beside it)
- Evidence produced: T-302
- Done when: the plugin build succeeds; `xvfb-run -a ctest --test-dir $BP --output-on-failure -E folk-perf` exits 0 with the five `...HostTest` tests and `folk-tests` passed; five `.vst3` bundles exist under `$BP/plugins`. Under rule DR-10 the same is shown by the `plugins` job of CI instead.
- Checkpoint: step done; where it was verified (local or CI run URL).
- On failure: fix the code; rules DR-05, DR-10.
- Gate: none
- Relevant decisions/claims: D-094; C-057
- Lessons applied: group "juce-build" and "vst3-plugin"; knowledge K-20261104T004700Z (no APVTS state calls in `processBlock`), K-20261009T092101Z (`JUCE_VST3_CAN_REPLACE_VST2=0`), K-20261009T092103Z (no copy into system plugin folders)
- Exclusive resources: none

### S-320 Green on every platform
- Tier: T3
- Profile: software
- Depends on: S-310, S-003
- Inputs: the CI workflow
- Actions:
  1. PUSH and wait for the CI run on the pushed commit.
  2. Read every job's conclusion; for the `plugins` job read the five `pluginval log check: passed` lines per runner; for the `core` job on `ubuntu-24.04` read the five `PERF` lines.
  3. Fix failures in the code and repeat. Apply rule DR-06 for T-013 and rule DR-09 for pluginval.
- Outputs: none new
- Evidence produced: T-013 (gating), T-300, T-310, the CI platform matrix of D-084
- Done when: one CI run on the head commit has `freeze`, `core` (4 runners), `plugins` (4 runners) and `audit` green; job `reference` may still be red at this step and `all-green` with it; the 20 pluginval log checks passed; the five `PERF` lines on `ubuntu-24.04` show `realtime_factor` of 4.00 or more with `gate=1`; the run URL and those figures are in `EXECUTION_LOG.md`.
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
  1. Implement `tools/evidence_guard.py` to the contract in `tests/py/test_evidence_guard.py`.
  2. TinySOL: download and check it as the `reference` job of `plan/ci/ci.yml` does, into `$HOME/folk-refs/tinysol` (outside the repository). If Zenodo is unreachable locally, rely on the CI job (rule DR-13).
  3. Search for further references, in this order, and stop for an instrument as soon as 12 usable notes are indexed: (a) Wikimedia Commons, through `https://commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6&srsearch=<instrument>+filetype:audio`, for the five instrument names and for "mouth organ", "melodica", "mandoline", "bouzouki"; start from the four files `Tuning-Sound-G-Bouzouki.ogg`, `Tuning-Sound-d-Bouzouki.ogg`, `Tuning-Sound-a-Bouzouki.ogg`, `Tuning-Sound-dd-Bouzouki.ogg`; (b) Zenodo, through `https://zenodo.org/api/records?q=<instrument>&type=dataset`; (c) the Internet Archive item `GTownChurchSamplingProject`; (d) the Philharmonia sample library, mandolin files only, as a private reference under D-051. A note is usable when it is a single isolated note at least 1.2 s long, its pitch is identified, its source page names an author and a licence, and the licence was read on that page. Record every source opened in the source register (`knowledge/K-*-source-register-*.md`), with licence and permitted use.
  4. Write `references/index.csv` with the header of D-052 and one row per usable note (none is a valid result), with `redistributable` `true` only for public-domain, CC0, CC BY and CC BY-SA material. Store redistributable files under `$HOME/folk-refs/redistributable/` and private ones under `$HOME/folk-refs/private/`; set `FOLK_REF_ROOT=$HOME/folk-refs` and use paths relative to it in the `file` column. Commit `references/index.csv` and `references/ATTRIBUTION.md` (author, title, URL and licence of every redistributable reference, and the TinySOL citation). Never commit audio.
  5. For the CI `reference` job: add a step before "Reference comparison" that downloads each redistributable file of the index from its `source_url` into `refs-redistributable/` at the indexed relative path and checks its sha256; rows with `redistributable` `false` are not downloaded in CI, so T-201 in CI sees only redistributable notes (the private mandolin comparison runs locally, action 6). Implement this as `tools/fetch_references.py --index references/index.csv --out refs-redistributable --only-redistributable`, which exits non-zero on a hash mismatch.
  6. Record in `EXECUTION_LOG.md`, per instrument, the number of redistributable and private notes indexed and whether D-051's threshold of 12 is met.
- Outputs: `tools/evidence_guard.py`, `tools/fetch_references.py`, `references/index.csv`, `references/ATTRIBUTION.md`, an updated source register
- Evidence produced: T-210, T-201a
- Done when: PY `T210`; `cd tests && python3 -m pytest -m reference -k "T201_index"` exits 0; `references/index.csv` has the exact header of D-052; `git ls-files | grep -E "\.(wav|ogg|flac|mp3|aiff?)$"` prints nothing; every source opened is in the source register with a licence read from the source.
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
  1. Run the reference tests locally (`plan/ENVIRONMENT.md` section 3) with `FOLK_TINYSOL` and `FOLK_REF_ROOT` set, or in CI under rule DR-13; save the output to `baseline/reference-before.txt` (pass and fail lines and the printed T-201 lines only; no reference-derived numbers for private references beyond pass counts).
  2. If any reference test fails, calibrate by rule DR-07, re-running the check of `S-201` (its `Done when`) and `tools/calibrate_reeds.py` after any change to a reed curve, and re-running the whole of `S-300`'s `Done when` after each round.
  3. Save the final output to `baseline/reference-after.txt`.
- Outputs: `baseline/reference-before.txt`, `baseline/reference-after.txt`, possibly updated `presets/reeds.json` and `presets/bodies.json`
- Evidence produced: T-200, T-201b
- Done when: `python3 -m pytest -m reference -s` exits 0 locally or in the CI `reference` job, and the `Done when` of `S-300` still holds; or rule DR-07's five rounds are used up, in which case the step is logged as failed, the failing tests are listed in `EXECUTION_LOG.md`, and the plan continues to `S-340` with that failure carried into the evidence of the listening gate of the instrument concerned.
- Checkpoint: rounds used; pass or fail per test.
- On failure: rule DR-07.
- Gate: none
- Relevant decisions/claims: D-050, D-051; C-055
- Lessons applied: L-20261007T150400Z-threshold-not-checked-against-reference-spread; L-20261004T162213Z-timbre-invariance-measured-on-whole-chain
- Exclusive resources: none

### S-340 Demos and evidence tooling
- Tier: T3
- Profile: software
- Depends on: S-300, S-REF
- Inputs: `demos/*.events`, `tools/make_demos.py`, `tools/listening/make_blind_pairs.py`, `tools/evidence_guard.py`, D-052, D-053
- Actions:
  1. Write `tools/build_evidence.py --gate <gate id> --instrument <name> --seed <n> --out <dir> [--private-out <dir>]`. It (a) renders every `demos/<instrument>-*.events` file to `<dir>/demos/<same name>.wav` at 48 kHz; (b) if `references/index.csv` holds 12 or more notes of the instrument, picks the 12 with the lowest ids, renders the candidate for each with the row's `velocity` and `sets` for the reference's duration (at most 3 s), and runs `tools/listening/make_blind_pairs.py --ref <refs> --cand <cands> --out <pairs dir> --seed <n> --pairs 12 --window start`; the pairs directory is `<dir>/pairs` when every one of the 12 references is redistributable, otherwise `<private-out>/pairs` with only a file `PAIRS-SHA256SUMS` in `<dir>`; for the accordion the 12 references are the TinySOL mf notes at MIDI 48, 52, 55, 59, 62, 65, 69, 72, 76, 79, 83, 86 and the candidate patch is that of D-050; (c) writes `<dir>/MANIFEST.json` (every file with its `derived_from` list), `<dir>/SHA256SUMS`, `<dir>/ATTRIBUTION.md` and `<dir>/METRICS.md` (the pass or fail of each frozen test concerning the instrument, taken from a pytest run); (d) runs `tools/evidence_guard.py` on `<dir>` and exits non-zero if it fails. The answer key written by the pair builder stays base64-encoded.
  2. Add `.github/workflows/gate-evidence.yml`: triggered on push to `impl-**` when the head commit message contains `[gate-evidence `; it parses the gate id and instrument from the message `[gate-evidence <gate id> <instrument> seed=<n>]`, builds the render tool, fetches the redistributable references, runs `tools/build_evidence.py`, and pushes the result as the only content of the orphan branch `evidence/<gate id>` (force-push to that evidence branch only); `permissions: contents: write`; its own concurrency group `gate-evidence-${{ github.ref }}` with `cancel-in-progress: false`; the same action pins as `ci.yml`; no failure-swallowing; a final step that fails if `SHA256SUMS` or `MANIFEST.json` is missing from the pushed tree.
  3. Dry run locally: `python3 tools/build_evidence.py --gate G-TEST --instrument accordion --seed 1 --out $HOME/folk-evidence/G-TEST`.
- Outputs: `tools/build_evidence.py`, `.github/workflows/gate-evidence.yml`
- Evidence produced: none (tooling for S-LISTEN)
- Done when: the dry run exits 0 and its output directory holds `MANIFEST.json`, `SHA256SUMS`, `ATTRIBUTION.md`, `METRICS.md`, at least 20 WAV files under `demos/`, and (TinySOL being available locally) 24 WAV files under `pairs/`; a second dry run with an index row's `redistributable` flag temporarily set to `false` for one of the 12 notes writes no `pairs/` directory into the output (try it with a copy of the index, not the committed file).
- Checkpoint: step done.
- On failure: fix the tool. If TinySOL is not available locally, perform the dry run in CI by pushing a commit with `[gate-evidence G-TEST accordion seed=1]`, verify the branch `evidence/G-TEST`, then delete that branch.
- Gate: none
- Relevant decisions/claims: D-052, D-053
- Lessons applied: group "listening-gate"; knowledge K-20261105T223100Z (pair builder level)
- Exclusive resources: none

### S-REVIEW Code review
- Tier: T2 (a fresh-context agent that wrote none of the code)
- Profile: software
- Depends on: S-320, S-330, S-340
- Inputs: `git diff origin/gen-20261114T004707Z-folk-instruments-vst...HEAD`, the frozen tests (read only), `plan/DECISIONS.md`
- Actions: review the whole diff for: dead code, duplication, hidden mutation, unclear names, needless complexity; code paths no frozen test reaches (name them); unsafe memory or file handling, unchecked input at the boundaries (event files, state text, plugin state, command-line arguments), secrets; real-time violations (allocation, locks, I/O on the audio thread); each dependency compared with its current release and deprecation notices (JUCE 8.0.17-security, Catch2 v3.16.1, the four Python packages, the four actions, pluginval v1.0.4: compare version numbers, and record any that is behind). Classify each finding Critical, High, Medium or Low (the rubric in `HANDOFF.md`). Fix every Critical and High finding before any later step; a fix that corrects the implementer's own mistake is recorded as a lesson. New tests a finding calls for go through a `TEST_CHALLENGE.md` amendment, never straight into the frozen files.
- Outputs: `reviews/CODE_REVIEW.md` (every finding with severity and either the fix commit or an `R-###` entry added to `premortem/RISK_REGISTER.md` with the reason for accepting it)
- Evidence produced: none
- Done when: `reviews/CODE_REVIEW.md` exists, lists the files reviewed, and every finding has a severity and a fix commit or risk ID; no Critical or High finding is open; the `Done when` of `S-300` and of `S-320` hold again on the head commit.
- Checkpoint: counts by severity.
- On failure: an unfixable Critical or High finding halts the plan with `BLOCKED.md`.
- Gate: none
- Relevant decisions/claims: all of Part 2 and 3
- Lessons applied: group "planning-process" (review by a fresh context)
- Exclusive resources: none

### S-ADVERSARIAL Adversarial review
- Tier: T2 or T1 (a fresh-context agent that wrote none of the code)
- Profile: software
- Depends on: S-REVIEW
- Inputs: the built render tool and plugins, `plan/ASSUMPTIONS.md`, `plan/DECISIONS.md`
- Actions: try to break the product. At least: (1) event files: binary data, 1 GB of text, lines without newline, times as `nan`, `inf`, `1e308`, 10 million events, an `end` at 1e9 s; (2) state text and plugin state: truncated, repeated keys, 65 536 and 65 537 bytes, values `-0`, `1e-320`, locale-style decimal commas; (3) engine calls: 10 000 note-ons in one block, every controller number, parameter changes on every sample, `prepare` at 44 100, 96 000 and again 44 100 without `reset`, `process` with `n` of 0 and of a size above the prepared block; (4) sound: every instrument held for 10 minutes (no growth, no drift above 2 cents, no denormal slowdown: time the last minute against the first), extreme parameter corners (breath 1 with vibrato 1 and 16 keys; `pick_position` 0.5; `pair_detune_cents` 8 with `body_coupling` 1; mistuning at the locking boundary), sample rate 88 200; (5) hand-made mutants of the formulas in `strings.cpp` and `tuning.cpp` (change one constant or sign at a time, ten mutants): each must be caught by a frozen test; a survivor is a finding; (6) every `A-###` that is expressed in code (A-005 formats, A-007 controllers, A-009 performance) checked against the build.
- Outputs: `reviews/ADVERSARIAL_REVIEW.md` (each attack, its result, and for each confirmed break either a fix commit, or a `TEST_CHALLENGE.md`-route proposal for a new frozen test, or an accepted `R-###` with severity)
- Evidence produced: none
- Done when: `reviews/ADVERSARIAL_REVIEW.md` exists and covers the six groups; no Critical or High break is open; the `Done when` of `S-300` and `S-320` hold again on the head commit.
- Checkpoint: counts of attacks and confirmed breaks.
- On failure: Critical or High breaks block `S-LISTEN` until fixed.
- Gate: none
- Relevant decisions/claims: D-015, D-090 to D-094; threat model in `plan/ASSUMPTIONS.md`
- Lessons applied: L-20261101T140000Z-intermittent-host-failure-needs-a-stress-test
- Exclusive resources: none

### S-LISTEN Listening validation
- Tier: T3
- Profile: software (audio)
- Depends on: S-ADVERSARIAL
- Inputs: `tools/build_evidence.py`, `.github/workflows/gate-evidence.yml`, `plan/GATES.md` (gates G-L1 to G-L5), `HANDOFF.md` sections "Listening gates" and "Delivering audio"
- Actions: for each instrument in the order harmonica (G-L1), mandolin (G-L2), accordion (G-L3), melodion (G-L4), bouzouki (G-L5); the five gates may be open at the same time:
  1. Push an otherwise empty commit to `impl-<run_id>` with the message `[gate-evidence <gate id> <instrument> seed=<round number>]` (round 1 uses seed 1; every later round a new seed).
  2. Wait for the `gate-evidence` workflow; verify that branch `evidence/<gate id>` exists and holds `SHA256SUMS` and `MANIFEST.json`.
  3. If the instrument's pairs use a private reference, run `tools/build_evidence.py` locally with `--private-out $HOME/folk-private/<gate id>` and check that `PAIRS-SHA256SUMS` matches the CI branch's copy or, if CI built none, add the local one to the gate record.
  4. Write `GATE-<gate id>.md` (round 1) or `GATE-<gate id>-r<N>.md` from the template, with: the evidence branch URL `https://github.com/qualitycoding/folk-instruments/tree/evidence/<gate id>` and zip URL `https://github.com/qualitycoding/folk-instruments/archive/refs/heads/evidence/<gate id>.zip`; the reference set and how many references are redistributable and how many private; the frozen pass condition; the contents of `METRICS.md`; any failed reference test from `S-330`; the questions and allowed responses of `plan/GATES.md`. Deliver private pairs by the delivery rule. PUSH; report the gate in chat.
  5. On a response: record it in the gate file; if pairs were judged, score them with `python3 tools/listening/score_blind.py --key <key file> --answers <letters>` and record seed, score, p-value and the listener's remarks verbatim in `listening/<gate id>-round-<N>.md` (create the directory); apply the branch of `plan/GATES.md` for the response; for `iterate`, rule DR-12.
- Outputs: `GATE-G-L1.md` to `GATE-G-L5.md` (and round files), `listening/*.md`
- Evidence produced: the listening records
- Done when: each of the five gates has a recorded response of `proceed` or `proceed-with-rescope: <text>` (the rescope text copied into `DEVIATIONS.md`), or `stop`; for every gate with pairs, the recorded score meets the pass condition (at most 8 of 12 correct) or the response is `proceed-with-rescope` naming the shortfall; no gate is `OPEN`.
- Checkpoint: per gate: rounds, score, response.
- On failure: a `stop` response for an instrument removes that instrument's plugin target from the default build (keep the code), logged in `DEVIATIONS.md`; the other instruments continue. No response: wait (rule in `HANDOFF.md`, "Waiting").
- Gate: G-L1, G-L2, G-L3, G-L4, G-L5 (each at most 3 rounds)
- Relevant decisions/claims: D-050 to D-053; C-055, C-056
- Lessons applied: group "listening-gate"; L-20261004T162210Z-user-premise-dismissed-instead-of-asked (act on the listener's words)
- Exclusive resources: the `gate-evidence` workflow

### S-INTEGRATE Integration
- Tier: T3
- Profile: software
- Depends on: S-LISTEN
- Inputs: the implementation branch, D-003, D-006
- Actions:
  1. `git fetch origin main`. If `origin/main` has moved since commit `375f6508eb07d8dfe4176ba7b5391ae428471f8d`, merge it into `impl-<run_id>`, then re-run the `Done when` of `S-300` and the manifest check. A conflict in a frozen file is a `TEST_CHALLENGE.md`, never resolved by editing the test.
  2. Create branch `pr-<run_id>` from `impl-<run_id>` and, in one commit on it, remove `research/`, `premortem/`, `.checkpoints/`, `lessons/`, `knowledge/` (D-003). Re-run `sha256sum -c tests/FROZEN_MANIFEST.sha256` there. In `.github/workflows/ci.yml` on that branch, remove the "Schema of lessons and knowledge items" step of job `freeze` (its inputs no longer exist there); log this in `DEVIATIONS.md`.
  3. Push `pr-<run_id>` and open a pull request from it to `main`. The description lists the steps completed, links the gate records, `DEVIATIONS.md`, `reviews/CODE_REVIEW.md` and `reviews/ADVERSARIAL_REVIEW.md`, and links both `impl-<run_id>` and the generation branch. Add the two closing lines required by the session's attribution rules, if any.
  4. Wait for the pull request's checks. Every check must finish green: the jobs of `ci.yml` including `all-green`, and any check `main`'s protection requires (read in `S-000`).
  5. Do not merge. Record the pull request URL in `EXECUTION_LOG.md` and report it.
- Outputs: branch `pr-<run_id>`, the pull request
- Evidence produced: none
- Done when: the pull request exists; every check on its head commit is green (none failing, pending or missing); its URL is in `EXECUTION_LOG.md`.
- Checkpoint: pull request URL, head commit.
- On failure: a red check is fixed on `impl-<run_id>` and brought over by repeating actions 2 to 4 (recreate `pr-<run_id>` from the new head; a force-push to `pr-<run_id>` is allowed because only this plan writes to it). Never force-push `main`, bypass protection, or merge with a check skipped or pending.
- Gate: none (route `pull-request`: the owner merges)
- Relevant decisions/claims: D-003, D-006, D-007
- Lessons applied: groups "git-and-push" and "ci-github-actions"
- Exclusive resources: none

### S-RETRO Retrospective
- Tier: T2 (fresh context), after a T4 agent has collected the inputs into `baseline/retro-digest.md`
- Profile: software
- Depends on: S-INTEGRATE, and every step before it
- Inputs: `EXECUTION_LOG.md`, the commit history of `impl-<run_id>`, `DEVIATIONS.md`, any `BLOCKED.md` and `TEST_CHALLENGE.md`, all `GATE-*.md`, CI run history, `research/PRIOR_KNOWLEDGE.md`, `lessons/`, `knowledge/`, `reviews/`
- Actions: one pass over the records; re-run nothing and change no deliverable. Answer the questions listed in `HANDOFF.md` section "Retrospective", fill its table "Protocol performance" by counting, diff the workflows and manifests of the implementation branch against `plan/ENVIRONMENT.md` and record every unexplained difference as a missing deviation and a lesson, write a lesson for every error or overlooked step not yet recorded and a knowledge item for every new fact, and amend the source register for every source checked after planning.
- Outputs: `RETROSPECTIVE.md` (opening with the implementation results header: code-review findings by severity and how many were fixed or accepted, adversarial breaks confirmed, the statement that no mutation step was planned (D-004), and the statement that the work is on `pr-<run_id>` awaiting the owner's merge); new files under `lessons/` and `knowledge/`
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
  2. On sign-off: clone each target; copy each lesson to `lessons/<primary-tag>/` (its first `tech:` or `domain:` tag with `:` replaced by `-`, else `general`) and each knowledge item to `knowledge/<subject>/` (its first `subject:` tag without the prefix); add the new tags to `TAXONOMY.md`; run `python scripts/build_index.py` and `python scripts/check_knowledge_schema.py` in each store; commit and push each store on the branch the response names (default: the store's default branch; if this session may only push to a designated branch of the stores, push there and say so in the report).
  3. If a push is rejected because the target moved, pull, rebuild the indexes, and retry, up to 3 times per store. If a push still fails, a target is unreachable, or no response arrives: `git bundle create lessons-<run_id>.bundle --all` in the prepared lesson-store clone and `git bundle create knowledge-<run_id>.bundle --all` in the knowledge-store clone, and report the paths.
- Outputs: `GATE-G-003.md`; pushed stores or bundles
- Evidence produced: none
- Done when: the lesson store's index lists every pushed lesson ID and the knowledge store's index lists every pushed knowledge ID including the source register; or the response was `do-not-push`; or the bundles were written and reported.
- Checkpoint: response; store commits or bundle paths.
- On failure: action 3.
- Gate: G-003
- Relevant decisions/claims: A-015
- Lessons applied: group "git-and-push"
- Exclusive resources: none
