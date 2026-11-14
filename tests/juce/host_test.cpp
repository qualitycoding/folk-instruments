// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// T-302 the JUCE wrapper of each plugin, driven headlessly (SC-01, SC-11; D-094; threat model: state blobs from a host).
// One executable per plugin; FOLK_INSTRUMENT is defined by the plugin target.
#include <catch2/catch_session.hpp>
#include <catch2/catch_test_macros.hpp>
#include <juce_audio_utils/juce_audio_utils.h>
#include <cmath>
#include <memory>
#include "folk/engine.h"

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter();

namespace {
std::unique_ptr<juce::AudioProcessor> make() { return std::unique_ptr<juce::AudioProcessor>(createPluginFilter()); }
int safeNote() { return FOLK_INSTRUMENT == folk::Instrument::Harmonica ? 72 : 69; }
double renderRms(juce::AudioProcessor& p, int blocks, bool noteOn) {
    juce::AudioBuffer<float> buf(2, 512); double s = 0; long n = 0;
    for (int b = 0; b < blocks; ++b) {
        juce::MidiBuffer midi; buf.clear();
        if (b == 0 && noteOn) midi.addEvent(juce::MidiMessage::noteOn(1, safeNote(), 0.8f), 17);
        p.processBlock(buf, midi);
        for (int i = 0; i < 512; ++i) { const float v = buf.getSample(0, i); REQUIRE(std::isfinite(v)); s += double(v) * v; ++n; }
    }
    return 10.0 * std::log10(s / double(n) + 1e-30);
}
}  // namespace

TEST_CASE("T-302 the wrapper exposes the core's parameters and a stereo output", "[juce]") {
    auto p = make(); REQUIRE(p != nullptr);
    auto core = folk::Engine::create(FOLK_INSTRUMENT);
    const auto& params = p->getParameters();
    REQUIRE(params.size() == core->numParams());
    for (int i = 0; i < params.size(); ++i) {
        auto* withId = dynamic_cast<juce::AudioProcessorParameterWithID*>(params[i]);
        REQUIRE(withId != nullptr);
        CHECK(withId->paramID == juce::String(core->paramInfo(i).id));
    }
    CHECK(p->getTotalNumInputChannels() == 0);
    CHECK(p->getTotalNumOutputChannels() == 2);
    CHECK(p->acceptsMidi());
    CHECK_FALSE(p->producesMidi());
    CHECK(p->getName().startsWith("Folk "));
}

TEST_CASE("T-302 a MIDI note produces sound and silence follows no note", "[juce]") {
    auto p = make(); p->setPlayConfigDetails(0, 2, 48000.0, 512); p->prepareToPlay(48000.0, 512);
    CHECK(renderRms(*p, 20, false) < -90.0);
    CHECK(renderRms(*p, 40, true) > -50.0);
    p->releaseResources();
}

TEST_CASE("T-302 state round trip and malformed state", "[juce][security]") {
    auto a = make(); a->setPlayConfigDetails(0, 2, 48000.0, 512); a->prepareToPlay(48000.0, 512);
    const auto& pa = a->getParameters();
    for (int i = 0; i < pa.size(); ++i) pa[i]->setValueNotifyingHost(0.37f);
    juce::MemoryBlock state; a->getStateInformation(state);
    REQUIRE(state.getSize() > 0);
    auto b = make(); b->setPlayConfigDetails(0, 2, 48000.0, 512); b->prepareToPlay(48000.0, 512);
    b->setStateInformation(state.getData(), static_cast<int>(state.getSize()));
    const auto& pb = b->getParameters();
    for (int i = 0; i < pa.size(); ++i) CHECK(std::fabs(pb[i]->getValue() - pa[i]->getValue()) < 1e-6f);

    // Malformed blobs: nothing may throw, crash or change the parameters.
    juce::Array<float> before; for (auto* q : pb) before.add(q->getValue());
    const char garbage[] = "\x00\xff<VC2!>\x01 not a state \x7f";
    CHECK_NOTHROW(b->setStateInformation(garbage, static_cast<int>(sizeof(garbage))));
    CHECK_NOTHROW(b->setStateInformation(nullptr, 0));
    juce::MemoryBlock big(200000, true); std::memset(big.getData(), 'x', big.getSize());
    CHECK_NOTHROW(b->setStateInformation(big.getData(), static_cast<int>(big.getSize())));
    juce::MemoryBlock truncated(state.getData(), state.getSize() / 2);
    CHECK_NOTHROW(b->setStateInformation(truncated.getData(), static_cast<int>(truncated.getSize())));
    for (int i = 0; i < pb.size(); ++i) CHECK(pb[i]->getValue() == before[i]);
}

TEST_CASE("T-302 an editor can be created and destroyed", "[juce]") {
    auto p = make();
    REQUIRE(p->hasEditor());
    std::unique_ptr<juce::AudioProcessorEditor> ed(p->createEditorAndMakeActive());   // createEditor() is private in JUCE 8.0.17
    REQUIRE(ed != nullptr);
    CHECK(ed->getWidth() > 0);
    CHECK(ed->getHeight() > 0);
}

int main(int argc, char* argv[]) {
    juce::ScopedJuceInitialiser_GUI gui;   // message manager for parameter and editor code (knowledge K-20261007T160027Z-c-028)
    return Catch::Session().run(argc, argv);
}
