#!/usr/bin/env python3
"""
run_omega_alpha_scan.py — Round 3 diagnostic: (Ω, |α|) → contrast surface.

At Hasse-matched (N=30, δt=0.13·T_m, intra_pulse_motion=True), sweep:
    Ω   ∈ [0.04, 0.20]   (12 points)
    |α| ∈ [0, 8]          (17 points)

For each point: read |C| = √(σ_x² + σ_y²) and σ_z. Goal: locate any
Ω regime where C(α) decays monotonically (Hasse Fig 8b shape) instead
of showing revivals.

Output: numerics/omega_alpha_scan.h5 + plots/omega_alpha_scan.png
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
T_M       = 2 * np.pi / OMEGA_M
DELTA_T   = 0.13 * T_M
N_PULSES  = 30
N_THERMAL = 0.0       # use pure state for cleaner diagnosis
N_TH_TRAJ = 1

OMEGA_GRID = np.linspace(0.04, 0.20, 12)
ALPHA_GRID = np.linspace(0.0, 8.0, 17)


def nmax_for_alpha(a):
    if a <= 1.0: return 30
    if a <= 3.0: return 60
    if a <= 5.0: return 100
    return 140


def run_point(omega, alpha):
    p = dict(
        alpha=float(alpha), alpha_phase_deg=0.0,
        eta=ETA, omega_m=OMEGA_M, omega_r=float(omega),
        n_pulses=N_PULSES, n_thermal=N_THERMAL, n_thermal_traj=N_TH_TRAJ,
        nmax=nmax_for_alpha(alpha),
        det_min=0.0, det_max=0.0, npts=1,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0, T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_rep=0,
        mw_pi2_phase_deg=0.0, intra_pulse_motion=True,
        delta_t_us=DELTA_T, ac_phase_deg=0.0,
    )
    d, _ = ss.run_single(p, verbose=False)
    return d['sigma_x'][0], d['sigma_y'][0], d['sigma_z'][0]


def main():
    n_o, n_a = len(OMEGA_GRID), len(ALPHA_GRID)
    print(f"Grid: {n_o} × {n_a} = {n_o*n_a} runs")
    print(f"  N={N_PULSES}, δt={DELTA_T:.3f}, ω_m·δt={OMEGA_M*DELTA_T:.3f} rad")

    sx = np.zeros((n_o, n_a)); sy = np.zeros((n_o, n_a)); sz = np.zeros((n_o, n_a))

    t0 = time.time()
    for k, omega in enumerate(OMEGA_GRID):
        for i, a in enumerate(ALPHA_GRID):
            sx[k,i], sy[k,i], sz[k,i] = run_point(omega, a)
        # Compute monotonicity score: sum of sign-flips in d|C|/dα
        Cabs = np.hypot(sx[k], sy[k])
        signs = np.sign(np.diff(Cabs))
        flips = int(np.sum(np.diff(signs) != 0))
        Cabs0 = Cabs[0]; Cabs8 = Cabs[-1]
        szmax0 = sz[k, 0]
        print(f"  Ω={omega:.4f}  σ_z(α=0)={szmax0:+.3f}  |C|(α=0)={Cabs0:.3f}  "
              f"|C|(α=8)={Cabs8:.3f}  flips={flips}", flush=True)
    elapsed = time.time() - t0
    print(f"  total {elapsed:.1f} s")

    Cabs = np.hypot(sx, sy)
    Cnorm = Cabs / np.maximum(Cabs[:, :1], 1e-12)

    out_h5 = os.path.join(SCRIPT_DIR, 'omega_alpha_scan.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('omega', data=OMEGA_GRID)
        f.create_dataset('alpha', data=ALPHA_GRID)
        f.create_dataset('sigma_x', data=sx)
        f.create_dataset('sigma_y', data=sy)
        f.create_dataset('sigma_z', data=sz)
        f.create_dataset('C_abs',   data=Cabs)
        f.create_dataset('C_norm',  data=Cnorm)
        f.attrs['eta']=ETA; f.attrs['omega_m']=OMEGA_M
        f.attrs['delta_t_us']=DELTA_T; f.attrs['n_pulses']=N_PULSES
        f.attrs['code_version']=ss.CODE_VERSION
        f.attrs['datetime_utc']=datetime.now(timezone.utc).isoformat()

    # Plot: 2 panels — heatmap of |C|(Ω, α) and σ_z(Ω, α)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), constrained_layout=True)
    for ax, M, title, cmap, vlim in [
        (axs[0], Cabs, r'$|C| = \sqrt{\sigma_x^2 + \sigma_y^2}$', 'magma',  None),
        (axs[1], sz,   r'$\langle\sigma_z\rangle$',                'RdBu_r', 1.0)]:
        v = vlim if vlim else float(np.abs(M).max())
        kw = dict(origin='lower', aspect='auto',
                  extent=[ALPHA_GRID[0], ALPHA_GRID[-1],
                          OMEGA_GRID[0], OMEGA_GRID[-1]])
        if title.startswith(r'$\langle'):
            im = ax.imshow(M, cmap=cmap, vmin=-v, vmax=+v, **kw)
        else:
            im = ax.imshow(M, cmap=cmap, vmin=0, vmax=+v, **kw)
        ax.set_xlabel(r'$|\alpha|$'); ax.set_ylabel(r'$\Omega$')
        ax.set_title(title, fontsize=10)
        fig.colorbar(im, ax=ax, shrink=0.85)
    fig.suptitle(rf'$(\Omega,\,|\alpha|)$ at Hasse-matched $N={N_PULSES}$, '
                 rf'$\delta t/T_m=0.13$  '
                 f'(engine v{ss.CODE_VERSION})', fontsize=10)
    out_png = os.path.join(PLOTS_DIR, 'omega_alpha_scan.png')
    fig.savefig(out_png, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out_png}")

    # Companion 1D: |C|(α) curves at all Ω
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    cmap = plt.get_cmap('viridis')
    for k, omega in enumerate(OMEGA_GRID):
        ax.plot(ALPHA_GRID, Cabs[k], color=cmap(k/(n_o-1)),
                marker='o', ms=3, label=f'Ω={omega:.3f}')
    ax.set_xlabel(r'$|\alpha|$'); ax.set_ylabel(r'$|C|$')
    ax.set_ylim(-0.02, 1.02); ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    ax.set_title(rf'$|C|(|\alpha|)$ at swept $\Omega$  (Hasse-matched $N$, $\delta t$)',
                 fontsize=10)
    out_png = os.path.join(PLOTS_DIR, 'omega_alpha_curves.png')
    fig.tight_layout(); fig.savefig(out_png, dpi=140); plt.close(fig)
    print(f"  wrote {out_png}")


if __name__ == '__main__':
    main()
