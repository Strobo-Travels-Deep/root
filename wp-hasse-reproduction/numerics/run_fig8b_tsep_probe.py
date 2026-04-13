#!/usr/bin/env python3
"""
run_fig8b_tsep_probe.py — Discriminator follow-up to WP-V results §2.

Re-runs the Fig 8b sweep at three t_sep_factor values:
    1.0     — the original (Ufree = None branch in stroboscopic_sweep.py)
    0.999   — Ufree active, near-stroboscopic
    1.001   — Ufree active, near-stroboscopic from the other side

Single tilt (0°), single n_thermal = 0.15. Same |α| grid.
If contrast decays at 0.999/1.001 but not at 1.0, the t_sep_factor = 1.0
shortcut is silently dropping the inter-pulse motional propagator.

Output: numerics/fig8b_tsep_probe.h5 + plots/fig8b_tsep_probe.png
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


ETA       = 0.397
OMEGA_M   = 1.3
OMEGA_R   = 0.3
N_PULSES  = 22
N_THERMAL = 0.15
N_TH_TRAJ = 32

ALPHA_GRID    = np.linspace(0.0, 8.0, 17)
TSEP_FACTORS  = (1.0, 0.999, 1.001)


def nmax_for_alpha(a):
    if a <= 1.0: return 30
    if a <= 3.0: return 50
    if a <= 5.0: return 80
    return 120


def run_point(alpha, tsep):
    p = dict(
        alpha=float(alpha), alpha_phase_deg=0.0,
        eta=ETA, omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES, n_thermal=N_THERMAL,
        n_thermal_traj=N_TH_TRAJ,
        nmax=nmax_for_alpha(alpha),
        det_min=0.0, det_max=0.0, npts=1,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=float(tsep),
        T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_rep=0,
    )
    d, _ = ss.run_single(p, verbose=False)
    return d['sigma_x'][0], d['sigma_y'][0]


def main():
    n_a, n_t = len(ALPHA_GRID), len(TSEP_FACTORS)
    sx = np.zeros((n_t, n_a)); sy = np.zeros((n_t, n_a))

    t0 = time.time()
    for j, tsep in enumerate(TSEP_FACTORS):
        print(f"\n=== t_sep_factor = {tsep} ===")
        for i, a in enumerate(ALPHA_GRID):
            sx[j, i], sy[j, i] = run_point(a, tsep)
            print(f"  |α|={a:4.1f}  σ_x={sx[j,i]:+.3f}  σ_y={sy[j,i]:+.3f}  "
                  f"|C|={np.hypot(sx[j,i], sy[j,i]):.3f}", flush=True)
    print(f"\n  total {time.time()-t0:.1f} s")

    C_abs = np.hypot(sx, sy)
    C_norm = C_abs / np.maximum(C_abs[:, :1], 1e-12)

    out_h5 = os.path.join(SCRIPT_DIR, 'fig8b_tsep_probe.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('alpha', data=ALPHA_GRID)
        f.create_dataset('t_sep_factor', data=np.array(TSEP_FACTORS))
        f.create_dataset('sigma_x', data=sx)
        f.create_dataset('sigma_y', data=sy)
        f.create_dataset('C_abs', data=C_abs)
        f.create_dataset('contrast_norm', data=C_norm)
        f.attrs['eta']        = ETA
        f.attrs['omega_m']    = OMEGA_M
        f.attrs['omega_r']    = OMEGA_R
        f.attrs['n_pulses']   = N_PULSES
        f.attrs['n_thermal']  = N_THERMAL
        f.attrs['n_thermal_traj'] = N_TH_TRAJ
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
    print(f"  wrote {out_h5}")

    # Plot
    fig, ax = plt.subplots(figsize=(5.6, 4.4))
    colors = {1.0: 'tab:red', 0.999: 'tab:blue', 1.001: 'tab:green'}
    for j, tsep in enumerate(TSEP_FACTORS):
        ax.plot(C_norm[j], ALPHA_GRID, marker='o',
                color=colors[tsep], label=f't_sep_factor = {tsep}')
    ax.set_xlabel('Contrast  $C / C(\\alpha=0)$')
    ax.set_ylabel(r'Displ. amplitude $|\alpha|$')
    ax.set_xlim(-0.05, 1.10); ax.set_ylim(0, ALPHA_GRID.max() * 1.05)
    ax.legend(fontsize=9)
    ax.set_title('Fig 8b discriminator: t_sep_factor 1.0 vs near-1\n'
                 r'($\eta=0.397$, $n_\mathrm{th}=0.15$, tilt 0°)', fontsize=10)
    ax.grid(alpha=0.3)
    out_png = os.path.join(PLOTS_DIR, 'fig8b_tsep_probe.png')
    fig.tight_layout(); fig.savefig(out_png, dpi=140); plt.close(fig)
    print(f"  wrote {out_png}")

    print("\nVerdict:")
    for j, tsep in enumerate(TSEP_FACTORS):
        print(f"  t_sep={tsep}:  C(α=0)={C_abs[j,0]:.3f}  "
              f"C(α=8)={C_abs[j,-1]:.3f}  C(α=8)/C(α=0)={C_norm[j,-1]:.3f}")


if __name__ == '__main__':
    main()
