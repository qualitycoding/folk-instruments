// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// T-001 midiToHz (SC-03; C-034, knowledge K-20261101T043000Z twelve-tet formula)
// T-002 Richter diatonic layout in every key (SC-05; C-011)
// T-003 note mapping for the diatonic (naturals, bends, overbends) and the chromatic (SC-05; C-012, C-013, C-014; D-021, D-023)
// T-004 accordion register table (SC-06; C-017; D-030)
// T-007 string courses and note-to-course rule (SC-10; C-034, C-039, C-040; D-070, D-073)
#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>
#include "folk/tuning.h"
using namespace folk;
using Catch::Matchers::WithinRel;

TEST_CASE("T-001 midiToHz follows 12-tone equal temperament", "[unit][tuning]") {
    // Tolerance 1e-12 relative: the formula is exact up to floating-point rounding of pow().
    CHECK_THAT(midiToHz(69), WithinRel(440.0, 1e-12));
    CHECK_THAT(midiToHz(60), WithinRel(261.6255653005986, 1e-12));
    CHECK_THAT(midiToHz(81), WithinRel(880.0, 1e-12));
    CHECK_THAT(midiToHz(69, 442.0), WithinRel(442.0, 1e-12));
    CHECK_THAT(midiToHz(69.5), WithinRel(440.0 * 1.0293022366434921, 1e-12));
}

TEST_CASE("T-002 Richter layout in C", "[unit][harmonica]") {
    const int blow[10] = {60, 64, 67, 72, 76, 79, 84, 88, 91, 96};   // C4 E4 G4 C5 E5 G5 C6 E6 G6 C7
    const int draw[10] = {62, 67, 71, 74, 77, 81, 83, 86, 89, 93};   // D4 G4 B4 D5 F5 A5 B5 D6 F6 A6
    for (int h = 1; h <= 10; ++h) {
        CHECK(diatonicReedNote(0, h, Breath::Blow) == blow[h - 1]);
        CHECK(diatonicReedNote(0, h, Breath::Draw) == draw[h - 1]);
    }
}

TEST_CASE("T-002 Richter layout transposes by key", "[unit][harmonica]") {
    const int hole1Blow[12] = {60, 61, 62, 63, 64, 65, 66, 55, 56, 57, 58, 59};  // C..F# above middle C, G..B below (D-020)
    for (int key = 0; key < 12; ++key) {
        CHECK(diatonicReedNote(key, 1, Breath::Blow) == hole1Blow[key]);
        CHECK(diatonicReedNote(key, 10, Breath::Draw) - diatonicReedNote(key, 1, Breath::Blow) == 33);
    }
    CHECK(diatonicReedNote(7, 4, Breath::Blow) == 67);  // G harmonica, hole 4: G4
    CHECK(diatonicReedNote(7, 4, Breath::Draw) == 69);  // and A4 (the 444 Hz reed of C-011)
}

TEST_CASE("T-002 invalid layout arguments throw std::out_of_range", "[unit][harmonica]") {
    CHECK_THROWS_AS(diatonicReedNote(12, 1, Breath::Blow), std::out_of_range);
    CHECK_THROWS_AS(diatonicReedNote(-1, 1, Breath::Blow), std::out_of_range);
    CHECK_THROWS_AS(diatonicReedNote(0, 0, Breath::Blow), std::out_of_range);
    CHECK_THROWS_AS(diatonicReedNote(0, 11, Breath::Draw), std::out_of_range);
}

TEST_CASE("T-003 maximum bends of the diatonic", "[unit][harmonica]") {
    const int drawBend[10] = {1, 2, 3, 1, 0, 1, 0, 0, 0, 0};
    const int blowBend[10] = {0, 0, 0, 0, 0, 0, 0, 1, 1, 2};
    for (int h = 1; h <= 10; ++h) {
        CHECK(diatonicMaxBend(h, Breath::Draw) == drawBend[h - 1]);
        CHECK(diatonicMaxBend(h, Breath::Blow) == blowBend[h - 1]);
    }
}

namespace {
struct Row { int midi; HarpNoteKind kind; int hole; Breath breath; int bend; };
}

TEST_CASE("T-003 every note from C4 to D-flat 7 on a C diatonic", "[unit][harmonica]") {
    const auto N = HarpNoteKind::Natural; const auto B = HarpNoteKind::Bend; const auto O = HarpNoteKind::Overbend;
    const auto b = Breath::Blow; const auto d = Breath::Draw;
    const Row rows[] = {
        {60, N, 1, b, 0}, {61, B, 1, d, 1}, {62, N, 1, d, 0}, {63, O, 1, b, 0}, {64, N, 2, b, 0}, {65, B, 2, d, 2},
        {66, B, 2, d, 1}, {67, N, 2, d, 0}, {68, B, 3, d, 3}, {69, B, 3, d, 2}, {70, B, 3, d, 1}, {71, N, 3, d, 0},
        {72, N, 4, b, 0}, {73, B, 4, d, 1}, {74, N, 4, d, 0}, {75, O, 4, b, 0}, {76, N, 5, b, 0}, {77, N, 5, d, 0},
        {78, O, 5, b, 0}, {79, N, 6, b, 0}, {80, B, 6, d, 1}, {81, N, 6, d, 0}, {82, O, 6, b, 0}, {83, N, 7, d, 0},
        {84, N, 7, b, 0}, {85, O, 7, d, 0}, {86, N, 8, d, 0}, {87, B, 8, b, 1}, {88, N, 8, b, 0}, {89, N, 9, d, 0},
        {90, B, 9, b, 1}, {91, N, 9, b, 0}, {92, O, 9, d, 0}, {93, N, 10, d, 0}, {94, B, 10, b, 2}, {95, B, 10, b, 1},
        {96, N, 10, b, 0}, {97, O, 10, d, 0}};
    for (const Row& r : rows) {
        INFO("midi " << r.midi);
        const HarpNote n = diatonicNoteFor(0, r.midi);
        CHECK(n.kind == r.kind);
        CHECK(n.hole == r.hole);
        CHECK(n.breath == r.breath);
        CHECK(n.bendSemitones == r.bend);
        CHECK(n.slideIn == false);
    }
    CHECK(diatonicNoteFor(0, 59).kind == HarpNoteKind::None);
    CHECK(diatonicNoteFor(0, 98).kind == HarpNoteKind::None);
    // Key G: everything five semitones lower.
    CHECK(diatonicNoteFor(7, 69).kind == HarpNoteKind::Natural);
    CHECK(diatonicNoteFor(7, 69).hole == 4);
    CHECK(diatonicNoteFor(7, 69).breath == Breath::Draw);
}

TEST_CASE("T-003 chromatic harmonica in C, solo tuning", "[unit][harmonica]") {
    const auto b = Breath::Blow; const auto d = Breath::Draw;
    struct CRow { int midi; int hole; Breath breath; bool slide; };
    const CRow rows[] = {{60, 1, b, false}, {61, 1, b, true}, {62, 1, d, false}, {63, 1, d, true}, {64, 2, b, false},
                         {65, 2, d, false}, {66, 2, d, true}, {67, 3, b, false}, {68, 3, b, true}, {69, 3, d, false},
                         {70, 3, d, true}, {71, 4, d, false}, {72, 4, b, false}, {73, 4, b, true}, {84, 8, b, false},
                         {95, 12, d, false}, {96, 12, b, false}, {97, 12, b, true}};
    for (const CRow& r : rows) {
        INFO("midi " << r.midi);
        const HarpNote n = chromaticNoteFor(r.midi);
        CHECK(n.kind == HarpNoteKind::Natural);
        CHECK(n.hole == r.hole);
        CHECK(n.breath == r.breath);
        CHECK(n.slideIn == r.slide);
        CHECK(n.bendSemitones == 0);
    }
    CHECK(chromaticNoteFor(59).kind == HarpNoteKind::None);
    CHECK(chromaticNoteFor(98).kind == HarpNoteKind::None);
}

TEST_CASE("T-004 accordion register table", "[unit][accordion]") {
    const unsigned L = RankL, Mm = RankMminus, M = RankM, Mp = RankMplus, Hh = RankH;
    const unsigned expected[12] = {Hh, M, L, M | Hh, M | Mp, M | Mp | Hh, Mm | M | Mp, L | Hh, L | M | Hh, L | M, L | M | Mp, L | M | Mp | Hh};
    const char* names[12] = {"Piccolo", "Clarinet", "Bassoon", "Oboe", "Violin", "Musette (imitation)", "Musette (authentic)",
                             "Organ", "Harmonium", "Bandoneon", "Accordion", "Master"};
    for (int i = 0; i < 12; ++i) {
        INFO("register " << i);
        CHECK(accordionRegisterRanks(i) == expected[i]);
        CHECK(std::string(accordionRegisterName(i)) == names[i]);
    }
    CHECK(accordionRegisterRanks(-1) == 0u);
    CHECK(accordionRegisterRanks(12) == 0u);
}

TEST_CASE("T-007 mandolin courses", "[unit][strings]") {
    for (int variant = 0; variant < 3; ++variant) {
        const auto c = mandolinCourses(variant);
        REQUIRE(c.size() == 4);
        const int open[4] = {55, 62, 69, 76};  // G3 D4 A4 E5
        for (int i = 0; i < 4; ++i) {
            CHECK(c[i].first.midiNote == open[i]);
            CHECK(c[i].second.midiNote == open[i]);
            CHECK(c[i].first.wound == (i < 2));
            CHECK(c[i].first.linearDensity > 0.0);
        }
    }
    CHECK_THAT(mandolinScaleLengthM(0), WithinRel(0.3524, 1e-9));
    CHECK_THAT(mandolinScaleLengthM(1), WithinRel(0.3524, 1e-9));
    CHECK_THAT(mandolinScaleLengthM(2), WithinRel(0.330, 1e-9));
    // Plain strings: linear density is rho * pi * d^2 / 4 with rho = 7850 kg/m3 (0.5 % tolerance for rounding of the gauge).
    const auto f = mandolinCourses(0);
    CHECK_THAT(f[2].first.diameterM, WithinRel(0.015 * 0.0254, 1e-6));
    CHECK_THAT(f[2].first.linearDensity, WithinRel(0.000894972, 5e-3));
    CHECK_THAT(f[3].first.diameterM, WithinRel(0.011 * 0.0254, 1e-6));
}

TEST_CASE("T-007 bouzouki courses", "[unit][strings]") {
    const auto tri = bouzoukiCourses(0);
    REQUIRE(tri.size() == 3);
    CHECK(tri[0].first.midiNote == 50);   // D3, the thick string, met first on a downstroke
    CHECK(tri[0].second.midiNote == 62);  // D4
    CHECK(tri[0].first.wound);
    CHECK_FALSE(tri[0].second.wound);
    CHECK(tri[1].first.midiNote == 57); CHECK(tri[1].second.midiNote == 57);
    CHECK(tri[2].first.midiNote == 62); CHECK(tri[2].second.midiNote == 62);

    const auto tet = bouzoukiCourses(1);
    REQUIRE(tet.size() == 4);
    const int lowT[4] = {48, 53, 57, 62}, highT[4] = {60, 65, 57, 62};  // C3C4 F3F4 A3A3 D4D4
    for (int i = 0; i < 4; ++i) { CHECK(tet[i].first.midiNote == lowT[i]); CHECK(tet[i].second.midiNote == highT[i]); }

    const auto irish = bouzoukiCourses(2);
    REQUIRE(irish.size() == 4);
    const int openI[4] = {43, 50, 57, 62};  // G2 D3 A3 D4, unison pairs
    for (int i = 0; i < 4; ++i) { CHECK(irish[i].first.midiNote == openI[i]); CHECK(irish[i].second.midiNote == openI[i]); }
    CHECK(irish[0].first.wound); CHECK(irish[1].first.wound); CHECK_FALSE(irish[2].first.wound); CHECK_FALSE(irish[3].first.wound);

    CHECK_THAT(bouzoukiScaleLengthM(0), WithinRel(0.680, 1e-9));
    CHECK_THAT(bouzoukiScaleLengthM(1), WithinRel(0.680, 1e-9));
    CHECK_THAT(bouzoukiScaleLengthM(2), WithinRel(0.650, 1e-9));
    CHECK_THROWS_AS(bouzoukiCourses(3), std::out_of_range);
    CHECK_THROWS_AS(mandolinCourses(-1), std::out_of_range);
}

TEST_CASE("T-007 note-to-course rule", "[unit][strings]") {
    const auto m = mandolinCourses(0);
    CHECK(courseForNote(m, 54, 24) == -1);  // below G3
    CHECK(courseForNote(m, 55, 24) == 0);
    CHECK(courseForNote(m, 61, 24) == 0);
    CHECK(courseForNote(m, 62, 24) == 1);
    CHECK(courseForNote(m, 69, 24) == 2);
    CHECK(courseForNote(m, 76, 24) == 3);
    CHECK(courseForNote(m, 100, 24) == 3);  // fret 24 on the E course
    CHECK(courseForNote(m, 101, 24) == -1);
    const auto tet = bouzoukiCourses(1);
    CHECK(courseForNote(tet, 48, 27) == 0);  // the octave course is addressed by its lower string
    CHECK(courseForNote(tet, 60, 27) == 2);  // C4 is fret 3 on the A course, not the octave string of course 0
}
