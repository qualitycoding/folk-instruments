# Templates (copied verbatim from planning protocol core v4.0, Appendices A to C)

## Appendix A: Lesson Template `[All]`

```markdown
---
id: L-20261003T101500Z-ci-logs-unreachable
title: CI logs are stored on a host the sandbox cannot reach
status: active                 # active | superseded | retired
supersedes: []                 # IDs this lesson replaces
recurrence_of: null            # ID of an earlier lesson whose mistake this repeats
occurrences: 1                 # times the mistake happened in this run
severity: High                 # Critical | High | Medium | Low (Global Rule 4)
tags: [tech:github-actions, phase:verification, kind:environment]
recorded_by: implementer       # planner | implementer
run: <run_id or branch>
recorded_at: 2026-10-03T10:15:00Z
---
## Trigger
How to recognise the situation in advance: circumstances, versions, observable signals.
## What went wrong
## Correction
## Prevention rule
One imperative, checkable instruction.
## Detection check
A command or observation that shows whether the rule was followed.
## Evidence
Commit, file, or log excerpt. No secrets.
```

## Appendix B: Knowledge Item Template `[All]`

```markdown
---
id: K-20261003T101700Z-central-portal-plugin
statement: Maven Central publishing uses the Central Portal through org.sonatype.central:central-publishing-maven-plugin; OSSRH is retired.
status: current                # current | superseded
supersedes: []
tags: [subject:maven-central-publishing, tech:maven, phase:release]
applies_to_version: central-publishing-maven-plugin 0.11.0   # or "version-independent"
source: { url: "", doi: "", title: "", locator: "", accessed: "YYYY-MM-DD", tier: 1 }
confidence: corroborated       # verified | corroborated | single-source | inferred
derived_from: [C-###]
discovered_by: planner         # planner | implementer
run: <run_id or branch>
recorded_at: 2026-10-03T10:17:00Z
---
Detail, conditions, and caveats.
```

**Source register template (R7).** The same front matter as a knowledge item, with these values, and a table as the body. It is filed under its first `subject:` tag like any other item, and the `kind:source-register` tag marks it.

```markdown
---
id: K-20261105T213000Z-source-register-central-publishing
statement: Source register for the Maven Central publishing research (run gen-20261105): 23 external sources checked, 14 used, 5 corroborating, 3 rejected, 1 unreachable; 2 have no stated licence.
status: current                # current | superseded
supersedes: []
tags: [subject:maven-central-publishing, tech:maven, phase:research, kind:source-register]
applies_to_version: version-independent   # each row records its own version or date
source: { url: "", doi: "", title: "Source register, run gen-20261105", locator: "table below", accessed: 2026-11-05, tier: n/a }
confidence: verified           # verified once the R7 review and completeness check pass
derived_from: [C-001, C-002]   # every C-### the register cites
discovered_by: planner
run: gen-20261105
recorded_at: 2026-11-05T21:30:00Z
---
| # | Source (title, owner) | URL or DOI | Version or date | Accessed | Tier | Outcome | Content (own words) | Claims | Licence or terms (read where) | Permitted use | Access notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Central Portal publishing guide, Sonatype | https://central.sonatype.org/publish/ | 2026-09 | 2026-11-05 | 1 | used | How to publish through the Portal, and the plugin goals involved. | C-001 | Publisher terms, https://www.sonatype.com/terms (page footer) | read only | none |
```

The statement carries the counts so the knowledge-store index (`knowledge/INDEX.md`) shows them without opening the item. Rows are in the order first checked. The body holds summaries in the agent's own words, never extracts of a source whose licence does not permit copying it.

## Appendix C: Lesson & Knowledge Stores `[All]`

**Stores.** Use two repositories, each with its own `TAXONOMY.md`, generated indexes, and schema script.

`<lessons-repo>/` (default: a repository named `Lessons`):
```
<lessons-repo>/
  TAXONOMY.md                        Controlled vocabulary of tags, with aliases
  lessons/<primary-tag>/L-*.md       One file per lesson; <primary-tag> is its first tech: or domain: tag with ':' replaced by '-', else "general"
  lessons/INDEX.md                   Generated: tag -> lesson IDs, titles, severity (run `python scripts/build_index.py`; never edited by hand)
  scripts/                           Index/schema helpers (`python scripts/check_knowledge_schema.py`)
```

`<knowledge-repo>/` (default: a repository named `knowledge`):
```
<knowledge-repo>/
  TAXONOMY.md                        Controlled vocabulary of tags, with aliases
  knowledge/<subject>/K-*.md         One file per item, filed under its first subject: tag
  knowledge/INDEX.md                 Generated: tag -> item IDs and statements (run `python scripts/build_index.py`; never edited by hand)
  scripts/                           Index/schema helpers (`python scripts/check_knowledge_schema.py`)
```

**Tags.** Each lesson and item carries tags from these facets:
* `domain:` the problem domain, e.g. `domain:audio`, `domain:automotive`, `domain:quantum-gravity`;
* `tech:` a language, framework, library, tool, or platform, e.g. `tech:java`, `tech:maven`, `tech:juce`, `tech:github-actions`;
* `subject:` (knowledge items) the specific thing a fact is about, e.g. `subject:maven-central-publishing`;
* `phase:` where it applies: `intake`, `research`, `specification`, `planning`, `implementation`, `verification`, `release`, or `retrospective`;
* `kind:` (lessons) `wrong-assumption`, `environment`, `tooling`, `permissions`, `verification-gap`, `scope`, `process`, `integrity`, `security`, or `protocol` (3.7.1 question 6); (knowledge items) `source-register` for the register of external sources checked in a run (R7, Appendix B), which is the only `kind:` tag a knowledge item carries;
* `applies:all` for a lesson that applies to every task.

Use an existing tag (or one of its aliases in `TAXONOMY.md`) whenever one fits. A new tag is added to `TAXONOMY.md` in the same commit, never as a near-duplicate of an existing tag.

**Matching rule (R0).** In the lesson store, a lesson is relevant when any of its `domain:` or `tech:` tags equals one of the task's tags or an alias of one, or when it carries `applies:all`. In the knowledge store, an item is relevant when any of its `domain:`, `tech:`, or `subject:` tags equals one of the task's tags or an alias of one. Superseded and retired entries are not loaded.

**Protocol lessons.** A lesson tagged `kind:protocol` is about this protocol, not about a subject. It carries no `domain:` or `tech:` tag and is therefore not loaded in R0. It is read when the protocol is revised: list them from the lesson store with `grep -rl "kind:protocol" lessons/`. A protocol change cites the lessons it rests on in the change record.

**Schema check.** Every entry has all front-matter fields of its template; its `id` matches its file name; every tag has a known facet, and every knowledge item has a `subject:` tag; and no entry matches a secret pattern. Run this from the root of the working branch or from the relevant store; in a split store it validates the entry type present there. Exit status 0 means every entry is valid:
```python
import pathlib, re, sys
REQUIRED = {
    "L": ["id", "title", "status", "supersedes", "recurrence_of", "occurrences", "severity", "tags", "recorded_by", "run", "recorded_at"],
    "K": ["id", "statement", "status", "supersedes", "tags", "applies_to_version", "source", "confidence", "derived_from", "discovered_by", "run", "recorded_at"],
}
FACETS = ("domain:", "tech:", "subject:", "phase:", "kind:", "applies:")
SECRET = re.compile(r"github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
problems = []
for path in sorted([*pathlib.Path(".").glob("lessons/**/L-*.md"), *pathlib.Path(".").glob("knowledge/**/K-*.md")]):
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    head = parts[1] if text.startswith("---") and len(parts) == 3 else ""
    fields = dict(re.findall(r"^(\w+):[ \t]*(.*)$", head, re.M))
    problems += [f"{path}: missing field '{f}'" for f in REQUIRED[path.name[0]] if f not in fields]
    if fields.get("id", "").split("#")[0].strip() != path.stem:
        problems.append(f"{path}: id does not match the file name")
    tags = re.findall(r"[\w-]+:[\w.-]+", fields.get("tags", ""))
    if not tags:
        problems.append(f"{path}: no tags")
    problems += [f"{path}: unknown tag facet '{t}'" for t in tags if not t.startswith(FACETS)]
    if path.name.startswith("K-") and not any(t.startswith("subject:") for t in tags):
        problems.append(f"{path}: no subject: tag")
    if SECRET.search(text):
        problems.append(f"{path}: possible secret")
print("\n".join(problems) or "all entries valid")
sys.exit(1 if problems else 0)
```
