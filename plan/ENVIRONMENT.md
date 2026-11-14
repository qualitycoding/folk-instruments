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
| Runner labels | `ubuntu-24.04` (x64), `windows-2025` (x64), `macos-15` (arm64), `macos-15-intel` (x64) | `actions/runner-images` README at commit `95e6f51a068507e8f43d061d2166a39d0ef36ce8` | C-047 |
| TinySOL | version 6.0, Zenodo record 3685367; `TinySOL.tar.gz` md5 `36030a7fe389da86c3419e5ee48e3b7f` (1 026 917 185 bytes); `TinySOL_metadata.csv` md5 `a86c9bb115f69e61f2f25872e397fc4a` | Zenodo record API | downloaded and checked in spike S07 (C-021) |
| Listening scripts | `qualitycoding/skills` commit `a20ed73`, `skills/audio-blind-listening-validation/scripts/` | copied into `tools/listening/` | `--help` of both scripts run 2026-11-14 |

The Python pins are in `tests/requirements.txt`, which is the lockfile for the test tooling (four direct packages; their own dependencies are resolved by pip at install time). The C++ dependencies are locked by commit in `CMakeLists.txt` (`FOLK_JUCE_COMMIT`, `FOLK_CATCH2_COMMIT`).

## 2. Setup on Ubuntu 24.04 (verified in the planning sandbox as root; CI prefixes `sudo`)

```
apt-get update
apt-get install -y --no-install-recommends libasound2-dev libfreetype-dev libfontconfig1-dev libx11-dev libxcomposite-dev libxcursor-dev libxext-dev libxinerama-dev libxrandr-dev libxrender-dev libglu1-mesa-dev mesa-common-dev xvfb
python3 -m pip install -r tests/requirements.txt
```

`apt-get update` returned success in the planning sandbox on 2026-11-14. In earlier sandboxes it exited non-zero because one third-party package source answered 403 (knowledge item K-20261009T234252Z). If that happens, run `apt-get update -o Dir::Etc::sourceparts=/dev/null` so that only the main sources list is read, and log the substitution in `DEVIATIONS.md`. The packages are the ones JUCE's `docs/Linux Dependencies.md` lists for the modules in use, without the optional ones switched off by `JUCE_WEB_BROWSER=0` and `JUCE_USE_CURL=0`.

## 3. Build and test commands (verified in the planning sandbox against the stubs)

Core, render tool and C++ tests, without JUCE (about one minute on 4 cores):

```
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DFOLK_BUILD_PLUGINS=OFF
cmake --build build
build/folk-tests
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
xvfb-run -a ctest --test-dir build-plugins --output-on-failure -E folk-perf
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
python3 -m pip_audit --strict -r tests/requirements.txt
```

State of the suite at the freeze (against the stubs): `build/folk-tests` runs 27 test cases and all 27 fail with `not implemented`; `build/folk-perf` fails the same way; the five host tests fail with `not implemented: createPluginFilter`; `pytest -m "not reference"` reports the tool-check tests passing (`test_metrics_selfcheck.py`, `test_pluginval_log_check.py`) and every other test failing on `folk-render failed with status 64` or, for the evidence guard, status 64 from the stub. Exact counts are in `plan/TRACEABILITY.md`.

## 4. Long builds in a recycling sandbox

The plugin build takes longer than one tool call in some sandboxes. Run it as `setsid nohup bash -c "cmake --build build-plugins > build-plugins.log 2>&1; echo EXIT=\$? >> build-plugins.log" < /dev/null &`, poll the log, and re-run the same command after a container recycle (Ninja continues where it stopped). Keep build directories outside the repository. If the sandbox cannot finish the build, rule DR-10 applies: the plugins are built and tested in CI only.

## 5. CI

`plan/ci/ci.yml` is the complete workflow; step `S-003` copies it to `.github/workflows/ci.yml` unchanged. Jobs: `freeze` (manifest and schema), `core` (4 runners: C++ tests, performance gate on `ubuntu-24.04`, audio behaviour tests), `plugins` (4 runners: plugin build, host tests, pluginval at strictness 10 with the log check, artifact upload with 3 days' retention), `reference` (TinySOL comparison), `audit` (pip-audit), and `all-green`, the single job to require in branch protection. Matrices use `fail-fast: false`.

Not verified at planning time, and therefore opened by `S-003` as its first action with a decision rule (1.3.6 item 4):

| Unverified item | First run shows | If it fails |
|---|---|---|
| The default CMake generator on `windows-2025` and on both macOS runners configures and builds the project with `cmake --build build --config Release` | the Configure and Build steps of the `core` job | halt with `BLOCKED.md` and the log excerpt (DR-14); a generator or toolchain change is an amendment to this page |
| `"-DCMAKE_OSX_ARCHITECTURES=arm64;x86_64"` builds universal plugins on both macOS runners (documented in JUCE `docs/CMake API.md`, "Building universal binaries for macOS") | the `plugins` job on `macos-15` and `macos-15-intel`; `lipo -archs` on one bundle binary must print both architectures (add that command to the step's log) | halt with `BLOCKED.md` |
| The pluginval archives unpack to `pluginval` (Linux), `pluginval.app/Contents/MacOS/pluginval` (macOS) and `pluginval.exe` (Windows) | the `find` listing printed by the download step | correct the three paths in the workflow to what the listing shows; log a deviation |
| pluginval's output contains the marker strings the log check expects (read from its v1.0.4 source, never observed) | `tests/ci/check_pluginval_log.py` on the first real log | if a marker differs from the source reading, write `TEST_CHALLENGE.md` with the log excerpt (the check is frozen) |
| The repository accepts pushes that add workflow files with the implementer's credential | the push in `S-003` | halt with `BLOCKED.md` naming the missing permission |

Per-environment performance target: `ubuntu-24.04` hosted runner, x64, 4 cores, Release build: every instrument at full polyphony at least 4 times faster than real time (T-013). No target on the other runners (D-086).
