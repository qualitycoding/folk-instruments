# Research round 3

## What was done
R5: a fresh-context reviewer attacked all 26 load-bearing claims (`r3-adversarial.json`), re-ran the reed spike at 44.1 to 705.6 kHz and with a second integrator, and searched Zenodo, Wikimedia Commons and archive.org for reference recordings. Spikes S03c (pressure-driven reed), S05 (cost), S06 (known answers), S07 (TinySOL accordion measured), S08 (test oracle), S09, S10 (five plugins built).

## Outcome
No claim refuted; C-002, C-030 and C-051 weakened and reworded; C-040's tuning corroborated by the maker's page; eight missing claims added (hysteresis, real-time safety, cost, JUCE 9, Python version, download hosts). Not saturated.

## Sources checked

- <https://arxiv.org/pdf/2401.01606>, accessed 2026-11-14: **used**. Primary source for C-001 to C-004; read in full text via pdftotext
- <https://euphonics.org/wp-content/uploads/2022/03/Double_decays_JASA.pdf> (DOI 10.1121/10.0009012), accessed 2026-11-14: **used**. Checks C-027 and C-028
- <https://www.cs.bu.edu/fac/snyder/TablatureWeb/Bahnson%20JASA%201998.pdf>, accessed 2026-11-14: **unreachable**. Proxy refused cs.bu.edu (403); web.archive.org does not resolve; archive.org availability API shows a 2026-04-12 snapshot
- <https://archive.org/wayback/available?url=www.cs.bu.edu/fac/snyder/TablatureWeb/Bahnson%20JASA%201998.pdf>, accessed 2026-11-14: **not relevant**. Snapshot exists but host web.archive.org unresolvable
- <https://en.wikipedia.org/wiki/Overblowing>, accessed 2026-11-14: **corroborating**. C-012, C-013
- <https://en.wikipedia.org/wiki/Chromatic_harmonica>, accessed 2026-11-14: **corroborating**. C-014
- <https://en.wikipedia.org/wiki/Harmonica>, accessed 2026-11-14: **corroborating**. C-012 to C-014
- <https://archive.org/advancedsearch.php?q=harmonica+bending+acoustics>, accessed 2026-11-14: **not relevant**. Only method books and unrelated items
- <https://hal.science/search/index/?q=harmonica+reed>, accessed 2026-11-14: **unreachable**. Bot challenge page (Anubis) instead of results; api.archives-ouvertes.fr refused by proxy
- <https://arxiv.org/search/?query=bouzouki>, accessed 2026-11-14: **not relevant**. No instrument-acoustics papers except 0906.0127 (fret intonation) and two hulusi free-reed papers, not opened
- <https://ccrma.stanford.edu/~jos/pasp/Ideal_Plucked_String.html>, accessed 2026-11-14: **not relevant**. Defines the ideal pluck, gives no spectral formula
- <https://www.dafx.de/paper-archive/2011/Papers/24_e.pdf>, accessed 2026-11-14: **used**. C-030: does not support a plectrum low-pass statement
- <https://www.jstage.jst.go.jp/article/ast/24/1/24_1_1/_pdf> (DOI 10.1250/ast.24.1), accessed 2026-11-14: **used**. C-034
- <https://www.daddario.com/products/ej81-irish-bouzouki-strings>, accessed 2026-11-14: **corroborating**. C-040
- <https://en.wikipedia.org/wiki/Bouzouki>, accessed 2026-11-14: **corroborating**. C-039
- <https://en.wikipedia.org/wiki/Irish_bouzouki>, accessed 2026-11-14: **corroborating**. C-040
- <https://github.com/juce-framework/JUCE>, accessed 2026-11-14: **used**. C-043, C-044; found JUCE 9.0.5
- <https://github.com/Tracktion/pluginval>, accessed 2026-11-14: **used**. C-045
- <https://github.com/actions/checkout>, accessed 2026-11-14: **used**. C-046
- <https://github.com/actions/runner-images>, accessed 2026-11-14: **used**. C-047
- <https://pypi.org/pypi/numpy/json>, accessed 2026-11-14: **used**. C-048
- <https://philharmonia.co.uk/resources/sound-samples/>, accessed 2026-11-14: **used**. C-049
- <https://zenodo.org/api/records/3685367> (DOI 10.5281/zenodo.3685367), accessed 2026-11-14: **used**. C-021
- <https://www.google.com/search (WebSearch tool)>, accessed 2026-11-14: **not relevant**. Used only to locate sources; retailer snippets (Presto Music, Bernunzio) give EJ81 gauges .011 .016 .028 .040
- <https://zenodo.org/api/records?q=harmonica&type=dataset>, accessed 2026-11-14: **not relevant**. No audio of the four instruments; harmonica/mandolin hits are 3-D models (10228073, 10368454, 10311073)
- <https://zenodo.org/records/4588740> (DOI 10.5281/zenodo.4588740), accessed 2026-11-14: **not relevant**. Instruments: flute, cello, clarinet, trumpet, violin, saxophones, oboe, piccolo, bass
- <https://archive.org/advancedsearch.php>, accessed 2026-11-14: **not relevant**. Concert recordings and albums, no isolated-note sets except G-Town (below)
- <https://archive.org/details/GTownChurchSamplingProject>, accessed 2026-11-14: **corroborating**. C-051 candidate for mandolin
- <https://commons.wikimedia.org/w/api.php>, accessed 2026-11-14: **unreachable**. HTTP 429 rate limit on every call; ordinary search pages and action=render file pages worked
- <https://commons.wikimedia.org/w/index.php?search=bouzouki+filetype%3Aaudio>, accessed 2026-11-14: **used**. C-051
- <https://commons.wikimedia.org/wiki/File:Tuning-Sound-G-Bouzouki.ogg>, accessed 2026-11-14: **used**. C-051 reference candidate
- <https://commons.wikimedia.org/wiki/File:Bending_Mundharmonika.ogg>, accessed 2026-11-14: **used**. C-051 reference candidate
- <https://commons.wikimedia.org/wiki/File:Harmonica_02.ogg>, accessed 2026-11-14: **used**. C-051 reference candidate
- <https://commons.wikimedia.org/wiki/File:Blues_Harp1.ogg>, accessed 2026-11-14: **used**. C-051 candidate
- <https://commons.wikimedia.org/wiki/File:MandolinenDemo.ogg>, accessed 2026-11-14: **not relevant**. Music with synthetic accompaniment, not isolated notes
- <https://commons.wikimedia.org/wiki/File:Electra-Melodica-Hohner-1967_CC-BY_Reuter-Schefczik.flac>, accessed 2026-11-14: **not relevant**. Electro-acoustic variant, not a standard melodica
- <https://www.daddario.com/sitemap.xml>, accessed 2026-11-14: **not relevant**. Product sitemaps returned empty; the index lists a file named sitemap_agentic_discovery.xml, which was not opened
