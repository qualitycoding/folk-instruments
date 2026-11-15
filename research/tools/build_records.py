#!/usr/bin/env python3
"""Builds, from research/claims.json and the per-round JSON files: research/SOURCES.md, research/rounds/round-N.md,
one knowledge item per claim under knowledge/, and the source register (R7). Run from the repository root after
research/tools/build_claims.py. Hand-written text for the round logs is in ROUND_TEXT below."""
import json, glob, pathlib, re, collections
RUN = "gen-20261114T004707Z-folk-instruments-vst"
C = json.load(open("research/claims.json"))
ROUND_FILES = {1: ["r1-A-free-reed.json", "r1-B-harmonica.json", "r1-C-accordion-melodica.json", "r1-D-plucked-string.json", "r1-E-mandolin-bouzouki.json", "r1-G-references.json"],
               2: ["r1-P-planner.json"], 3: ["r3-adversarial.json"], 4: ["r4-adversarial.json"], 5: ["r5-adversarial.json"], 6: ["r6-adversarial.json"]}
SEARCHES = [(2, "web search: Millot Baumann \"minimal model of free reeds\" Acta Acustica 2007", "used", "located arXiv:2401.01606"),
            (2, "web search: Ricot Causse Misdariis blown-closed free reeds accordion reed pdf", "used", "located the JASA record and a HAL entry; no full text"),
            (2, "web search: Bahnson Antaki Beery diatonic harmonica 1998 pdf", "used", "located a copy on a host outside the allowlist; not read"),
            (2, "web search: Philharmonia sound samples licence terms", "used", "led to the Philharmonia page, which was then read"),
            (2, "web search: GitHub-hosted runners available images labels 2026", "corroborating", "led to the runner-images README, which was then read")]
ROUND_TEXT = {
 1: """## What was done
R0: the lesson store (251 matching active lessons) and the knowledge store (323 matching items) were digested (`research/r0/`). R1: the question tree (`research/QUESTIONS.md`). R2, breadth: six workers, one per branch (free reeds, harmonica, accordion and melodion, plucked strings, mandolin and bouzouki, reference recordings), each testing the owner's input file statement by statement. Spike S01 recomputed the file's tables.

## Access failure
The fetch tool could not resolve hosts outside the environment's network allowlist and the search tool hit a usage limit, so every worker read its sources at search-snippet or abstract level only. No claim from this round was accepted as corroborated. Lesson: `lessons/L-20261114T090000Z-fetch-tool-shares-sandbox-allowlist.md`. The owner then approved adding 20 literature, dataset and manufacturer hosts to the allowlist; a later request for five more was refused by the service, which left `www.cs.bu.edu` (a copy of Bahnson et al. 1998) and `web.archive.org` out of reach.

## Outcome
151 worker claims (files `r1-*.json`): the input file's computed tables are arithmetically right; many of its attributions could not be traced (reed Q values and thresholds, laser-vibrometer pressures, cassotto figures' origin, melodica experiments, the mandolin '318 against 423 Hz' pair, 'mandolin #95'); its melodica ranges and its light mandolin string set are wrong.""",
 2: """## What was done
R3 and R4, depth: the planner read the primary sources that the allowlist now reached (Millot and Baumann; Cohen and Rossing; Woodhouse; Quintavalla et al.; the encyclopaedia pages for layouts and tunings; the TinySOL record; the Philharmonia and Iowa pages; JUCE at the pinned tag; the runner-images README) and built the claim register (`research/claims.json`, first 51 claims). R6, spikes: S02 (JUCE build), S03 and S03b (minimal reed model and the volume condition), S04 (coupled string pair).

## Gaps found
Nine load-bearing claims below the corroboration bar; Brezas et al. 2023, Bahnson et al. 1998 and Ricot et al. 2005 unreadable (publishers refuse automated requests).""",
 3: """## What was done
R5: a fresh-context reviewer attacked all 26 load-bearing claims (`r3-adversarial.json`), re-ran the reed spike at 44.1 to 705.6 kHz and with a second integrator, and searched Zenodo, Wikimedia Commons and archive.org for reference recordings. Spikes S03c (pressure-driven reed), S05 (cost), S06 (known answers), S07 (TinySOL accordion measured), S08 (test oracle), S09, S10 (five plugins built).

## Outcome
No claim refuted; C-002, C-030 and C-051 weakened and reworded; C-040's tuning corroborated by the maker's page; eight missing claims added (hysteresis, real-time safety, cost, JUCE 9, Python version, download hosts). Not saturated.""",
 4: """## What was done
R5 on the five claims added in round 3 and on the frozen tests (`r4-adversarial.json`).

## Outcome
A real defect in the design: the reed model with the reference reed's proportions did not transfer to other pitches (a cantilever-scaled 3520 Hz reed never oscillated; a 111 Hz reed was 50 to 100 cents flat). C-053 and C-055 weakened. Eight test defects reported; five were corrected before the freeze (band-limited beat measurement; an interpolation bug in the modulation measurement; brightness tested at five pitches; threshold, level and pitch tests at low, middle and high notes; a deprecated JUCE call), three were kept as statements of the design (single polarisation, re-pluck damping, absence of a rank). Not saturated.""",
 5: """## What was done
The planner derived a similarity scaling for the reed and verified it in spike S12 from 55 Hz to 5.3 kHz, re-measured the cost (S05b), checked the headless editor and the dependency scan (S11), and rewrote decisions D-011 and D-012. R5 on those changes (`r5-adversarial.json`).

## Outcome
The scaling is exact (every dimensionless group invariant). Three contradictions between the decision text and the reference spike were found (table range and confining spring; calibration ranges against the sub-step rule; the quoted offset band) and one new fact (the source level is the same at every pitch). Not saturated.""",
 6: """## What was done
The planner corrected D-010, D-011, D-012, D-015, D-016, DR-03 and step S-201. R5, last permitted round (`r6-adversarial.json`): the reviewer simulated a build that follows the decisions literally and checked the plan's own numerical gates and the breath law.

## Outcome
Steps S-200 and S-201 would pass (40 rows, smallest margin 0.95 cents); the frozen reed tests T-101, T-102, T-103 and T-105 can be satisfied. The calibration ranges were still too wide and the re-check clause could not be met by a calibrated set; both were then narrowed and replaced (D-012's calibrated-set check). **The research loop ended at the round limit, not by saturation**: round 6 still produced new load-bearing findings. They are in the register as C-062 and C-063, and what was not re-reviewed after the last correction is risk R-003.

## Termination criteria
Rounds run: 6 of at most 6. Load-bearing claims: 36; verified 26, corroborated 3, below the bar 7 (C-012, C-013, C-014, C-017, C-027, C-039, C-051), each carried into `premortem/RISK_REGISTER.md` (R-001, R-004, R-005). R7: the source register is `knowledge/K-20261115T020000Z-source-register-folk-instruments-vst.md`."""}
RANK = {"used": 0, "corroborating": 1, "rejected": 2, "not relevant": 3, "unreachable": 4}
src_by_url, per_round = {}, collections.defaultdict(list)
for rnd, files in ROUND_FILES.items():
    for f in files:
        d = json.load(open("research/rounds/" + f))
        for s in d.get("sources_checked", []):
            if not isinstance(s, dict) or not str(s.get("url", "")).startswith("http"): continue
            u = re.sub(r"[?&](token|sig|signature|X-Amz-[A-Za-z-]+)=[^&]+", "", s["url"]).strip()
            s = dict(s, url=u, round=rnd, file=f); per_round[rnd].append(s)
            old = src_by_url.get(u)
            if old is None or RANK.get(s.get("outcome"), 9) < RANK.get(old.get("outcome"), 9):
                if old: s["first_round"] = old.get("first_round", old["round"])
                src_by_url[u] = s
            for k in ("licence_or_terms", "content_summary"):
                if old and (not src_by_url[u].get(k) or src_by_url[u].get(k) in ("not read", "")) and old.get(k) not in (None, "", "not read"): src_by_url[u][k] = old[k]
claims_by_url = collections.defaultdict(list)
for c in C:
    for s in c["sources"]:
        if s["url"].startswith("http"): claims_by_url[s["url"]].append(c["id"])
missing = sorted(set(claims_by_url) - set(src_by_url))
assert not missing, missing
def one(t): return " ".join(str(t or "").replace("|", "/").split())
def permitted(s):
    if s["url"] in PERMIT: return PERMIT[s["url"]]
    lic = (s.get("licence_or_terms") or "").lower(); u = s["url"]
    if s.get("outcome") == "unreachable" and not s.get("swept"): return "read only (not read)"
    if "philharmonia" in u: return "private reference only (linked, not republished; Rule 15)"
    if "zenodo.org/records/3685367" in u or "zenodo.org/api/records/3685367" in u: return "redistribute (CC BY 4.0, with attribution)"
    if "juce-framework/JUCE" in u: return "adapt (AGPL-3.0; compatible with the repository's AGPL-3.0)"
    if "choosealicense" in u: return "redistribute (licence text copied verbatim into LICENSE)"
    if "cc0" in lic or "public domain" in lic: return "redistribute"
    if "nc" in lic.split("(")[0] and "cc by" in lic: return "quote briefly with attribution (non-commercial licence)"
    if "cc by" in lic or "creative commons attribution" in lic: return "adapt with attribution"
    if "without restrictions" in lic: return "redistribute"
    return "read only"
def licence(s):
    l = one(s.get("licence_or_terms"))
    if not l or l.lower().startswith("not read"):
        return UNREACHABLE_NOTE if s.get("unreached_at_sweep") or s.get("outcome") == "unreachable" or "not allowed" in (s.get("reason") or "") or "fetch failed" in (s.get("reason") or "") else "unknown (" + (l or "not read") + ")"
    return l
# Corrections from the R7 review (research/r7-register-review.json), keyed by a substring of the URL: (licence, permitted use, owner)
OVERRIDE = {"euphonics.org/publication-list": ("Site text CC BY-NC-SA 4.0 except where noted (footer); linked papers remain under their publishers' copyright and are offered for personal use only (publication list page)", "quote briefly with attribution", None),
            "euphonics.org/wp-content/uploads/2022/03/Double_decays_JASA.pdf": ("Copyright 2021 Acoustical Society of America (first page of the PDF); offered by the author for personal use only, any other use needs permission of the author and the Society (publication list, item 142)", "read only", None),
            "euphonics.org/uncategorized": ("Site text CC BY-NC-SA 4.0 except where noted (footer)", "quote briefly with attribution", None),
         "daddario.com": ("Copyright D'Addario & Co., all rights reserved; site Terms of Service (page footer)", "read only", None),
            "daddario.com/sitemap": ("none stated on the sitemap (an XML index of the site's pages); the site's product pages state 'Copyright D'Addario & Co., all rights reserved' with Terms of Service (see the EJ81 row)", "read only", None),
            "zenodo.org/records/3685367": (None, None, "C.-E. Cella, D. Ghisi, V. Lostanlen, F. Levy, J. Fineberg, Y. Maresz (recorded at Ircam)"),
            "zenodo.org/api/records/3685367": (None, None, "C.-E. Cella, D. Ghisi, V. Lostanlen, F. Levy, J. Fineberg, Y. Maresz (recorded at Ircam)")}
PERMIT = {}
SUMMARY = {"https://pypi.org/simple/": "The PyPI simple index (project names only); the version numbers were read with `pip index versions`, which queries each project's own index page.",
           "https://www.daddario.com/sitemap.xml": "The XML sitemap of the D'Addario website, used to find the product page of the EJ81 set.",
           "https://www.jstage.jst.go.jp/article/ast/24/1/24_1_1/_article": "Article page of Cohen and Rossing (2003): abstract (TV holography of four mandolins and a mandola; modal frequencies; frequency response; sound spectra 0 to 5 kHz) and free full text. The full text (PDF, its own row) holds Table 1 with the modal and air-cavity frequencies, the accelerance curves and the radiated spectra.",
           "https://zenodo.org/api/records?q=harmonica|mandolin": "Zenodo API searches for the instrument names (the query separators must be percent-encoded as %7C to run). Among the first hits are dataset records (3D models of a mandolin, a 'wood harmonica', an 1892 harmonica record, a corpus of allemandes), none of them a set of isolated notes of these instruments.",
           "https://commons.wikimedia.org/w/index.php?search=bouzouki": "A Wikimedia Commons search for bouzouki audio files; its hits carry mixed licences per file (for example CC BY-SA 4.0). The other Commons searches of round 3 (harmonica, melodica, mandolin) are summarised in research/rounds/r3-adversarial.json; the files used have their own rows.",
           "https://zenodo.org/records/4588740": "Good-sounds dataset: single notes and scales of orchestral and other instruments recorded at 48 kHz; none of the five instruments.",
           "https://commons.wikimedia.org/wiki/File:Tuning-Sound-G-Bouzouki.ogg": "A short recording, 'Tuning Sound G for Irish Bouzouki', the contributor's own work (24 August 2019).",
           "https://commons.wikimedia.org/wiki/File:Harmonica_02.ogg": "Harmonica 02: a 17 s clip, released into the public domain by its author through pdsounds.org; the original was a mono MP3 at 22 kHz (27 March 2008).",
           "https://euphonics.org/7-3-multiple-strings": "Section 7.3 of Woodhouse's online book Euphonics: multiple strings, coupled polarisations and double-decay envelopes, with sound examples.",
           "https://arxiv.org/pdf/2104.02480": "'Pickers' Guide to Acoustics of the Banjo', parts I and II (Politzer, Woodhouse, Mansour). A round-1 worker took this to be the preprint of Woodhouse's double-decay paper; it is not, and no claim rests on it.",
           "https://en.wikipedia.org/wiki/Irish_bouzouki": "History of the Irish bouzouki (Johnny Moynihan's retuning of a Greek bouzouki in the mid-1960s; Andy Irvine and Donal Lunny in the early 1970s, unison bass courses, Peter Abnett's first purpose-built instrument in 1972), common tunings (G2 D3 A3 D4), construction and scale lengths (24 to 25 in, some 26 to 27 in).",
           "https://ccrma.stanford.edu/software/stk/classstk_1_1Mandolin.html": "STK Mandolin class reference: two detuned plucked strings with a commuted body response; the page warns that commuted synthesis was covered by a Stanford patent.",
           "ccrma.stanford.edu/~jos/pasp/Stiff_String.html": "The stiffness term in the string wave equation and the resulting dispersion (high-frequency components travel faster); points to the following page, Stiff String Synthesis Models, for allpass dispersion filters.",
           "commons.wikimedia.org/wiki/File:Electra-Melodica": "A recording of a Hohner Electra-Melodica (an instrument of 1967); not used.",
           "commons.wikimedia.org/wiki/File:Bending_Mundharmonika.ogg": "A recording of draw bends on a harmonica (the contributor's own work, 2006)."}
for u, s_ in src_by_url.items():
    for key, text in SUMMARY.items():
        if (u.startswith(key) if key.startswith("http") else key in u): s_["content_summary"] = text; s_["fixed_summary"] = True
for u, s_ in src_by_url.items():
    for key, (lic, per, owner) in OVERRIDE.items():
        if key in u:
            if lic: s_["licence_or_terms"] = lic
            if per: PERMIT[u] = per
            if owner: s_["owner_or_authors"] = owner
# Licence sweep of spike S16 (research/spikes/s16-licence-sweep): statements read from the pages themselves.
SWEEP = {"https://arxiv.org/html/0810.2870": "arXiv.org perpetual non-exclusive licence (HTML page)",
         "https://arxiv.org/html/2401.01606": "arXiv.org perpetual non-exclusive licence (HTML page)",
         "https://arxiv.org/pdf/2401.01606": "arXiv.org non-exclusive distribution licence 1.0 (abstract page of the same paper)",
         "https://arxiv.org/pdf/2104.02480": "CC BY 4.0 (arXiv abstract page of the same preprint)",
         "dael.euracoustics.org/confs/fa2023/data/articles/000853.pdf": "CC BY 3.0 (first page of the PDF)",
         "dael.euracoustics.org/confs/fa2023/data/articles/000539.pdf": "CC BY 3.0 (first page of the PDF)",
         "dael.euracoustics.org/confs/fa2026/data/articles/000418.pdf": "CC BY 3.0 (first page of the PDF)",
         "dafx.de/paper-archive/2023/DAFx23_paper_47.pdf": "CC BY 4.0 (first page of the PDF)",
         "dafx.de/paper-archive/2010/DAFx10/PerngSmithRossing": "unknown: no licence or copyright statement on the first two pages of the PDF or on the archive page (DAFx proceedings)",
         "dafx.de/paper-archive/2011/Papers/24_e.pdf": "unknown: no licence or copyright statement on the first two pages of the PDF (DAFx proceedings)",
         "euphonics.org/11-6-free-reeds": "CC BY-NC-SA 4.0 (site footer)",
         "euphonics.org/7-3-multiple-strings": "CC BY-NC-SA 4.0 (site footer)",
         "en.wikipedia.org/wiki/Accordion": "CC BY-SA 4.0 (page footer)",
         "en.wikipedia.org/wiki/Irish_bouzouki": "CC BY-SA 4.0 (page footer)",
         "ccrma.stanford.edu/%7Ejos/pasp": "Copyright J. O. Smith III (page footer); read only",
         "ccrma.stanford.edu/~jos/pasp/Ideal_Plucked_String": "Copyright J. O. Smith III (page footer); read only",
         "ccrma.stanford.edu/software/stk/classstk_1_1Mandolin": "Copyright 1995 to 2023 Perry R. Cook and Gary P. Scavone, all rights reserved (page footer)",
         "jstage.jst.go.jp/article/ast/24/1/24_1_1/_pdf": "Copyright 2003 The Acoustical Society of Japan (meta tag 'copyright' of the article page https://www.jstage.jst.go.jp/article/ast/24/1/24_1_1/_article; the PDF itself carries no statement)",
         "commons.wikimedia.org/wiki/File:Blues_Harp1.ogg": "GFDL 1.2 or later; CC BY-SA 1.0, 2.0, 2.5 and 3.0 (file description page, Licensing section)",
         "zenodo.org/record/3685367": "CC BY 4.0 (Zenodo record metadata, licence id cc-by-4.0)",
         "zenodo.org/api/records?q=": "not applicable: a search query; each record carries its own licence",
         "archive.org/advancedsearch": "not applicable: a search query",
         "archive.org/wayback/available": "not applicable: an availability query",
         "commons.wikimedia.org/w/api.php": "not applicable: a search query",
         "arxiv.org/search": "not applicable: a search query",
         "hal.science/search": "not applicable: a search query",
         "pypi.org/simple": "not applicable: a package index queried for version numbers",
         "pypi.org/pypi/numpy/json": "not applicable: package metadata queried for version and Python requirement",
         "www.google.com/search": "not applicable: web search queries",
         "https://archive.org/": "not applicable: site searched, no item used",
         "https://commons.wikimedia.org/": "not applicable: site searched; licences of the files used are in their own rows"}
UNREACHABLE_NOTE = "unknown: the host was not reachable from the planning sandbox (no network route or HTTP 403), so the licence could not be read"
# Content cells: replace reasons and bare claim IDs with what the source is cited for.
CITED = {}
for f in ROUND_FILES[1]:
    for c in json.load(open("research/rounds/" + f)).get("claims", []):
        for s_ in c.get("sources", []):
            CITED.setdefault(s_.get("url", "").strip(), c["claim"])
SWEPT = json.load(open("research/spikes/s16-licence-sweep/output.json"))
for u, s_ in src_by_url.items():
    if SWEPT.get(u, {}).get("status") in ("000", "403", ""): s_["unreached_at_sweep"] = True
    for key, lic in SWEEP.items():
        if (u == key if key.endswith(".org/") else (u.startswith(key) if key.startswith("http") else key in u)):
            s_["licence_or_terms"] = lic; s_["swept"] = True
            if lic.startswith("not applicable"): PERMIT[u] = "not applicable (no content used)"
            break
    if SWEPT.get(u, {}).get("status") == "200" and (s_.get("outcome") == "unreachable" or re.search(r"fail|blocked|not allowed|not resolv|snippet", s_.get("access_notes") or "", re.I)):
        s_["access_notes"] = "unreachable when first checked in round 1; fetched with HTTP 200 on 2026-11-15 by the licence sweep (spike S16), after the owner widened the network allowlist"
    if u.startswith("https://ccrma.stanford.edu/software/stk/classstk_1_1Mandolin"): s_["access_notes"] = "class reference page fetched with HTTP 200 on 2026-11-15"
    if u == "https://doi.org/10.1163/27723194-bja10001": s_["access_notes"] = "read in full on 2026-11-14 (HTTP 200, licence links on the article page); a re-check on 2026-11-15 was refused by the publisher's site (HTTP 403)"
    if u == "https://zenodo.org/record/3685367": s_["access_notes"] = "record metadata read through the Zenodo API; the archive was downloaded and its md5 checked in spike S07"
    if u.startswith("https://commons.wikimedia.org/w/index.php?search=bouzouki"): s_["title"] = "Wikimedia Commons search: bouzouki filetype:audio"
    if u.startswith("https://zenodo.org/records/4588740"): s_["version_or_date"] = "version 1.1 (record page)"
    if u == "https://commons.wikimedia.org/wiki/File:Harmonica_02.ogg": s_["title"] = "Harmonica 02 (Harmonica_02.ogg)"
    if u == "https://arxiv.org/pdf/2104.02480": s_["title"] = "Pickers' Guide to Acoustics of the Banjo, parts I and II (arXiv 2104.02480)"; s_["owner_or_authors"] = "D. Politzer, J. Woodhouse, H. Mansour"
    if u.startswith("https://dael.euracoustics.org/confs/fa2023/data/articles/000853.pdf"): s_["title"] = "Clamped bar model for free reeds (Forum Acusticum 2023)"; s_["owner_or_authors"] = "N. Puranik, G. Scavone"
    cs = (s_.get("content_summary") or "").strip()
    if s_.get("fixed_summary"): continue
    if len(cs) < 25 or re.fullmatch(r"[A-Z]\d+[a-z]?", cs):
        if u in CITED: s_["content_summary"] = "Cited by a round-1 worker for: " + CITED[u][:220]
        elif s_.get("outcome") == "unreachable": s_["content_summary"] = "Not read (" + (one(s_.get("reason")) or "unreachable") + ")."
        else: s_["content_summary"] = (one(s_.get("title")) or "untitled") + "; " + (cs or "no summary recorded") + "."
rows = sorted(src_by_url.values(), key=lambda s: (s.get("first_round", s["round"]), s["file"], s["url"]))
# ---- SOURCES.md
out = ["# Sources", "", f"Every external source opened or queried during planning ({len(rows)} distinct URLs), in the order first checked. The source register (`knowledge/K-20261115T020000Z-source-register-folk-instruments-vst.md`) holds the same list with licence and permitted use. Web search queries are listed in the round logs.", ""]
for i, s in enumerate(rows, 1):
    out.append(f"{i}. {one(s.get('title')) or '(untitled)'}. {one(s.get('owner_or_authors'))}. {one(s.get('version_or_date'))}. <{s['url']}>" + (f" DOI {s['doi']}." if s.get("doi") else "") + f" Accessed {s.get('accessed', '2026-11-14')}. Tier {s.get('tier')}. Outcome: {s.get('outcome')}." + (f" Claims: {', '.join(sorted(set(claims_by_url.get(s['url'], []))))}." if claims_by_url.get(s["url"]) else "") + (f" Note: {one(s.get('reason'))}" if s.get("reason") else ""))
out += ["", "## Command and pin verification locators (1.3.6)", "",
        "- JUCE `docs/CMake API.md` and `docs/Linux Dependencies.md` at commit dabd5ad13cd869cba41046947fffc8e5ce5cd662: `juce_add_plugin`, `juce_add_console_app`, universal binaries, Linux packages.",
        "- pluginval `Source/CommandLine.cpp`, `Source/PluginTests.cpp`, `Source/Validator.cpp` at v1.0.4 (commit ed19c2c16b57a6d94db391bea3ef4a80b769d5bf): options and log strings.",
        "- `actions/runner-images` README at commit 95e6f51a068507e8f43d061d2166a39d0ef36ce8: runner labels.",
        "- Every other command in `plan/ENVIRONMENT.md` was executed in the planning sandbox (spikes S02, S08, S10, S11 and the red verification)."]
pathlib.Path("research/SOURCES.md").write_text("\n".join(out) + "\n")
# ---- round logs
for rnd in range(1, 7):
    L = [f"# Research round {rnd}", "", ROUND_TEXT[rnd], "", "## Sources checked", ""]
    seen = set()
    for s in per_round[rnd]:
        if s["url"] in seen: continue
        seen.add(s["url"]); L.append(f"- <{s['url']}>" + (f" (DOI {s['doi']})" if s.get("doi") else "") + f", accessed {s.get('accessed', '2026-11-14')}: **{s.get('outcome')}**. {one(s.get('reason')) or one(s.get('content_summary'))[:160]}")
    for (r, q, o, why) in SEARCHES:
        if r == rnd: L.append(f"- {q}, 2026-11-14: **{o}**. {why}")
    if rnd == 2: L.append("- git tag lists (`git ls-remote --tags`) of juce-framework/JUCE, catchorg/Catch2, Tracktion/pluginval, actions/checkout, actions/upload-artifact, actions/download-artifact, actions/setup-python, actions/cache, ilammy/msvc-dev-cmd, mull-project/mull, steinbergmedia/vst3sdk, free-audio/clap, 2026-11-14: **used** (pins) or **not relevant** (msvc-dev-cmd, mull, vst3sdk, clap: not used by the plan).")
    if rnd in (5, 6): L.append("- No external source was opened in this round; it consisted of spikes and of a review of files on this branch.")
    if not seen and rnd not in (5, 6): L.append("- none")
    pathlib.Path(f"research/rounds/round-{rnd}.md").write_text("\n".join(L) + "\n")
# ---- knowledge items
K = pathlib.Path("knowledge")
for old in K.glob("K-*.md"): old.unlink()
ids = []
for i, c in enumerate(C):
    slug = re.sub(r"[^a-z0-9]+", "-", c["claim"].lower())[:48].strip("-")
    kid = f"K-20261115T01{i // 60:02d}{i % 60:02d}Z-{c['id'].lower()}-{slug}"
    tags = list(c["tags"])
    if not any(t.startswith("subject:") for t in tags): tags.append("subject:juce" if "tech:juce" in tags else "subject:python-test-tooling")
    tags.append("phase:research")
    s0 = c["sources"][0]; ver = s0.get("version") or "version-independent"
    stmt = c["claim"].replace('"', "'")
    body = (c["note"] + "\n\n" if c["note"] else "") + f"Input-file verdict: {c['input_file_verdict']}. Load-bearing: {'yes' if c['load_bearing'] else 'no'}. Informs: {', '.join(c['informs']) or 'nothing directly'}.\n\nAll sources: " + "; ".join(f"{s['title']} ({s['locator']})" for s in c["sources"]) + "."
    K.joinpath(kid + ".md").write_text(f"""---
id: {kid}
statement: "{stmt}"
status: current
supersedes: []
tags: [{', '.join(tags)}]
applies_to_version: "{one(ver).replace('"', "'")}"
source: {{ url: "{s0['url']}", doi: "{s0.get('doi', '')}", title: "{one(s0['title']).replace('"', "'")}", locator: "{one(s0['locator']).replace('"', "'")}", accessed: "{s0['accessed']}", tier: {s0['tier']} }}
confidence: {c['confidence']}
derived_from: [{c['id']}]
discovered_by: planner
run: {RUN}
recorded_at: 2026-11-15T01:{i // 60:02d}:{i % 60:02d}Z
---
{body}
""")
    ids.append(kid)
# ---- source register
cnt = collections.Counter(s.get("outcome") for s in rows); unk = sum(1 for s in rows if licence(s).startswith("unknown") or licence(s).lower() == "none stated")
cited = sorted({cid for v in claims_by_url.values() for cid in v})
head = f"""---
id: K-20261115T020000Z-source-register-folk-instruments-vst
statement: "Source register for the folk-instruments VST research (run {RUN}): {len(rows)} external sources checked, {cnt.get('used', 0)} used, {cnt.get('corroborating', 0)} corroborating, {cnt.get('rejected', 0)} rejected, {cnt.get('not relevant', 0)} not relevant, {cnt.get('unreachable', 0)} unreachable; {unk} have an unknown or unstated licence."
status: current
supersedes: []
tags: [subject:free-reed-modelling, subject:plucked-string-modelling, domain:audio, phase:research, kind:source-register]
applies_to_version: version-independent
source: {{ url: "", doi: "", title: "Source register, run {RUN}", locator: "table below", accessed: "2026-11-15", tier: n/a }}
confidence: REVIEW_PENDING
derived_from: [{', '.join(cited)}]
discovered_by: planner
run: {RUN}
recorded_at: 2026-11-15T02:00:00Z
---
| # | Source (title, owner) | URL or DOI | Version or date | Accessed | Tier | Outcome | Content (own words) | Claims | Licence or terms (read where) | Permitted use | Access notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
"""
body = "".join(f"| {i} | {one(s.get('title')) or '(untitled)'}; {one(s.get('owner_or_authors')) or 'owner not recorded'} | {s['url']}{(' ; DOI ' + s['doi']) if s.get('doi') else ''} | {one(s.get('version_or_date')) or 'not dated'} | {s.get('accessed', '2026-11-14')} | {s.get('tier')} | {s.get('outcome')} | {one(s.get('content_summary')) or one(s.get('reason')) or 'not read'} | {', '.join(sorted(set(claims_by_url.get(s['url'], [])))) or 'none'} | {licence(s)} | {permitted(s)} | {one(s.get('access_notes')) or 'none'} |\n" for i, s in enumerate(rows, 1))
K.joinpath("K-20261115T020000Z-source-register-folk-instruments-vst.md").write_text(head + body)
print(len(rows), "sources;", dict(cnt), "; unknown licence:", unk, ";", len(ids), "knowledge items")
