# Knowledge highlights for the five folk-instrument VST3 plugins (from 323 prior items)
Bracketed ids are full item ids; every item is evidence, re-check version-sensitive lines (dated 2026-09 to 2026-11) before pinning.

## CONFLICTS (read first)
- JUCE pin: 9.0.3 latest on 2026-09-28 [K-20261007T160000Z-c-001], 9.0.4 commit 3fb5cbc0340758596dac39f7c8de47d562b4896e [K-20261028T222647Z-juce-vst3-toolchain], 9.0.5 [K-20261104T003002Z-juce-9-agpl-commercial-license]; task says JUCE 8, last 8.x seen is 8.0.15 [K-20261004T151500Z-juce-8-vs-9-vst3-breaking-change]/8.0.16 [K-20261029T030300Z-juce-decibelstogain-second-argument]. Decide one pin and re-check tags.
- setup-python: v7.0.0 commit 5fda3b95a4ea91299a34e894583c3862153e4b97 [K-20261007T160018Z-c-019] vs v7.1.0 [K-20261104T004300Z-immutable-github-action-pins] (SHA only in the evidence file). Use SHA pins and re-resolve.
- Sandbox GitHub writes: token push and contents API worked 2026-10-04 [K-20261004T162306Z-git-push-and-contents-api-worked], REST blob/tree/commit route [K-20261004T151600Z-github-rest-api-bypasses-broken-pack-transport][K-20261102T085800Z-github-git-database-api-writes-when-transport-blocked]; but cloud session refused git/blobs and contents writes (403) [K-20261102T232300Z-pages-api-and-api-writes-refused-by-proxy], repo creation [K-20261102T225700Z-repo-creation-refused-in-cloud-session], and push without App scope [K-20261102T232330Z-git-push-refused-github-app-scope]. Probe first.
- Sandbox egress: zenodo.org and api.github.com blocked 2026-10-09 [K-20261009T193501Z-sandbox-egress-policy]; reachable 2026-11-05 [K-20261105T223300Z-sandbox-reachability-2026-11-05]. TinySOL download needs a re-probe.
- Sandbox stability: protocol says Claude cloud is stable [K-20261112T134530Z-environment-class-by-platform-2026-11] but the item itself warns directories vanished [K-20261008T173543Z-sandbox-working-directory-resets-corroborated]; treat as ephemeral.
- Runner labels: macos-latest now macOS 26 [K-20261007T160023Z-c-024]; windows-latest is VS 18 2026, VS2022 needs windows-2022 [K-20261007T160024Z-c-025]; use versioned labels [K-20261104T003007Z-versioned-github-runner-labels].

## juce
- JUCE 9.0.3 commit be29c81492b6151c8ea8d14c840e1311963b3a83; 9.0.2 commit 72782788ce18c2d4d760b28e0921d6ffc6431102; 9.0.0 2026-07-21 [K-20261007T160001Z-c-002][K-20261007T160002Z-c-003]
- juce_audio_processors_headless introduced 8.0.11 (absent 8.0.10); AudioProcessor lives there in 9.x; APVTS stays in juce_audio_processors [K-20261007T160029Z-c-030][K-20261104T003004Z-juce-9-headless-audioprocessor-path]
- JUCE 9 restructures VST3 client extensions (VST3Interface, JUCE_VST3_COMPATIBLE_CLASSES), 35+ breaking changes [K-20261004T151500Z-juce-8-vs-9-vst3-breaking-change]; CMake API doc identical 8.0.15 vs 9.0.3 [K-20261007T160030Z-c-031]
- Linux apt: 18 packages for 9.0.3 incl libegl-dev, libxi-dev [K-20261007T160005Z-c-006]; 16 for 8.0.15 [K-20261008T173542Z-juce-linux-build-dependencies-8-0-15]; 14 sufficed for VST3 build on Ubuntu 24.04 (g++ 13.3, CMake 3.28.3) [K-20261008T223321Z-juce-vst3-linux-build-14-packages]
- Decibels::decibelsToGain(db, minusInfinityDb=-100): 2nd arg is dB, not linear [K-20261029T030300Z-juce-decibelstogain-second-argument]
- APVTS copyState/replaceState lock: never in processBlock [K-20261104T004700Z-apvts-state-not-realtime-safe]; presets via replaceState, not per-parameter setValueNotifyingHost [K-20261027T120100Z-juce-preset-automation-spam]
- Convolution: loadImpulseResponse from worker thread threw bad_function_call under pluginval; internal gain ~1.53 for 0.5 IR [K-20261101T140100Z-juce-convolution-load-from-second-thread][K-20261029T030400Z-juce-convolution-default-state-and-gain]
- MPESynthesiser findFreeVoice/default zone with 15 member channels [K-20261009T092105Z-juce-mpesynthesiser-voice-allocation-and-default-zone]; ComboBoxAttachment linear spacing [K-20261009T164200Z-juce-combobox-attachment-spaces-items-linearly-over-the-parameter-range]; FontOptions version unknown [K-20261009T164400Z-juce-fontoptions-exists-on-master-without-stated-introduction-version]; ComboBox lacks getCurrentTextEditor in 8.0.15 [K-20261009T164300Z-juce-8-0-15-combobox-has-no-gettext-editor-accessor]
- Headless: ScopedJuceInitialiser_GUI for console tools [K-20261007T160027Z-c-028]; xvfb use is an inference only [K-20261007T160028Z-c-029]; no-editor host-parameter VST3 feasible [K-20261104T004600Z-juce-host-only-processor-contract]
- JUCE 9.0.5 macOS default deployment target 12.0 [K-20261104T005000Z-juce-905-parser-and-macos-limits]

## vst3
- JUCE_VST3_CAN_REPLACE_VST2 defaults 1 and can #error; set 0 [K-20261009T092101Z-juce-vst3-can-replace-vst2-default-and-error][K-20261104T003005Z-juce-9-vst3-cmake-options]; IS_SYNTH and NEEDS_MIDI_INPUT CMake options [K-20261104T003005Z-juce-9-vst3-cmake-options]
- Windows C:\Program Files\Common Files\VST3 not writable: COPY_PLUGIN_AFTER_BUILD fails 'Permission denied' [K-20261009T092103Z-vst3-system-folder-needs-write-access-windows]
- Ableton Live 12: VST3 only on Win/macOS, Apple-silicon builds needed natively; macOS path /Library/Audio/Plug-Ins/VST3/ [K-20261027T120000Z-live-vst3-support]
- Bundled VST3 SDK moved to juce_audio_processors_headless; MIT [K-20261007T160016Z-c-017][K-20261007T160015Z-c-016]; SDK 3.8.0 MIT in 9.0.5 [K-20261104T005100Z-vst3-sdk-mit-sbom]

## cmake-cpp-build
- JUCE 9.0.3 and 9.0.5 need CMake >= 3.22 [K-20261007T160004Z-c-005][K-20261104T003003Z-juce-9-cmake-minimum]; toolchain verified CMake 3.31.6 and 3.22.4, NumPy 2.2.6, SciPy 1.15.3, SoundFile 0.13.1; no-exec mount needs complete cmake/data tree copied [K-20261104T004500Z-pinned-toolchain-staging]
- Standalone target also compiles VST3 client: set macros via add_compile_definitions before add_subdirectory(JUCE) [K-20261009T092102Z-juce-standalone-target-compiles-vst3-client]
- Ninja+MSVC needs vcvars64 env and -DCMAKE_BUILD_TYPE [K-20261009T092107Z-msvc-ninja-needs-vcvars-environment]; windows-2025 is VS 18 2026 / cl 14.51 [K-20261007T160024Z-c-025][K-20261105T233000Z-windows-default-stack-vs-engine-size]
- Windows 1 MB stack: a 3.5 MB local crashes pre-main (0xC00000FD) [K-20261105T233000Z-windows-default-stack-vs-engine-size]
- Catch2 v3.16.0 commit 317ac1ed4c0bb6e6b91eafc817e05c488feffcb3 [K-20261007T160006Z-c-007]; nlohmann/json v3.12.0 commit 55f93686c01528224f448c19128836e7df245f72 [K-20261007T160007Z-c-008]

## ci-runners-and-actions
- Labels: ubuntu-24.04 x64, windows-2025 x64, macos-15 arm64, macos-15-intel; no -latest in frozen matrix [K-20261104T003007Z-versioned-github-runner-labels][K-20261106T120012Z-c-013-rainbow-vcv][K-20261007T160023Z-c-024]
- Tags/commits: checkout v7.0.1 3d3c42e5aac5ba805825da76410c181273ba90b1 [K-20261007T160017Z-c-018]; upload-artifact v7.0.2 cf430e030ddbb5b0abf93d22962f4752f3646cd9 [K-20261007T160019Z-c-020]; download-artifact v8.0.2 9000827ccba6bdab643e8b6fd33ac0654aef8333 [K-20261007T160020Z-c-021]; cache v6.1.0 55cc8345863c7cc4c66a329aec7e433d2d1c52a9 [K-20261007T160021Z-c-022]; pin by full SHA with tag comment [K-20261104T004300Z-immutable-github-action-pins]
- Breaking: setup-python v7 no pip-install input; download-artifact v8 digest mismatch fails; node24 [K-20261007T160136Z-c-097]
- Use explicit shell: bash (pipefail); default is bash -e [K-20261031T100200Z-github-actions-default-shell-pipefail]
- Windows checkout CRLF breaks sha256sum -c; .gitattributes 'tests/** text eol=lf' [K-20261029T030600Z-windows-checkout-crlf-hash-manifests]; frozen manifest must be re-frozen in the PR touching listed files, CI job sha256sum -c [K-20261101T200100Z-frozen-manifest-refreeze]
- Hosted-runner timing varies by CPU (EPYC 9V74 vs 7763; macOS 18.0-35.6% vs 17.0-18.3%): no absolute-timing gates [K-20261029T030800Z-github-hosted-runner-benchmark-variance]
- workflow_dispatch needs workflow on default branch [K-20261009T160121Z-dispatch-default-branch]; logs unreadable from sandbox, use ci-diag branch summary [K-20261009T160120Z-actions-blob-unreachable]; gh logs need --allow-escape-sequences and a finished job [K-20261029T030900Z-gh-run-logs-and-escape-sequences]
- Billing and label lists from protocol v3.15 are unsourced/unchecked: re-read GitHub pages [K-20261112T134510Z-github-hosted-runner-billing-2026-11][K-20261112T134500Z-github-hosted-runner-labels-2026-11]

## pluginval
- v1.0.4 (2024-12-04) commit ed19c2c16b57a6d94db391bea3ef4a80b769d5bf [K-20261007T160008Z-c-009]; Linux zip 5911681 B sha256 c01c49d8063965c4c2dea8324468336768f5c9139e0b1caebde14c2400b55352 [K-20261007T160009Z-c-010]
- macOS zip 9202795 B sha256 3c4c533bda0c5059eea3ddaea752d757ee2025041f0f47e6bcb0e87f6082b29f [K-20261007T160010Z-c-011]; Windows zip 2408590 B sha256 c08e61ce3b96db41636f8ec7e76f4c7e2c13ebdac7fa1b5a1f52b4f32ec715ab [K-20261007T160011Z-c-012]
- --strictness-level 1-10 default 5; --timeout-ms default 30000 [K-20261007T160012Z-c-013][K-20261007T160013Z-c-014]; strictness 10 used as gate in sibling plan [K-20261028T222647Z-pluginval-validation]
- CI guide's --validate-in-process does not exist in 1.0.4 [K-20261007T160014Z-c-015]; no stable 2.0.0, only v2.0.0-beta1..3; action Tracktion/pluginval/validate has no v2 tag [K-20261029T030000Z-pluginval-releases-and-action]
- Exit 0 is not coverage proof: assert log contents [K-20261104T005300Z-pluginval-exit-not-coverage-proof]; PluginInfoTest race fix commit fea38e7 (issue 149) postdates 1.0.4 [K-20261104T005200Z-pluginval-plugin-info-race]; auval presence on macos-15 unconfirmed [K-20261007T160025Z-c-026]

## sandbox
- Planning sandbox: Ubuntu 24.04, no sudo/cmake/pip; venv --without-pip + get-pip.py; CMake 4.4.4, Ninja 1.13.2 binaries worked; JUCE dev libs missing [K-20261007T160129Z-c-090]
- Builds exceed one 300 s call on 1 core; use CI [K-20261009T164500Z-juce-module-build-on-one-cpu-core-exceeds-a-300-second-tool-call]; background jobs need setsid nohup [K-20261009T120116Z-sandbox-background-jobs-and-git-proxy-limits]; /bin/sh is dash, use bash -c [K-20261004T162307Z-sandbox-shell-is-dash][K-20261009T234256Z-dash-lacks-pipestatus-and-time-keyword]
- apt-get update exits non-zero (nodesource 403) [K-20261009T234252Z-apt-install-needs-update-and-nodesource-update-fails-403]; add_repo (push) required before any repo access [K-20261009T120115Z-github-repo-access-is-per-session]; allowlist changes need a fresh container [K-20261009T193009Z-codeberg-allowlist-live-proxy-can-be-stale]
- github.io blocked [K-20261004T162305Z-github-io-unreachable-from-sandbox]; injected GIT_CONFIG_*/GH_TOKEN can break fetch [K-20261009T193504Z-proxy-injected-git-config]; shallow clone needs git fetch origin main before push (413) [K-20261009T120116Z-sandbox-background-jobs-and-git-proxy-limits]
- Apache-2.0 text at /usr/share/common-licenses/Apache-2.0 [K-20261009T233105Z-licence-texts-offline-in-sandbox]

## git-github
- Fine-grained PAT needs Workflows permission for .github/workflows [K-20261009T160122Z-token-scopes]; draft to ready only via GraphQL markPullRequestReadyForReview [K-20261009T160123Z-pr-draft]
- Git DB API fallback: plural PATCH git/refs/heads/{branch}, retry on replica lag [K-20261102T085800Z-github-git-database-api-writes-when-transport-blocked][K-20261004T151600Z-github-rest-api-bypasses-broken-pack-transport]; verify tree hashes [K-20261009T193503Z-github-web-upload-tree-hash]

## mutation-testing
- Mull 0.34.0 (May 2026): mull-19 bundles LLVM 19.1.7, pair with clang-19; build -O0 -g -grecord-command-line -fpass-plugin=/usr/lib/mull-ir-frontend-19; not Release [K-20261027T123200Z-mull-mutation-testing]
- mull-runner-19 options; include/exclude in mull.yml [K-20261029T030100Z-mull-runner-cli-and-config]; sqlite execution_status 2 = survived, 1 and 3 killed [K-20261029T030200Z-mull-sqlite-schema]
- Timings are estimates until first CI run; floor = first measured score minus 5 points [K-20261102T085900Z-mutation-ci-pricing-estimate-vs-measured]

## sanitizers
- clang -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=undefined; ASAN_OPTIONS=detect_leaks=0:halt_on_error=1; 6143 checks under 10 min [K-20261029T030700Z-asan-ubsan-juce-tests-in-actions]
- Zero-allocation processBlock check via counting operator new/delete with self-test [K-20261101T140200Z-test-executable-allocation-probe]

## modal-and-string-dsp
- Two-pole resonator with input zero x[n]-r cos(w)x[n-1] gives r^n cos(wn) [K-20261009T120109Z-two-pole-resonator-with-input-zero-gives-cosine-start]; damping sigma=s0+pi*eta*f+s2*f^2, T60=6.91/sigma (constants were estimates) [K-20261009T120114Z-engine-damping-law-parameters-are-estimates]
- Uniform noise std 1/sqrt(3): scale by 1.7321 or ~41 dB too quiet [K-20261009T120117Z-uniform-noise-needs-sqrt3-for-unit-variance]; Hertz pulse T=2.943*delta_max/v [K-20261009T120106Z-hertz-contact-pulse-and-duration]; fret at 1-1/r of scale [K-20261009T092106Z-fret-position-from-pitch-ratio]
- Prior spike: 8 voices, 0.015 sympathetic coupling, spectral radius 0.105, RTF 0.021304663 at 96 kHz/64, CI ceiling 0.25 [K-20261104T011300Z-eight-voice-lifecycle-results][K-20261104T011500Z-native-eight-voice-performance]; extended KS prior art [K-20261104T003008Z-extended-waveguide-plucked-strings]

## audio-metrics
- Block-size invariance: block 128 matches 512 within 0.008 dB; shorter blocks truncate decays [K-20261009T234224Z-oildrumkit-engine-output-depends-on-process-segmentation]
- Note-conditioned pitch window +/-50 cents; 21-cent regression limit [K-20261104T011100Z-analyser-known-answer-results]; spectral max is not a pitch estimator [K-20261104T003013Z-second-harmonic-dominates-reference-fft]; octave errors [K-20261004T162312Z-comb-occupancy-pitch-tracking]
- Detuned courses: analyse one beat period 1/(f0*(2^(c/1200)-1)) rectangular window [K-20261004T162313Z-beat-period-window-for-detuned-sources]; synthetic-fixture bias [K-20261009T160105Z-transcription-synthetic-bias]; numpy array vs scalar last-bit differences [K-20261004T151300Z-numpy-array-vs-scalar-ufunc-rounding-differs]

## reference-recordings
- TinySOL Zenodo 3685367 v6.0 CC BY 4.0, archive md5 36030a7fe389da86c3419e5ee48e3b7f, metadata md5 a86c9bb115f69e61f2f25872e397fc4a, 44.1 kHz 16-bit mono [K-20261007T160111Z-c-072]; files attack-trimmed; resampled neighbours excluded [K-20261007T160135Z-c-096]
- VSCO 2 CE CC0 commit 440300901dfe9275fd84e0b7763af1f8443ae62e, 44.1 kHz stereo 16-bit [K-20261104T003011Z-vsco-cc0-pizzicato-candidates]; ordinary pluck only [K-20261104T003012Z-pizzicato-reference-not-slap-evidence]

## listening-gate
- 12 seeded RMS-matched pairs, <=8/12 necessary not sufficient [K-20261106T120013Z-c-014-rainbow-vcv]; decay mismatch (spread 2.983474685004709 log2) means listening mandatory [K-20261104T011400Z-reference-spread-not-realism]; pair-builder RMS -23 dB built 4 of 15, needed -36 dB [K-20261105T223100Z-oildrum-hits-crest-factor-and-pair-builder-level]; prior gate failed (11,8,9,6,8,12 of 12) [K-20261106T180600Z-oildrumkit-listening-gate-results]; constant centroid sounds artificial [K-20261106T010000Z-pitch-flat-timbre-reads-as-synthetic]

## licensing
- JUCE 9 AGPLv3 or commercial [K-20261007T160003Z-c-004][K-20261104T003002Z-juce-9-agpl-commercial-license]; binaries linking JUCE 9 are AGPLv3 as a whole; TinySOL CC BY 4.0 attribution; ASIO GPLv3 only with JUCE_ASIO=1 [K-20261007T160137Z-c-098]; JUCE 8 tiers Starter $20,000 / Indie $300,000 [K-20261027T123100Z-juce8-licensing]; public artifacts are distribution [K-20261007T160139Z-c-100]

## python-tooling and tunings
- pip-tools 7.5.1 --require-hashes, list setuptools (80.9.0 flagged, 84.0.0 clean) [K-20261009T140031Z-pip-tools-hash-locking-build-backend]; pip-audit 2.10.0 --no-deps --disable-pip --strict [K-20261104T013000Z-pip-audit-pinned-offline-flags]
- Mandolin G3 D4 A4 E5 [K-20261009T164000Z-violin-family-mandolin-and-seven-string-guitar-tunings]; guitar MIDI 40,45,50,55,59,64 (G-B gap 4 semitones) [K-20261009T092108Z-standard-guitar-tuning-midi-and-hz]; f=440*2^((m-69)/12) [K-20261101T043000Z-twelve-tet-formula]
