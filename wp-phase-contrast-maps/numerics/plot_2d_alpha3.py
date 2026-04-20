#!/usr/bin/env python3
"""
plot_2d_alpha3.py — Heatmaps for the 2D (δ₀, φ_α) scan at |α| = 3.

Reads  numerics/scan_2d_alpha3.h5
Writes plots/scan_2d_alpha3_overview.png
       plots/scan_2d_alpha3_sideband_zooms.png
"""

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
os.makedirs(PLOT_DIR, exist_ok=True)

PHASE_MASK = 0.05   # mask arg C where |C| < 0.05


def wrap_deg(x): return ((x + 180) % 360) - 180


def load():
    with h5py.File(os.path.join(SCRIPT_DIR, 'scan_2d_alpha3.h5'), 'r') as f:
        return {
            'det_MHz': f['detuning_MHz_over_2pi'][:],
            'phi_deg': f['phi_alpha_deg'][:],
            'C_abs':   f['C_abs'][:],
            'C_arg':   wrap_deg(f['C_arg_deg'][:]),
            'sz':      f['sigma_z'][:],
            'alpha':   float(f.attrs['alpha']),
            'eta':     float(f.attrs['eta']),
            'omega_m': float(f.attrs['omega_m']),
        }


def overview(d):
    """Full ±15 MHz panels."""
    det = d['det_MHz']; phi = d['phi_deg']
    extent = [det[0], det[-1], phi[0], phi[-1]]
    omega_m = d['omega_m']

    fig, axes = plt.subplots(3, 1, figsize=(14, 10))

    # |C|
    ax = axes[0]
    im = ax.imshow(d['C_abs'], aspect='auto', origin='lower', extent=extent,
                   cmap='viridis', vmin=0, vmax=1,
                   interpolation='none')
    plt.colorbar(im, ax=ax, fraction=0.02, pad=0.01)
    ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
    ax.set_title(fr'$|C|$ — $|\alpha|={d["alpha"]:g}$, $\eta={d["eta"]}$, synced-phase, v0.9.1')
    # Sideband markers
    for k in range(-11, 12):
        ax.axvline(k * omega_m, color='white', lw=0.4, alpha=0.3)

    # arg C (masked where |C| small)
    ax = axes[1]
    arg_masked = np.where(d['C_abs'] >= PHASE_MASK, d['C_arg'], np.nan)
    im = ax.imshow(arg_masked, aspect='auto', origin='lower', extent=extent,
                   cmap='hsv', vmin=-180, vmax=180,
                   interpolation='none')
    plt.colorbar(im, ax=ax, fraction=0.02, pad=0.01, label='deg')
    ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
    ax.set_title(fr'$\arg C$ (deg, masked $|C| < {PHASE_MASK}$)')
    for k in range(-11, 12):
        ax.axvline(k * omega_m, color='black', lw=0.4, alpha=0.3)

    # σ_z
    ax = axes[2]
    sz_max = max(abs(d['sz'].min()), abs(d['sz'].max()))
    im = ax.imshow(d['sz'], aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', vmin=-sz_max, vmax=+sz_max,
                   interpolation='none')
    plt.colorbar(im, ax=ax, fraction=0.02, pad=0.01)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
    ax.set_title(r'$\langle\sigma_z\rangle$')
    for k in range(-11, 12):
        ax.axvline(k * omega_m, color='white', lw=0.4, alpha=0.3)

    fig.suptitle(fr'WP-E 2D scan at $|\alpha|=3$: $\delta_0 \in \pm 15$ MHz, '
                 fr'$\varphi_\alpha \in [0, 2\pi)$  (vertical lines = $k\omega_m$)')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'scan_2d_alpha3_overview.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def sideband_zooms(d):
    """Zoom into individual sidebands to see each tooth's φ_α-dependence."""
    det = d['det_MHz']; phi = d['phi_deg']
    omega_m = d['omega_m']

    # Pick a few sideband orders to show
    k_list = [0, 1, 2, 3, 5, -1]
    zoom_width = 0.25   # MHz each side of tooth centre

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes_flat = axes.flatten()

    for idx, k in enumerate(k_list):
        ax = axes_flat[idx]
        center = k * omega_m
        mask = (det > center - zoom_width) & (det < center + zoom_width)
        det_z = det[mask]
        if len(det_z) < 2:
            ax.text(0.5, 0.5, 'no data', ha='center', va='center', transform=ax.transAxes)
            continue
        C_z = d['C_abs'][:, mask]
        extent = [det_z[0] - center, det_z[-1] - center, phi[0], phi[-1]]
        im = ax.imshow(C_z, aspect='auto', origin='lower', extent=extent,
                       cmap='viridis', vmin=0, vmax=1, interpolation='none')
        plt.colorbar(im, ax=ax, fraction=0.05)
        ax.set_xlabel(fr'$\delta_0/(2\pi) - {k}\omega_m/(2\pi)$ (MHz)')
        ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
        # Carrier-value reading at tooth centre
        j0 = int(np.argmin(np.abs(det - center)))
        slice_at_tooth = d['C_abs'][:, j0]
        ax.set_title(fr'$k = {k}$ ($\delta = {center:+.2f}$ MHz) | '
                     fr'$|C|$ at tooth: {slice_at_tooth.min():.3f}–{slice_at_tooth.max():.3f}')

    fig.suptitle(r'WP-E 2D scan $|\alpha|=3$: zooms on individual comb teeth — each tooth\'s $\varphi_\alpha$ signature')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'scan_2d_alpha3_sideband_zooms.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def tooth_envelope(d):
    """|C| at exact tooth centres (δ = k·ω_m) as a function of k and φ_α."""
    det = d['det_MHz']; phi = d['phi_deg']
    omega_m = d['omega_m']
    ks = np.arange(-11, 12)
    tooth_centres = ks * omega_m

    # Find each tooth's grid index (nearest point)
    j_teeth = [int(np.argmin(np.abs(det - c))) for c in tooth_centres]

    C_teeth = d['C_abs'][:, j_teeth]
    arg_teeth = d['C_arg'][:, j_teeth]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # |C| at each tooth, one trace per φ_α
    ax = axes[0]
    extent = [ks[0]-0.5, ks[-1]+0.5, phi[0], phi[-1]]
    im = ax.imshow(C_teeth, aspect='auto', origin='lower', extent=extent,
                   cmap='viridis', vmin=0, vmax=1, interpolation='none')
    plt.colorbar(im, ax=ax, fraction=0.05, label=r'$|C|$')
    ax.set_xlabel(r'sideband order $k$ at $\delta = k\omega_m$')
    ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
    ax.set_title(r'$|C|$ at exact tooth centres $\delta_0 = k\omega_m$')
    ax.set_xticks(ks[::2])

    # Traces at selected φ_α
    ax = axes[1]
    sample_phi = [0, 45, 90, 135, 180, 225, 270, 315]
    for target in sample_phi:
        j = int(np.argmin(np.abs(phi - target)))
        ax.plot(ks, C_teeth[j], 'o-', ms=4, lw=1,
                label=fr'$\varphi_\alpha = {phi[j]:.0f}°$')
    ax.set_xlabel(r'sideband order $k$')
    ax.set_ylabel(r'$|C|$')
    ax.set_title(r'Tooth-centre $|C|$ vs $k$ at selected $\varphi_\alpha$')
    ax.legend(fontsize=8, ncol=2); ax.grid(alpha=0.3)
    ax.set_xticks(ks[::2])

    fig.suptitle(r'WP-E: per-tooth $|C|$ map — the velocity-channel signature aliased into the comb')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'scan_2d_alpha3_tooth_envelope.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


if __name__ == '__main__':
    d = load()
    print(f'Loaded: {d["C_abs"].shape}  det step ≈ '
          f'{(d["det_MHz"][1] - d["det_MHz"][0])*1000:.1f} kHz')
    outs = [overview(d), sideband_zooms(d), tooth_envelope(d)]
    for o in outs: print(f'  wrote {o}')
