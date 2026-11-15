# Tests

Everything listed in `FROZEN_MANIFEST.sha256` is frozen: do not modify, skip, weaken or mark as expected-failure
(`HANDOFF.md`, section 3). Verify with `sha256sum -c tests/FROZEN_MANIFEST.sha256` from the repository root.
`requirements.txt` and this file are not frozen (a dependency may move under rule DR-08). How to run the suites:
`plan/ENVIRONMENT.md`, section 3. What each test proves: `plan/TRACEABILITY.md`.
