// Shared machinery of the three free-reed instruments (plan/DECISIONS.md D-010 to D-016): voices, breath, vibrato, noise, decimation.
#pragma once
#include <array>
#include <cstdint>
#include <memory>
#include <vector>
#include "engine_base.h"
#include "reed.h"

namespace folk {

/// 63-tap linear-phase half-band decimator by two (D-011); coefficients are generated into presets_data.h.
class HalfBandDecimator {
public:
    void reset();
    /// Pushes one input sample; returns true and sets out on every second call.
    bool push(double in, double& out) noexcept;
private:
    std::array<double, 64> buf_{};
    int pos_ = 0;
    bool phase_ = false;
};

class ReedEngine : public EngineBase {
public:
    explicit ReedEngine(Instrument ins);
    double tailSeconds() const override { return 2.6; }
    int latencySamples() const override { return 23; }

protected:
    static constexpr int kMaxReeds = 4;
    static constexpr int kControlTick = 64;
    struct Setup {
        int nReeds = 0;
        double midi[kMaxReeds] = {};       ///< target pitch of each reed as a (fractional) MIDI note, before bend and tuning
        double detuneCents[kMaxReeds] = {};
        double gain[kMaxReeds] = {};
        int bendRoom = 0;                   ///< whole semitones the wheel may bend this note down (harmonica)
    };
    struct Voice {
        bool active = false, held = false, fading = false;
        int note = 0;
        uint64_t age = 0;
        Setup setup;
        float velocity = 0;
        double breath = 0, breathTarget = 0;
        double msSource = 0, vjAvg = 0, releaseTimer = 0, sinceOn = 0;
        std::array<Reed, kMaxReeds> reeds;
        std::array<double, kMaxReeds> uPrev{};
        double fade = 1.0;
        // pending note when the voice is stolen (5 ms fade first)
        bool hasPending = false;
        int pendingNote = 0;
        float pendingVel = 0;
        Setup pendingSetup;
        // noise
        uint64_t rng = 1;
        double hp = 0, lp = 0, hpIn = 0;
    };

    /// Maps a MIDI note to reeds. Returns false if the instrument cannot play it.
    virtual bool mapNote(int note, Setup& out) = 0;
    virtual int maxVoices() const = 0;
    /// Semitones to add to a voice's pitch from the pitch wheel (smoothed value in -1..1).
    virtual double wheelSemitones(const Voice& v, double wheel) const { (void)v; (void)wheel; return 0.0; }
    virtual void postProcess(float* out, int n) noexcept { (void)out; (void)n; }
    virtual void onVoiceStart(Voice& v) { (void)v; }
    virtual double extraSourceGain(const Voice& v) const { (void)v; return 1.0; }
    virtual double noiseScale(const Voice& v) const { (void)v; return 1.0; }
    virtual void onReedReset() {}

    void onPrepare() override;
    void onReset() override;
    void onEvent(const Event& e) override;
    void render(float* out, int n) noexcept override;

    int reedInstrumentIndex() const { return int(ins_); }
    double baseRate() const { return 4.0 * sampleRate_; }
    double gainOut() const;
    float currentWheel() const { return float(wheelSmooth_); }

    std::vector<Voice> voices_;
    std::shared_ptr<const ReedTable> table_;
    uint64_t counter_ = 0;

private:
    void startVoice(Voice& v, int note, float vel, const Setup& s);
    void noteOnImpl(int note, float vel);
    void noteOffImpl(int note);
    double offsetCents(double midi) const;
    void retune(Voice& v);
    void seedVoice(Voice& v, int index);

    HalfBandDecimator dec1_, dec2_;
    double wheel_ = 0, wheelSmooth_ = 0, wheelCoeff_ = 0;
    double breathCtl_ = 0.5, modWheel_ = 0, vibPhase_ = 0;
    bool ctlSeen_ = false;
    int tick_ = 0;
    int rateIndex_ = 1;
    double noiseNorm_ = 1.0, breathCoeff_ = 0, vjCoeff_ = 0, msCoeff_ = 0, hpCoeff_ = 0, lpCoeff_ = 0;
    double gaussSpare_ = 0;
    bool hasSpare_ = false;
    uint64_t sampleCount_ = 0;
};

}  // namespace folk
