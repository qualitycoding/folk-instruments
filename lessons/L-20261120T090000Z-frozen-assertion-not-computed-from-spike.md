---
id: L-20261120T090000Z-frozen-assertion-not-computed-from-spike
title: A frozen C++ test asserted a ratio that nobody had computed, and no correct implementation could pass it
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Medium
tags: [tech:cpp, domain:audio, phase:planning, kind:verification-gap]
recorded_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-20T09:00:00Z
---
## Trigger
A frozen test adds an assertion (a ratio, a bound, 'remains distinct') beyond the values the cited spike actually measured.
## What went wrong
T-006's 3-cent case required the fast mode to decay more than 10 times faster than the slow one. Spike S04 had measured only the frequency split for that case; the exact eigenvalues give 6.63 and 2.50, a ratio of 2.65. Red verification against stubs passed (every case fails against a stub), and the oracle check of the frozen suite (spike S08) covered the Python tests only, so the impossible assertion reached the implementer, who stopped at S-101 with a TEST_CHALLENGE.
## Correction
D-096: the case pins both decay rates to the closed form and requires a factor of 2; re-frozen; checked red against the stubs and green against the implementer's solver.
## Prevention rule
Every numeric assertion in a frozen test is computed from the spike or a closed form before freezing, and the whole frozen suite, C++ included, is run once against a reference implementation (the spike's code or a minimal oracle) so that every assertion is shown satisfiable, not only shown to fail against stubs.
## Detection check
For each frozen test file, a run against a reference implementation passes every assertion; any assertion not exercised by such a run is listed and justified.
## Evidence
Implementer's `TEST_CHALLENGE.md` (branch ccr-f45525dd-81yib1, commit d7ef528); `research/spikes/s04-coupled-pair/output.json` (`3c_strong_coupling_mode_split_Hz` only); `tests/cpp/test_strings.cpp`.
