# Research round 2

## What was done
R3 and R4, depth: the planner read the primary sources that the allowlist now reached (Millot and Baumann; Cohen and Rossing; Woodhouse; Quintavalla et al.; the encyclopaedia pages for layouts and tunings; the TinySOL record; the Philharmonia and Iowa pages; JUCE at the pinned tag; the runner-images README) and built the claim register (`research/claims.json`, first 51 claims). R6, spikes: S02 (JUCE build), S03 and S03b (minimal reed model and the volume condition), S04 (coupled string pair).

## Gaps found
Nine load-bearing claims below the corroboration bar; Brezas et al. 2023, Bahnson et al. 1998 and Ricot et al. 2005 unreadable (publishers refuse automated requests).

## Sources checked

- <https://arxiv.org/abs/2401.01606>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://www.jstage.jst.go.jp/article/ast/24/1/24_1_1/_article> (DOI 10.1250/ast.24.1), accessed 2026-11-14: **used**. read by the planner; full text
- <https://euphonics.org/wp-content/uploads/2022/03/Double_decays_JASA.pdf> (DOI 10.1121/10.0009012), accessed 2026-11-14: **used**. read by the planner; full text
- <https://euphonics.org/publication-list-jim-woodhouse/>, accessed 2026-11-14: **corroborating**. read by the planner; full text
- <https://doi.org/10.1163/27723194-bja10001> (DOI 10.1163/27723194-bja10001), accessed 2026-11-14: **used**. read by the planner; full text except tables, which are images
- <https://en.wikipedia.org/wiki/Richter-tuned_harmonica>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Harmonica>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Chromatic_harmonica>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Accordion_reed_ranks_and_switches>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Cassotto>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Melodica>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Bouzouki>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Irish_bouzouki>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Mandolin>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Inharmonicity>, accessed 2026-11-14: **corroborating**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Helmholtz_resonance>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://ccrma.stanford.edu/~jos/pasp/Stiff_String.html>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://ccrma.stanford.edu/~jos/pasp/Coupled_Strings.html>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://zenodo.org/records/3685367> (DOI 10.5281/zenodo.3685367), accessed 2026-11-14: **used**. read by the planner; record and metadata file
- <https://philharmonia.co.uk/resources/sound-samples/>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://theremin.music.uiowa.edu/MIS.html>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://github.com/juce-framework/JUCE>, accessed 2026-11-14: **used**. read by the planner; source read and built
- <https://github.com/actions/runner-images>, accessed 2026-11-14: **used**. read by the planner; README read
- <https://github.com/actions/checkout>, accessed 2026-11-14: **used**. read by the planner; tag lists
- <https://pypi.org/simple/>, accessed 2026-11-14: **used**. read by the planner; index queried with pip
- <https://github.com/github/choosealicense.com>, accessed 2026-11-14: **corroborating**. read by the planner; file copied
- <https://www.mdpi.com/2076-3417/13/7/4585> (DOI 10.3390/app13074585), accessed 2026-11-14: **unreachable**. refused by the publisher (HTTP 403) from the sandbox
- <https://pubs.aip.org/asa/jasa/article/103/4/2134/556883> (DOI 10.1121/1.421359), accessed 2026-11-14: **unreachable**. refused by the publisher (HTTP 403) from the sandbox
- <https://pubs.aip.org/asa/jasa/article-abstract/117/4/2279/543421> (DOI 10.1121/1.1852546), accessed 2026-11-14: **unreachable**. refused by the publisher (HTTP 403) from the sandbox
- <https://www.daddario.com/products/ej81-irish-bouzouki-strings>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://en.wikipedia.org/wiki/Overblowing>, accessed 2026-11-14: **used**. read by the planner; full text
- <https://commons.wikimedia.org/wiki/File:Tuning-Sound-G-Bouzouki.ogg>, accessed 2026-11-14: **used**. read by the planner; file page read by the round-3 reviewer
- <https://github.com/Tracktion/pluginval>, accessed 2026-11-14: **used**. read by the planner; source read by the round-3 reviewer
- web search: Millot Baumann "minimal model of free reeds" Acta Acustica 2007, 2026-11-14: **used**. located arXiv:2401.01606
- web search: Ricot Causse Misdariis blown-closed free reeds accordion reed pdf, 2026-11-14: **used**. located the JASA record and a HAL entry; no full text
- web search: Bahnson Antaki Beery diatonic harmonica 1998 pdf, 2026-11-14: **used**. located a copy on a host outside the allowlist; not read
- web search: Philharmonia sound samples licence terms, 2026-11-14: **used**. led to the Philharmonia page, which was then read
- web search: GitHub-hosted runners available images labels 2026, 2026-11-14: **corroborating**. led to the runner-images README, which was then read
- git tag lists (`git ls-remote --tags`) of juce-framework/JUCE, catchorg/Catch2, Tracktion/pluginval, actions/checkout, actions/upload-artifact, actions/download-artifact, actions/setup-python, actions/cache, ilammy/msvc-dev-cmd, mull-project/mull, steinbergmedia/vst3sdk, free-audio/clap, 2026-11-14: **used** (pins) or **not relevant** (msvc-dev-cmd, mull, vst3sdk, clap: not used by the plan).
