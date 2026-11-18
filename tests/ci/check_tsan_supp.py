#!/usr/bin/env python3
# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""Checks tests/ci/tsan.supp before the host-tsan job uses it (R-021, R-051). Usage: check_tsan_supp.py <file>.
A missing file passes (no suppressions). Otherwise every line must be blank, a comment starting with '#', or exactly
'race_top:^juce::<Class>::<function>(': the top-frame form, because a 'race:' line suppresses a report if ANY frame of
either stack matches, so an entry for a JUCE thread-entry or dispatch function would hide every race in plugins/ and
core/ code that runs under it; anchored at the start and closed by the opening parenthesis of the parameter list
(ThreadSanitizer matches a pattern as a substring of the demangled frame, which ends in the parameter list: an
unanchored pattern would match parameter types, and a pattern ending in '$' matches no function at all); at least a
class and a function inside JUCE's namespace, no wildcard, no other suppression type (no 'race', 'deadlock',
'called_from_lib', 'mutex', 'thread' or 'signal'), and never 'folk'.
Exit status 0 when the file is acceptable, 1 otherwise, naming each bad line."""
import pathlib
import re
import sys

LINE = re.compile(r"race_top:\^juce::[A-Za-z_][A-Za-z0-9_]*(::[A-Za-z_][A-Za-z0-9_]*)*::~?[A-Za-z_][A-Za-z0-9_]*\(")


def main(argv):
    if len(argv) != 2:
        print("usage: check_tsan_supp.py <file>")
        return 2
    path = pathlib.Path(argv[1])
    if not path.exists():
        print("no suppressions file: nothing suppressed")
        return 0
    bad = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not LINE.fullmatch(line) or "folk" in line.lower():
            bad.append(f"line {n}: {raw!r}")
    for b in bad:
        print("not allowed:", b)
    print("tsan suppressions check:", "failed" if bad else "passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
