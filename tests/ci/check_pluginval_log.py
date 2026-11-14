#!/usr/bin/env python3
# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""T-300 coverage proof for one pluginval run (plan/DECISIONS.md, D-082). pluginval can exit with status 0 without having
run every test, so CI passes its captured output through this check.
Usage: check_pluginval_log.py <log file> <product name, e.g. "Folk Mandolin">
The markers are the strings pluginval v1.0.4 writes (Source/PluginTests.cpp lines 93, 185, 190; Source/Validator.cpp
lines 206 to 208; Source/CommandLine.cpp lines 98 to 106)."""
import sys

REQUIRED_TESTS = ["Plugin info", "Editor", "Plugin state", "Audio processing", "Automation", "Fuzz parameters", "Plugin state restoration",
                  "Parameter thread safety", "Process called with a larger than prepared block size", "Allocations during process"]


def problems(text, product):
    out = []
    if "Started validating: " not in text: out.append("no 'Started validating:' line")
    if product not in text: out.append(f"the product name '{product}' does not appear")
    if "Strictness level: 10" not in text: out.append("strictness level 10 was not in force")
    for name in REQUIRED_TESTS:
        if f"pluginval / {name}" not in text: out.append(f"test '{name}' did not start")
        if f'"{name}" is disabled' in text: out.append(f"test '{name}' is disabled")
    if "is disabled." in text: out.append("at least one test is disabled")
    if "*** FAILED" in text or "FAILURE" in text: out.append("the log reports a failure")
    if text.count("SUCCESS") < 1: out.append("no SUCCESS line")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write(__doc__); sys.exit(2)
    with open(sys.argv[1], encoding="utf-8", errors="replace") as fh:
        found = problems(fh.read(), sys.argv[2])
    for p in found: print("pluginval log check:", p)
    print("pluginval log check:", "FAILED" if found else "passed", "for", sys.argv[2])
    sys.exit(1 if found else 0)
