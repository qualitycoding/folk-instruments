// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// T-302 the JUCE wrapper of each plugin, driven headlessly (SC-01, SC-11; D-094; threat model: state blobs from a host).
// T-303 the wrapper plays exactly what the core plays for the same MIDI and parameter values (D-093, D-094; R-017 to R-021).
// T-304 host-style concurrency: state and parameter calls on one thread while another processes audio (D-094).
// One executable per plugin; FOLK_INSTRUMENT is defined by the plugin target.
#include <catch2/catch_session.hpp>
#include <catch2/catch_test_macros.hpp>
#include <juce_audio_utils/juce_audio_utils.h>
#include <atomic>
#include <chrono>
#include <clocale>
#include <cmath>
#include <cstring>
#include <exception>
#include <locale>
#include <memory>
#include <string>
#include <random>
#include <sstream>
#include <thread>
#include <vector>
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

namespace {
juce::RangedAudioParameter* paramById(juce::AudioProcessor& p, const char* id) {
    for (auto* q : p.getParameters())
        if (auto* r = dynamic_cast<juce::RangedAudioParameter*>(q); r != nullptr && r->paramID == id) return r;
    return nullptr;
}
// Switches both the C locale and the C++ global locale (default-constructed streams follow the latter; audit TP-LOC-2).
bool setCommaLocale() {
    for (const char* name : {"de_DE.UTF-8", "de_DE.utf8", "de_DE", "German_Germany.1252", "German", "de-DE"}) {
        if (std::setlocale(LC_ALL, name) == nullptr || std::strcmp(std::localeconv()->decimal_point, ",") != 0) continue;
        try {
            std::locale cpp(name);
            if (std::use_facet<std::numpunct<char>>(cpp).decimal_point() != ',') continue;
            std::locale::global(cpp);
        } catch (const std::exception&) { continue; }
        std::ostringstream probe; probe << 0.5;
        if (probe.str() == "0,5") return true;
    }
    std::setlocale(LC_ALL, "C");
    std::locale::global(std::locale::classic());
    return false;
}
void restoreClassicLocale() { std::setlocale(LC_ALL, "C"); std::locale::global(std::locale::classic()); }
}  // namespace

TEST_CASE("T-302 state round trip under a decimal-comma locale", "[juce][security][locale]") {
    struct Restore { ~Restore() { restoreClassicLocale(); } } restore;   // also on a failed REQUIRE, so later cases run in "C"
    REQUIRE(setCommaLocale());
    auto a = make(); a->setPlayConfigDetails(0, 2, 48000.0, 512); a->prepareToPlay(48000.0, 512);
    const auto& pa = a->getParameters();
    for (int i = 0; i < pa.size(); ++i) pa[i]->setValueNotifyingHost(0.37f);
    juce::MemoryBlock state; a->getStateInformation(state);
    auto b = make(); b->setPlayConfigDetails(0, 2, 48000.0, 512); b->prepareToPlay(48000.0, 512);
    b->setStateInformation(state.getData(), static_cast<int>(state.getSize()));
    const auto& pb = b->getParameters();
    for (int i = 0; i < pa.size(); ++i) CHECK(std::fabs(pb[i]->getValue() - pa[i]->getValue()) < 1e-6f);
}

TEST_CASE("T-302 the current program survives a restore and re-selecting it changes nothing", "[juce]") {
    auto a = make(); a->setPlayConfigDetails(0, 2, 48000.0, 512); a->prepareToPlay(48000.0, 512);
    REQUIRE(a->getNumPrograms() >= 2);
    const int prog = a->getNumPrograms() - 1;          // a non-default program, so a lost index is visible
    a->setCurrentProgram(prog);
    REQUIRE(a->getCurrentProgram() == prog);
    const auto& pa = a->getParameters();
    for (int i = 0; i < pa.size(); ++i) pa[i]->setValueNotifyingHost(0.37f);   // the user edits after choosing a preset
    juce::MemoryBlock state; a->getStateInformation(state);
    auto b = make(); b->setPlayConfigDetails(0, 2, 48000.0, 512); b->prepareToPlay(48000.0, 512);
    b->setStateInformation(state.getData(), static_cast<int>(state.getSize()));
    CHECK(b->getCurrentProgram() == prog);
    b->setCurrentProgram(b->getCurrentProgram());      // some hosts do this after restoring a session
    const auto& pb = b->getParameters();
    for (int i = 0; i < pa.size(); ++i) CHECK(std::fabs(pb[i]->getValue() - pa[i]->getValue()) < 1e-6f);

    // D-094: the state is the engine's text followed by a last line '#program <index>'.
    const std::string text(static_cast<const char*>(state.getData()), state.getSize());
    const auto cut = text.rfind("#program ");
    REQUIRE(cut != std::string::npos);
    for (const std::string& variant : {text.substr(0, cut), text.substr(0, cut) + "#program 9999\n", text.substr(0, cut) + "#program x\n"}) {
        auto c = make(); c->setPlayConfigDetails(0, 2, 48000.0, 512); c->prepareToPlay(48000.0, 512);
        c->setStateInformation(variant.data(), static_cast<int>(variant.size()));
        CHECK(c->getCurrentProgram() == 0);            // missing or bad index: program 0, parameters still restored
        const auto& pc = c->getParameters();
        for (int i = 0; i < pa.size(); ++i) CHECK(std::fabs(pc[i]->getValue() - pa[i]->getValue()) < 1e-6f);
    }
}

TEST_CASE("T-302 sample rates outside 44.1 to 96 kHz neither throw nor produce invalid output", "[juce][robustness]") {
    for (double sr : {22050.0, 32000.0, 176400.0, 192000.0}) {
        INFO("sample rate " << sr);
        auto p = make(); p->setPlayConfigDetails(0, 2, sr, 512);
        CHECK_NOTHROW(p->prepareToPlay(sr, 512));
        juce::AudioBuffer<float> buf(2, 512);
        for (int b = 0; b < 40; ++b) {
            juce::MidiBuffer midi; buf.clear();
            if (b == 0) midi.addEvent(juce::MidiMessage::noteOn(1, safeNote(), 0.8f), 3);
            CHECK_NOTHROW(p->processBlock(buf, midi));
            for (int c = 0; c < 2; ++c) for (int i = 0; i < 512; ++i) { const float v = buf.getSample(c, i); REQUIRE(std::isfinite(v)); REQUIRE(std::fabs(v) <= 1.0f); }
        }
        p->releaseResources();
        p->setPlayConfigDetails(0, 2, 48000.0, 512); p->prepareToPlay(48000.0, 512);
        CHECK(renderRms(*p, 40, true) > -50.0);   // a supported rate plays again after an unsupported one
    }
}

TEST_CASE("T-303 the wrapper's output equals the core's for the same MIDI and parameter values", "[juce][integration]") {
    const int note = safeNote();
    auto p = make(); p->setPlayConfigDetails(0, 2, 48000.0, 512); p->prepareToPlay(48000.0, 512);
    auto e = folk::Engine::create(FOLK_INSTRUMENT); e->prepare(48000.0, 512);
    // A parameter set through the host in engine units (a4_hz = 435 Hz) must reach the engine as 435, not as a normalised value.
    auto* a4 = paramById(*p, "a4_hz"); REQUIRE(a4 != nullptr);
    a4->setValueNotifyingHost(a4->convertTo0to1(435.0f));
    e->setParam(e->paramIndex("a4_hz"), 435.0f);
    CHECK(std::fabs(a4->convertFrom0to1(a4->getValue()) - 435.0f) < 0.01f);
    // MIDI mapping of D-093: velocity v/127, controller value v/127, pitch wheel (v - 8192)/8192.
    struct M { int block, offset; juce::MidiMessage msg; };
    const std::vector<M> script = {
        {0, 17, juce::MidiMessage::noteOn(1, note, static_cast<juce::uint8>(102))},
        {4, 100, juce::MidiMessage::pitchWheel(1, 4096)},
        {6, 300, juce::MidiMessage::controllerEvent(1, 1, 100)},
        {8, 5, juce::MidiMessage::controllerEvent(1, 2, 64)},
        {9, 700, juce::MidiMessage::controllerEvent(1, 64, 127)},   // offset 700 lies in the second half of an oversized block
        {12, 40, juce::MidiMessage::noteOff(1, note)},
        {14, 0, juce::MidiMessage::pitchWheel(1, 8192)},
        {16, 250, juce::MidiMessage::controllerEvent(1, 64, 0)},
        {20, 10, juce::MidiMessage::controllerEvent(1, 123, 0)},
    };
    double worst = 0, energy = 0;
    std::vector<float> l(1024), r(1024);
    for (int block = 0; block < 30; ++block) {
        const int n = block == 9 ? 1024 : 512;   // one block larger than the prepared size: the wrapper must split it
        juce::AudioBuffer<float> buf(2, n); buf.clear();
        juce::MidiBuffer midi;
        for (const auto& m : script) if (m.block == block) midi.addEvent(m.msg, m.offset);
        p->processBlock(buf, midi);
        for (int start = 0; start < n; start += 512) {
            const int len = std::min(512, n - start);
            for (const auto& m : script) {
                if (m.block != block || m.offset < start || m.offset >= start + len) continue;
                const int off = m.offset - start;
                if (m.msg.isNoteOn()) e->noteOn(m.msg.getNoteNumber(), m.msg.getVelocity() / 127.0f, off);
                else if (m.msg.isNoteOff()) e->noteOff(m.msg.getNoteNumber(), off);
                else if (m.msg.isPitchWheel()) e->pitchBend((m.msg.getPitchWheelValue() - 8192) / 8192.0f, off);
                else if (m.msg.isController()) {
                    if (m.msg.getControllerNumber() == 123) e->allNotesOff(off);
                    else e->controlChange(m.msg.getControllerNumber(), m.msg.getControllerValue() / 127.0f, off);
                }
            }
            e->process(l.data(), r.data(), len);
            for (int i = 0; i < len; ++i) {
                worst = std::max(worst, double(std::fabs(buf.getSample(0, start + i) - l[i])));
                worst = std::max(worst, double(std::fabs(buf.getSample(1, start + i) - r[i])));
                energy += double(l[i]) * l[i];
            }
        }
    }
    CHECK(energy > 1e-3);       // the comparison is not between two silences
    CHECK(worst <= 1e-4);
}

TEST_CASE("T-304 state and parameter calls from another thread while audio is processed", "[juce][realtime][concurrency]") {
    auto p = make(); p->setPlayConfigDetails(0, 2, 48000.0, 256); p->prepareToPlay(48000.0, 256);
    juce::MemoryBlock saved; p->getStateInformation(saved);
    std::atomic<bool> stop{false}, bad{false};
    std::atomic<long> blocks{0}, calls{0};
    std::thread audio([&] {
        juce::AudioBuffer<float> buf(2, 256);
        for (long b = 0; !stop.load(); ++b) {
            juce::MidiBuffer midi; buf.clear();
            if (b % 50 == 0) midi.addEvent(juce::MidiMessage::noteOn(1, safeNote() + int(b / 50 % 5), 0.7f), 11);
            if (b % 50 == 30) midi.addEvent(juce::MidiMessage::noteOff(1, safeNote() + int(b / 50 % 5)), 7);
            p->processBlock(buf, midi);
            for (int c = 0; c < 2; ++c) for (int i = 0; i < 256; ++i) if (!std::isfinite(buf.getSample(c, i)) || std::fabs(buf.getSample(c, i)) > 1.0f) bad = true;
            ++blocks;
        }
    });
    std::mt19937 rng(7);
    std::uniform_real_distribution<float> u(0.0f, 1.0f);
    const auto& params = p->getParameters();
    const auto until = std::chrono::steady_clock::now() + std::chrono::seconds(5);
    while (std::chrono::steady_clock::now() < until) {
        juce::MemoryBlock s; p->getStateInformation(s);
        p->setStateInformation(saved.getData(), static_cast<int>(saved.getSize()));
        p->setStateInformation(s.getData(), static_cast<int>(s.getSize()));
        params[static_cast<int>(rng() % static_cast<unsigned>(params.size()))]->setValueNotifyingHost(u(rng));
        ++calls;
    }
    stop = true; audio.join();
    CHECK_FALSE(bad.load());
    CHECK(blocks.load() > 100);
    CHECK(calls.load() > 100);
}

int main(int argc, char* argv[]) {
    juce::ScopedJuceInitialiser_GUI gui;   // message manager for parameter and editor code (knowledge K-20261007T160027Z-c-028)
    return Catch::Session().run(argc, argv);
}
