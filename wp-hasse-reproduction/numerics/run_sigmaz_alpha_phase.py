#!/usr/bin/env python3
"""
run_sigmaz_alpha_phase.py — σ_z(|α|, ϑ₀) scan (engine native readout).

Direct probe: read the engine's σ_z at each (|α|, ϑ₀) point with no
basis rotation and no |C|-style contrast definition. Returns:

  σ_z(|α|, ϑ₀)                   2D map
  σ_z fringe amplitude(|α|)      = (max_ϑ₀ σ_z − min_ϑ₀ σ_z) / 2
  σ_z mean(|α|)                  = mean over ϑ₀
  σ_z std(|α|)                   = std over ϑ₀

Asks the question: does the engine's σ_z (i) depend on ϑ₀ at all, and
(ii) lose its ϑ₀-amplitude as |α| grows? The latter is the σ_z analogue
of Hasse's Fig 8b contrast decay; the former is a sanity check on
whether the engine carries motional-phase information into the spin
observable in its native frame at all.

Three configurations, mirroring the t_sep_factor probe:
    t_sep_factor = 1.0     (Ufree = None)
    t_sep_factor = 0.999   (Ufree active)
    + an n_thermal = 0 / 0.15 toggle on the t_sep = 1.0 sheet to
      separate thermal smearing from the underlying ϑ₀-dependence.

Output:
    numerics/sigmaz_alpha_phase.h5
    plots/sigmaz_alpha_phase_maps.png
    plots/sigmaz_amplitude_vs_alpha.png
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
N_TH_TRAJ = 24

ALPHA_GRID  = np.linspace(0.0, 8.0, 17)
THETA0_GRID = np.linspace(0.0, 2.0 * np.pi, 32, endpoint=False)

# Each row: (label, t_sep_factor, n_thermal)
CONFIGS = (
    ('tsep1.0_nth0.00',   1.000, 0.00),
    ('tsep1.0_nth0.15',   1.000, 0.15),
    ('tsep0.999_nth0.00', 0.999, 0.00),
)


def nmax_for_alpha(a):
    if a <= 1.0: return 30
    if a <= 3.0: return 50
    if a <= 5.0: return 80
    return 120


def run_point(alpha, theta0_rad, tsep, n_thermal):
    p = dict(
        alpha=float(alpha), alpha_phase_deg=float(np.degrees(theta0_rad)),
        eta=ETA, omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES,
        n_thermal=float(n_thermal),
        n_thermal_traj=(N_TH_TRAJ if n_thermal > 0 else 1),
        nmax=nmax_for_alpha(alpha),
        det_min=0.0, det_max=0.0, npts=1,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=float(tsep),
        T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_rep=0,
    )
    d, _ = ss.run_single(p, verbose=False)
    return d['sigma_z'][0], d['sigma_x'][0], d['sigma_y'][0], d['nbar'][0]


def main():
    n_a, n_p, n_c = len(ALPHA_GRID), len(THETA0_GRID), len(CONFIGS)
    sz_3d = np.zeros((n_c, n_a, n_p))
    sx_3d = np.zeros((n_c, n_a, n_p))
    sy_3d = np.zeros((n_c, n_a, n_p))
    nb_3d = np.zeros((n_c, n_a, n_p))

    t0 = time.time()
    for c, (label, tsep, nth) in enumerate(CONFIGS):
        print(f"\n=== [{c+1}/{n_c}] {label}  (t_sep={tsep}, n_th={nth}) ===")
        for i, a in enumerate(ALPHA_GRID):
            for j, th in enumerate(THETA0_GRID):
                sz, sx, sy, nb = run_point(a, th, tsep, nth)
                sz_3d[c, i, j] = sz
                sx_3d[c, i, j] = sx
                sy_3d[c, i, j] = sy
                nb_3d[c, i, j] = nb
            sz_row = sz_3d[c, i]
            print(f"  |α|={a:4.1f}  ⟨σ_z⟩ ∈ [{sz_row.min():+.3f}, {sz_row.max():+.3f}]  "
                  f"amp/2={(sz_row.max()-sz_row.min())/2:.3f}  "
                  f"mean={sz_row.mean():+.3f}", flush=True)
    elapsed = time.time() - t0
    print(f"\n  total {elapsed:.1f} s for {n_c}×{n_a}×{n_p} = {n_c*n_a*n_p} runs")

    # Derived 1D summaries vs |α|
    sz_amp  = (sz_3d.max(axis=2) - sz_3d.min(axis=2)) / 2.0   # (n_c, n_a)
    sz_mean = sz_3d.mean(axis=2)
    sz_std  = sz_3d.std(axis=2)

    # Write HDF5
    out_h5 = os.path.join(SCRIPT_DIR, 'sigmaz_alpha_phase.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('alpha',       data=ALPHA_GRID)
        f.create_dataset('theta0_rad',  data=THETA0_GRID)
        f.create_dataset('config_label', data=np.array([c[0] for c in CONFIGS], dtype='S'))
        f.create_dataset('t_sep_factor', data=np.array([c[1] for c in CONFIGS]))
        f.create_dataset('n_thermal',    data=np.array([c[2] for c in CONFIGS]))
        f.create_dataset('sigma_z',     data=sz_3d)   # (n_c, n_a, n_phi)
        f.create_dataset('sigma_x',     data=sx_3d)
        f.create_dataset('sigma_y',     data=sy_3d)
        f.create_dataset('nbar',        data=nb_3d)
        f.create_dataset('sz_amplitude', data=sz_amp)
        f.create_dataset('sz_mean',      data=sz_mean)
        f.create_dataset('sz_std',       data=sz_std)
        f.attrs['eta']      = ETA
        f.attrs['omega_m']  = OMEGA_M
        f.attrs['omega_r']  = OMEGA_R
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = (
            'sz_amplitude = (max_ϑ₀ σ_z − min_ϑ₀ σ_z) / 2 per config, per |α|; '
            'σ_z is the engine native readout (no basis rotation).'
        )
    print(f"  wrote {out_h5}")

    # === Plot 1: heatmaps σ_z(|α|, ϑ₀) per config ===
    fig, axs = plt.subplots(1, n_c, figsize=(4.2 * n_c, 4.0),
                            sharex=True, sharey=True, constrained_layout=True)
    if n_c == 1:
        axs = [axs]
    vmax = float(np.max(np.abs(sz_3d)))
    for c, (label, tsep, nth) in enumerate(CONFIGS):
        im = axs[c].imshow(
            sz_3d[c],
            origin='lower', aspect='auto',
            extent=[THETA0_GRID[0], THETA0_GRID[-1] + (THETA0_GRID[1]-THETA0_GRID[0]),
                    ALPHA_GRID[0], ALPHA_GRID[-1]],
            cmap='RdBu_r', vmin=-vmax, vmax=+vmax,
        )
        axs[c].set_xlabel(r'$\vartheta_0$ (rad)')
        axs[c].set_xticks([0, np.pi, 2 * np.pi])
        axs[c].set_xticklabels(['0', r'$\pi$', r'$2\pi$'])
        axs[c].set_title(f't_sep={tsep},  n_th={nth}', fontsize=10)
    axs[0].set_ylabel(r'$|\alpha|$')
    cb = fig.colorbar(im, ax=axs, shrink=0.85, pad=0.02)
    cb.set_label(r'$\langle\sigma_z\rangle$ (engine native, no basis rotation)')
    fig.suptitle(r'Engine-native $\langle\sigma_z\rangle(|\alpha|, \vartheta_0)$ '
                 r'— direct readout, $\eta=0.397$', fontsize=11)
    out_png = os.path.join(PLOTS_DIR, 'sigmaz_alpha_phase_maps.png')
    fig.savefig(out_png, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out_png}")

    # === Plot 2: σ_z amplitude vs |α| (the σ_z analogue of contrast loss) ===
    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    colors = ('tab:blue', 'tab:red', 'tab:green')
    for c, (label, tsep, nth) in enumerate(CONFIGS):
        ax.plot(ALPHA_GRID, sz_amp[c], 'o-', color=colors[c],
                label=f't_sep={tsep},  n_th={nth}')
    ax.set_xlabel(r'Motional amplitude $|\alpha|$')
    ax.set_ylabel(r'$\sigma_z$ fringe amplitude  $(\max_{\vartheta_0} - \min_{\vartheta_0}) / 2$')
    ax.set_xlim(0, ALPHA_GRID.max() * 1.02)
    ax.set_ylim(-0.02, max(sz_amp.max() * 1.15, 0.05))
    ax.axhline(0, color='k', lw=0.4)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    ax.set_title(r'Engine-native $\sigma_z$ amplitude vs $|\alpha|$  '
                 r'(σ_z analogue of Hasse Fig 8b)', fontsize=10)
    out_png = os.path.join(PLOTS_DIR, 'sigmaz_amplitude_vs_alpha.png')
    fig.tight_layout(); fig.savefig(out_png, dpi=140); plt.close(fig)
    print(f"  wrote {out_png}")

    # Console summary
    print("\nSummary (sz_amplitude = (max_ϑ₀ − min_ϑ₀) σ_z / 2):")
    for c, (label, tsep, nth) in enumerate(CONFIGS):
        amp0 = sz_amp[c, 0]; amp_max = sz_amp[c].max()
        print(f"  {label:24s}  amp(α=0)={amp0:.4f}  "
              f"max amp over α={amp_max:.4f}  amp(α=8)={sz_amp[c,-1]:.4f}")


if __name__ == '__main__':
    main()
