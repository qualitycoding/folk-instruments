---
id: K-20261119T150100Z-github-runner-german-locales
statement: "German locales on GitHub hosted runners (2026-11): windows-2025 accepts de_DE.UTF-8, de_DE.utf8, de_DE, German_Germany.1252, German and de-DE for both setlocale and std::locale; macos-15 and macos-15-intel accept de_DE.UTF-8 and de_DE (not de_DE.utf8 or the Windows names); ubuntu-24.04 needs 'apt-get install locales' and 'locale-gen de_DE.UTF-8', after which the de_DE forms work. In each working case printf and a default C++ stream print 0,5."
status: current
supersedes: []
tags: [subject:ci-runners, phase:planning]
applies_to_version: "ubuntu-24.04, windows-2025, macos-15, macos-15-intel images of 2026-11"
source: { url: "https://github.com/qualitycoding/folk-instruments/actions", doi: "", title: "CI probe run 44535956613, jobs locale (four runners)", locator: "job log", accessed: "2026-11-19", tier: 2 }
confidence: verified
derived_from: []
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-19T15:01:00Z
---
Measured by a one-off probe workflow run at the owner's request to check planning assumptions; the probe branch was deleted after its logs were read.
