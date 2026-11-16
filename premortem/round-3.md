# Pre-mortem, round 3 (fresh context)

Material: the checkout `pm3`. Read: `HANDOFF.md`, `plan/PLAN.md`, `plan/DECISIONS.md` (Parts 1, 2.7, 2.8, 3, 4), `plan/ENVIRONMENT.md`, `plan/GATES.md`, `plan/TRACEABILITY.md`, `plan/ASSUMPTIONS.md`, `plan/ci/ci.yml`, `plan/ci/gate-evidence.yml`, `premortem/RISK_REGISTER.md` (R-001 to R-066) and `premortem/round-2.md`; also `research/claims.json` (the load-bearing claims below the bar, plus C-021, C-043 to C-049), `research/PRIOR_KNOWLEDGE.md` (first 120 lines), `tests/juce/host_test.cpp`, `tests/ci/check_tsan_supp.py`, `tests/ci/tsan_canary.cpp`, `tests/data/tinysol-accordion.sha256`, `tests/py/test_reference.py`, `tests/py/test_common.py` (T-162), `tools/listening/make_blind_pairs.py`, `tools/fetch_references.py`, `core/include/folk/engine.h` and `strings.h`, and `research/spikes/s17-string-body/pluck_ref.py` and `s06-known-answers/ka.py` for the air-damping formula.

Nothing was built and no file in the checkout was changed. I ran read-only Python only: (a) the frozen manifest matches the files (0 mismatches); (b) the TinySOL hash list has 689 entries, all `ordinario`, and the 12 index rows of `plan/ENVIRONMENT.md` section 1 match it; (c) a simulation of the pair builder's answer key under D-053's per-gate seed schedule (finding 6). Severity follows `HANDOFF.md` section 6 (`[All]` and `[software]` lines). Finding numbers (F-n) match `premortem-round-3.json`.

## Incident report (simulated, 16 May 2027)

The pull request merged on 2027-01-05. Every `Done when` had passed. The pull request's checks were green, and all five listening gates were closed.

By May the owner had stopped using the harmonica and the melodion, and no longer trusted any of the listening records. Three things went wrong.

**The harmonica that shipped was not the harmonica that was approved.** G-L1 (harmonica) closed with `proceed` in round 1. The owner was still at G-L3 (accordion), where the remark "the attack is too soft and too clean" led to an `iterate` round. As the iterate procedure requires, the fix was a general mechanism: a breath-noise burst and a faster pressure rise in the shared reed voice (`core/src/reed.cpp`). The frozen suite still passed, so the change was correct by every check. But it changed the harmonica and the melodion as well. The melodion gate was still open and heard the new attack. The harmonica gate, already closed, never did. The owner heard the shipped harmonica for the first time in Live and found the onset chiffy and harsh. The pull request still linked `GATE-G-L1.md` as proof that the harmonica had passed. Nothing in the plan ties a closed gate to the code it judged. Lesson L-20261009T193614Z ("fail when DSP source changes while recorded results carry an older provenance commit") is in the checklist, but no step applies it.

**A red reference job that had nothing to do with references.** The first `gate-evidence` run (G-P1, at `S-210`) found no TinySOL cache. It downloaded the archive without `TinySOL_metadata.csv`, which only `ci.yml` fetches, and on success saved `refs/tinysol` under the key `ci.yml` also uses. No `ci.yml` `reference` job had succeeded yet, so none had saved first. From then on, every `reference` run on `impl-<run_id>` hit that cache, passed both the count and the hash-list checks, and failed T-200 with `TinySOL_metadata.csv is missing`. Zenodo was unreachable from the sandbox, so `S-330` relied on CI (DR-13), and the job could not turn green. The implementer spent two DR-07 calibration rounds on a missing file before reading the fixture message. They then changed the workflow by deviation and deleted the cache entry, an operation the plan never mentions. Every listening gate record named the latest CI `reference` job, as `S-340` requires, and that job was red. The pull request was green only because `pr-<run_id>` has its own cache scope.

**A blind test that told the listener two answers.** In G-L3 the two control pairs were built from `accordion-001` and `accordion-002`, and those notes were also two of the 12 real pairs. `prepare()` is deterministic, so the reference clip in each control pair was byte-identical to the reference side of a real pair. Two pairs of WAV files even carried the same line in `SHA256SUMS`. The owner recognised the repeated clip and answered those two real pairs correctly. The final score of 9 of 12 failed the pass condition. One more `iterate` round followed, and its change to the shared reed voice is the one above.

## Findings by lens

### 1. Technical correctness (DSP, numerics, real-time safety, state, the tests themselves)

- **F-3 (residual on R-051, High, remote). The suppression checker cannot stop a JUCE pattern from hiding a wrapper race.** `check_tsan_supp.py` accepts any line matching `race:juce::Name(::Name)*`, for example `race:juce::A`, `race:juce::AudioBuffer` or `race:juce::MidiBuffer`. ThreadSanitizer suppressions are unanchored substring templates (sanitizer_common `TemplateMatch`: no leading `^` means "anywhere"). They are matched against every frame's function name of both stacks, and the symbolizer returns demangled names with parameter types. The audio-side frame of every T-304 report is `...FolkProcessor::processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&)`, so any accepted line naming `juce::AudioBuffer`, `juce::MidiBuffer`, `juce::Mem` or `juce::A` suppresses every wrapper race, and so does any prefix of a JUCE type that appears in a wrapper signature. The checker's ban on "folk" does not help: the match comes from the JUCE type in the signature. The canary has no JUCE types in its frames, so it cannot detect this. Path: ENVIRONMENT section 5 row "host-tsan ... without reports from inside JUCE" → JUCE-internal report → the implementer writes a class-level line, which T-092 accepts → `host-tsan` green with a real wrapper race. Mitigation: amend `check_tsan_supp.py` and T-092 to require the anchored form `race:^juce::Class::function` (at least two name components, `^` mandatory) and to reject unanchored lines. A frame then matches only if its name begins with `juce::`, so no `folk::` frame can match.
- **F-7 (new, Medium, plausible). `gen_presets.py --check` compares floating-point text that is computed differently on different CPUs.** `S-100` puts the D-011 half-band coefficients from `scipy.signal.firwin` into the committed header, and the CI `core` job on `ubuntu-24.04` regenerates and compares them (the R-057 mitigation). The window and sinc use NumPy's `cos` and `sin`, whose SIMD paths depend on the CPU features at run time. Hosted runners vary in CPU model (K-20261029T030800Z, quoted in D-086). If the generator prints shortest-round-trip or 17-digit values, a last-place difference makes the check fail on some runners and not others, with no code change. The workaround is the implementer's: round the coefficients, or compare numerically with a tolerance. The plan does not say so.
- **F-2 is listed under lens 9 (integration).** Its root cause is technical: shared DSP code changes after gates close.
- **Speculative (F-12). C-027's air-damping term may be a factor of 2 too large.** Starting from Valette's air resistance per unit length, `R = 2 pi eta_a + 2 pi d sqrt(pi eta_a rho_a f)`, I derive `eta_air = (rho_a/rho) (2 sqrt(2) M + 1) / (2 M^2)` with the same `M`. That is half of C-027's formula, which `strings.h`, `ka.py`, `pluck_ref.py` and T-005 all encode. I cannot read the source to settle it, so the finding is speculative. If it holds, low modes decay too fast by up to a factor of 2. DR-07 cannot calibrate that, because it adjusts `eta_E` and the body only. Restates R-004.
- R-054's mitigation looks effective: the strengthened T-302 program case saves at a non-default program, checks the index after restore and re-selection, and checks the three faulty `#program` lines. R-066 is restated: T-304 still never calls `setCurrentProgram`, and only D-094's prose constrains it.

### 2. Dependency and supply-chain drift

- **F-1 (new, High, expected). The `gate-evidence` workflow poisons the shared TinySOL cache with a copy that has no metadata file.** Both workflows cache `refs/tinysol` under `tinysol-6.0-36030a7fe389da86c3419e5ee48e3b7f-accordion`. Only `ci.yml`'s download step fetches `TinySOL_metadata.csv`; `gate-evidence.yml` does not. `actions/cache` saves only when the job succeeds (`post-if: success()`). The `ci.yml` `reference` job cannot succeed before the accordion exists and is calibrated: at `S-003` it fails at the fetch stub by design, and later T-200 fails. The `gate-evidence` job for G-P1 (`S-210`) does succeed. It is therefore expected to write the cache first, without the metadata file. Every later `reference` run on `impl-<run_id>` then passes the 689-file count and the R-053 hash list (which covers only WAVs) and fails T-200 at `tinysol_root()` with `TinySOL_metadata.csv is missing`. The entry is used on every push and so never expires. Consequences:
  - `S-330` cannot finish wherever Zenodo is unreachable locally (DR-13 requires the CI job green).
  - Every listening gate record names a red CI `reference` job (`S-340` action 2).
  - The fix needs a workflow edit or a cache deletion that the plan does not foresee.
  - The pull request itself is unaffected, because `pr-**` and `refs/pull/*` have their own cache scope. That hides the defect from the final check.

  Mitigation: make the download steps identical, so `gate-evidence.yml` also fetches and md5-checks the metadata file. In both workflows, add a step after the cache that requires `TinySOL_metadata.csv` with md5 `a86c9bb1...`. The cache content is then the same whichever workflow writes it, and a hit without the file fails loudly at the cache step, not inside T-200.
- **F-9 (new, Medium, remote). An archive found by `S-REF` is downloaded whole on every CI run, with no size bound.** `fetch_references.py` downloads each row's archive "once into the cache", but the CI cache is `$RUNNER_TEMP/ref-archives`, which is discarded after every job. Only TinySOL is cached. A usable note found inside a multi-GB Zenodo dataset (`S-REF` source (b)) is fetched on every push to `main` and on every pull request for the life of the repository, by both workflows. A hosted runner has about 14 GB free, so a large archive makes `reference` (and `all-green`) red, or slow, with no code change. Restates R-028's maintenance theme, but with a new cause. Mitigation (optional): `S-REF` refuses archives above a size bound, or records the size in `archives.csv` and caches them like TinySOL when redistributable.
- Restated: R-028 (new advisories in the hash-locked Python set, Zenodo and Philharmonia availability, runner image updates, all of which turn `main` red with no code change); R-006 (`macos-15` and `macos-15-intel` retirement).

### 3. Invalid research assumptions

- C-012, C-013, C-014, C-017, C-039 (tables and conventions): restated as R-001. The layout values I could check against common knowledge are consistent (draw bends 1/2/3/1/-/1; C chromatic from C4; trichordo D-A-D with an octave bass course). C-051 (no redistributable single notes for harmonica, melodica or mandolin) is restated as R-037. C-027 is speculative F-12 above.

### 4. Implementer misinterpretation

- **F-10 (new, Low, remote). `S-LISTEN`'s `Done when` does not literally accept `proceed-without-pairs` on a gate that has pairs.** Clause 1 accepts `proceed-without-pairs: <text>`. Clause 2 says that "for every gate with pairs" the score meets the condition or the response is `proceed-with-rescope`. GATES and D-053 call `proceed-without-pairs` a rescope, so the intended reading is recoverable; it is a documentation fix.
- **F-4 (residual on R-055, Medium, plausible). Code changed after `S-REVIEW-DELTA` is reviewed by nobody.** `S-REVIEW-DELTA` says it is repeated "if `S-INTEGRATE` later merges a moved `main`". But `S-INTEGRATE` depends on it, and its own actions (merge, re-run `S-300`, open the pull request) never say to go back. `S-INTEGRATE`'s `On failure` also fixes red checks "on `impl-<run_id>`" and brings them over, and a G-004 `fix: <direction>` produces code after the review. None of these changes passes a fresh-context review, and the pull request presents `DELTA_REVIEW.md` as covering the delivered code. Mitigation (optional): `S-INTEGRATE` action 4 adds "if the head of `impl-<run_id>` differs from the end of the range named in `reviews/DELTA_REVIEW.md`, repeat `S-REVIEW-DELTA` for the difference before opening or refreshing the pull request".

### 5. Integrity

- **F-5 (new, Medium, plausible). The control pairs reuse two of the real pairs' reference clips byte for byte.** D-053 and `S-340` build both controls from "the first two of the 12 references by id", and those references are also two of the 12 real pairs. `prepare()` is deterministic, so the reference side of each control pair is identical to the reference side of a real pair. It even has the same digest in the bundle's `SHA256SUMS`, and in `PAIRS-SHA256SUMS` in the public gate record for private sets. A listener who recognises a repeated clip, which is plausible over 14 one-second pairs of the same instrument, gets two real answers for free. That inflates the score towards failing (more than 8 correct), so it causes spurious `iterate` rounds rather than false passes. Those rounds are the very changes behind F-2. Mitigation (optional): build the controls from the reference's middle window, or from a 13th and 14th reference not used in the real pairs.
- **F-6 (new, Medium, remote). Under one planned seed a listener who answers every pair 'A' gets a valid, passing round.** The key depends only on the seed and the pair count. I simulated the seed schedule with the stems the plan defines. Seed 411 (G-L4 round 1, attempt 1) gives `AABBAAAABAAAAB`: 10 'A', both controls 'A'. Fourteen 'A' answers therefore get both controls right and are not void (the key has 10 'A'), and score 8 of 12, which passes. Conditions: the melodion has 12 or more references (C-051 found none), and attempt 0 was void. The schedule is public, so every key and control position can be computed before any audio exists (restates R-034). Mitigation (optional): make the side-bias rule "10 or more of one letter" unconditional for any answer that differs from the key, or derive seeds from a secret drawn at the gate.
- **F-8 (residual on R-052 and R-022, Medium, plausible). The sine controls test only that the files were played.** A pure sine against a recording is caught by anyone who plays the files at all. A listener who plays every pair casually, spots the two sines, and guesses the other 12 passes with probability 0.93, whatever they could have heard with care. That is R-022's original failure, now behind a control that cannot fail an attentive listener but also cannot detect an inattentive one. The plan already states that the score is necessary, not sufficient. Restating that in the gate question (play each pair through, on headphones) is the proportionate response.

### 6. Past lessons (PRIOR_KNOWLEDGE.md)

- Not applied: L-20261009T193614Z (fail when DSP source changes while recorded results carry an older provenance commit) and L-20261009T192606Z (regenerate every result that cites a changed model). Both bear on F-2. L-20261106T010000Z (each blind clip checked against its source) is applied by `S-340`'s correlation check, but it checks mapping, not uniqueness (F-5).

### 7. Untrusted content

- No new path. R-024 (archive extraction) and Rule 16 handling in `S-REF` look effective. Downloaded audio is parsed by libsndfile inside `soundfile` on CI runners only.

### 8. Security

- Restated: R-023 (fork pull requests and private references; the owner's Actions setting). The `publish` job pushes the downloaded artifact with `contents: write`. A crafted bundle cannot add workflow files, because `GITHUB_TOKEN` lacks the `workflows` permission, and `GATE` is constrained by the marker regex. No new finding.

### 9. Integration

- **F-2 (new, High, plausible). A change to shared code after a gate closes ships audio the owner never heard, and nothing re-opens the gate.**
  - The harmonica, accordion and melodion share `reed.cpp`, the reed curves and the offset table. The mandolin and bouzouki share `pluck.cpp`.
  - The iterate procedure requires general mechanisms, not per-note constants, so iterate changes land in shared code by design.
  - The five gates may be open at once and close in any order.
  - After a gate closes, any `iterate` change at another gate of the family, any G-L1 question-4 fix, any `S-REVIEW-DELTA` fix and any `S-INTEGRATE` fix alters the closed instrument's sound. DR-12 re-runs only the frozen suite and `S-300`'s `Done when`.
  - No rule ties a gate record to the commit it judged. The pull request presents every gate as passed for the head commit.

  For three instruments with no pairs, the gate is the only check of realism. A verification thus reports a pass for audio it never heard; I grade it High, not Critical, because the gate did run on a closely related build. Conditions: an `iterate` response at a later gate of the same family, or any later code fix to shared DSP. Both are expected uses (R-055).

  Mitigation: each gate record names the commit of the audio it judged. Before `S-REVIEW-DELTA` completes, run `git diff --quiet <gate commit> HEAD -- core/ presets/ tools/folk-render/`. If it is non-empty for a closed gate whose instrument uses the changed files, open a confirmation round of that gate: new demos with a new seed, the same questions, not counted against the round limit. This applies the two lessons above and makes "approved" mean "approved as shipped".
- The plan ends on a pull request that the owner merges (D-006, A-002), with the later records on `impl-<run_id>` (D-003). That is a recorded decision, so no finding.

### 10. Scale and performance

- Restated: R-007, R-041 (96 kHz cost), R-047. No new path.

### 11. Operational realities

- F-1 (above) is also operational: an immutable cache entry written by the wrong workflow is never evicted while it is used. Restated: R-028, R-043 and R-061 (artifacts and installation).

### 12. CI platform coverage and runner-label drift

- The host-tsan canary (R-051) proves only that ThreadSanitizer works on the runner. Nothing checks that `build-tsan`'s host programs are instrumented: a project `CMakeLists.txt` that overwrites `CMAKE_CXX_FLAGS` would leave them uninstrumented, and T-304 would pass. I found no concrete reason for the implementer to do that, so this stays speculative (F-13). Restated: R-006.

### 13. Licensing

- Restated: R-016 (T-201 statistic in public logs), R-045 and R-063 (notices), R-023. No new path.

## Findings table

| F | Description | Class | Severity | Likelihood (conditions) | Failure path | Mitigation |
|---|---|---|---|---|---|---|
| 1 | `gate-evidence` saves the shared TinySOL cache without `TinySOL_metadata.csv`; every later `reference` run on the implementation branch fails T-200 | new | High | expected (the G-P1 evidence job is the first successful job with that key) | S-210 marker run → cache saved on success → ci.yml hit passes count and hash list → T-200 fixture asserts the file is missing → S-330 under DR-13 cannot go green; gate records name a red job | identical download steps; post-cache metadata md5 check in both workflows |
| 2 | Changes to shared DSP code after a gate closes alter instruments whose gates are closed; the shipped audio was never heard | new | High | plausible (an iterate at a later gate of the family, or any later DSP fix) | DR-12 / G-L1 q4 / S-REVIEW-DELTA / S-INTEGRATE fix in reed.cpp or pluck.cpp → frozen suite passes → closed gate stands → pull request claims all gates passed | gate records name their commit; confirmation round when `git diff` of `core/ presets/ tools/folk-render/` since that commit is non-empty |
| 3 | The TSan suppression checker accepts unanchored class-level patterns that match wrapper frames through JUCE parameter types | residual R-051 | High | remote (a JUCE-internal report needs suppressing, and a wrapper race exists) | `race:juce::AudioBuffer` (accepted by T-092) matches `FolkProcessor::processBlock(juce::AudioBuffer<float>&, ...)` → T-304 under TSan green | require `race:^juce::Class::function` in the checker and T-092 |
| 4 | Code changed after S-REVIEW-DELTA (S-INTEGRATE fixes, G-004 fixes, a main merge) is not reviewed; S-INTEGRATE never sends you back | residual R-055 | Medium | plausible | S-INTEGRATE On failure → fix on impl → PR → DELTA_REVIEW range ends earlier | S-INTEGRATE checks the head against the reviewed range |
| 5 | Control pairs reuse two real pairs' reference clips byte-identically | new | Medium | plausible | S-340 builds controls from accordion-001/002 → identical clips and digests → two free answers → spurious fails and iterates | controls from other notes or another window |
| 6 | Seed 411 makes an all-'A' answer valid and passing; all keys are computable from the public seed schedule | new | Medium | remote (melodion has 12 references and attempt 0 was void) | D-053 seed → key with 10 'A' and both controls 'A' → 14 'A' → 8 of 12 → pass | unconditional side-bias rule or secret seeds |
| 7 | `gen_presets.py --check` exact text of SIMD-dependent firwin coefficients | new | Medium | plausible (sandbox and runner CPUs take different SIMD paths, full-precision print) | CI core job ubuntu step fails or flakes with no code change | round coefficients or compare with a tolerance |
| 8 | Sine controls cannot detect a casual listener | residual R-052/R-022 | Medium | plausible | listener spots the sines, guesses the rest → pass with p 0.93 | restate the listening instruction; score is necessary, not sufficient |
| 9 | A large reference archive is downloaded on every CI run with no size bound | new | Medium | remote (S-REF indexes a note inside a large Zenodo archive) | fetch_references → $RUNNER_TEMP each run → disk or time limit → reference red on main | size bound or cache |
| 10 | S-LISTEN Done when does not literally accept proceed-without-pairs on a gate with pairs | new | Low | remote | two void attempts → owner answers proceed-without-pairs → clause 2 unmet | reword clause 2 |
| 11 | Restatements: R-001, R-004, R-006, R-016, R-023, R-028, R-034, R-037, R-066 | restated | n/a | n/a | n/a | n/a |
| 12 | C-027 air-damping term possibly 2 times too large | speculative (restates R-004) | Medium | not established | none shown | read the source formula |
| 13 | host-tsan does not prove the host programs are instrumented | speculative | High | not established | none shown | check that a TSan symbol is present in one host binary |
