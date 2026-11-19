# Phase 4 convergence record

Rigour `standard`: at most 5 pre-mortem rounds (protocol 4.5). Each round was run by a fresh-context agent that did not write the plan, on a clean clone; reports are `premortem/round-1.md` to `round-5.md`.

| Round | Findings (new + residual, counted) | Critical | High (expected or plausible) | After the round |
|---|---|---|---|---|
| 1 | 31 new, 3 residual | 7 | 7 | every Critical and High mitigated; tests re-frozen (T-016, T-211, T-302 cases, T-303, T-304) |
| 2 | 8 new, 7 residual | 2 | 3 | all mitigated; re-frozen (T-092, TinySOL hash list, stronger T-302 program case) |
| 3 | 7 new, 3 residual | 0 | 3 | all mitigated; checker anchored |
| 4 | 7 new, 2 residual | 0 | 2 | all mitigated; named canary |
| 5 | 6 new, 4 residual | 0 | 3 (plus 1 High at remote) | all mitigated after the round; scope canary; checker restricted to `race_top:` |

A cold-read re-run (protocol 4.4) followed every round's amendments; their records are `research/coldread/coldread-6*.json` to `coldread-9.json`, and their findings were resolved.

**Outcome.** The loop did not reach a round with no counted finding: round 5, the last permitted, still found three High risks at `plausible` likelihood. Each was mitigated after the round (two of them had already been fixed on the branch before the round's report arrived, because the round ran on the previous commit). No Critical risk and no High risk at `expected` or `plausible` likelihood is open in `premortem/RISK_REGISTER.md`. Protocol 4.6 applies only when counted risks remain after the last round; none remains, so the plan is not marked `BLOCKED`. The owner should know that the mitigations added after round 5 (R-088 to R-095) were checked by a cold-read re-run and, where executable, by running them in the planning sandbox (the three ThreadSanitizer canaries, the suppression checker, the exclusion grep), but not by a sixth pre-mortem round. This is stated again in the Phase 5 report.

**After the assumption audit (protocol 4.7.4).** The audit falsified three premises and changed the plan (`premortem/ASSUMPTION_AUDIT.md`). As 4.7.4 requires, the changed steps then had one cold-read re-run with a re-audit of the corrected premises (`research/coldread/coldread-11.json`: all three confirmed; its items resolved) and one pre-mortem round limited to the changed steps (`premortem/round-6.md`). That round is the one the audit rule mandates, not a sixth round of the 4.5 loop, whose limit of five was reached before the audit.

Register by severity and status (133 rows, including R-098 to R-133 from the assumption audit):

| Severity | Status | Count |
|---|---|---|
| Critical | mitigated | 11 |
| High | accepted | 1 |
| High | mitigated | 26 |
| Low | accepted | 31 |
| Low | mitigated | 6 |
| Low | speculative | 1 |
| Medium | accepted | 19 |
| Medium | mitigated | 37 |
| Medium | speculative | 1 |
