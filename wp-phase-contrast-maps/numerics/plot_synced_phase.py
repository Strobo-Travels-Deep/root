#!/usr/bin/env python3
"""
plot_synced_phase.py — Flag 1 closure figure.

Three engines side by side at |α| ∈ {0, 3} over ±500 kHz zoom:
  synced — finite-δt pulses + inter-pulse Ufree (spin+motion), v0.9.1
           corrections. "Phase kept synced" convention (user 2026-04-14).
  engine — v0.9.1 current, omits inter-pulse Ufree at t_sep_factor=1.
  R2     — Monroe impulsive kicks + inter-pulse spin Ufree.

Shows synced ≡ R2 lineshape (comb) to within ~0.5%; engine is broad
single-peak. Flag 1 closed: the engine's lineshape is wrong under the
phase-synced experimental convention.
"""

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))

with h5py.File(os.path.join(SCRIPT_DIR, 'synced_phase_alpha0and3.h5'), 'r') as f:
    det_MHz = f['detuning_MHz_over_2pi'][:]
    alphas = list(f.attrs['alpha_values'])
    data = {}
    for a in alphas:
        g = f[f'alpha_{a:g}']
        data[a] = {}
        for k in ('synced', 'engine', 'R2'):
            sx = g[f'{k}/sx'][:]; sy = g[f'{k}/sy'][:]
            data[a][k] = np.sqrt(sx**2 + sy**2)

fig, axes = plt.subplots(2, 2, figsize=(13, 8))

for col, a in enumerate(alphas):
    # Linear scale
    ax = axes[0, col]
    ax.plot(det_MHz*1000, data[a]['engine'], '-', lw=1.2, color='C0',
            label='v0.9.1 engine (no inter-pulse U$_{\\rm gap}$)')
    ax.plot(det_MHz*1000, data[a]['synced'], '-', lw=1.2, color='C1',
            label='synced-phase (finite-δt + U$_{\\rm gap}$)')
    ax.plot(det_MHz*1000, data[a]['R2'],    '--', lw=1.0, color='C3',
            label='R2 Monroe (impulsive + U$_{\\rm gap}$)')
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (kHz)')
    ax.set_ylabel(r'$|C|$')
    ax.set_title(fr'$|\alpha| = {a:g}$ — linear')
    ax.grid(alpha=0.3); ax.legend(fontsize=8, loc='upper right')
    ax.set_ylim(-0.05, 1.02)

    # Log scale
    ax = axes[1, col]
    ax.semilogy(det_MHz*1000, np.maximum(data[a]['engine'], 1e-4), '-', lw=1.2,
                color='C0', label='engine')
    ax.semilogy(det_MHz*1000, np.maximum(data[a]['synced'], 1e-4), '-', lw=1.2,
                color='C1', label='synced-phase')
    ax.semilogy(det_MHz*1000, np.maximum(data[a]['R2'], 1e-4),    '--', lw=1.0,
                color='C3', label='R2 Monroe')
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (kHz)')
    ax.set_ylabel(r'$|C|$  (log)')
    ax.set_title(fr'$|\alpha| = {a:g}$ — log (synced overlaps R2)')
    ax.grid(alpha=0.3, which='both'); ax.legend(fontsize=8)
    ax.set_ylim(1e-3, 2)

fig.suptitle('WP-E Flag 1 closure: under phase-synced protocol, lineshape is the comb, '
             'not the engine\'s broad single peak')
fig.tight_layout()
out = os.path.join(PLOT_DIR, 'flag1_synced_phase_lineshape.png')
fig.savefig(out, dpi=140)
plt.close(fig)
print(f'Wrote {out}')
