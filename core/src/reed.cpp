#include "reed.h"
#include <algorithm>
#include <cmath>

namespace folk {
namespace {
constexpr double kRho = 1.2, kC0 = 343.0, kAlpha = 0.61;
constexpr double kLr = 12.95e-3, kWr = 2.1e-3, kEr = 110e-6, kEs = 900e-6, kHmin = 50e-6, kX0 = 528e-6, kK = 47.9, kQ = 95.0;
constexpr double kS2 = 25e-6, kL2 = 20e-3, kV1 = 800e-6 * 0.06, kAin = 30e-6;
constexpr int kTable = 2048, kPsi = 201;
constexpr double kPi = 3.14159265358979323846;
}  // namespace

std::shared_ptr<const ReedTable> buildReedTable(double x0Factor, double hminFactor) {
    const double b = 1.875104;
    const double sig = (std::cosh(b) + std::cos(b)) / (std::sinh(b) + std::sin(b));
    std::vector<double> s(kPsi), psi(kPsi);
    for (int i = 0; i < kPsi; ++i) {
        s[size_t(i)] = double(i) / (kPsi - 1);
        const double z = b * s[size_t(i)];
        psi[size_t(i)] = (std::cosh(z) - std::cos(z)) - sig * (std::sinh(z) - std::sin(z));
    }
    const double end = psi.back();
    for (double& p : psi) p /= end;
    const double x0 = kX0 * x0Factor, hmin = kHmin * hminFactor, esr = kEs + kEr;
    auto t = std::make_shared<ReedTable>();
    t->xiLo = -6.0 - esr / x0;
    t->xiHi = 6.0;
    t->su.resize(kTable);
    const double xLo = t->xiLo * x0, xHi = t->xiHi * x0;
    std::vector<double> hh(kPsi);
    for (int i = 0; i < kTable; ++i) {
        const double x = xLo + (xHi - xLo) * double(i) / (kTable - 1);
        for (int j = 0; j < kPsi; ++j) {
            const double d = x * psi[size_t(j)];
            const double h = d > 0 ? d : (d < -esr ? -(d + esr) : 0.0);
            hh[size_t(j)] = std::hypot(h, hmin);
        }
        double integral = 0;
        for (int j = 0; j + 1 < kPsi; ++j) integral += 0.5 * (hh[size_t(j)] + hh[size_t(j + 1)]) * (s[size_t(j + 1)] - s[size_t(j)]);
        t->su[size_t(i)] = kWr * hh.back() + 2.0 * kLr * integral;
    }
    return t;
}

void Reed::configure(std::shared_ptr<const ReedTable> table, double naturalHz, double baseRateHz, const Curves& curves) {
    table_ = std::move(table);
    curves_ = curves;
    baseRate_ = baseRateHz;
    fr_ = naturalHz;
    derive();
    reset();
}

void Reed::setNaturalHz(double hz) {
    fr_ = hz;
    derive();
}

void Reed::derive() {
    // Similarity scaling (D-012): heights, Sr and A_in ~ 1/k, V1 ~ 1/k^2; K, Q, Lr, Wr, S2, L2 unchanged.
    const double k = fr_ / kReedRefHz;
    // Sr = Wr * Lr * integral(psi) with the same quadrature as the table.
    const double b = 1.875104, sig = (std::cosh(b) + std::cos(b)) / (std::sinh(b) + std::sin(b));
    static const double ipsi = [&] {
        double prev = 0, acc = 0;
        const double end = (std::cosh(b) - std::cos(b)) - sig * (std::sinh(b) - std::sin(b));
        for (int i = 0; i < kPsi; ++i) {
            const double z = b * double(i) / (kPsi - 1);
            const double p = ((std::cosh(z) - std::cos(z)) - sig * (std::sinh(z) - std::sin(z))) / end;
            if (i > 0) acc += 0.5 * (prev + p) / (kPsi - 1);
            prev = p;
        }
        return acc;
    }();
    x0_ = kX0 * curves_.x0 / k;
    invX0_ = 1.0 / x0_;
    sr_ = kWr * kLr * ipsi / k;
    ain_ = kAin / k;
    v1_ = kV1 / (k * k);
    w0_ = 2.0 * kPi * fr_;
    w02_ = w0_ * w0_;
    q_ = kQ * curves_.q;
    mu_ = sr_ * w02_ / kK;
    tabK_ = k;
    const double c = (curves_.x0 == 1.0 && curves_.q == 1.0 && curves_.hmin == 1.0) ? 110.0 : 160.0;  // D-011
    m_ = std::max(1, int(std::ceil(c * fr_ / baseRate_)));
    dt_ = 1.0 / (baseRate_ * m_);
    cellGain_ = kRho * kC0 * kC0 / v1_;
    passGain_ = kS2 / (kRho * kL2);
    damp_ = w0_ / q_;
    confine_ = 100.0 * w02_;  // confining spring of stiffness 100 K beyond 20 x0 (D-015)
}

void Reed::reset() {
    x_ = x0_;
    v_ = p1_ = u_ = vj_ = 0.0;
}

bool Reed::finite() const noexcept { return std::isfinite(x_) && std::isfinite(v_) && std::isfinite(p1_) && std::isfinite(u_); }

double Reed::step(double p0) noexcept {
    const double* su = table_->su.data();
    const double lo = table_->xiLo, hi = table_->xiHi;
    const double scale = (kTable - 1) / (hi - lo);
    const double top = double(kTable - 1);
    for (int n = 0; n < m_; ++n) {
        const double d = p0 - p1_;
        const double u0 = kAlpha * ain_ * (d >= 0 ? 1.0 : -1.0) * std::sqrt(2.0 * std::fabs(d) / kRho);
        double t = (x_ * invX0_ - lo) * scale;
        t = t < 0.0 ? 0.0 : (t >= top ? top - 1e-9 : t);
        const int j = int(t);
        const double Su = (su[j] + (su[j + 1] - su[j]) * (t - j)) / tabK_;
        vj_ = (u_ + sr_ * v_) / (kAlpha * Su);
        const double p2 = 0.5 * kRho * vj_ * std::fabs(vj_);
        p1_ += dt_ * cellGain_ * (u0 - u_);
        u_ += dt_ * passGain_ * (p1_ - p2);
        double acc = -damp_ * v_ - w02_ * (x_ - x0_) - mu_ * p2;
        const double dev = x_ - x0_, over = std::fabs(dev) - 20.0 * x0_;
        if (over > 0) acc -= confine_ * (dev > 0 ? over : -over);
        v_ += dt_ * acc;
        x_ += dt_ * v_;
    }
    if (std::fabs(v_) < 1e-20) v_ = 0;
    if (std::fabs(p1_) < 1e-20) p1_ = 0;
    if (std::fabs(u_) < 1e-20) u_ = 0;
    if (std::fabs(x_ - x0_) < 1e-20) x_ = x0_;
    return u_;
}

}  // namespace folk
