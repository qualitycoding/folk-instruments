---
id: K-20261115T010030Z-c-031-modal-synthesis-a-bank-of-exponentially-decaying
statement: "Modal synthesis (a bank of exponentially decaying sinusoidal modes whose complex frequencies come from the coupled string, bridge and body system) reproduces a linear coupled model exactly whenever the system matrix can be diagonalised; near the locking boundary of a coupled pair the modal amplitudes become large and cancel, and exactly at it the response contains terms the modal sum cannot represent."
status: current
supersedes: []
tags: [subject:plucked-string-modelling, phase:research]
applies_to_version: "this run"
source: { url: "research/spikes/s04-coupled-pair/output.json", doi: "", title: "planning spike S04", locator: "envelope computed from the eigen-decomposition", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-031]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:30Z
---
Consequence (D-062): each coupled pair is integrated as a 2 x 2 block in the time domain, not expanded into its two modes.

Input-file verdict: not-in-input. Load-bearing: yes. Informs: D-060, D-062.

All sources: planning spike S04 (envelope computed from the eigen-decomposition); knowledge item from the store (resonator form); planning spike S09R (comparison with a matrix exponential: agreement to 6e-13 from 1 to 8 cents; condition number 45 near 3.46 cents).
