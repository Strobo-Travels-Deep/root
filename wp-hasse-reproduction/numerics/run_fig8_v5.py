#!/usr/bin/env python3
"""
run_fig8_v5.py — Hasse Fig 8 with Hasse's OWN contrast definition.

Per refs/vpaula_hologram_2026_02_25.ipynb (cells 9, 14, 25, 26):

    contrast_z = (max_scan σ_z − min_scan σ_z) / 2
    contrast_x, contrast_y analogous.

where the scan is a detuning (or analysis-phase) scan. This is the
Ramsey fringe amplitude over the scan variable, NOT the modulus of
the final-state complex coherence at fixed detuning (which was my
erroneous v0.8 / v2 / v3 definition).

For each (|α|, tilt) we run a detuning scan, record (σ_x, σ_y, σ_z)
at end of train for each detuning point, then extract Hasse's three
contrast_* numbers. Output the family vs |α|.

Engine config (v0.9.1 Hasse-matched + centered + fast-AOM timing):
    N = 22  (≈ Hasse's fast-AOM N ≈ 23)
    δt auto-derived so N·Ω_eff·δt = π/2   (matches Hasse fast-AOM regime)
    intra_pulse_motion = True   (D1 fix)
    center_pulses_at_phase = True   (v0.9.1 convention fix)
    mw_pi2_phase_deg = 0.0   (D3 fix)
    Ω/(2π) = 0.3 MHz (engine angular units = 0.3)
    ω_m/(2π) = 1.3 MHz  (engine angular units = 1.3)
    n_thermal = 0.15

Output: numerics/fig8_calibrations_v5.h5
        plots/fig8b_contrast_v5.png
"""

import os, sys, time
from datetime import datetime, timezone
import numpy as np
import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts'))
PLOTS_DIR  = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
sys.path.insert(0, ENGINE_DIR)
import stroboscopic_sweep as ss


ETA_LF      = 0.397
TILT_DEG    = (-5.0, 0.0, +5.0)
ALPHA_GRID  = np.linspace(0.0, 8.0, 17)
OMEGA_M     = 1.3
OMEGA_R     = 0.3                  # Hasse Table II exact
N_PULSES    = 22
N_THERMAL   = 0.15
N_TH_TRAJ   = 24

N_DET       = 41                   # detuning grid size per α
DET_REL_MAX = 6.0 / OMEGA_M        # ±6 MHz/(2π) / ω_m  dimensionless


def nmax_for_alpha(alpha):
    a = float(alpha)
    if a <= 1.0: return 30
    if a <= 3.0: return 60
    if a <= 5.0: return 100
    return 140


def run_detuning_scan(alpha, eta):
    """Returns (σ_x, σ_y, σ_z) arrays of shape (n_det,) at end of train."""
    p = dict(
        alpha=float(alpha), alpha_phase_deg=0.0,
        eta=float(eta), omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES, n_thermal=N_THERMAL, n_thermal_traj=N_TH_TRAJ,
        nmax=nmax_for_alpha(alpha),
        det_min=-DET_REL_MAX, det_max=+DET_REL_MAX, npts=N_DET,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0, T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_rep=0,
        mw_pi2_phase_deg=0.0,
        intra_pulse_motion=True,
        center_pulses_at_phase=True,
    )
    d, conv = ss.run_single(p, verbose=False)
    sx = np.array(d['sigma_x']); sy = np.array(d['sigma_y']); sz = np.array(d['sigma_z'])
    return sx, sy, sz, conv['max_fock_leakage']


def main():
    out_path = os.path.join(SCRIPT_DIR, 'fig8_calibrations_v5.h5')
    n_a, n_t = len(ALPHA_GRID), len(TILT_DEG)

    print(f"Hasse Fig 8 v5 — engine v{ss.CODE_VERSION}")
    print(f"  Ω/(2π)={OMEGA_R:.3f} MHz, ω_m/(2π)={OMEGA_M:.3f} MHz, η={ETA_LF:.3f}")
    print(f"  N={N_PULSES}, fast-AOM regime (engine auto-derives δt from π/2 budget)")
    print(f"  detuning scan: ±{DET_REL_MAX*OMEGA_M:.1f} MHz/(2π), {N_DET} points per α")
    print(f"  CONTRAST = (max_δ σ_z − min_δ σ_z)/2  — Hasse notebook convention")
    print()

    # Storage: full sigma arrays for each (tilt, alpha) and their extracted contrasts
    det_rel = np.linspace(-DET_REL_MAX, +DET_REL_MAX, N_DET)
    sx_full = np.zeros((n_t, n_a, N_DET))
    sy_full = np.zeros((n_t, n_a, N_DET))
    sz_full = np.zeros((n_t, n_a, N_DET))
    leak    = np.zeros((n_t, n_a))
    cz = np.zeros((n_t, n_a))
    cy = np.zeros((n_t, n_a))
    cx = np.zeros((n_t, n_a))

    t0 = time.time()
    for j, tilt in enumerate(TILT_DEG):
        eta_j = ETA_LF * np.cos(np.radians(tilt))
        print(f"=== tilt {tilt:+.0f}°  η={eta_j:.4f} ===")
        for i, a in enumerate(ALPHA_GRID):
            sx, sy, sz, lk = run_detuning_scan(a, eta_j)
            sx_full[j, i] = sx; sy_full[j, i] = sy; sz_full[j, i] = sz
            leak[j, i] = lk
            cx[j, i] = 0.5 * (sx.max() - sx.min())
            cy[j, i] = 0.5 * (sy.max() - sy.min())
            cz[j, i] = 0.5 * (sz.max() - sz.min())
            print(f"  |α|={a:4.1f}  contrast_x={cx[j,i]:.3f}  "
                  f"contrast_y={cy[j,i]:.3f}  contrast_z={cz[j,i]:.3f}  "
                  f"leak={lk:.1e}", flush=True)
    elapsed = time.time() - t0
    print(f"\n  total {elapsed:.1f} s for {n_t}×{n_a}×{N_DET} = {n_t*n_a*N_DET} detuning points")

    # Normalise contrast by α=0 value (what Hasse Fig 8b plots)
    cz_norm = cz / np.maximum(cz[:, :1], 1e-12)
    cy_norm = cy / np.maximum(cy[:, :1], 1e-12)

    with h5py.File(out_path, 'w') as f:
        f.create_dataset('alpha',          data=ALPHA_GRID)
        f.create_dataset('tilt_deg',       data=np.array(TILT_DEG))
        f.create_dataset('detuning_rel',   data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi', data=det_rel * OMEGA_M)
        f.create_dataset('sigma_x',        data=sx_full)
        f.create_dataset('sigma_y',        data=sy_full)
        f.create_dataset('sigma_z',        data=sz_full)
        f.create_dataset('contrast_x',     data=cx)
        f.create_dataset('contrast_y',     data=cy)
        f.create_dataset('contrast_z',     data=cz)
        f.create_dataset('contrast_z_norm',data=cz_norm)
        f.create_dataset('contrast_y_norm',data=cy_norm)
        f.create_dataset('max_fock_leakage',data=leak)
        f.attrs['eta_LF']    = ETA_LF
        f.attrs['omega_m']   = OMEGA_M
        f.attrs['omega_r']   = OMEGA_R
        f.attrs['n_pulses']  = N_PULSES
        f.attrs['n_thermal'] = N_THERMAL
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('Hasse Fig 8 v5 — contrast_* = (max_δ σ_* − min_δ σ_*)/2 '
                            'over ±6 MHz/(2π) detuning scan. Engine v0.9.1 with '
                            'intra_pulse_motion + centered pulses + MW π/2.')

    TILT_COLORS = {-5.0: 'tab:green', 0.0: 'tab:blue', +5.0: 'tab:orange'}

    # Fig 8b in Hasse's convention
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), constrained_layout=True)

    ax = axs[0]
    for j, tilt in enumerate(TILT_DEG):
        c = TILT_COLORS.get(float(tilt), 'k')
        ax.plot(cz[j], ALPHA_GRID, marker='o', ms=3, color=c,
                label=fr'tilt {tilt:+.0f}°')
    ax.set_xlabel(r'contrast$_z$  $(\max_\delta - \min_\delta)\sigma_z / 2$')
    ax.set_ylabel(r'$|\alpha|$'); ax.set_xlim(-0.02, 1.05); ax.set_ylim(0, 8.2)
    ax.grid(alpha=0.3); ax.legend(fontsize=9)
    ax.set_title(r'Hasse Fig 8b — $\sigma_z$ contrast vs $|\alpha|$', fontsize=10)

    ax = axs[1]
    for j, tilt in enumerate(TILT_DEG):
        c = TILT_COLORS.get(float(tilt), 'k')
        ax.plot(cz_norm[j], ALPHA_GRID, marker='o', ms=3, color=c,
                label=fr'tilt {tilt:+.0f}°')
    ax.set_xlabel(r'normalised: contrast$_z$ / contrast$_z(\alpha=0)$')
    ax.set_ylabel(r'$|\alpha|$'); ax.set_xlim(-0.02, 1.10); ax.set_ylim(0, 8.2)
    ax.grid(alpha=0.3); ax.legend(fontsize=9)
    ax.set_title(r'Normalised — direct comparison to Hasse Fig 8b', fontsize=10)

    fig.suptitle(
        f'engine v{ss.CODE_VERSION}, N={N_PULSES}, Ω/(2π)=0.3 MHz, n_th=0.15, '
        r'detuning scan ±6 MHz/(2$\pi$)', fontsize=10)
    out = os.path.join(PLOTS_DIR, 'fig8b_contrast_v5.png')
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")

    # Diagnostic: look at contrast_z curve for monotonicity
    print()
    print("Hasse anchor: contrast_z(α=0) ≈ 1, contrast_z(α=8) → 0 (smooth decay)")
    for j, tilt in enumerate(TILT_DEG):
        flips = int(np.sum(np.diff(np.sign(np.diff(cz[j]))) != 0))
        print(f"  tilt {tilt:+.0f}°: contrast_z(α=0)={cz[j,0]:.3f}  "
              f"contrast_z(α=8)={cz[j,-1]:.3f}  "
              f"normalised(α=8)={cz_norm[j,-1]:.3f}  flips={flips}")


if __name__ == '__main__':
    main()
