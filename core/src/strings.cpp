// String physics (plan/DECISIONS.md D-060 to D-062).
#include "folk/strings.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace folk {
namespace {
constexpr double kPi = 3.14159265358979323846;
void need(bool ok, const char* what) {
    if (!ok) throw std::invalid_argument(what);
}
}  // namespace

double inharmonicityB(double E, double d, double T, double L) {
    need(E > 0 && d > 0 && T > 0 && L > 0, "inharmonicityB: arguments must be positive");
    return kPi * kPi * kPi * E * d * d * d * d / (64.0 * T * L * L);
}

double partialHz(double f0, double B, int n) {
    need(f0 > 0 && B >= 0 && n >= 1, "partialHz: f0 > 0, B >= 0, n >= 1 required");
    return n * f0 * std::sqrt(1.0 + B * double(n) * double(n));
}

double stringTensionN(double mu, double L, double f0) {
    need(mu > 0 && L > 0 && f0 > 0, "stringTensionN: arguments must be positive");
    const double v = 2.0 * L * f0;
    return mu * v * v;
}

double lossFactorAir(double d, double rhoS, double f, double rhoAir, double nuAir) {
    need(d > 0 && rhoS > 0 && f > 0 && rhoAir > 0 && nuAir > 0, "lossFactorAir: arguments must be positive");
    const double M = (d / 4.0) * std::sqrt(2.0 * kPi * f / nuAir);
    return (rhoAir / rhoS) * (2.0 * std::sqrt(2.0) * M + 1.0) / (M * M);
}

double lossFactorBending(double E, double d, double rho, double L, double f1, int n, double etaE) {
    need(E > 0 && d > 0 && rho > 0 && L > 0 && f1 > 0 && n >= 1 && etaE >= 0, "lossFactorBending: invalid argument");
    const double k = E * kPi * kPi * d * d * double(n) * double(n);
    return k * etaE / (64.0 * rho * std::pow(L, 4) * f1 * f1 + k);
}

double lossFactorBridge(double Y, int n, double T, double mu) {
    need(Y >= 0 && n >= 1 && T > 0 && mu > 0, "lossFactorBridge: invalid argument");
    const double Y0 = 1.0 / std::sqrt(T * mu);
    return 2.0 * Y / (kPi * n * Y0);
}

PairModes solveCoupledPair(double w1, double w2, double eta1, double eta2, std::complex<double> ratio, double fRef) {
    using C = std::complex<double>;
    const C I(0.0, 1.0);
    const C z = I * (2.0 * fRef) * ratio;
    const C a = w1 * C(1.0, eta1 / 2.0) + z;
    const C d = w2 * C(1.0, eta2 / 2.0) + z;
    const C mean = 0.5 * (a + d);
    const C half = 0.5 * (a - d);
    const C root = std::sqrt(half * half + z * z);
    C lam[2] = {mean + root, mean - root};
    C shape[2][2];
    const double scale = std::max({std::abs(a), std::abs(d), std::abs(z), 1e-300});
    if (std::abs(z) <= 1e-15 * scale) {
        // Uncoupled (or degenerate): the shapes are the string axes, or the limit shapes for a repeated eigenvalue.
        if (std::abs(a - d) <= 1e-15 * scale) {
            const double s = std::sqrt(0.5);
            shape[0][0] = s; shape[0][1] = s; shape[1][0] = s; shape[1][1] = -s;
            lam[0] = lam[1] = a;
        } else {
            const bool firstIsA = std::abs(lam[0] - a) <= std::abs(lam[0] - d);
            lam[0] = firstIsA ? a : d;
            lam[1] = firstIsA ? d : a;
            shape[0][0] = firstIsA ? 1.0 : 0.0; shape[0][1] = firstIsA ? 0.0 : 1.0;
            shape[1][0] = firstIsA ? 0.0 : 1.0; shape[1][1] = firstIsA ? 1.0 : 0.0;
        }
    } else {
        for (int k = 0; k < 2; ++k) {
            // Eigenvector of [[a, z], [z, d]]: (z, lam - a) or (lam - d, z); take the longer, better conditioned one.
            const C v1[2] = {z, lam[k] - a};
            const C v2[2] = {lam[k] - d, z};
            const double n1 = std::norm(v1[0]) + std::norm(v1[1]);
            const double n2 = std::norm(v2[0]) + std::norm(v2[1]);
            const C* v = n1 >= n2 ? v1 : v2;
            const double n = std::sqrt(std::max(n1, n2));
            shape[k][0] = v[0] / n;
            shape[k][1] = v[1] / n;
        }
    }
    int hi = lam[0].imag() >= lam[1].imag() ? 0 : 1;
    PairModes out;
    for (int k = 0; k < 2; ++k) {
        const int s = k == 0 ? hi : 1 - hi;
        out.omega[k] = lam[s];
        out.shape[k][0] = shape[s][0];
        out.shape[k][1] = shape[s][1];
    }
    return out;
}

}  // namespace folk
