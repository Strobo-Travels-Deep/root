#!/usr/bin/env python3
"""
plot_aom_envelope.py — AOM erf-envelope effect on the WP-E observables.

Panels:
  1. Envelope shapes f(t) for σ ∈ {0 (rect), 20, 50} ns.
  2. arg C(φ_α) − theory residuals at δ=0, α=3 under each envelope.
  3. |C|(φ_α) at δ=0, α=3 under each envelope — spread narrows with σ.
  4. Trend: γ_c and |C|-spread vs area fraction.
"""

import os, numpy as np, h5py, matplotlib.pyplot as plt
from scipy.special import erf

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))

OMEGA_M = 1.3; T_M = 2 * np.pi / OMEGA_M
DELTA_T = 0.13 * T_M; ETA = 0.397; ALPHA = 3.0


def envelope(t, dt, sigma):
    if sigma <= 0:
        return np.where((t > 0) & (t < dt), 1.0, 0.0)
    t_L, t_R = 3 * sigma, dt - 3 * sigma
    rise = 0.5 * (1 + erf((t - t_L) / (sigma * np.sqrt(2))))
    fall = 0.5 * (1 + erf((t_R - t) / (sigma * np.sqrt(2))))
    return rise * fall


def wrap_deg(x): return ((x + 180) % 360) - 180


def unwrap_anchor(arg_w):
    uw = np.degrees(np.unwrap(np.radians(arg_w)))
    return uw - uw[0] + 90.0


def load_sigma50():
    with h5py.File(os.path.join(SCRIPT_DIR, 'aom_envelope_carrier_phi.h5'), 'r') as f:
        return f['phi_alpha_deg'][:], f['sigma_x'][:], f['sigma_y'][:]


def load_sigma20():
    with h5py.File(os.path.join(SCRIPT_DIR, 'aom_envelope_carrier_phi_sigma20.h5'), 'r') as f:
        return f['phi_alpha_deg'][:], f['sigma_x'][:], f['sigma_y'][:]


def load_rect():
    with h5py.File(os.path.join(SCRIPT_DIR, 'S2_v09_alpha3.h5'), 'r') as f:
        det = f['detuning_MHz_over_2pi'][:]
        i0 = int(np.argmin(np.abs(det)))
        return f['phi_alpha_deg'][:], f['sigma_x'][:, i0], f['sigma_y'][:, i0]


phi_r, sx_r, sy_r = load_rect()
phi_20, sx_20, sy_20 = load_sigma20()
phi_50, sx_50, sy_50 = load_sigma50()

def summarise(phi, sx, sy):
    C = np.sqrt(sx**2 + sy**2)
    arg_w = wrap_deg(np.degrees(np.arctan2(sy, sx)))
    arg_uw = unwrap_anchor(arg_w)
    theory = 90 + np.degrees(2 * ETA * ALPHA * (np.cos(np.radians(phi)) - 1))
    resid = arg_uw - theory
    rng = arg_uw.max() - arg_uw.min()
    gamma_c = rng / (4 * ETA * ALPHA * 180 / np.pi)
    return C, arg_uw, resid, gamma_c

C_r, arg_r_uw, resid_r, g_r = summarise(phi_r, sx_r, sy_r)
C_20, arg_20_uw, resid_20, g_20 = summarise(phi_20, sx_20, sy_20)
C_50, arg_50_uw, resid_50, g_50 = summarise(phi_50, sx_50, sy_50)

fig, axes = plt.subplots(2, 2, figsize=(13, 8))

# Panel 1: envelopes
ax = axes[0, 0]
t = np.linspace(-0.1, DELTA_T + 0.1, 500)
ax.plot(t * 1000, envelope(t, DELTA_T, 0), lw=2, label='rect (σ=0 ns)')
ax.plot(t * 1000, envelope(t, DELTA_T, 0.020), lw=2, label='σ=20 ns (τ_rise 10–90% ≈ 51 ns)')
ax.plot(t * 1000, envelope(t, DELTA_T, 0.050), lw=2, label='σ=50 ns (slow AOM)')
ax.axvspan(0, DELTA_T * 1000, color='gray', alpha=0.08)
ax.set_xlabel('time (ns)')
ax.set_ylabel(r'$f(t)$')
ax.set_title(fr'Pulse envelope, $\delta t_{{\rm total}}$ = {DELTA_T*1000:.1f} ns')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 2: arg residuals vs φ_α
ax = axes[0, 1]
ax.plot(phi_r,  resid_r,  'o-', ms=3, lw=1, label=f'rect, RMS {np.sqrt(np.mean(resid_r**2)):.2f}°')
ax.plot(phi_20, resid_20, 's-', ms=3, lw=1, label=f'σ=20 ns, RMS {np.sqrt(np.mean(resid_20**2)):.2f}°')
ax.plot(phi_50, resid_50, '^-', ms=3, lw=1, label=f'σ=50 ns, RMS {np.sqrt(np.mean(resid_50**2)):.2f}°')
ax.axhline(0, color='k', lw=0.5)
ax.set_xlim(0, 360)
ax.set_xlabel(r'$\varphi_\alpha$ (deg)')
ax.set_ylabel(r'arg C − theory (deg)')
ax.set_title(r'Residual vs theory $90° + 2\eta|\alpha|\cos\varphi_\alpha$')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 3: |C|(φ_α)
ax = axes[1, 0]
ax.plot(phi_r,  C_r,  'o-', ms=3, lw=1, label=f'rect, Δ={C_r.max()-C_r.min():.3f}')
ax.plot(phi_20, C_20, 's-', ms=3, lw=1, label=f'σ=20 ns, Δ={C_20.max()-C_20.min():.3f}')
ax.plot(phi_50, C_50, '^-', ms=3, lw=1, label=f'σ=50 ns, Δ={C_50.max()-C_50.min():.3f}')
ax.set_xlim(0, 360)
ax.set_xlabel(r'$\varphi_\alpha$ (deg)')
ax.set_ylabel(r'$|C|$ at $\delta_0 = 0$')
ax.set_title(r'$|C|(\varphi_\alpha)$ spread narrows with softer edges')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 4: γ_c and spread vs area fraction
area_fracs = [1.000, 0.809, 0.522]
gammas = [g_r, g_20, g_50]
spreads = [C_r.max()-C_r.min(), C_20.max()-C_20.min(), C_50.max()-C_50.min()]
labels = ['rect', 'σ=20 ns', 'σ=50 ns']

ax = axes[1, 1]
ax.plot(area_fracs, gammas, 'o-', lw=1.5, ms=8, color='C0', label=r'$\gamma_c$ (left axis)')
for xi, yi, lab in zip(area_fracs, gammas, labels):
    ax.annotate(lab, (xi, yi), xytext=(5, 5), textcoords='offset points', fontsize=8)
ax.set_ylim(0.965, 1.005)
ax.set_xlabel('envelope area fraction')
ax.set_ylabel(r'$\gamma_c$', color='C0')
ax.tick_params(axis='y', colors='C0')
ax.grid(alpha=0.3)

ax2 = ax.twinx()
ax2.plot(area_fracs, spreads, 's-', lw=1.5, ms=8, color='C3', label=r'$|C|$ spread')
ax2.set_ylabel(r'$|C|(\varphi_\alpha)$ spread', color='C3')
ax2.tick_params(axis='y', colors='C3')
ax.set_title(r'Softer AOM edges → $\gamma_c \to 1$, $|C|$ spread $\to 0$')
# v0.8 horizontal line
ax.axhline(1.0, color='k', lw=0.5, ls=':', alpha=0.5)
ax.text(0.55, 1.001, 'v0.8 frozen-motion limit (γ_c=1)', fontsize=7, alpha=0.7)

fig.suptitle(r'WP-E: AOM erf-envelope effect on v0.9.1 γ-corrections ($|\alpha|=3$, $\eta=0.397$, $\delta_0=0$)')
fig.tight_layout()
out = os.path.join(PLOT_DIR, 'aom_envelope_carrier.png')
fig.savefig(out, dpi=140)
plt.close(fig)
print(f'Wrote {out}')
