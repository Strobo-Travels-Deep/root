#!/usr/bin/env python3
"""
engine_spectral_scan.py — verify multi-sideband structure of the pulse train.

A stroboscopic train with T_sep = T_m = 2π/ω_m has spectral support at
every harmonic k·ω_m. For laser detuning δ relative to the carrier,
resonance conditions are δ = k·ω_m for k ∈ ℤ. Outside the Lamb–Dicke
regime, each harmonic couples |n⟩ ↔ |n+|k|⟩ (and further in non-LD) via
the Laguerre-dressed matrix elements.

Our engine (v0.9.1) computes exp(-iH δt) exactly with H containing
ω_m·a†a AND the full non-LD coupling, so all sidebands are present in
principle. This script verifies by running a WIDE detuning scan
δ ∈ [-3ω_m, +3ω_m] and showing that distinct resonance features appear
at δ = 0, ±ω_m, ±2ω_m, ±3ω_m.

Output: notebooks/outputs/engine_spectrum.png
"""

import os, sys, time
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = SCRIPT_DIR.parent / 'scripts'
sys.path.insert(0, str(ENGINE_DIR))
import stroboscopic_sweep as ss


ETA       = 0.397
OMEGA_M   = 1.3
OMEGA_R   = 0.3
N_PULSES  = 22

ALPHA_VALUES = (0.0, 1.0, 3.0)
DET_REL_MAX  = 3.0               # ±3·ω_m — spans carrier + three sideband orders
N_DET        = 401
NMAX         = 60


def run_alpha(alpha):
    p = dict(
        alpha=float(alpha), alpha_phase_deg=0.0,
        eta=ETA, omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES, n_thermal=0.0, n_thermal_traj=1,
        nmax=NMAX,
        det_min=-DET_REL_MAX, det_max=+DET_REL_MAX, npts=N_DET,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0, T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_rep=0,
        mw_pi2_phase_deg=None,              # no MW π/2 — bare pulse-train response
        intra_pulse_motion=True,
        center_pulses_at_phase=False,
    )
    d, conv = ss.run_single(p, verbose=False)
    return (np.array(d['detuning']),
            np.array(d['sigma_x']), np.array(d['sigma_y']), np.array(d['sigma_z']),
            np.array(d['nbar']), conv['max_fock_leakage'])


def main():
    print(f"Engine spectral scan: α ∈ {ALPHA_VALUES}, "
          f"δ/ω_m ∈ [−{DET_REL_MAX}, +{DET_REL_MAX}] ({N_DET} pts each)")
    print(f"  η={ETA}, ω_m/(2π)={OMEGA_M}, Ω/(2π)={OMEGA_R}, N={N_PULSES}, "
          f"intra_pulse_motion=True, no MW π/2")
    print()

    results = {}
    t0 = time.time()
    for a in ALPHA_VALUES:
        det, sx, sy, sz, nb, leak = run_alpha(a)
        results[a] = (det, sx, sy, sz, nb, leak)
        Cabs = np.hypot(sx, sy)
        print(f"  α = {a:.1f}  worst leak {leak:.1e}  "
              f"|C| range [{Cabs.min():.3f}, {Cabs.max():.3f}]  "
              f"σ_z range [{sz.min():+.3f}, {sz.max():+.3f}]")
    print(f"  total {time.time() - t0:.1f} s")

    # Plot: σ_z(δ) for each α, marking integer-sideband positions
    fig, axs = plt.subplots(2, 1, figsize=(11, 6), sharex=True, constrained_layout=True)

    ax = axs[0]
    for a in ALPHA_VALUES:
        det, sx, sy, sz, nb, leak = results[a]
        ax.plot(det, sz, lw=1.4, label=fr'$|\alpha|={a:.1f}$')
    for k in (-3, -2, -1, 0, 1, 2, 3):
        ax.axvline(k, color='grey', lw=0.4, ls='--', alpha=0.6)
        ax.text(k, 1.0, f'{k:+d}' if k else '0', color='grey',
                fontsize=9, ha='center', va='bottom')
    ax.axhline(0, color='k', lw=0.3)
    ax.set_ylabel(r'$\langle\sigma_z\rangle$')
    ax.set_title(r'Stroboscopic pulse-train spectrum: $\sigma_z$ vs $\delta/\omega_m$',
                 fontsize=10)
    ax.legend(fontsize=9)
    ax.set_xlim(-DET_REL_MAX, +DET_REL_MAX)
    ax.grid(alpha=0.3)

    ax = axs[1]
    for a in ALPHA_VALUES:
        det, sx, sy, sz, nb, leak = results[a]
        Cabs = np.hypot(sx, sy)
        ax.plot(det, Cabs, lw=1.4, label=fr'$|\alpha|={a:.1f}$')
    for k in (-3, -2, -1, 0, 1, 2, 3):
        ax.axvline(k, color='grey', lw=0.4, ls='--', alpha=0.6)
    ax.axhline(0, color='k', lw=0.3)
    ax.set_xlabel(r'laser detuning  $\delta / \omega_m$  (integer = sideband order)')
    ax.set_ylabel(r'$|C| = \sqrt{\sigma_x^2 + \sigma_y^2}$')
    ax.set_title(r'Same, for $|C|$ (Bloch-vector amplitude)', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    fig.suptitle('Engine wide-δ scan — sidebands of the stroboscopic pulse train',
                 fontsize=11)

    out_path = SCRIPT_DIR / 'outputs' / 'engine_spectrum.png'
    fig.savefig(out_path, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"\n  wrote {out_path.relative_to(SCRIPT_DIR.parent)}")

    # Quantitative summary: σ_z peak positions
    det_ref, _, _, sz_ref, _, _ = results[ALPHA_VALUES[1]]   # α=1, sideband structure sharpest
    from scipy.signal import find_peaks
    pk, props = find_peaks(np.abs(sz_ref), prominence=0.05)
    print(f"\nσ_z(δ) prominent features at α=1 (prominence ≥ 0.05):")
    for p in pk:
        print(f"  δ/ω_m = {det_ref[p]:+6.3f}   σ_z = {sz_ref[p]:+.4f}")


if __name__ == '__main__':
    main()
