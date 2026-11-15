---
id: K-20261115T010057Z-c-058-numpy-2-5-and-scipy-1-18-require-python-3-12-or
statement: "numpy 2.5 and scipy 1.18 require Python 3.12 or later."
status: current
supersedes: []
tags: [tech:python, subject:python-test-tooling, phase:research]
applies_to_version: "this run"
source: { url: "research/rounds/r3-adversarial.json", doi: "", title: "round-3 adversarial review (sources read in full where it says so)", locator: "missing_claims: PyPI requires_python", accessed: "2026-11-14", tier: 3 }
confidence: single-source
derived_from: [C-058]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:57Z
---
The plan pins Python 3.13, the version the spikes ran on, so the claim's exact lower bound does not matter.

Input-file verdict: not-in-input. Load-bearing: no. Informs: D-085.

All sources: round-3 adversarial review (sources read in full where it says so) (missing_claims: PyPI requires_python); PyPI index: numpy, scipy, soundfile, pytest versions (installed on Python 3.13 in the sandbox).
