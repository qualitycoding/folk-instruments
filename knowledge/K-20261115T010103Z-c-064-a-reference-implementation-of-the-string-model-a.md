---
id: K-20261115T010103Z-c-064-a-reference-implementation-of-the-string-model-a
statement: "A reference implementation of the string model as decided (D-060 to D-064: greedy pairing, bridge admittance from the body modes capped at a bridge loss factor of 8e-3, pitch compensation, exact matrix-exponential steps, body modes driven by the bridge force) puts every fretted note of the f-hole mandolin within 0.51 cents of its target; on the bowl-back the E pair decays at -95.6 dB/s early and -22.5 dB/s late while one string alone decays at -56.6 dB/s throughout; a 4-cent mistuning on a nearly rigid bridge beats at 1.534 Hz; a tap rings the first three f-hole body modes within 11 dB of each other. A stagger of 0.84 ms between the strokes on the two strings starts the E strings almost in antiphase and removes the two-stage decay; 0.105 ms keeps it."
status: current
supersedes: []
tags: [subject:plucked-string-modelling, phase:research]
applies_to_version: "this run"
source: { url: "research/spikes/s17-string-body/output.json", doi: "", title: "planning spike S17", locator: "all fields", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-064]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:01:03Z
---
The spike is the reference for step S-240. It checks the frozen tests' measurements on the spike's own output, not on the product.

Input-file verdict: not-in-input. Load-bearing: yes. Informs: D-060, D-061, D-062, D-063, D-064, T-140, T-143, T-144, T-146, T-154.

All sources: planning spike S17 (all fields); A necessary condition for double-decay envelopes in stringed instruments, J. Acoust. Soc. Am. 150(6), 4375-4384 (sections I and III (the physics the model follows)).
