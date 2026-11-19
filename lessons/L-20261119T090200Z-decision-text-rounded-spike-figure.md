---
id: L-20261119T090200Z-decision-text-rounded-spike-figure
title: A decision quoted a spike result rounded the wrong way
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Low
tags: [domain:audio, phase:planning, kind:wrong-assumption]
recorded_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-19T09:02:00Z
---
## Trigger
A decision or claim restates a number measured by a spike in words such as 'within N dB'.
## What went wrong
D-064 said the first three f-hole body modes of spike S17 lie within 11 dB after a tap; a re-run gives -36.7, -42.9 and -47.9 dB, a spread of 11.2 dB. No test depended on it (T-146 allows 30 dB), but the decision text misreported the reference.
## Correction
D-064 now quotes the three levels and the spread.
## Prevention rule
Quote a spike's measured figures with the bound computed from them, rounding the bound outwards, and cite the output file.
## Detection check
Every 'within' figure in a decision is at least the spread computed from the cited output file.
## Evidence
`premortem/ASSUMPTION_AUDIT.md`, item 'D-060 to D-064 string premises (S17)'; `research/spikes/s17-string-body/output.json`.
