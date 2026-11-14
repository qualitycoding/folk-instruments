---
id: L-20261114T090000Z-fetch-tool-shares-sandbox-allowlist
title: The web fetch tool obeys the sandbox network allowlist, so research workers could not read sources
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Medium
tags: [tech:claude-code-cloud, phase:research, kind:wrong-assumption]
recorded_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-14T09:00:00Z
---
## Trigger
A planning run in a cloud session whose environment has limited network access. The 0.1 diagnostic shows `curl` to paper and dataset hosts refused, and the plan is to do literature research "through the web search and fetch tools".
## What went wrong
The planner assumed the fetch tool ran outside the sandbox allowlist and launched six research workers. The fetch tool failed name resolution for every host outside the allowlist, so the workers returned claims read from search snippets only, and worker quota was spent on a round that could not corroborate anything.
## Correction
The planner proposed adding the exact literature, dataset and manufacturer hosts to the environment's allowlist, the owner approved, and the depth pass was re-run against the sources themselves.
## Prevention rule
In the 0.1 diagnostic, fetch one page from each class of host the research depends on with the same tool the research will use, and resolve every refusal (allowlist change or recorded alternative channel) before any research worker is started.
## Detection check
`.checkpoints/state.json` `diagnostic` lists, per research host class, the tool used and the result of a real fetch made before round 1.
## Evidence
`research/rounds/round-1.md`, section "Access failure"; the first versions of `research/rounds/r1-*.json` carry `read_depth: snippet only` on every source.
