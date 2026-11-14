---
id: L-20261114T135000Z-onset-counter-missed-first-frame
title: An onset counter that compares each frame with an earlier frame missed the attack at time zero
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Low
tags: [domain:audio, tech:python, phase:specification, kind:verification-gap]
recorded_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-14T13:50:00Z
---
## Trigger
Writing an attack or onset counter for rendered audio that detects a rise in frame level relative to a frame a few frames earlier, where the rendered file starts with a note at time zero.
## What went wrong
The loop started at the third frame, so a note that begins in the first frame had no earlier frame to rise from and was not counted: 23 attacks were reported for 24 strokes.
## Correction
The envelope is padded with two frames of silence before the comparison, so an attack in the first frame counts. The known-answer test (24 strokes in 2 s) then passed.
## Prevention rule
Give every measurement function used by a frozen test a known-answer test whose signal includes an event in the first analysis frame and one in the last.
## Detection check
`python3 -m pytest -q tests/py/test_metrics_selfcheck.py` passes, and `test_count_onsets` uses a signal whose first stroke starts at sample 0.
## Evidence
`tests/py/test_metrics_selfcheck.py::test_count_onsets` failed with `assert 23 == 24` before the change.
