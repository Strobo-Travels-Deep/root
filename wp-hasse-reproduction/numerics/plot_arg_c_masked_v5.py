#!/usr/bin/env python3
"""
plot_arg_c_masked_v5.py — arg(C) heatmaps with (1 − |C|) alpha mask.

Follow-up 3 from 2026-04-21-coh-theta0-det-rabi5x.md. The baseline
v5 plot alpha-masked by |C|, which is backwards: off-tooth the
coherence is ~1 (so the bright alpha made the rapidly-winding global
phase dominate), while on-tooth |C| → 0 (where the phase is
meaningful for ϑ₀-structure but got hidden).

Re-reads existing h5 outputs and plots with the inverted alpha,
saturating only where |C| is close to 1.
"""
from __future__ import annotations

import os

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))


def plot(h5_path, out_png, title, det_ticks=(-3, -2, -1, 0, 1, 2, 3)):
    with h5py.File(h5_path, 'r') as f:
        theta0 = f['theta0_rad'][:]
        det = f['detuning_rel'][:]
        coh_abs = f['coh_abs_map'][:]
        coh_arg = f['coh_arg_deg_map'][:]

    # Alpha = (1 − |C|) saturated: only non-trivial at the comb teeth.
    alpha = np.clip(1.0 - coh_abs, 0.0, 1.0)
    # Stretch to use full range so the teeth pop.
    alpha = alpha / max(1e-12, alpha.max())

    fig = plt.figure(figsize=(7.2, 5.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 3], height_ratios=[3, 1],
                          hspace=0.30, wspace=0.30)
    vlim = 180.0

    ax_map = fig.add_subplot(gs[0, 1])
    im = ax_map.imshow(
        coh_arg.T, alpha=alpha.T, origin='lower',
        extent=[theta0[0], theta0[-1], det[0], det[-1]],
        aspect='auto', cmap='twilight', vmin=-vlim, vmax=+vlim,
    )
    ax_map.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_map.set_ylabel(r'$\delta / \omega_m$')
    ax_map.set_xticks([0, np.pi, 2 * np.pi])
    ax_map.set_xticklabels(['0', r'$\pi$', r'$2\pi$'])
    valid_ticks = [t for t in det_ticks if det[0] <= t <= det[-1]]
    ax_map.set_yticks(valid_ticks)
    for n in valid_ticks:
        ax_map.axhline(n, color='gray', lw=0.3, alpha=0.25)
    cb = fig.colorbar(im, ax=ax_map, shrink=0.85, pad=0.02)
    cb.set_label(r'$\arg(C)$ (deg),  masked by $(1-|C|)$')

    cuts_det = [d for d in (0.0, 1.0, 2.0) if det[0] <= d <= det[-1]]
    cuts_styles = ('lightgray', 'dimgray', 'black')
    ax_bot = fig.add_subplot(gs[1, 1], sharex=ax_map)
    for d_t, col in zip(cuts_det, cuts_styles):
        j = int(np.argmin(np.abs(det - d_t)))
        ax_bot.plot(theta0, coh_arg[:, j], color=col,
                    label=fr'$\delta/\omega_m={d_t:.1f}$')
    ax_bot.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_bot.set_ylabel(r'$\arg(C)$ (deg)')
    ax_bot.set_ylim(-vlim * 1.1, +vlim * 1.1)
    ax_bot.axhline(0, color='k', lw=0.4)
    ax_bot.legend(loc='lower right', fontsize=7, framealpha=0.9)

    ax_left = fig.add_subplot(gs[0, 0], sharey=ax_map)
    cuts_theta = (np.pi / 4, np.pi / 2, np.pi)
    for th_t, col in zip(cuts_theta, cuts_styles):
        i = int(np.argmin(np.abs(theta0 - th_t)))
        ax_left.plot(coh_arg[i, :], det, color=col,
                     label=fr'$\vartheta_0={th_t/np.pi:.2f}\pi$')
    ax_left.set_xlabel(r'$\arg(C)$ (deg)')
    ax_left.set_xlim(+vlim * 1.1, -vlim * 1.1)
    ax_left.axvline(0, color='k', lw=0.4)
    ax_left.legend(loc='lower left', fontsize=7, framealpha=0.9)

    fig.suptitle(title, fontsize=10)
    out = os.path.join(PLOTS_DIR, out_png)
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")


def main():
    for h5_name, png_name, rs_tag in [
        ('coh_theta0_det_v5.h5', 'coh_theta0_det_coh_arg_masked_v5.png',
         r'$\Omega\times 1$'),
        ('coh_theta0_det_v5_rabi5x.h5', 'coh_theta0_det_rabi5x_coh_arg_masked_v5.png',
         r'$\Omega\times 5$'),
    ]:
        h5_path = os.path.join(SCRIPT_DIR, h5_name)
        if not os.path.exists(h5_path):
            print(f"  skipping {h5_path}: not found")
            continue
        plot(h5_path, png_name,
             rf'$\arg C(\vartheta_0, \delta)$  (alpha masked by $1-|C|$;  {rs_tag})')


if __name__ == '__main__':
    main()
