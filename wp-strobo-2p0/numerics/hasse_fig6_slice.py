#!/usr/bin/env python3
"""Hasse-Fig.-6-style (phi, theta_0) slice.

Direct visual analogue of Hasse 2024 Fig. 6(a,b): at a single
informative cell (delta_0 = 0, |alpha| = 3) scan the AC-train analysis
phase phi and the initial motional-state phase theta_0. Record
<sigma_z> and the Hasse back-action delta<n> = <n>_fin - |alpha|^2.

Runs T1 (N=3, dt=100 ns) and T2 (N=7, dt=50 ns) in parallel for
comparison. Also runs |alpha|=4.5 as a companion sheet since the
back-action amplitude scales with |alpha|.

Output:
  numerics/hasse_fig6_slice.npz
  plots/06_hasse_fig6_alpha3.png
  plots/07_hasse_fig6_alpha4p5.png
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from stroboscopic_sweep import run_single  # noqa: E402

ETA = 0.395
OMEGA_M_MHZ = 1.306
DELTA_T_US = 0.77
T_M_US = 1.0 / OMEGA_M_MHZ
T_SEP_FACTOR = DELTA_T_US / T_M_US
NMAX = 60
_DW = float(np.exp(-ETA ** 2 / 2))


def omega_for_pi2(N: int, dt_us: float) -> float:
    """Bare Omega/(2pi) [MHz] such that N*Omega*DW*dt = pi/2."""
    return 1.0 / (4.0 * N * dt_us * _DW)


N_PHI = 32
N_THETA = 64
PHI_DEG = np.linspace(0.0, 360.0, N_PHI, endpoint=False)
THETA0_DEG = np.linspace(0.0, 360.0, N_THETA, endpoint=False)

TRAINS = [
    {"label": "T1", "title": "T1:  N=3,  $\\delta t$=100 ns", "N": 3, "dt_us": 0.100},
    {"label": "T2", "title": "T2:  N=7,  $\\delta t$= 50 ns", "N": 7, "dt_us": 0.050},
]
for _t in TRAINS:
    _t["omega_r_MHz"] = omega_for_pi2(_t["N"], _t["dt_us"])

ALPHAS = [3.0, 4.5]


def base_params(N: int, dt_us: float, alpha: float, omega_r_MHz: float) -> dict:
    return dict(
        alpha=alpha,
        eta=ETA,
        omega_m=2 * np.pi * OMEGA_M_MHZ,
        omega_r=2 * np.pi * omega_r_MHz,
        nmax=NMAX,
        theta_deg=90.0,
        phi_deg=0.0,
        det_min=0.0, det_max=0.0, npts=1,
        n_pulses=N,
        delta_t_us=dt_us,
        t_sep_factor=T_SEP_FACTOR,
        intra_pulse_motion=True,
        mw_pi2_phase_deg=None,
    )


def run_sheet(N: int, dt_us: float, alpha: float, omega_r_MHz: float) -> dict:
    """(phi, theta_0) sheet at delta=0. One engine call per cell."""
    sz = np.zeros((N_PHI, N_THETA))
    nbar = np.zeros((N_PHI, N_THETA))
    base = base_params(N, dt_us, alpha, omega_r_MHz)
    t0 = time.time()
    for i, phi in enumerate(PHI_DEG):
        for j, th0 in enumerate(THETA0_DEG):
            p = dict(base)
            p["ac_phase_deg"] = float(phi)
            p["alpha_phase_deg"] = float(th0)
            d, _ = run_single(p, verbose=False)
            sz[i, j] = d["sigma_z"][0]
            nbar[i, j] = d["nbar"][0]
        if (i + 1) % 4 == 0:
            el = time.time() - t0
            pct = (i + 1) / N_PHI * 100
            eta = el * (N_PHI - i - 1) / (i + 1)
            print(f"    phi {i + 1:2d}/{N_PHI}  ({pct:4.1f} %)   "
                  f"elapsed {el:5.1f}s   ETA {eta:5.1f}s", flush=True)
    return dict(sz=sz, nbar=nbar, delta_n=nbar - alpha ** 2)


def main() -> None:
    print("strobo 2.0  —  Hasse-Fig-6 (phi, theta_0) slice (pi/2-calibrated)")
    print(f"  delta_0 = 0,  alphas = {ALPHAS}")
    for t in TRAINS:
        print(f"  {t['label']}: N={t['N']}, dt={t['dt_us']*1e3:.0f} ns  ->  "
              f"Omega/(2pi) = {t['omega_r_MHz']:.4f} MHz")
    print(f"  grid = {N_PHI} phi x {N_THETA} theta_0 = {N_PHI * N_THETA} cells per sheet")
    print(f"  sheets = {len(ALPHAS)} alpha x {len(TRAINS)} trains = "
          f"{len(ALPHAS) * len(TRAINS)} total\n")

    out: dict = {"PHI_DEG": PHI_DEG, "THETA0_DEG": THETA0_DEG,
                 "ALPHAS": np.array(ALPHAS)}
    t_tot = time.time()
    for alpha in ALPHAS:
        for train in TRAINS:
            tag = f"{train['label']}_alpha{alpha:g}".replace(".", "p")
            print(f"[{tag}]  N={train['N']}  dt={train['dt_us']*1e3:.0f} ns  "
                  f"|alpha|={alpha}  Omega/(2pi)={train['omega_r_MHz']:.4f} MHz")
            sh = run_sheet(train["N"], train["dt_us"], alpha, train["omega_r_MHz"])
            for k, v in sh.items():
                out[f"{tag}_{k}"] = v

    out_path = Path(__file__).parent / "hasse_fig6_slice.npz"
    np.savez_compressed(out_path, **out)
    print(f"\nSaved: {out_path.relative_to(Path(__file__).parents[2])}  "
          f"({out_path.stat().st_size / 1024:.0f} KB)")
    print(f"Total wall time: {time.time() - t_tot:.1f} s")


if __name__ == "__main__":
    main()
