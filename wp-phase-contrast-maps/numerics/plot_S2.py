#!/usr/bin/env python3
"""
plot_S2.py — Figures for WP-E S2 sheet (δ₀, φ_α) at fixed |α|.

Reads:
  numerics/S2_delta_phi_alpha{α}.h5

Writes (to plots/):
  S2_alpha{α}_summary.png       Headline: |C| vs (δ, φ_α) heatmap, arg C
                                heatmap, arg C(δ=0) vs φ_α with theory.
  S2_alpha{α}_residuals.png     Δ_η maps (full − R1) and slice cuts.

Documents the falsification of the |α|·|sin φ_α| Doppler-broadening
prediction from `2026-04-13-S1-plots.md` §2 — see logbook entry
`2026-04-13-S2-and-falsification.md`.
"""

import os, sys, glob
import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
os.makedirs(PLOT_DIR, exist_ok=True)

PHASE_MASK_THRESHOLD = 0.1


def wrap_deg(x):
    return ((x + 180) % 360) - 180


def load_S2(path):
    with h5py.File(path, 'r') as f:
        out = {
            'det_MHz': f['detuning_MHz_over_2pi'][:],
            'phi_deg': f['phi_alpha_deg'][:],
            'alpha': float(f.attrs['alpha']),
            'eta_full': float(f.attrs['eta_full']),
            'eta_R1': float(f.attrs['eta_R1']),
        }
        for tag in ('full', 'R1'):
            out[tag] = {k: f[f'{tag}/{k}'][:] for k in
                        ('sigma_x', 'sigma_y', 'sigma_z',
                         'C_abs', 'C_arg_deg', 'max_fock_leakage')}
    return out


def plot_S2_summary(d):
    a = d['alpha']
    det = d['det_MHz']; phi = d['phi_deg']
    Cf = d['full']['C_abs']
    af = wrap_deg(d['full']['C_arg_deg'])
    af_m = np.where(Cf >= PHASE_MASK_THRESHOLD, af, np.nan)
    extent = [det[0], det[-1], phi[0], phi[-1]]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    # |C| heatmap (full) — should show vertical bands (φ_α-independent)
    ax = axes[0,0]
    im = ax.imshow(Cf, aspect='auto', origin='lower', extent=extent,
                   cmap='viridis', vmin=0, vmax=1)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$\varphi_\alpha$  (deg)')
    ax.set_title(fr'$|C|_{{\rm full}}$ at $|\alpha|={a:g}$  (vertical bands → $\varphi_\alpha$-independent)')
    plt.colorbar(im, ax=ax, fraction=0.05)

    # arg C heatmap (full, masked) — should show rich φ_α structure
    ax = axes[0,1]
    im = ax.imshow(af_m, aspect='auto', origin='lower', extent=extent,
                   cmap='hsv', vmin=-180, vmax=180)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$\varphi_\alpha$  (deg)')
    ax.set_title(fr'$\arg C_{{\rm full}}$ (deg, masked $|C| < {PHASE_MASK_THRESHOLD}$)')
    plt.colorbar(im, ax=ax, fraction=0.05, label='deg')

    # |C|(δ) line cuts at sample φ_α — overlay completely
    ax = axes[1,0]
    sample_idxs = np.linspace(0, len(phi)-1, 8, dtype=int)
    for j in sample_idxs:
        ax.plot(det, Cf[j], lw=1.0, alpha=0.7,
                label=fr'$\varphi_\alpha = {phi[j]:.0f}°$')
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$|C|_{\rm full}$')
    ax.set_title(fr'$|C|(\delta_0)$ at 8 $\varphi_\alpha$ values — eight curves overlap exactly')
    ax.legend(fontsize=7, ncol=2); ax.grid(alpha=0.3)

    # arg C at δ=0 vs φ_α, with theory prediction
    ax = axes[1,1]
    i0 = int(np.argmin(np.abs(det)))
    arg0_full = wrap_deg(af[:, i0])
    arg0_R1 = wrap_deg(d['R1']['C_arg_deg'][:, i0])
    eta_full = d['eta_full']
    # Theory: matrix-element phase 2η|α|cos φ_α (modulo overall offset)
    # The S1 reference at φ_α=0 (cos=1) had arg C = -133.52° at α=3.
    # For visualisation, plot the theoretical structure
    phi_dense = np.linspace(0, 360, 361)
    me_phase = np.degrees(2 * eta_full * a * np.cos(np.radians(phi_dense)))
    # Anchor: at φ_α=0, theory phase = +136.48°; measured = -133.52°.
    # Difference = -270° (≡ +90° mod 360). This is the carrier rotation offset.
    offset_full = arg0_full[0] - 2 * eta_full * a * 180/np.pi
    me_phase_full_anchored = wrap_deg(me_phase + offset_full)

    eta_R1 = d['eta_R1']
    me_phase_R1 = np.degrees(2 * eta_R1 * a * np.cos(np.radians(phi_dense)))
    offset_R1 = arg0_R1[0] - 2 * eta_R1 * a * 180/np.pi
    me_phase_R1_anchored = wrap_deg(me_phase_R1 + offset_R1)

    ax.plot(phi, arg0_full, 'o-', color='C0', ms=4, label='measured (full)')
    ax.plot(phi_dense, me_phase_full_anchored, '-', color='C0', alpha=0.4, lw=1,
            label=r'theory: $+2\eta|\alpha|\cos\varphi_\alpha + $ offset (full)')
    ax.plot(phi, arg0_R1, 's-', color='C1', ms=4, label='measured (R1, η=0.04)')
    ax.plot(phi_dense, me_phase_R1_anchored, '-', color='C1', alpha=0.4, lw=1,
            label=r'theory: linear-η (R1)')
    ax.set_xlabel(r'$\varphi_\alpha$  (deg)')
    ax.set_ylabel(r'$\arg C(\delta_0=0)$  (deg)')
    ax.set_title(r'Position-phase channel: $\arg C(\delta_0=0)$ vs $\varphi_\alpha$')
    ax.set_xlim(0, 360)
    ax.set_ylim(-200, 200)
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    fig.suptitle(fr'WP-E S2 — $(\delta_0, \varphi_\alpha)$ at $|\alpha|={a:g}$  '
                 r'(falsifies $|\alpha|\cdot|\sin\varphi_\alpha|$ broadening)')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, f'S2_alpha{a:g}_summary.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def plot_S2_residuals(d):
    a = d['alpha']
    det = d['det_MHz']; phi = d['phi_deg']
    Cf = d['full']['C_abs']; Cr = d['R1']['C_abs']
    af = wrap_deg(d['full']['C_arg_deg']); ar = wrap_deg(d['R1']['C_arg_deg'])
    extent = [det[0], det[-1], phi[0], phi[-1]]

    Delta_C = Cf - Cr
    Delta_arg = wrap_deg(af - ar)
    mask = (Cf >= PHASE_MASK_THRESHOLD) & (Cr >= PHASE_MASK_THRESHOLD)
    Delta_arg_m = np.where(mask, Delta_arg, np.nan)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    # Δ|C| heatmap
    ax = axes[0,0]
    vmax = max(abs(Delta_C.min()), abs(Delta_C.max()))
    im = ax.imshow(Delta_C, aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', norm=TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax))
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$\varphi_\alpha$  (deg)')
    ax.set_title(r'$\Delta_\eta\,|C| = |C|_{\rm full} - |C|_{R1}$')
    plt.colorbar(im, ax=ax, fraction=0.05)

    # Δ arg C heatmap (masked)
    ax = axes[0,1]
    vmax = np.nanmax(np.abs(Delta_arg_m))
    im = ax.imshow(Delta_arg_m, aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', norm=TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax))
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$\varphi_\alpha$  (deg)')
    ax.set_title(fr'$\Delta_\eta\,\arg C$ (deg, masked)')
    plt.colorbar(im, ax=ax, fraction=0.05, label='deg')

    # |C|(φ) at carrier zoom — show φ-independence visually as a flat line
    ax = axes[1,0]
    i0 = int(np.argmin(np.abs(det)))
    ax.plot(phi, Cf[:, i0], 'o-', color='C0', ms=4, label='full at $\\delta_0 = 0$')
    ax.plot(phi, Cr[:, i0], 's-', color='C1', ms=4, label='R1 at $\\delta_0 = 0$')
    # Also show at a typical Doppler tail to confirm flat there too
    j_off = int(np.argmin(np.abs(det - 1.0)))   # δ = 1 MHz
    ax.plot(phi, Cf[:, j_off], '.', color='C0', alpha=0.5,
            label=fr'full at $\delta_0 = {det[j_off]:.2f}$ MHz')
    ax.plot(phi, Cr[:, j_off], '.', color='C1', alpha=0.5,
            label=fr'R1 at $\delta_0 = {det[j_off]:.2f}$ MHz')
    ax.set_xlabel(r'$\varphi_\alpha$  (deg)')
    ax.set_ylabel(r'$|C|$')
    ax.set_title(r'$|C|$ vs $\varphi_\alpha$ — flat $\Rightarrow$ no Doppler')
    ax.legend(fontsize=8); ax.grid(alpha=0.3); ax.set_xlim(0, 360)

    # Δ_η arg C at δ=0 vs φ_α — the η-driven phase residual
    ax = axes[1,1]
    Delta_arg_carrier = wrap_deg(Delta_arg_m[:, i0])
    ax.plot(phi, Delta_arg_carrier, 'o-', color='C3', ms=4)
    ax.set_xlabel(r'$\varphi_\alpha$  (deg)')
    ax.set_ylabel(r'$\Delta_\eta\,\arg C$ at $\delta_0 = 0$ (deg)')
    ax.set_title(r'$\Delta_\eta\,\arg C(\delta_0=0)$ vs $\varphi_\alpha$ — η-driven phase')
    ax.axhline(0, color='k', lw=0.5)
    ax.set_xlim(0, 360); ax.set_ylim(-200, 200)
    ax.grid(alpha=0.3)

    fig.suptitle(fr'WP-E S2 residuals at $|\alpha|={a:g}$  '
                 r'($\Delta_\eta\,|C| \approx -0.083$ constant; phase carries the signal)')
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, f'S2_alpha{a:g}_residuals.png')
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(SCRIPT_DIR, 'S2_delta_phi_alpha*.h5')))
    if not files:
        print('No S2 files found.')
        sys.exit(1)
    for f in files:
        print(f'\n--- {os.path.basename(f)} ---')
        d = load_S2(f)
        p1 = plot_S2_summary(d)
        p2 = plot_S2_residuals(d)
        print(f'  {p1}')
        print(f'  {p2}')
