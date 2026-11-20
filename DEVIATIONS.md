# Deviations

- 2026-11-19 S-000: the implementation branch is `ccr-f45525dd-81yib1` (required by the session's rules) instead of `impl-gen-20261114T004707Z-folk-instruments-vst`; it was cut from the generation branch head. Reason: this session may push only to that branch.
- 2026-11-20 S-210: `.github/workflows/gate-evidence.yml` is copied unchanged but triggers only on `impl-**` branches, so it cannot run from `ccr-f45525dd-81yib1`. The G-P1 demos were rendered locally by `tools/build_evidence.py` and delivered with the session's file-sending tool instead of the `evidence/G-P1` branch.
