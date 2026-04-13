#!/usr/bin/env python3
"""
plot_fine_grids.py — Fine-grid figures for Guardian flags 2 and 3.

Flag 3: carrier-zoom S1 at 10 kHz/(2π) step localising the Magnus bias.
Flag 2: R2 at 5 kHz/(2π) step resolving the tooth sinc-shape.

Reads:
  numerics/S1_carrier_zoom.h5
  numerics/R2_fine_tooth.h5
Writes:
  plots/S1_carrier_zoom.png
  plots/R2_fine_tooth.png
"""

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))


def plot_S1_carrier_zoom():
    p = os.path.join(SCRIPT_DIR, 'S1_carrier_zoom.h5')
    with h5py.File(p, 'r') as f:
        det = f['detuning_MHz_over_2pi'][:]
        alpha = f['alpha'][:]
        full_sx = f['full/sigma_x'][:]; full_sy = f['full/sigma_y'][:]
        R1_sx = f['R1/sigma_x'][:];    R1_sy = f['R1/sigma_y'][:]
    Cf = np.sqrt(full_sx**2 + full_sy**2)
    Cr = np.sqrt(R1_sx**2 + R1_sy**2)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    for i, a in enumerate(alpha):
        ax.plot(det * 1000, Cf[i], '.-', ms=3, lw=1,
                label=fr'$|\alpha|={a:g}$')
    peak_full_kHz = -205.856   # from parabolic fit
    ax.axvline(peak_full_kHz, color='k', ls=':', lw=1,
               label=fr'peak @ ${peak_full_kHz:+.1f}$ kHz')
    ax.axvline(0, color='gray', lw=0.5)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (kHz)')
    ax.set_ylabel(r'$|C|_{\rm full}$')
    ax.set_title(r'Full engine (η = 0.397) — carrier-zoom at 10 kHz step')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1]
    for i, a in enumerate(alpha):
        ax.plot(det * 1000, Cr[i], '.-', ms=3, lw=1,
                label=fr'$|\alpha|={a:g}$')
    peak_R1_kHz = -20.721
    ax.axvline(peak_R1_kHz, color='k', ls=':', lw=1,
               label=fr'peak @ ${peak_R1_kHz:+.1f}$ kHz')
    ax.axvline(0, color='gray', lw=0.5)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (kHz)')
    ax.set_ylabel(r'$|C|_{R1}$')
    ax.set_title(r'R1 (η = 0.04) — same zoom, peak scales linearly with η')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    fig.suptitle(r'WP-E Flag 3: Magnus carrier-bias is real; ratio $\approx \eta_{\rm full}/\eta_{R1} = 9.93$')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'S1_carrier_zoom.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f'Wrote {out}')


def plot_R2_fine_tooth():
    p = os.path.join(SCRIPT_DIR, 'R2_fine_tooth.h5')
    with h5py.File(p, 'r') as f:
        det = f['detuning_MHz_over_2pi'][:]
        C_R2 = f['R2/C_abs'][:]
        C_R12 = f['R12/C_abs'][:]
    # Coarse comparison
    p2 = os.path.join(SCRIPT_DIR, 'R2_delta_alpha.h5')
    with h5py.File(p2, 'r') as f:
        det_c = f['detuning_MHz_over_2pi'][:]
        C_R2_c = f['R2/C_abs'][0]
        C_R12_c = f['R12/C_abs'][0]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    ax.plot(det * 1000, C_R2, '.-', ms=3, lw=1, color='C0',
            label=r'R2 (η=0.397) fine, 5 kHz step')
    ax.plot(det_c * 1000, C_R2_c, 's', ms=6, color='C0', alpha=0.5,
            label=r'R2 coarse, 100 kHz step (undersampled)')
    ax.set_xlim(-500, 500)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (kHz)')
    ax.set_ylabel(r'$|C|_{R2}$')
    ax.set_title(r'R2 tooth at $\delta = 0$, |α| = 0')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.set_ylim(-0.02, 1.0)

    ax = axes[1]
    ax.semilogy(det * 1000, np.maximum(C_R2, 1e-6), '.-', ms=3, lw=1,
                color='C0', label=r'R2 fine, log scale')
    ax.semilogy(det_c * 1000, np.maximum(C_R2_c, 1e-6), 's', ms=6,
                color='C0', alpha=0.5, label=r'R2 coarse')
    ax.set_xlim(-500, 500)
    ax.set_ylim(1e-4, 2)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (kHz)')
    ax.set_ylabel(r'$|C|_{R2}$  (log)')
    ax.set_title(r'Log scale — between-tooth min drops to $\sim 10^{-3}$, not $10^{-1.5}$')
    ax.legend(fontsize=8); ax.grid(alpha=0.3, which='both')

    fig.suptitle(r'WP-E Flag 2: R2 tooth HWHM = 41 kHz/(2π); coarse grid (100 kHz) undersamples')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'R2_fine_tooth.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f'Wrote {out}')


if __name__ == '__main__':
    plot_S1_carrier_zoom()
    plot_R2_fine_tooth()
