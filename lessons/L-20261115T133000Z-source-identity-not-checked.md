---
id: L-20261115T133000Z-source-identity-not-checked
title: A research worker named an arXiv identifier as a paper's preprint without opening it, and the register carried the wrong identity
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Low
tags: [domain:audio, phase:research, kind:verification-gap]
recorded_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T13:30:00Z
---
## Trigger
A research worker, reading search results only, links a paper to a preprint identifier (arXiv, HAL, a repository record) that appears near it in the results.
## What went wrong
arXiv 2104.02480 was recorded as the preprint of Woodhouse's double-decay paper; it is a banjo guide by other authors. The source register repeated the error until the fifth review pass opened the page.
## Correction
The register row was rewritten from the page itself; no claim had relied on the identifier.
## Prevention rule
Record a preprint or mirror as a version of a paper only after opening it and matching title and authors; otherwise list it as a separate, unverified source.
## Detection check
For every register row whose content names a paper, the title on the fetched page matches the title in the row.
## Evidence
`research/r7-register-review-pass5.json`, row 45; `research/rounds/r1-D-plucked-string.json`, claim D8.
