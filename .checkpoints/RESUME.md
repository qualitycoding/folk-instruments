# Resume note (planning agent)

This note is for the PLANNING agent. An implementing agent starts at `HANDOFF.md` and step `S-000`, not here.

**Where things stand.** Phases 0 to 2 are complete (six research rounds, ended at the round limit; 65 claims; tests frozen and red-verified). Phase 3 documents exist. Cold reads 1 to 3 (dry run plus mechanical each) produced 38 + 6, 31 + 3 and 33 + 4 items; pass 4 found 19 + 9; all were resolved by amending the plan (records in `research/coldread/`). The source register passed its twelfth review clean and is marked `verified`.

**Next action.** None. Planning is complete (status READY, Phase 5 done). Execution is not to be started by the planner; an implementing agent starts at `HANDOFF.md` and `S-000` on a new branch `impl-<run_id>`.

**Open questions.** None for the owner.

**Do not redo.** `research/tools/build_records.py` rebuilds `knowledge/` and deletes items it did not generate (the three K-20261119 items); after running it, restore them with `git checkout -- knowledge/K-20261119*`. Research is closed at round 6. The intake batch is used. `main` exists; do not push to it. Spikes S17 and S18 are current; S08 (the stand-in renderer) predates S17 and is a check of the tests only.

**Human answers still to apply.** None.
