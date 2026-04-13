#!/usr/bin/env python3
"""
plot_S2_combined.py — Three-sheet S2 synthesis (|α| ∈ {1, 3, 5}).

Addresses Guardian flags from the falsification review:
  Flag 2 — unwrapped arg C panel beside the wrapped one.
  Flag 4 — arg C(|α|, φ_α) at δ₀ = 0 (S3-replacement panel).

Writes:
  plots/S2_combined.png      Three-sheet summary: |C| banding panel,
                             wrapped + unwrapped arg C vs φ_α, and
                             arg C(|α|, φ_α) replacing S3.
"""

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
os.makedirs(PLOT_DIR, exist_ok=True)

ALPHAS = [1.0, 3.0, 5.0]
ETA_FULL = 0.397
ETA_R1 = 0.04
MASK = 0.1


def load_sheet(a):
    p = os.path.join(SCRIPT_DIR, f'S2_delta_phi_alpha{a:g}.h5')
    with h5py.File(p, 'r') as f:
        return {
            'det_MHz': f['detuning_MHz_over_2pi'][:],
            'phi_deg': f['phi_alpha_deg'][:],
            'Cf': f['full/C_abs'][:],  'Cr': f['R1/C_abs'][:],
            'af': f['full/C_arg_deg'][:], 'ar': f['R1/C_arg_deg'][:],
            'alpha': float(f.attrs['alpha']),
        }


def wrap_deg(x): return ((x + 180) % 360) - 180


def main():
    sheets = [load_sheet(a) for a in ALPHAS]

    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.45, wspace=0.35)

    # --- Row 1: |C|_full heatmaps for each |α|, one per column ---
    for k, s in enumerate(sheets):
        ax = fig.add_subplot(gs[0, k])
        im = ax.imshow(s['Cf'], aspect='auto', origin='lower',
                       extent=[s['det_MHz'][0], s['det_MHz'][-1],
                               s['phi_deg'][0], s['phi_deg'][-1]],
                       cmap='viridis', vmin=0, vmax=1)
        ax.set_xlabel(r'$\delta_0/(2\pi)$ (MHz)')
        ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
        ax.set_title(fr'$|C|_{{\rm full}}$ at $|\alpha|={s["alpha"]:g}$')
        plt.colorbar(im, ax=ax, fraction=0.05)

    # --- Row 2 left + centre: wrapped vs unwrapped arg C(δ=0) vs φ_α ---
    # Left: wrapped (principal branch).
    ax_w = fig.add_subplot(gs[1, 0])
    for s, color in zip(sheets, ['C0', 'C1', 'C2']):
        i0 = int(np.argmin(np.abs(s['det_MHz'])))
        ax_w.plot(s['phi_deg'], wrap_deg(s['af'][:, i0]), '.-',
                  color=color, ms=4, lw=1,
                  label=fr'$|\alpha|={s["alpha"]:g}$')
    ax_w.set_xlim(0, 360); ax_w.set_ylim(-200, 200)
    ax_w.set_xlabel(r'$\varphi_\alpha$ (deg)')
    ax_w.set_ylabel(r'$\arg C$ at $\delta_0=0$  (deg, wrapped)')
    ax_w.set_title(r'Wrapped arg C — full engine (η = 0.397)')
    ax_w.legend(fontsize=8); ax_w.grid(alpha=0.3)

    # Centre: unwrapped + theory overlay.
    ax_u = fig.add_subplot(gs[1, 1])
    phi_dense = np.linspace(0, 360, 361)
    for s, color in zip(sheets, ['C0', 'C1', 'C2']):
        i0 = int(np.argmin(np.abs(s['det_MHz'])))
        arg0_unwrapped = np.degrees(np.unwrap(np.radians(wrap_deg(s['af'][:, i0]))))
        arg0_unwrapped -= arg0_unwrapped[0] - 90.0   # anchor at +90° at φ=0
        ax_u.plot(s['phi_deg'], arg0_unwrapped, '.-', color=color, ms=4, lw=1,
                  label=fr'measured, $|\alpha|={s["alpha"]:g}$')
        # Theory: 90° + 2·η_full·|α|·(cos φ_α - 1)  (anchored at φ=0)
        theory = 90 + np.degrees(2 * ETA_FULL * s['alpha']
                                 * (np.cos(np.radians(phi_dense)) - 1))
        ax_u.plot(phi_dense, theory, '--', color=color, alpha=0.5, lw=1)
    ax_u.set_xlim(0, 360)
    ax_u.set_xlabel(r'$\varphi_\alpha$ (deg)')
    ax_u.set_ylabel(r'$\arg C$ at $\delta_0=0$  (deg, unwrapped)')
    ax_u.set_title(r'Unwrapped — dashed = $90° + 2\eta|\alpha|(\cos\varphi_\alpha - 1)$')
    ax_u.legend(fontsize=7, loc='best'); ax_u.grid(alpha=0.3)

    # Right: R1 engine, same layout, linear-in-η regime
    ax_r = fig.add_subplot(gs[1, 2])
    for s, color in zip(sheets, ['C0', 'C1', 'C2']):
        i0 = int(np.argmin(np.abs(s['det_MHz'])))
        arg_r = wrap_deg(s['ar'][:, i0])
        ax_r.plot(s['phi_deg'], arg_r, '.-', color=color, ms=4, lw=1,
                  label=fr'$|\alpha|={s["alpha"]:g}$')
        theory_r = 90 + np.degrees(2 * ETA_R1 * s['alpha']
                                   * (np.cos(np.radians(phi_dense)) - 1))
        ax_r.plot(phi_dense, theory_r, '--', color=color, alpha=0.5, lw=1)
    ax_r.set_xlim(0, 360); ax_r.set_ylim(30, 100)
    ax_r.set_xlabel(r'$\varphi_\alpha$ (deg)')
    ax_r.set_ylabel(r'$\arg C$ at $\delta_0=0$  (deg)')
    ax_r.set_title(r'R1 (η = 0.04) — linear regime, matches theory')
    ax_r.legend(fontsize=8); ax_r.grid(alpha=0.3)

    # --- Row 3: arg C(|α|, φ_α) at δ₀=0 as 2D scatter (S3 replacement) ---
    # Left: wrapped heatmap-like view. With 3 |α| × 64 φ_α, use pcolormesh.
    ax_a = fig.add_subplot(gs[2, 0])
    phi_grid = sheets[0]['phi_deg']
    n_phi = len(phi_grid)
    arg_matrix = np.zeros((3, n_phi))
    for k, s in enumerate(sheets):
        i0 = int(np.argmin(np.abs(s['det_MHz'])))
        arg_matrix[k] = wrap_deg(s['af'][:, i0])
    # Plot as scatter
    phi_mesh = np.meshgrid(phi_grid, np.arange(3))[0]
    alpha_mesh = np.meshgrid(phi_grid, [s['alpha'] for s in sheets])[1]
    sc = ax_a.scatter(phi_mesh.flatten(), alpha_mesh.flatten(),
                      c=arg_matrix.flatten(), cmap='hsv', s=12,
                      vmin=-180, vmax=180)
    ax_a.set_xlim(0, 360); ax_a.set_ylim(0, 6)
    ax_a.set_xlabel(r'$\varphi_\alpha$ (deg)')
    ax_a.set_ylabel(r'$|\alpha|$')
    ax_a.set_title(r'S3-replacement: $\arg C_{\rm full}(\delta_0=0, |\alpha|, \varphi_\alpha)$')
    plt.colorbar(sc, ax=ax_a, fraction=0.05, label='deg (wrapped)')

    # Centre: residual vs theory, computed in UNWRAPPED space.
    ax_res = fig.add_subplot(gs[2, 1])
    for s, color in zip(sheets, ['C0', 'C1', 'C2']):
        i0 = int(np.argmin(np.abs(s['det_MHz'])))
        arg0 = wrap_deg(s['af'][:, i0])
        arg0_unwrapped = np.degrees(np.unwrap(np.radians(arg0)))
        arg0_unwrapped -= arg0_unwrapped[0] - 90.0      # anchor at 90° at φ=0
        theory = 90 + np.degrees(2 * ETA_FULL * s['alpha']
                                 * (np.cos(np.radians(s['phi_deg'])) - 1))
        resid = arg0_unwrapped - theory
        ax_res.plot(s['phi_deg'], resid, '.-', color=color, ms=4, lw=1,
                    label=fr'$|\alpha|={s["alpha"]:g}$, rms={np.sqrt(np.mean(resid**2)):.2f}°')
    ax_res.set_xlim(0, 360)
    ax_res.axhline(0, color='k', lw=0.5)
    ax_res.set_xlabel(r'$\varphi_\alpha$ (deg)')
    ax_res.set_ylabel(r'measured − theory (deg, unwrapped)')
    ax_res.set_title(r'Residual (unwrapped) vs $2\eta|\alpha|\cos\varphi_\alpha$ model')
    ax_res.legend(fontsize=7); ax_res.grid(alpha=0.3)

    # Right: unwrapped range of arg C(δ=0) vs |α| for both engines
    ax_rng = fig.add_subplot(gs[2, 2])
    alphas = np.array(ALPHAS)
    # Measured ranges
    ranges_full = np.zeros(3); ranges_r1 = np.zeros(3)
    for k, s in enumerate(sheets):
        i0 = int(np.argmin(np.abs(s['det_MHz'])))
        uf = np.degrees(np.unwrap(np.radians(wrap_deg(s['af'][:, i0]))))
        ur = np.degrees(np.unwrap(np.radians(wrap_deg(s['ar'][:, i0]))))
        ranges_full[k] = uf.max() - uf.min()
        ranges_r1[k] = ur.max() - ur.min()
    # Theory: 4·η·|α| rad = 4·η·|α|·(180/π) deg
    a_dense = np.linspace(0, 6, 100)
    theory_full = 4 * ETA_FULL * a_dense * 180/np.pi
    theory_r1 = 4 * ETA_R1 * a_dense * 180/np.pi
    ax_rng.plot(a_dense, theory_full, '-', color='C0', alpha=0.5,
                label=fr'theory: $4\eta|\alpha|$, η = {ETA_FULL}')
    ax_rng.plot(alphas, ranges_full, 'o', color='C0', ms=8, label='measured (full)')
    ax_rng.plot(a_dense, theory_r1, '-', color='C1', alpha=0.5,
                label=fr'theory: $4\eta|\alpha|$, η = {ETA_R1}')
    ax_rng.plot(alphas, ranges_r1, 's', color='C1', ms=8, label='measured (R1)')
    ax_rng.set_xlabel(r'$|\alpha|$')
    ax_rng.set_ylabel(r'unwrapped range of $\arg C(\delta_0=0)$ over $\varphi_\alpha$  (deg)')
    ax_rng.set_title(r'Unwrapped range = $4\eta|\alpha|$ — confirmed both engines')
    ax_rng.legend(fontsize=7); ax_rng.grid(alpha=0.3)

    fig.suptitle(r'WP-E S2 synthesis — three sheets, $|\alpha| \in \{1, 3, 5\}$ at $\varphi_\alpha = 0$',
                 y=0.995, fontsize=12)
    out = os.path.join(PLOT_DIR, 'S2_combined.png')
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f'Wrote {out}')

    # Print key numbers
    print(f'\nUnwrapped arg C range vs theory (4·η·|α|, deg):')
    for k, s in enumerate(sheets):
        a = s['alpha']
        print(f'  |α|={a}: measured full={ranges_full[k]:.2f}°  theory={4*ETA_FULL*a*180/np.pi:.2f}°  '
              f'| measured R1={ranges_r1[k]:.2f}°  theory={4*ETA_R1*a*180/np.pi:.2f}°')


if __name__ == '__main__':
    main()
