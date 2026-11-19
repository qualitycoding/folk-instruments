# Pre-mortem round 6 (limited to the steps changed by the assumption audit)

Reviewer: fresh context; did not write the plan. Material: the checkout `pm6`, read only (no git, no web, no builds). Scope: D-090 (locale rationale), D-064 (body-mode figures), the frozen `tests/cpp/test_locale.cpp` (T-016) and the T-302 locale case in `tests/juce/host_test.cpp`, the `host-tsan` object-instrumentation check in `plan/ci/ci.yml` and its row in `plan/ENVIRONMENT.md` section 5, the new section 5 rows TP-LOC-1 and TP-T304-1, S-201's Checkpoint, S-220's Done when, S-330 action 2, and question 4 at the pilot gates in `plan/GATES.md`. Severity is graded by `HANDOFF.md` section 6 (the `[All]` and `[software]` lines). Likelihood is graded as in `premortem/RISK_REGISTER.md`.

Read-only checks run for this round (none of them changed the checkout):
- The frozen manifest: all 36 hashes in `tests/FROZEN_MANIFEST.sha256` match, including the re-frozen `test_locale.cpp` and `host_test.cpp`.
- pytest collection on a **copy** of `tests/` in the scratchpad (`PYTHONDONTWRITEBYTECODE=1`; the copy was deleted afterwards). `python3 -m pytest -m reference -k accordion --collect-only` gives `no tests collected (361 deselected)`, exit status 5. `-m reference` alone collects 16 tests. `-m reference -k T200` collects 11.
- The sub-step counts of D-011, `m = ceil(C f / (4 fs))`: at 444 Hz, m = 1 for both C = 110 and C = 160. At MIDI 87, m = 1 or 2. At MIDI 99, m = 2 (C = 110) or 3 (C = 160). At MIDI 112, m = 4 or 5.
- The S17 output (`research/spikes/s17-string-body/output.json`) gives T146 levels of -36.68, -42.87 and -47.91 dB. That is a spread of 11.23 dB, so the corrected D-064 text is right.

## 1. Incident report (simulation)

**Folk Instruments, six months after delivery: the accordion ships late and reduced, and the owner stops using it.**

Every step's `Done when` passed, or was logged as failed in the way the plan allows (S-330 after five DR-07 rounds). The run still delivered an accordion that fails its reference comparison and holds fewer keys than intended. It also lost three weeks to a halt at the pilot gate.

1. **G-P1, question 4.** The owner answered the new scope question with `proceed-with-rescope: drop the Irish bouzouki variant, keep the rest`. The branch text says to apply a reduction of scope, "for example dropping a variant". The implementer recorded the rescope and kept going. At S-260, T-140 and the T-15x cases for `("bouzouki", "variant", 2)` could not pass, because the variant is frozen in `param_table.h` and in `test_strings.py`. The implementer wrote `TEST_CHALLENGE.md` and the strings track halted until the planning agent amended the plan.
2. **S-220 early reference probe.** The implementer ran the command exactly as written, `cd tests && python3 -m pytest -m reference -k accordion -s`. pytest printed `no tests collected (361 deselected)`. `EXECUTION_LOG.md` recorded "accordion reference probe run once: no failures", and S-220 was done. On the next try, in a recycled sandbox without TinySOL, the implementer used the CI route instead. DR-13 says the step is done only when that job is green. But the job is red until S-330 calibrates, and S-330 depends on S-300, which depends on S-220. The implementer guessed that the step's own words ("a failure here does not fail this step") overrode DR-13. Either way, nobody learned at the pilot stage that the similarity-scaled reed misses the TinySOL harmonic profile at pp.
3. **S-201 Checkpoint.** The "cost of one reed per sample" was taken with `time reed_probe --freq 444 ...`. That is one reed for about one second of audio with one sub-step per base-rate sample (m = 1), so the figure was mostly process start and table build. It showed plenty of headroom, and it said nothing about C = 160 or about the 4' rank up to MIDI 99, where m is 3.
4. **S-330 calibration.** The A-022 miss surfaced only here. Round 3 raised the Q curve, so C became 160. The local `FOLK_PERF_GATE=1 $B/folk-perf` run then printed `gate=1` with an accordion factor of 3.7 and exited non-zero. S-300 says that a local factor below 4 is not a failure, but this command makes the miss a failing test. The implementer read it as a regression and reverted round 3, which spent a round. The five rounds were used up and S-330 was logged as failed.
5. **S-320.** The runner gave the accordion 3.4x. DR-06 reduced its polyphony from 16 keys to 12. G-L3 was answered `proceed-with-rescope` and the PR was opened red (DR-16). In use, four-rank chords with a bass line drop notes in the owner's DAW, the timbre at pp sounds thin, and the owner stops using the plugin.

What held: the locale changes. T-016 and the T-302 locale case now switch both the C and the C++ global locale and probe a default stream. A stream left on the global locale would write `0,37…`, which the comma check catches. A default `istringstream` reading `0.37` under `de_DE` treats the `.` as a grouping separator and fails, which the round trip catches. The widened ThreadSanitizer object check still catches every translation unit compiled without the sanitiser.

## 2. Findings by lens

### Technical correctness
- **F1 (High, expected, residual R-128).** S-220's early probe selector `-k accordion` matches no reference test. The item names are `test_T200_*[pp|mf|ff]` and `test_T201_*[harmonica|melodion|mandolin|bouzouki]`, and the module is `test_reference.py`. The collection check gives `no tests collected (361 deselected)` with exit status 5. The A-022 probe that R-128's mitigation depends on therefore never runs locally.
- **F7 (Low, remote, new).** The T-302 locale case restores the locale by a plain call at the end, not RAII as in T-016's `RestoreC`. If an exception escapes between `setCommaLocale()` and `restoreClassicLocale()`, the later test cases in the same host program run under a comma C locale and a comma C++ global locale. The result is cascading failures, never a false pass.
- **F10 (speculative).** The T-302 locale case checks only a round trip within one locale and never searches the blob for a comma. Its only wrapper-specific content is `#program <int>`, which is locale-proof for indexes below 1000, and T-016 covers the engine text, so no failure path was found.

### Invalid assumptions
- **F2 (High, plausible, new).** S-220's Done when sends the probe to CI "under rule DR-13". DR-13 makes the step "done only when that job is green", while the step says that a failure "does not fail this step". The `reference` job is red until S-330 calibrates (that is the purpose of S-330). Under DR-13 this makes a cycle: S-220 waits for a green job, the job waits for S-330, S-330 needs S-300, and S-300 needs S-220.
- **F4 (Medium, plausible, residual R-120).** S-201's per-reed cost is measured at 444 Hz, where m = 1 for both C values: the cheapest case. It times the whole `reed_probe` process for about one second of a single reed. From S05, one reed costs about 2.8 ms per second of audio, so the timing is dominated by process start, table build and JSON output, which past lessons L-20261004T102002Z and L-20261009T150301Z forbid. It runs on the local machine, not the runner, and has no threshold or decision rule. C = 160 and the high ranks (m = 2 or 3), which the audit named for A-009, are outside what it measures. T-013 and DR-06 still catch a real miss on the runner, so the result is late discovery, not a hidden one.

### Implementer misinterpretation
- **F3 (High, plausible, new).** Pilot-gate question 4 invites rescoping "five instruments, the variants, VST3 and Standalone on Windows, macOS and Linux". The `proceed-with-rescope` branch says to apply a reduction "for example dropping a variant", and to write `BLOCKED.md` only "if the text asks for something that changes a public interface or a frozen test". Every variant, every instrument and every runner is frozen: in `param_table.h`, `test_strings.py`, `test_harmonica.py`, `kAllInstruments` in T-013 and T-016, and the ctest count of 7. So the plan's own example is a frozen-test change. An owner's reduction asks nothing about tests, but applying it makes frozen tests unpassable. The implementer must guess between applying it (and halting late at S-260 or S-300) and blocking at once.
- **F5 (Medium, plausible, new).** S-330 action 2 runs `FOLK_PERF_GATE=1 $B/folk-perf` locally after each calibration round. With the variable set, T-013 `CHECK`s the factor and the program exits non-zero below 4. D-086 confines the gate to the ubuntu-24.04 runner, and S-300 says that a local factor below 4 "is not a failure". A red local run during calibration can be read as a regression (revert the round) or as DR-06 (cut polyphony on sandbox figures). Both cost DR-07 rounds or scope. Recording the PERF lines needs no gate: they are printed with or without it.

### Integrity
- **F11 (speculative).** The re-frozen locale tests were verified red against the stubs only. The past lessons (L-20261029T000000Z, L-20261009T234102Z) ask that a gate be fed a failing input. No mutant with default-stream formatting was run. Analysis shows that the `find(',')` check and the round trip catch it, so no failure path was found. The `setCommaLocale()` code itself did execute in the red run, because it comes before `Engine::create` in case 1 and in T-302.

### Past lessons
These are covered within F1, F3, F4 and F11. The three new lessons are applied correctly: D-064 quotes the measured levels with an outward-rounded bound; both locale tests switch both locales and probe; and the hook set includes `__tsan_init`, which an empty translation unit references.

### CI platform coverage
- **F8 (Low, remote, new).** The widened object check reads `nm` symbols. If the ThreadSanitizer build is ever made with GCC LTO (slim objects, where the tsan pass and its constructor run at link time), the objects carry no `__tsan_*` reference. The check would then fail on a correctly instrumented build, and section 5 would call that "a defect, never an exception". The failure is loud and the remedy (no LTO in that job) is evident. Nothing in the plan enables LTO.
- **F9 (speculative).** Accepting `__tsan_init` turns the check into "the translation unit was compiled with `-fsanitize=thread`". It no longer notices `--param=tsan-instrument-func-entry-exit=0`, which the old `__tsan_func_entry` rule would have caught. That parameter removes only caller frames from reports. The `race_top:` rule and the plugins/core top-frame rule are unaffected, so there is no product harm.
- **F12 (Low, remote, new).** The `core` job's Linux locale step runs `apt-get install locales` without `apt-get update`, unlike the `plugins` and `host-tsan` jobs. If an image ever lacks the package and has empty apt lists, the step fails loudly. The package is unpinned (supply-chain drift): `locale-gen` behaviour comes from the image.
- TP-LOC-1 (macOS, Windows): no new failure path. The loop's names cover UCRT and Apple. `std::locale::global` of a named locale also calls `setlocale`, and a missing locale fails loudly at `REQUIRE(setCommaLocale())`, which is the first statement of T-016 case 1 and of the T-302 case and so is visible even against the stubs. This is R-098, restated, and not counted.

### Performance
- F4 and F5 above.
- **F6 (Low, plausible, residual R-130).** The TP-T304-1 row says "Catch2 prints both counts when a CHECK fails". Catch2 prints only the failing `CHECK`'s expansion, so the other count is never shown. The auditor's proposal to print the counts on every run (`-s` or `INFO`) was not adopted, so the margin of T-304 under ThreadSanitizer stays invisible while S-330 (C = 160) and later fixes add cost. A real shortfall still fails loudly, with the TEST_CHALLENGE route.

### Operations
- F3 (a gate answer that halts the run).

### Documentation
- **F13 (Low, expected, new).** D-064 now says "within 11.3 dB (… a spread of 11.2 dB …)": two bounds for one quantity in one sentence. Both are right for 11.23 dB, but a reader may take one of them as a test threshold. T-146 uses 30 dB.

### Security, untrusted content, licensing, supply chain
No new failure path in the changed steps. The state-text grammar, the refusal of `level=0,25` and the threat model are unchanged. No licence or pin changed. The unpinned `locales` package is noted under F12.

## 3. Findings table

| n | Class | Restates | Lens | Severity | Likelihood (conditions) | Status | Short description |
|---|---|---|---|---|---|---|---|
| 1 | residual | R-128 | technical correctness | High | expected (the command as written) | open | S-220 probe `-k accordion` selects 0 of 16 reference tests (exit 5); the A-022 probe never runs locally |
| 2 | new | | invalid assumptions | High | plausible (local TinySOL run not possible, so the CI route; T-200 red before S-330) | open | S-220's "failure does not fail this step" against DR-13's "done only when that job is green": a dependency cycle S-220 → reference green → S-330 → S-300 → S-220 |
| 3 | new | | implementer misinterpretation / operations | High | plausible (the owner answers question 4 with a reduction) | open | Pilot-gate rescope branch: the example "dropping a variant" is itself a frozen-test change; the implementer must guess between applying it (late halt) and blocking |
| 4 | residual | R-120 | performance / invalid assumptions | Medium | plausible (the runner is slower than local, or C = 160 and the high ranks erode the margin) | open | S-201's per-reed cost is timed at 444 Hz (m = 1), whole process, local machine, no threshold: no early warning |
| 5 | new | | implementer misinterpretation / performance | Medium | plausible (the local factor is below 4 during calibration) | open | S-330's local `FOLK_PERF_GATE=1` run fails locally, against D-086 and S-300; read as a regression or as DR-06 |
| 6 | residual | R-130 | performance / documentation | Low | plausible | open | The TP-T304-1 row overstates Catch2's output; the T-304 margin under ThreadSanitizer stays invisible |
| 7 | new | | technical correctness | Low | remote (an exception inside the T-302 locale case) | open | The T-302 locale case restores the locale without RAII; later cases run under a comma locale |
| 8 | new | | CI platform coverage | Low | remote (LTO enabled in the ThreadSanitizer build) | open | Slim LTO objects carry no `__tsan_*` reference, so the object check fails a correct build |
| 9 | new | | CI platform coverage | Low | remote | speculative | Accepting `__tsan_init` no longer detects a ThreadSanitizer function-entry parameter; no product harm |
| 10 | new | | technical correctness | Low | remote | speculative | The T-302 locale case never checks the blob for commas or across locales; no wrapper route found |
| 11 | new | | integrity / past lessons | Low | remote | speculative | The amended locale tests were never fed a default-stream mutant; analysis shows it is caught |
| 12 | new | | CI platform coverage / supply chain | Low | remote (an image without `locales` and with empty apt lists) | open | The `core` job installs `locales` without `apt-get update`, unpinned |
| 13 | new | | documentation | Low | expected | open | D-064 gives two bounds (11.3 and 11.2 dB) for one spread |

Counted (new or residual, not speculative): 10. Critical: 0. High: 3 (1 expected, 2 plausible). Medium: 2. Low: 5 counted, plus 3 speculative.

## 4. Mitigations (each new or residual High at expected or plausible)

- **F1.** In S-220's Done when, replace `-k accordion` with `-k T200` (11 tests; T-200 is the accordion comparison, and it needs `FOLK_TINYSOL` and `FOLK_RENDER` only). Require the record to name the number of tests run, which must be 11, with their pass or fail lines, and state that pytest exit status 5 ("no tests collected") means the probe did not run. *Adds:* the probe actually executes T-200a to T-200e against the first accordion build, and a vacuous run cannot be recorded as a result.
- **F2.** In S-220, say that DR-13 applies to where the probe runs, not to its outcome: "the step is done once a CI `reference` run on a commit that contains the accordion has finished and its T-200 pass or fail lines are copied into `EXECUTION_LOG.md`, green or red". Exempt this probe from DR-13's "green" clause in the DR-13 row as well. *Adds:* removes the cycle S-220 → S-330 → S-300 → S-220 and the guess between the two texts.
- **F3.** In `plan/GATES.md`, replace the example "dropping a variant" with a reduction that touches no frozen test (for example, dropping a factory preset or a demo). Add one sentence: "dropping an instrument, a variant, a format or a platform changes frozen tests or `ci.yml`. Write `BLOCKED.md` at once, naming the frozen tests and workflow lines concerned, so the planning agent can amend them, and continue the steps the reduction does not touch (as DR-05 does)". Then mirror question 4's list in the gate record template, so the owner sees that such answers pause the run. *Adds:* a reduction is routed at the gate rather than discovered at S-260 or S-300, the owner knows what the answer costs, and the implementer has nothing to guess.

Suggested only (Medium, no mitigation required): for F4, time 64 reeds over the T-013 key range inside `reed_probe` (in-process `steady_clock` around the step loop, at C = 110 and C = 160), and compare the result with 4x on the S-320 runner once CI exists. For F5, drop `FOLK_PERF_GATE=1` from S-330 action 2 (the PERF lines print without it) and state that a local factor below 4 is recorded, not acted on.
