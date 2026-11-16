// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// Canary for the host-tsan job (R-051): a deliberate data race. Built with the same sanitiser flags and suppressions as the
// host tests, it must be reported (non-zero exit with halt_on_error=1); if it exits 0, ThreadSanitizer is not active and
// the T-304 result proves nothing.
#include <cstdio>
#include <thread>

static int shared = 0;   // written by two threads without synchronisation, on purpose

int main() {
    std::thread a([] { for (int i = 0; i < 100000; ++i) shared = shared + 1; });
    std::thread b([] { for (int i = 0; i < 100000; ++i) shared = shared + 2; });
    a.join();
    b.join();
    std::printf("canary finished: %d\n", shared);
    return 0;
}
