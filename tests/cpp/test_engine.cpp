// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// T-008 parameter table (SC-11; D-091)                T-012 determinism after reset (SC-11)
// T-009 robustness under random events (SC-11)        T-014 state text: round trip and malformed input (SC-11; threat model)
// T-010 block-size invariance (SC-11; lesson: output depended on process segmentation)
// T-011 no allocation on the audio thread (SC-11; K-20261101T140200Z allocation probe)
// T-015 notes end: the tail decays within tailSeconds() (SC-11)
#include <catch2/catch_test_macros.hpp>
#include <atomic>
#include <cmath>
#include <cstdlib>
#include <new>
#include <random>
#include <string>
#include <vector>
#include "folk/engine.h"
#include "param_table.h"
using namespace folk;

// ---- allocation probe (T-011): counts every operator new while armed.
static std::atomic<bool> gArmed{false};
static std::atomic<long> gAllocations{0};
void* operator new(std::size_t n) { if (gArmed.load(std::memory_order_relaxed)) gAllocations.fetch_add(1, std::memory_order_relaxed);
                                    if (void* p = std::malloc(n ? n : 1)) return p; throw std::bad_alloc(); }
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void operator delete[](void* p, std::size_t) noexcept { std::free(p); }

namespace {
struct Ev { long at; int type; int a; float b; };  // type 0 on, 1 off, 2 cc, 3 bend, 4 param
std::vector<Ev> script(Instrument ins) {
    const int n = safeNote(ins);
    return {{0, 0, n, 0.8f}, {4800, 0, n + 5, 0.6f}, {9000, 3, 0, -0.5f}, {14400, 2, 1, 0.7f}, {20000, 1, n, 0}, {26000, 0, n + 7, 1.0f},
            {30000, 3, 0, 0.0f}, {40000, 1, n + 5, 0}, {44000, 1, n + 7, 0}};
}
// Renders total samples in blocks given by the cyclic pattern, delivering events at exact sample offsets.
std::vector<float> render(Engine& e, const std::vector<Ev>& evs, long total, const std::vector<int>& pattern) {
    std::vector<float> out(static_cast<size_t>(total)), l(8192), r(8192);
    long pos = 0; size_t next = 0, pi = 0;
    while (pos < total) {
        int n = pattern[pi++ % pattern.size()]; if (pos + n > total) n = static_cast<int>(total - pos);
        while (next < evs.size() && evs[next].at < pos + n) {
            const Ev& v = evs[next++]; const int off = static_cast<int>(v.at - pos);
            if (v.type == 0) e.noteOn(v.a, v.b, off); else if (v.type == 1) e.noteOff(v.a, off);
            else if (v.type == 2) e.controlChange(v.a, v.b, off); else if (v.type == 3) e.pitchBend(v.b, off);
        }
        e.process(l.data(), r.data(), n);
        for (int k = 0; k < n; ++k) out[static_cast<size_t>(pos + k)] = 0.5f * (l[k] + r[k]);
        pos += n;
    }
    return out;
}
double rmsDb(const std::vector<float>& x, size_t a, size_t b) {
    double s = 0; for (size_t i = a; i < b; ++i) s += double(x[i]) * x[i];
    return 10.0 * std::log10(s / double(b - a) + 1e-30);
}
}  // namespace

TEST_CASE("T-008 each instrument exposes exactly the frozen parameter table", "[unit][engine]") {
    for (Instrument ins : kAllInstruments) {
        auto e = Engine::create(ins);
        REQUIRE(e != nullptr);
        CHECK(e->instrument() == ins);
        const auto exp = expectedParams(ins);
        REQUIRE(e->numParams() == static_cast<int>(exp.size()));
        e->prepare(48000.0, 512);
        for (int i = 0; i < e->numParams(); ++i) {
            const ParamInfo p = e->paramInfo(i);
            INFO(instrumentName(ins) << " param " << i << " " << exp[static_cast<size_t>(i)].id);
            CHECK(std::string(p.id) == exp[static_cast<size_t>(i)].id);
            CHECK(p.min == exp[static_cast<size_t>(i)].min);
            CHECK(p.max == exp[static_cast<size_t>(i)].max);
            CHECK(p.def == exp[static_cast<size_t>(i)].def);
            CHECK(p.steps == exp[static_cast<size_t>(i)].steps);
            CHECK(std::string(p.name).size() > 0);
            CHECK(e->paramIndex(p.id) == i);
            CHECK(e->getParam(i) == p.def);
            e->setParam(i, p.max + 100.0f); CHECK(e->getParam(i) == p.max);   // clamped
            e->setParam(i, p.min - 100.0f); CHECK(e->getParam(i) == p.min);
        }
        CHECK(e->paramIndex("no_such_param") == -1);
    }
}

TEST_CASE("T-008 instrument names", "[unit][engine]") {
    const char* names[5] = {"harmonica", "accordion", "melodion", "mandolin", "bouzouki"};
    for (int i = 0; i < 5; ++i) {
        CHECK(std::string(instrumentName(kAllInstruments[i])) == names[i]);
        Instrument out = Instrument::Bouzouki;
        CHECK(instrumentFromName(names[i], out)); CHECK(out == kAllInstruments[i]);
    }
    Instrument out = Instrument::Harmonica;
    CHECK_FALSE(instrumentFromName("melodica", out));
    CHECK_FALSE(instrumentFromName("", out));
}

TEST_CASE("T-009 output stays finite and within [-1, 1] under random events and parameters", "[integration][engine][robustness]") {
    for (Instrument ins : kAllInstruments) {
        for (double sr : {44100.0, 96000.0}) {
            auto e = Engine::create(ins); e->prepare(sr, 256);
            std::mt19937 rng(20261114u + static_cast<unsigned>(ins));   // fixed seed
            std::uniform_real_distribution<float> u(0.0f, 1.0f);
            std::vector<float> l(256), r(256);
            bool finite = true; float peak = 0;
            for (int block = 0; block < 1500; ++block) {   // 8 s at 48 kHz
                for (int k = 0; k < 3; ++k) {
                    const float c = u(rng); const int off = static_cast<int>(u(rng) * 255);
                    if (c < 0.30f) e->noteOn(static_cast<int>(u(rng) * 127), u(rng), off);
                    else if (c < 0.50f) e->noteOff(static_cast<int>(u(rng) * 127), off);
                    else if (c < 0.65f) e->controlChange(static_cast<int>(u(rng) * 127), u(rng), off);
                    else if (c < 0.75f) e->pitchBend(u(rng) * 2 - 1, off);
                    else if (c < 0.95f) { const int p = static_cast<int>(u(rng) * e->numParams()) % e->numParams(); const ParamInfo pi = e->paramInfo(p);
                                          e->setParam(p, pi.min + u(rng) * (pi.max - pi.min)); }
                    else e->allNotesOff(off);
                }
                e->process(l.data(), r.data(), 256);
                for (int i = 0; i < 256; ++i) { finite = finite && std::isfinite(l[i]) && std::isfinite(r[i]); peak = std::max({peak, std::fabs(l[i]), std::fabs(r[i])}); }
            }
            INFO(instrumentName(ins) << " at " << sr);
            CHECK(finite);
            CHECK(peak <= 1.0f);
        }
    }
}

TEST_CASE("T-009 out-of-range event arguments are ignored, not fatal", "[unit][engine][robustness]") {
    for (Instrument ins : kAllInstruments) {
        auto e = Engine::create(ins); e->prepare(48000.0, 64);
        std::vector<float> l(64), r(64);
        e->noteOn(-5, 0.5f, 0); e->noteOn(400, 0.5f, 0); e->noteOn(60, -3.0f, 0); e->noteOn(60, 9.0f, 0);
        e->noteOff(999, 0); e->controlChange(-1, 0.5f, 0); e->controlChange(200, 2.0f, 0); e->pitchBend(50.0f, 0);
        e->noteOn(safeNote(ins), 0.5f, -10); e->noteOn(safeNote(ins), 0.5f, 5000);   // offsets outside the block are clamped
        e->setParam(-1, 0.5f); e->setParam(10000, 0.5f);
        e->setParam(0, std::nanf("")); e->controlChange(1, std::nanf(""), 0);
        e->process(l.data(), r.data(), 64);
        bool finite = true; for (int i = 0; i < 64; ++i) finite = finite && std::isfinite(l[i]) && std::isfinite(r[i]);
        CHECK(finite);
        CHECK(std::isfinite(e->getParam(0)));
    }
}

TEST_CASE("T-010 output does not depend on the block size", "[integration][engine]") {
    // Tolerance 1e-5 absolute (about -100 dBFS): events are applied at exact sample offsets, so only rounding may differ.
    for (Instrument ins : kAllInstruments) {
        const long total = 48000;
        auto a = Engine::create(ins); a->prepare(48000.0, 4096);
        auto b = Engine::create(ins); b->prepare(48000.0, 4096);
        auto c = Engine::create(ins); c->prepare(48000.0, 4096);
        const auto x = render(*a, script(ins), total, {512});
        const auto y = render(*b, script(ins), total, {64});
        const auto z = render(*c, script(ins), total, {1, 7, 4096, 33, 128, 1});
        double dxy = 0, dxz = 0, peak = 0;
        for (size_t i = 0; i < x.size(); ++i) { dxy = std::max(dxy, double(std::fabs(x[i] - y[i]))); dxz = std::max(dxz, double(std::fabs(x[i] - z[i]))); peak = std::max(peak, double(std::fabs(x[i]))); }
        INFO(instrumentName(ins));
        CHECK(peak > 0.01);   // the script must actually sound
        CHECK(dxy <= 1e-5);
        CHECK(dxz <= 1e-5);
    }
}

TEST_CASE("T-011 no heap allocation in events, setParam or process", "[integration][engine][realtime]") {
    // Self-test of the probe: it must see an allocation when one happens.
    gAllocations = 0; gArmed = true; { auto* p = new int(1); delete p; } gArmed = false;
    REQUIRE(gAllocations.load() == 1);
    for (Instrument ins : kAllInstruments) {
        auto e = Engine::create(ins); e->prepare(48000.0, 512);
        std::vector<float> l(512), r(512);
        const int n = safeNote(ins);
        e->noteOn(n, 0.9f, 0); e->process(l.data(), r.data(), 512);   // warm-up outside the armed region
        gAllocations = 0; gArmed = true;
        for (int block = 0; block < 200; ++block) {
            if (block % 7 == 0) e->noteOn(n + (block % 12), 0.7f, block % 512);
            if (block % 11 == 0) e->noteOff(n + (block % 12), 3);
            if (block % 5 == 0) e->setParam(block % e->numParams(), e->paramInfo(block % e->numParams()).def);
            if (block % 13 == 0) e->controlChange(1, 0.5f, 0);
            if (block % 17 == 0) e->pitchBend(-0.3f, 0);
            if (block == 150) e->allNotesOff(0);
            e->process(l.data(), r.data(), 512);
        }
        gArmed = false;
        INFO(instrumentName(ins));
        CHECK(gAllocations.load() == 0);
    }
}

TEST_CASE("T-012 the same events after reset give the same samples", "[integration][engine]") {
    for (Instrument ins : kAllInstruments) {
        auto e = Engine::create(ins); e->prepare(48000.0, 512);
        const auto x = render(*e, script(ins), 48000, {512});
        e->reset();
        const auto y = render(*e, script(ins), 48000, {512});
        INFO(instrumentName(ins));
        CHECK(x == y);   // bit-exact: noise generators are reseeded by reset()
    }
}

TEST_CASE("T-014 state text round trip", "[unit][engine][security]") {
    for (Instrument ins : kAllInstruments) {
        auto a = Engine::create(ins); a->prepare(48000.0, 512);
        for (int i = 0; i < a->numParams(); ++i) { const ParamInfo p = a->paramInfo(i); a->setParam(i, p.min + 0.37f * (p.max - p.min)); }
        const std::string s = a->saveState();
        CHECK(s.rfind(std::string("folk-state 1 ") + instrumentName(ins) + "\n", 0) == 0);
        auto b = Engine::create(ins); b->prepare(48000.0, 512);
        REQUIRE(b->loadState(s));
        for (int i = 0; i < a->numParams(); ++i) CHECK(b->getParam(i) == a->getParam(i));
        CHECK(b->saveState() == s);
    }
}

TEST_CASE("T-014 malformed state is refused and changes nothing", "[unit][engine][security]") {
    for (Instrument ins : kAllInstruments) {
        auto e = Engine::create(ins); e->prepare(48000.0, 512);
        const std::string good = e->saveState();
        const Instrument other = ins == Instrument::Harmonica ? Instrument::Mandolin : Instrument::Harmonica;
        auto o = Engine::create(other); o->prepare(48000.0, 512);
        std::vector<std::string> bad = {"", "garbage", "folk-state 2 " + std::string(instrumentName(ins)) + "\n", o->saveState(),
                                        good.substr(0, good.size() / 2) + "\x01\x02\xff", std::string(70000, 'a'),
                                        "folk-state 1 " + std::string(instrumentName(ins)) + "\nlevel=abc\n",
                                        "folk-state 1 " + std::string(instrumentName(ins)) + "\nlevel=nan\n",
                                        "folk-state 1 " + std::string(instrumentName(ins)) + "\nlevel=1e999\n",
                                        "folk-state 1 " + std::string(instrumentName(ins)) + "\nno_such_param=1\n",
                                        std::string("folk-state 1 ") + instrumentName(ins) + std::string("\n\0level=0.1\n", 12)};
        for (size_t k = 0; k < bad.size(); ++k) {
            INFO(instrumentName(ins) << " malformed case " << k);
            CHECK_NOTHROW(e->loadState(bad[k]));
            CHECK_FALSE(e->loadState(bad[k]));
            CHECK(e->saveState() == good);
        }
        // Values outside a parameter's range are clamped, not refused.
        CHECK(e->loadState("folk-state 1 " + std::string(instrumentName(ins)) + "\nlevel=7\n"));
        CHECK(e->getParam(e->paramIndex("level")) == 1.0f);
    }
}

TEST_CASE("T-015 after notes end the output falls below -90 dBFS within tailSeconds()", "[integration][engine]") {
    for (Instrument ins : kAllInstruments) {
        auto e = Engine::create(ins); e->prepare(48000.0, 512);
        const double tail = e->tailSeconds();
        INFO(instrumentName(ins) << " tail " << tail);
        REQUIRE(tail > 0.0);
        REQUIRE(tail <= 30.0);
        const int n = safeNote(ins);
        const long off = 24000, total = off + static_cast<long>(tail * 48000.0) + 9600;
        const auto x = render(*e, {{0, 0, n, 0.9f}, {off, 1, n, 0}}, total, {512});
        CHECK(rmsDb(x, 4800, 24000) > -50.0);                                            // it sounded
        CHECK(rmsDb(x, static_cast<size_t>(total - 9600), static_cast<size_t>(total)) < -90.0);   // and it stopped
    }
}
