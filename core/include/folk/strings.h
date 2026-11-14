// String physics used by the plucked instruments (plan/DECISIONS.md, D-060 to D-062).
#pragma once
#include <complex>

namespace folk {

/// B = pi^3 E d^4 / (64 T L^2) for a solid round wire.
double inharmonicityB(double youngsModulusPa, double diameterM, double tensionN, double lengthM);
/// f_n = n f0 sqrt(1 + B n^2).
double partialHz(double f0Hz, double B, int n);
/// T = mu (2 L f0)^2.
double stringTensionN(double linearDensity, double lengthM, double f0Hz);

/// eta_air = (rhoAir / rhoString) (2 sqrt(2) M + 1) / M^2, M = (d / 4) sqrt(2 pi f / nuAir).
double lossFactorAir(double diameterM, double stringDensity, double frequencyHz, double rhoAir = 1.2, double nuAir = 1.5e-5);
/// eta_bend = E pi^2 d^2 n^2 etaE / (64 rho L^4 f1^2 + E pi^2 d^2 n^2).
double lossFactorBending(double youngsModulusPa, double diameterM, double stringDensity, double lengthM, double f1Hz, int n, double etaE);
/// eta_b = 2 Re(Y) / (pi n Y0), Y0 = 1 / sqrt(T mu).
double lossFactorBridge(double bridgeConductance, int n, double tensionN, double linearDensity);

struct PairModes {
    std::complex<double> omega[2];        ///< complex angular frequencies (rad/s), Im > 0 means decay, a(t) ~ exp(i omega t)
    std::complex<double> shape[2][2];     ///< shape[k][j]: component of string j in mode k (each mode normalised to unit Euclidean norm)
};
/// Two strings sharing a bridge, one partial each: Omega = [[w1 (1 + i eta1/2) + z, z], [z, w2 (1 + i eta2/2) + z]],
/// z = i * 2 * fRef * Y / Y0 with Y / Y0 = bridgeAdmittanceRatio (complex). omega[0] is the mode with the larger Im.
PairModes solveCoupledPair(double w1, double w2, double eta1, double eta2, std::complex<double> bridgeAdmittanceRatio, double fRefHz);

}  // namespace folk
