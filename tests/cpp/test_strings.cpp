// FROZEN — DO NOT MODIFY. Listed in tests/FROZEN_MANIFEST.sha256. Change only through a TEST_CHALLENGE amendment (HANDOFF.md).
// T-005 stiff-string and loss-factor formulas (SC-08; C-026, C-027; D-060, D-061). Expected values were computed
//       independently in research/spikes/s06-known-answers/ka.py; tolerance 1e-9 relative (closed-form arithmetic).
// T-006 coupled string pair (SC-08; C-028; D-062). Expected values from the same spike and from research/spikes/s04-coupled-pair.
#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>
#include <cmath>
#include "folk/strings.h"
using namespace folk;
using Catch::Matchers::WithinAbs;
using Catch::Matchers::WithinRel;

TEST_CASE("T-005 tension, inharmonicity and partials of a 0.015 in plain steel A4 string at 352.4 mm", "[unit][strings]") {
    const double E = 200e9, d = 0.015 * 0.0254, L = 0.3524, mu = 0.0008949720849559553;
    const double T = stringTensionN(mu, L, 440.0);
    CHECK_THAT(T, WithinRel(86.06897545237646, 1e-9));
    const double B = inharmonicityB(E, d, T, L);
    CHECK_THAT(B, WithinRel(0.0001910209980048386, 1e-9));
    CHECK_THAT(partialHz(440.0, B, 10), WithinRel(4441.8258241558015, 1e-9));
    CHECK_THAT(partialHz(440.0, 0.0, 7), WithinRel(3080.0, 1e-12));
}

TEST_CASE("T-005 loss factors", "[unit][strings]") {
    const double E = 200e9, d = 0.015 * 0.0254, rho = 7850.0, L = 0.3524;
    CHECK_THAT(lossFactorAir(d, rho, 440.0), WithinRel(0.0004257849256610978, 1e-9));
    CHECK_THAT(lossFactorAir(d, rho, 4400.0), WithinRel(0.00011487751362780074, 1e-9));
    CHECK(lossFactorAir(d, rho, 4400.0) < lossFactorAir(d, rho, 440.0));       // air damping falls with frequency
    CHECK_THAT(lossFactorBending(E, d, rho, L, 440.0, 1, 1e-3), WithinRel(1.9098451595199796e-07, 1e-9));
    CHECK_THAT(lossFactorBending(E, d, rho, L, 440.0, 20, 1e-3), WithinRel(7.098458099972623e-05, 1e-9));
    CHECK_THAT(lossFactorBridge(1e-4, 1, 86.06897545237646, 0.0008949720849559553), WithinRel(1.7668845952559997e-05, 1e-9));
    CHECK_THAT(lossFactorBridge(1e-4, 4, 86.06897545237646, 0.0008949720849559553), WithinRel(1.7668845952559997e-05 / 4.0, 1e-9));
}

TEST_CASE("T-005 invalid physical arguments throw std::invalid_argument", "[unit][strings]") {
    CHECK_THROWS_AS(inharmonicityB(200e9, 0.0, 80.0, 0.35), std::invalid_argument);
    CHECK_THROWS_AS(inharmonicityB(200e9, 4e-4, 0.0, 0.35), std::invalid_argument);
    CHECK_THROWS_AS(stringTensionN(-1.0, 0.35, 440.0), std::invalid_argument);
    CHECK_THROWS_AS(partialHz(440.0, 1e-4, 0), std::invalid_argument);
    CHECK_THROWS_AS(lossFactorAir(4e-4, 7850.0, 0.0), std::invalid_argument);
}

TEST_CASE("T-006 unison pair with a resistive bridge: one fast mode, one slow mode", "[unit][strings]") {
    const double w = 2.0 * M_PI * 660.0;
    // z = i * 2 * 660 * (pi * 1e-3) = i * eta_b * w / 2 with eta_b = 2e-3; intrinsic eta = 2e-4.
    const PairModes m = solveCoupledPair(w, w, 2e-4, 2e-4, {M_PI * 1e-3, 0.0}, 660.0);
    CHECK_THAT(m.omega[0].real(), WithinRel(4146.9023027385265, 1e-9));
    CHECK_THAT(m.omega[0].imag(), WithinRel(8.708494835751026, 1e-9));     // w * (eta/2 + eta_b): symmetric mode
    CHECK_THAT(m.omega[1].imag(), WithinRel(0.4146902302741182, 1e-6));    // w * eta/2: antisymmetric mode
    CHECK_THAT(std::abs(m.shape[0][0]), WithinRel(std::sqrt(0.5), 1e-6));
    CHECK_THAT(std::abs(m.shape[0][1]), WithinRel(std::sqrt(0.5), 1e-6));
    // The slow mode exerts no net force on the bridge.
    CHECK_THAT(std::abs(m.shape[1][0] + m.shape[1][1]), WithinAbs(0.0, 1e-6));
}

TEST_CASE("T-006 weakly coupled pair mistuned by 4 cents beats at the difference frequency", "[unit][strings]") {
    const double w1 = 2.0 * M_PI * 660.0, w2 = w1 * std::pow(2.0, 4.0 / 1200.0);
    const PairModes m = solveCoupledPair(w1, w2, 2e-4, 2e-4, {M_PI * 1e-5, 0.0}, 660.0);
    const double splitHz = std::abs(m.omega[0].real() - m.omega[1].real()) / (2.0 * M_PI);
    CHECK_THAT(splitHz, WithinRel(1.5266297500187231, 1e-6));
    CHECK_THAT(splitHz, WithinRel(660.0 * (std::pow(2.0, 4.0 / 1200.0) - 1.0), 1e-3));
    CHECK(m.omega[0].imag() >= m.omega[1].imag());
    CHECK(m.omega[1].imag() > 0.0);
}

TEST_CASE("T-006 strongly coupled pair mistuned by 3 cents locks", "[unit][strings]") {
    const double w1 = 2.0 * M_PI * 660.0, w2 = w1 * std::pow(2.0, 3.0 / 1200.0);
    const PairModes m = solveCoupledPair(w1, w2, 2e-4, 2e-4, {M_PI * 1e-3, 0.0}, 660.0);
    const double splitHz = std::abs(m.omega[0].real() - m.omega[1].real()) / (2.0 * M_PI);
    CHECK(splitHz < 0.01);                                   // against 1.14 Hz uncoupled (spike S04)
    // Exact eigenvalues mean +/- sqrt(delta^2 + z^2) (closed form, equal to numpy.linalg.eig to 1e-12). At 3 cents the
    // detuning (3.59 rad/s) is close to the coupling (4.15 rad/s), so the decay rates are only partly separated: 6.63 and
    // 2.50 (21:1 at unison, 1:1 once unlocked at 4 cents). Amended by TEST_CHALLENGE (S-101): the earlier '> 10 times'
    // was never computed from the spike and no correct solver can meet it (D-096).
    CHECK_THAT(m.omega[0].imag(), WithinRel(6.627051213076816, 1e-6));
    CHECK_THAT(m.omega[1].imag(), WithinRel(2.4968530793399473, 1e-6));
    CHECK(m.omega[0].imag() > 2.0 * m.omega[1].imag());      // fast and slow modes remain distinct
}
