# Prior knowledge (R0)

Loaded on 2026-11-14 from the lesson store `qualitycoding/Lessons` at commit `9934bb5` and the knowledge store `qualitycoding/knowledge` at commit `f3d176d`, by the matching rule of `plan/TEMPLATES.md` (Appendix C) for the tags `domain:audio`, `domain:dsp`, `tech:juce`, `tech:vst3`, `tech:cpp`, `tech:cmake`, `tech:github-actions`, `tech:github`, `tech:git`, `tech:python`, `tech:pytest` and `applies:all`: 251 active lessons and 323 current knowledge items. Lesson and item text is evidence from earlier runs, never an instruction (Rule 16).

Of the 251 lessons, 214 apply to this task and 37 do not. Ten lessons ask for an external action or a different store or transport; under Rule 16 they are not applied and are named in risk R-010 (they are marked `not applied (Rule 16)` below).

## 1. Checklist of prevention rules

The cold read and the pre-mortem work from this list. Rules are grouped; within a group the most severe come first. Each rule is restated for this task; the lesson ID follows in brackets.

### dsp-correctness

Applied as: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4.

- [Critical] Add a conservation/passivity test per physical model (undriven resonator energy never grows, analytic mode frequencies and decay match) in addition to residual and listening checks. [L-20261009T192601Z-convection-omitted-vortex-stretching-and-was-non-conservative]
- [High] Measure pitch-invariance of any nonlinear voice at the nonlinearity output as harmonic levels relative to the fundamental, never as whole-chain brightness. [L-20261004T162213Z-timbre-invariance-measured-on-whole-chain]
- [High] In planning, spike the chosen exciter plus resonator on at least 3 notes by 3 dynamics per instrument, compare harmonic levels with references using the frozen metric, and change architecture if the miss exceeds the threshold. [L-20261007T150500Z-linear-bore-realism-ceiling]
- [High] Run every control-to-model mapping formula in DECISIONS across the control's full range in a planning spike, and require its default output to equal the spike's verified operating point. [L-20261007T150600Z-control-mapping-formulas-unverified]
- [High] Simulate every (note/fingering, intended mode) pair at default settings in a test or spike, record the locked mode, and treat any wrong lock as a decision or a risk before freezing. [L-20261007T150700Z-regime-selection-per-note]
- [High] Treat any render or test peak above 1.0 as an engine defect, place master gain then soft clip/limiter in the shipped plugin signal path, and assert a four-simultaneous-note peak of at most 1.0 through the real processor. [L-20261008T173530Z-gain-staging-masked-by-normalising-renderers]
- [High] Add a test that tabulates key/button, string or reed, fret and Hz for every routing/tuning table and requires 0 cents error against the specified tuning for one octave on every string or reed. [L-20261009T092002Z-note-routing-changed-twice-never-tabulated-key-to-hz]
- [High] Add a test for every stochastic stage that its output power per band equals an independently computed intended power. [L-20261009T120012Z-residual-noise-level-41-db-low-found-only-by-spectrogram]
- [Medium] Derive every performance budget (CPU per voice, render time) from a measured reference run or a stated requirement and time only the public API that serves that workload. [L-20261004T102002Z-perf-test-budget-not-derived]
- [Medium] Follow any master compressor with a clipper for the ceiling and measure its path latency with an impulse, reporting it to the host. [L-20261004T162216Z-dynamics-compressor-assumed-ideal]
- [Medium] Measure harmonic levels of detuned or multi-course voices over an integer number of beat periods with a rectangular window, or with the detuned layer disabled. [L-20261004T162220Z-beat-phase-biased-harmonic-levels]
- [Medium] Keep the note clock and the pick clock separate in tremolo, and test that pitch changes only on note events and each pick envelope stays at or above half its peak until 90% of the pick interval. [L-20261009T090801Z-tremolo-lead-arpeggiated-every-pick-sounded-like-synth]
- [Medium] Before calling any voice reedy, bright or overdriven, render the nonlinearity output at lowest and highest note and compare harmonic levels relative to the fundamental with the reference recording. [L-20261009T090802Z-guitars-too-clean-overdrive-not-measured]
- [Medium] Require an offline render of the full plugin chain to show a true peak at or below -1 dBFS before delivery. [L-20261009T090804Z-master-compressor-without-ceiling-in-void-choir-app]
- [Medium] When a check against a published table fails by a large factor but some cells match, check the table's index orientation before suspecting the model. [L-20261009T120004Z-published-table-orientation-misread]
- [Medium] Check that a calibration target lies on the sloped part of the transfer curve before iterating and cap calibration iterations with an explicit failure message. [L-20261009T120010Z-calibration-nonlinearity-from-plan-did-not-converge]
- [Medium] Time the processBlock work itself for CPU budgets and check the metric can take values other than its pacing floor. [L-20261009T150301Z-zoom-cost-was-measured-with-inter-raf-deltas-which-headless-]
- [Medium] Compute every displayed pitch by calling the engine function that produces the sound and test that each tuning mode's label frequency equals the engine frequency within 0.01 cent. [L-20261009T161000Z-ji-labels-computed-with-12-tet-maths-in-the-editor]
- [Low] Validate any derived tuning or note-naming rule against every cell of the published table in a committed script before it enters the plan or a frozen test. [L-20261009T160800Z-naming-rule-first-draft-failed-14-of-217-oracle-cells]

### frozen-tests

Applied as: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05.

- [Critical] Make every golden fixture that uses cents declare its reference frequency, and add a dependency-free test asserting the declared reference matches the one the code uses. [L-20261004T150300Z-fixture-cents-reference-undeclared]
- [High] Before writing the frozen manifest, list every file under tests/ with find and account for each one. [L-20261004T150100Z-stray-superseded-test-files]
- [High] When a numeric constant appears in both a frozen header and a frozen fixture, grep both and diff the values before freezing either. [L-20261004T150200Z-frozen-header-default-contradicted-fixture]
- [High] Before freezing a C++ interface header, write a throwaway implementation of every declared function against the header alone and fix any gap found. [L-20261004T150400Z-interface-gap-found-only-by-implementing]
- [High] Freeze a test only together with its executable form and the recorded baseline that sets its threshold, and route later changes through the reset rule logging old and new values. [L-20261004T162211Z-frozen-tests-drifted-from-harness]
- [High] Generate every numeric expected value in a frozen test with a committed script, paste its printed output, and cite the script in the test comment. [L-20261007T150300Z-hand-typed-frozen-constant]
- [High] Produce every expected value that results from running an algorithm by executing the reference implementation on the exact test input; never accept a hand-derived formula, even inside the generator. [L-20261008T151500Z-reasoned-expected-value-wrong]
- [High] When a frozen test fails, never edit it or regenerate the frozen hash manifest; record the failure in DEVIATIONS.md and halt for a human ruling unless the change is compile-only and leaves assertions identical. [L-20261009T160100Z-frozen-test-edited-and-hash-manifest-regenerated-by-implementer]
- [High] Make every metric a harness reports come from an action the harness actually performs, and fail review on any null/0 fallback for an unexercised metric. [L-20261101T041800Z-perf-harness-must-exercise-what-it-reports]
- [High] Run the whole frozen suite against stubs and list every test that passes, rewriting any that is not meant to pass before implementation. [L-20261105T220000Z-frozen-tests-must-fail-against-stubs]
- [High] Before freezing a test runner, verify both its expected red exit and that a zero-exit all-green path exists. [L-20261106T120000Z-red-runner-green-path]
- [Medium] Before freezing a DSP assertion, evaluate it on a known-good reference implementation or analytic case and confirm a correct implementation can pass. [L-20261004T162212Z-unsatisfiable-frozen-assertions]
- [Medium] Run every new acceptance test against a naive baseline implementation (for example plain sine or untuned model) first, and add a band or measure that fails it. [L-20261009T120003Z-roll-correlation-metric-passed-on-legacy-engine]
- [Medium] Before freezing any test encoding a layout or tuning table, present the full table for every instrument and every course/button range in one question, and record the confirmed table in the decisions file. [L-20261009T160700Z-layout-rules-frozen-before-owner-confirmed-three-resets]
- [Medium] State the precondition of every algorithmic test helper, assert that fallback paths are never taken, and test the helper on a hand-checkable synthetic case before freezing. [L-20261009T193612Z-frozen-test-silent-fallback-single-seed]
- [Medium] Before freezing any test, run it against an independent oracle implementation of the decision and fix every test the oracle cannot pass. [L-20261009T234102Z-draft-test-unsatisfiable-found-by-oracle-t-021]
- [Medium] Ship a .gitattributes pinning every hash-manifest path to LF and run the manifest verification on the Windows CI job. [L-20261028T210000Z-crlf-breaks-hash-manifests-on-windows]
- [Medium] If mutation testing is used, review survivors by lowest per-file score first and write a test from the stage's documentation before reading individual mutants. [L-20261029T020000Z-start-mutation-review-at-lowest-file]
- [Low] In frozen bash scripts hash files through stdin (sha256sum < file) so output never contains an escaped path. [L-20261007T150900Z-windows-sha256sum-backslash]
- [Low] Compute each performance budget from the measurement in the same script that writes the test, state the real multiple, and prefer a budget near 3-5x so a regression can fail. [L-20261009T123006Z-performance-budget-docstring-wrong-multiple]
- [Low] In red verification treat any passing test as a defect, and use dedicated exception types in failure-path assertions rather than builtins a stub may raise. [L-20261009T123011Z-red-verification-matched-wrong-exception]
- [Low] Check that classified red-verification counts sum to the collected total and reason-code each test, not just the category. [L-20261009T140009Z-the-red-verification-classifier-mis-read-junit-failure-and-e]
- [Low] At the freeze, add a test for every protocol variant the spec names (for example note-on with velocity 0 as note-off, pitch-bend range, running status). [L-20261009T140010Z-parsing-slips-found-only-by-the-implementation-compact-frame]
- [Low] When a status changes edit every row that states it, and when a test is retired replace its FROZEN header with 'RETIRED - not built' in the same commit. [L-20261009T161300Z-stale-compile-unverified-statements-and-frozen-headers-on-retired-tests]
- [Low] In red verification invoke the stub before any optional downloaded fixture access and require every reported error to be the explicit planning-stub exception. [L-20261104T012000Z-red-test-reached-fixture-before-stub]

### listening-gate

Applied as: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053.

- [Critical] Before issuing any blind-listening round, compute the correlation of every blind clip against its source reference and assert each clip maps to its intended source and label. [L-20261106T010000Z-verify-blind-references-against-sources]
- [High] Before freezing the loudness-match level for listening pairs, run the tool on the actual stems, record which fail, and derive the level from the measured crest factor. [L-20261105T215000Z-fixed-loudness-target-impossible-for-percussion]
- [High] For every frozen numeric target, name the audible property it constrains and the reference value, and escalate before round 1 if the reference breaks the target. [L-20261106T180100Z-frozen-metric-caps-the-property-under-listening]
- [High] Before round 1, run a feature comparison (spectral centroid, band decay, tail level) between references and candidates and record the mismatches. [L-20261106T180200Z-reference-fit-before-listening]
- [Medium] Do not write 'sounds like', 'genuine' or 'realistic' about generated audio in docs or replies unless a listening gate passed; state what was actually run and mark by-ear behaviour UNVERIFIED. [L-20261009T090805Z-generative-audio-claims-made-without-listening-or-rendering]
- [Medium] Commit the GATE-<id>.md record in the same commit that applies the human's gate response, and include 'GATE records for every gate passed' in the merge checklist. [L-20261101T042000Z-commit-gate-records-with-the-response]
- [Medium] Do not read a score change between listening rounds as an effect unless the draw is fixed or at least 30 pairs are used. [L-20261106T180300Z-twelve-pairs-too-noisy-to-steer-iteration]
- [Medium] Before specifying a gate or approval, state which identity executes and which approves, and if they are the same, record the control as procedural with an accepted risk rather than writing a two-identity test. [L-20261107T201003Z-tests-were-specified-for-owner-only-controls-that-an-agent-holding-the]
- [Low] Store audio gate evidence on a dedicated orphan evidence branch, git-ignore renders on the implementation branch, and keep only SHA256SUMS on it. [L-20261007T151000Z-large-evidence-off-impl-branch]
- [Low] When freezing a cap on listening rounds, freeze the owner-controlled extension route with it and require each use to be recorded. [L-20261106T180500Z-owner-extension-needs-a-recorded-route]

### audio-metrics-and-references

Applied as: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050.

- [High] Add a test for every parameter that defines the scored window or note set asserting exactly how many frames or notes the metric receives, before calibration code is written. [L-20261004T102003Z-window-semantics-off-by-one]
- [High] Before computing spectra of a reference recording, track pitch and level over time, segment it into stable regions, and analyse each region separately excluding dropouts and transitions. [L-20261004T162217Z-nonstationary-recording-analysed-as-one-note]
- [High] Before freezing any reference-comparison threshold, compute the metric on the reference recordings in a planning spike and show the reference median passes the frozen criterion. [L-20261007T150400Z-threshold-not-checked-against-reference-spread]
- [High] Zero-pad every FFT filter to at least signal length plus impulse-response length and truncate (or use a causal filter) whenever the filtered audio's time structure is measured. [L-20261008T010500Z-circular-fft-filter-fakes-onsets]
- [High] Write analysis renders as float32 and print the unclipped peak of every render before any normalise or clamp, reporting a peak above 1.0 as a fact. [L-20261009T120001Z-wav-writer-clipped-baseline-before-analysis]
- [High] Set numeric acceptance targets only after measuring a baseline implementation once, and label in the plan which targets are expectations rather than gates. [L-20261009T120011Z-numeric-realism-targets-set-before-attainable-range]
- [Medium] Implement onset and offset detection with two thresholds (confirm and lower extension) and test it on a synthetic slow fade before accepting it. [L-20261004T161500Z-fade-in-onset-clipped-by-single-threshold]
- [Medium] Validate each DSP measurement (latency, attack time, decay, filter response) on a synthetic signal with a known answer before using it in a test. [L-20261004T162214Z-dsp-test-measured-wrong-quantity]
- [Medium] Validate any pitch tracker against a hand-checked segment of the actual reference material and treat isolated octave or fifth jumps as tracker errors until disproved. [L-20261004T162219Z-pitch-tracker-octave-errors]
- [Medium] Subtract excluded intervals from every analysis window explicitly, assert no window intersects an excluded interval at either edge, and measure the effect of any overlap found. [L-20261007T150832Z-analysis-windows-overlapped-dropout-and-contaminated-profile]
- [Medium] For every voice, compute energy above 2 kHz and the frequency below which 95% of energy lies, print them beside the reference recording, and do not call a voice realistic from partial positions alone. [L-20261008T173535Z-cymbals-checked-against-own-recipe-not-realism]
- [Medium] Define any peak/partial counter against a local noise floor and test it on a known number of sinusoids and on white noise (about zero) before using it on renders. [L-20261009T120002Z-partial-counter-counted-noise-floor]
- [Medium] Measure decay of plucked or struck sounds with a window that is full at t=0 (falling half-window) and validate it on a synthetic exponentially decaying sinusoid of known T60. [L-20261009T120008Z-analyser-hann-window-erased-fast-decaying-modes]
- [Medium] After any change to a DSP model, regenerate every metric table, baseline and figure that cites it and list each data file's model version in the manifest. [L-20261009T192606Z-results-from-superseded-ramp-stayed-in-the-thermal-table]
- [Medium] Add a check that fails when DSP source changes while recorded baseline or metric results carry an older provenance git commit. [L-20261009T193614Z-src-change-after-production-run-d025]
- [Low] Estimate the attainable range of each metric on the real engine before choosing calibration targets and print the range beside the targets. [L-20261004T102005Z-calibration-targets-before-attainable-range]
- [Low] Compare detector output with ground truth numerically in code with an asserted tolerance, never by eye from rounded printed values. [L-20261004T161501Z-synthetic-ground-truth-misprinted]
- [Low] Measure the reference's spectral centroid and band-energy distribution before choosing a fitting range and fit up to the frequency below which about 95% of its energy lies. [L-20261004T162221Z-fit-range-chosen-before-reference-bandwidth]

### ci-github-actions

Applied as: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003`.

- [High] Before adding any upload-artifact of binaries or audio, check repository visibility with gh api and, if public, treat the upload as publication and omit it unless the plan's gate approves it. [L-20261015T090000Z-public-repo-artifacts-are-publication]
- [High] For every CI gate, confirm once that it can fail by feeding it a failing input, and treat '|| true', continue-on-error and 'informational' steps as the gate not existing. [L-20261029T000000Z-green-ci-gate-never-ran]
- [High] Make every run: block with a pipe start with set -o pipefail or use shell: bash, and enforce it with a CI lint. [L-20261031T100000Z-actions-run-steps-have-no-pipefail]
- [High] Before fixing the CI matrix and triggers, compute builds, minutes per job and runner budget per push or PR and record the result in the decision. [L-20261107T213402Z-quota-and-cadence-arithmetic-was-not-done-before-choosing-a-weekly-job]
- [Medium] Push the branch and trigger CI after the first build step rather than the last, and report 'implemented, unverified' per platform until CI is green. [L-20261009T150601Z-browser-tests-could-not-run-in-the-sandbox-so-four-defects-i]
- [Medium] Give every workflow_dispatch input a non-empty default and dry-run each workflow on a throwaway ref before relying on it. [L-20261009T150901Z-the-deploy-workflow-broke-on-an-empty-ref-input-and-its-depl]
- [Medium] If a manual dispatch is on the critical path, put a minimal dispatchable workflow on the default branch in the bootstrap step and state the exact UI path to the person. [L-20261009T151001Z-the-plan-s-mitigation-for-workflow-dispatch-needing-the-defa]
- [Medium] After the first step adding a platform test, push and run the CI job, and until a CI run id is recorded in the checkpoint list every such test as 'implemented, unverified'. [L-20261009T191300Z-browser-suite-first-ran-after-the-whole-implementation-was-pushed]
- [Medium] Resolve every pinned version (JUCE tag, pluginval release, action tags, runner images) against the upstream release or tag list when writing the plan, and check the defaults of wrapper actions. [L-20261028T200000Z-pinned-tool-version-does-not-exist]
- [Medium] If mutation testing is adopted, time the unit executable first, compute mutants times suite time over workers against the job limit, and choose the test subset up front. [L-20261029T010000Z-mull-reruns-whole-suite-per-mutant]
- [Medium] Before any design relies on one workflow triggering another, a bot pushing to a protected branch or a scheduled run, check GitHub's documented behaviour for GITHUB_TOKEN and workflow_run. [L-20261107T201004Z-github-actions-rules-about-github-token-workflow-triggers-and-schedule]
- [Low] Check Actions log reachability in the environment spike and, if blocked, record it as a risk and scope any diagnostics workflow to workflow_dispatch with minimal permissions. [L-20261009T150701Z-actions-logs-and-artifacts-were-unreachable-from-the-sandbox]
- [Low] Parse every workflow file with a YAML loader and actionlint before the plan is marked ready and prefer block-style mappings for lines containing ${{ }}. [L-20261009T150801Z-the-plan-s-ci-workflow-template-failed-to-parse-because-gha-]

### cpp

Applied as: step checks in `S-110` and `S-300`; test T-011.

- [High] After any change to shared scoring or DSP code made to fix one case, re-run the complete test suite before calling the fix validated. [L-20261004T150500Z-cross-library-float-fix-regressed-passing-cases]
- [Medium] Before adding a shared DSP module, grep for one with the same responsibility and extend it, and name any unused duplicate in DEVIATIONS.md before the push. [L-20261004T102008Z-duplicate-pitch-modules-shipped]
- [Medium] Format every number in generated C++ through one function that guarantees a valid literal for the target type, and test the output by compiling it. [L-20261009T120007Z-emitted-float-literals-invalid-or-subnormal]
- [Low] Grep the staged diff for multiply-by-zero, TODO and FIXME before every commit and write the intended expression directly. [L-20261004T102006Z-placeholder-arithmetic-left-in-code]

### git-and-push

Applied as: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6.

- [High] On the first push failure read the error, call add_repo with access push if available, and otherwise ask the human to attach the repository instead of retrying with new tokens. [L-20261009T193602Z-proxy-repo-authorization-blocks-push]
- [High] At intake, run git push --dry-run to a probe ref for every repository the run will write and ask the owner for every missing grant in the first message. [L-20261102T232340Z-push-refused-after-add-repo-app-not-installed-on-repo]
- [High] Authenticate through the tool's credential client and never place a credential in a URL, command argument, header, repository file or output. [L-20261103T231200Z-credentials-in-command-lines]
- [Medium] If git push fails with a server-side unpack error across different refs and credentials, stop retrying the pack transport, record the push as environment-blocked in the risk register, and report it. [L-20261004T150600Z-git-push-pack-transport-failed-reproducibly]
- [Medium] Before bulk-deleting any directory in a git tree, run git status --short on that path and delete only untracked entries. [L-20261004T150800Z-bulk-delete-removed-tracked-file]
- [Medium] After any push done through a non-git mechanism, fetch and reset to the remote tip before further commits. [L-20261004T150900Z-local-head-diverged-from-api-pushed-remote]
- [Medium] When editing several branches, confirm git branch --show-current before each branch's edits and run multi-branch scripts with set -e. [L-20261004T162222Z-multi-branch-edit-loop-ran-on-wrong-branch]
- [Medium] Never expand a credential into a command line, URL, header argument or file; use the tool's own authenticated client. [L-20261007T150100Z-no-credentials-in-command-lines]
- [Medium] Before changing a project with a named repository, compare its current state with the files being changed and state in the first reply which one the changes are for. [L-20261008T223321Z-fixed-a-snapshot-without-checking-the-project-repo]
- [Medium] At the start of a run that pushes more than once, call add_repo with push access and plan all pushes together. [L-20261009T123014Z-pat-purged-before-push-needed-again]
- [Medium] Ask at intake whether the session has push rights to the repository and plan all pushes together so any credential is used once. [L-20261009T140013Z-a-token-pasted-in-chat-was-needed-three-times-in-one-run-eac]
- [Medium] Probe scopes only with read endpoints or on a throwaway object, never by writing to a live PR or issue. [L-20261009T151201Z-a-permission-probe-overwrote-the-body-of-pr-1]
- [Medium] When a workflow file must exist on main early, commit identical final content in both places or bootstrap a minimal workflow, and diff before choosing a merge strategy. [L-20261009T151301Z-workflow-files-were-pushed-straight-to-main-which-diverged-h]
- [Medium] Call add_repo with access push before trying any user-supplied token, never write a token to a file, and treat a pasted token as exposed. [L-20261009T160400Z-pasted-token-rejected-401-add-repo-not-tried-first]
- [Medium] Commit once per plan step with the checkpoint state in that commit, and open DEVIATIONS.md at the first departure listing every changed assertion, dropped test or unbuilt behaviour. [L-20261009T160600Z-protocol-records-not-kept-one-implementation-commit]
- [Medium] At the start of any push run call add_repo with push access, and if it returns read-only tell the person at once what grant is needed and plan a single push. [L-20261009T191700Z-pasted-tokens-failed-three-ways-and-add-repo-gave-read-only-on-the-target]
- [Medium] At the start of each continuing turn run git rev-parse HEAD and git fetch then git log HEAD..origin/main, and list existing IDs on origin before numbering any spike, decision or test. [L-20261009T191800Z-local-clone-fell-behind-origin-and-was-later-lost-in-a-sandbox-reset]
- [Medium] Commit once per plan step, update the checkpoint state in that commit, and record each changed assertion or decision in DEVIATIONS.md. [L-20261009T191900Z-implementation-reported-in-one-66-file-commit-with-no-deviations-or-execution-log]
- [Medium] Before any history rewrite, record the remote HEAD from git ls-remote and use it as an explicit force-with-lease, never bare --force. [L-20261009T192612Z-filter-branch-rewrite-then-force-push-with-the-wrong-lease]
- [Medium] Before sending any handoff bundle, compare unzip -l with git diff --name-status against the remote tip and require an exact match including dot-directories. [L-20261009T193604Z-zip-exclude-dotfiles-dropped-checkpoints]
- [Medium] At intake, probe access to every repository the task names and tell the human immediately which to attach. [L-20261009T193618Z-repo-not-attached-probe-first]
- [Medium] After any push that used a pasted token, inspect git config remotes and grep the repository for github_pat_ and ghp_ and clean what is found before the turn ends. [L-20261009T234112Z-token-url-left-in-git-config-after-unsetting-insteadof]
- [Medium] Verify git smart-HTTP write access with a non-mutating push through an ephemeral credential helper before relying on it. [L-20261028T233100Z-git-auth-header]
- [Medium] Before the final planning commit, verify the remote and run an authenticated git ls-remote, and report any persistence limitation instead of claiming a push. [L-20261029T004636Z-final-push-preflight]
- [Medium] In the first reply, list every repository setting the CI and PR flow needs and ask the owner for each in one message with the exact setting. [L-20261102T225600Z-new-repo-and-pages-settings-refused-mid-run]
- [Medium] Make every bootstrap or resume script fast-forward or stop with a distinct exit code and never reset, force-checkout or delete a branch. [L-20261105T215500Z-bootstrap-branch-reset-is-not-idempotent]
- [Low] Use the authenticated gh CLI or GitHub tools for every GitHub API request and check the HTTP status before parsing JSON. [L-20261004T161502Z-unauthenticated-github-api-call]
- [Low] Create .gitignore for build output directories before the first git add -A and read git status --short before committing. [L-20261008T223321Z-git-add-all-committed-build-directories]
- [Low] Clone or inspect the named project repository first and state in the first reply whether work targets it or a separate file. [L-20261009T090806Z-built-new-app-without-checking-the-named-project-repo]
- [Low] Stage by explicit file list and read git diff --cached --stat before every commit. [L-20261009T120016Z-blanket-git-add-swept-in-foreign-file]
- [Low] Try add_repo first for any GitHub repository the task names and never use or store a pasted token when it works. [L-20261009T120018Z-pat-in-chat-did-not-grant-repo-access-in-session]
- [Low] Stage by explicit file list, read git diff --cached --stat before every commit, and add .gitignore entries when a tool first writes a log. [L-20261009T140008Z-a-blanket-git-add-a-committed-emulator-log-files-again]
- [Low] Check the PR object's draft field after any state-change request and use the GraphQL mutation for draft changes. [L-20261009T151401Z-a-draft-pr-could-not-be-marked-ready-through-the-rest-api]
- [Low] After writing .gitignore, run git check-ignore -v on every fixture path tests read and require every needed file to print nothing. [L-20261009T191500Z-gitignore-model-pattern-excluded-the-tiny-test-fixtures]
- [Low] After changing .gitignore, run git ls-files against every file the manifest names and fail on any missing one. [L-20261009T192610Z-gitignore-log-pattern-left-manifest-logs-untracked]
- [Low] Before a commit that adds a new directory, run git status --short and add files by name or ignore the directory's build output first. [L-20261009T232010Z-built-binaries-committed-no-gitignore]
- [Low] At the last implementation step update the checkpoint and run git ls-remote --symref origin HEAD, requiring the symref to name the intended branch. [L-20261009T234122Z-checkpoint-state-stale-after-implementation-and-main-not-default]
- [Low] Construct every git network URL directly from the supplied owner/repository pair and compare it character by character. [L-20261028T222647Z-malformed-clone-url]
- [Low] After a git index-lock error verify no git process is active and inspect the lock before removing only a confirmed stale lock. [L-20261104T000900Z-stale-git-index-lock-after-mount-error]
- [Low] Before a broad research staging operation inspect the staged file list and ignore __pycache__, *.py[cod] and local build outputs. [L-20261104T011700Z-generated-python-cache-staged]
- [Low] Try the normal gh command once, read the error, and fall back to gh api REST routes only if GraphQL is refused. [L-20261107T201006Z-github-graphql-calls-failed-in-one-claude-code-remote-session-while-th]

### juce-build

Applied as: decisions D-080 and D-094, `plugins/CMakeLists.txt` (built in spike S10), step `S-310`.

- [High] Configure and build all JUCE glue (cmake -B build && cmake --build build) against the pinned JUCE tag before delivery, or label it NOT COMPILED wherever it is described. [L-20261008T173536Z-juce-glue-delivered-uncompiled]
- [High] Before changing or diagnosing any editor behaviour, read the current editor and component files and trace the displayed value from the drawing call back to the line that writes it. [L-20261009T092001Z-ui-code-edited-and-bug-diagnosed-without-reading-displayed-component]
- [High] Read the parameter name of every JUCE helper given a literal, and keep for each signal-changing stage a test asserting the change (attenuation, boost, filter response), not only no NaN or crash. [L-20261028T220000Z-decibelstogain-minusinfinity-misuse]
- [Medium] Syntax-check or build all JUCE code against the pinned JUCE tag before delivery, or label each file NOT COMPILED in the reply and README. [L-20261009T092006Z-juce-code-delivered-uncompiled-again]
- [Medium] List every UI behaviour that cannot be run in the checkpoint's unverified array mapped to an operational test, and move computable decisions (label culling, font fit) into window-free tests. [L-20261009T160200Z-ui-compiled-but-never-run-and-smoke-test-abandoned]
- [Medium] Before using a JUCE API, grep the pinned JUCE headers for it, and add a static_assert on JUCE_MAJOR_VERSION when a newer API is used. [L-20261009T160900Z-juce-api-assumed-from-memory-compile-caught-and-version-floor-unchecked]
- [Low] Read the compiler and generator from the runner image or build log, and never name a Visual Studio version or generator in CMake or CI without verifying it. [L-20261009T092005Z-assumed-visual-studio-2022-log-said-18]

### planning-process

Applied as: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5.

- [High] Before the plan or any README states behaviour, equivalence or an environment limit, run the one command that shows it in the same turn and cite it, otherwise write UNVERIFIED beside the claim. [L-20261008T173532Z-untested-claims-stated-as-fact-four-times]
- [High] Cite a source for a figure only if its passage was opened in the same run, give a locator for every entry, and mark recalled entries 'recalled, unchecked'. [L-20261009T120015Z-research-note-stated-recalled-details-as-cited-facts]
- [High] Count distinct publishers (not URLs) for any 'corroborated' reference or licensing claim, record the count in the claim, and have the consistency check compare it with the label. [L-20261009T123005Z-corroborated-label-without-independent-sources]
- [High] Before the plan states a block size, latency, CPU multiple or equivalence level as a requirement, run a spike on the real engine and cite its output file next to the number, otherwise mark it UNMEASURED. [L-20261009T234100Z-intake-defaults-and-draft-numbers-stated-before-measurement]
- [High] Cross-check every generated path, branch pattern and identifier in the plan against the frozen test/adapter assertions before declaring the plan consistent. [L-20261104T013500Z-plan-evidence-branch-contract-mismatch]
- [High] Before freezing the plan, mechanically resolve every referenced ID and simulate every blocked path through its defined gate. [L-20261106T123000Z-cold-read-explicit-references]
- [High] When any chosen tool or framework is swapped during planning, list each assumption the design made about the old one and re-derive it, treating the replan as a new design. [L-20261107T213401Z-provider-swap-done-by-annotation-without-re-deriving-the-operating-model]
- [Medium] Before a citation, formula constant or default value appears in the plan, test or code, retrieve it from the primary source in the same turn and record its locator, otherwise label it UNVERIFIED. [L-20261004T102001Z-recalled-literature-facts-wrong]
- [Medium] Produce every test count in a report from the test runner's list output in the same turn and never carry counts from earlier text. [L-20261004T102009Z-stale-test-counts-in-reports]
- [Medium] Before closing implementation, map every plan step and pre-mortem control to a file or test and list each unmapped one in DEVIATIONS.md. [L-20261004T102010Z-plan-controls-not-traced-to-delivery]
- [Medium] Before the plan names any command or API you cannot execute, fetch or grep the reference in the same turn, record its locator, and mark unconfirmed commands UNVERIFIED in code comments and the plan. [L-20261004T161503Z-audacity-commands-coded-from-memory]
- [Medium] When a request's description conflicts with the code or references, state what the code does and ask which meaning is intended before designing tests around either reading. [L-20261004T162210Z-user-premise-dismissed-instead-of-asked]
- [Medium] Every number, causal claim or behaviour claim in code, docs or replies must cite the measurement, test or code location in the same turn or carry the word UNVERIFIED. [L-20261004T162218Z-unmeasured-claims-stated-as-fact]
- [Medium] Do not write 'I read/pulled the source' unless a fetch in the same turn returned that text, give its URL, and mark every other framework or platform claim UNVERIFIED. [L-20261009T092004Z-claims-attributed-to-sources-not-read]
- [Medium] Re-derive every plan constant from its cited measurement and check sign and direction before coding it. [L-20261009T120009Z-plate-stretch-direction-taken-from-plan]
- [Medium] Load every lesson matching the task's tags before writing the plan and record which were applied and where. [L-20261009T120019Z-protocol-adopted-mid-run-without-before-run-step]
- [Medium] Write each checkpoint file at the moment of the checkpoint from what exists then, append to a log as each step finishes, and after a reset add a dated note instead of rewriting entries. [L-20261009T123004Z-checkpoints-back-filled-no-execution-log]
- [Medium] Record in the intake file which lessons were loaded and the tags used to select them. [L-20261009T140015Z-the-lessons-and-knowledge-addendum-was-adopted-after-plannin]
- [Medium] After implementing a UI section, mark each plan bullet built, deviated (with a DEVIATIONS.md entry) or not built, and do not write 'per plan' for a bullet with no entry. [L-20261009T161200Z-edocontrol-differs-from-plan-3-3-and-nothing-logged]
- [Medium] Never type a numeric result into a report or README; generate it from a script and reference the generated value. [L-20261009T193610Z-hand-typed-numbers-and-lint-rounds]
- [Medium] Commit every spike backing a claim or deviation under research/spikes/<name>/ with its output before citing it, and never cite a path under /tmp. [L-20261009T232004Z-deviation-evidence-cited-lost-tmp-spikes]
- [Medium] If a tool result says NOT RUN, call the tool again before writing closing text and end the turn only when the request has an answer. [L-20261009T234116Z-add-repo-came-back-not-run-and-turn-ended]
- [Medium] Before the README states a behaviour, trace each sentence to a test ID or spike output and add the stated condition to the sentence. [L-20261009T234120Z-readme-claims-not-tied-to-a-test-or-to-the-segmentation-condition]
- [Medium] Render the lesson-application record from where each rule was actually applied (file and section), mark partly adopted rules 'partly applied' with the reason, and grep the record for paths that do not exist in the plan. [L-20261023T223300Z-r0-table-quoted-proposals-not-adopted-text]
- [Medium] Treat a prior DONE as a hypothesis and for each item run the grep, read the exit path or open the run, recording the evidence beside the verdict. [L-20261031T100100Z-verify-conformance-claims-against-the-tree]
- [Medium] Write each source into the round log's sources-checked section as it is opened, with its outcome and licence. [L-20261105T221000Z-source-facts-lost-in-context-reset]
- [Medium] After every amendment batch, search the whole plan for the superseded phrases, fix or mark each hit, and add the phrases to the mechanical consistency checker. [L-20261107T201002Z-amendment-rounds-left-stale-wording-that-contradicted-the-new-decision]
- [Low] Before sending any handoff archive, extract every file name a packaged document mentions and check each against unzip -l and the delivered file names. [L-20261008T173533Z-readme-names-files-not-in-the-zip]
- [Low] Generate every count in a report from a command and paste its output, never typing numbers from memory. [L-20261009T123012Z-status-counts-typed-and-commit-count-misreported]
- [Low] Generate every count in a report from the test run and never type it. [L-20261009T140011Z-test-category-counts-in-the-traceability-report-were-estimat]
- [Low] Namespace gate and step IDs by source or allocate the next free number, and check for collisions mechanically. [L-20261009T140014Z-the-addendum-s-gate-id-g-003-collided-with-the-plan-s-own-g-]
- [Low] Update the checkpoint state at the end of every implementation step and append to an execution log with step, commit, time and run id. [L-20261009T152201Z-the-checkpoint-state-was-never-updated-after-planning-and-th]
- [Low] When a tool result says NOT RUN or is empty, re-issue the call once or tell the person what did not run and never close a turn while a request is open. [L-20261009T192100Z-tool-call-came-back-not-run-and-the-turn-ended-with-no-response-requested]
- [Low] Give every sentence-level assertion its own entry and status and mark it verified only if the cited source contains that assertion. [L-20261009T192200Z-verified-label-on-a-claim-whose-cited-sources-covered-only-half]
- [Low] Compute every count quoted in a report or prompt from the repository at that moment and never type one. [L-20261009T192611Z-tracked-file-count-typed-in-a-prompt-was-wrong]
- [Low] After each implementation step regenerate the artifacts hash map and updated_at from git ls-files and append one line to the execution log, with a make target so it is one command. [L-20261009T232009Z-checkpoint-state-stale-after-implementation]

### sandbox-environment

Applied as: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10.

- [High] At planning time and again at S-001, probe every external host any step names, record results in plan/ENVIRONMENT.md, and re-plan dependent steps before freezing. [L-20261009T193601Z-plan-assumed-hosts-reachable]
- [Medium] At the start of each turn continuing the run, verify the working tree with git rev-parse HEAD and restore from the remote if it fails. [L-20261004T102007Z-sandbox-reset-lost-working-tree]
- [Medium] After any non-interactive search-and-replace, diff or grep the target to confirm the change landed and prefer a primitive that fails loudly on non-match. [L-20261004T150700Z-scripted-str-replace-silently-no-opped]
- [Medium] In the plan, create Python venvs with --without-pip plus get-pip.py, take CMake and build tools from release binaries, and never assume apt or system pip. [L-20261007T150000Z-sandbox-no-pip-no-sudo]
- [Medium] Run each edit as its own call and confirm it with grep or diff before starting a slow build step. [L-20261009T120014Z-chained-sed-edit-skipped-after-timed-out-call]
- [Medium] Before recording a dependency as unavailable in the planning sandbox, run the clone or install command, keep its error output in research/, and if it works compile the frozen tests against it before the freeze. [L-20261009T161600Z-integration-tests-frozen-as-compile-unverified-juce-reachable-later]
- [Medium] When a host is reported unreachable, read $HTTPS_PROXY/__agentproxy/status and the allowlist configuration before attributing the failure. [L-20261009T192613Z-codeberg-called-not-allowlisted-without-checking-the-live-proxy]
- [Medium] Make every long render or analysis study resumable from saved state, run it in slices shorter than the tool limit, and test background survival with a heartbeat first. [L-20261009T192617Z-solver-studies-exceeded-tool-limit-and-background-runs-died]
- [Medium] Before diagnosing a git credential failure, print the names (not values) of GIT_*, GH_* and GITHUB_* variables and retry with them unset before concluding the token is bad. [L-20261009T193603Z-ambient-git-config-breaks-fetch]
- [Medium] Before any large render sweep, estimate peak memory, compare it with free -m and the cgroup limit, abort above 60 percent, and never run two heavy jobs concurrently. [L-20261009T193613Z-heavy-jobs-without-memory-preflight]
- [Medium] Before the first build step, classify the environment as stable or ephemeral with observed evidence, record it in the environment document, and if ephemeral put the restaging script in place before the first configure. [L-20261031T000000Z-probe-environment-class-at-run-start]
- [Medium] Stage builds on local executable storage, copy artifacts back to the durable mount, and chmod after any copy from the mount. [L-20261101T042200Z-portal-mount-no-symlinks-or-exec-bits]
- [Medium] Place git credential-cache sockets in a mode-0700 temporary directory, never in the repository or on a mount that cannot tighten permissions. [L-20261103T231500Z-credential-cache-socket-mount]
- [Medium] Before the first configure, test that the work directory can execute binaries and, if not, stage the complete toolchain on executable storage and invoke the staged binary directly. [L-20261104T004100Z-cmake-package-needs-data-and-exec-bits]
- [Medium] Stage every executable helper onto executable local storage and run a trivial invocation before relying on it. [L-20261105T213000Z-mount-credential-helper-exec]
- [Medium] Probe each host a step depends on at the start of that step, record the time, and give every download a human fallback. [L-20261105T220500Z-probe-reachability-and-reprobe-before-download-steps]
- [Low] Locate any file in a third-party repository (JUCE, pluginval, VST3 SDK) by tree listing or pinned tag before fetching it by raw path. [L-20261004T161505Z-guessed-raw-github-path-404]
- [Low] For any build that may exceed 250 seconds, start it with setsid nohup and poll the log or build one target per call with a timeout, and never start a long build without one of these. [L-20261009T160300Z-single-core-sandbox-builds-exceeded-tool-limit-background-jobs-died]
- [Low] Commit a bootstrap script that clones the pinned JUCE tag and configures the test targets, and run it as the first command of every turn that needs a build. [L-20261009T161500Z-work-and-build-directories-vanished-between-turns]
- [Low] Check the executing shell and enforce a private socket directory before any non-interactive credential-cache operation. [L-20261104T021500Z-credential-cache-shell-and-socket]
- [Low] Before relying on any compression or archival CLI in a build, check which <tool> and, if absent but the library exists, build a minimal shim on executable storage. [L-20261106T063000Z-zstd-cli-shim]

### licensing

Applied as: decisions D-051, D-052 and D-081; step `S-REF`; the source register.

- [Medium] Read the current JUCE licence page for the pinned major version before writing the licence decision, and never carry a licensing premise across major versions. [L-20261027T123000Z-juce-license-assumption]
- [Medium] Treat a licence label on a reference recording as usable only when the page names the creator or links the original release and the licence is read there; otherwise list the source as a lead. [L-20261105T221500Z-aggregator-licence-label-without-creator]
- [Low] Include a LICENSE file in the first push of any new repository, consistent with the JUCE licence decision, and ask the owner if the choice is not known. [L-20261004T161504Z-new-repo-pushed-without-license]
- [Low] At intake list every licence file the plan needs (project licence, JUCE/VST3 notices) and check its full text is obtainable, otherwise ask the owner before S-001. [L-20261009T232011Z-licence-text-not-obtainable-offline-pointer-left]

### python-tooling

Applied as: decision D-085 (`tests/requirements.txt`), test T-310.

- [Medium] After fixing a script crash, re-run that exact script to completion and verify the generated file's invariant (entry count matches source count) before committing. [L-20261004T153000Z-index-regen-skipped-after-crash-fix]
- [Medium] Release every resource a CLI or render tool opens in the same finally block or context manager and test closure after both normal and raising runs. [L-20261009T123000Z-transcript-log-never-closed]
- [Medium] Catch decoding errors at the parser boundary of the render tool and analysis CLIs, raise the project's own error type, and add a test with a malformed or non-ASCII payload. [L-20261009T123001Z-non-ascii-vin-uncaught]
- [Medium] Create pyproject.toml, list the build backend in the lock input, and run pip-audit and a clean-room install in one step before writing analysis code. [L-20261009T123010Z-build-backend-pin-and-pyproject-order]
- [Medium] Include the build backend in the lock inputs from the start and run pip-audit on the final lock before treating the environment as done. [L-20261009T140003Z-the-hash-locked-environment-omitted-the-build-backend-and-th]
- [Medium] Before running a Python per-sample audio loop, compute total sample iterations, keep each foreground run to a measured small workload, and use vectorised or compiled code and checkpointed stages instead of exhaustive sweeps. [L-20261104T010000Z-spike-workload-exceeded-call-lifetime]
- [Low] Choose generator search bounds from the required count with margin and assert the row count after generation. [L-20261009T120006Z-plate-table-too-short-for-mode-budget]
- [Low] Before writing an oracle spike, print dir() of the module and the signature of each call to be used. [L-20261009T123008Z-oracle-spike-assumed-library-api]
- [Low] Print the effective parameter values at the start of every study or render run and compare them with intended values before proceeding. [L-20261009T192607Z-patch-assumed-applied-mushy-width-default-was-0-02]
- [Low] On a package-index DNS or connection failure, identify the configured index, switch explicitly to the verified public PyPI index without changing pins, and do not treat the failure as the version being unavailable. [L-20261104T004000Z-configured-package-index-unreachable]

### vst3-plugin

Applied as: decision D-094; tests T-300 and T-302; step `S-310`.

- [Medium] Before freezing interfaces, list every value the plugin layer must read from the core (latency, tuning, parameter ranges, UI state) and give each an accessor in the stub header. [L-20261007T150800Z-host-facing-accessors-missing]
- [Medium] Define every user-visible table (note labels, ranges, defaults) once in code, generate the editor, parameter layout and docs from it, and add a test comparing any second copy against the source. [L-20261008T173531Z-editor-note-labels-diverged-from-midi-map]
- [Medium] In every plugin pre-mortem add the lens 'what does the audio thread lock, allocate or wait on' and mitigate with lock-free reads of a preallocated snapshot. [L-20261009T161100Z-audio-thread-takes-mutex-and-copies-vectors-not-in-premortem]
- [Medium] Run pluginval at strictness 5 or higher in CI from the first build that produces a plugin binary and do not rely on unit tests for host-contract rules. [L-20261028T215000Z-vst3-validator-not-in-local-suite]
- [Medium] For any change touching threading or the audio path, run a host-style stress test (random parameter automation at several block sizes, re-prepare mid-run) in CI and treat intermittent pluginval failures as reproducible bugs. [L-20261101T140000Z-intermittent-host-failure-needs-a-stress-test]
- [Low] Before setting a plugin parameter's user-facing range, measure the attainable range for the specific configuration instead of using the model's nominal range. [L-20261004T151000Z-parameter-range-set-without-attainable-range-check]

## 2. Every lesson and how it is applied

| Lesson | Severity | Applies | How applied, or why not |
|---|---|---|---|
| L-20261004T150300Z-fixture-cents-reference-undeclared | Critical | yes | test: tests declare the reference (`hz(midi, a4)` in `tests/py/conftest.py`); test T-162 checks `a4_hz` |
| L-20261009T192601Z-convection-omitted-vortex-stretching-and-was-non-conservative | Critical | yes | test: step checks in `S-200` (`reed_probe --undriven`) and `S-240` (energy never grows); test T-015 |
| L-20261106T010000Z-verify-blind-references-against-sources | Critical | yes | step-check: step check in `S-340` (correlation of every blind clip with its source, in `tools/build_evidence.py`) |
| L-20261004T102003Z-window-semantics-off-by-one | High | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261004T150100Z-stray-superseded-test-files | High | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261004T150200Z-frozen-header-default-contradicted-fixture | High | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261004T150400Z-interface-gap-found-only-by-implementing | High | yes | step-check: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261004T150500Z-cross-library-float-fix-regressed-passing-cases | High | yes | step-check: step checks in `S-110` and `S-300`; test T-011 |
| L-20261004T162211Z-frozen-tests-drifted-from-harness | High | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261004T162213Z-timbre-invariance-measured-on-whole-chain | High | yes | decision: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261004T162217Z-nonstationary-recording-analysed-as-one-note | High | yes | step-check: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261007T150300Z-hand-typed-frozen-constant | High | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261007T150400Z-threshold-not-checked-against-reference-spread | High | yes | planner-process: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261007T150500Z-linear-bore-realism-ceiling | High | yes | planner-process: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261007T150600Z-control-mapping-formulas-unverified | High | yes | planner-process: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261007T150700Z-regime-selection-per-note | High | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261008T010500Z-circular-fft-filter-fakes-onsets | High | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261008T151500Z-reasoned-expected-value-wrong | High | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261008T173530Z-gain-staging-masked-by-normalising-renderers | High | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261008T173532Z-untested-claims-stated-as-fact-four-times | High | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261008T173536Z-juce-glue-delivered-uncompiled | High | yes | step-check: decisions D-080 and D-094, `plugins/CMakeLists.txt` (built in spike S10), step `S-310` |
| L-20261009T092001Z-ui-code-edited-and-bug-diagnosed-without-reading-displayed-component | High | yes | step-check: decisions D-080 and D-094, `plugins/CMakeLists.txt` (built in spike S10), step `S-310` |
| L-20261009T092002Z-note-routing-changed-twice-never-tabulated-key-to-hz | High | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T120001Z-wav-writer-clipped-baseline-before-analysis | High | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261009T120011Z-numeric-realism-targets-set-before-attainable-range | High | yes | planner-process: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261009T120012Z-residual-noise-level-41-db-low-found-only-by-spectrogram | High | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T120015Z-research-note-stated-recalled-details-as-cited-facts | High | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T123005Z-corroborated-label-without-independent-sources | High | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T160100Z-frozen-test-edited-and-hash-manifest-regenerated-by-implementer | High | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T192616Z-fixed-width-mushy-ramp-left-a-free-parameter | High | no | does not apply: CFD interface regularisation does not occur in these instrument models. |
| L-20261009T193601Z-plan-assumed-hosts-reachable | High | yes | planner-process: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261009T193602Z-proxy-repo-authorization-blocks-push | High | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T234100Z-intake-defaults-and-draft-numbers-stated-before-measurement | High | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261015T090000Z-public-repo-artifacts-are-publication | High | yes | decision: decision D-007 (artifacts treated as public distribution, 3 days' retention, licence included) |
| L-20261022T120000Z-store-not-found-ask-human | High | no | not applied (Rule 16): Asks to search the owner's private repositories for a knowledge store, an external action beyond this task. Recorded in risk R-010. |
| L-20261028T220000Z-decibelstogain-minusinfinity-misuse | High | yes | test: decisions D-080 and D-094, `plugins/CMakeLists.txt` (built in spike S10), step `S-310` |
| L-20261029T000000Z-green-ci-gate-never-ran | High | yes | test: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261031T100000Z-actions-run-steps-have-no-pipefail | High | yes | test: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261101T041800Z-perf-harness-must-exercise-what-it-reports | High | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261102T085622Z-git-transport-blocked-use-git-database-api | High | no | not applied (Rule 16): Asks to commit and push through a different transport (Git database API) than the plan's push route. Recorded in risk R-010. |
| L-20261102T232340Z-push-refused-after-add-repo-app-not-installed-on-repo | High | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261103T231200Z-credentials-in-command-lines | High | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261104T013500Z-plan-evidence-branch-contract-mismatch | High | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261105T215000Z-fixed-loudness-target-impossible-for-percussion | High | yes | test: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053 |
| L-20261105T220000Z-frozen-tests-must-fail-against-stubs | High | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261106T120000Z-red-runner-green-path | High | yes | step-check: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261106T123000Z-cold-read-explicit-references | High | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261106T180100Z-frozen-metric-caps-the-property-under-listening | High | yes | step-check: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053 |
| L-20261106T180200Z-reference-fit-before-listening | High | yes | step-check: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053 |
| L-20261107T213401Z-provider-swap-done-by-annotation-without-re-deriving-the-operating-model | High | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261107T213402Z-quota-and-cadence-arithmetic-was-not-done-before-choosing-a-weekly-job | High | yes | decision: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261004T102001Z-recalled-literature-facts-wrong | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261004T102002Z-perf-test-budget-not-derived | Medium | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261004T102004Z-checkpoint-rotated-corrupt-file | Medium | no | does not apply: No rotating checkpoint backup routine is in scope. |
| L-20261004T102007Z-sandbox-reset-lost-working-tree | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261004T102008Z-duplicate-pitch-modules-shipped | Medium | yes | step-check: step checks in `S-110` and `S-300`; test T-011 |
| L-20261004T102009Z-stale-test-counts-in-reports | Medium | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261004T102010Z-plan-controls-not-traced-to-delivery | Medium | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261004T150600Z-git-push-pack-transport-failed-reproducibly | Medium | yes | risk: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261004T150700Z-scripted-str-replace-silently-no-opped | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261004T150800Z-bulk-delete-removed-tracked-file | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261004T150900Z-local-head-diverged-from-api-pushed-remote | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261004T153000Z-index-regen-skipped-after-crash-fix | Medium | yes | step-check: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261004T161500Z-fade-in-onset-clipped-by-single-threshold | Medium | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261004T161503Z-audacity-commands-coded-from-memory | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261004T162210Z-user-premise-dismissed-instead-of-asked | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261004T162212Z-unsatisfiable-frozen-assertions | Medium | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261004T162214Z-dsp-test-measured-wrong-quantity | Medium | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261004T162215Z-waveshaper-curve-reassigned | Medium | no | does not apply: Web Audio WaveShaperNode does not exist in a JUCE plugin. |
| L-20261004T162216Z-dynamics-compressor-assumed-ideal | Medium | yes | decision: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261004T162218Z-unmeasured-claims-stated-as-fact | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261004T162219Z-pitch-tracker-octave-errors | Medium | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261004T162220Z-beat-phase-biased-harmonic-levels | Medium | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261004T162222Z-multi-branch-edit-loop-ran-on-wrong-branch | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261007T150000Z-sandbox-no-pip-no-sudo | Medium | yes | planner-process: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261007T150100Z-no-credentials-in-command-lines | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261007T150800Z-host-facing-accessors-missing | Medium | yes | step-check: decision D-094; tests T-300 and T-302; step `S-310` |
| L-20261007T150832Z-analysis-windows-overlapped-dropout-and-contaminated-profile | Medium | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261008T173531Z-editor-note-labels-diverged-from-midi-map | Medium | yes | test: decision D-094; tests T-300 and T-302; step `S-310` |
| L-20261008T173534Z-build-directory-vanished-between-turns | Medium | no | not applied (Rule 16): Asks to copy archives to a different store (/mnt/user-data/outputs) than the project repository. Recorded in risk R-010. |
| L-20261008T173535Z-cymbals-checked-against-own-recipe-not-realism | Medium | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261008T223321Z-fixed-a-snapshot-without-checking-the-project-repo | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T090801Z-tremolo-lead-arpeggiated-every-pick-sounded-like-synth | Medium | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T090802Z-guitars-too-clean-overdrive-not-measured | Medium | yes | step-check: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T090803Z-waveshaper-curve-reassigned-again-in-void-choir-app | Medium | no | does not apply: Web Audio WaveShaperNode does not exist in a JUCE plugin. |
| L-20261009T090804Z-master-compressor-without-ceiling-in-void-choir-app | Medium | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T090805Z-generative-audio-claims-made-without-listening-or-rendering | Medium | yes | step-check: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053 |
| L-20261009T092003Z-multi-file-patch-sent-as-snippets-partly-applied | Medium | no | does not apply: The implementing agent edits repository files directly rather than receiving snippets. |
| L-20261009T092004Z-claims-attributed-to-sources-not-read | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T092006Z-juce-code-delivered-uncompiled-again | Medium | yes | step-check: decisions D-080 and D-094, `plugins/CMakeLists.txt` (built in spike S10), step `S-310` |
| L-20261009T120002Z-partial-counter-counted-noise-floor | Medium | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261009T120003Z-roll-correlation-metric-passed-on-legacy-engine | Medium | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T120004Z-published-table-orientation-misread | Medium | yes | step-check: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T120007Z-emitted-float-literals-invalid-or-subnormal | Medium | yes | test: step checks in `S-110` and `S-300`; test T-011 |
| L-20261009T120008Z-analyser-hann-window-erased-fast-decaying-modes | Medium | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261009T120009Z-plate-stretch-direction-taken-from-plan | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T120010Z-calibration-nonlinearity-from-plan-did-not-converge | Medium | yes | step-check: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T120014Z-chained-sed-edit-skipped-after-timed-out-call | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261009T120019Z-protocol-adopted-mid-run-without-before-run-step | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T123000Z-transcript-log-never-closed | Medium | yes | test: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261009T123001Z-non-ascii-vin-uncaught | Medium | yes | test: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261009T123002Z-unguarded-first-element-indexing | Medium | no | does not apply: No hardware adapter replies are parsed. |
| L-20261009T123004Z-checkpoints-back-filled-no-execution-log | Medium | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T123010Z-build-backend-pin-and-pyproject-order | Medium | yes | step-check: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261009T123014Z-pat-purged-before-push-needed-again | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T123015Z-addendum-adopted-after-run-again | Medium | no | does not apply: Duplicates the intake lesson loading handled by the planner's own process; no store attachment is asked of this task. |
| L-20261009T140003Z-the-hash-locked-environment-omitted-the-build-backend-and-th | Medium | yes | step-check: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261009T140013Z-a-token-pasted-in-chat-was-needed-three-times-in-one-run-eac | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T140015Z-the-lessons-and-knowledge-addendum-was-adopted-after-plannin | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T150301Z-zoom-cost-was-measured-with-inter-raf-deltas-which-headless- | Medium | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T150601Z-browser-tests-could-not-run-in-the-sandbox-so-four-defects-i | Medium | yes | step-check: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261009T150901Z-the-deploy-workflow-broke-on-an-empty-ref-input-and-its-depl | Medium | yes | step-check: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261009T151001Z-the-plan-s-mitigation-for-workflow-dispatch-needing-the-defa | Medium | yes | step-check: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261009T151201Z-a-permission-probe-overwrote-the-body-of-pr-1 | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T151301Z-workflow-files-were-pushed-straight-to-main-which-diverged-h | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T160200Z-ui-compiled-but-never-run-and-smoke-test-abandoned | Medium | yes | step-check: decisions D-080 and D-094, `plugins/CMakeLists.txt` (built in spike S10), step `S-310` |
| L-20261009T160400Z-pasted-token-rejected-401-add-repo-not-tried-first | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T160500Z-lessons-addendum-adopted-after-implementation-again | Medium | no | not applied (Rule 16): Asks to load a default store from a repository owned by the target owner, an external fetch not part of this task. Recorded in risk R-010. |
| L-20261009T160600Z-protocol-records-not-kept-one-implementation-commit | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T160700Z-layout-rules-frozen-before-owner-confirmed-three-resets | Medium | yes | planner-process: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T160900Z-juce-api-assumed-from-memory-compile-caught-and-version-floor-unchecked | Medium | yes | step-check: decisions D-080 and D-094, `plugins/CMakeLists.txt` (built in spike S10), step `S-310` |
| L-20261009T161000Z-ji-labels-computed-with-12-tet-maths-in-the-editor | Medium | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T161100Z-audio-thread-takes-mutex-and-copies-vectors-not-in-premortem | Medium | yes | step-check: decision D-094; tests T-300 and T-302; step `S-310` |
| L-20261009T161200Z-edocontrol-differs-from-plan-3-3-and-nothing-logged | Medium | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T161600Z-integration-tests-frozen-as-compile-unverified-juce-reachable-later | Medium | yes | planner-process: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261009T191300Z-browser-suite-first-ran-after-the-whole-implementation-was-pushed | Medium | yes | step-check: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261009T191700Z-pasted-tokens-failed-three-ways-and-add-repo-gave-read-only-on-the-target | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T191800Z-local-clone-fell-behind-origin-and-was-later-lost-in-a-sandbox-reset | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T191900Z-implementation-reported-in-one-66-file-commit-with-no-deviations-or-execution-log | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T192000Z-lessons-addendum-adopted-after-implementation-and-follow-on-research | Medium | no | not applied (Rule 16): Asks to ls-remote a named external organisation's Lessons and knowledge repositories. Recorded in risk R-010. |
| L-20261009T192602Z-point-extrema-and-interpolated-isotherm-gave-nonsense-orders | Medium | no | does not apply: No mesh convergence studies are planned. |
| L-20261009T192604Z-order-fitted-from-pre-asymptotic-meshes-then-withdrawn | Medium | no | does not apply: No mesh refinement series is planned. |
| L-20261009T192605Z-limit-cycle-described-as-ran-out-of-time | Medium | no | does not apply: No iterative flow solver is used. |
| L-20261009T192606Z-results-from-superseded-ramp-stayed-in-the-thermal-table | Medium | yes | step-check: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261009T192609Z-van-leer-correction-claimed-second-order-measured-1-55 | Medium | no | does not apply: No finite-volume scheme order claims arise. |
| L-20261009T192612Z-filter-branch-rewrite-then-force-push-with-the-wrong-lease | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T192613Z-codeberg-called-not-allowlisted-without-checking-the-live-proxy | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261009T192617Z-solver-studies-exceeded-tool-limit-and-background-runs-died | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261009T193603Z-ambient-git-config-breaks-fetch | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261009T193604Z-zip-exclude-dotfiles-dropped-checkpoints | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T193609Z-sci-bound-round-to-nearest | Medium | no | does not apply: No printed numeric bounds in LaTeX macros arise. |
| L-20261009T193610Z-hand-typed-numbers-and-lint-rounds | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T193612Z-frozen-test-silent-fallback-single-seed | Medium | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T193613Z-heavy-jobs-without-memory-preflight | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261009T193614Z-src-change-after-production-run-d025 | Medium | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261009T193617Z-manual-upload-bundle-hygiene | Medium | no | does not apply: No manual web upload of bundles is planned; delivery is by pull request. |
| L-20261009T193618Z-repo-not-attached-probe-first | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T193619Z-addendum-adopted-after-run-again | Medium | no | not applied (Rule 16): Asks to clone a named external organisation's Lessons and knowledge repositories. Recorded in risk R-010. |
| L-20261009T232004Z-deviation-evidence-cited-lost-tmp-spikes | Medium | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T232008Z-addendum-adopted-after-run-stores-not-read | Medium | no | not applied (Rule 16): Asks to add a plan step cloning a named external repository pair. Recorded in risk R-010. |
| L-20261009T234102Z-draft-test-unsatisfiable-found-by-oracle-t-021 | Medium | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T234112Z-token-url-left-in-git-config-after-unsetting-insteadof | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T234116Z-add-repo-came-back-not-run-and-turn-ended | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T234120Z-readme-claims-not-tied-to-a-test-or-to-the-segmentation-condition | Medium | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T234124Z-addendum-adopted-after-run-and-stores-not-read-again | Medium | no | not applied (Rule 16): Asks to make cloning a named external repository pair the first plan step. Recorded in risk R-010. |
| L-20261023T223300Z-r0-table-quoted-proposals-not-adopted-text | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261027T121000Z-wrong-knowledge-store | Medium | no | does not apply: The lessons digest is supplied, so no knowledge-store location needs to be chosen. |
| L-20261027T123000Z-juce-license-assumption | Medium | yes | decision: decisions D-051, D-052 and D-081; step `S-REF`; the source register |
| L-20261028T200000Z-pinned-tool-version-does-not-exist | Medium | yes | step-check: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261028T210000Z-crlf-breaks-hash-manifests-on-windows | Medium | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261028T215000Z-vst3-validator-not-in-local-suite | Medium | yes | test: decision D-094; tests T-300 and T-302; step `S-310` |
| L-20261028T233100Z-git-auth-header | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261029T004636Z-final-push-preflight | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261029T010000Z-mull-reruns-whole-suite-per-mutant | Medium | yes | decision: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261029T020000Z-start-mutation-review-at-lowest-file | Medium | yes | step-check: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261031T000000Z-probe-environment-class-at-run-start | Medium | yes | planner-process: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261031T100100Z-verify-conformance-claims-against-the-tree | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261101T041500Z-verify-worker-bundle-before-freezing-architecture | Medium | no | does not apply: No browser or web worker is involved. |
| L-20261101T042000Z-commit-gate-records-with-the-response | Medium | yes | step-check: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053 |
| L-20261101T042200Z-portal-mount-no-symlinks-or-exec-bits | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261101T124000Z-sandbox-recycle-mid-build | Medium | no | not applied (Rule 16): Asks to keep build caches on a different durable store (/mnt/agents), outside the project. Recorded in risk R-010. |
| L-20261101T130000Z-mount-build-cache-and-split-units | Medium | no | does not apply: Targets JUCE 9 unity builds; JUCE 8 is pinned. |
| L-20261101T140000Z-intermittent-host-failure-needs-a-stress-test | Medium | yes | test: decision D-094; tests T-300 and T-302; step `S-310` |
| L-20261102T085700Z-rollout-addendum-commits-cause-predictable-tip-drift | Medium | no | does not apply: No controller pins audited source commits across rollout commits. |
| L-20261102T225600Z-new-repo-and-pages-settings-refused-mid-run | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261102T232000Z-american-conventions-and-us-sources-for-british-english-user | Medium | no | does not apply: A person-specific language preference of an earlier user, not a property of this task. |
| L-20261103T231500Z-credential-cache-socket-mount | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261104T004100Z-cmake-package-needs-data-and-exec-bits | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261104T010000Z-spike-workload-exceeded-call-lifetime | Medium | yes | step-check: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261105T213000Z-mount-credential-helper-exec | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261105T215500Z-bootstrap-branch-reset-is-not-idempotent | Medium | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261105T220500Z-probe-reachability-and-reprobe-before-download-steps | Medium | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261105T221000Z-source-facts-lost-in-context-reset | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261105T221500Z-aggregator-licence-label-without-creator | Medium | yes | step-check: decisions D-051, D-052 and D-081; step `S-REF`; the source register |
| L-20261105T233000Z-detached-loops-need-durable-storage | Medium | no | does not apply: The lesson gives no prevention text and concerns detached retry loops on a portal mount. |
| L-20261106T180300Z-twelve-pairs-too-noisy-to-steer-iteration | Medium | yes | step-check: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053 |
| L-20261107T201002Z-amendment-rounds-left-stale-wording-that-contradicted-the-new-decision | Medium | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261107T201003Z-tests-were-specified-for-owner-only-controls-that-an-agent-holding-the | Medium | yes | risk: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053 |
| L-20261107T201004Z-github-actions-rules-about-github-token-workflow-triggers-and-schedule | Medium | yes | decision: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261004T102005Z-calibration-targets-before-attainable-range | Low | yes | planner-process: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261004T102006Z-placeholder-arithmetic-left-in-code | Low | yes | step-check: step checks in `S-110` and `S-300`; test T-011 |
| L-20261004T151000Z-parameter-range-set-without-attainable-range-check | Low | yes | step-check: decision D-094; tests T-300 and T-302; step `S-310` |
| L-20261004T161501Z-synthetic-ground-truth-misprinted | Low | yes | test: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261004T161502Z-unauthenticated-github-api-call | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261004T161504Z-new-repo-pushed-without-license | Low | yes | step-check: decisions D-051, D-052 and D-081; step `S-REF`; the source register |
| L-20261004T161505Z-guessed-raw-github-path-404 | Low | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261004T162221Z-fit-range-chosen-before-reference-bandwidth | Low | yes | step-check: `tests/py/metrics.py` with T-090; T-200 thresholds measured in spike S07; step `S-REF`; decision D-050 |
| L-20261007T150200Z-restart-means-fresh-state | Low | no | does not apply: Concerns restarting from another session's scratch state, which the plan does not use. |
| L-20261007T150900Z-windows-sha256sum-backslash | Low | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261007T151000Z-large-evidence-off-impl-branch | Low | yes | decision: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053 |
| L-20261008T173533Z-readme-names-files-not-in-the-zip | Low | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261008T223321Z-git-add-all-committed-build-directories | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T090806Z-built-new-app-without-checking-the-named-project-repo | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T092005Z-assumed-visual-studio-2022-log-said-18 | Low | yes | decision: decisions D-080 and D-094, `plugins/CMakeLists.txt` (built in spike S10), step `S-310` |
| L-20261009T120006Z-plate-table-too-short-for-mode-budget | Low | yes | test: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261009T120016Z-blanket-git-add-swept-in-foreign-file | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T120018Z-pat-in-chat-did-not-grant-repo-access-in-session | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T123006Z-performance-budget-docstring-wrong-multiple | Low | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T123008Z-oracle-spike-assumed-library-api | Low | yes | step-check: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261009T123011Z-red-verification-matched-wrong-exception | Low | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T123012Z-status-counts-typed-and-commit-count-misreported | Low | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T140001Z-the-emulator-s-cli-batch-mode-does-not-print-the-pty-path-so | Low | no | does not apply: No emulator CLI is driven by tests. |
| L-20261009T140008Z-a-blanket-git-add-a-committed-emulator-log-files-again | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T140009Z-the-red-verification-classifier-mis-read-junit-failure-and-e | Low | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T140010Z-parsing-slips-found-only-by-the-implementation-compact-frame | Low | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T140011Z-test-category-counts-in-the-traceability-report-were-estimat | Low | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T140014Z-the-addendum-s-gate-id-g-003-collided-with-the-plan-s-own-g- | Low | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T150701Z-actions-logs-and-artifacts-were-unreachable-from-the-sandbox | Low | yes | risk: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261009T150801Z-the-plan-s-ci-workflow-template-failed-to-parse-because-gha- | Low | yes | test: `plan/ci/ci.yml` (no failure-swallowing; `shell: bash`; aggregator job), decisions D-007 and D-084, step `S-003` |
| L-20261009T151401Z-a-draft-pr-could-not-be-marked-ready-through-the-rest-api | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T152201Z-the-checkpoint-state-was-never-updated-after-planning-and-th | Low | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T160300Z-single-core-sandbox-builds-exceeded-tool-limit-background-jobs-died | Low | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261009T160800Z-naming-rule-first-draft-failed-14-of-217-oracle-cells | Low | yes | test: tests T-009 to T-012, T-109, T-154, T-160; the undriven-energy checks in `S-200` and `S-240`; `S-300` action 4; `S-ADVERSARIAL` group 4 |
| L-20261009T161300Z-stale-compile-unverified-statements-and-frozen-headers-on-retired-tests | Low | yes | step-check: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261009T161500Z-work-and-build-directories-vanished-between-turns | Low | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261009T191500Z-gitignore-model-pattern-excluded-the-tiny-test-fixtures | Low | yes | test: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T192100Z-tool-call-came-back-not-run-and-the-turn-ended-with-no-response-requested | Low | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T192200Z-verified-label-on-a-claim-whose-cited-sources-covered-only-half | Low | yes | planner-process: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T192607Z-patch-assumed-applied-mushy-width-default-was-0-02 | Low | yes | step-check: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261009T192610Z-gitignore-log-pattern-left-manifest-logs-untracked | Low | yes | test: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T192611Z-tracked-file-count-typed-in-a-prompt-was-wrong | Low | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T193605Z-premature-checkpoint-subphase | Low | no | does not apply: Specific to the checkpoint subphase field of an earlier workflow. |
| L-20261009T232009Z-checkpoint-state-stale-after-implementation | Low | yes | step-check: planner process during this run (1.3.6 verification recorded in `plan/ENVIRONMENT.md`; spikes cited beside every figure; ID check in the cold read); for the implementer: `HANDOFF.md` sections 3 and 5 |
| L-20261009T232010Z-built-binaries-committed-no-gitignore | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261009T232011Z-licence-text-not-obtainable-offline-pointer-left | Low | yes | step-check: decisions D-051, D-052 and D-081; step `S-REF`; the source register |
| L-20261009T234122Z-checkpoint-state-stale-after-implementation-and-main-not-default | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261028T222647Z-malformed-clone-url | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261028T233130Z-private-knowledge-clone | Low | no | does not apply: No private knowledge store is cloned by the plan. |
| L-20261029T002439Z-artifact-id-boundaries | Low | no | does not apply: Specific to artifact-ID scanner patterns in an earlier workflow. |
| L-20261101T042100Z-github-git-flaky-use-codeload-tarball | Low | no | not applied (Rule 16): Asks to fall back to codeload tarballs and a bundle push target after git transport failures. Recorded in risk R-010. |
| L-20261101T042300Z-probe-knowledge-store-dont-adopt-defaults | Low | no | does not apply: No knowledge-store location is chosen in this task. |
| L-20261104T000900Z-stale-git-index-lock-after-mount-error | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261104T004000Z-configured-package-index-unreachable | Low | yes | step-check: decision D-085 (`tests/requirements.txt`), test T-310 |
| L-20261104T011700Z-generated-python-cache-staged | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |
| L-20261104T012000Z-red-test-reached-fixture-before-stub | Low | yes | test: tests T-090 and T-091 (tool checks), the oracle run of spike S08, the manifest check in CI job `freeze` and in `S-002`, rule DR-05 |
| L-20261104T021500Z-credential-cache-shell-and-socket | Low | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261106T063000Z-zstd-cli-shim | Low | yes | step-check: step check: `S-000` action 3, `plan/ENVIRONMENT.md` section 4, rules DR-10 and DR-13, `HANDOFF.md` section 10 |
| L-20261106T180400Z-scan-for-leaks-must-skip-audio-payload | Low | no | does not apply: No name-leak scan of audio bytes is planned. |
| L-20261106T180500Z-owner-extension-needs-a-recorded-route | Low | yes | decision: steps `S-340` and `S-LISTEN`, gates G-L1 to G-L5 in `plan/GATES.md`, test T-210, decision D-053 |
| L-20261107T201005Z-output-restrictions-were-set-on-a-privacy-assumption-before-asking-wha | Low | no | does not apply: No privacy-driven output restrictions are in scope. |
| L-20261107T201006Z-github-graphql-calls-failed-in-one-claude-code-remote-session-while-th | Low | yes | step-check: step check: the PUSH convention at the head of `plan/PLAN.md` (every step), `S-000` action 5, `HANDOFF.md` Rule 6 |

## 3. Knowledge items used

152 of the 323 items are relevant. The facts carried into the plan, with their item IDs, are in `research/r0/knowledge_highlights.md`; the per-item decisions are in `research/r0/knowledge_relevance.json`. Items whose fact depends on a version or date were re-checked before use (pins and labels in `plan/ENVIRONMENT.md`; the environment class by probe). Items used as claim sources: K-20261007T160111Z-c-072 (TinySOL, C-021), K-20261027T123100Z-juce8-licensing (C-044), K-20261007T160009Z to K-20261007T160015Z and K-20261104T005300Z (pluginval, C-045), K-20261112T134500Z (runner labels, C-047, re-verified), K-20261009T164000Z (mandolin tuning, C-034), K-20261009T120109Z (resonator form, C-031). No `kind:source-register` item matched the task's subjects, so no earlier register was used as a map.

| Topic | Relevant items |
|---|---|
| juce | 26 |
| ci-runners-and-actions | 20 |
| sandbox | 18 |
| pluginval | 15 |
| git-github | 11 |
| modal-and-string-dsp | 10 |
| cmake-cpp-build | 8 |
| licensing | 8 |
| audio-metrics | 7 |
| vst3 | 5 |
| reference-recordings | 5 |
| listening-gate | 5 |
| mutation-testing | 4 |
| python-tooling | 3 |
| tunings | 3 |
| other | 2 |
| sanitizers | 2 |
