# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""T-091 known-answer checks of tests/ci/check_pluginval_log.py (test tooling: passes from the day it is frozen; Rule 14:
the check has been shown to fail)."""
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location("chk", pathlib.Path(__file__).resolve().parents[1] / "ci" / "check_pluginval_log.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

GOOD = "Started validating: /x/Folk Mandolin.vst3\nTesting plugin: VST3-Folk Mandolin-1234\nStrictness level: 10\n" + \
       "".join(f"Starting test: pluginval / {n}...\nCompleted test: pluginval / {n}\n" for n in chk.REQUIRED_TESTS) + "SUCCESS\n"


def test_complete_log_passes():
    assert chk.problems(GOOD, "Folk Mandolin") == []


def test_each_defect_is_caught():
    assert chk.problems(GOOD.replace("Strictness level: 10", "Strictness level: 5"), "Folk Mandolin")
    assert chk.problems(GOOD.replace("SUCCESS", ""), "Folk Mandolin")
    assert chk.problems(GOOD + "*** FAILED\n", "Folk Mandolin")
    assert chk.problems(GOOD.replace("SUCCESS", "FAILURE"), "Folk Mandolin")
    assert chk.problems(GOOD + 'INFO: "Editor" is disabled.\n', "Folk Mandolin")
    assert chk.problems(GOOD.replace("Starting test: pluginval / Fuzz parameters...\n", "").replace("Completed test: pluginval / Fuzz parameters\n", ""), "Folk Mandolin")
    assert chk.problems(GOOD, "Folk Bouzouki")
    assert chk.problems("", "Folk Mandolin")
