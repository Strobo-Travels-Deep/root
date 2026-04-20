#!/usr/bin/env python3
"""
plot_fig6_coherences.py — Spin-coherence maps for the Hasse Fig 6 parameters.

Reads fig6_alpha3_v5.h5 (produced by run_fig6_v5.py) and plots:
    fig6c_sigma_x_v5.png     ⟨σ_x⟩ over (ϑ₀, φ_AC)
    fig6c_sigma_y_v5.png     ⟨σ_y⟩ over (ϑ₀, φ_AC)
    fig6c_coh_abs_v5.png     |C| = √(σ_x² + σ_y²)
    fig6c_coh_arg_v5.png     arg(C) = atan2(σ_y, σ_x)  (degrees)

The arg(C) panel is alpha-masked by |C| so noise-dominated regions
(|C| → 0) don't swamp the figure visually.
"""
from __future__ import annotations

import argparse
import os

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))


def heatmap(map_arr, theta0_grid, phi_grid, title, fname, cmap, ylabel,
            vlim=None, symmetric=True, alpha_map=None):
    cuts_theta = (np.pi / 4, np.pi / 2, np.pi)
    cuts_phi = (np.pi / 4, np.pi / 2, np.pi)
    cut_styles = ('lightgray', 'dimgray', 'black')

    fig = plt.figure(figsize=(7.0, 5.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 3], height_ratios=[3, 1],
                          hspace=0.30, wspace=0.30)
    if vlim is None:
        vlim = max(0.9, float(np.abs(map_arr).max()))
    if symmetric:
        vmin, vmax = -vlim, +vlim
    else:
        vmin, vmax = float(map_arr.min()), float(map_arr.max())

    ax_map = fig.add_subplot(gs[0, 1])
    img_kwargs = dict(origin='lower',
                      extent=[theta0_grid[0], theta0_grid[-1],
                              phi_grid[0], phi_grid[-1]],
                      aspect='auto', cmap=cmap, vmin=vmin, vmax=vmax)
    if alpha_map is not None:
        # Normalize alpha to [0, 1] by |C| saturation.
        a_norm = np.clip(alpha_map / max(1e-12, float(alpha_map.max())), 0.0, 1.0).T
        im = ax_map.imshow(map_arr.T, alpha=a_norm, **img_kwargs)
    else:
        im = ax_map.imshow(map_arr.T, **img_kwargs)
    ax_map.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_map.set_ylabel(r'$\varphi_\mathrm{AC}$ (rad)')
    ax_map.set_xticks([0, np.pi, 2 * np.pi])
    ax_map.set_xticklabels(['0', r'$\pi$', r'$2\pi$'])
    ax_map.set_yticks([0, np.pi, 2 * np.pi])
    ax_map.set_yticklabels(['0', r'$\pi$', r'$2\pi$'])
    cb = fig.colorbar(im, ax=ax_map, shrink=0.85, pad=0.02)
    cb.set_label(ylabel)

    ax_bot = fig.add_subplot(gs[1, 1], sharex=ax_map)
    for ph_t, col in zip(cuts_phi, cut_styles):
        j = int(np.argmin(np.abs(phi_grid - ph_t)))
        ax_bot.plot(theta0_grid, map_arr[:, j], color=col,
                    label=fr'$\varphi={ph_t/np.pi:.2f}\pi$')
    ax_bot.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_bot.set_ylabel(ylabel)
    if symmetric:
        ax_bot.set_ylim(-vlim * 1.1, +vlim * 1.1)
        ax_bot.axhline(0, color='k', lw=0.4)
    ax_bot.legend(loc='lower right', fontsize=7, framealpha=0.9)

    ax_left = fig.add_subplot(gs[0, 0], sharey=ax_map)
    for th_t, col in zip(cuts_theta, cut_styles):
        i = int(np.argmin(np.abs(theta0_grid - th_t)))
        ax_left.plot(map_arr[i, :], phi_grid, color=col,
                     label=fr'$\vartheta_0={th_t/np.pi:.2f}\pi$')
    ax_left.set_xlabel(ylabel)
    if symmetric:
        ax_left.set_xlim(+vlim * 1.1, -vlim * 1.1)
        ax_left.axvline(0, color='k', lw=0.4)
    ax_left.legend(loc='lower left', fontsize=7, framealpha=0.9)

    fig.suptitle(title, fontsize=10)
    out = os.path.join(PLOTS_DIR, fname)
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default=os.path.join(SCRIPT_DIR,
                                                    'fig6_alpha3_v5.h5'))
    args = ap.parse_args()

    with h5py.File(args.input, 'r') as f:
        theta0 = f['theta0_rad'][:]
        phi = f['phi_rad'][:]
        sx = f['sigma_x_map'][:]
        sy = f['sigma_y_map'][:]
        attrs = dict(f.attrs)

    coh_abs = np.sqrt(sx ** 2 + sy ** 2)
    coh_arg_deg = np.degrees(np.arctan2(sy, sx))

    print(f"Read {args.input}")
    print(f"  ⟨σ_x⟩ range: [{sx.min():+.3f}, {sx.max():+.3f}]")
    print(f"  ⟨σ_y⟩ range: [{sy.min():+.3f}, {sy.max():+.3f}]")
    print(f"  |C|   range: [{coh_abs.min():.3f}, {coh_abs.max():.3f}]")
    print(f"  code_version = {attrs.get('code_version')}  "
          f"engine = {attrs.get('engine')}")

    title_suffix = (rf"N={int(attrs.get('n_pulses', 30))}, "
                    rf"$\delta t/T_m$={float(attrs.get('delta_t_frac_Tm', 0.13)):.2f}, "
                    rf"$|\alpha|$={float(attrs.get('alpha', 3.0)):.0f}, "
                    rf"η={float(attrs.get('eta', 0.397)):.3f}")

    heatmap(sx, theta0, phi,
            rf'Hasse Fig 6c — $\langle\sigma_x\rangle$  ({title_suffix})',
            'fig6c_sigma_x_v5.png',
            cmap='RdBu_r', ylabel=r'$\langle\sigma_x\rangle$')
    heatmap(sy, theta0, phi,
            rf'Hasse Fig 6c — $\langle\sigma_y\rangle$  ({title_suffix})',
            'fig6c_sigma_y_v5.png',
            cmap='RdBu_r', ylabel=r'$\langle\sigma_y\rangle$')
    heatmap(coh_abs, theta0, phi,
            rf'Hasse Fig 6c — coherence $|C| = \sqrt{{\sigma_x^2+\sigma_y^2}}$  ({title_suffix})',
            'fig6c_coh_abs_v5.png',
            cmap='magma', ylabel=r'$|C|$',
            vlim=1.0, symmetric=False)
    heatmap(coh_arg_deg, theta0, phi,
            rf'Hasse Fig 6c — coherence phase $\arg(C)$  ({title_suffix})',
            'fig6c_coh_arg_v5.png',
            cmap='twilight', ylabel=r'$\arg(C)$ (deg)',
            vlim=180.0, symmetric=True, alpha_map=coh_abs)


if __name__ == '__main__':
    main()
