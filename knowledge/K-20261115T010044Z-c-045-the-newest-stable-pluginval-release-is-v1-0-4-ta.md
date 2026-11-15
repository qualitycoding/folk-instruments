---
id: K-20261115T010044Z-c-045-the-newest-stable-pluginval-release-is-v1-0-4-ta
statement: "The newest stable pluginval release is v1.0.4 (tag commit ed19c2c16b57a6d94db391bea3ef4a80b769d5bf); the only 2.x tags are betas (v2.0.0-beta1 to beta3). Its Linux, macOS and Windows archives have SHA-256 c01c49d8063965c4c2dea8324468336768f5c9139e0b1caebde14c2400b55352, 3c4c533bda0c5059eea3ddaea752d757ee2025041f0f47e6bcb0e87f6082b29f and c08e61ce3b96db41636f8ec7e76f4c7e2c13ebdac7fa1b5a1f52b4f32ec715ab; the command line takes --strictness-level 1 to 10 and --timeout-ms, validates in process without a flag, and can exit 0 without having run every test."
status: current
supersedes: []
tags: [subject:pluginval, phase:research]
applies_to_version: "tag v1.0.4, commit ed19c2c16b57a6d94db391bea3ef4a80b769d5bf"
source: { url: "https://github.com/Tracktion/pluginval", doi: "", title: "pluginval source at v1.0.4: Source/CommandLine.cpp", locator: "Source/CommandLine.cpp lines 98, 147, 165, 357 to 361; tag list", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-045]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:44Z
---
Hashes and flags come from verified knowledge items at the same version; the release assets cannot be downloaded from the planning sandbox, so the implementer's first use re-checks the hash (it gates). v1.0.4 dates from December 2024; no newer stable release exists.

Input-file verdict: not-in-input. Load-bearing: yes. Informs: D-082, T-300.

All sources: pluginval source at v1.0.4: Source/CommandLine.cpp (Source/CommandLine.cpp lines 98, 147, 165, 357 to 361; tag list); knowledge item from the store (and K-...c-009, c-010, c-012 to c-015, K-20261104T005300Z: archive hashes and CLI read from the v1.0.4 release in earlier runs).
