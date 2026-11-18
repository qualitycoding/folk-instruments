# Pre-mortem, round 4 (fresh context)

Material: the checkout `pm4`. I read `HANDOFF.md` (sections 6 and 9), `plan/PLAN.md` (S-100, S-REF to S-INTEGRATE), `plan/DECISIONS.md` (D-011, D-053, D-084), `plan/ENVIRONMENT.md` (sections 1 and 5), `plan/GATES.md`, `plan/TRACEABILITY.md`, `plan/ci/ci.yml`, `plan/ci/gate-evidence.yml`, `premortem/RISK_REGISTER.md` (R-001 to R-077), `premortem/round-3.md`, `research/PRIOR_KNOWLEDGE.md` (first 120 lines), `tests/ci/check_tsan_supp.py`, `tests/ci/tsan_canary.cpp`, `tests/py/test_tsan_supp_check.py`, `tests/py/test_reference.py`, `tests/py/test_fetch_references.py`, `tests/data/tinysol-accordion.sha256`, `tools/listening/make_blind_pairs.py` and `tools/fetch_references.py`.

No file in the checkout was changed and nothing was built. I ran read-only checks only:
- (a) `sha256sum -c tests/FROZEN_MANIFEST.sha256`: 34 entries, all match.
- (b) The two control notes (A3 and E4 mf, `N-N` takes) are in the frozen 689-line TinySOL hash list, with the hashes given in ENVIRONMENT section 1.
- (c) A simulation of the pair builder's key for the accordion's 14 stems. Seed 1 (the `S-340` dry run) gives 6 'A' and is balanced, as do 3100, 3101, 3102, 3200, 3300 and 3400. Seeds 2 and 3 would be refused as unbalanced, which is harmless.
- (d) I re-read the round-3 anchor verification files left in the scratchpad (`a.supp` = `race:^shared$`, `b.supp` = `race:^share$`, `canary.log`).

Severity follows `HANDOFF.md` section 6 (`[All]` and `[software]` lines). Finding numbers (F-n) match `premortem-round-4.json`.

## Incident report (simulated, 18 May 2027)

The pull request merged in January. Every `Done when` passed and all five listening gates showed `proceed` or `confirm`. By May the owner had withdrawn the accordion and stopped trusting the plan's verification. Three things went wrong.

**1. The race detector was switched off in all but name.**
- At `S-320`, `host-tsan` reported a data race whose frames all lay inside JUCE (a `juce::AudioProcessor` member touched by the message thread and the audio thread). ENVIRONMENT section 5 permits a suppression for that.
- The implementer wrote `race:^juce::AudioProcessor::setPlayConfigDetails$`, the only form `check_tsan_supp.py` accepts, and T-092 passed. The job stayed red.
- ThreadSanitizer matches a suppression against the demangled frame name, and that name always ends in a parameter list, for example `juce::AudioProcessor::setPlayConfigDetails(int, int, double, int)`. A pattern ending in `$` right after the function name therefore never matches a function frame.
- Round 3's check that "an exact pattern suppresses" used `race:^shared$`. That pattern matched the *global variable* named in the report's `Location is global 'shared'` line, not a function frame.
- After two days blocked, the implementer logged a deviation that builds the JUCE module sources without `-fsanitize=thread` (a `set_source_files_properties` in `CMakeLists.txt`). The report disappeared, and the R-077 check `nm | grep __tsan_init` still passed, because the wrapper's own translation units were instrumented. From then on, a race between wrapper code and JUCE-owned state could not be seen. Three months after the merge, a user's DAW crashed when it automated the program parameter during playback.

**2. A regression approved as "confirm".**
- The harmonica's round-2 `iterate` changed `core/src/reed.cpp`, which reopened G-L3 (accordion) for a confirmation round under D-053.
- The confirmation pairs scored 10 of 12: the listener now told the real accordion from the model reliably. But a confirmation round allows only `confirm` or `iterate`, and no rule applies the frozen pass condition to it.
- The owner, tired after the fourth confirmation round in a week, answered `confirm`. The implementer read `S-LISTEN`'s `Done when` clause "(or each has `confirm`)" as satisfied. The record's last valid scored attempt was taken to be the round-1 attempt (8 of 12), so the "last valid attempt" clause passed too.
- Those confirmation rounds came from a ping-pong. Each `iterate` given in a confirmation round of one reed instrument changed shared code, which reopened the other two, and confirmation rounds have no limit.

**3. The mandolin controls gave answers away.**
- `S-REF` stops searching at 12 usable notes per instrument. So the Philharmonia mandolin set had exactly 12, and D-053's fallback built both controls from `mandolin-001` and `mandolin-002`. Those are the same clips as two real pairs, which is R-071, unfixed for every instrument but the accordion.
- The gate passed at 8 of 12 with two free answers in it.

## Findings by lens

### 1. Technical correctness (DSP, numerics, real-time safety, tests)

- **F-1 (new; introduced by R-069's mitigation; High, plausible). Every suppression the anchored checker accepts is inert for function frames.**
  - What the checker accepts: `check_tsan_supp.py` and T-092 accept only `race:^juce::<Class>::<function>$`.
  - How TSan matches:
    - sanitizer_common's `TemplateMatch` treats `$` as "end of string".
    - TSan's `IsSuppressed` matches the template against each frame's `info.function`, `info.file` and `info.module`.
    - `info.function` is the demangled name with its parameter list. The GCC 13 / libtsan canary log shows `std::thread::_State_impl<...>::_M_run()`.
  - So `^juce::X::f$` can match only a name that ends exactly at `f`. No C++ function frame does; only global or static variables in a `Location is global` line do.
  - Round 3's verification (scratchpad `a.supp` = `race:^shared$`, `b.supp` = `race:^share$`) exercised exactly that global-variable path, so it proved nothing about function frames. Lesson L-20261029T000000Z: confirm that a gate can act on the input it is meant for.
  - Two further limits make it worse:
    - The regex also forbids template arguments, so `juce::AudioBuffer<float>::...` can never be named.
    - It forbids `deadlock:`, so a JUCE-internal lock-order report cannot be suppressed at all.
  - Failure path: `S-003`/`S-320` `host-tsan` shows a JUCE-internal report → an anchored line that T-092 accepts → the job is still red → `S-320`'s `Done when` cannot be met → the implementer is blocked or forced to guess.
  - The likely workaround is a deviation that compiles JUCE sources without TSan. It passes R-077's `nm` check (which proves only that some translation unit is instrumented), and it hides wrapper-against-JUCE races. That is the original R-051 failure reached by another route.
  - Rubric line: implementer blocked, and a frozen tool test (T-092) is invalid. Conditions: T-304 under TSan produces any JUCE-internal report, which ENVIRONMENT section 5 explicitly anticipates.
  - Mitigation, through a `TEST_CHALLENGE` amendment of the frozen checker:
    - Accept `race:^juce::<Name>(<literal template args>)?(::<Name>)+(` (an open parenthesis, no `$`, no `*`). That pins the start of the name to `juce::`, so a `FolkProcessor::` or `folk::` frame cannot match.
    - Accept `deadlock:` lines of the same form.
    - Add a second canary to `host-tsan` whose race lies in a named function `canary_ns::Writer::write(int)`. Under `race:^canary_ns::Writer::write(` it must exit 0; under `race:^canary_ns::Writer::writ$` it must exit 66. This proves the accepted syntax on a function frame.
    - Forbid any deviation that removes `-fsanitize=thread` from a translation unit (ENVIRONMENT section 5).
  - What it adds: a positive control on the code path that the suppressions actually use.
- **F-5 (new, Medium, remote). R-077's check can turn `host-tsan` red with no defect.**
  - The workflow sets `shell: bash`, so each step runs with `-eo pipefail`. In `nm "$b" | grep -q __tsan_init`, grep exits at the first match.
  - If `nm` is still writing at that moment, it dies of SIGPIPE (status 141), and pipefail fails the step.
  - With GCC the symbol tail after `__tsan_init` is short, so this is rare; with a toolchain that links the TSan runtime statically (clang) it is likely.
  - Fix: write `nm` output to a file, then `grep -q` the file.
- Checked and effective: `gen_presets --check` with relative 1e-12. The near-zero half-band taps come from `sin(k*pi)` and agree to a few ULP relative across SIMD paths, so the tolerance holds. The separate TinySOL cache key plus the md5 check of `TinySOL_metadata.csv` in `ci.yml` closes R-067.

### 2. Dependency and supply-chain drift

- Restated (R-028): `actions/cache` saves only on success. So until `S-330` makes `reference` green, and on every `pr-**` and pull-request run, the 1 GB TinySOL archive is downloaded from Zenodo on every push. Zenodo throttling turns the job red with no code change.
- Restated: R-006 (runner labels).

### 3. Invalid research assumptions

- Restated: R-001 (C-012, C-013, C-014, C-017, C-039 tables), R-004 (C-027 loss model; round-3 F-12 is still unresolved), R-037 (C-051, no redistributable references for harmonica, melodica and mandolin). No new path.

### 4. Implementer misinterpretation

- **F-2 (new; from R-068's mitigation; High, plausible). A confirmation round has no pass condition, and `S-LISTEN`'s `Done when` contradicts itself on it.**
  - D-053 and GATES allow only `confirm` or `iterate` in a confirmation round. Neither says whether the frozen "at most 8 of 12" applies to a confirmation round with pairs.
  - `S-LISTEN`'s `Done when` accepts "(or each has `confirm`)", and also requires that "the recorded score of its last valid attempt meets the pass condition".
  - With a confirmation score of 9 or more and `confirm`, the implementer must guess whether the confirmation attempt is the "last valid attempt". Either guess is bad: it reopens a gate the owner confirmed, or it ships an instrument whose blind score now fails the frozen condition.
  - The seed and record name are also undefined: is the "next seed" the next attempt `k` of the last round, or the next round `N`?
  - Conditions: a confirmation round on a gate with pairs (G-L3 after any later reed change; that is expected when the harmonica or melodion iterate after G-L3 closes), and a score of 9 or more.
  - Mitigation: in a confirmation round with pairs, the frozen pass condition applies. `confirm` is valid only with a score of at most 8, otherwise the `proceed` branch's question is asked (`iterate`, `proceed-with-rescope` or `stop`). The seed is the next attempt `k` of the gate's last round, and the record is `listening/<gate>-round-<N>-confirm-<k>.md`. `S-LISTEN`'s `Done when` names the confirmation attempt as the last valid attempt.
  - What it adds: the frozen blind check covers the code that ships.
- **F-7 (new, Low, remote). `S-REVIEW-DELTA`'s output says one thing and its `Done when` another.** On a repeat the review covers "from the head this step last reviewed", but the `Done when` requires `DELTA_REVIEW.md` to name the range from the `S-ADVERSARIAL` commit to the head. If the file is overwritten with the increment, the clause fails literally, and the pull request lists a partial range. Fix: append one section per pass; the `Done when` reads the union.
- HANDOFF section 9 (the listening procedure the implementer follows) never mentions confirmation rounds; only D-053, GATES and PLAN do. This is documentation only, so it is folded into F-2.

### 5. Integrity

- **F-4 (residual on R-071, Medium, expected for any non-accordion instrument that reaches 12 references). The 13th and 14th control notes exist only for the accordion.** `S-REF` action 3 stops "for an instrument as soon as 12 usable notes are indexed", so no other instrument can have 14. D-053's fallback (the first two by id) then repeats two real-pair clips byte for byte, and the gate record merely says so. For G-L2 (Philharmonia mandolin, the most likely second set with pairs), R-071's failure is unchanged. Mitigation (optional; Medium): stop at 14 where the source has more, and keep 12 as the threshold of D-051.
- **F-8 (new, Low, plausible). Each run force-pushes `evidence/<gate id>`.** The bundle a closed gate judged is therefore replaced by later rounds and confirmation rounds, and earlier gate records point to audio that no longer exists there. Only `PAIRS-SHA256SUMS` (private sets) is copied into a record. Fix: copy `SHA256SUMS` into each gate record. F-3's mitigation needs this.
- R-072 is closed: with unbalanced keys refused, every uniform answer of 10 or more is void, and a perfect answer never is. R-074 (casual listener) is restated.

### 6. Past lessons

- L-20261029T000000Z (confirm that each gate can fail, and act, on its real input) was not applied to the R-069 anchor verification; see F-1.
- L-20261009T193614Z is now applied by D-053, but its trigger is a path list, not provenance of the output; see F-3.

### 7. Untrusted content

- No new path. Downloaded audio is still parsed only on CI and in the implementer's sandbox. The 2 GiB limit is counted while streaming.

### 8. Security

- Restated: R-023. No new finding.

### 9. Integration

- **F-3 (new; from R-068's mitigation; Medium, plausible). The confirmation trigger is a path list and has no bound.**
  - Over-trigger: any edit under `core/` or `presets/` reopens every gate whose model it "reaches", including a comment, a refactor, or an `S-REVIEW-DELTA` hardening of the event parser in the shared engine frame (all five gates).
  - Loop: an `iterate` given in a confirmation round lands in shared code by design, which reopens the sibling gates. None of this counts towards the round limit, so nothing ends it but the owner's fatigue, and fatigue produces rubber-stamp `confirm`s (feeding F-2). The mandolin's private pairs need a manual hand-over every time.
  - Under-trigger: a change outside the listed paths that alters rendering (compile flags in the top-level `CMakeLists.txt`, for example a fast-math or flush-to-zero fix from `S-ADVERSARIAL` group 4) reopens nothing.
  - Mitigation (optional; Medium): base the trigger on output. Rebuild the gate's demos at HEAD with its recorded seed and compare them against the gate's `SHA256SUMS` (rendering is deterministic, T-163). Only a mismatch reopens the gate. An `iterate` in a confirmation round counts towards the round limit.
- **F-6 (residual on R-068, Medium, remote). D-053 applies the confirmation rule only to gates answered `proceed` or `proceed-with-rescope`.** A gate closed with `proceed-without-pairs` (after two void attempts) is never reconfirmed, although D-053 calls it a rescope. That path leads straight back to R-068's failure. Fix: name all closing responses.

### 10. Scale and performance

- Restated: R-007, R-041, R-047. No new path.

### 11. Operational realities

- F-3 (owner fatigue from unbounded confirmation rounds) and F-8 (bundles overwritten). Restated: R-028, R-043, R-061.

### 12. CI platform coverage and runner-label drift

- F-1 and F-5. R-077's `nm` check proves only that one translation unit is instrumented, not that every source is (part of F-1).
- **F-9 (new, Low, remote).** No frozen test covers the 2 GiB archive limit: T-211 has no oversize case. The R-075 mitigation is therefore an unverified promise. Fix: a T-211 case with a mocked stream above the bound.
- Restated: R-006.

### 13. Licensing

- Restated: R-016, R-045, R-063, R-023. The two control notes are TinySOL CC BY 4.0, covered by the existing attribution. No new path.

## Findings table

| F | Description | Class | Severity | Likelihood (conditions) | Failure path | Mitigation |
|---|---|---|---|---|---|---|
| 1 | Anchored `...::function$` suppressions never match C++ function frames (the demangled names carry parameter lists); round 3 verified on a global-variable name only | new (from R-069's fix) | High | plausible (any JUCE-internal TSan report in T-304) | S-320 host-tsan red → accepted line inert → blocked; the workaround of un-instrumenting JUCE sources passes R-077's nm check and hides races | accept `race:^juce::...::f(` and `deadlock:`; function-frame canary pair; forbid un-instrumenting |
| 2 | Confirmation rounds have no pass condition; S-LISTEN Done when contradicts itself | new (from R-068's fix) | High | plausible (a confirmation round with pairs scoring 9 or more) | `confirm` with 10/12 → "last valid attempt" read as round 1 → regressed instrument ships, or the implementer guesses | pass condition applies; `confirm` only at 8 or fewer; define seed and record |
| 3 | Path-based confirmation trigger: over-triggers, has no bound, misses build-flag changes | new (from R-068's fix) | Medium | plausible | confirmation `iterate` in reed.cpp → siblings reopen → loop → fatigued `confirm` | trigger on demo hash mismatch; count confirmation `iterate`s towards the round limit |
| 4 | 13th and 14th controls exist only for the accordion; S-REF stops at 12 | residual R-071 | Medium | expected (any other instrument with pairs) | S-REF 12 notes → fallback controls repeat real clips | stop the search at 14 |
| 5 | `nm \| grep -q` under pipefail can SIGPIPE | new | Medium | remote (long symbol tail after `__tsan_init`) | host-tsan red, no defect | nm to a file, then grep |
| 6 | `proceed-without-pairs` gates are excluded from confirmation | residual R-068 | Medium | remote | two void attempts → proceed-without-pairs → later shared change → never reheard | list all closing responses |
| 7 | DELTA_REVIEW repeat range against Done when wording | new | Low | remote | overwritten file names a partial range | append per pass |
| 8 | Evidence branch force-pushed; judged bundles lost | new | Low | plausible | later round overwrites → records point to other audio | copy SHA256SUMS into records |
| 9 | 2 GiB archive limit untested | new | Low | remote | limit unimplemented, nothing fails | T-211 oversize case |
| 10 | Restatements: R-001, R-004, R-006, R-007, R-016, R-023, R-028, R-034, R-037, R-041, R-043, R-045, R-047, R-061, R-063, R-074 | restated | n/a | n/a | n/a | n/a |
