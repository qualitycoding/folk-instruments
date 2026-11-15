---
id: K-20261115T010006Z-c-007-the-first-clamped-free-bending-frequency-of-a-un
statement: "The first clamped-free bending frequency of a uniform rectangular reed is f1 = (1.875104^2/(2 pi sqrt(12))) (t/L^2) sqrt(E/rho) = 0.16154 (t/L^2) sqrt(E/rho), and the input file's reed-length table follows from it to within 0.005 mm."
status: current
supersedes: []
tags: [subject:free-reed-modelling, phase:research]
applies_to_version: "this run"
source: { url: "research/spikes/s01-input-tables/output.json", doi: "", title: "planning spike S01", locator: "reed_table_max_abs_diff_mm", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-007]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:06Z
---
Arithmetic only. The plan does not model reed geometry: each reed is specified by its natural frequency, Q, effective areas and offsets.

Input-file verdict: supported. Load-bearing: no. Informs: nothing directly.

All sources: planning spike S01 (reed_table_max_abs_diff_mm); round-1 worker file (sources read at snippet level; see that file) (claims A1, A2).
