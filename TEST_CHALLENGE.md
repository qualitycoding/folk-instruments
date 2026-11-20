# TEST_CHALLENGE: T-006 "strongly coupled pair mistuned by 3 cents locks" (tests/cpp/test_strings.cpp:70)

- Item: the `CHECK(m.omega[0].imag() > 10.0 * m.omega[1].imag())` in the third T-006 test case. Step affected: S-101 (all other T-005/T-006 checks pass: 15 of 16 assertions in the two cases).
- Evidence: Omega = [[w1(1+i eta/2)+z, z],[z, w2(1+i eta/2)+z]] with w1 = 2 pi 660, w2 = w1 2^(3/1200), eta = 2e-4, z = i 2 660 pi 1e-3 = 4.147 i (the convention fixed by the first T-006 case and by `research/spikes/s04-coupled-pair/pair.py`). The half-difference of the diagonal is delta = (w2 - w1)/2 = 3.59 rad/s, so the eigenvalues are mean ± sqrt(delta^2 + z^2) = 4.56 i ± 2.07 i. numpy.linalg.eig on the same matrix gives 4150.499 + 6.627i and 4150.498 + 2.497i. The slow mode's decay (2.497) is not below a tenth of the fast one's (6.627); the check would need 6.627 > 24.97.
- Reasoning: coupling |z| = 4.15 rad/s is only 1.15 times the detuning 3.59 rad/s, so the pair is locked in frequency (the split check at line 69 passes: Re parts equal) but the modes are only partly separated. A 10:1 ratio needs delta of about 1.4 rad/s (about 1.1 cents) at this coupling, or a coupling of about 9 rad/s at 3 cents. The solver is an exact closed form and agrees with numpy, so no implementation can satisfy the check.
- Proposed fix: change the mistuning to 1 cent (delta 1.2 rad/s: expected imag parts 6.6+ and about 0.7... re-derive with ka.py), or lower the factor from 10 to 2.5 (6.627 > 2.5 x 2.497 = 6.24), or raise the coupling to pi * 2.2e-3. The planning agent should pick and recompute against `research/spikes/s06-known-answers/ka.py`.

## Resolution
Resolved by the planner as D-096 (commit 8454145); merged into this branch, frozen manifest verified, T-005 and T-006 pass.
