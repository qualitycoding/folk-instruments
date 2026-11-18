# Environment: pins and verified commands

Every pin below was looked up on 2026-11-14. "Verified" names the spike or source that showed the command or pin to work at that version. A substitution of anything on this page is a deviation: write it to `DEVIATIONS.md` when it is made.

## 1. Pins

| Item | Pin | Existence check | Verified by |
|---|---|---|---|
| JUCE | tag `8.0.17-security`, commit `dabd5ad13cd869cba41046947fffc8e5ce5cd662` (tag object `e548e97a54a083acbfc330d584419fd074409045`) | `git ls-remote --tags https://github.com/juce-framework/JUCE` | built in spikes S02, S10, S11 (C-043, C-057) |
| VST3 SDK | the copy bundled with that JUCE tag (MIT) | file `modules/juce_audio_processors_headless/format_types/VST3_SDK/LICENSE.txt` | C-044 |
| Catch2 | tag `v3.16.1`, commit `08092139210881f01a34e60c5f2fd6afa0ea4024` | `git ls-remote --tags https://github.com/catchorg/Catch2` | fetched and built in the core build (section 3) |
| pluginval | `v1.0.4`, tag commit `ed19c2c16b57a6d94db391bea3ef4a80b769d5bf`; archives `pluginval_Linux.zip` sha256 `c01c49d8063965c4c2dea8324468336768f5c9139e0b1caebde14c2400b55352`, `pluginval_macOS.zip` sha256 `3c4c533bda0c5059eea3ddaea752d757ee2025041f0f47e6bcb0e87f6082b29f`, `pluginval_Windows.zip` sha256 `c08e61ce3b96db41636f8ec7e76f4c7e2c13ebdac7fa1b5a1f52b4f32ec715ab` | tag list read 2026-11-14 (newest stable; 2.x is beta only) | command line read from the v1.0.4 source (C-045); hashes from knowledge items of the same version; **not run at planning time** (release downloads are refused in the planning sandbox). The CI step checks the hash before running it (section 5). |
| CMake | 3.22 or newer (`cmake_minimum_required`); 3.28.3 used in the sandbox | preinstalled | S02, S10 |
| Ninja | 1.11.1 in the sandbox (local builds only; CI uses each runner's default generator) | preinstalled | S02, S10 |
| C++ compiler | g++ 13.3.0 in the sandbox; C++20 | preinstalled | S02, S10 |
| Python | 3.13 | `actions/setup-python` input `python-version: "3.13"` | spikes ran on 3.13.18 |
| numpy | 2.5.3 | `pip index versions numpy` (2.5.4 is newer; 2.5.3 is what was installed and run) | spikes S03, S07, S08 |
| scipy | 1.18.1 | `pip index versions scipy` | S07, S08 |
| soundfile | 0.14.0 | `pip index versions soundfile` | S07, S08 |
| pytest | 9.2.0 | `pip index versions pytest` | S08 |
| pip-audit | 2.10.0 | installed from PyPI 2026-11-14 | `research/spikes/s11-headless-editor/pip_audit_output.txt` |
| actions/checkout | `v7.0.1`, `3d3c42e5aac5ba805825da76410c181273ba90b1` | `git ls-remote --tags` | C-046 |
| actions/setup-python | `v7.1.0`, `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` | same | C-046 |
| actions/upload-artifact | `v7.0.2`, `cf430e030ddbb5b0abf93d22962f4752f3646cd9` | same | C-046 |
| actions/cache | `v6.1.0`, `55cc8345863c7cc4c66a329aec7e433d2d1c52a9` | same | C-046 |
| actions/download-artifact | `v8.0.2`, `9000827ccba6bdab643e8b6fd33ac0654aef8333` | `git ls-remote --tags` (2026-11-15) | not run at planning time (section 5) |
| Runner labels | `ubuntu-24.04` (x64), `windows-2025` (x64), `macos-15` (arm64), `macos-15-intel` (x64) | `actions/runner-images` README at commit `95e6f51a068507e8f43d061d2166a39d0ef36ce8` | C-047 |
| TinySOL | version 6.0, Zenodo record 3685367; `TinySOL.tar.gz` md5 `36030a7fe389da86c3419e5ee48e3b7f`, sha256 `a537e5de4f64edf0a56032369f66fc76adcb67db875e466f54cad2999e00364c` (the row of `references/archives.csv`) (1 026 917 185 bytes); `TinySOL_metadata.csv` md5 `a86c9bb115f69e61f2f25872e397fc4a` | Zenodo record API | downloaded and checked in spike S07 (C-021) |
| Listening scripts | `qualitycoding/skills` commit `a20ed73`, `skills/audio-blind-listening-validation/scripts/` | copied into `tools/listening/` | `--help` of both scripts run 2026-11-14 |

The Python pins are in `tests/requirements.txt` (four direct packages) and, with every transitive dependency and its hashes, in `tests/requirements.lock`. Wheels for Python 3.13 exist for numpy 2.5.3 and scipy 1.18.1 on `win_amd64`, `macosx_14_0_arm64`, `macosx_14_0_x86_64` and `manylinux_2_28_x86_64` (PyPI file lists read 2026-11-15); soundfile and pytest are pure-Python or universal wheels; no runner builds from source. The C++ dependencies are locked by commit in `CMakeLists.txt` (`FOLK_JUCE_COMMIT`, `FOLK_CATCH2_COMMIT`).

The 689 extracted accordion files are hashed in the frozen list `tests/data/tinysol-accordion.sha256` (made 2026-11-16 from the archive above); both workflows check it after the cache or download step, so a poisoned or corrupted cache fails the job (R-053).

### TinySOL rows of the accordion reference set

The other columns are the same for all 14 rows: `instrument` `accordion`; `source_url` `https://zenodo.org/api/records/3685367/files/TinySOL.tar.gz/content`; `licence` `CC-BY-4.0`; `licence_url` `https://creativecommons.org/licenses/by/4.0/`; `accessed` `2026-11-14`; `redistributable` `true`; ids `accordion-001` to `accordion-014` in the order below; `velocity`, `sets` and `author` as `S-REF` action 4 says.

The 12 mf notes of D-050, then the two control notes of D-053 (MIDI 57 and 64, not among the 12), all chosen by D-052's tie rule from `TinySOL_metadata.csv` (md5 above) and hashed from the files of `TinySOL.tar.gz` (md5 above) on 2026-11-15; the first was also checked against the archive member directly. `S-REF` copies these into `references/index.csv`; if a fresh download gives a different hash, rule DR-11 applies as for any reference, except that losing any of these 12 rows is a halt with `BLOCKED.md` (T-200 and gate G-L3 depend on all 12); the row is never edited to match.

| MIDI | `file` | sha256 |
|---|---|---|
| 48 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-C3-mf-N-N.wav` | `8104a1b94189528cdadb8924c7f5f9078b97682fff803c2603c03855714f0147` |
| 52 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-E3-mf-N-N.wav` | `595a61999f8bf55d5cf12c9a3fa221ec35623548146b6f4dad1d31a24cba0df7` |
| 55 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-G3-mf-N-N.wav` | `ae260ca6b36e54fb09a3ab7c8c7756a28137bcd4f32e920c3dc0002c05b2d7ad` |
| 59 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-B3-mf-N-N.wav` | `6212e1a4fcae58b92cf869a2dae810a4cd7d955f333a4f724279beb29aa3e461` |
| 62 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-D4-mf-N-N.wav` | `ed4b652c6f8742b5984cf6fbfd7c8ff75e895fa675d71463b2e7426ee9bbeb15` |
| 65 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-F4-mf-N-N.wav` | `8972f9b19e44a3dce5735d3967b13daa2bff2aa9469f0143ff22d5f5f4427bb6` |
| 69 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-A4-mf-N-N.wav` | `86d7b1767461c4340dccc7bbe953395abe059741da8511f0649e157cfdb2115c` |
| 72 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-C5-mf-N-N.wav` | `3f622c5d45d900b717a4349fa501dd9d7a18bf5c8e7a26ea295022768be90e4e` |
| 76 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-E5-mf-N-N.wav` | `0d5c45ee87cfe9023efffa13dfa65fa789bcaab90093be781574c2058f833c61` |
| 79 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-G5-mf-N-N.wav` | `f1074a98319c2f76b3114a09a5d0395335695728bef4b96d31ecc13ce23664d4` |
| 83 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-B5-mf-N-N.wav` | `6649162d7d6576d768f1d13bf9426852998fe396236259da02e73ee102b522b2` |
| 86 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-D6-mf-N-N.wav` | `4a7aaf99956994e8ea86f760adffd0ea4746c04199f9aa983af641bf47bb012a` |
| 57 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-A3-mf-N-N.wav` | `6f34a60001b8ad521c58fbda5ca43f881a1439624a412d2bbabc8e6cb9c49350` |
| 64 | `tinysol/Keyboards/Accordion/ordinario/Acc-ord-E4-mf-N-N.wav` | `ca7c735847cc35131fc3034741f69f5c7ed7c24d33b37be7f49a4d2e4ebc7525` |

## 2. Setup on Ubuntu 24.04 (verified in the planning sandbox as root; CI prefixes `sudo`)

```
apt-get update
apt-get install -y --no-install-recommends libasound2-dev libfreetype-dev libfontconfig1-dev libx11-dev libxcomposite-dev libxcursor-dev libxext-dev libxinerama-dev libxrandr-dev libxrender-dev libglu1-mesa-dev mesa-common-dev xvfb
apt-get install -y --no-install-recommends locales && locale-gen de_DE.UTF-8
python3 -m pip install --require-hashes -r tests/requirements.lock
```

`tests/requirements.lock` is generated from `tests/requirements.txt` by `uv pip compile --universal --generate-hashes --python-version 3.13 --no-header tests/requirements.txt -o tests/requirements.lock` (uv 0.11.32, 2026-11-15) and lists every transitive package with its hashes for all four platforms; CI installs only from it (R-030). A pin change regenerates it in the same commit. The German locale is needed by the locale tests (T-016, T-302).

`apt-get update` returned success in the planning sandbox on 2026-11-14. In earlier sandboxes it exited non-zero because one third-party package source answered 403 (knowledge item K-20261009T234252Z). If that happens, run `apt-get update -o Dir::Etc::sourceparts=/dev/null` so that only the main sources list is read, and log the substitution in `DEVIATIONS.md`. The packages are the ones JUCE's `docs/Linux Dependencies.md` lists for the modules in use, without the optional ones switched off by `JUCE_WEB_BROWSER=0` and `JUCE_USE_CURL=0`.

## 3. Build and test commands (verified in the planning sandbox against the stubs)

Core, render tool and C++ tests, without JUCE (about one minute on 4 cores):

```
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DFOLK_BUILD_PLUGINS=OFF
cmake --build build
build/folk-tests
build/folk-locale-tests
build/folk-perf
```

Audio behaviour tests (run from `tests/`; `FOLK_RENDER` must be an absolute path):

```
cd tests && FOLK_RENDER="$PWD/../build/folk-render" python3 -m pytest -m "not reference"
```

Reference tests (need the TinySOL accordion notes extracted under `$FOLK_TINYSOL`, with `TinySOL_metadata.csv` beside the `Keyboards` folder; `FOLK_REF_ROOT` is the directory of the files named in `references/index.csv`):

```
cd tests && FOLK_RENDER="$PWD/../build/folk-render" FOLK_TINYSOL=/path/to/tinysol FOLK_REF_ROOT=/path/to/refs python3 -m pytest -m reference -s
```

Plugins and host tests (810 s on 4 cores in the planning sandbox; JUCE is fetched by git at the pinned commit unless `-DFOLK_JUCE_DIR=<checkout>` names an existing checkout at that commit):

```
cmake -S . -B build-plugins -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build-plugins
xvfb-run -a ctest --test-dir build-plugins --no-tests=error --output-on-failure -E folk-perf
```

A headless program can create and destroy a JUCE editor on Linux with or without a display (spike S11); `xvfb-run -a` is kept because pluginval opens real windows.

Freeze manifest and schema check:

```
sha256sum -c tests/FROZEN_MANIFEST.sha256
python3 scripts/check_knowledge_schema.py
```

Dependency scan:

```
python3 -m pip install pip-audit==2.10.0
python3 -m pip_audit --strict --require-hashes -r tests/requirements.lock
```

State of the suite at the freeze (against the stubs): `build/folk-tests` runs 27 test cases and all 27 fail with `not implemented`; `build/folk-locale-tests` runs 2 and both fail the same way; `build/folk-perf` fails the same way; the five host programs (9 test cases each) fail with `not implemented: createPluginFilter`; `pytest -m "not reference"` reports the tool-check tests passing (`test_metrics_selfcheck.py`, `test_pluginval_log_check.py`, `test_tsan_supp_check.py`) and every other test failing on `folk-render failed with status 64` or, for the evidence guard and the fetch tool (T-210, T-211), status 64 from their stubs. Exact counts are in `plan/TRACEABILITY.md`.

## 4. Long builds in a recycling sandbox

The plugin build takes longer than one tool call in some sandboxes. Run it as `setsid nohup bash -c "cmake --build build-plugins > build-plugins.log 2>&1; echo EXIT=\$? >> build-plugins.log" < /dev/null &`, poll the log, and re-run the same command after a container recycle (Ninja continues where it stopped). Keep build directories outside the repository. If the sandbox cannot finish the build, rule DR-10 applies: the plugins are built and tested in CI only.

## 5. CI

`plan/ci/ci.yml` is the complete workflow; step `S-003` copies it to `.github/workflows/ci.yml` unchanged. Jobs: `freeze` (manifest and schema), `core` (4 runners: C++ tests, locale tests, performance gate on `ubuntu-24.04`, audio behaviour tests), `plugins` (4 runners: plugin build, host tests with their count checked, pluginval at strictness 10 with the log check, artifact upload with 3 days' retention), `host-tsan` (`ubuntu-24.04`: the host tests built with ThreadSanitizer, running T-304), `reference` (TinySOL comparison), `audit` (pip-audit), and `all-green`, the single job to require in branch protection. Matrices use `fail-fast: false`.

Not verified at planning time, and therefore opened by `S-003` as its first action with a decision rule (1.3.6 item 4):

| Unverified item | First run shows | If it fails |
|---|---|---|
| The default CMake generator on `windows-2025` and on both macOS runners configures and builds the project with `cmake --build build --config Release` | the Configure and Build steps of the `core` job | halt with `BLOCKED.md` and the log excerpt (DR-14); a generator or toolchain change is an amendment to this page |
| `"-DCMAKE_OSX_ARCHITECTURES=arm64;x86_64"` builds universal plugins on both macOS runners (documented in JUCE `docs/CMake API.md`, "Building universal binaries for macOS") | the `plugins` job on `macos-15` and `macos-15-intel`; `lipo -archs` on one bundle binary must print both architectures (add that command to the step's log) | halt with `BLOCKED.md` |
| The pluginval archives unpack to `pluginval` (Linux), `pluginval.app/Contents/MacOS/pluginval` (macOS) and `pluginval.exe` (Windows) | the `find` listing printed by the download step | correct the three paths in the workflow to what the listing shows; log a deviation |
| pluginval's output contains the marker strings the log check expects (read from its v1.0.4 source, never observed) | `tests/ci/check_pluginval_log.py` on the first real log | if a marker differs from the source reading, write `TEST_CHALLENGE.md` with the log excerpt (the check is frozen) |
| The repository accepts pushes that add workflow files with the implementer's credential | the push in `S-003` | halt with `BLOCKED.md` naming the missing permission |
| `actions/download-artifact` v8.0.2 reads the artifact written by `actions/upload-artifact` v7.0.2 in the `gate-evidence` workflow | the first marker run, in `S-210` | pin the `download-artifact` release that the `upload-artifact` release notes name as compatible; log a deviation |
| ThreadSanitizer starts on the runner (a kernel with high `vm.mmap_rnd_bits` makes it abort with 'unexpected memory mapping'; the job sets it to 28 first) | the `host-tsan` job in `S-003` | if it still aborts at start-up, run each program under `setarch -R` and log a deviation |
| The `host-tsan` job's ThreadSanitizer build of JUCE runs T-304 without reports from inside JUCE itself (no source file may be built without the sanitiser: the job fails on any `no_sanitize` or `-fno-sanitize` in the build or sources; suppression lines take the form `race:^juce::<Class>::<function>(`, which the named canary shows to work) | the `host-tsan` job in `S-003` (it fails there at its test step, after building) and `S-320` | a report whose every frame lies in JUCE module code goes into `tests/ci/tsan.supp` only with a `DEVIATIONS.md` entry naming it; a report with a frame in `plugins/` or `core/` is a defect, never suppressed |
| The `gate-evidence` workflow's token may push the branch `evidence/<gate>` (the repository's Actions setting 'Workflow permissions' must allow write access; the workflow asks for `contents: write`) | the first marker commit, in `S-210` | halt with `BLOCKED.md` asking the owner to allow read and write permissions for workflows in the repository settings |

Per-environment performance target: `ubuntu-24.04` hosted runner, x64, 4 cores, Release build: every instrument at full polyphony at least 4 times faster than real time (T-013). No target on the other runners (D-086).
