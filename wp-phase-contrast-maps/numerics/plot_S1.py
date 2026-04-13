#!/usr/bin/env python3
"""
plot_S1.py — Figures for WP-E S1 slice (δ₀, |α|) at φ_α = 0.

Reads:
  numerics/S1_delta_alpha.h5
  numerics/R1_convergence.h5

Writes (to plots/):
  S1_carrier_summary.png    Headline: |C|(δ=0) and arg C(δ=0) vs α, full vs R1.
  S1_contrast_maps.png      |C| heatmaps (full, R1) + |C|(δ) line plots.
  S1_phase_maps.png         arg C heatmaps (full, R1), masked where |C| < 0.1.
  S1_eta_residuals.png      Δη = full − R1 for |C| and arg C; carrier slice.
  R1_convergence.png        η = 0.04 vs η = 0.02 cross-check.

Conventions per v0.3 §2/§2.2: positive φ_α rotates α from +X̂ toward +P̂;
det_rel = δ / ω_m; arg C in degrees, principal branch (−180, +180].
Phase residuals masked at |C| < 0.1 per S1+R1 logbook §4.
"""

import os, sys
import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
os.makedirs(PLOT_DIR, exist_ok=True)

S1_FILE = os.path.join(SCRIPT_DIR, 'S1_delta_alpha.h5')
R1C_FILE = os.path.join(SCRIPT_DIR, 'R1_convergence.h5')

PHASE_MASK_THRESHOLD = 0.1


def load_S1():
    with h5py.File(S1_FILE, 'r') as f:
        det_MHz = f['detuning_MHz_over_2pi'][:]
        det_rel = f['detuning_rel'][:]
        alpha = f['alpha'][:]
        out = {'det_MHz': det_MHz, 'det_rel': det_rel, 'alpha': alpha,
               'attrs': dict(f.attrs)}
        for tag in ('full', 'R1'):
            out[tag] = {k: f[f'{tag}/{k}'][:] for k in
                        ('sigma_x', 'sigma_y', 'sigma_z',
                         'C_abs', 'C_arg_deg', 'max_fock_leakage')}
    return out


def wrap_deg(x):
    """Wrap to (-180, 180]."""
    return ((x + 180) % 360) - 180


# ═══════════════════════════════════════════════════════════════
# Figure 1 — Carrier summary (the headline)
# ═══════════════════════════════════════════════════════════════

def plot_carrier_summary(d):
    det = d['det_MHz']
    i0 = int(np.argmin(np.abs(det)))
    alpha = d['alpha']
    Cf = d['full']['C_abs'][:, i0]
    Cr = d['R1']['C_abs'][:, i0]
    af = d['full']['C_arg_deg'][:, i0]
    ar = d['R1']['C_arg_deg'][:, i0]
    sz_f = d['full']['sigma_z'][:, i0]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # |C| at δ=0
    ax = axes[0]
    ax.plot(alpha, Cf, 'o-', color='C0', label=f'full (η = {d["attrs"]["eta_full"]})')
    ax.plot(alpha, Cr, 's--', color='C1', label=f'R1 (η = {d["attrs"]["eta_R1"]})')
    ax.set_xlabel(r'$|\alpha|$')
    ax.set_ylabel(r'$|C|$ at $\delta_0 = 0$')
    ax.set_title(r'Carrier contrast — α-independent in both engines')
    ax.set_ylim(0.85, 1.02)
    ax.grid(alpha=0.3)
    ax.legend()

    # arg C at δ=0 (the position phase channel)
    ax = axes[1]
    ax.plot(alpha, wrap_deg(af), 'o-', color='C0', label='full')
    ax.plot(alpha, wrap_deg(ar), 's--', color='C1', label='R1')
    # R1 linear extrapolation guide: +4.6° per unit α, anchored at α=0
    a_dense = np.linspace(0, alpha.max(), 100)
    ax.plot(a_dense, 90 + 4.58 * a_dense, ':', color='C1', alpha=0.5,
            label='R1 linear: +90° + 4.6°·α')
    ax.set_xlabel(r'$|\alpha|$')
    ax.set_ylabel(r'$\arg C$ at $\delta_0 = 0$ (deg)')
    ax.set_title(r'Position-phase channel (dossier §1.3)')
    ax.set_ylim(-200, 200)
    ax.grid(alpha=0.3)
    ax.legend(loc='lower left')

    # σ_z at δ=0
    ax = axes[2]
    ax.plot(alpha, sz_f, 'o-', color='C0', label='full')
    ax.plot(alpha, d['R1']['sigma_z'][:, i0], 's--', color='C1', label='R1')
    ax.set_xlabel(r'$|\alpha|$')
    ax.set_ylabel(r'$\langle\sigma_z\rangle$ at $\delta_0 = 0$')
    ax.set_title(r'$\langle\sigma_z\rangle$ — also α-independent')
    ax.axhline(0, color='k', lw=0.5)
    ax.grid(alpha=0.3)
    ax.legend()

    fig.suptitle(r'WP-E S1 — Carrier ($\delta_0 = 0$) summary at $\varphi_\alpha = 0$')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'S1_carrier_summary.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


# ═══════════════════════════════════════════════════════════════
# Figure 2 — |C| maps and Doppler signature
# ═══════════════════════════════════════════════════════════════

def plot_contrast_maps(d):
    det = d['det_MHz']
    alpha = d['alpha']
    Cf = d['full']['C_abs']
    Cr = d['R1']['C_abs']

    fig, axes = plt.subplots(2, 3, figsize=(13, 7),
                             gridspec_kw={'height_ratios': [1, 0.9]})

    # Heatmaps: full, R1, Δη
    extent = [det[0], det[-1], -0.5, len(alpha) - 0.5]
    for ax, M, title, cmap, vmin, vmax in [
        (axes[0,0], Cf, r'$|C|_{\rm full}$ (η = 0.397)', 'viridis', 0, 1),
        (axes[0,1], Cr, r'$|C|_{R1}$ (η = 0.04)', 'viridis', 0, 1),
    ]:
        im = ax.imshow(M, aspect='auto', origin='lower', extent=extent,
                       cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_yticks(range(len(alpha)))
        ax.set_yticklabels([f'{a:g}' for a in alpha])
        ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
        ax.set_ylabel(r'$|\alpha|$')
        ax.set_title(title)
        plt.colorbar(im, ax=ax, fraction=0.05)

    # Δη with diverging colormap
    Delta = Cf - Cr
    vmax = max(abs(Delta.min()), abs(Delta.max()))
    ax = axes[0,2]
    im = ax.imshow(Delta, aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', norm=TwoSlopeNorm(vcenter=0,
                                                    vmin=-vmax, vmax=vmax))
    ax.set_yticks(range(len(alpha)))
    ax.set_yticklabels([f'{a:g}' for a in alpha])
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$|\alpha|$')
    ax.set_title(r'$\Delta_\eta = |C|_{\rm full} - |C|_{R1}$')
    plt.colorbar(im, ax=ax, fraction=0.05)

    # Line plots: |C|(δ) for each α (full only, then R1)
    ax = axes[1,0]
    for i, a in enumerate(alpha):
        ax.plot(det, Cf[i], label=fr'$|\alpha|={a:g}$', lw=1.5)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$|C|_{\rm full}$')
    ax.set_title('full engine — Doppler broadening with α')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1,1]
    for i, a in enumerate(alpha):
        ax.plot(det, Cr[i], label=fr'$|\alpha|={a:g}$', lw=1.5)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$|C|_{R1}$')
    ax.set_title('R1 (η = 0.04) — broadening from finite ω_m only')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Carrier-bias zoom
    ax = axes[1,2]
    mask = np.abs(det) < 1.0
    for i, a in enumerate(alpha):
        ax.plot(det[mask], Cf[i, mask], lw=1.5, label=fr'$|\alpha|={a:g}$')
    j = int(np.argmax(Cf[0]))
    ax.axvline(det[j], color='k', ls=':', lw=1, alpha=0.7,
               label=fr'peak @ {det[j]:+.2f} MHz')
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$|C|_{\rm full}$')
    ax.set_title('carrier zoom — α-independent finite-δt bias')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    fig.suptitle(r'WP-E S1 — Contrast maps and Doppler signature')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'S1_contrast_maps.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


# ═══════════════════════════════════════════════════════════════
# Figure 3 — Phase maps
# ═══════════════════════════════════════════════════════════════

def plot_phase_maps(d):
    det = d['det_MHz']
    alpha = d['alpha']
    Cf = d['full']['C_abs']
    Cr = d['R1']['C_abs']
    af = wrap_deg(d['full']['C_arg_deg'])
    ar = wrap_deg(d['R1']['C_arg_deg'])

    af_m = np.where(Cf >= PHASE_MASK_THRESHOLD, af, np.nan)
    ar_m = np.where(Cr >= PHASE_MASK_THRESHOLD, ar, np.nan)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    extent = [det[0], det[-1], -0.5, len(alpha) - 0.5]

    for ax, M, title in [
        (axes[0,0], af_m, r'$\arg C_{\rm full}$ (deg)'),
        (axes[0,1], ar_m, r'$\arg C_{R1}$ (deg)'),
    ]:
        im = ax.imshow(M, aspect='auto', origin='lower', extent=extent,
                       cmap='hsv', vmin=-180, vmax=180)
        ax.set_yticks(range(len(alpha)))
        ax.set_yticklabels([f'{a:g}' for a in alpha])
        ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
        ax.set_ylabel(r'$|\alpha|$')
        ax.set_title(title + fr'  (masked at $|C| < {PHASE_MASK_THRESHOLD}$)')
        plt.colorbar(im, ax=ax, fraction=0.05, label='deg')

    # Phase line cuts at carrier zoom
    for ax, A, C, title in [
        (axes[1,0], af, Cf, 'full engine'),
        (axes[1,1], ar, Cr, 'R1 (η = 0.04)'),
    ]:
        for i, a in enumerate(alpha):
            mask = C[i] >= PHASE_MASK_THRESHOLD
            ax.plot(det[mask], A[i, mask], '.', ms=2, label=fr'$|\alpha|={a:g}$')
        ax.set_xlim(-2, 2)
        ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
        ax.set_ylabel(r'$\arg C$  (deg)')
        ax.set_title(f'{title} — carrier zoom, masked')
        ax.set_ylim(-200, 200)
        ax.grid(alpha=0.3); ax.legend(fontsize=8)

    fig.suptitle(r'WP-E S1 — Position-phase channel ($\arg C$)')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'S1_phase_maps.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


# ═══════════════════════════════════════════════════════════════
# Figure 4 — Δη residuals dedicated plot
# ═══════════════════════════════════════════════════════════════

def plot_eta_residuals(d):
    det = d['det_MHz']
    alpha = d['alpha']
    Cf = d['full']['C_abs']; Cr = d['R1']['C_abs']
    af = wrap_deg(d['full']['C_arg_deg']); ar = wrap_deg(d['R1']['C_arg_deg'])

    Delta_C = Cf - Cr
    Delta_arg = wrap_deg(af - ar)
    # Mask Δarg where either |C| < threshold
    mask = (Cf >= PHASE_MASK_THRESHOLD) & (Cr >= PHASE_MASK_THRESHOLD)
    Delta_arg_m = np.where(mask, Delta_arg, np.nan)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    extent = [det[0], det[-1], -0.5, len(alpha) - 0.5]

    # Δ|C| heatmap
    vmax = max(abs(Delta_C.min()), abs(Delta_C.max()))
    ax = axes[0,0]
    im = ax.imshow(Delta_C, aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', norm=TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax))
    ax.set_yticks(range(len(alpha)))
    ax.set_yticklabels([f'{a:g}' for a in alpha])
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$|\alpha|$')
    ax.set_title(r'$\Delta_\eta\,|C| = |C|_{\rm full} - |C|_{R1}$')
    plt.colorbar(im, ax=ax, fraction=0.05)

    # Δ arg C heatmap
    vmax_a = np.nanmax(np.abs(Delta_arg_m))
    ax = axes[0,1]
    im = ax.imshow(Delta_arg_m, aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', norm=TwoSlopeNorm(vcenter=0, vmin=-vmax_a, vmax=vmax_a))
    ax.set_yticks(range(len(alpha)))
    ax.set_yticklabels([f'{a:g}' for a in alpha])
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$|\alpha|$')
    ax.set_title(fr'$\Delta_\eta\,\arg C$ (deg, masked $|C| < {PHASE_MASK_THRESHOLD}$)')
    plt.colorbar(im, ax=ax, fraction=0.05, label='deg')

    # Δ|C| line cuts at α-slices
    ax = axes[1,0]
    for i, a in enumerate(alpha):
        ax.plot(det, Delta_C[i], lw=1.5, label=fr'$|\alpha|={a:g}$')
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$\Delta_\eta\,|C|$')
    ax.set_title(r'$\Delta_\eta\,|C|$ vs $\delta_0$')
    ax.axhline(0, color='k', lw=0.5)
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Carrier slice: Δ|C|(δ=0) and Δarg(δ=0) vs α
    i0 = int(np.argmin(np.abs(det)))
    ax = axes[1,1]
    ax2 = ax.twinx()
    ax.plot(alpha, Delta_C[:, i0], 'o-', color='C0', label=r'$\Delta_\eta\,|C|$ (left)')
    ax2.plot(alpha, wrap_deg(Delta_arg_m[:, i0]), 's-', color='C3',
             label=r'$\Delta_\eta\,\arg C$ (right)')
    ax.set_xlabel(r'$|\alpha|$')
    ax.set_ylabel(r'$\Delta_\eta\,|C|$ at $\delta_0 = 0$', color='C0')
    ax2.set_ylabel(r'$\Delta_\eta\,\arg C$  (deg)', color='C3')
    ax.tick_params(axis='y', colors='C0')
    ax2.tick_params(axis='y', colors='C3')
    ax.set_title(r'Carrier slice — $\Delta_\eta$ vs $|\alpha|$')
    ax.grid(alpha=0.3)

    fig.suptitle(r'WP-E S1 — η-nonlinearity residuals  $\Delta_\eta = $ full − R1')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'S1_eta_residuals.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


# ═══════════════════════════════════════════════════════════════
# Figure 5 — R1 convergence cross-check
# ═══════════════════════════════════════════════════════════════

def plot_R1_convergence():
    with h5py.File(R1C_FILE, 'r') as f:
        det = f['detuning_rel'][:] * 1.3   # to MHz/(2π)
        alpha = f['alpha'][:]
        e04_sx = f['eta_0.04/sigma_x'][:]; e04_sy = f['eta_0.04/sigma_y'][:]
        e02_sx = f['eta_0.02/sigma_x'][:]; e02_sy = f['eta_0.02/sigma_y'][:]
    e04_C = np.sqrt(e04_sx**2 + e04_sy**2)
    e02_C = np.sqrt(e02_sx**2 + e02_sy**2)
    diff = e04_C - e02_C

    # Predicted scaling from quadratic residual: (η²_a − η²_b)/2
    predicted = (0.04**2 - 0.02**2) / 2

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    ax = axes[0]
    for i, a in enumerate(alpha):
        ax.plot(det, e04_C[i], label=fr'$|\alpha|={a:g}$, η = 0.04', lw=1.5)
        ax.plot(det, e02_C[i], '--', label=fr'$|\alpha|={a:g}$, η = 0.02', lw=1)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$|C|$')
    ax.set_title('R1 reference at two η values')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1]
    for i, a in enumerate(alpha):
        ax.plot(det, diff[i], label=fr'$|\alpha|={a:g}$', lw=1.5)
    ax.axhline(predicted, color='k', ls=':', lw=1,
               label=fr'predicted $({0.04**2-0.02**2:.4f})/2 = {predicted:.4f}$')
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$|C|(\eta=0.04) - |C|(\eta=0.02)$')
    ax.set_title('Residual matches the predicted quadratic scaling')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    fig.suptitle('WP-E — R1 convergence cross-check (Guardian flag 1)')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, 'R1_convergence.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


# ═══════════════════════════════════════════════════════════════
# Driver
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    d = load_S1()
    paths = []
    paths.append(plot_carrier_summary(d))
    paths.append(plot_contrast_maps(d))
    paths.append(plot_phase_maps(d))
    paths.append(plot_eta_residuals(d))
    paths.append(plot_R1_convergence())
    print('Wrote:')
    for p in paths:
        print(f'  {p}')
