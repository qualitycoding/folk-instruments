// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// T-016 the state text does not depend on the process locale (SC-11; D-090; pre-mortem R-017: a host running under a
// decimal-comma locale must not lose its sessions; both the C and the C++ global locale are switched). A separate program (folk-locale-tests), so that the locale change
// cannot leak into other test cases. Failing to set a comma locale fails the test; it is never skipped.
#include <catch2/catch_test_macros.hpp>
#include <clocale>
#include <cstring>
#include <exception>
#include <locale>
#include <sstream>
#include <string>
#include "folk/engine.h"
#include "param_table.h"
using namespace folk;

namespace {
// Both the C locale (printf, strtod) and the C++ global locale (default-constructed streams) are switched: a host may
// change either, and a stream left on the global locale writes "0,5" (planning audit, TP-LOC-2).
bool setCommaLocale() {
    for (const char* name : {"de_DE.UTF-8", "de_DE.utf8", "de_DE", "German_Germany.1252", "German", "de-DE"}) {
        if (std::setlocale(LC_ALL, name) == nullptr || std::strcmp(std::localeconv()->decimal_point, ",") != 0) continue;
        try {
            std::locale cpp(name);
            if (std::use_facet<std::numpunct<char>>(cpp).decimal_point() != ',') continue;
            std::locale::global(cpp);
        } catch (const std::exception&) { continue; }
        std::ostringstream probe; probe << 0.5;
        if (probe.str() == "0,5") return true;   // the switch is real for streams as well
    }
    std::setlocale(LC_ALL, "C");
    std::locale::global(std::locale::classic());
    return false;
}
struct RestoreC { ~RestoreC() { std::setlocale(LC_ALL, "C"); std::locale::global(std::locale::classic()); } };
}  // namespace

TEST_CASE("T-016 state text round trip under a decimal-comma locale", "[unit][engine][security][locale]") {
    RestoreC restore;
    REQUIRE(setCommaLocale());   // CI provides de_DE.UTF-8 (Ubuntu: locale-gen) or German (Windows)
    for (Instrument ins : kAllInstruments) {
        INFO(instrumentName(ins));
        auto a = Engine::create(ins); a->prepare(48000.0, 512);
        for (int i = 0; i < a->numParams(); ++i) { const ParamInfo p = a->paramInfo(i); a->setParam(i, p.min + 0.37f * (p.max - p.min)); }
        const std::string s = a->saveState();
        CHECK(s.find(',') == std::string::npos);   // numbers use '.', whatever the locale
        auto b = Engine::create(ins); b->prepare(48000.0, 512);
        REQUIRE(b->loadState(s));
        for (int i = 0; i < a->numParams(); ++i) CHECK(b->getParam(i) == a->getParam(i));
        CHECK(b->saveState() == s);
    }
}

TEST_CASE("T-016 a state written in the C locale loads under a decimal-comma locale", "[unit][engine][security][locale]") {
    RestoreC restore;
    std::setlocale(LC_ALL, "C");
    auto a = Engine::create(Instrument::Accordion); a->prepare(48000.0, 512);
    a->setParam(a->paramIndex("level"), 0.55f);
    const std::string s = a->saveState();
    REQUIRE(setCommaLocale());
    auto b = Engine::create(Instrument::Accordion); b->prepare(48000.0, 512);
    REQUIRE(b->loadState(s));
    CHECK(b->getParam(b->paramIndex("level")) == a->getParam(a->paramIndex("level")));
    REQUIRE(b->loadState("folk-state 1 accordion\nlevel=0.25\n"));
    CHECK(b->getParam(b->paramIndex("level")) == 0.25f);
    CHECK_FALSE(b->loadState("folk-state 1 accordion\nlevel=0,25\n"));   // a comma is not a decimal separator in the grammar
}
