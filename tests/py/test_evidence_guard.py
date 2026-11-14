# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""T-210 the fail-closed check on publishing reference-derived material (Rule 15; D-052). tools/evidence_guard.py is called as
    python3 tools/evidence_guard.py --index <index.csv> --evidence <directory>
The directory must hold MANIFEST.json: {"files": [{"path": "<relative path>", "derived_from": ["<reference id>", ...]}, ...]}.
Exit status 0 only if every file in the directory (other than MANIFEST.json) is listed and every reference it derives from
has redistributable == 'true' in the index. A missing, empty or unknown flag counts as false."""
import json
import pathlib
import subprocess
import sys

import pytest

GUARD = pathlib.Path(__file__).resolve().parents[2] / "tools" / "evidence_guard.py"
HEAD = "id,instrument,file,sha256,midi,velocity,sets,source_url,author,licence,licence_url,accessed,redistributable\n"
ROW = "{id},mandolin,{id}.wav," + "a" * 64 + ",69,0.7,,https://example.org/{id},An Author,{lic},https://example.org/licence,2026-11-14,{flag}\n"


def run_guard(tmp_path, rows, files, manifest):
    (tmp_path / "index.csv").write_text(HEAD + "".join(rows))
    ev = tmp_path / "evidence"
    ev.mkdir()
    for f in files:
        (ev / f).parent.mkdir(parents=True, exist_ok=True)
        (ev / f).write_bytes(b"RIFF....")
    if manifest is not None:
        (ev / "MANIFEST.json").write_text(json.dumps({"files": manifest}))
    return subprocess.run([sys.executable, str(GUARD), "--index", str(tmp_path / "index.csv"), "--evidence", str(ev)], capture_output=True, text=True, timeout=60)


OPEN_ROW = ROW.format(id="open1", lic="CC-BY-4.0", flag="true")
PRIVATE_ROW = ROW.format(id="priv1", lic="site terms", flag="false")


def test_T210_demos_and_redistributable_pairs_pass(tmp_path):
    r = run_guard(tmp_path, [OPEN_ROW, PRIVATE_ROW], ["demo-01.wav", "pairs/p01_a.wav"],
                  [{"path": "demo-01.wav", "derived_from": []}, {"path": "pairs/p01_a.wav", "derived_from": ["open1"]}])
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("flag", ["false", "", "unknown", "TRUE", "yes"])
def test_T210_private_or_unflagged_reference_blocks_publication(tmp_path, flag):
    row = ROW.format(id="ref1", lic="site terms", flag=flag)
    r = run_guard(tmp_path, [row], ["pairs/p01_a.wav"], [{"path": "pairs/p01_a.wav", "derived_from": ["ref1"]}])
    assert r.returncode == 1, (r.returncode, r.stderr)
    assert "ref1" in r.stderr


def test_T210_unlisted_file_unknown_reference_and_missing_manifest_fail(tmp_path):
    a = tmp_path / "a"; a.mkdir()
    assert run_guard(a, [OPEN_ROW], ["demo-01.wav", "stray.wav"], [{"path": "demo-01.wav", "derived_from": []}]).returncode == 1
    b = tmp_path / "b"; b.mkdir()
    assert run_guard(b, [OPEN_ROW], ["pairs/p01_a.wav"], [{"path": "pairs/p01_a.wav", "derived_from": ["nobody"]}]).returncode == 1
    c = tmp_path / "c"; c.mkdir()
    assert run_guard(c, [OPEN_ROW], ["demo-01.wav"], None).returncode == 1
    d = tmp_path / "d"; d.mkdir()
    assert run_guard(d, [OPEN_ROW], ["demo-01.wav"], [{"path": "demo-01.wav"}]).returncode == 1   # derived_from is mandatory
