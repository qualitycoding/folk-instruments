#!/usr/bin/env python3
"""Download and check the reference files named in references/index.csv (plan/DECISIONS.md D-052; test T-211).

  fetch_references.py --index <index.csv> --root <dir> [--archive-cache <dir>] [--archives <file>] [--only-redistributable]

Archives (source_url path ending in .zip or .tar.gz, after dropping a trailing /content) are cached under their last path component;
their sha256 must match references/archives.csv before anything is read; only the member named by `file` (minus its first component)
is extracted, only if it is a regular file, by reading it and writing it to <root>/<file>. Unsafe `file` values are refused. Every
refusal exits 1 and writes nothing. Other source URLs are downloaded directly. Every sha256 is checked."""
import argparse, csv, hashlib, os, sys, tarfile, tempfile, urllib.request, zipfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent


class Refusal(Exception):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_parts(file):
    if not file or file.startswith("/") or "\\" in file or (len(file) > 1 and file[1] == ":"):
        raise Refusal(f"unsafe file path '{file}'")
    parts = file.split("/")
    if any(p in ("", ".", "..") for p in parts) or len(parts) < 2:
        raise Refusal(f"unsafe file path '{file}'")
    return parts


def archive_name(url):
    path = urlparse(url).path
    if path.endswith("/content"):
        path = path[: -len("/content")]
    name = path.rsplit("/", 1)[-1]
    return name if name.endswith((".zip", ".tar.gz")) else None


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "folk-fetch-references"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)


def member_bytes(archive, name, member):
    want = member
    if name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():
                if info.filename.removeprefix("./") == want or info.filename == want:
                    if info.is_dir() or ((info.external_attr >> 16) & 0o170000) == 0o120000:
                        raise Refusal(f"member {member} is not a regular file")
                    return zf.read(info)
    else:
        with tarfile.open(archive, "r:gz") as tf:
            for ti in tf:
                n = ti.name[2:] if ti.name.startswith("./") else ti.name
                if n == want:
                    if not ti.isreg():
                        raise Refusal(f"member {member} is not a regular file")
                    return tf.extractfile(ti).read()
    raise Refusal(f"member {member} not found in {name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--archive-cache")
    ap.add_argument("--archives", default=str(ROOT / "references" / "archives.csv"))
    ap.add_argument("--only-redistributable", action="store_true")
    a = ap.parse_args()
    root = Path(a.root)
    try:
        with open(a.index, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        hashes = {}
        if Path(a.archives).exists():
            with open(a.archives, newline="", encoding="utf-8") as f:
                hashes = {r["source_url"]: r["sha256"] for r in csv.DictReader(f)}
        cache = Path(a.archive_cache) if a.archive_cache else Path(tempfile.mkdtemp(prefix="folk-archives-"))
        cache.mkdir(parents=True, exist_ok=True)
        for row in rows:
            if a.only_redistributable and row["redistributable"] != "true":
                continue
            parts = safe_parts(row["file"])
            dest = root.joinpath(*parts)
            if dest.is_file() and sha(dest.read_bytes()) == row["sha256"]:
                continue
            url, aname = row["source_url"], archive_name(row["source_url"])
            if aname:
                arch = cache / aname
                if url not in hashes:
                    raise Refusal(f"archive {url} is not listed in archives.csv")
                if not arch.exists():
                    download(url, arch)
                if sha(arch.read_bytes()) != hashes[url]:
                    raise Refusal(f"archive {aname} does not match its sha256")
                data = member_bytes(arch, aname, "/".join(parts[1:]))
            else:
                tmp = cache / ("direct-" + sha(url.encode())[:16])
                download(url, tmp)
                data = tmp.read_bytes()
                tmp.unlink()
            if sha(data) != row["sha256"]:
                raise Refusal(f"{row['id']}: sha256 of the file does not match the index")
            dest.parent.mkdir(parents=True, exist_ok=True)
            part = dest.with_name(dest.name + ".part")
            part.write_bytes(data)
            os.replace(part, dest)
    except Refusal as e:
        print(f"fetch_references: {e}", file=sys.stderr)
        return 1
    except (OSError, KeyError, csv.Error, zipfile.BadZipFile, tarfile.TarError) as e:
        print(f"fetch_references: {e!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
