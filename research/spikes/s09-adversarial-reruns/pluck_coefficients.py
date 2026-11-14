"""Fourier sine coefficients of a string released from rest in a triangle with its apex at fraction beta:
b_n = 2 sin(n pi beta) / (n^2 pi^2 beta (1 - beta)). Checked by numerical integration (claim C-030)."""
import numpy as np, json
out = {}
for beta in (0.2, 0.25, 0.12):
    x = np.linspace(0, 1, 200001); y = np.where(x < beta, x / beta, (1 - x) / (1 - beta))
    num = [2 * np.trapezoid(y * np.sin(n * np.pi * x), x) for n in range(1, 13)]
    ana = [2 * np.sin(n * np.pi * beta) / (n * n * np.pi ** 2 * beta * (1 - beta)) for n in range(1, 13)]
    out[str(beta)] = dict(max_abs_diff=float(np.max(np.abs(np.array(num) - np.array(ana)))), vanishing=[n for n in range(1, 13) if abs(ana[n - 1]) < 1e-12])
print(json.dumps(out)); json.dump(out, open(__file__.replace(".py", "_output.json"), "w"), indent=1)
