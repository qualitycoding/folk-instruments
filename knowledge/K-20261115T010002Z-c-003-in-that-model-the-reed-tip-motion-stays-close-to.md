---
id: K-20261115T010002Z-c-003-in-that-model-the-reed-tip-motion-stays-close-to
statement: "In that model the reed tip motion stays close to sinusoidal (second harmonic of the displacement between -53 and -43 dB) while the total volume flow through the reed (jet plus pumped flow) carries strong harmonics that grow with the supply (second harmonic of the flow from -18.5 dB to -8.9 dB re the fundamental), so in this model the harmonic content of the source flow comes from the nonlinear flow law, not from the reed motion."
status: current
supersedes: []
tags: [subject:free-reed-modelling, phase:research]
applies_to_version: "this run"
source: { url: "research/spikes/s03-reed-minimal-model/output.json", doi: "", title: "planning spike S03", locator: "flow_harmonics_dB, reed_h2_dB", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-003]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:02Z
---
The spike computes no radiated sound; a monopole radiates as the time derivative of the flow, which raises the harmonics further.

Input-file verdict: supported. Load-bearing: yes. Informs: D-011, T-104.

All sources: planning spike S03 (flow_harmonics_dB, reed_h2_dB); A proposal for a minimal model of free reeds (Acta Acustica united with Acustica 93 (2007) 122-144) (section 2.1 first paragraph; section 3.3).
