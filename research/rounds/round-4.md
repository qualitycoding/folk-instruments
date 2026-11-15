# Research round 4

## What was done
R5 on the five claims added in round 3 and on the frozen tests (`r4-adversarial.json`).

## Outcome
A real defect in the design: the reed model with the reference reed's proportions did not transfer to other pitches (a cantilever-scaled 3520 Hz reed never oscillated; a 111 Hz reed was 50 to 100 cents flat). C-053 and C-055 weakened. Eight test defects reported; five were corrected before the freeze (band-limited beat measurement; an interpolation bug in the modulation measurement; brightness tested at five pitches; threshold, level and pitch tests at low, middle and high notes; a deprecated JUCE call), three were kept as statements of the design (single polarisation, re-pluck damping, absence of a rank). Not saturated.

## Sources checked

- <https://zenodo.org/record/3685367> (DOI 10.5281/zenodo.3685367), accessed 2026-11-14: **used**. independent recomputation of C-055 statistics on 330 notes
- <https://github.com/juce-framework/JUCE>, accessed 2026-11-14: **used**. checked createEditor access and createEditorIfNeeded deprecation
