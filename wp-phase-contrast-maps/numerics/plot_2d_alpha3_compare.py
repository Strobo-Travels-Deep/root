#!/usr/bin/env python3
"""
plot_2d_alpha3_compare.py — Side-by-side heatmaps and per-tooth
envelopes: synced vs unsynced 2D scans at |α|=3.
"""

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
os.makedirs(PLOT_DIR, exist_ok=True)

PHASE_MASK = 0.05


def wrap_deg(x): return ((x + 180) % 360) - 180


def load(fname):
    with h5py.File(os.path.join(SCRIPT_DIR, fname), 'r') as f:
        return {
            'det_MHz': f['detuning_MHz_over_2pi'][:],
            'phi_deg': f['phi_alpha_deg'][:],
            'C_abs':   f['C_abs'][:],
            'C_arg':   wrap_deg(f['C_arg_deg'][:]),
            'sz':      f['sigma_z'][:],
            'omega_m': float(f.attrs['omega_m']),
        }


def main():
    S = load('scan_2d_alpha3.h5')
    U = load('scan_2d_alpha3_unsynced.h5')
    omega_m = S['omega_m']

    # === Compare |C| heatmaps side by side ===
    extent = [S['det_MHz'][0], S['det_MHz'][-1], S['phi_deg'][0], S['phi_deg'][-1]]
    fig, axes = plt.subplots(3, 2, figsize=(15, 11))

    for col, (d, label) in enumerate([(U, 'unsynced (engine-native)'),
                                       (S, 'synced-phase (Flag 1)')]):
        ax = axes[0, col]
        im = ax.imshow(d['C_abs'], aspect='auto', origin='lower', extent=extent,
                       cmap='viridis', vmin=0, vmax=1, interpolation='none')
        plt.colorbar(im, ax=ax, fraction=0.03)
        ax.set_title(fr'$|C|$ — {label}')
        ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
        for k in range(-11, 12):
            ax.axvline(k * omega_m, color='white', lw=0.4, alpha=0.3)

        ax = axes[1, col]
        arg_m = np.where(d['C_abs'] >= PHASE_MASK, d['C_arg'], np.nan)
        im = ax.imshow(arg_m, aspect='auto', origin='lower', extent=extent,
                       cmap='hsv', vmin=-180, vmax=180, interpolation='none')
        plt.colorbar(im, ax=ax, fraction=0.03, label='deg')
        ax.set_title(fr'$\arg C$ — {label}')
        ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
        for k in range(-11, 12):
            ax.axvline(k * omega_m, color='black', lw=0.4, alpha=0.3)

        ax = axes[2, col]
        sz_max = max(abs(d['sz'].min()), abs(d['sz'].max()))
        im = ax.imshow(d['sz'], aspect='auto', origin='lower', extent=extent,
                       cmap='RdBu_r', vmin=-sz_max, vmax=+sz_max, interpolation='none')
        plt.colorbar(im, ax=ax, fraction=0.03)
        ax.set_title(fr'$\langle\sigma_z\rangle$ — {label}')
        ax.set_xlabel(r'$\delta_0/(2\pi)$ (MHz)')
        ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
        for k in range(-11, 12):
            ax.axvline(k * omega_m, color='white', lw=0.4, alpha=0.3)

    fig.suptitle(r'WP-E 2D scan $|\alpha|=3$: synced-phase vs engine-native convention')
    fig.tight_layout()
    out1 = os.path.join(PLOT_DIR, 'scan_2d_alpha3_compare_overview.png')
    fig.savefig(out1, dpi=140); plt.close(fig)
    print(f'wrote {out1}')

    # === Per-tooth envelope comparison ===
    ks = np.arange(-11, 12)
    tooth_centres = ks * omega_m
    j_teeth = [int(np.argmin(np.abs(S['det_MHz'] - c))) for c in tooth_centres]
    CS = S['C_abs'][:, j_teeth]
    CU = U['C_abs'][:, j_teeth]

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))

    for row, (C_tag, C_grid, tag) in enumerate([
            ('unsynced', CU, 'unsynced (engine)'),
            ('synced',   CS, 'synced-phase'),
    ]):
        # Heatmap
        ax = axes[row, 0]
        extent2 = [ks[0]-0.5, ks[-1]+0.5, S['phi_deg'][0], S['phi_deg'][-1]]
        im = ax.imshow(C_grid, aspect='auto', origin='lower', extent=extent2,
                       cmap='viridis', vmin=0, vmax=1, interpolation='none')
        plt.colorbar(im, ax=ax, fraction=0.05)
        ax.set_xlabel(r'sideband order $k$')
        ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
        ax.set_title(fr'$|C|$ at $\delta = k\omega_m$ — {tag}')
        ax.set_xticks(ks[::2])

        # Traces at 8 φ_α
        ax = axes[row, 1]
        sample_phi = [0, 45, 90, 135, 180, 225, 270, 315]
        for target in sample_phi:
            j = int(np.argmin(np.abs(S['phi_deg'] - target)))
            ax.plot(ks, C_grid[j], 'o-', ms=4, lw=1,
                    label=fr'$\varphi_\alpha = {S["phi_deg"][j]:.0f}°$')
        ax.set_xlabel(r'sideband order $k$')
        ax.set_ylabel(r'$|C|$')
        ax.set_title(fr'traces — {tag}')
        ax.legend(fontsize=7, ncol=2); ax.grid(alpha=0.3)
        ax.set_xticks(ks[::2])
        ax.set_ylim(-0.05, 1.05)

    fig.suptitle(r'Per-tooth envelope: sideband asymmetry appears only in synced-phase convention')
    fig.tight_layout()
    out2 = os.path.join(PLOT_DIR, 'scan_2d_alpha3_compare_tooth_envelope.png')
    fig.savefig(out2, dpi=140); plt.close(fig)
    print(f'wrote {out2}')

    # === Numerical summary ===
    print('\n=== Summary at sideband k=0, ±1, ±5 ===')
    ks_print = [0, +1, +2, +5, -1, -2, -5]
    phi_print = [0, 90, 180, 270]
    print('convention  φ_α  ' + '  '.join(f'k={k:+d}' for k in ks_print))
    for tag, grid in [('unsynced', CU), ('synced  ', CS)]:
        for phi_tgt in phi_print:
            j = int(np.argmin(np.abs(S['phi_deg'] - phi_tgt)))
            vals = ' '.join(f'{grid[j, list(ks).index(k)]:.3f}' for k in ks_print)
            print(f'{tag}    {phi_tgt:5.1f}  {vals}')


if __name__ == '__main__':
    main()
