// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// Scope canary for the host-tsan job (R-087, R-088): a race in non-JUCE code that runs under a JUCE-namespaced thread entry.
// The job runs it with the accepted line 'race_top:^juce::ScopeThread::entry(' and requires the race to be reported
// (exit 66): an accepted suppression for a JUCE function low in the stack must never hide a race in plugin or core code.
#include <cstdio>
#include <thread>

namespace juce { struct ScopeThread { static void entry(void (*body)()) { body(); } }; }
static int shared = 0;   // written by two threads without synchronisation, on purpose
static void pluginCode() { for (int i = 0; i < 100000; ++i) shared = shared + 1; }

int main() {
    std::thread a(juce::ScopeThread::entry, pluginCode);
    std::thread b(juce::ScopeThread::entry, pluginCode);
    a.join();
    b.join();
    std::printf("scope canary finished: %d\n", shared);
    return 0;
}
