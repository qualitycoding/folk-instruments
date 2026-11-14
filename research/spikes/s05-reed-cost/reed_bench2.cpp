// Spike S05b: cost of 64 sounding reeds (16 keys x ranks L, M, M+, H) with the similarity scaling of S12 and per-reed
// sub-steps so that every reed takes at least 110 steps per period. Build: g++ -O2 -std=c++20 reed_bench2.cpp -o reed_bench2
#include <chrono>
#include <cmath>
#include <cstdio>
#include <vector>
struct Reed { double x, v, p1, u, w0, x0, Sr, mu, V1, Ain, lo, hi; int sub; std::vector<double> tab; double amp; };
int main() {
  const double fsHost = 48000.0, R = 4, fs = fsHost * R, rho = 1.2, c0 = 343, alpha = 0.61, Q = 95, K = 47.9, Lr = 12.95e-3, Wr = 2.1e-3, L2 = 20e-3, S2 = 25e-6;
  const int N = 2048; std::vector<Reed> r;
  for (int key = 48; key < 80; key += 2)
    for (double mult : {0.5, 1.0, 1.009, 2.0}) {
      double f = 440.0 * std::pow(2.0, (key - 69) / 12.0) * mult, k = f / 444.0; Reed q{};
      q.x0 = 528e-6 / k; double er = 110e-6 / k, es = 900e-6 / k, hmin = 50e-6 / k; q.Sr = Wr * Lr * 0.3915 / k; q.w0 = 2 * M_PI * f; q.mu = q.Sr * q.w0 * q.w0 / K;
      q.V1 = 800e-6 * 0.06 / (k * k); q.Ain = 30e-6 / k; q.lo = -6 * q.x0 - es - er; q.hi = 6 * q.x0; q.tab.resize(N + 1);
      for (int i = 0; i <= N; ++i) { double x = q.lo + (q.hi - q.lo) * i / N, h = x > 0 ? x : (x < -(es + er) ? -(x + es + er) : 0); q.tab[i] = Wr * std::hypot(h, hmin) + 2 * Lr * std::hypot(0.39 * h, hmin); }
      q.sub = (int)std::ceil(110.0 * f / fs); q.x = q.x0; r.push_back(q);
    }
  const double seconds = 3.0, p0 = 600; const long n = (long)(seconds * fs); double acc = 0; long steps = 0;
  auto t0 = std::chrono::steady_clock::now();
  for (long kk = 0; kk < n; ++kk)
    for (auto& q : r) {
      const double dt = 1.0 / (fs * q.sub);
      for (int s = 0; s < q.sub; ++s) {
        double d = p0 - q.p1, u0 = alpha * q.Ain * std::copysign(std::sqrt(2 * std::fabs(d) / rho), d);
        double t = (q.x - q.lo) / (q.hi - q.lo) * N; t = t < 0 ? 0 : (t > N - 1 ? N - 1 : t); int i = (int)t; double Su = q.tab[i] + (q.tab[i + 1] - q.tab[i]) * (t - i);
        double vj = (q.u + q.Sr * q.v) / (alpha * Su), p2 = 0.5 * rho * vj * std::fabs(vj);
        q.p1 += dt * rho * c0 * c0 / q.V1 * (u0 - q.u); q.u += dt * S2 / (rho * L2) * (q.p1 - p2);
        q.v += dt * (-q.w0 / Q * q.v - q.w0 * q.w0 * (q.x - q.x0) - q.mu * p2); q.x += dt * q.v; ++steps;
      }
      acc += q.u; if (kk > n / 2) q.amp = std::max(q.amp, std::fabs(q.x - q.x0) / q.x0);
    }
  double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count(); int sounding = 0, maxsub = 0; bool finite = true;
  for (auto& q : r) { sounding += q.amp > 0.5; maxsub = std::max(maxsub, q.sub); finite = finite && std::isfinite(q.x); }
  std::printf("{\"reeds\": %zu, \"sounding\": %d, \"finite\": %s, \"max_substeps\": %d, \"steps_per_host_sample\": %.1f, \"audio_seconds\": %.1f, \"wall_seconds\": %.3f, \"realtime_factor\": %.2f, \"ns_per_step\": %.2f}\n",
              r.size(), sounding, finite ? "true" : "false", maxsub, double(steps) / (seconds * fsHost), seconds, el, seconds / el, el * 1e9 / steps);
}
