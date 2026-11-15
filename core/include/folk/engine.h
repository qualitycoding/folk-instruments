// Public interface of the folk-instruments DSP core (plan/DECISIONS.md, D-090). No JUCE types appear here.
#pragma once
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>

namespace folk {

/// Thrown by every stub until the implementing step replaces it.
struct NotImplemented : std::logic_error {
    explicit NotImplemented(const char* what) : std::logic_error(std::string("not implemented: ") + what) {}
};

enum class Instrument { Harmonica = 0, Accordion = 1, Melodion = 2, Mandolin = 3, Bouzouki = 4 };

/// Lower-case name used by the render tool and the preset files: "harmonica", "accordion", "melodion", "mandolin", "bouzouki".
const char* instrumentName(Instrument);
/// Returns false if the name is not one of the five.
bool instrumentFromName(std::string_view name, Instrument& out);

struct ParamInfo {
    const char* id;    ///< stable identifier, e.g. "pick_position" (the table is in plan/DECISIONS.md, D-091)
    const char* name;  ///< label shown to the user
    float min, max, def;
    int steps;         ///< 0 for a continuous parameter, otherwise the number of discrete values (min..max inclusive)
};

/// One instrument. All methods except create(), prepare(), saveState() and loadState() are real-time safe:
/// they do not allocate, lock or perform I/O.
class Engine {
public:
    static std::unique_ptr<Engine> create(Instrument);
    virtual ~Engine() = default;

    virtual Instrument instrument() const = 0;
    virtual void prepare(double sampleRate, int maxBlockSize) = 0;   ///< 44100 <= sampleRate <= 96000
    virtual void reset() = 0;                                        ///< silence, default controller state, reseeded noise

    virtual int numParams() const = 0;
    virtual ParamInfo paramInfo(int index) const = 0;
    virtual int paramIndex(std::string_view id) const = 0;           ///< -1 if unknown
    virtual void setParam(int index, float value) = 0;               ///< clamped to [min, max]; discrete values rounded
    virtual float getParam(int index) const = 0;

    // Events take effect at sampleOffset samples into the next process() call (0 <= sampleOffset < n of that call).
    // Events with the same offset are applied in the order received.
    virtual void noteOn(int midiNote, float velocity01, int sampleOffset) = 0;
    virtual void noteOff(int midiNote, int sampleOffset) = 0;
    virtual void controlChange(int cc, float value01, int sampleOffset) = 0;
    virtual void pitchBend(float valueMinus1To1, int sampleOffset) = 0;
    virtual void allNotesOff(int sampleOffset) = 0;

    /// Writes n samples to each channel (it overwrites; it does not add). |sample| <= 1 always.
    virtual void process(float* left, float* right, int n) noexcept = 0;
    virtual double tailSeconds() const = 0;
    /// Processing latency in host samples (23 for the reed instruments, 0 for the plucked ones; plan/DECISIONS.md D-011).
    virtual int latencySamples() const = 0;

    /// Text form of all parameter values: lines "id=value\n", first line "folk-state 1 <instrument name>".
    virtual std::string saveState() const = 0;
    /// Returns false and changes nothing if the text is malformed, is for another instrument, or is longer than 65536 bytes.
    virtual bool loadState(std::string_view text) = 0;
};

}  // namespace folk
