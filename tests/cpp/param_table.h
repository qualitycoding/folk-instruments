// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// The parameter table of every instrument (plan/DECISIONS.md, D-091). Shared by the engine tests.
#pragma once
#include "folk/engine.h"
#include <vector>

struct ExpectedParam { const char* id; float min, max, def; int steps; };

inline std::vector<ExpectedParam> expectedParams(folk::Instrument i) {
    using P = ExpectedParam;
    std::vector<P> common = {P{"level", 0, 1, 0.7f, 0}, P{"a4_hz", 415, 466, 440, 0}};
    std::vector<P> reed = {P{"breath", 0, 1, 0.5f, 0}, P{"breath_source", 0, 2, 0, 3}, P{"vibrato_rate_hz", 0, 10, 5.5f, 0},
                           P{"vibrato_depth", 0, 1, 0, 0}, P{"air_noise", 0, 1, 0.2f, 0}};
    std::vector<P> pluck = {P{"pick_position", 0.03f, 0.5f, 0.12f, 0}, P{"pick_stiffness", 0, 1, 0.6f, 0},
                            P{"pair_detune_cents", 0, 8, 1.5f, 0}, P{"course_mode", 0, 1, 0, 2}, P{"body_coupling", 0, 1, 1, 0},
                            P{"damping", 0, 1, 0.3f, 0}, P{"tremolo", 0, 1, 0, 2}, P{"tremolo_rate_hz", 4, 20, 12, 0},
                            P{"bend_range", 0, 12, 2, 13}};
    std::vector<P> own;
    switch (i) {
        case folk::Instrument::Harmonica:
            own = {P{"variant", 0, 1, 0, 2}, P{"key", 0, 11, 0, 12}, P{"wah", 0, 1, 0, 0}, P{"airtightness", 0, 1, 0.9f, 0}, P{"valve_buzz", 0, 1, 0, 0}};
            common.insert(common.end(), reed.begin(), reed.end());
            break;
        case folk::Instrument::Accordion:
            own = {P{"register", 0, 11, 1, 12}, P{"cassotto", 0, 1, 0, 2}, P{"musette_cents", 0, 25, 15, 0}, P{"musette_scaling", 0, 1, 0, 2},
                   P{"bend_cents", 0, 25, 25, 0}, P{"sordina", 0, 1, 0, 2}, P{"key_noise", 0, 1, 0.1f, 0}};
            common.insert(common.end(), reed.begin(), reed.end());
            break;
        case folk::Instrument::Melodion:
            own = {P{"range", 0, 2, 1, 3}, P{"body", 0, 2, 0, 3}, P{"breath_mode", 0, 1, 0, 2}, P{"moisture", 0, 1, 0, 0}};
            common.insert(common.end(), reed.begin(), reed.end());
            break;
        case folk::Instrument::Mandolin:
            own = {P{"body", 0, 2, 0, 3}};
            common.insert(common.end(), pluck.begin(), pluck.end());
            break;
        case folk::Instrument::Bouzouki:
            own = {P{"variant", 0, 2, 1, 3}, P{"octave_order", 0, 1, 0, 2}};
            common.insert(common.end(), pluck.begin(), pluck.end());
            break;
    }
    common.insert(common.end(), own.begin(), own.end());
    return common;
}

inline const folk::Instrument kAllInstruments[5] = {folk::Instrument::Harmonica, folk::Instrument::Accordion, folk::Instrument::Melodion,
                                                    folk::Instrument::Mandolin, folk::Instrument::Bouzouki};
/// A MIDI note every instrument can play with its default settings.
inline int safeNote(folk::Instrument i) { return i == folk::Instrument::Harmonica ? 72 : 69; }
