// Spike S05: cost of one reed step (pressure-driven minimal model, table-lookup useful section) in C++.
// Build: g++ -O2 -std=c++20 reed_bench.cpp -o reed_bench ; run: ./reed_bench <reeds> <oversampling>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>
struct Reed { double x, v, p1, u, w0, x0; };
int main(int argc, char** argv) {
  int reeds = argc > 1 ? atoi(argv[1]) : 64, os = argc > 2 ? atoi(argv[2]) : 4;
  const double fs = 48000.0 * os, dt = 1 / fs, rho = 1.2, c0 = 343, alpha = 0.61, Q = 95, K = 47.9;
  const double Lr = 12.95e-3, Wr = 2.1e-3, hmin = 50e-6, er = 110e-6, es = 900e-6, Sr = Wr * Lr * 0.3915;
  const double V1 = 800e-6 * 0.06, L2 = 20e-3, S2 = 25e-6, Ain = 30e-6;
  const int N = 4096; const double xlo = -4e-3, xhi = 4e-3; std::vector<double> tab(N + 1);
  for (int i = 0; i <= N; ++i) { double x = xlo + (xhi - xlo) * i / N, h = x > 0 ? x : (x < -(es + er) ? -(x + es + er) : 0);
    tab[i] = Wr * std::hypot(h, hmin) + 2 * Lr * std::hypot(0.39 * h, hmin); }
  std::vector<Reed> r(reeds);
  for (int i = 0; i < reeds; ++i) { double f = 110.0 * std::pow(2.0, i / 12.0); r[i] = {528e-6, 0, 0, 0, 2 * M_PI * f, 528e-6}; }
  const double seconds = 2.0; const long n = (long)(seconds * fs); double acc = 0; const double p0 = 400;
  auto t0 = std::chrono::steady_clock::now();
  for (long k = 0; k < n; ++k)
    for (auto& q : r) {
      double mu = Sr * q.w0 * q.w0 / K, d = p0 - q.p1, u0 = alpha * Ain * std::copysign(std::sqrt(2 * std::fabs(d) / rho), d);
      double t = (q.x - xlo) / (xhi - xlo) * N; t = t < 0 ? 0 : (t > N - 1 ? N - 1 : t); int i = (int)t; double Su = tab[i] + (tab[i + 1] - tab[i]) * (t - i);
      double vj = (q.u + Sr * q.v) / (alpha * Su), p2 = 0.5 * rho * vj * std::fabs(vj);
      q.p1 += dt * rho * c0 * c0 / V1 * (u0 - q.u); q.u += dt * S2 / (rho * L2) * (q.p1 - p2);
      q.v += dt * (-q.w0 / Q * q.v - q.w0 * q.w0 * (q.x - q.x0) - mu * p2); q.x += dt * q.v; acc += q.u;
    }
  double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  std::printf("{\"reeds\": %d, \"oversampling\": %d, \"audio_seconds\": %.1f, \"wall_seconds\": %.4f, \"realtime_factor\": %.2f, \"ns_per_reed_step\": %.2f, \"checksum\": %.6g}\n",
              reeds, os, seconds, el, seconds / el, el * 1e9 / (double(n) * reeds), acc);
}
