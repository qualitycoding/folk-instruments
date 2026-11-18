# Pre-mortem, round 5 (fresh context, last permitted round)

Material: the checkout `pm5`. I read `HANDOFF.md`, `plan/PLAN.md` (S-003, S-310, S-320 to S-INTEGRATE), `plan/DECISIONS.md` (D-050 to D-053), `plan/ENVIRONMENT.md`, `plan/GATES.md`, `plan/TRACEABILITY.md` (T-092, T-304, the freeze state), `plan/ci/ci.yml`, `plan/ci/gate-evidence.yml`, `premortem/RISK_REGISTER.md` (R-001 to R-086), `premortem/round-4.md`, the below-bar claims in `research/claims.json`, `tests/ci/check_tsan_supp.py`, `tests/ci/tsan_canary.cpp`, `tests/ci/tsan_canary_named.cpp`, `tests/py/test_tsan_supp_check.py`, `tests/juce/host_test.cpp` (T-302, T-304), `tests/py/test_reference.py` (T-201) and `tests/py/test_evidence_guard.py`.

I changed no file in the checkout, built nothing and used neither git nor the web. Read-only checks:
- (a) `sha256sum -c tests/FROZEN_MANIFEST.sha256`: 35 entries, all `OK` (both canaries, the checker and T-092 included).
- (b) The frozen checker's regular expression, run on sample lines. It accepts `race:^juce::AudioProcessorParameter::setValueNotifyingHost(`, `race:^juce::AudioProcessorParameter::sendValueChangedMessageToListeners(`, `race:^juce::Thread::threadEntryPoint(` and `deadlock:^juce::CriticalSection::enter(`. It refuses `race_top:...`, `juce::(anonymous namespace)::...` and any template argument.
- (c) The seed formulas of D-053, enumerated. A confirmation seed first equals a normal-round seed of the next gate at confirmation `j = 20`.

Severity follows `HANDOFF.md` section 6 (the `[All]` and `[software]` lines). Finding numbers (F-n) match `premortem-round-5.json`.

## Incident report (simulated, 20 June 2027)

The pull request merged in December 2026. Every `Done when` passed, `host-tsan` was green and all five listening gates were closed. By June the owner had pulled the harmonica and the mandolin and filed a crash report against the accordion. Three failures combined.

**1. A suppression in the accepted form hid a wrapper race.**
- In `S-320`, `host-tsan` showed a report whose top frames lay in JUCE's parameter-notification code. The test thread's stack ran through `juce::AudioProcessorParameter::setValueNotifyingHost(float)`.
- The implementer added `race:^juce::AudioProcessorParameter::setValueNotifyingHost(`. `check_tsan_supp.py` accepted the line, and the named canary had shown that this form works. The job turned green.
- ThreadSanitizer applies a `race:` line to every frame of both access stacks, not only the top frame.
- The wrapper's parameter listener, `FolkProcessor::parameterValueChanged(int, float)`, writes a non-atomic engine field that `processBlock` reads. That listener is always called beneath `setValueNotifyingHost`. Its race was therefore suppressed from then on, and so was every later race on the same path, including the state-restore path (S-310 action 2 updates the JUCE parameters through the same call).
- After release, hosts that automate parameters during playback produced clicks, and an accordion register sweep crashed one DAW.

**2. A harmonica "confirm" despite a wrong demo.**
- The accordion's round 2 `iterate` changed `core/src/reed.cpp`, so G-L1 (harmonica, no pairs) was reopened for confirmation.
- The owner answered `wrong: -08-bend` and `confirm`.
- `confirm` is "valid only if the pass condition holds where pairs exist". G-L1 has no pairs, so nothing checked the `wrong:` line. `S-LISTEN`'s `Done when` ("or each has `confirm`") passed.
- The harmonica shipped with the bend the owner had called wrong.

**3. The mandolin gate could not be closed honestly.**
- G-L2 had been closed with `proceed-with-rescope` at 10 of 12.
- A bouzouki `iterate` changed `pluck.cpp`. The confirmation scored 10 of 12 again, so `confirm` was invalid.
- The owner was "asked as for `proceed`" and repeated the rescope. No confirmation round allows that response, and `S-LISTEN`'s `Done when` accepts only `confirm` for a gate that needs confirmation.
- The confirmation had not moved the gate's evidence commit, so every later check reopened the gate.
- Before the pull request, the implementer recorded the rescope as a `confirm`.

## Findings by lens

### 1. Technical correctness

- **F-1 (residual of R-051 and R-078; High; plausible). An accepted suppression silences wrapper races that run through the named JUCE function.**
  - How TSan applies a line:
    - In `IsSuppressed`, a `race:` (or `deadlock:`) template is tried against every frame of every access stack.
    - For a heap or global location, it is also tried against the allocation stack or the global's name.
    - Only `race_top:` restricts the match to the top frame (`#0`).
  - What the anchor does and does not do:
    - `^juce::` pins where the *frame name* starts. It does not limit which *reports* are suppressed.
    - In T-304, JUCE frames sit above wrapper code on both state and parameter paths:
      - test → `juce::AudioProcessorParameter::setValueNotifyingHost(float)` → `sendValueChangedMessageToListeners(float)` → the wrapper's listener;
      - `FolkProcessor::setStateInformation` → JUCE parameter setters (S-310 action 2: "update the JUCE parameters at once").
    - Every line that T-092 accepts and that names one of these JUCE functions hides every race below it.
  - T-092's own passing example, `deadlock:^juce::CriticalSection::enter(`, suppresses every lock-order report that involves any `juce::CriticalSection`, wrapper-owned ones included.
  - What the canaries prove: the anchor syntax works on a function frame. Neither canary tests scope, so neither can fail on over-suppression.
  - Failure path: JUCE-internal report on the parameter path (which ENVIRONMENT section 5 anticipates) → an accepted line naming a JUCE function on that path → `host-tsan` green → a wrapper race below that frame never appears again.
  - Mitigation (through `TEST_CHALLENGE.md`):
    - Accept only `race_top:^juce::<Name>(::<Name>)+(`. Refuse `race:` lines.
    - Allow no `deadlock:` line without an owner's answer at G-004.
    - Add a third frozen canary, `tsan_canary_scope.cpp`: `juce::CanaryBox::call(void (*)(int), int)` calls a racing `canary_ns::touch(int)`. Under the accepted line `race_top:^juce::CanaryBox::call(` it must still exit 66. Under a `race:` line it would exit 0.
    - What it adds: a negative control on the scope of a suppression, which is the property R-051 was about.
- **F-2 (new; Medium; plausible). ENVIRONMENT section 5's suppression criterion cannot be met as written.**
  - The rule: suppress only "a report whose every frame lies in JUCE module code"; "a report with a frame in `plugins/` or `core/` is a defect".
  - Why no T-304 report qualifies:
    - every stack contains frames from `tests/juce/host_test.cpp` (the Catch2 test body or the audio lambda) and from libstdc++ (`std::thread::_State_impl<...>::_M_run()`);
    - every audio-thread stack contains `FolkProcessor::processBlock` from `plugins/`.
  - The implementer must guess which frames "don't count". A loose reading has no bound, which feeds F-1. The strict reading makes every JUCE-internal report an unfixable "defect" (blocked).
  - Failure path: S-320, any JUCE-internal report → guess.
  - Fix: state the rule on the top frames, matching F-1. Both accesses' `#0` frames lie in JUCE module code, and no frame above the first test-harness frame lies in `plugins/` or `core/`.

### 2. Dependency and supply-chain drift

- Restated: R-028 (TinySOL downloads on every cache miss; pip-audit advisories), R-006 (runner labels), R-009 (C-047 lists `windows-2025` with Visual Studio 2026; JUCE 8.0.17 under that toolset is unverified).
- Checked and effective: every action is pinned by commit, Python is installed from the hash-locked lock file, and JUCE and Catch2 are pinned by commit.

### 3. Invalid research assumptions

- Restated: R-001 (C-012, C-013, C-014, C-017, C-039), R-004 (C-027), R-037 (C-051; Freesound still not searched). The 14-note search does not change C-051's finding for the harmonica and the melodica. No new path.

### 4. Implementer misinterpretation

- **F-5 (new; introduced by R-079's mitigation; High; plausible). A confirmation round can close only with `confirm`, and it does not re-baseline.**
  - (a) A gate with pairs closed with `proceed-with-rescope` because it scored above 8 will usually score above 8 again in confirmation, since it is the same distinguishable model. In that case:
    - `confirm` is invalid;
    - D-053 says to ask "as for `proceed`", which offers `iterate`, `proceed-with-rescope` or `stop`;
    - GATES' allowed responses for a confirmation round exclude `proceed-with-rescope`;
    - `S-LISTEN`'s `Done when` lets a gate needing confirmation pass only with `confirm`;
    - two void attempts (`proceed-without-pairs`) and `stop` hit the same wall.
  - (b) The trigger compares against "the commit its evidence was built from", and nothing says a confirmation replaces it. Every later check (before `S-REVIEW-DELTA`, before the pull request, after each `S-INTEGRATE` fix) reopens a gate that was already confirmed on identical audio. It reaches the two-confirmation cap without any change.
  - Failure path: G-L2 rescope at 10/12 → bouzouki `iterate` in `pluck.cpp` → G-L2 confirmation at 10/12 → the owner repeats the rescope (not allowed) → the implementer halts, forces an unwanted `iterate` round (counted towards the limit), or records something else as `confirm`.
  - Mitigation:
    - A confirmation round also accepts `proceed-with-rescope: <text>`.
    - For a gate previously closed by rescope, `confirm` is valid when the score is no higher than the score the rescope accepted.
    - Each confirmation records its evidence commit, which becomes the gate's commit for later checks.
    - `S-LISTEN`'s `Done when` reads "each gate's latest closing response is valid and its recorded commit renders the same demos as the head commit".
  - What it adds: every gate has a defined way to close, and identical audio is never re-heard.
- **F-6 (new; Medium; plausible). `confirm-again` is ambiguous and is paired only with `stop`.**
  - "confirm-again" reads naturally as "I confirm again", meaning close without listening. The intended meaning is "start a third confirmation round".
  - Its only alternative, `stop`, removes the instrument (DR-15).
  - A tired owner answers `confirm-again`. If the implementer closes the gate on it, unheard audio ships (R-068's harm). Otherwise the owner faces a fourth listening session.
  - Fix: rename it `start-confirmation`, and offer `proceed-with-rescope: <text>` (accept the unheard change, recorded) beside `stop`.
- **F-9 (new; Low; remote). The seed claim "never collide" is false for long confirmation chains.** Confirmation `j = 20` of gate `g` uses seed `1000(g+1) + 100 + k`, which is attempt `k` of round 1 of gate `g+1`. This needs 20 confirmations, each beyond the second approved with `confirm-again`. Fix: `j` below 10, or a separate range such as `100000 + ...`.

### 5. Integrity

- **F-4 (residual of R-079; High; plausible). `confirm` on a gate without pairs ignores "no demo reported as wrong".**
  - D-053 and GATES make `confirm` "valid only if the pass condition holds where pairs exist". `S-LISTEN`'s `Done when` checks scores only, never the `wrong:` line.
  - G-L1 and G-L4 (and G-L5 unless S-REF finds 12 notes) have no pairs (C-051). They are also the reed gates that a later reed change is expected to reopen.
  - Failure path: G-L1 `proceed` → G-L3 `iterate` changes `reed.cpp` → G-L1 confirmation → `wrong: -08-bend` with `confirm` → valid by the wording → gate closed → the pull request presents the harmonica as confirmed.
  - Mitigation:
    - `confirm` (and `proceed`) is valid only if the full pass condition holds: the score where pairs exist and, always, `wrong: none`. Otherwise ask once, as for `proceed`.
    - `S-LISTEN`'s `Done when` requires `wrong: none` in each gate's latest valid attempt, or a rescope that names the demo.
  - What it adds: the frozen demo clause covers the audio that ships.
- **F-3 (residual of R-078; High; remote). The exclusion grep stops only four spellings.**
  - What `grep -rnE "no_sanitize|fno-sanitize|__tsan_ignore|tsan_ignore" CMakeLists.txt plugins core tests/juce` misses:
    - removing the flag: `string(REPLACE "-fsanitize=thread" "" CMAKE_CXX_FLAGS ...)` or `list(REMOVE_ITEM ...)`, in a subdirectory or `cmake/` module that builds the JUCE modules as a separate static library;
    - files outside the four paths (`cmake/`, `CMakePresets.json`, `third_party/`);
    - TSan dynamic annotations, which hide races without removing instrumentation: `AnnotateIgnoreReadsBegin`/`WritesBegin`, `AnnotateBenignRaceSized`, `AnnotateHappensBefore`/`After`, `__tsan_acquire`/`__tsan_release`.
  - Two further weaknesses:
    - Without `-q`, grep returns 2 when any path is unreadable or missing, even with a match, and `if` treats 2 as "no match".
    - R-077's `nm` check still proves only that some translation unit is instrumented.
  - Failure path: a JUCE report that no accepted line can express (anonymous namespace, template-only frames, a `thread leak` or `mutex` report) → the implementer un-instruments the JUCE library by a route the grep misses → green → wrapper-against-JUCE races are invisible (round 4's incident 1).
  - Mitigation (optional; remote):
    - Check every object file in `build-tsan` that was compiled from JUCE module or `plugins/` sources: `nm -u` must list `__tsan_func_entry`.
    - Widen the grep to `fsanitize|Annotate(Ignore|BenignRace|HappensBefore|HappensAfter)|__tsan_` over all tracked files except the workflow.
    - Test grep's status explicitly (`rc=0; grep ... || rc=$?; test "$rc" -eq 1`).
- Restated: R-034 and R-056 (keys follow from public seeds), R-074 (casual listener), R-085 (a confirmation run force-pushes `evidence/<gate>` and replaces the bundle a gate judged).

### 6. Past lessons

- L-20261029T000000Z (confirm that a check can fail on the input it is meant for) was applied to the anchor syntax but not to the *scope* of a suppression; see F-1.
- L-20261009T193614Z (sign-off covers the code it judged) is applied by the demos-differ trigger, but a confirmation does not move the judged commit; see F-5(b).

### 7. Untrusted content

- No new path. The marker is parsed from the event payload with a strict pattern, references are hashed, and the 2 GiB bound applies (still untested: R-086).

### 8. Security

- Restated: R-023 (fork pull requests and the private fetch), R-030 (write token only in `publish`). The `audit` job installs `pip-audit==2.10.0` without hashes, but it runs with `contents: read` and no persisted credentials. No new path.

### 9. Integration

- **F-7 (residual of R-080; Medium; remote). The output trigger is ANDed with the old path list.**
  - D-053 reopens a gate only if the demos differ *and* `git diff -- core/ presets/ tools/folk-render/` is non-empty. A render-changing edit elsewhere (top-level `CMakeLists.txt` options such as `-ffast-math`, `-O3` or FTZ; a `cmake/` module) changes the demos but reopens nothing.
  - Failure path: an `S-REVIEW-DELTA` or `S-INTEGRATE` fix for a denormal or performance finding adds a compile option → the demos differ → no listed path changed → no confirmation → the pull request presents audio the owner never heard.
  - Fix: let the demo comparison alone decide.
- Restated: R-019 (the demos and the confirmation comparison use `folk-render`, never the plugin, so wrapper changes after a gate are never re-heard).

### 10. Scale and performance

- Restated: R-007, R-041. No new path.

### 11. Operational realities

- F-5 and F-6 (confirmation fatigue). A G-L1 confirmation repeats question 4, which needs a fresh CI artifact (younger than 3 days) and a reinstall each time (restated R-061, R-080).

### 12. CI platform coverage and runner-label drift

- **F-10 (new; Low; speculative). The canaries are built differently from the host tests.**
  - The canaries are built `c++ -fsanitize=thread -O1` without `-g`, so frames are symbolised from the symbol table.
  - The host tests are `RelWithDebInfo` (`-O2 -g`), so frames are symbolised from DWARF through libbacktrace, inlined frames included.
  - Both should give the same demangled names with parameter lists. I found no path where they differ, so this is recorded as speculative.
  - Cheap fix: compile the canaries with `-O2 -g -fno-omit-frame-pointer`.
- Restated: R-006 (`macos-15-intel` is the last Intel image), R-082 (the same SIGPIPE class exists in `b="$(find ... | head -n 1)"`, but harmless with one match).

### 13. Licensing

- **F-8 (new; Medium; remote). D-051's private threshold (12) contradicts S-REF's search to 14, and the control references are not part of the routing rule.**
  - The contradiction: S-REF searches (a) to (c) first and (d) Philharmonia last, and stops at 14. With 12 or 13 redistributable mandolin notes, S-REF goes on to Philharmonia for the controls, which D-051 does not justify (Rule 15).
  - The routing rule: `build_evidence.py` sends pairs to the public `pairs/` "when every one of the 12 references is redistributable", and skips pairs only if one of "the 12" is absent.
  - In CI the private controls are absent (the fetch is `--only-redistributable`), so the build fails or falls back to repeating controls. I checked the publication path: it is closed by that fetch, so this is not Critical.
  - Fix:
    - S-REF indexes a private note only while the redistributable pool has fewer than 12.
    - Routing, absence handling and `MANIFEST.json` consider all 14 references.
- Restated: R-045 and R-063 (notices), R-016.

## Findings table

| F | Description | Class | Severity | Likelihood (conditions) | Failure path | Mitigation |
|---|---|---|---|---|---|---|
| 1 | Accepted `race:`/`deadlock:` lines apply to every frame of both stacks; JUCE frames lie above wrapper code in T-304, so a line naming one hides wrapper races; the canaries test syntax, not scope | residual (R-051, R-078) | High | plausible (a JUCE-internal report on the parameter or state path, as ENVIRONMENT section 5 anticipates) | report → `race:^juce::AudioProcessorParameter::setValueNotifyingHost(` → green → wrapper listener race hidden for good | `race_top:` only; `deadlock:` only via G-004; a scope canary that must still report |
| 2 | "Every frame lies in JUCE" is unsatisfiable in T-304 (harness, libstdc++ and processBlock frames) | new | Medium | plausible (any JUCE-internal report) | S-320 → guess, or blocked | rule stated on top frames |
| 3 | The exclusion grep misses flag removal, other paths and TSan annotations; grep status 2 is read as no match | residual (R-078) | High | remote (an unexpressible JUCE report and a deliberate workaround) | un-instrumented JUCE library → green → wrapper-against-JUCE races invisible | per-object `__tsan_func_entry` check; wider grep; explicit status |
| 4 | `confirm` on a gate without pairs does not check "no demo reported as wrong"; the Done when never reads the `wrong:` line | residual (R-079) | High | plausible (confirmation of G-L1, G-L4 or G-L5 with a demo named wrong) | reed change → G-L1 confirmation → `wrong: -08-bend` + `confirm` → shipped | full pass condition for `confirm`; Done when reads `wrong:` |
| 5 | A confirmation can close only with `confirm`; a rescoped gate cannot re-close; no re-baseline, so gates re-trigger on identical audio | new (from R-079's fix) | High | plausible (a gate with pairs rescoped over its score, then a shared change) | G-L2 rescope → pluck change → 10/12 → rescope not allowed → guess or forced `iterate` | `proceed-with-rescope` in confirmations; re-baseline; Done when on latest valid closure |
| 6 | `confirm-again` is ambiguous; the only alternative is `stop` | new | Medium | plausible (a third confirmation) | read as closure → unheard audio ships | rename; add rescope |
| 7 | Demo-diff trigger ANDed with the path list misses render changes outside it | residual (R-080) | Medium | remote | compile-option fix → demos differ → no confirmation | demo comparison alone |
| 8 | D-051 (12) against S-REF (14); routing and absence rules see only 12 references | new | Medium | remote (12 or 13 redistributable mandolin notes) | Philharmonia controls without justification; CI evidence fails | private only below 12; route on 14 |
| 9 | Confirmation seed collides with the next gate's round 1 at j = 20 | new | Low | remote | 20 confirmations → shared key | bound j |
| 10 | Canaries are built with other flags than the host tests | new | Low | remote | none found | speculative; same flags |
| 11 | Restatements: R-001, R-004, R-006, R-009, R-016, R-019, R-023, R-028, R-030, R-034, R-037, R-045, R-056, R-061, R-063, R-074, R-080, R-082, R-085, R-086 | restated | n/a | n/a | n/a | n/a |
