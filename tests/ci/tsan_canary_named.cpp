// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// Second canary for the host-tsan job (R-069, R-078): a deliberate race inside a named function in JUCE's namespace. The job
// runs it twice: with the suppression line 'race:^juce::CanaryBox::bump(' it must exit 0 (the form that
// tests/ci/check_tsan_supp.py accepts really suppresses a function frame), and with the near miss
// 'race:^juce::CanaryBox::bum(' it must be reported (exit 66).
#include <cstdio>
#include <thread>

namespace juce { struct CanaryBox { static void bump(int k); }; }
static int shared = 0;   // written by two threads without synchronisation, on purpose
void juce::CanaryBox::bump(int k) { for (int i = 0; i < 100000; ++i) shared = shared + k; }

int main() {
    std::thread a(juce::CanaryBox::bump, 1);
    std::thread b(juce::CanaryBox::bump, 2);
    a.join();
    b.join();
    std::printf("named canary finished: %d\n", shared);
    return 0;
}
