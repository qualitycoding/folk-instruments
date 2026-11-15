// Pitch helpers, harmonica layout, accordion registers and string courses (plan/DECISIONS.md, D-020 to D-023, D-030, D-070, D-073).
#pragma once
#include <vector>

namespace folk {

/// 12-tone equal temperament: a4Hz * 2^((midiNote - 69) / 12).
double midiToHz(double midiNote, double a4Hz = 440.0);

// ---------------------------------------------------------------- harmonica
enum class Breath { Blow = 0, Draw = 1 };
enum class HarpNoteKind { None = 0, Natural = 1, Bend = 2, Overbend = 3 };

/// key: 0 = C, 1 = D-flat, ... 11 = B. Keys 0..6 (C to F-sharp) have hole 1 blow at MIDI 60 + key;
/// keys 7..11 (G to B) have it at MIDI 48 + key. hole: 1..10. Returns the MIDI note of the unbent reed.
int diatonicReedNote(int key, int hole, Breath breath);

struct HarpNote {
    HarpNoteKind kind = HarpNoteKind::None;
    int hole = 0;             ///< 1..10 (diatonic) or 1..12 (chromatic)
    Breath breath = Breath::Blow;
    int bendSemitones = 0;    ///< Bend: 1..3 below the natural note of (hole, breath). Overbend: 0.
    bool slideIn = false;     ///< chromatic only
};

/// How a 10-hole Richter diatonic in the given key produces a MIDI note (D-021). kind == None if it cannot.
HarpNote diatonicNoteFor(int key, int midiNote);
/// The largest whole-semitone bend available on (hole, breath) of a diatonic (0 if none).
int diatonicMaxBend(int hole, Breath breath);
/// How a 12-hole solo-tuned chromatic in C (lowest note MIDI 60, highest MIDI 97) produces a MIDI note (D-023).
HarpNote chromaticNoteFor(int midiNote);

// ---------------------------------------------------------------- accordion
/// Bit mask of reed ranks.
enum Rank : unsigned { RankL = 1u, RankMminus = 2u, RankM = 4u, RankMplus = 8u, RankH = 16u };
/// Register index 0..11 in the order of D-030. Returns 0 for an index out of range.
unsigned accordionRegisterRanks(int registerIndex);
const char* accordionRegisterName(int registerIndex);

// ---------------------------------------------------------------- plucked instruments
struct StringSpec {
    int midiNote;         ///< open pitch
    double diameterM;     ///< outer diameter of a plain string; core diameter of a wound string (0.4 x the outer diameter listed in D-072)
    bool wound;
    double linearDensity; ///< kg/m
};
struct CourseSpec {
    StringSpec first, second;  ///< the strings in the order a downstroke meets them
};
/// instrumentVariant: mandolin 0 = f-hole, 1 = oval-hole, 2 = bowl-back; bouzouki 0 = trichordo, 1 = tetrachordo, 2 = Irish.
/// Courses are ordered from the lowest-pitched to the highest-pitched.
std::vector<CourseSpec> mandolinCourses(int instrumentVariant);
std::vector<CourseSpec> bouzoukiCourses(int instrumentVariant);
double mandolinScaleLengthM(int instrumentVariant);
double bouzoukiScaleLengthM(int instrumentVariant);
/// Index of the course that plays a MIDI note: the highest-pitched course whose lower open string is <= the note,
/// provided the fret (note minus that open pitch) is <= maxFret; otherwise -1.
int courseForNote(const std::vector<CourseSpec>& courses, int midiNote, int maxFret);

}  // namespace folk
