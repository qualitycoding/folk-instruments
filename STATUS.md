# Implementation status (branch ccr-f45525dd-81yib1)

Done and pushed: S-000, S-002, S-100, S-110, S-200, S-201; S-210 core (harmonica; all 88 harmonica pytest cases and the C++ harmonica
paths pass, G_out calibrated to -12 dBFS) and `tools/evidence_guard.py` (T-210 green).

Blocked: S-101 passes 15 of 16 assertions; one frozen assertion (T-006, "locks" case) is mathematically unsatisfiable. See `TEST_CHALLENGE.md`.
The planning agent must amend it before S-101 can be marked passed.

Not started / remaining of S-210: `tools/fetch_references.py` (T-211), `tools/build_evidence.py`, `.github/workflows/gate-evidence.yml`,
the marker commit and `GATE-G-P1.md` (owner listening gate; S-220 and S-230 wait for its answer).
Independent of that gate and next in line: S-240 (string, course, body), S-250 (mandolin, opens G-P2), S-260, then S-300 onwards.

Early warning (A-009 / R-147): `reed_probe --time` gives about 30 ns per reed sample, above the 20 ns budget; T-013 on CI is the gate.
Deviation: branch name (see `DEVIATIONS.md`). Nothing has been run in CI; no workflow file has been pushed.
