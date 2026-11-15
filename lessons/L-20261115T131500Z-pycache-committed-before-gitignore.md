---
id: L-20261115T131500Z-pycache-committed-before-gitignore
title: Python cache files were committed because .gitignore was written after the first commits
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Low
tags: [tech:git, tech:python, phase:planning, kind:process]
recorded_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T13:15:00Z
---
## Trigger
A generation branch whose checkpoint helper runs `git add -A`, with Python spikes and tests run in the working tree before any `.gitignore` exists.
## What went wrong
Four `__pycache__/*.pyc` files were committed in checkpoints; the mechanical cold read found one of them under `tests/`, outside the freeze manifest.
## Correction
The files were removed from the index with `git rm --cached` and `.gitignore` lists `__pycache__/`, `*.pyc` and `.pytest_cache/`.
## Prevention rule
Write `.gitignore` (with the language's cache and build patterns) in the same commit that creates the generation branch's skeleton, before any script is run in the working tree.
## Detection check
`git ls-files | grep -E '__pycache__|\.pyc$|\.pytest_cache'` prints nothing.
## Evidence
`research` commit "checkpoint: 3.6 cold-read pass 1 fixes"; mechanical cold-read check 8.
