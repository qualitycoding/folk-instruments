---
id: K-20261115T010000Z-c-001-the-minimal-free-reed-model-one-mode-reed-equati
statement: "The minimal free-reed model (one-mode reed equation z'' + (w0/Q) z' + w0^2 z = mu*dp with mu = Sr/M, pumped flow Sr*z', jet flow alpha*Su(h)*vj with dp = rho*vj^2/2, an upstream volume V1 obeying (V1/c0^2) dp1/dt = rho*(u0 - u) and an upstream pipe obeying p1 = p2 + rho*(L2/S2) du/dt) self-oscillates when integrated with a semi-implicit Euler scheme at 44.1 to 705.6 kHz (converged; a fourth-order Runge-Kutta run agrees), using the published reed parameters (Lr 12.95 mm, Wr 2.1 mm, er 110 um, es 900 um, rest offset 528 um, hmin 50 um, fr 444 Hz, K 47.9 N/m, Q 95; S0 30 mm2, S1 800 mm2, L2 20 mm, S2 25 mm2)."
status: current
supersedes: []
tags: [subject:free-reed-modelling, phase:research]
applies_to_version: "arXiv v1, 2024-01 (paper 2007)"
source: { url: "https://arxiv.org/abs/2401.01606", doi: "", title: "A proposal for a minimal model of free reeds (Acta Acustica united with Acustica 93 (2007) 122-144)", locator: "section 2.1 eq. (4); section 2.2 eqs (5)-(7); section 3.1 equation list; Tables 2 and 3; appendix 5.2 and 5.4", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-001]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:00Z
---
The spike used the Debut/Millot useful-section law, not the refined law of section 2.3.2. The Table 2 parameters were measured on a (+,-) reed and are borrowed here for the (-,+) arrangement; the source says the two reeds of a channel differ. The sign convention of the rest offset differs between the source's two reed types; the spike uses its own coordinate (D-010).

Input-file verdict: not-in-input. Load-bearing: yes. Informs: D-010, D-011, T-100, T-101.

All sources: A proposal for a minimal model of free reeds (Acta Acustica united with Acustica 93 (2007) 122-144) (section 2.1 eq. (4); section 2.2 eqs (5)-(7); section 3.1 equation list; Tables 2 and 3; appendix 5.2 and 5.4); planning spike S03 (runs v0 = 1.5 to 3.5 m/s); planning spike S09R (sample-rate sweep and RK4 comparison).
