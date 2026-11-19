#include "reed_engine.h"
#include <algorithm>
#include <cmath>
#include <mutex>
#include "folk/tuning.h"
#include "generated/presets_data.h"

namespace folk {
namespace {
constexpr double kPi = 3.14159265358979323846;

std::shared_ptr<const ReedTable> sharedTable() {
    static std::mutex m;
    static std::shared_ptr<const ReedTable> t;
    std::lock_guard<std::mutex> lock(m);
    if (!t) t = buildReedTable();
    return t;
}

const double* offsetTable(int ins, int rateIdx) {
    switch (ins) {
        case 0: return gen::kReedOffsets0[rateIdx];
        case 1: return gen::kReedOffsets1[rateIdx];
        default: return gen::kReedOffsets2[rateIdx];
    }
}

inline double uniform(uint64_t& s) noexcept {
    s ^= s >> 12; s ^= s << 25; s ^= s >> 27;
    return double((s * 2685821657736338717ULL) >> 11) * (1.0 / 9007199254740992.0);
}
// Sum of four uniforms: close to Gaussian, unit variance after scaling, cheap enough for the base rate.
inline double gauss(uint64_t& s) noexcept {
    return (uniform(s) + uniform(s) + uniform(s) + uniform(s) - 2.0) * 1.7320508075688772;
}
}  // namespace

void HalfBandDecimator::reset() {
    buf_.fill(0.0);
    pos_ = 0;
    phase_ = false;
}

bool HalfBandDecimator::push(double in, double& out) noexcept {
    pos_ = (pos_ + 1) & 63;
    buf_[size_t(pos_)] = in;
    phase_ = !phase_;
    if (phase_) return false;
    double acc = 0;
    for (int k = 0; k < 63; ++k) acc += gen::kHalfBand63[k] * buf_[size_t((pos_ - k) & 63)];
    out = acc;
    return true;
}

ReedEngine::ReedEngine(Instrument ins) : EngineBase(ins) {}

double ReedEngine::gainOut() const { return gen::kGainOut[int(ins_)]; }

void ReedEngine::onPrepare() {
    voices_.assign(size_t(maxVoices()), Voice{});
    table_ = sharedTable();
    int best = 0;
    for (int i = 0; i < 4; ++i)
        if (std::fabs(gen::kReedRates[i] - sampleRate_) < std::fabs(gen::kReedRates[best] - sampleRate_)) best = i;
    rateIndex_ = best;
    const double R = baseRate();
    breathCoeff_ = 1.0 - std::exp(-1.0 / (0.015 * sampleRate_));
    wheelCoeff_ = 1.0 - std::exp(-1.0 / (0.030 * sampleRate_));
    vjCoeff_ = 1.0 - std::exp(-1.0 / (0.001 * R));
    msCoeff_ = 1.0 - std::exp(-1.0 / (0.010 * R));
    hpCoeff_ = std::exp(-2.0 * kPi * 300.0 / R);
    lpCoeff_ = 1.0 - std::exp(-2.0 * kPi * 8000.0 / R);
    // Normalise the 300 Hz to 8 kHz noise to unit RMS (measured once, here).
    uint64_t s = 88172645463325252ULL;
    double hp = 0, hpIn = 0, lp = 0, acc = 0;
    const int N = 200000;
    for (int i = 0; i < N; ++i) {
        const double x = gauss(s);
        hp = hpCoeff_ * (hp + x - hpIn);
        hpIn = x;
        lp += lpCoeff_ * (hp - lp);
        if (i > 1000) acc += lp * lp;
    }
    noiseNorm_ = 1.0 / std::sqrt(acc / (N - 1000));
}

void ReedEngine::seedVoice(Voice& v, int index) {
    v.rng = 0x9E3779B97F4A7C15ULL * uint64_t(index + 1) + 12345;
    v.hp = v.lp = v.hpIn = 0;
}

void ReedEngine::onReset() {
    for (size_t i = 0; i < voices_.size(); ++i) {
        Voice& v = voices_[i];
        v = Voice{};
        seedVoice(v, int(i));
    }
    dec1_.reset();
    dec2_.reset();
    wheel_ = wheelSmooth_ = 0;
    breathCtl_ = 0.5;
    modWheel_ = 0;
    vibPhase_ = 0;
    ctlSeen_ = false;
    tick_ = 0;
    counter_ = 0;
    sampleCount_ = 0;
}

double ReedEngine::offsetCents(double midi) const {
    const double* t = offsetTable(int(ins_), rateIndex_);
    const double x = std::min(std::max(midi, 28.0), 112.0) - 28.0;
    const int i = std::min(int(x), 83);
    const double f = x - i;
    return t[i] + (t[i + 1] - t[i]) * f;
}

void ReedEngine::retune(Voice& v) {
    const double wheel = wheelSemitones(v, wheelSmooth_);
    const double a4 = param(1);
    for (int r = 0; r < v.setup.nReeds; ++r) {
        const double m = v.setup.midi[r] + v.setup.detuneCents[r] / 100.0 + wheel;
        const double target = midiToHz(m, a4);
        const double natural = target * std::pow(2.0, -offsetCents(m) / 1200.0);
        v.reeds[size_t(r)].setNaturalHz(natural);
    }
}

void ReedEngine::startVoice(Voice& v, int note, float vel, const Setup& s) {
    seedVoice(v, int(&v - voices_.data()));
    v.active = true;
    v.held = true;
    v.fading = false;
    v.fade = 1.0;
    v.hasPending = false;
    v.note = note;
    v.velocity = vel;
    v.setup = s;
    v.age = ++counter_;
    v.breath = 0;
    v.breathTarget = 0;
    v.msSource = v.vjAvg = v.releaseTimer = v.sinceOn = 0;
    const double a4 = param(1);
    const double wheel = wheelSemitones(v, wheelSmooth_);
    for (int r = 0; r < s.nReeds; ++r) {
        const double m = s.midi[r] + s.detuneCents[r] / 100.0 + wheel;
        const double natural = midiToHz(m, a4) * std::pow(2.0, -offsetCents(m) / 1200.0);
        v.reeds[size_t(r)].configure(table_, natural, baseRate(), {});
        v.uPrev[size_t(r)] = 0;
    }
    onVoiceStart(v);
}

void ReedEngine::noteOnImpl(int note, float vel) {
    Setup s;
    if (!mapNote(note, s) || s.nReeds <= 0) return;
    for (Voice& v : voices_)
        if (v.active && !v.fading && v.note == note) {   // still sounding: raise the breath, no reset
            v.held = true;
            v.velocity = vel;
            v.releaseTimer = 0;
            return;
        }
    for (Voice& v : voices_)
        if (!v.active) { startVoice(v, note, vel, s); return; }
    Voice* oldest = nullptr;
    for (Voice& v : voices_)
        if (!v.fading && (!oldest || v.age < oldest->age)) oldest = &v;
    if (!oldest) oldest = &voices_[0];
    oldest->fading = true;
    oldest->hasPending = true;
    oldest->pendingNote = note;
    oldest->pendingVel = vel;
    oldest->pendingSetup = s;
}

void ReedEngine::noteOffImpl(int note) {
    for (Voice& v : voices_)
        if (v.active && v.held && v.note == note) v.held = false;
}

void ReedEngine::onEvent(const Event& e) {
    switch (e.type) {
        case EvType::NoteOn: noteOnImpl(e.a, e.b); break;
        case EvType::NoteOff: noteOffImpl(e.a); break;
        case EvType::Cc:
            if (e.a == 1) modWheel_ = e.b;
            else if (e.a == 2 && param(3) == 1.0f) { breathCtl_ = e.b; ctlSeen_ = true; }
            else if (e.a == 11 && param(3) == 2.0f) { breathCtl_ = e.b; ctlSeen_ = true; }
            else if (e.a == 120 || e.a == 123) for (Voice& v : voices_) v.held = false;
            break;
        case EvType::Bend: wheel_ = e.b; break;
        case EvType::AllOff: for (Voice& v : voices_) v.held = false; break;
    }
}

void ReedEngine::render(float* out, int n) noexcept {
    const double R = baseRate();
    const double fs = sampleRate_;
    const float level = param(0) / 0.7f;
    const double gain = gainOut() * level;
    const int breathSrc = int(param(3));
    const double ctl = ctlSeen_ ? breathCtl_ : double(param(2));
    const double sRef = gen::kSourceRmsRef;
    const double airNoise = param(6);
    for (int i = 0; i < n; ++i) {
        wheelSmooth_ += wheelCoeff_ * (wheel_ - wheelSmooth_);
        if (tick_ == 0)
            for (Voice& v : voices_)
                if (v.active) retune(v);
        tick_ = (tick_ + 1) % kControlTick;
        const double depth = std::min(std::max(double(param(5)) + modWheel_, 0.0), 1.0);
        vibPhase_ += 2.0 * kPi * param(4) / fs;
        if (vibPhase_ > 2.0 * kPi) vibPhase_ -= 2.0 * kPi;
        const double vibMul = 1.0 + 0.2 * depth * std::sin(vibPhase_);
        double bus[4] = {0, 0, 0, 0};
        for (Voice& v : voices_) {
            if (!v.active) continue;
            if (v.fading) {
                v.fade -= 1.0 / (0.005 * fs);
                if (v.fade <= 0) {
                    if (v.hasPending) { const int nn = v.pendingNote; const float vv = v.pendingVel; const Setup ss = v.pendingSetup; startVoice(v, nn, vv, ss); }
                    else v.active = false;
                    continue;
                }
            }
            double target = 0;
            if (v.held) target = breathSrc == 0 ? double(v.velocity) : ctl;
            v.breath += breathCoeff_ * (target - v.breath);
            const double p0 = 1250.0 * std::pow(std::max(v.breath, 0.0), 1.5) * vibMul;
            v.sinceOn += 1.0 / fs;
            const double extra = extraSourceGain(v) * (v.fading ? v.fade : 1.0);
            const double noiseRms = 0.03 * airNoise * std::pow(v.vjAvg / 31.0, 3.0) * sRef * noiseScale(v);
            for (int b = 0; b < 4; ++b) {
                double src = 0;
                for (int r = 0; r < v.setup.nReeds; ++r) {
                    Reed& reed = v.reeds[size_t(r)];
                    const double u = reed.step(p0);
                    src += v.setup.gain[r] * (u - v.uPrev[size_t(r)]) * R;
                    v.uPrev[size_t(r)] = u;
                }
                v.vjAvg += vjCoeff_ * (std::fabs(v.reeds[0].jetVelocity()) - v.vjAvg);
                if (noiseRms > 0) {
                    const double x = gauss(v.rng);
                    v.hp = hpCoeff_ * (v.hp + x - v.hpIn);
                    v.hpIn = x;
                    v.lp += lpCoeff_ * (v.hp - v.lp);
                    src += v.lp * noiseNorm_ * noiseRms;
                }
                v.msSource += msCoeff_ * (src * src - v.msSource);
                bus[b] += src * extra;
            }
            bool ok = true;
            for (int r = 0; r < v.setup.nReeds; ++r) ok = ok && v.reeds[size_t(r)].finite();
            if (!ok || !std::isfinite(v.msSource)) { v.active = false; continue; }
            if (!v.held) {
                v.releaseTimer += 1.0 / fs;
                if (v.releaseTimer > 2.0 || std::sqrt(v.msSource) < sRef * 1e-5) {
                    if (!v.fading) v.active = false;
                }
            }
        }
        double y1, y2 = 0;
        for (int b = 0; b < 4; ++b)
            if (dec1_.push(bus[b], y1)) dec2_.push(y1, y2);
        out[i] = float(y2 * gain);
    }
    postProcess(out, n);
}

}  // namespace folk
