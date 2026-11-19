---
id: L-20261119T090000Z-setlocale-does-not-switch-cpp-streams
title: A locale test switched only the C locale, so it could not catch a C++ stream following the global locale
status: active
supersedes: []
recurrence_of: null
occurrences: 1
severity: Medium
tags: [tech:cpp, domain:audio, phase:planning, kind:wrong-assumption]
recorded_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-19T09:00:00Z
---
## Trigger
A test or decision guards against locale-dependent number formatting and changes the locale only with `setlocale`.
## What went wrong
T-016 and the T-302 locale case set `de_DE.UTF-8` with `setlocale` and assumed every forbidden formatting route then follows it. Default-constructed C++ streams follow `std::locale::global`, which `setlocale` does not change: under the probe, `printf` wrote `0,5` while `std::ostringstream` still wrote `0.5`. The frozen tests could not catch the stream route that D-090 forbids.
## Correction
Both tests now switch the C locale and the C++ global locale, and check with a probe stream that the switch is real; they were re-frozen and red-verified. D-090 states both routes.
## Prevention rule
When a test is meant to catch locale-dependent formatting, switch both `setlocale(LC_ALL, ...)` and `std::locale::global(std::locale(...))`, and assert with a probe (`printf` and a default stream both print `0,5`) that the switch took effect.
## Detection check
The locale test contains a probe that formats 0.5 with a default-constructed stream and requires `0,5`.
## Evidence
`premortem/ASSUMPTION_AUDIT.md`, item TP-LOC-2; `tests/cpp/test_locale.cpp`.
