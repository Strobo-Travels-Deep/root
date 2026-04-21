#!/usr/bin/env python3
"""Rabi-rate calibration reference for strobo 2.0.

At the clean anchor (alpha = 0, delta_0 = 0, theta_0 = 0) the coherence
contrast reduces to the closed form

    |C|_vacuum(Omega) = |sin(N * Omega_eff * dt)|,  Omega_eff = Omega * exp(-eta^2/2),

for both trains T1 and T2. Given a single experimental |C|_vacuum value
for either train, Omega can be read off directly.

This script:
  1. Plots |C|_vacuum vs Omega/(2*pi) on [0, 1.0] MHz for T1 and T2.
  2. Marks three candidate values: 0.178 MHz (strobo 2.0 sweep),
     0.300 MHz (Hasse 2024 Table II AC), 0.446 MHz (implied by
     t_pi = 1.122 us).
  3. Cross-checks |C|_vacuum numerically against the full engine at
     each candidate for T2 to confirm the closed form.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from stroboscopic_sweep import run_single  # noqa: E402

ETA = 0.395
OMEGA_M_MHZ = 1.306
DW = float(np.exp(-ETA ** 2 / 2))          # ~0.9249

TRAINS = [
    {"label": "T1:  N=3,  dt=100 ns", "N": 3, "dt_us": 0.100, "color": "#1f77b4"},
    {"label": "T2:  N=7,  dt= 50 ns", "N": 7, "dt_us": 0.050, "color": "#d62728"},
]

CANDIDATES = [
    (0.178, "sweep value (strobo 2.0)"),
    (0.300, "Hasse 2024 Table II AC"),
    (0.446, "from t_pi = 1.122 us"),
]


def coh_vacuum_closed_form(omega_2pi_mhz: float, N: int, dt_us: float) -> float:
    """|C|_vacuum = |sin(N * Omega_eff * dt)|. Omega_eff = 2*pi*omega_2pi*DW."""
    omega_eff = 2 * np.pi * omega_2pi_mhz * DW  # rad/us
    return abs(np.sin(N * omega_eff * dt_us))


def coh_vacuum_engine(omega_2pi_mhz: float, N: int, dt_us: float) -> float:
    """Run the full engine at (alpha=0, delta=0, theta_0=0) and compute
    |C| = sqrt(sz_A^2 + sz_B^2) from two initial spins."""
    base = dict(
        alpha=0.0,
        alpha_phase_deg=0.0,
        eta=ETA,
        omega_m=2 * np.pi * OMEGA_M_MHZ,
        omega_r=2 * np.pi * omega_2pi_mhz,
        nmax=40,
        theta_deg=90.0,
        phi_deg=0.0,
        det_min=0.0, det_max=0.0, npts=1,
        n_pulses=N,
        delta_t_us=dt_us,
        t_sep_factor=0.77 / (1.0 / OMEGA_M_MHZ),
        intra_pulse_motion=True,
        ac_phase_deg=0.0,
        mw_pi2_phase_deg=None,
    )
    pA = dict(base); pA["phi_deg"] = 0.0
    dA, _ = run_single(pA, verbose=False)
    pB = dict(base); pB["phi_deg"] = 90.0
    dB, _ = run_single(pB, verbose=False)
    return float(np.hypot(dA["sigma_z"][0], dB["sigma_z"][0]))


def main() -> None:
    print("Rabi calibration reference (strobo 2.0)")
    print(f"  eta = {ETA}   Debye-Waller factor = exp(-eta^2/2) = {DW:.4f}")
    print(f"  |C|_vacuum = |sin(N * 2*pi*Omega/(2pi) * DW * dt)|\n")

    print(f"  {'Omega/(2pi) [MHz]':<22}  {'|C|_vac T1':>10}  {'|C|_vac T2':>10}  source")
    print(f"  {'-'*22}  {'-'*10}  {'-'*10}  ------")
    for om, label in CANDIDATES:
        c1 = coh_vacuum_closed_form(om, 3, 0.100)
        c2 = coh_vacuum_closed_form(om, 7, 0.050)
        print(f"  {om:<22.4f}  {c1:>10.4f}  {c2:>10.4f}  {label}")

    print("\n  Numerical cross-check (full engine, T2, each candidate):")
    for om, label in CANDIDATES:
        c_cf = coh_vacuum_closed_form(om, 7, 0.050)
        c_en = coh_vacuum_engine(om, 7, 0.050)
        print(f"    Omega/(2pi) = {om:.3f} MHz  closed form = {c_cf:.6f}   "
              f"engine = {c_en:.6f}   diff = {c_en - c_cf:+.2e}")

    omega_grid = np.linspace(0.01, 1.0, 500)
    fig, ax = plt.subplots(figsize=(8.5, 5.0), constrained_layout=True)
    for tr in TRAINS:
        c = np.array([coh_vacuum_closed_form(om, tr["N"], tr["dt_us"]) for om in omega_grid])
        ax.plot(omega_grid, c, lw=2.2, color=tr["color"], label=tr["label"])

    for om, label in CANDIDATES:
        ax.axvline(om, ls="--", color="gray", lw=0.7, alpha=0.6)
        ax.text(om, 1.03, f"{om:.3f}", rotation=90, ha="right", va="bottom",
                fontsize=8, color="gray")

    ax.set_xlabel(r"$\Omega/(2\pi)$  [MHz]")
    ax.set_ylabel(r"$|C|_\mathrm{vacuum}$  at  $(\delta_0=0,\ \vartheta_0=0,\ |\alpha|=0)$")
    ax.set_title("Rabi calibration reference  —  "
                 r"$|C|_\mathrm{vacuum} = |\sin(N\, \Omega_\mathrm{eff}\, \delta t)|$,  "
                 r"$\Omega_\mathrm{eff} = \Omega\, e^{-\eta^2/2}$  "
                 f"($\\eta={ETA}$,  DW$=${DW:.4f})")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right")

    out = Path(__file__).resolve().parents[1] / "plots" / "00_rabi_calibration.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  wrote {out.relative_to(out.parents[2])}")


if __name__ == "__main__":
    main()
