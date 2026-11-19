---
id: K-20261119T090300Z-cpp-streams-follow-global-locale-not-setlocale
statement: "Default-constructed C++ streams format numbers by std::locale::global, which setlocale does not change: with g++ 13 and libstdc++ under de_DE.UTF-8 set by setlocale alone, printf('%g', 0.5) gives 0,5 while std::ostringstream << 0.5 gives 0.5; after std::locale::global(std::locale('de_DE.UTF-8')) the stream gives 0,5, and a stream imbued with std::locale::classic() gives 0.5 in both cases."
status: current
supersedes: []
tags: [subject:cpp-locale, phase:planning]
applies_to_version: "g++ 13.3.0, libstdc++ 13, glibc 2.39"
source: { url: "", doi: "", title: "planning sandbox probe 2026-11-19 (locprobe/p.cpp)", locator: "", accessed: "2026-11-19", tier: 2 }
confidence: verified
derived_from: []
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-19T09:03:00Z
---
Measured in the planning sandbox by running the probe programs named in the source; recorded by the 4.7 assumption audit of this plan, which falsified the plan's earlier premise.
