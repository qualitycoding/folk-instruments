# GATE G-P1 (round 1 of 2)
- Status: OPEN
- Opened: 2026-11-20, commit a07c0cf (plus the commit that adds this file), step S-210
- Blocks: S-220, S-230
- Continues meanwhile: S-212, S-101, S-240, S-250, S-REF
## Evidence
- Delivery: the `gate-evidence` workflow only runs for branches named `impl-**`; this session may push only to `ccr-f45525dd-81yib1`, so no `evidence/G-P1` branch was built (deviation logged). The 13 harmonica demos were rendered locally with `tools/build_evidence.py` and sent as one zip, `folk-harmonica-G-P1-demos.zip` (demos, MANIFEST.json, SHA256SUMS, ATTRIBUTION.md). All demos are product-rendered; references: 0 redistributable used, 0 private used.
- Demos to listen to first: `harmonica-01-melody`, `harmonica-04-dynamics`, `harmonica-08-bend`, `harmonica-10-chromatic-on-diatonic`, `harmonica-203-variant`.
- Frozen tests passing for the harmonica: all 88 pytest cases selected by `-k harmonica` (T-100 to T-109, T-110 to T-114 and the common tests that name the harmonica); C++ T-001 to T-004 (layout) and T-008, T-014, T-016.
- `folk-perf` PERF lines: not available; `folk-perf` needs all five instruments and still fails against the unimplemented ones. Single-reed cost measured instead: about 30 ns per reed sample (`reed_probe --time`, above the 20 ns early-warning budget; T-013 on CI decides).
## Questions
1. Does this sound like the instrument? If not, what is wrong, in your own words (for example: too clean, too bright, synthetic attack, wrong pitch, lifeless sustain)?
2. Which demo is the weakest?
3. May the remaining instruments of this family be built on this sound engine as it is?
4. Is the scope still right: five instruments with the variants listed (D-020, D-030, D-040, D-070, D-073), VST3 and Standalone on Windows, macOS and Linux, nothing released (A-003, A-018)? Answer with `proceed-with-rescope: <text>` to change it.
## Allowed responses
`proceed`; `iterate: <notes>`; `proceed-with-rescope: <text>`; `stop`; `override-round-limit: <reason>` (only after round 2).
## Response
- Response:
- Given by:
- Verbatim:
- Recorded by:
