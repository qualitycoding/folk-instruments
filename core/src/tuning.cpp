// Pitch helpers, harmonica layout, accordion registers and string courses (plan/DECISIONS.md D-020 to D-023, D-030, D-070 to D-073).
// All tables come from presets/*.json through core/src/generated/presets_data.h.
#include "folk/tuning.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include "generated/presets_data.h"

namespace folk {

double midiToHz(double midiNote, double a4Hz) { return a4Hz * std::pow(2.0, (midiNote - 69.0) / 12.0); }

int diatonicReedNote(int key, int hole, Breath breath) {
    if (key < 0 || key > 11) throw std::out_of_range("diatonicReedNote: key");
    if (hole < 1 || hole > 10) throw std::out_of_range("diatonicReedNote: hole");
    const int hole1 = key <= 6 ? gen::kHarp_key_hole1_blow_high_keys_0_to_6 + key : gen::kHarp_key_hole1_blow_low_keys_7_to_11 + key;
    const int shift = hole1 - gen::kHarp_key_hole1_blow_high_keys_0_to_6;
    return (breath == Breath::Blow ? gen::kHarp_richter_blow_c[hole - 1] : gen::kHarp_richter_draw_c[hole - 1]) + shift;
}

int diatonicMaxBend(int hole, Breath breath) {
    if (hole < 1 || hole > 10) return 0;
    return breath == Breath::Draw ? gen::kHarp_max_bend_draw_holes_1_to_10[hole - 1] : gen::kHarp_max_bend_blow_holes_1_to_10[hole - 1];
}

namespace {
template <size_t N>
bool contains(const int (&a)[N], int v) {
    for (int x : a) if (x == v) return true;
    return false;
}
}  // namespace

HarpNote diatonicNoteFor(int key, int midiNote) {
    HarpNote n;
    // (1) natural notes: holes 1..10, blow before draw.
    for (int h = 1; h <= 10; ++h)
        for (Breath b : {Breath::Blow, Breath::Draw})
            if (diatonicReedNote(key, h, b) == midiNote) { n.kind = HarpNoteKind::Natural; n.hole = h; n.breath = b; return n; }
    // (2) bends: draw bends before blow bends, holes 1..10.
    for (Breath b : {Breath::Draw, Breath::Blow})
        for (int h = 1; h <= 10; ++h)
            for (int depth = 1; depth <= diatonicMaxBend(h, b); ++depth)
                if (diatonicReedNote(key, h, b) - depth == midiNote) {
                    n.kind = HarpNoteKind::Bend; n.hole = h; n.breath = b; n.bendSemitones = depth; return n;
                }
    // (3) overbends: overblow above the draw note, overdraw above the blow note.
    for (int h = 1; h <= 10; ++h) {
        if (contains(gen::kHarp_overblow_holes, h) && diatonicReedNote(key, h, Breath::Draw) + 1 == midiNote) {
            n.kind = HarpNoteKind::Overbend; n.hole = h; n.breath = Breath::Blow; return n;
        }
        if (contains(gen::kHarp_overdraw_holes, h) && diatonicReedNote(key, h, Breath::Blow) + 1 == midiNote) {
            n.kind = HarpNoteKind::Overbend; n.hole = h; n.breath = Breath::Draw; return n;
        }
    }
    return n;
}

HarpNote chromaticNoteFor(int midiNote) {
    HarpNote n;
    for (int h = 1; h <= gen::kHarp_chromatic_holes; ++h) {
        const int group = (h - 1) / 4, idx = (h - 1) % 4;
        const int base = gen::kHarp_chromatic_first_note + 12 * group;
        const int blow = base + gen::kHarp_chromatic_blow_offsets_per_group[idx];
        const int draw = base + gen::kHarp_chromatic_draw_offsets_per_group[idx];
        struct Try { int note; Breath b; bool slide; };
        for (const Try t : {Try{blow, Breath::Blow, false}, Try{draw, Breath::Draw, false}, Try{blow + 1, Breath::Blow, true}, Try{draw + 1, Breath::Draw, true}})
            if (t.note == midiNote) { n.kind = HarpNoteKind::Natural; n.hole = h; n.breath = t.b; n.slideIn = t.slide; return n; }
    }
    return n;
}

unsigned accordionRegisterRanks(int i) {
    return i >= 0 && i < 12 ? gen::kAccRanks[i] : 0u;
}
const char* accordionRegisterName(int i) {
    return i >= 0 && i < 12 ? gen::kAccNames[i] : "";
}

namespace {
std::vector<CourseSpec> toCourses(const gen::CourseSpecData* rows, int count) {
    std::vector<CourseSpec> out;
    for (int i = 0; i < count; ++i) {
        const auto& r = rows[i];
        out.push_back({{r.first.midi, r.first.diameterM, r.first.wound, r.first.linearDensity},
                       {r.second.midi, r.second.diameterM, r.second.wound, r.second.linearDensity}});
    }
    return out;
}
void checkVariant(int v) {
    if (v < 0 || v > 2) throw std::out_of_range("instrument variant");
}
}  // namespace

std::vector<CourseSpec> mandolinCourses(int v) {
    checkVariant(v);
    switch (v) {
        case 0: return toCourses(gen::kMandolinCourses0, gen::kMandolinCourses0Count);
        case 1: return toCourses(gen::kMandolinCourses1, gen::kMandolinCourses1Count);
        default: return toCourses(gen::kMandolinCourses2, gen::kMandolinCourses2Count);
    }
}
std::vector<CourseSpec> bouzoukiCourses(int v) {
    checkVariant(v);
    switch (v) {
        case 0: return toCourses(gen::kBouzoukiCourses0, gen::kBouzoukiCourses0Count);
        case 1: return toCourses(gen::kBouzoukiCourses1, gen::kBouzoukiCourses1Count);
        default: return toCourses(gen::kBouzoukiCourses2, gen::kBouzoukiCourses2Count);
    }
}
double mandolinScaleLengthM(int v) { checkVariant(v); return gen::kMandolinScale[v]; }
double bouzoukiScaleLengthM(int v) { checkVariant(v); return gen::kBouzoukiScale[v]; }

int courseForNote(const std::vector<CourseSpec>& courses, int midiNote, int maxFret) {
    for (int i = int(courses.size()) - 1; i >= 0; --i) {
        const int lower = std::min(courses[i].first.midiNote, courses[i].second.midiNote);
        if (lower <= midiNote) return midiNote - lower <= maxFret ? i : -1;
    }
    return -1;
}

}  // namespace folk
