---
id: K-20261115T010053Z-c-054-one-step-of-the-reed-model-costs-10-to-15-ns-per
statement: "One step of the reed model costs 10 to 15 ns per reed in plain C++ (-O2, double precision, table look-up for the useful section; the loop is not vectorised) on the planning sandbox (Intel Xeon 2.1 GHz): 64 sounding reeds between 65 Hz and 1.5 kHz, scaled as in D-012, at 4 times 48 kHz run 5.6 times faster than real time on one core (6.4 times with -ffast-math). The figure covers the reeds only, not decimation, filters or the wrapper."
status: current
supersedes: []
tags: [subject:free-reed-modelling, phase:research]
applies_to_version: "this run"
source: { url: "research/spikes/s05-reed-cost/output2.txt", doi: "", title: "planning spike S05B", locator: "both lines", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-054]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:53Z
---
Measured on the sandbox, not on the CI runner the target names (A-009); T-013 gates there.

Input-file verdict: not-in-input. Load-bearing: yes. Informs: D-014, D-086, T-013.

All sources: planning spike S05B (both lines); planning spike S05 (first benchmark (A4 geometry for every reed)); round-4 adversarial review (review of C-054).
