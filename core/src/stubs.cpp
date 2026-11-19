// Stubs: every function throws folk::NotImplemented until its implementing step replaces it (plan/PLAN.md, steps S-100 to S-300).
#include "folk/engine.h"
#include "folk/strings.h"
#include "folk/tuning.h"

namespace folk {
#define FOLK_STUB(name) throw NotImplemented(name)
}  // namespace folk
