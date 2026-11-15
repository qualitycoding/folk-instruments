#!/usr/bin/env python3
"""R7 step 4: the URLs and DOIs in the source register equal the union of those in the round logs, research/SOURCES.md and
research/claims.json, and every row has every field. Exit 0 if complete."""
import json, re, glob, sys
reg = open(glob.glob("knowledge/K-*-source-register-*.md")[0]).read()
rows = [l.split("|")[1:-1] for l in reg.split("\n") if re.match(r"\| \d+ \|", l)]
problems = [f"row {r[0].strip()}: {len(r)} fields" for r in rows if len(r) != 12]
problems += [f"row {r[0].strip()}: empty field {i}" for r in rows for i, c in enumerate(r) if not c.strip()]
reg_urls = {r[2].strip().split(" ; ")[0] for r in rows}
url = re.compile(r"https?://[^\s<>)\]`|,]+")
logs = set()
for f in glob.glob("research/rounds/round-*.md"):
    for line in open(f):
        if line.startswith("- <"): logs.add(line[3:line.index(">")])
src = {m.group(0).rstrip(".>") for m in re.finditer(r"<(https?://[^>]+)>", open("research/SOURCES.md").read())}
src = {u.lstrip("<") for u in src}
cl = {s["url"] for c in json.load(open("research/claims.json")) for s in c["sources"] if s["url"].startswith("http")}
for name, sset in (("round logs", logs), ("SOURCES.md", src), ("claims.json", cl)):
    miss = sorted(sset - reg_urls)
    problems += [f"{name}: {u} is not in the register" for u in miss]
extra = sorted(reg_urls - (logs | src | cl))
problems += [f"register: {u} appears in no source list" for u in extra]
print("\n".join(problems) or f"complete: {len(rows)} rows, every list covered")
sys.exit(1 if problems else 0)
