---
id: L-20261119T090100Z-tsan-func-entry-not-in-every-object
title: A CI check required __tsan_func_entry in every instrumented object, which GCC omits for trivial functions
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Medium
tags: [tech:cpp, tech:github-actions, phase:planning, kind:wrong-assumption]
recorded_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-19T09:01:00Z
---
## Trigger
A CI step proves a sanitiser build by looking for one specific hook symbol in every object file.
## What went wrong
R-088's check required `__tsan_func_entry` in every object with a function. GCC 13 omits it for functions with no instrumented memory access or call (a function returning `x * 2.0 + 1.0` has none), so a correctly instrumented build could fail CI and the plan called that a defect.
## Correction
The check accepts any ThreadSanitizer hook, including `__tsan_init`, which GCC 13 references even from an empty or data-only object (verified in the sandbox); ENVIRONMENT section 5 says so.
## Prevention rule
Before writing a check that a build is instrumented, compile an empty file, a data-only file and a trivial pure function with the same compiler and flags, and list which hooks each object references; accept the hook that all three carry.
## Detection check
The check's accepted hook set includes one that an empty translation unit compiled with the sanitiser references.
## Evidence
`premortem/ASSUMPTION_AUDIT.md`, item TP-TSAN-2; `plan/ci/ci.yml` job `host-tsan`.
