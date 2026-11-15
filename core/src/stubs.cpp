// Stubs: every function throws folk::NotImplemented until its implementing step replaces it (plan/PLAN.md, steps S-100 to S-300).
#include "folk/engine.h"
#include "folk/strings.h"
#include "folk/tuning.h"

namespace folk {
#define FOLK_STUB(name) throw NotImplemented(name)
const char* instrumentName(Instrument) { FOLK_STUB("instrumentName"); }
bool instrumentFromName(std::string_view, Instrument&) { FOLK_STUB("instrumentFromName"); }
std::unique_ptr<Engine> Engine::create(Instrument) { FOLK_STUB("Engine::create"); }
double midiToHz(double, double) { FOLK_STUB("midiToHz"); }
int diatonicReedNote(int, int, Breath) { FOLK_STUB("diatonicReedNote"); }
HarpNote diatonicNoteFor(int, int) { FOLK_STUB("diatonicNoteFor"); }
int diatonicMaxBend(int, Breath) { FOLK_STUB("diatonicMaxBend"); }
HarpNote chromaticNoteFor(int) { FOLK_STUB("chromaticNoteFor"); }
unsigned accordionRegisterRanks(int) { FOLK_STUB("accordionRegisterRanks"); }
const char* accordionRegisterName(int) { FOLK_STUB("accordionRegisterName"); }
std::vector<CourseSpec> mandolinCourses(int) { FOLK_STUB("mandolinCourses"); }
std::vector<CourseSpec> bouzoukiCourses(int) { FOLK_STUB("bouzoukiCourses"); }
double mandolinScaleLengthM(int) { FOLK_STUB("mandolinScaleLengthM"); }
double bouzoukiScaleLengthM(int) { FOLK_STUB("bouzoukiScaleLengthM"); }
int courseForNote(const std::vector<CourseSpec>&, int, int) { FOLK_STUB("courseForNote"); }
double inharmonicityB(double, double, double, double) { FOLK_STUB("inharmonicityB"); }
double partialHz(double, double, int) { FOLK_STUB("partialHz"); }
double stringTensionN(double, double, double) { FOLK_STUB("stringTensionN"); }
double lossFactorAir(double, double, double, double, double) { FOLK_STUB("lossFactorAir"); }
double lossFactorBending(double, double, double, double, double, int, double) { FOLK_STUB("lossFactorBending"); }
double lossFactorBridge(double, int, double, double) { FOLK_STUB("lossFactorBridge"); }
PairModes solveCoupledPair(double, double, double, double, std::complex<double>, double) { FOLK_STUB("solveCoupledPair"); }
}  // namespace folk
