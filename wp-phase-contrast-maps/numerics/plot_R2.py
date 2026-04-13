#!/usr/bin/env python3
"""
plot_R2.py — R2 reference (instantaneous-pulse idealisation) figure.

Reads:
  numerics/R2_delta_alpha.h5
  numerics/S1_delta_alpha.h5       (full + R1)
Writes:
  plots/R2_vs_full.png
"""

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))

with h5py.File(os.path.join(SCRIPT_DIR, 'R2_delta_alpha.h5'), 'r') as f:
    det = f['detuning_MHz_over_2pi'][:]
    alpha = f['alpha'][:]
    R2_C = f['R2/C_abs'][:]
    R12_C = f['R12/C_abs'][:]

with h5py.File(os.path.join(SCRIPT_DIR, 'S1_delta_alpha.h5'), 'r') as f:
    full_C = f['full/C_abs'][:]
    R1_C = f['R1/C_abs'][:]

omega_m = 1.3

fig, axes = plt.subplots(2, 2, figsize=(13, 8))

# Top-left: full vs R2 at α=0 over full detuning range
ax = axes[0, 0]
ax.plot(det, full_C[0], lw=1.5, label=r'full (η = 0.397)')
ax.plot(det, R2_C[0], lw=1.0, label=r'R2 (η = 0.397, δt → 0)')
# Mark sideband positions
for k in range(-4, 5):
    ax.axvline(k * omega_m, color='gray', ls=':', lw=0.5, alpha=0.4)
ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
ax.set_ylabel(r'$|C|$')
ax.set_title(r'$|\alpha| = 0$: full engine lineshape vs R2 comb')
ax.legend(fontsize=9); ax.grid(alpha=0.3); ax.set_xlim(-6, 6)

# Top-right: central zoom showing R2 very narrow peak
ax = axes[0, 1]
mask = np.abs(det) < 1.5
ax.plot(det[mask], full_C[0, mask], 'o-', lw=1.5, ms=3, label='full')
ax.plot(det[mask], R2_C[0, mask], 's-', lw=1.0, ms=3, label='R2')
ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
ax.set_ylabel(r'$|C|$')
ax.set_title(r'Central zoom — R2 narrow peak vs full broad lineshape')
ax.legend(fontsize=9); ax.grid(alpha=0.3)

# Bottom-left: R1 vs R12 (the low-η pair)
ax = axes[1, 0]
ax.plot(det, R1_C[0], lw=1.5, label=r'R1 (η = 0.04)')
ax.plot(det, R12_C[0], lw=1.0, label=r'R12 (η = 0.04, δt → 0)')
for k in range(-4, 5):
    ax.axvline(k * omega_m, color='gray', ls=':', lw=0.5, alpha=0.4)
ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
ax.set_ylabel(r'$|C|$')
ax.set_title(r'$|\alpha| = 0$: R1 vs R12 (small-η pair)')
ax.legend(fontsize=9); ax.grid(alpha=0.3); ax.set_xlim(-6, 6)

# Bottom-right: carrier and sideband values across engines (α=3 here)
ax = axes[1, 1]
i0 = int(np.argmin(np.abs(det)))
# Extract values at sideband positions δ = k·ω_m
ks = np.arange(-4, 5)
delta_sidebands = ks * omega_m
j_sb = [int(np.argmin(np.abs(det - d))) for d in delta_sidebands]
ax.plot(ks, [full_C[2, j] for j in j_sb], 'o-', label=r'full, $|\alpha|=3$')
ax.plot(ks, [R2_C[2, j] for j in j_sb], 's-', label=r'R2, $|\alpha|=3$')
ax.plot(ks, [R1_C[2, j] for j in j_sb], '^-', label=r'R1, $|\alpha|=3$')
ax.plot(ks, [R12_C[2, j] for j in j_sb], 'd-', label=r'R12, $|\alpha|=3$')
ax.set_xlabel(r'sideband index $k$ at $\delta = k\omega_m$')
ax.set_ylabel(r'$|C|$')
ax.set_title(r'Values at $\delta = k\omega_m$ (|α| = 3)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.set_xticks(ks)

fig.suptitle(r'WP-E R2 — instantaneous-pulse idealisation; stroboscopic aliasing $\delta \rightarrow \delta + \omega_m$')
fig.tight_layout()
out = os.path.join(PLOT_DIR, 'R2_vs_full.png')
fig.savefig(out, dpi=140)
plt.close(fig)
print(f'Wrote {out}')
