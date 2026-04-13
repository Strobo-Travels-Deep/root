#!/usr/bin/env python3
"""
plot_H1.py — Floquet lock-tolerance figure.

Reads  numerics/H1_lock_tolerance.h5
Writes plots/H1_lock_tolerance.png
"""

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))

with h5py.File(os.path.join(SCRIPT_DIR, 'H1_lock_tolerance.h5'), 'r') as f:
    eps = f['epsilon'][:]
    alpha = f['alpha'][:]
    C = f['C_abs'][:]
    sz = f['sigma_z'][:]

# Published Hasse2024 tolerance Δω_m/ω_m ≲ 1/(2π·N) = 0.72 %.
pub_tol = 1.0 / (2 * np.pi * 22)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

ax = axes[0]
for i, a in enumerate(alpha):
    ax.plot(eps * 100, C[i], '.-', ms=4, lw=1, label=fr'$|\alpha| = {a:g}$')
ax.axvspan(-pub_tol * 100, +pub_tol * 100, color='gray', alpha=0.15,
           label=fr'published $\pm 1/(2\pi N) = \pm {pub_tol*100:.2f}\%$')
ax.axvline(0, color='k', lw=0.5)
ax.set_xlabel(r'$\varepsilon = \omega_{\rm pulse}/\omega_m - 1$  (%)')
ax.set_ylabel(r'$|C|$ at $\delta_0 = 0$')
ax.set_title(r'H1 — Floquet lock-tolerance')
ax.legend(fontsize=9); ax.grid(alpha=0.3); ax.set_ylim(0, 1.02)

ax = axes[1]
for i, a in enumerate(alpha):
    ax.plot(eps * 100, sz[i], '.-', ms=4, lw=1, label=fr'$|\alpha| = {a:g}$')
ax.axvspan(-pub_tol * 100, +pub_tol * 100, color='gray', alpha=0.15)
ax.axvline(0, color='k', lw=0.5)
ax.axhline(0, color='k', lw=0.5)
ax.set_xlabel(r'$\varepsilon = \omega_{\rm pulse}/\omega_m - 1$  (%)')
ax.set_ylabel(r'$\langle\sigma_z\rangle$ at $\delta_0 = 0$')
ax.set_title(r'H1 — $\sigma_z$ vs $\varepsilon$')
ax.legend(fontsize=9); ax.grid(alpha=0.3); ax.set_ylim(-1.05, 1.05)

fig.suptitle(r'WP-E H1 — stroboscopic lock tolerance; $|\alpha|$-dependent decoherence window')
fig.tight_layout()
out = os.path.join(PLOT_DIR, 'H1_lock_tolerance.png')
fig.savefig(out, dpi=140)
plt.close(fig)
print(f'Wrote {out}')
