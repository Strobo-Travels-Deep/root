#!/usr/bin/env python3
"""
run_lock_tolerance_wedge.py — σ_z fringe amplitude on the (t_sep_factor, |α|) plane.

Builds on `run_sigmaz_alpha_phase.py`: at each (t_sep_factor, |α|) point
we sweep ϑ₀ ∈ [0, 2π) and record σ_z, then collapse to

    sz_amplitude(t_sep, |α|) = (max_ϑ₀ σ_z − min_ϑ₀ σ_z) / 2

This is the cleanest engine-native probe of stroboscopic lock tolerance:
identically zero on the t_sep = 1.0 axis, growing wedge-like as the
mismatch (t_sep − 1) couples motional phase into σ_z.

Compares against Hasse's experimentally measured Δω_m/ω_m ≲ 0.7 % bound.

Output:
    numerics/lock_tolerance_wedge.h5
    plots/lock_tolerance_wedge.png        — heatmap + slices
    plots/lock_tolerance_curves.png       — 1D cuts vs t_sep, vs |α|
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

# Grid choices
TSEP_GRID   = np.linspace(0.98, 1.02, 21)        # ±2%, 0.2% step (Hasse: 0.7% bound)
ALPHA_GRID  = np.linspace(0.0, 8.0, 17)
THETA0_GRID = np.linspace(0.0, 2.0 * np.pi, 24, endpoint=False)


def nmax_for_alpha(a):
    if a <= 1.0: return 30
    if a <= 3.0: return 50
    if a <= 5.0: return 80
    return 120


def run_point(alpha, theta0_rad, tsep):
    p = dict(
        alpha=float(alpha), alpha_phase_deg=float(np.degrees(theta0_rad)),
        eta=ETA, omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES,
        n_thermal=0.0, n_thermal_traj=1,
        nmax=nmax_for_alpha(alpha),
        det_min=0.0, det_max=0.0, npts=1,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=float(tsep),
        T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_rep=0,
    )
    d, _ = ss.run_single(p, verbose=False)
    return d['sigma_z'][0]


def main():
    n_t, n_a, n_p = len(TSEP_GRID), len(ALPHA_GRID), len(THETA0_GRID)
    print(f"Grid: {n_t} × {n_a} × {n_p} = {n_t * n_a * n_p} runs")

    sz_3d = np.zeros((n_t, n_a, n_p))

    t0 = time.time()
    for k, tsep in enumerate(TSEP_GRID):
        eps_pct = (tsep - 1.0) * 100
        for i, a in enumerate(ALPHA_GRID):
            for j, th in enumerate(THETA0_GRID):
                sz_3d[k, i, j] = run_point(a, th, tsep)
        rng = sz_3d[k].max(axis=1) - sz_3d[k].min(axis=1)
        print(f"  t_sep={tsep:.4f}  (ε={eps_pct:+.2f}%)  "
              f"max sz_amp over α: {(rng/2).max():.4f}  "
              f"@α={ALPHA_GRID[(rng/2).argmax()]:.1f}", flush=True)
    elapsed = time.time() - t0
    print(f"\n  total {elapsed:.1f} s")

    sz_amp = (sz_3d.max(axis=2) - sz_3d.min(axis=2)) / 2.0   # (n_t, n_a)
    sz_mean = sz_3d.mean(axis=2)
    eps_pct = (TSEP_GRID - 1.0) * 100

    out_h5 = os.path.join(SCRIPT_DIR, 'lock_tolerance_wedge.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('t_sep_factor', data=TSEP_GRID)
        f.create_dataset('eps_percent',  data=eps_pct)
        f.create_dataset('alpha',        data=ALPHA_GRID)
        f.create_dataset('theta0_rad',   data=THETA0_GRID)
        f.create_dataset('sigma_z',      data=sz_3d)
        f.create_dataset('sz_amplitude', data=sz_amp)
        f.create_dataset('sz_mean',      data=sz_mean)
        f.attrs['eta']      = ETA
        f.attrs['omega_m']  = OMEGA_M
        f.attrs['omega_r']  = OMEGA_R
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('sz_amplitude = (max_ϑ₀ σ_z − min_ϑ₀ σ_z) / 2; '
                            't_sep_factor = ω_pulse / ω_m; '
                            'eps = (t_sep − 1) × 100%')
    print(f"  wrote {out_h5}")

    # === Plot 1: heatmap (t_sep ε, |α|) of sz_amplitude ===
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6),
                            gridspec_kw=dict(width_ratios=[1.4, 1]),
                            constrained_layout=True)

    ax = axs[0]
    vmax = float(sz_amp.max())
    im = ax.imshow(
        sz_amp.T,                              # rows: |α|, cols: ε
        origin='lower', aspect='auto',
        extent=[eps_pct[0], eps_pct[-1], ALPHA_GRID[0], ALPHA_GRID[-1]],
        cmap='magma', vmin=0, vmax=vmax,
    )
    ax.axvline(0, color='cyan', lw=0.8, ls='--', alpha=0.6, label='perfect lock')
    # Hasse's experimentally measured tolerance ≲ 0.7%
    for x in (-0.7, +0.7):
        ax.axvline(x, color='white', lw=0.6, ls=':', alpha=0.7)
    ax.text(0.7, ALPHA_GRID[-1] * 0.95, '  Hasse Δω/ω ≲ 0.7%',
            color='white', fontsize=8, ha='left', va='top')
    ax.text(-0.7, ALPHA_GRID[-1] * 0.95, 'Hasse Δω/ω ≲ 0.7%  ',
            color='white', fontsize=8, ha='right', va='top')
    ax.set_xlabel(r'Stroboscopic mismatch  $\epsilon = (t_\mathrm{sep}/T_m - 1) \times 100\%$')
    ax.set_ylabel(r'$|\alpha|$')
    ax.set_title(r'$\sigma_z$ fringe amplitude on $(t_\mathrm{sep},\,|\alpha|)$  '
                 r'(engine native, $\eta=0.397$)', fontsize=10)
    cb = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cb.set_label(r'$(\max_{\vartheta_0} - \min_{\vartheta_0}) \langle\sigma_z\rangle / 2$')

    # Slice panel: sz_amp vs ε at selected |α|
    ax = axs[1]
    alpha_picks = [1.0, 3.0, 5.0, 8.0]
    cmap = plt.get_cmap('viridis')
    for k, a_target in enumerate(alpha_picks):
        i = int(np.argmin(np.abs(ALPHA_GRID - a_target)))
        ax.plot(eps_pct, sz_amp[:, i],
                color=cmap(k / max(1, len(alpha_picks) - 1)),
                marker='o', ms=3,
                label=fr'$|\alpha|={ALPHA_GRID[i]:.1f}$')
    ax.axvline(0, color='k', lw=0.5, ls='--', alpha=0.6)
    for x in (-0.7, +0.7):
        ax.axvline(x, color='gray', lw=0.4, ls=':', alpha=0.6)
    ax.set_xlabel(r'$\epsilon$ (%)')
    ax.set_ylabel(r'$\sigma_z$ fringe amplitude')
    ax.set_title(r'Cuts at fixed $|\alpha|$', fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    out_png = os.path.join(PLOTS_DIR, 'lock_tolerance_wedge.png')
    fig.savefig(out_png, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out_png}")

    # === Plot 2: companion 1D — sz_amp vs |α| at fixed ε; and ε at fixed |α| (log) ===
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), constrained_layout=True)

    # Panel A: vs |α|, several ε
    ax = axs[0]
    eps_picks_pct = [0.0, 0.2, 0.5, 1.0, 2.0]
    for k, ep in enumerate(eps_picks_pct):
        kk = int(np.argmin(np.abs(eps_pct - ep)))
        ax.plot(ALPHA_GRID, sz_amp[kk],
                color=cmap(k / max(1, len(eps_picks_pct) - 1)),
                marker='o', ms=3, label=fr'$\epsilon={eps_pct[kk]:+.2f}\%$')
    ax.set_xlabel(r'$|\alpha|$')
    ax.set_ylabel(r'$\sigma_z$ fringe amplitude')
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    ax.set_title('vs amplitude, several mismatches', fontsize=10)

    # Panel B: vs |ε|, several |α|, log axes — look for power law
    ax = axs[1]
    pos_mask = eps_pct > 0
    for k, a_target in enumerate(alpha_picks):
        i = int(np.argmin(np.abs(ALPHA_GRID - a_target)))
        ax.loglog(eps_pct[pos_mask], np.maximum(sz_amp[pos_mask, i], 1e-6),
                  color=cmap(k / max(1, len(alpha_picks) - 1)),
                  marker='o', ms=3,
                  label=fr'$|\alpha|={ALPHA_GRID[i]:.1f}$')
    ax.set_xlabel(r'$\epsilon$ (%, log)')
    ax.set_ylabel(r'$\sigma_z$ fringe amplitude (log)')
    ax.grid(alpha=0.3, which='both'); ax.legend(fontsize=8)
    ax.set_title('Power-law check (positive ε side)', fontsize=10)

    out_png = os.path.join(PLOTS_DIR, 'lock_tolerance_curves.png')
    fig.savefig(out_png, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out_png}")

    # Console summary at Hasse 0.7% bound
    print("\nAt Hasse-quoted lock tolerance ε = ±0.7%:")
    for ep_target in (-0.7, 0.7):
        kk = int(np.argmin(np.abs(eps_pct - ep_target)))
        print(f"  ε={eps_pct[kk]:+.2f}%:  sz_amp at α=3 = {sz_amp[kk, 6]:.4f}, "
              f"α=5 = {sz_amp[kk, 10]:.4f}, α=8 = {sz_amp[kk, 16]:.4f}")
    print(f"At ε=0:  sz_amp identically zero (max = {sz_amp[10].max():.2e})")


if __name__ == '__main__':
    main()
