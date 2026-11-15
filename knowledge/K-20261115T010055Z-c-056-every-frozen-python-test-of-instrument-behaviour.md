---
id: K-20261115T010055Z-c-056-every-frozen-python-test-of-instrument-behaviour
statement: "Every frozen Python test of instrument behaviour can be passed by one consistent idealised instrument (an additive stand-in), with the exception of the byte-identity test, which the stand-in fails only because libsndfile time-stamps float WAV files."
status: current
supersedes: []
tags: [subject:frozen-test-manifest, phase:research]
applies_to_version: "this run"
source: { url: "research/spikes/s08-test-oracle/README.md", doi: "", title: "planning spike S08", locator: "result paragraph", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-056]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:55Z
---
Round 4: this shows the tests are mutually consistent, not that they separate a right instrument from a wrong one; that is the job of the reference metrics and the listening gates.

Input-file verdict: not-in-input. Load-bearing: yes. Informs: T-100, T-163, D-092.

All sources: planning spike S08 (result paragraph).
