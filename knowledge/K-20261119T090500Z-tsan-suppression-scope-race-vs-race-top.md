---
id: K-20261119T090500Z-tsan-suppression-scope-race-vs-race-top
statement: "ThreadSanitizer suppressions: a race: pattern is matched against every frame of both stacks (and global names), a race_top: pattern only against the top frame; patterns match substrings of demangled frames, which end in the parameter list, so ^ns::Class::fn( matches exactly while a trailing $ never matches a function frame. Verified: race:^juce::Thread::entry( hid a race in non-JUCE code called from that function, race_top: did not; race_top:^juce::CanaryBox::bump( silenced a race whose top frame is that function and the near miss ...::bum( did not."
status: current
supersedes: []
tags: [subject:thread-sanitizer, phase:planning]
applies_to_version: "g++ 13.3.0 libtsan"
source: { url: "", doi: "", title: "planning sandbox probes 2026-11-18 (tsanfn/r.cpp, tsanfn/deep.cpp, canaries in tests/ci/)", locator: "", accessed: "2026-11-19", tier: 2 }
confidence: verified
derived_from: []
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-19T09:05:00Z
---
Measured in the planning sandbox by running the probe programs named in the source; recorded by the 4.7 assumption audit of this plan, which falsified the plan's earlier premise.
