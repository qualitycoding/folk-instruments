---
id: K-20261119T150000Z-apple-libcxx-float-charconv-availability
statement: "With Xcode 16.4 (Apple clang 17.0.0) on the macos-15 GitHub runner, float std::to_chars is marked unavailable below deployment target macOS 13.3 ('introduced in macOS 13.3'), and float std::from_chars is not provided at deployment targets 11.0, 13.3 or 15.0 (the call resolves to a deleted overload)."
status: current
supersedes: []
tags: [subject:cpp-portability, phase:planning]
applies_to_version: "Xcode 16.4, macos-15 runner image of 2026-11"
source: { url: "https://github.com/qualitycoding/folk-instruments/actions", doi: "", title: "CI probe run 44538676455, job apple-tochars (branch probe-assumptions, deleted after reading)", locator: "job log", accessed: "2026-11-19", tier: 2 }
confidence: verified
derived_from: []
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-19T15:00:00Z
---
Measured by a one-off probe workflow run at the owner's request to check planning assumptions; the probe branch was deleted after its logs were read.
