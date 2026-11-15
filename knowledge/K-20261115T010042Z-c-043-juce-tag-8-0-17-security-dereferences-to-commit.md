---
id: K-20261115T010042Z-c-043-juce-tag-8-0-17-security-dereferences-to-commit
statement: "JUCE tag 8.0.17-security dereferences to commit dabd5ad13cd869cba41046947fffc8e5ce5cd662 (2026-11-02); it differs from 8.0.15 (91ad83ae34a81e0833b1a2b0866f54846370ae53) by hardening of file, XML, JSON, ZIP, image and ValueTree parsing; a VST3 plus Standalone instrument plugin builds from it with CMake 3.28.3, Ninja 1.11.1 and g++ 13.3.0 on Ubuntu 24.04 in 88 s on 4 cores after installing 13 development packages, with juce_add_plugin(... FORMATS VST3 Standalone IS_SYNTH TRUE NEEDS_MIDI_INPUT TRUE COPY_PLUGIN_AFTER_BUILD FALSE) and JUCE_VST3_CAN_REPLACE_VST2=0."
status: current
supersedes: []
tags: [tech:juce, subject:juce, phase:research]
applies_to_version: "tag 8.0.17-security, commit dabd5ad13cd869cba41046947fffc8e5ce5cd662, 2026-11-02"
source: { url: "https://github.com/juce-framework/JUCE", doi: "", title: "JUCE framework source at tag 8.0.17-security (LICENSE.md, docs/Linux Dependencies.md, docs/CMake API.md, bundled VST3 SDK LICENSE.txt)", locator: "git log of the tag; docs/Linux Dependencies.md; docs/CMake API.md", accessed: "2026-11-14", tier: 1 }
confidence: verified
derived_from: [C-043]
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-15T01:00:42Z
---
JUCE 9 is the current major release (9.0.5 on the same day); the choice of the JUCE 8 maintenance line is decision D-080.

Input-file verdict: not-in-input. Load-bearing: yes. Informs: D-080, S-002.

All sources: JUCE framework source at tag 8.0.17-security (LICENSE.md, docs/Linux Dependencies.md, docs/CMake API.md, bundled VST3 SDK LICENSE.txt) (git log of the tag; docs/Linux Dependencies.md; docs/CMake API.md); planning spike S02 (configure.log, build.log (EXIT=0)).
