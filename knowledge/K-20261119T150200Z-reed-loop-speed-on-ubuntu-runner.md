---
id: K-20261119T150200Z-reed-loop-speed-on-ubuntu-runner
statement: "The bare minimal free-reed loop of planning spike S05 (64 reeds, 4 x 48 kHz base rate, semi-implicit Euler) runs 4.87 times faster than real time at C = 110 steps per period and 4.65 times at C = 160 on a GitHub ubuntu-24.04 hosted runner (Intel Xeon Platinum 8370C, 4 cores, best of 3, about 16.8 ns per reed step), against 7.46 and 7.06 times on the planning sandbox (Xeon 2.1 GHz)."
status: current
supersedes: []
tags: [subject:free-reed-modelling, phase:planning]
applies_to_version: "ubuntu-24.04 runner image 20261116"
source: { url: "https://github.com/qualitycoding/folk-instruments/actions", doi: "", title: "CI probe run 44535956613, job reed-cost; sandbox re-run of research/spikes/s05-reed-cost", locator: "job log", accessed: "2026-11-19", tier: 2 }
confidence: verified
derived_from: []
discovered_by: planner
run: gen-20261114T004707Z-folk-instruments-vst
recorded_at: 2026-11-19T15:02:00Z
---
Measured by a one-off probe workflow run at the owner's request to check planning assumptions; the probe branch was deleted after its logs were read.
