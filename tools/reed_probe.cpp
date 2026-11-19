// reed_probe: runs one reed of the core from rest and reports pitch offset and amplitude (plan/PLAN.md S-200; analysis as analyse() in
// research/spikes/s12-reed-similarity-scaling/similarity.py).
//   reed_probe --freq <natural Hz> --pressure <Pa> --rate <host Hz> [--instrument <name>] [--undriven] [--time]
#include <algorithm>
#include <chrono>
#include <cmath>
#include <complex>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include "../core/src/reed.h"

namespace {
using cd = std::complex<double>;
void fft(std::vector<cd>& a) {
    const size_t n = a.size();
    for (size_t i = 1, j = 0; i < n; ++i) {
        size_t bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) std::swap(a[i], a[j]);
    }
    for (size_t len = 2; len <= n; len <<= 1) {
        const double ang = -2.0 * M_PI / double(len);
        const cd wl(std::cos(ang), std::sin(ang));
        for (size_t i = 0; i < n; i += len) {
            cd w(1.0);
            for (size_t k = 0; k < len / 2; ++k) {
                const cd u = a[i + k], v = a[i + k + len / 2] * w;
                a[i + k] = u + v;
                a[i + k + len / 2] = u - v;
                w *= wl;
            }
        }
    }
}
}  // namespace

int main(int argc, char** argv) {
    double freq = 444, pressure = 400, rate = 48000;
    bool undriven = false, timing = false;
    for (int i = 1; i < argc; ++i) {
        const std::string a = argv[i];
        auto val = [&]() { return i + 1 < argc ? std::atof(argv[++i]) : 0.0; };
        if (a == "--freq") freq = val();
        else if (a == "--pressure") pressure = val();
        else if (a == "--rate") rate = val();
        else if (a == "--instrument") { if (i + 1 < argc) ++i; }
        else if (a == "--undriven") undriven = true;
        else if (a == "--time") timing = true;
        else { std::fprintf(stderr, "reed_probe: unknown option %s\n", a.c_str()); return 2; }
    }
    const double R = 4.0 * rate;
    auto table = folk::buildReedTable();
    folk::Reed reed;
    reed.configure(table, freq, R, {});
    const double x0 = reed.x0();

    if (undriven) {
        const long n = long(2.0 * R);
        // Displace the tip by x0 (x = 2 x0) with the supply at 0 Pa: the amplitude must decay.
        folk::Reed r2;
        r2.configure(table, freq, R, {});
        r2.reset();
        // use public API only: emulate displacement by driving nothing; the displacement is set through a short kick below.
        std::vector<double> xs(static_cast<size_t>(n));
        // Kick: a brief high pressure would change the state differently; instead integrate from x0 + x0 via the friend-free helper.
        r2.kick(x0);
        for (long i = 0; i < n; ++i) { r2.step(0.0); xs[size_t(i)] = r2.x(); }
        auto amp = [&](long a, long b) { double lo = 1e9, hi = -1e9; for (long i = a; i < b; ++i) { lo = std::min(lo, xs[size_t(i)]); hi = std::max(hi, xs[size_t(i)]); } return (hi - lo) / 2.0 / x0; };
        std::printf("{\"amp_first_10pct\": %.6g, \"amp_last_10pct\": %.6g}\n", amp(0, n / 10), amp(n - n / 10, n));
        return 0;
    }

    const long n = long(std::ceil(450.0 * R / freq));
    const long rampN = long(9.0 * R / freq);
    std::vector<double> xs(static_cast<size_t>(n)), us(static_cast<size_t>(n));
    bool bad = false;
    double prevU = 0;
    std::vector<double> src(static_cast<size_t>(n));
    for (long i = 0; i < n; ++i) {
        const double p0 = pressure * std::min(1.0, double(i) / double(rampN));
        const double u = reed.step(p0);
        xs[size_t(i)] = reed.x();
        us[size_t(i)] = u;
        src[size_t(i)] = (u - prevU) * R;
        prevU = u;
        if (!reed.finite() || std::fabs(reed.x()) > 1.0) { bad = true; break; }
    }
    if (bad) { std::printf("{\"state\": \"diverged\", \"cents\": 0, \"amp_over_x0\": 0, \"source_rms\": 0}\n"); return 0; }
    const long a0 = long(0.7 * double(n)), len = n - a0;
    double lo = 1e9, hi = -1e9, mean = 0, ss = 0;
    for (long i = a0; i < n; ++i) { lo = std::min(lo, xs[size_t(i)]); hi = std::max(hi, xs[size_t(i)]); mean += xs[size_t(i)]; ss += src[size_t(i)] * src[size_t(i)]; }
    mean /= double(len);
    const double amp = (hi - lo) / 2.0 / x0, srms = std::sqrt(ss / double(len));
    if (amp < 0.02) {
        std::printf("{\"state\": \"silent\", \"cents\": 0, \"amp_over_x0\": %.4f, \"source_rms\": %.6g}\n", amp, srms);
    } else {
        size_t N = 1; while (N < size_t(4 * len)) N <<= 1;
        std::vector<cd> buf(N, cd(0));
        for (long i = 0; i < len; ++i) {
            const double w = 0.5 - 0.5 * std::cos(2.0 * M_PI * double(i) / double(len - 1));
            buf[size_t(i)] = (xs[size_t(a0 + i)] - mean) * w;
        }
        fft(buf);
        const size_t k0 = size_t(0.5 * freq * double(N) / R);
        size_t k = k0;
        for (size_t j = k0; j < N / 2; ++j) if (std::abs(buf[j]) > std::abs(buf[k])) k = j;
        const double A = std::log(std::abs(buf[k - 1])), B = std::log(std::abs(buf[k])), C = std::log(std::abs(buf[k + 1]));
        const double f0 = (double(k) + 0.5 * (A - C) / (A - 2 * B + C)) * R / double(N);
        std::printf("{\"state\": \"sounds\", \"cents\": %.3f, \"amp_over_x0\": %.4f, \"source_rms\": %.6g}\n", 1200.0 * std::log2(f0 / freq), amp, srms);
    }
    if (timing) {
        const long steps = long(10.0 * R);
        double best = 1e30;
        for (int rep = 0; rep < 3; ++rep) {
            const auto t0 = std::chrono::steady_clock::now();
            double sink = 0;
            for (long i = 0; i < steps; ++i) sink += reed.step(pressure);
            const auto t1 = std::chrono::steady_clock::now();
            best = std::min(best, std::chrono::duration<double, std::nano>(t1 - t0).count() / double(steps));
            if (sink == 12345.678) std::puts("");
        }
        std::printf("{\"ns_per_reed_sample\": %.3f}\n", best);
    }
    return 0;
}
