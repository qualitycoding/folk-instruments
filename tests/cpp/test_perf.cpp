// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// T-013 real-time factor at full polyphony (SC-12; A-009; C-001 spike S05). Environment: the Linux x64 CI job only
// (runner label ubuntu-24.04, Release build); ctest label "perf". Other platforms print the figure and do not gate (D-086).
#include <catch2/catch_test_macros.hpp>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include "folk/engine.h"
#include "param_table.h"
using namespace folk;

TEST_CASE("T-013 ten seconds at full polyphony render at least four times faster than real time", "[perf]") {
    const bool gate = std::getenv("FOLK_PERF_GATE") != nullptr;   // set to 1 by the Linux x64 Release CI job
    for (Instrument ins : kAllInstruments) {
        auto e = Engine::create(ins); e->prepare(48000.0, 256);
        if (ins == Instrument::Accordion) e->setParam(e->paramIndex("register"), 11);   // Master: four ranks
        std::vector<float> l(256), r(256);
        const int voices = ins == Instrument::Accordion ? 16 : ins == Instrument::Melodion ? 10 : ins == Instrument::Harmonica ? 4 : 8;
        const int base = ins == Instrument::Harmonica ? 60 : 55;
        double best = 1e9;
        for (int rep = 0; rep < 3; ++rep) {   // best of three, to shed scheduler noise on shared runners
            e->reset();
            if (ins == Instrument::Accordion) e->setParam(e->paramIndex("register"), 11);
            const auto t0 = std::chrono::steady_clock::now();
            for (int block = 0; block < 1875; ++block) {   // 10 s
                if (block % 94 == 0) for (int v = 0; v < voices; ++v) e->noteOn(base + 2 * v + (block / 94) % 3, 0.9f, 0);   // retrigger every 0.5 s
                e->process(l.data(), r.data(), 256);
            }
            best = std::min(best, std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count());
        }
        const double factor = 10.0 / best;
        std::printf("PERF %s realtime_factor=%.2f gate=%d\n", instrumentName(ins), factor, gate ? 1 : 0);
        if (gate) CHECK(factor >= 4.0);
        else SUCCEED("informational on this platform");
    }
}
