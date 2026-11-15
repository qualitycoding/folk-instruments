"""Spike S16: read the licence or terms statement of every source in the register whose licence was not read, from the
page itself (curl through the sandbox proxy). Records the evidence found (licence links, copyright lines) per URL.
Usage: sweep.py <register.md> <out.json> <cache dir>"""
import re, sys, json, subprocess, pathlib, hashlib
reg, out, cache = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3]); cache.mkdir(parents=True, exist_ok=True)
rows = [l.split('|') for l in open(reg).read().split('\n') if re.match(r'\| \d+ \|', l)]
todo = [(r[1].strip(), r[3].strip().split(' ;')[0]) for r in rows if r[10].strip().startswith('unknown')]
res = {}
for n, u in todo:
    f = cache / (hashlib.sha1(u.encode()).hexdigest()[:16])
    if not f.exists():
        p = subprocess.run(["curl", "-sS", "-L", "-m", "40", "-A", "Mozilla/5.0 research-fetch", "-o", str(f), "-w", "%{http_code} %{content_type}", u], capture_output=True, text=True)
        (cache / (f.name + ".status")).write_text(p.stdout + " " + p.stderr.strip()[:200])
    st = (cache / (f.name + ".status")).read_text()
    raw = f.read_bytes() if f.exists() else b""
    if raw[:4] == b"%PDF":
        txt = subprocess.run(["pdftotext", "-l", "2", str(f), "-"], capture_output=True, text=True).stdout
    else:
        txt = raw.decode("utf-8", "replace")
    lic = sorted(set(re.findall(r"creativecommons\.org/(?:licenses|publicdomain)/[a-z-]+/[0-9.]+", txt)))
    arx = sorted(set(re.findall(r"arxiv\.org/licenses/[a-z0-9./-]+", txt)))
    cop = sorted(set(m.strip()[:120] for m in re.findall(r"(?:©|&copy;|Copyright)\s*(?:\(c\)\s*)?[^<\n]{0,100}", txt)))[:3]
    spdx = sorted(set(re.findall(r'"license"\s*:\s*\{[^}]*"id"\s*:\s*"([^"]+)"', txt)))
    pypi = sorted(set(re.findall(r"License:\s*([^<\n]{1,60})", txt)))[:2]
    res[u] = dict(row=int(n), status=st.split()[0] if st else "", cc=lic, arxiv=arx, copyright=cop, zenodo=spdx, pypi=pypi)
    print(n, st.split()[0] if st else "-", lic[:2], arx[:1], cop[:1], spdx, pypi[:1], u[:70], flush=True)
json.dump(res, open(out, "w"), indent=1)
