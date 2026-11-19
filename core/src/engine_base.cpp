#include "engine_base.h"
#include <algorithm>
#include <cmath>
#include <iomanip>
#include <locale>
#include <sstream>
#include "generated/presets_data.h"

namespace folk {

const char* instrumentName(Instrument i) {
    static const char* names[5] = {"harmonica", "accordion", "melodion", "mandolin", "bouzouki"};
    const int k = int(i);
    return k >= 0 && k < 5 ? names[k] : "";
}

bool instrumentFromName(std::string_view name, Instrument& out) {
    for (int i = 0; i < 5; ++i)
        if (name == instrumentName(Instrument(i))) { out = Instrument(i); return true; }
    return false;
}

EngineBase::EngineBase(Instrument ins) : ins_(ins) {
    const gen::ParamRow* rows = nullptr;
    int count = 0;
    switch (ins) {
        case Instrument::Harmonica: rows = gen::kParams0; count = gen::kParams0Count; break;
        case Instrument::Accordion: rows = gen::kParams1; count = gen::kParams1Count; break;
        case Instrument::Melodion: rows = gen::kParams2; count = gen::kParams2Count; break;
        case Instrument::Mandolin: rows = gen::kParams3; count = gen::kParams3Count; break;
        case Instrument::Bouzouki: rows = gen::kParams4; count = gen::kParams4Count; break;
    }
    for (int i = 0; i < count; ++i) {
        info_.push_back({rows[i].id, rows[i].name, rows[i].min, rows[i].max, rows[i].def, rows[i].steps});
        values_.push_back(rows[i].def);
    }
}

void EngineBase::prepare(double sampleRate, int maxBlockSize) {
    sampleRate_ = sampleRate;
    maxBlock_ = std::max(1, maxBlockSize);
    supported_ = std::isfinite(sampleRate) && sampleRate >= 44100.0 && sampleRate <= 96000.0;
    mono_.assign(size_t(maxBlock_), 0.0f);
    onPrepare();
    reset();
}

void EngineBase::reset() {
    queued_ = 0;
    onReset();
}

ParamInfo EngineBase::paramInfo(int index) const {
    if (index < 0 || index >= numParams()) return {"", "", 0, 0, 0, 0};
    return info_[size_t(index)];
}

int EngineBase::paramIndex(std::string_view id) const {
    for (int i = 0; i < numParams(); ++i)
        if (id == info_[size_t(i)].id) return i;
    return -1;
}

void EngineBase::setParam(int index, float value) {
    if (index < 0 || index >= numParams() || !std::isfinite(value)) return;
    const ParamInfo& p = info_[size_t(index)];
    value = std::min(std::max(value, p.min), p.max);
    if (p.steps > 0) value = std::round(value);
    values_[size_t(index)] = value;
    onParamChanged(index);
}

float EngineBase::getParam(int index) const {
    return index >= 0 && index < numParams() ? values_[size_t(index)] : 0.0f;
}

void EngineBase::push(const Event& e) noexcept {
    if (queued_ >= kMaxEvents) return;  // further events in the same block are dropped
    int pos = queued_++;
    while (pos > 0 && queue_[size_t(pos - 1)].offset > e.offset) {  // stable insertion by offset
        queue_[size_t(pos)] = queue_[size_t(pos - 1)];
        --pos;
    }
    queue_[size_t(pos)] = e;
}

void EngineBase::noteOn(int note, float vel, int off) {
    if (note < 0 || note > 127 || !std::isfinite(vel)) return;
    push({std::max(off, 0), EvType::NoteOn, note, std::min(std::max(vel, 0.0f), 1.0f)});
}
void EngineBase::noteOff(int note, int off) {
    if (note < 0 || note > 127) return;
    push({std::max(off, 0), EvType::NoteOff, note, 0.0f});
}
void EngineBase::controlChange(int cc, float v, int off) {
    if (cc < 0 || cc > 127 || !std::isfinite(v)) return;
    push({std::max(off, 0), EvType::Cc, cc, std::min(std::max(v, 0.0f), 1.0f)});
}
void EngineBase::pitchBend(float v, int off) {
    if (!std::isfinite(v)) return;
    push({std::max(off, 0), EvType::Bend, 0, std::min(std::max(v, -1.0f), 1.0f)});
}
void EngineBase::allNotesOff(int off) { push({std::max(off, 0), EvType::AllOff, 0, 0.0f}); }

void EngineBase::process(float* left, float* right, int n) noexcept {
    if (n <= 0) return;
    if (!supported_) {
        std::fill(left, left + n, 0.0f);
        std::fill(right, right + n, 0.0f);
        queued_ = 0;
        return;
    }
    int pos = 0, next = 0;
    while (pos < n) {
        // Dispatch events due at pos, then render up to the next event or the end of the block (or the scratch size).
        while (next < queued_ && std::min(queue_[size_t(next)].offset, n - 1) <= pos) onEvent(queue_[size_t(next++)]);
        int end = n;
        if (next < queued_) end = std::min(end, std::min(queue_[size_t(next)].offset, n - 1));
        end = std::min(end, pos + maxBlock_);
        if (end <= pos) end = std::min(n, pos + 1);
        std::fill(mono_.begin(), mono_.begin() + (end - pos), 0.0f);
        render(mono_.data(), end - pos);
        for (int i = pos; i < end; ++i) {
            const float y = std::tanh(mono_[size_t(i - pos)]);  // output limiter (D-015)
            left[i] = right[i] = std::isfinite(y) ? y : 0.0f;
        }
        pos = end;
    }
    queued_ = 0;
}

std::string EngineBase::saveState() const {
    std::ostringstream os;
    os.imbue(std::locale::classic());
    os << std::setprecision(9);
    os << "folk-state 1 " << instrumentName(ins_) << "\n";
    for (int i = 0; i < numParams(); ++i) os << info_[size_t(i)].id << "=" << values_[size_t(i)] << "\n";
    return os.str();
}

bool EngineBase::loadState(std::string_view text) {
    if (text.size() > 65536) return false;
    const std::string header = std::string("folk-state 1 ") + instrumentName(ins_) + "\n";
    if (text.substr(0, header.size()) != header) return false;
    std::vector<float> v = values_;
    std::vector<bool> seen(values_.size(), false);
    size_t pos = header.size();
    while (pos < text.size()) {
        const size_t nl = text.find('\n', pos);
        if (nl == std::string_view::npos) return false;  // incomplete line
        const std::string_view line = text.substr(pos, nl - pos);
        pos = nl + 1;
        const size_t eq = line.find('=');
        if (eq == std::string_view::npos) return false;
        const int idx = paramIndex(line.substr(0, eq));
        if (idx < 0 || seen[size_t(idx)]) return false;
        seen[size_t(idx)] = true;
        std::istringstream is{std::string(line.substr(eq + 1))};
        is.imbue(std::locale::classic());
        double d = 0;
        is >> d;
        if (is.fail() || !is.eof() || !std::isfinite(d) || line.size() == eq + 1) return false;
        const ParamInfo& p = info_[size_t(idx)];
        float f = float(std::min(std::max(d, double(p.min)), double(p.max)));
        if (p.steps > 0) f = std::round(f);
        v[size_t(idx)] = f;
    }
    values_ = v;
    for (int i = 0; i < numParams(); ++i) onParamChanged(i);
    return true;
}

namespace {
class SilentEngine final : public EngineBase {
public:
    using EngineBase::EngineBase;
};
}  // namespace

std::unique_ptr<Engine> makeHarmonica();

std::unique_ptr<Engine> Engine::create(Instrument i) {
    if (i == Instrument::Harmonica) return makeHarmonica();
    return std::make_unique<SilentEngine>(i);
}

}  // namespace folk
