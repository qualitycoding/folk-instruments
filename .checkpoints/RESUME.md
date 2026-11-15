# Resume note (planning agent)

This note is for the PLANNING agent. An implementing agent starts at `HANDOFF.md` and step `S-000`, not here.

**Where things stand.** Phases 0 to 2 are complete (six research rounds, ended at the round limit; 65 claims; tests frozen and red-verified). Phase 3 documents exist. Cold read pass 1 (dry run and mechanical) produced 38 + 6 items; all were resolved by amending the plan, with two new planning spikes: S17 (the reference implementation of the string and body model) and S18 (melodion plenum and body filters). The source register has had nine review passes; each found discrepancies, all corrected; it is not yet marked `verified`.

**Next action.** Cold read pass 2 with new agents on a clean clone (`state.json` `in_flight`). Resolve its items; repeat to at most 5 passes. Then a register review pass that finds nothing (then set the register's `confidence: verified`), Phase 4 pre-mortem, 4.7 assumption audit, Phase 5 final check and push.

**Open questions.** None for the owner.

**Do not redo.** Research is closed at round 6. The intake batch is used. `main` exists; do not push to it. Spikes S17 and S18 are current; S08 (the stand-in renderer) predates S17 and is a check of the tests only.

**Human answers still to apply.** None.
