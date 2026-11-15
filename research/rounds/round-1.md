# Research round 1

## What was done
R0: the lesson store (251 matching active lessons) and the knowledge store (323 matching items) were digested (`research/r0/`). R1: the question tree (`research/QUESTIONS.md`). R2, breadth: six workers, one per branch (free reeds, harmonica, accordion and melodion, plucked strings, mandolin and bouzouki, reference recordings), each testing the owner's input file statement by statement. Spike S01 recomputed the file's tables.

## Access failure
The fetch tool could not resolve hosts outside the environment's network allowlist and the search tool hit a usage limit, so every worker read its sources at search-snippet or abstract level only. No claim from this round was accepted as corroborated. Lesson: `lessons/L-20261114T090000Z-fetch-tool-shares-sandbox-allowlist.md`. The owner then approved adding 20 literature, dataset and manufacturer hosts to the allowlist; a later request for five more was refused by the service, which left `www.cs.bu.edu` (a copy of Bahnson et al. 1998) and `web.archive.org` out of reach.

## Outcome
151 worker claims (files `r1-*.json`): the input file's computed tables are arithmetically right; many of its attributions could not be traced (reed Q values and thresholds, laser-vibrometer pressures, cassotto figures' origin, melodica experiments, the mandolin '318 against 423 Hz' pair, 'mandolin #95'); its melodica ranges and its light mandolin string set are wrong.

## Sources checked

- <https://arxiv.org/pdf/2401.01606>, accessed 2026-11-14: **used**. Abstract-level: model, stability, thickness effects, Fletcher labels
- <https://ar5iv.labs.arxiv.org/html/2401.01606>, accessed 2026-11-14: **unreachable**. host not allowed
- <https://hal.archives-ouvertes.fr/hal-01106161>, accessed 2026-11-14: **unreachable**. host not allowed
- <https://www.phys.unsw.edu.au/music/people/publications/Tarnopolskyetal2000.pdf>, accessed 2026-11-14: **unreachable**. host not allowed
- <https://researchportalplus.anu.edu.au/en/publications/oscillating-reed-valves-an-experimental-study/>, accessed 2026-11-14: **used**. Bibliographic and abstract summary
- <https://resolve.cambridge.org/core/journals/journal-of-fluid-mechanics/article/aerodynamic-excitation-of-the-harmonium-reed/3B5156625194BBF5549B08928B2F5495>, accessed 2026-11-14: **used**. Abstract and bibliographic data
- <https://dael.euracoustics.org/confs/fa2023/data/articles/000853.pdf>, accessed 2026-11-14: **used**. Summary of St. Hilaire; harmonium LDV B5 reed; distributed bar model
- <https://www.cs.bu.edu/fac/snyder/TablatureWeb/BERLIN2.PDF>, accessed 2026-11-14: **used**. Frequency-pressure relationship, reed cell effects
- <https://physicstoday.aip.org/features/acoustics-of-free-reed-instruments>, accessed 2026-11-14: **used**. Blown-closed behaviour of Western reeds
- <https://www.cs.bu.edu/fac/snyder/TablatureWeb/Bahnson%20JASA%201998.pdf>, accessed 2026-11-14: **used**. Primary reed closing, companion reed blown open
- <https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_crossref_primary_10_1121_1_406857>, accessed 2026-11-14: **used**. Four configurations of one-degree-of-freedom valves
- <https://lampz.tugraz.at/~hadley/memm/mechanics/cbeam.php>, accessed 2026-11-14: **used**. Cantilever wavenumber and root equation
- <https://euphonics.org/11-6-free-reeds/>, accessed 2026-11-14: **not relevant**. not opened
- <https://colinpykett.org.uk/physics-of-free-reed-wind-instruments.htm>, accessed 2026-11-14: **not relevant**. not opened
- <https://arxiv.org/html/0810.2870v1>, accessed 2026-11-14: **not relevant**. not opened
- <https://arxiv.org/html/2401.01606v1>, accessed 2026-11-14: **unreachable**. arxiv.org not in allowed hosts
- <https://www.phys.unsw.edu.au/jw/reprints/WolfeSmithAA.pdf>, accessed 2026-11-14: **unreachable**. host not allowed
- <https://bluesharmonica.com/real_time_magnetic_resonance_imaging_fo_upper_airways_during_harmonica_pitch_bends_0>, accessed 2026-11-14: **unreachable**. host not allowed
- <https://ccrma405080.stanford.edu/events/peter-r-egbert-real-time-magnetic-resonance-imaging-of-vocal-tract-during-harmonica-pitch-ben>, accessed 2026-11-14: **unreachable**. host not allowed
- <https://doi.org/10.1121/1.421359> (DOI 10.1121/1.421359), accessed 2026-11-14: **unreachable**. host not allowed
- <https://en.wikipedia.org/wiki/Richter-tuned_harmonica>, accessed 2026-11-14: **unreachable**. host not allowed
- <https://harp-l.org/pipermail/harp-l/2014-May/msg00008.html>, accessed 2026-11-14: **corroborating**. snippet only
- <https://www.learntheharmonica.com/post/harmonica-notes-easy-guide-layout>, accessed 2026-11-14: **corroborating**. snippet only
- <https://www.brendan-power.com/images/POWERBENDER_BOOK_SAMPLE.pdf>, accessed 2026-11-14: **corroborating**. snippet only
- <https://www.musicjunction.com.au/products/hohner-marine-band-classic-1896-10-hole-diatonic-harmonica>, accessed 2026-11-14: **corroborating**. snippet only
- <https://www.bluesharmonica.com/website_dedicated_physics_harmonica>, accessed 2026-11-14: **corroborating**. snippet only
- <https://www.bluesharmonica.com/two_half_valving_strategies_diatonic_harmonicas>, accessed 2026-11-14: **used**. snippet only
- <https://en.wikipedia.com/wiki/Chromatic_harmonica>, accessed 2026-11-14: **used**. snippet only
- <https://hohner.de/en/instruments/harmonicas/chromatic/chrometta/chrometta-12>, accessed 2026-11-14: **used**. snippet only
- <https://harpsurgery.com/hand-tremolo>, accessed 2026-11-14: **used**. snippet only
- <https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6635814>, accessed 2026-11-14: **used**. snippet only
- <https://last.hit.bme.hu/sites/default/files/documents/Rudas_Annamaria_-_Szakdolgozat_2021.pdf>, accessed 2026-11-14: **used**. snippet only
- <https://www.dafx.de/paper-archive/2023/DAFx23_paper_47.pdf>, accessed 2026-11-14: **corroborating**. snippet only
- <https://euracoustics.org/documents/14/AiP_2021_02_Accordion_acoustics.pdf>, accessed 2026-11-14: **used**. Pitch-bend measurements on a concert accordion
- <https://dael.euracoustics.org/confs/fa2026/data/articles/000418.pdf>, accessed 2026-11-14: **used**. Vent-hole pressure loss mechanism
- <https://acta-acustica.edpsciences.org/10.1051/aacus/2024020> (DOI 10.1051/aacus/2024020), accessed 2026-11-14: **unreachable**. host blocked
- <https://en.wikipedia.org/wiki/Accordion>, accessed 2026-11-14: **unreachable**. host not allowed
- <https://www.libertybellows.com/general-accordion-questions.htm>, accessed 2026-11-14: **used**. Cited by a round-1 worker for: Register letters: L = 16' bassoon rank (one octave below written pitch), M = 8' clarinet rank (unison), H = 4' piccolo rank (one 
- <https://www.accordionists.info/threads/making-sense-out-of-cents.14511/latest>, accessed 2026-11-14: **used**. Cited by a round-1 worker for: Musette detuning is quoted in cents at A4 or beats per second; a typical shop rule is about 1 Hz = 3.5 cents mid-keyboard; style 
- <https://en.wikibooks.org/wiki/Accordion/Reed_Ranks_and_Switches>, accessed 2026-11-14: **used**. Cited by a round-1 worker for: Register letters: L = 16' bassoon rank (one octave below written pitch), M = 8' clarinet rank (unison), H = 4' piccolo rank (one 
- <https://usa.yamaha.com/products/musical_instruments/winds/pianica/p-37d/index.html>, accessed 2026-11-14: **used**. Cited by a round-1 worker for: Yamaha describes the P-37D Pianica as 37 keys covering F3 to F6 (three octaves).
- <https://www.hohner.de/en/instruments/melodica/student-melodicas/student-32-melodica>, accessed 2026-11-14: **used**. Cited by a round-1 worker for: Hohner lists the Student 32 range as f (small octave) to c (three-lined octave), which in German notation is F3 to C6 in scientif
- <https://melodicaworld.com/?p=11741>, accessed 2026-11-14: **used**. Cited by a round-1 worker for: The long-tube experiment: a melodica builder forum thread ('Tubes - some experiments', melodicaworld.com) reports no significant 
- <https://isma2017.cirmmt.mcgill.ca/proceedings/pdf/ISMA_2017_paper_52.pdf>, accessed 2026-11-14: **used**. Cited by a round-1 worker for: A Hatton study of harmonica note bending (leshatton.org, May 2015) and a McGill thesis (escholarship.mcgill.ca mc87pt57q) and an 
- <https://pubs.aip.org/asa/jasa/article/150/6/4375/994397/A-necessary-condition-for-double-decay-envelopes>, accessed 2026-11-14: **used**. Bibliographic record and abstract wording
- <https://arxiv.org/pdf/2104.02480>, accessed 2026-11-14: **unreachable**. 'Pickers' Guide to Acoustics of the Banjo', parts I and II (Politzer, Woodhouse, Mansour). A round-1 worker took this to be the preprint of Woodhouse's double-d
- <https://www.repository.cam.ac.uk/items/3d2cfb54-a00d-4dbb-8e08-69099990d8b2>, accessed 2026-11-14: **unreachable**. Cited by a round-1 worker for: Woodhouse's paper is J. Woodhouse, 'A necessary condition for double-decay envelopes in stringed instruments', J. Acoust. Soc. Am
- <https://euphonics.org/7-3-multiple-strings-and-double-decays/>, accessed 2026-11-14: **unreachable**. Exists per search; not opened
- <https://eprints.soton.ac.uk/476996/1/Pablo_Miranda_Internoise2022.pdf>, accessed 2026-11-14: **corroborating**. Relays Woodhouse criterion and Weinreich mechanism
- <https://www.dsprelated.com/freebooks/pasp/String_Coupling_Effects.html>, accessed 2026-11-14: **corroborating**. Vertical vs horizontal polarisation decay
- <https://ccrma.stanford.edu/software/stk/classstk_1_1Mandolin.html>, accessed 2026-11-14: **used**. STK Mandolin class reference: two detuned plucked strings with a commuted body response; the page warns that commuted synthesis was covered by a Stanford patent
- <https://purl.stanford.edu/wp454hs7976>, accessed 2026-11-14: **used**. Existence, year, advisors
- <https://www.dafx.de/paper-archive/2010/DAFx10/PerngSmithRossing_DAFx10_P93.pdf>, accessed 2026-11-14: **used**. Plectrum shape from bent-beam equations
- <https://core.ac.uk/download/357253971.pdf>, accessed 2026-11-14: **used**. B definition and listening thresholds exist
- <https://acta-acustica.edpsciences.org/10.1051/aacus/2020008>, accessed 2026-11-14: **used**. Existence, admittance figure
- <https://phys.unsw.edu.au/jw/Helmholtz.html>, accessed 2026-11-14: **corroborating**. Guitar air mode approx Helmholtz
- <https://www.rose-hulman.edu/~moloney/Acoustics/0506/End_correction_Meeks_0506.doc>, accessed 2026-11-14: **corroborating**. 0.85 r flanged, 0.6 r unflanged
- <https://www.firgelliauto.com/blogs/engineering-calculators/helmholtz-resonator-calculator>, accessed 2026-11-14: **corroborating**. Formula with garbled/incorrect end-correction assignment
- <https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9224380>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: End corrections: the textbook per-end values are about 0.85 r for a flanged opening and about 0.6 r (0.61 r) for an unflanged ope
- <https://www.dsprelated.com/freebooks/pasp/Commuted_Synthesis.html>, accessed 2026-11-14: **used**. Cited by a round-1 worker for: Commuted synthesis (Smith): because the linear parts of a plucked-string instrument commute, the body response can be moved befor
- <https://csound.com/manual/STKMandolin.html>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: Commuted synthesis (Smith): because the linear parts of a plucked-string instrument commute, the body response can be moved befor
- <https://typeset.io/papers/tunable-dispersion-filter-design-for-piano-synthesis-fy4bq64bfk>, accessed 2026-11-14: **used**. Second-order allpass cascade, Thiran-based
- <https://bibbase.org/network/publication/abel-vlimki-smith-robustefficientdesignofallpassfiltersfordispersivestringsoundsynthesis-2010>, accessed 2026-11-14: **used**. Cited by a round-1 worker for: Dispersion allpass design: Rauhala and Valimaki, 'Tunable dispersion filter design for piano synthesis', IEEE Signal Processing L
- <https://dafx.de/paper-archive/details/FxpIAYIVGkUKoqVYzYCHQg>, accessed 2026-11-14: **used**. Very high-order allpass design
- <https://dafx.de/paper-archive/details/XJTIoSIXj3qqer3WzLlEHQ>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: The input file does not cite Germain and Evangelista; the task cites 'Synthesis of guitar by digital waveguides: modeling the ple
- <https://dafx.de/paper-archive/details/PywhUlPUhwQUW7fKB6OHXQ>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: The input file does not cite Germain and Evangelista; the task cites 'Synthesis of guitar by digital waveguides: modeling the ple
- <https://concept.lib.ed.ac.uk/esjs/article/download/9815/12844>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: For a solid round wire of diameter d, Young's modulus E, tension T, vibrating length L, the stiff-string partials are f_n = n f_0
- <https://www.ioa.org.uk/system/files/publications/P%20CHUMNANTAS%20CA%20GREATED%20DM%20CAMPBELL%20INHARMONICITY%20OF%20STEPPED%20STIFF%20STRINGS.pdf>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: For wound strings the inharmonicity stiffness is usually taken from the core only (windings contribute little bending stiffness),
- <https://www.ece.uvic.ca/~bctill/papers/numacoust/V%c3%a4lim%c3%a4ki_etal_2006.pdf>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: Karplus-Strong reduces to a single delay loop with a loop filter and is a simplified digital waveguide; Jaffe and Smith (1983) ex
- <https://www.ioa.org.uk/system/files/publications/AR%20BAXANDALL%20IS%20BROWN%20CE%20GOUGH%20VIBRATIONS%20OF%20PIANO%20STRINGS%20AND%20COUPLING%20TO%20THE%20SOUNDBOARD.pdf>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: Weinreich, 'Coupled piano strings', J. Acoust. Soc. Am. 62, 1474-1484 (1977) exists. Its explanation of the two-stage piano decay
- <https://www.dsprelated.com/dspbooks/pasp/String_Coupling_Effects.html>, accessed 2026-11-14: **unreachable**. Not read (unreachable).
- <https://www.speech.kth.se/music/5_lectures/weinreic/weinreic.html>, accessed 2026-11-14: **unreachable**. Not read (unreachable).
- <https://www.bohrium.com/paper-details/a-necessary-condition-for-double-decay-envelopes-in-stringed-instruments/814713989719130112-582>, accessed 2026-11-14: **unreachable**. Not read (unreachable).
- <https://dafx.de/paper-archive/details/_B8kl7InKAjA221WjmV8Eg>, accessed 2026-11-14: **unreachable**. Not read (unreachable).
- <https://typeset.io/pdf/simple-model-for-low-frequency-guitar-function-plccqpv99x.pdf>, accessed 2026-11-14: **used**. Two-oscillator guitar model
- <https://repositori.upf.edu/items/7c207d44-4ac0-4100-a216-dc814a1abe60/full>, accessed 2026-11-14: **used**. Admittance + radiativity filter modelling
- <https://www.jstage.jst.go.jp/article/ast/24/1/24_1_1/_article>, accessed 2026-11-14: **not relevant**. Outside this branch; abstract mentions TV holography of four mandolins and a mandola
- <https://ccrma.stanford.edu/%7Ejos/pasp/EDR_Based_Loop_Filter_Design.html>, accessed 2026-11-14: **corroborating**. Loop filter fitting to decay
- <https://www.Wikipedia.com/wiki/Mandolin>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: Tremolo: no measured stroke rates, up/down asymmetry or re-excitation studies were found. Only (a) Wikipedia's statement that man
- <https://youtubemusicsucks.com/how-to-tremolo-pick-a-mandolin/>, accessed 2026-11-14: **corroborating**. Cited by a round-1 worker for: Tremolo: no measured stroke rates, up/down asymmetry or re-excitation studies were found. Only (a) Wikipedia's statement that man
- <https://openreview.net/pdf/617931ce90da4c3b1e5b20551bd1cd1a4b93c1b4.pdf>, accessed 2026-11-14: **not relevant**. Plucked-string synthesis paper (search hit); No mandolin data.
- <https://www.mdpi.com/2076-3417/13/7/4585> (DOI 10.3390/app13074585), accessed 2026-11-14: **unreachable**. host www.mdpi.com does not resolve from sandbox
- <https://acoustics.org/pressroom/httpdocs/139th/cohen.htm>, accessed 2026-11-14: **unreachable**. host does not resolve; summary only via search
- <https://dael.euracoustics.org/confs/fa2023/data/articles/000539.pdf>, accessed 2026-11-14: **unreachable**. host does not resolve
- <https://pdfs.semanticscholar.org/9f7c/49a5b574bfde828b3918313c7fcf54ab2d89.pdf> (DOI 10.1163/27723194-bja10001), accessed 2026-11-14: **unreachable**. host does not resolve
- <https://en.wikipedia.org/wiki/Irish_bouzouki>, accessed 2026-11-14: **used**. snippet via search
- <https://www.stewmac.com/strings-and-accessories/strings/mandolin-strings/daddario-phosphor-bronze-mandolin-strings/>, accessed 2026-11-14: **used**. snippet via search
- <https://h2g2.com/entry/A27733016>, accessed 2026-11-14: **corroborating**. snippet via search
- <https://www.prestomusic.com/instruments-accessories/products/8808454--daddario-ej81-irish-bouzouki-strings>, accessed 2026-11-14: **used**. snippet via search
- <https://www.h2g2.com/edited_entry/A827147>, accessed 2026-11-14: **used**. snippet via search
- <https://zenodo.org/records/3685367> (DOI 10.5281/zenodo.3685367), accessed 2026-11-14: **used**. 2913 samples, 14 instruments incl. Accordion, 44.1 kHz 16-bit mono, 1.0 GB
- <https://github.com/sgossner/VCSL>, accessed 2026-11-14: **used**. instrument list not shown
- <https://theremin.music.uiowa.edu/MIS.html>, accessed 2026-11-14: **unreachable**. host not resolvable in sandbox
- <https://philharmonia.co.uk/resources/sound-samples/>, accessed 2026-11-14: **unreachable**. host not resolvable in sandbox
- <https://magenta.tensorflow.org/datasets/nsynth>, accessed 2026-11-14: **unreachable**. host not resolvable in sandbox
- <https://sfzinstruments.github.io/>, accessed 2026-11-14: **unreachable**. host not resolvable in sandbox
- <https://freesound.org/>, accessed 2026-11-14: **unreachable**. host not resolvable in sandbox
- <https://commons.wikimedia.org/>, accessed 2026-11-14: **unreachable**. host not resolvable in sandbox
- <https://archive.org/>, accessed 2026-11-14: **unreachable**. host not resolvable in sandbox
- <https://zenodo.org/api/records?q=harmonica|mandolin|bouzouki>, accessed 2026-11-14: **used**. negative result
