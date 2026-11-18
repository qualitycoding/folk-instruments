# FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
"""T-092 tool check of tests/ci/check_tsan_supp.py (R-051, R-069): only exact, anchored, top-frame JUCE functions may be suppressed."""
import pathlib
import subprocess
import sys

import pytest

CHECK = pathlib.Path(__file__).resolve().parents[1] / "ci" / "check_tsan_supp.py"


def run(tmp_path, text):
    f = tmp_path / "tsan.supp"
    if text is not None:
        f.write_text(text)
    return subprocess.run([sys.executable, str(CHECK), str(f)], capture_output=True, text=True, timeout=60).returncode


def test_T092_missing_or_exact_juce_entries_pass(tmp_path):
    assert run(tmp_path, None) == 0
    assert run(tmp_path, "# JUCE message queue, see DEVIATIONS.md\n\nrace_top:^juce::MessageManager::runDispatchLoop(\nrace_top:^juce::AbstractFifo::prepareToWrite(\nrace_top:^juce::detail::Foo::~Foo(\n") == 0


@pytest.mark.parametrize("line", ["race:^juce::Thread::threadEntryPoint(", "race:^juce::MessageManager::runDispatchLoop(", "deadlock:^juce::CriticalSection::enter(", "race_top:juce::Thread::run(", "race_top:^juce::A(", "race_top:^folk::Engine::process(",
                                  "race:juce::MessageManager::runDispatchLoop", "race:^juce::AudioBuffer", "race:juce::AudioBuffer",
                                  "race:^juce::A(", "race:^juce::MessageManager::runDispatchLoop", "race:^juce::Thread::run$", "race:juce::Thread::run(", "race:^juce::Thread::run(int", "race:*", "race:juce::*", "race:juce", "race:folk::Engine::process", "race:FolkProcessor::processBlock",
                                  "called_from_lib:libjuce.so", "deadlock:juce::CriticalSection::enter", "deadlock:^juce::CriticalSection::enter$", "deadlock:^folk::X::y(", "mutex:juce::SpinLock",
                                  "race_top:juce::AudioProcessor::processBlock", "race:juce::folkHelper", "race:std::vector", "race:juce::Thread*"])
def test_T092_broad_or_foreign_entries_fail(tmp_path, line):
    assert run(tmp_path, f"# reason\n{line}\n") == 1
