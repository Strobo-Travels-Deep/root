#!/usr/bin/env python3
"""
plot_fig8.py — Render Hasse Fig 8 reproduction from fig8_calibrations.h5.

Two output PNGs in ../plots/:
    fig8a_position.png  — |α| vs analysis-phase shift ϕ₀ at three tilt angles
    fig8b_momentum.png  — |α| vs contrast (= proxy for momentum) at three tilts
"""

import os
import numpy as np
import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
H5         = os.path.join(SCRIPT_DIR, 'fig8_calibrations.h5')
OUT_DIR    = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))

TILT_COLORS = {
    -5.0: 'tab:green',
     0.0: 'tab:blue',
    +5.0: 'tab:orange',
}


def main():
    with h5py.File(H5, 'r') as f:
        alpha = f['alpha'][:]
        tilts = f['tilt_deg'][:]
        phi0  = f['phi0_rad'][:]
        Cnorm = f['contrast_norm'][:]
        eta_per_tilt = f['eta_per_tilt'][:]

    os.makedirs(OUT_DIR, exist_ok=True)

    # 8a — |α| vs ϕ₀ (Hasse layout: x = phase shift, y = amplitude)
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    for j, tilt in enumerate(tilts):
        c = TILT_COLORS.get(float(tilt), 'k')
        ax.plot(phi0[j], alpha, color=c,
                label=fr'tilt {tilt:+.0f}°  ($\eta={eta_per_tilt[j]:.4f}$)')
    ax.set_xlabel(r'Analysis-phase shift $\varphi_0$ (rad)')
    ax.set_ylabel(r'Displ. amplitude $|\alpha|$')
    ax.axhline(0, color='k', lw=0.3); ax.axvline(0, color='k', lw=0.3)
    ax.set_xlim(-2 * np.pi, +2 * np.pi)
    ax.set_xticks([-2 * np.pi, -np.pi, 0, np.pi, 2 * np.pi])
    ax.set_xticklabels([r'$-2\pi$', r'$-\pi$', '0', r'$\pi$', r'$2\pi$'])
    ax.set_ylim(0, alpha.max() * 1.05)
    ax.legend(fontsize=8)
    ax.set_title(r'Hasse Fig 8a reproduction — position calibration ($n_\mathrm{th}=0.15$)',
                 fontsize=9)
    out = os.path.join(OUT_DIR, 'fig8a_position.png')
    fig.tight_layout(); fig.savefig(out, dpi=140); plt.close(fig)
    print(f"  wrote {out}")

    # 8b — |α| vs C
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    for j, tilt in enumerate(tilts):
        c = TILT_COLORS.get(float(tilt), 'k')
        ax.plot(Cnorm[j], alpha, color=c,
                label=fr'tilt {tilt:+.0f}°  ($\eta={eta_per_tilt[j]:.4f}$)')
    ax.set_xlabel('Contrast  $C$ (normalised to $|C(\\alpha=0)|$)')
    ax.set_ylabel(r'Displ. amplitude $|\alpha|$')
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, alpha.max() * 1.05)
    ax.legend(fontsize=8)
    ax.set_title(r'Hasse Fig 8b reproduction — momentum calibration ($n_\mathrm{th}=0.15$)',
                 fontsize=9)
    out = os.path.join(OUT_DIR, 'fig8b_momentum.png')
    fig.tight_layout(); fig.savefig(out, dpi=140); plt.close(fig)
    print(f"  wrote {out}")


if __name__ == '__main__':
    main()
