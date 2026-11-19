// Pressure-driven free-reed model (plan/DECISIONS.md D-010 to D-016). Reference: research/spikes/s12-reed-similarity-scaling/similarity.py.
#pragma once
#include <memory>
#include <vector>

namespace folk {

/// Useful-section table in normalised units: Su(k = 1) against xi = x / x0, for given factors on x0 and hmin (D-012).
struct ReedTable {
    double xiLo = 0.0, xiHi = 0.0;   ///< range of xi covered by the table
    std::vector<double> su;          ///< 2048 values of Su * k
};
/// Builds the table. Takes a few milliseconds; never call it on the audio thread.
std::shared_ptr<const ReedTable> buildReedTable(double x0Factor = 1.0, double hminFactor = 1.0);

constexpr double kReedRefHz = 444.0;

/// One reed. step() advances one base-rate sample (m equal sub-steps).
class Reed {
public:
    /// Curve factors of D-012: factors on Q, x0 and hmin (1 = the reference reed scaled by similarity).
    struct Curves { double q = 1.0, x0 = 1.0, hmin = 1.0; };
    void configure(std::shared_ptr<const ReedTable> table, double naturalHz, double baseRateHz, const Curves& curves);
    /// Moves the natural frequency (pitch glide): changes the scaling k and the sub-step count, not the table.
    void setNaturalHz(double hz);
    void reset();                          ///< to rest: x = x0, the others 0
    /// Advances one base-rate sample with supply over-pressure p0 (Pa). Returns the flow u (m3/s) after the last sub-step.
    double step(double p0) noexcept;
    /// Test helper: displaces the tip by dx (m) from its current position.
    void kick(double dx) noexcept { x_ += dx; }
    double jetVelocity() const noexcept { return vj_; }
    double x() const noexcept { return x_; }
    double x0() const noexcept { return x0_; }
    bool finite() const noexcept;
    int subSteps() const noexcept { return m_; }

private:
    void derive();
    std::shared_ptr<const ReedTable> table_;
    Curves curves_;
    double baseRate_ = 192000.0, fr_ = kReedRefHz;
    // scaled parameters
    double x0_ = 0, w0_ = 0, q_ = 0, mu_ = 0, sr_ = 0, ain_ = 0, v1_ = 0, invK_ = 0;
    double invX0_ = 0, tabScale_ = 0, tabK_ = 0, kEff_ = 0;
    int m_ = 1;
    double dt_ = 0, cellGain_ = 0, passGain_ = 0, damp_ = 0, w02_ = 0, confine_ = 0;
    // state
    double x_ = 0, v_ = 0, p1_ = 0, u_ = 0, vj_ = 0;
};

}  // namespace folk
