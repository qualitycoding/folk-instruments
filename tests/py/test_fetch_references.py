# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""T-211 safe handling of downloaded archives by tools/fetch_references.py (D-052; Rule 16; pre-mortem R-024). Called as
    python3 tools/fetch_references.py --index <index.csv> --root <dir> --archive-cache <dir> --archives <archives.csv>
An archive row's archive is looked up in the cache under the last path component of its source_url (after removing a
trailing '/content'); its own sha256 must match the row of archives.csv (columns source_url, sha256) before anything is
extracted; only the one member named by `file` (without its first path component; a leading './' in the archive is
ignored) is extracted, and only if it is a regular file; a `file` with an empty, '.' or '..' component, or an absolute
path, is refused. Every refusal exits 1 and writes nothing under the root or outside it. No network is needed: every
archive is already in the cache, and the URLs use the reserved domain example.invalid."""
import hashlib
import io
import pathlib
import subprocess
import sys
import tarfile
import zipfile

import pytest

TOOL = pathlib.Path(__file__).resolve().parents[2] / "tools" / "fetch_references.py"
HEAD = "id,instrument,file,sha256,midi,velocity,sets,source_url,author,licence,licence_url,accessed,redistributable\n"
PAYLOAD = b"RIFF\x24\x00\x00\x00WAVEfmt payload of the reference note"
EVIL = b"overwritten by a crafted archive"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def make_tar(path, members):
    with tarfile.open(path, "w:gz") as tf:
        for name, kind, data in members:
            ti = tarfile.TarInfo(name)
            if kind == "file":
                ti.size = len(data)
                tf.addfile(ti, io.BytesIO(data))
            else:
                ti.type = tarfile.SYMTYPE
                ti.linkname = data
                tf.addfile(ti)


def make_zip(path, members):
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in members:
            zf.writestr(name, data)


def run(tmp_path, archive_name, file_col, archive_hash=None, listed=True):
    root, cache = tmp_path / "root", tmp_path / "cache"
    root.mkdir(exist_ok=True)
    url = f"https://example.invalid/files/{archive_name}/content"
    arch = cache / archive_name
    rows = f"t-001,accordion,{file_col},{sha(PAYLOAD)},69,0.6,,{url},An Author,CC-BY-4.0,https://creativecommons.org/licenses/by/4.0/,2026-11-15,true\n"
    (tmp_path / "index.csv").write_text(HEAD + rows)
    h = archive_hash if archive_hash is not None else sha(arch.read_bytes())
    (tmp_path / "archives.csv").write_text("source_url,sha256\n" + (f"{url},{h}\n" if listed else ""))
    r = subprocess.run([sys.executable, str(TOOL), "--index", str(tmp_path / "index.csv"), "--root", str(root),
                        "--archive-cache", str(cache), "--archives", str(tmp_path / "archives.csv")],
                       capture_output=True, text=True, timeout=120)
    return r, root


def files_under(d):
    return sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file() or p.is_symlink())


def no_escape(tmp_path):
    # nothing may appear beside the four planned entries of tmp_path, nor beside it
    return sorted(p.name for p in tmp_path.iterdir()) == ["archives.csv", "cache", "index.csv", "root"] and \
        not (tmp_path.parent / "escaped.txt").exists()


@pytest.fixture
def cache(tmp_path):
    c = tmp_path / "cache"
    c.mkdir()
    return c


def test_T211_named_member_only_is_extracted_from_a_hostile_tar(tmp_path, cache):
    make_tar(cache / "set.tar.gz", [("./good/a.wav", "file", PAYLOAD), ("../escaped.txt", "file", EVIL),
                                    ("/tmp/escaped.txt", "file", EVIL), ("./good/link.wav", "link", "/etc/passwd")])
    r, root = run(tmp_path, "set.tar.gz", "src/good/a.wav")
    assert r.returncode == 0, r.stderr
    assert files_under(root) == ["src/good/a.wav"]
    assert (root / "src/good/a.wav").read_bytes() == PAYLOAD
    assert no_escape(tmp_path)


def test_T211_zip_member_is_extracted(tmp_path, cache):
    make_zip(cache / "set.zip", [("good/a.wav", PAYLOAD), ("../escaped.txt", EVIL)])
    r, root = run(tmp_path, "set.zip", "src/good/a.wav")
    assert r.returncode == 0, r.stderr
    assert files_under(root) == ["src/good/a.wav"]
    assert no_escape(tmp_path)


@pytest.mark.parametrize("file_col", ["src/../../escaped.txt", "src/good/../../../escaped.txt", "/tmp/escaped.txt", "src//a.wav", "src/./a.wav"])
def test_T211_unsafe_file_column_is_refused(tmp_path, cache, file_col):
    make_tar(cache / "set.tar.gz", [("./good/a.wav", "file", PAYLOAD), ("../escaped.txt", "file", PAYLOAD)])
    r, root = run(tmp_path, "set.tar.gz", file_col)
    assert r.returncode == 1, (r.returncode, r.stderr)
    assert files_under(root) == []
    assert no_escape(tmp_path)


def test_T211_member_that_is_a_link_is_refused(tmp_path, cache):
    make_tar(cache / "set.tar.gz", [("./good/a.wav", "link", "/etc/passwd")])
    r, root = run(tmp_path, "set.tar.gz", "src/good/a.wav")
    assert r.returncode == 1, (r.returncode, r.stderr)
    assert files_under(root) == []


def test_T211_archive_hash_is_checked_before_extraction(tmp_path, cache):
    make_tar(cache / "set.tar.gz", [("./good/a.wav", "file", PAYLOAD)])
    r, root = run(tmp_path, "set.tar.gz", "src/good/a.wav", archive_hash="0" * 64)
    assert r.returncode == 1, (r.returncode, r.stderr)
    assert files_under(root) == []


def test_T211_archive_missing_from_archives_csv_is_refused(tmp_path, cache):
    make_tar(cache / "set.tar.gz", [("./good/a.wav", "file", PAYLOAD)])
    r, root = run(tmp_path, "set.tar.gz", "src/good/a.wav", listed=False)
    assert r.returncode == 1, (r.returncode, r.stderr)
    assert files_under(root) == []
