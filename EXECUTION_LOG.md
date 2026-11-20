2026-11-19T20:31:32Z S-000 1 pass 82a6dec environment ephemeral (worker restarted); branch deviation logged
2026-11-19T20:31:32Z S-002 1 pass 82a6dec freeze OK; 27/27, 2/2, 1/1 red; pytest 43 pass 302 fail
2026-11-19T20:32:44Z S-101 1 blocked 0a5ff15 strings.cpp written; T-006 lock check frozen-test invalid, see TEST_CHALLENGE.md
2026-11-19T20:33:56Z S-100 1 pass d7ef528 tables, gen_presets.py, tuning.cpp; T-001..T-004,T-007 green (params/reeds/gains/bodies json come in later steps)
2026-11-19T20:35:35Z S-110 1 pass 4f4c29b engine base (silent), params.json, folk-render; T-008,T-014,T-016,T-009 oor, T161 green
2026-11-19T20:37:10Z S-200 1 pass 30f884e reed.cpp, reed_probe, calibrate_gains.py; 444 Hz 400 Pa 48k: -23.05 cents, 4.632 x0 (spike -23.1, 4.63); undriven decays; ns_per_reed_sample 29.9 (above 20 ns early warning, A-009/R-147)
2026-11-19T20:38:04Z S-201 1 pass d38d9ca reed-check.csv 120 rows 0 failing (C=110); reeds.json offsets -24.31..-23.71 cents; ns_per_reed_sample 30.1 (> 20 ns early warning vs A-009; T-013 on CI is the gate)
2026-11-19T20:41:10Z S-210 1 partial 2618acd harmonica instrument + ReedEngine; all 88 harmonica pytest cases pass; G_out 0.0642117 (peak -11.996 dBFS); gate tooling (evidence_guard, fetch_references, build_evidence, workflow) and G-P1 not done
2026-11-19T20:41:35Z S-210 2 partial 2ef5ee8 tools/evidence_guard.py done (T-210 green). Not done: fetch_references.py (T-211), build_evidence.py, gate-evidence workflow, GATE-G-P1.md. Session stopped here.
2026-11-20T15:06:17Z S-101 2 pass a65ea0d T-006 amended by D-096 (8454145) merged; CPP T-005*, T-006* green; manifest OK
2026-11-20T15:08:26Z S-210 3 pass a07c0cf fetch_references (T-211), build_evidence, workflow copied, references index/archives; G-P1 OPEN (demos delivered by file, not evidence branch)
