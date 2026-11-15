# Resume note (planning agent)

This note is for the PLANNING agent. An implementing agent starts at `HANDOFF.md` and step `S-000`, not here.

**Where things stand.** Phases 0 to 2 are complete (six research rounds, ended at the round limit; 65 claims; tests frozen and red-verified). Phase 3 documents exist. Cold reads 1 to 3 (dry run plus mechanical each) produced 38 + 6, 31 + 3 and 33 + 4 items; pass 4 found 19 + 9; all were resolved by amending the plan (records in `research/coldread/`). The source register passed its twelfth review clean and is marked `verified`.

**Next action.** Pre-mortem round 1 is done (35 findings: 7 Critical, 8 High; all Critical and High mitigated; tests re-frozen with T-016, T-211, T-303, T-304 and three T-302 cases, red-verified; register R-017 to R-050). The protocol re-runs the cold read after a plan change: run one cold read (dry run on the changed parts plus mechanical) on a clean clone, resolve it, then pre-mortem round 2 with the register as input. At most 5 pre-mortem rounds; then the 4.7 audit and Phase 5.

**Open questions.** None for the owner.

**Do not redo.** Research is closed at round 6. The intake batch is used. `main` exists; do not push to it. Spikes S17 and S18 are current; S08 (the stand-in renderer) predates S17 and is a check of the tests only.

**Human answers still to apply.** None.
