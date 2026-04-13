#!/usr/bin/env python3
"""
run_fig8.py — Reproduce Hasse 2024 Fig 8 (panels a and b).

Numerical calibrations to convert (analysis-phase shift ϕ₀) and (contrast
C) into position |α| and momentum |⟨P⟩| respectively, evaluated at three
LF-mode tilt angles {−5°, 0°, +5°} relative to the AC wave-vector axis,
with n_thermal = 0.15.

For each tilt angle:
    η(angle) = η_LF · cos(angle)

For each |α| we read the engine's (σ_x, σ_y) at zero detuning and form

    C   = ⟨σ_x⟩ + i ⟨σ_y⟩
    ϕ₀  = arg(C)        (signed; unwrapped along |α| ascending)
    |C| = √(σ_x² + σ_y²)

Output: numerics/fig8_calibrations.h5
"""

import os
import sys
import time
from datetime import datetime, timezone
import numpy as np
import h5py

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts'))
sys.path.insert(0, ENGINE_DIR)
import stroboscopic_sweep as ss


ETA_LF      = 0.397
TILT_DEG    = (-5.0, 0.0, +5.0)
ALPHA_GRID  = np.linspace(0.0, 8.0, 17)         # 0, 0.5, 1, …, 8
OMEGA_M     = 1.3
OMEGA_R     = 0.3
N_PULSES    = 22
N_THERMAL   = 0.15
N_TH_TRAJ   = 32                                 # thermal sampling


def nmax_for_alpha(alpha):
    a = float(alpha)
    if a <= 1.0: return 30
    if a <= 3.0: return 50
    if a <= 5.0: return 80
    return 120


def run_single_alpha_eta(alpha, eta):
    p = dict(
        alpha=float(alpha), alpha_phase_deg=0.0,
        eta=float(eta), omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES, n_thermal=N_THERMAL,
        n_thermal_traj=N_TH_TRAJ,
        nmax=nmax_for_alpha(alpha),
        det_min=0.0, det_max=0.0, npts=1,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0,
        T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_rep=0,
    )
    d, conv = ss.run_single(p, verbose=False)
    sx = d['sigma_x'][0]
    sy = d['sigma_y'][0]
    return sx, sy, conv['max_fock_leakage']


def main():
    out_path = os.path.join(SCRIPT_DIR, 'fig8_calibrations.h5')
    n_a, n_t = len(ALPHA_GRID), len(TILT_DEG)

    sx_arr = np.zeros((n_t, n_a))
    sy_arr = np.zeros((n_t, n_a))
    leak   = np.zeros((n_t, n_a))

    t0 = time.time()
    for j, tilt in enumerate(TILT_DEG):
        eta_j = ETA_LF * np.cos(np.radians(tilt))
        print(f"\n=== tilt {tilt:+.0f}°  η = {eta_j:.4f} ===")
        for i, a in enumerate(ALPHA_GRID):
            sx_arr[j, i], sy_arr[j, i], leak[j, i] = run_single_alpha_eta(a, eta_j)
            print(f"  |α|={a:4.1f}  σ_x={sx_arr[j,i]:+.3f}  "
                  f"σ_y={sy_arr[j,i]:+.3f}  |C|={np.hypot(sx_arr[j,i], sy_arr[j,i]):.3f}  "
                  f"leak={leak[j,i]:.1e}", flush=True)
    elapsed = time.time() - t0

    # Derived
    C_abs   = np.hypot(sx_arr, sy_arr)
    C_arg   = np.arctan2(sy_arr, sx_arr)
    # Unwrap along |α| axis (axis = 1) per tilt sheet
    phi0    = np.unwrap(C_arg, axis=1)
    # Reference phase at α = 0 set to zero
    phi0   -= phi0[:, :1]
    contrast_norm = C_abs / np.maximum(C_abs[:, :1], 1e-12)

    print(f"\n  total time {elapsed:.1f} s for {n_t}×{n_a} = {n_t*n_a} runs")

    with h5py.File(out_path, 'w') as f:
        f.create_dataset('alpha',         data=ALPHA_GRID)
        f.create_dataset('tilt_deg',      data=np.array(TILT_DEG))
        f.create_dataset('eta_per_tilt',  data=ETA_LF * np.cos(np.radians(TILT_DEG)))
        f.create_dataset('sigma_x',       data=sx_arr)
        f.create_dataset('sigma_y',       data=sy_arr)
        f.create_dataset('C_abs',         data=C_abs)
        f.create_dataset('C_arg_rad',     data=C_arg)
        f.create_dataset('phi0_rad',      data=phi0)
        f.create_dataset('contrast_norm', data=contrast_norm)
        f.create_dataset('max_fock_leakage', data=leak)
        f.attrs['eta_LF']     = ETA_LF
        f.attrs['omega_m']    = OMEGA_M
        f.attrs['omega_r']    = OMEGA_R
        f.attrs['n_pulses']   = N_PULSES
        f.attrs['n_thermal']  = N_THERMAL
        f.attrs['n_thermal_traj'] = N_TH_TRAJ
        f.attrs['code_version']   = ss.CODE_VERSION
        f.attrs['datetime_utc']   = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('phi0 unwrapped along |α| axis and zeroed at α=0; '
                            'contrast_norm normalised by |C(α=0)| per tilt sheet.')

    # Console summary for results-entry comparison
    print("  Hasse Fig 8 anchor numbers (engine vs published):")
    for j, tilt in enumerate(TILT_DEG):
        print(f"    tilt {tilt:+.0f}°: ϕ₀(α=8) = {phi0[j, -1]:+.3f} rad  "
              f"(Hasse ≈ ±2π = ±6.283); "
              f"C(α=0)/C(α=0) = {contrast_norm[j, 0]:.3f} (ref); "
              f"C(α=8)/C(α=0) = {contrast_norm[j, -1]:.3f} (Hasse ≈ 0)")
    print(f"  written → {out_path}")


if __name__ == '__main__':
    main()
