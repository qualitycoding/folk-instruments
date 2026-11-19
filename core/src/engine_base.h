// Shared base of the five instruments: parameters, event queue, state text, output stage (plan/DECISIONS.md D-015, D-090 to D-093).
#pragma once
#include <array>
#include <string>
#include <vector>
#include "folk/engine.h"

namespace folk {

class EngineBase : public Engine {
public:
    explicit EngineBase(Instrument ins);

    Instrument instrument() const override { return ins_; }
    void prepare(double sampleRate, int maxBlockSize) override;
    void reset() override;

    int numParams() const override { return int(info_.size()); }
    ParamInfo paramInfo(int index) const override;
    int paramIndex(std::string_view id) const override;
    void setParam(int index, float value) override;
    float getParam(int index) const override;

    void noteOn(int midiNote, float velocity01, int sampleOffset) override;
    void noteOff(int midiNote, int sampleOffset) override;
    void controlChange(int cc, float value01, int sampleOffset) override;
    void pitchBend(float value, int sampleOffset) override;
    void allNotesOff(int sampleOffset) override;

    void process(float* left, float* right, int n) noexcept override;
    double tailSeconds() const override { return 1.0; }
    int latencySamples() const override { return 0; }

    std::string saveState() const override;
    bool loadState(std::string_view text) override;

protected:
    enum class EvType { NoteOn, NoteOff, Cc, Bend, AllOff };
    struct Event { int offset; EvType type; int a; float b; };
    static constexpr int kMaxEvents = 256;

    /// Hooks for the instruments. All are real-time safe except onPrepare.
    virtual void onPrepare() {}
    virtual void onReset() {}
    virtual void onEvent(const Event&) {}
    /// Adds n mono samples of the voice mix to out (before the output stage). Default: silence.
    virtual void render(float* out, int n) noexcept { (void)out; (void)n; }
    virtual void onParamChanged(int) {}

    float param(int i) const { return values_[size_t(i)]; }

    Instrument ins_;
    double sampleRate_ = 48000.0;
    int maxBlock_ = 512;
    bool supported_ = true;
    std::vector<ParamInfo> info_;
    std::vector<float> values_;
    std::vector<float> mono_;

private:
    void push(const Event& e) noexcept;
    std::array<Event, kMaxEvents> queue_{};
    int queued_ = 0;
};

}  // namespace folk
