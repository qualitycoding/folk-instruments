---
id: K-20261115T010001Z-c-002-in-that-model-the-onset-from-rest-needs-a-supply
statement: "In that model the onset from rest needs a supply between 1.0 and 1.5 m/s (through 30 mm2), but a reed that is already sounding keeps sounding at 1.0 m/s and below (hysteresis, the inverse bifurcation the source reports); the sounding frequency lies about 13 cents below the reed's natural frequency (440.7 Hz against 444 Hz) and falls slightly as the supply rises (-13.0 to -13.8 cents from 1.5 to 3.5 m/s); the tip amplitude grows with supply (1.3 to 2.4 mm); a sudden large supply from rest (4 m/s within 50 ms) pushes the reed through the plate without starting it, while a gradual rise from an established sound keeps it sounding to at least 6 m/s."
status: current
supersedes: []
tags: [subject:free-reed-modelling, phase:research]
applies_to_version: "this run"
source: { url: "research/spikes/s03-reed-minimal-model/output.json", doi: "", title: "planning spike S03", locator: "runs list", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-002]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:01Z
---
The input file says pitch 'drops flat under excessive airflow'; the model shows a small fall and then choking. Measured cents-per-pascal figures for real reeds were not found.

Input-file verdict: partly-supported. Load-bearing: yes. Informs: D-011, D-016, T-101, T-102, T-103.

All sources: planning spike S03 (runs list); A proposal for a minimal model of free reeds (Acta Acustica united with Acustica 93 (2007) 122-144) (section 3.2, figures 10 to 17 (qualitative agreement)); planning spike S09R (supply lowered to 1.0 and 0.8 m/s after sounding; gradual rise to 6 m/s); A proposal for a minimal model of free reeds (Acta Acustica united with Acustica 93 (2007) 122-144) (section 3.5).
