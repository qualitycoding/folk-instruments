---
id: L-20261114T135800Z-frozen-tests-checked-against-oracle
title: Three audio tests written against stubs were wrong, and only a stand-in renderer showed it
status: active
supersedes: []
recurrence_of: L-20261004T162212Z-unsatisfiable-frozen-assertions
occurrences: 3
severity: High
tags: [domain:audio, tech:pytest, phase:specification, kind:verification-gap]
recorded_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-14T13:58:00Z
---
## Trigger
Frozen tests for audio behaviour are written before any implementation exists. Against stubs each test fails at its first line (the render call), so red verification says nothing about the assertions after that line.
## What went wrong
Three of the planner's tests could not have been passed by a correct instrument: (1) a body-mode test analysed 0 to 0.5 s with a Hann window for a tap at 0 s, so the window removed the short-lived modes it was looking for (levels 41 dB apart for modes of nearly equal strength); (2) an octave-course test compared partial levels over 0.05 to 0.75 s, after the bridge-coupled pair's fast in-phase decay had removed the difference; (3) a sustain test required less than 15 dB of decay in 0.55 s, which the first decay of a coupled pair exceeds.
## Correction
An idealised additive stand-in for the render tool was written (`research/spikes/s08-test-oracle/fake_render.py`), the whole Python suite was run against it, the three tests were corrected (analysis window placed just after the tap; rigid bridge for the level comparison; a relative instead of an absolute bound), and the suite was re-run until every remaining failure was explained.
## Prevention rule
Before freezing audio tests, run every one of them against a stand-in renderer that implements the intended behaviour in the simplest possible way, and explain or fix every failure; a test that has only ever failed at its first line is not verified.
## Detection check
The generation branch holds the stand-in renderer and a note of its last run listing each failing test with its explanation, dated before the freeze commit.
## Evidence
`research/spikes/s08-test-oracle/README.md`; the earlier lesson of the same kind is L-20261004T162212Z-unsatisfiable-frozen-assertions (its rule, to check thresholds against the reference spread, is strengthened here to executing the assertions).
