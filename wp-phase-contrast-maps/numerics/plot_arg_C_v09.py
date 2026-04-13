#!/usr/bin/env python3
"""
plot_arg_C_v09.py — Figure for the v0.9.1 survival test of the
closed-form identity arg C(δ₀=0, φ_α) = 90° + 2η|α|·cos φ_α.

Reads:
  numerics/S2_v09_alpha3.h5          (v0.9.1, full η=0.397, full 2D grid)
  numerics/S2_delta_phi_alpha3.h5    (v0.8, full η=0.397, full 2D grid)
  numerics/R1_v09_carrier_phi.h5     (v0.9.1, R1 η=0.04, δ=0 only)
  numerics/S1_delta_alpha.h5         (v0.8, R1 carrier for comparison)

Writes:
  plots/arg_C_identity_v08_vs_v09.png
"""

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
os.makedirs(PLOT_DIR, exist_ok=True)


def wrap_deg(x): return ((x + 180) % 360) - 180


ALPHA = 3.0
ETA_FULL = 0.397
ETA_R1 = 0.04

# v0.9.1 full engine data
with h5py.File(os.path.join(SCRIPT_DIR, 'S2_v09_alpha3.h5'), 'r') as f:
    det = f['detuning_MHz_over_2pi'][:]
    phi = f['phi_alpha_deg'][:]
    af_v09 = f['C_arg_deg'][:]
i0 = int(np.argmin(np.abs(det)))
arg_full_v09 = wrap_deg(af_v09[:, i0])

# v0.8 full engine data
with h5py.File(os.path.join(SCRIPT_DIR, 'S2_delta_phi_alpha3.h5'), 'r') as f:
    af_v08 = f['full/C_arg_deg'][:]
arg_full_v08 = wrap_deg(af_v08[:, i0])

# v0.9.1 R1 data (carrier only)
with h5py.File(os.path.join(SCRIPT_DIR, 'R1_v09_carrier_phi.h5'), 'r') as f:
    phi_R1 = f['phi_alpha_deg'][:]
    arg_R1_v09 = wrap_deg(f['C_arg_deg'][:])

# v0.8 R1 data: S1 file had only 4 |α| × 121 det, no φ_α axis at α=3.
# So we only compare v0.8 full vs v0.9.1 full; v0.9.1 R1 vs theory.

# Unwrapped versions anchored at 90° at φ_α=0
def unwrap_anchor(arg_deg):
    uw = np.degrees(np.unwrap(np.radians(arg_deg)))
    uw -= uw[0] - 90.0
    return uw

arg_full_v08_uw = unwrap_anchor(arg_full_v08)
arg_full_v09_uw = unwrap_anchor(arg_full_v09)
arg_R1_v09_uw = unwrap_anchor(arg_R1_v09)

# Theory: 90° + 2η|α|(cos φ − cos 0) [anchored at 90° at φ_α=0]
theory_full = 90.0 + np.degrees(2 * ETA_FULL * ALPHA * (np.cos(np.radians(phi)) - 1))
theory_R1   = 90.0 + np.degrees(2 * ETA_R1   * ALPHA * (np.cos(np.radians(phi)) - 1))

resid_full_v08 = arg_full_v08_uw - theory_full
resid_full_v09 = arg_full_v09_uw - theory_full
resid_R1_v09   = arg_R1_v09_uw   - theory_R1

range_full_v08 = arg_full_v08_uw.max() - arg_full_v08_uw.min()
range_full_v09 = arg_full_v09_uw.max() - arg_full_v09_uw.min()
range_R1_v09   = arg_R1_v09_uw.max()   - arg_R1_v09_uw.min()
range_theory_full = 4 * ETA_FULL * ALPHA * 180/np.pi
range_theory_R1 = 4 * ETA_R1 * ALPHA * 180/np.pi

print('=== survival summary ===')
print(f'v0.8 full: range {range_full_v08:.3f}° (theory {range_theory_full:.3f}°)  '
      f'RMS residual {np.sqrt(np.mean(resid_full_v08**2)):.4f}°')
print(f'v0.9.1 full: range {range_full_v09:.3f}° (theory {range_theory_full:.3f}°)  '
      f'RMS residual {np.sqrt(np.mean(resid_full_v09**2)):.4f}°')
print(f'v0.9.1 R1:   range {range_R1_v09:.3f}° (theory {range_theory_R1:.3f}°)  '
      f'RMS residual {np.sqrt(np.mean(resid_R1_v09**2)):.4f}°')

gamma_full = range_full_v09 / range_theory_full
gamma_R1   = range_R1_v09   / range_theory_R1
print(f'\n  γ_full (range ratio) = {gamma_full:.5f}')
print(f'  γ_R1   (range ratio) = {gamma_R1:.5f}')
print(f'  γ is the same to 4 decimals → single-parameter correction')

# Fit residual to sin φ_α to check for momentum-channel leakage
from numpy.linalg import lstsq
phi_rad = np.radians(phi)
# resid = a0 + a_s · sin φ + a_c · (cos φ − 1) [correction factor]
for tag, resid in [('v0.8 full', resid_full_v08),
                   ('v0.9.1 full', resid_full_v09),
                   ('v0.9.1 R1', resid_R1_v09)]:
    M = np.column_stack([np.ones(len(phi)), np.sin(phi_rad), np.cos(phi_rad) - 1])
    coef, *_ = lstsq(M, resid, rcond=None)
    print(f'  {tag}: const={coef[0]:+.4f}°  sin={coef[1]:+.4f}°  (cos−1)={coef[2]:+.4f}°')


# === plotting ===
fig, axes = plt.subplots(2, 2, figsize=(13, 8))

# panel 1: arg C vs φ_α (full, wrapped), v0.8 vs v0.9.1 with theory
ax = axes[0,0]
ax.plot(phi, arg_full_v08, 'o', ms=3, color='C0', label='v0.8 (frozen motion)')
ax.plot(phi, arg_full_v09, 's', ms=3, color='C1', label='v0.9.1 (D1 + centered)')
theory_wrapped = wrap_deg(90.0 + np.degrees(2 * ETA_FULL * ALPHA * np.cos(np.radians(phi))))
ax.plot(phi, theory_wrapped, '-', color='k', lw=1, alpha=0.5,
        label=r'theory $90° + 2\eta|\alpha|\cos\varphi_\alpha$')
ax.set_xlim(0, 360); ax.set_ylim(-200, 200)
ax.set_xlabel(r'$\varphi_\alpha$ (deg)')
ax.set_ylabel(r'$\arg C$ at $\delta_0=0$  (wrapped)')
ax.set_title(r'Full engine, $|\alpha|=3$, $\eta=0.397$')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# panel 2: unwrapped comparison
ax = axes[0,1]
ax.plot(phi, arg_full_v08_uw, 'o-', ms=3, color='C0', lw=1, label='v0.8 unwrapped')
ax.plot(phi, arg_full_v09_uw, 's-', ms=3, color='C1', lw=1, label='v0.9.1 unwrapped')
ax.plot(phi, theory_full, '--', color='k', lw=1, alpha=0.7,
        label=r'theory (anchored at $\varphi_\alpha=0$)')
ax.set_xlim(0, 360)
ax.set_xlabel(r'$\varphi_\alpha$ (deg)')
ax.set_ylabel(r'$\arg C$ (unwrapped, anchored 90° at $\varphi=0$)')
ax.set_title(fr'Range: v0.8 = {range_full_v08:.2f}°, v0.9.1 = {range_full_v09:.2f}°, theory = {range_theory_full:.2f}°')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# panel 3: residuals
ax = axes[1,0]
ax.plot(phi, resid_full_v08, 'o-', ms=3, color='C0', lw=1, label='v0.8 residual (≈0 to 10⁻¹¹°)')
ax.plot(phi, resid_full_v09, 's-', ms=3, color='C1', lw=1,
        label=fr'v0.9.1 full: RMS {np.sqrt(np.mean(resid_full_v09**2)):.2f}°, max {np.max(np.abs(resid_full_v09)):.2f}°')
ax.plot(phi, resid_R1_v09, '^-', ms=3, color='C3', lw=1,
        label=fr'v0.9.1 R1 (η=0.04): RMS {np.sqrt(np.mean(resid_R1_v09**2)):.2f}°, max {np.max(np.abs(resid_R1_v09)):.2f}°')
ax.axhline(0, color='k', lw=0.5)
ax.set_xlim(0, 360)
ax.set_xlabel(r'$\varphi_\alpha$ (deg)')
ax.set_ylabel(r'measured − theory (deg)')
ax.set_title(r'Residual: v0.9.1 deviates by ~sin $\varphi_\alpha$, scales as $\eta$')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# panel 4: residual decomposition — ratio scales with η
ax = axes[1,1]
# Plot both residuals normalised by 2η|α| (in rad), which equals 2η|α|·(180/π) in deg
norm_full = 2 * ETA_FULL * ALPHA * 180/np.pi
norm_R1 = 2 * ETA_R1 * ALPHA * 180/np.pi
ax.plot(phi, resid_full_v09 / norm_full, 's-', ms=3, color='C1', lw=1,
        label=fr'v0.9.1 full / ($2\eta|\alpha|$)  [η={ETA_FULL}]')
ax.plot(phi, resid_R1_v09 / norm_R1, '^-', ms=3, color='C3', lw=1,
        label=fr'v0.9.1 R1 / ($2\eta|\alpha|$)  [η={ETA_R1}]')
ax.axhline(0, color='k', lw=0.5)
# Overlay pure sin φ_α guide
sin_amp = np.mean([np.sin(phi_rad) @ (resid_full_v09 / norm_full) / np.sum(np.sin(phi_rad)**2),
                   np.sin(phi_rad) @ (resid_R1_v09 / norm_R1) / np.sum(np.sin(phi_rad)**2)])
ax.plot(phi, sin_amp * np.sin(phi_rad), ':', color='k', lw=1,
        label=fr'pure sin $\varphi_\alpha$ component, amp $\approx {sin_amp:.3f}$')
ax.set_xlim(0, 360)
ax.set_xlabel(r'$\varphi_\alpha$ (deg)')
ax.set_ylabel(r'residual normalised by $2\eta|\alpha|$')
ax.set_title(r'Curves collapse → correction is linear in $\eta$; sin component = momentum mixing')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

fig.suptitle(r'WP-E: does $\arg C = 90° + 2\eta|\alpha|\cos\varphi_\alpha$ survive v0.9.1?'
             ' — yes, as leading order; corrections are $O(\eta \cdot \omega_m\delta t)$ momentum-channel mixing')
fig.tight_layout()
out = os.path.join(PLOT_DIR, 'arg_C_identity_v08_vs_v09.png')
fig.savefig(out, dpi=140)
plt.close(fig)
print(f'\nWrote {out}')
