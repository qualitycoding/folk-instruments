// Stubs: every function throws folk::NotImplemented until its implementing step replaces it (plan/PLAN.md, steps S-100 to S-300).
#include "folk/engine.h"
#include "folk/strings.h"
#include "folk/tuning.h"

namespace folk {
#define FOLK_STUB(name) throw NotImplemented(name)
const char* instrumentName(Instrument) { FOLK_STUB("instrumentName"); }
bool instrumentFromName(std::string_view, Instrument&) { FOLK_STUB("instrumentFromName"); }
std::unique_ptr<Engine> Engine::create(Instrument) { FOLK_STUB("Engine::create"); }
}  // namespace folk
