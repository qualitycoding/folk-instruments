---
id: K-20261115T010056Z-c-057-with-the-project-s-cmake-files-five-juce-plugins
statement: "With the project's CMake files, five JUCE plugins (VST3 and Standalone) and five headless host-test programs build from JUCE 8.0.17-security in 810 s on 4 cores; in this JUCE version AudioProcessor::createEditor() is private and a host calls createEditorAndMakeActive() (createEditorIfNeeded() is deprecated); a console program can host the wrapper by compiling its source and linking juce::juce_audio_utils."
status: current
supersedes: []
tags: [tech:juce, subject:juce, phase:research]
applies_to_version: "this run"
source: { url: "research/spikes/s10-plugin-build/build.log", doi: "", title: "planning spike S10", locator: "EXIT=0; time stamps 1794664297 and 1794665107", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-057]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:56Z
---
The committed log is the tail of the build output; it shows the last links and EXIT=0.

Input-file verdict: not-in-input. Load-bearing: yes. Informs: D-094, S-002, T-302.

All sources: planning spike S10 (EXIT=0; time stamps 1794664297 and 1794665107); JUCE framework source at tag 8.0.17-security (LICENSE.md, docs/Linux Dependencies.md, docs/CMake API.md, bundled VST3 SDK LICENSE.txt) (modules/juce_audio_processors_headless/processors/juce_AudioProcessor.h line 1027); planning spike S11 (editor created and destroyed with and without a display).
