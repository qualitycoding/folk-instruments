---
id: K-20261119T090400Z-gcc-tsan-hooks-in-trivial-objects
statement: "With g++ 13.3 and -fsanitize=thread, every object file references __tsan_init, including an empty translation unit and a data-only one, while __tsan_func_entry is omitted for functions with no instrumented memory access or call (for example double f(double x){return x*2.0+1.0;} at -O2)."
status: current
supersedes: []
tags: [subject:thread-sanitizer, phase:planning]
applies_to_version: "g++ 13.3.0"
source: { url: "", doi: "", title: "planning sandbox probe 2026-11-19 (locprobe/empty.cpp, data.cpp, pure.cpp) and planning audit TP-TSAN-2", locator: "", accessed: "2026-11-19", tier: 2 }
confidence: verified
derived_from: []
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-19T09:04:00Z
---
Measured in the planning sandbox by running the probe programs named in the source; recorded by the 4.7 assumption audit of this plan, which falsified the plan's earlier premise.
