// Harmonica (plan/DECISIONS.md D-020 to D-024): diatonic and chromatic note mapping, bend by wheel, wah, leak, valve buzz.
#include <cmath>
#include "folk/tuning.h"
#include "reed_engine.h"

namespace folk {
namespace {
constexpr double kPi = 3.14159265358979323846;

class Harmonica final : public ReedEngine {
public:
    Harmonica() : ReedEngine(Instrument::Harmonica) {
        variant_ = paramIndex("variant");
        key_ = paramIndex("key");
        wah_ = paramIndex("wah");
        air_ = paramIndex("airtightness");
        buzz_ = paramIndex("valve_buzz");
    }

protected:
    int maxVoices() const override { return 4; }

    bool mapNote(int note, Setup& s) override {
        HarpNote n;
        if (param(variant_) >= 0.5f) {
            n = chromaticNoteFor(note);
            if (n.kind == HarpNoteKind::None) return false;
            s.bendRoom = 1;
        } else {
            n = diatonicNoteFor(int(param(key_)), note);
            if (n.kind == HarpNoteKind::None) return false;
            if (n.kind == HarpNoteKind::Natural) s.bendRoom = diatonicMaxBend(n.hole, n.breath);
            else if (n.kind == HarpNoteKind::Bend) s.bendRoom = diatonicMaxBend(n.hole, n.breath) - n.bendSemitones;
            else s.bendRoom = 0;
        }
        s.nReeds = 1;
        s.midi[0] = note;
        s.gain[0] = 1.0;
        return true;
    }

    double wheelSemitones(const Voice& v, double wheel) const override {
        return wheel < 0 ? wheel * v.setup.bendRoom : 0.0;
    }

    double extraSourceGain(const Voice& v) const override {
        double g = 1.0 - (1.0 - param(air_)) * 0.5;   // leak past the reed
        if (param(variant_) >= 0.5f && param(buzz_) > 0 && v.sinceOn < 0.08)
            g *= 1.0 + 0.3 * param(buzz_) * std::sin(2.0 * kPi * 220.0 * v.sinceOn);
        return g;
    }
    double noiseScale(const Voice&) const override { return 1.0 + (1.0 - param(air_)) * 0.5; }

    void onReedReset() override { wahState_ = 0; }
    void onReset() override { ReedEngine::onReset(); wahState_ = 0; }

    void postProcess(float* out, int n) noexcept override {
        const double fc = 6000.0 * std::pow(900.0 / 6000.0, double(param(wah_)));
        const double a = 1.0 - std::exp(-2.0 * kPi * fc / sampleRate_);
        for (int i = 0; i < n; ++i) {
            wahState_ += a * (double(out[i]) - wahState_);
            out[i] = float(wahState_);
        }
    }

private:
    int variant_, key_, wah_, air_, buzz_;
    double wahState_ = 0;
};
}  // namespace

std::unique_ptr<Engine> makeHarmonica() { return std::make_unique<Harmonica>(); }

}  // namespace folk
