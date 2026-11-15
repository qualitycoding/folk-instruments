// JUCE wrapper around folk::Engine (plan/DECISIONS.md, D-094). Stub: createPluginFilter() throws until step S-310 replaces it.
#include <juce_audio_utils/juce_audio_utils.h>
#include "folk/engine.h"

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() {
    throw folk::NotImplemented("createPluginFilter");
}
