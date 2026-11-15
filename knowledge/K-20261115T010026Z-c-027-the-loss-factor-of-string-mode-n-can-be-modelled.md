---
id: K-20261115T010026Z-c-027-the-loss-factor-of-string-mode-n-can-be-modelled
statement: "The loss factor of string mode n can be modelled as the sum of a bridge term eta_b = 2*Re(Y)/(pi*n*Y0) with Y0 = 1/sqrt(T*m), an air term eta_air = (rho_a/rho)*(2*sqrt(2)*M + 1)/M^2 with M = (d/4)*sqrt(2*pi*f_n/nu_a), rho_a = 1.2 kg/m3, nu_a = 1.5e-5 m2/s, and a bending term eta_bend = E*pi^2*d^2*n^2*eta_E/(64*rho*L^4*f1^2 + E*pi^2*d^2*n^2); air damping dominates low modes and bending damping high modes."
status: current
supersedes: []
tags: [subject:plucked-string-modelling, phase:research]
applies_to_version: "2021"
source: { url: "https://euphonics.org/wp-content/uploads/2022/03/Double_decays_JASA.pdf", doi: "10.1121/10.0009012", title: "A necessary condition for double-decay envelopes in stringed instruments, J. Acoust. Soc. Am. 150(6), 4375-4384", locator: "section II A, eqs (1)-(4)", accessed: "2026-11-14", tier: 1 }
confidence: single-source
derived_from: [C-027]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:26Z
---
One Tier 1 source, read in full; its air term is quoted from Fletcher and Rossing (1998). The tests check the implementation against these formulas and check qualitative ordering; calibration to recordings is a later step. Limits stated in the source: the bridge term holds for |Y/Y0| much smaller than 1; for wound strings an effective diameter and density must be chosen and friction between windings adds loss.

Input-file verdict: not-in-input. Load-bearing: yes. Informs: D-061, T-131.

All sources: A necessary condition for double-decay envelopes in stringed instruments, J. Acoust. Soc. Am. 150(6), 4375-4384 (section II A, eqs (1)-(4)).
