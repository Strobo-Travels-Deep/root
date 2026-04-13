#!/usr/bin/env python3
"""
plot_fig6.py — Render Hasse Fig 6 reproduction from fig6_alpha3.h5.

Two output PNGs in ../plots/:
    fig6a_sigma_z.png      — heatmap σ_z(ϕ, ϑ₀) + cuts at ϑ₀ = {π/4, π/2, π}
    fig6b_back_action.png  — heatmap δ⟨n⟩(ϕ, ϑ₀) + cuts at ϑ₀ = {π/4, π/2, π}
"""

import os
import numpy as np
import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
H5         = os.path.join(SCRIPT_DIR, 'fig6_alpha3.h5')
OUT_DIR    = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))


def find_index(grid, target):
    return int(np.argmin(np.abs(grid - target)))


def render(map_arr, theta0, phi, title, fname, cmap, vlim, ylabel):
    cuts_theta = (np.pi / 4, np.pi / 2, np.pi)
    cut_styles = ('lightgray', 'dimgray', 'black')

    fig = plt.figure(figsize=(7.0, 5.5))
    gs  = fig.add_gridspec(2, 2, width_ratios=[1, 3], height_ratios=[3, 1],
                           hspace=0.30, wspace=0.30)

    # Heatmap (ϑ₀ on x, ϕ on y to match Hasse layout)
    ax_map = fig.add_subplot(gs[0, 1])
    im = ax_map.imshow(map_arr.T,
                       origin='lower',
                       extent=[theta0[0], theta0[-1], phi[0], phi[-1]],
                       aspect='auto',
                       cmap=cmap, vmin=-vlim, vmax=+vlim)
    ax_map.set_xlabel(r'Phase of displaced state $\vartheta_0$ (rad)')
    ax_map.set_ylabel(r'Analysis phase $\varphi$ (rad)')
    ax_map.set_xticks([0, np.pi, 2 * np.pi])
    ax_map.set_xticklabels(['0', r'$\pi$', r'$2\pi$'])
    ax_map.set_yticks([0, np.pi, 2 * np.pi])
    ax_map.set_yticklabels(['0', r'$\pi$', r'$2\pi$'])
    cb = fig.colorbar(im, ax=ax_map, shrink=0.85, pad=0.02)
    cb.set_label(ylabel)

    # Bottom panel: cuts along ϕ at fixed ϑ₀
    ax_bot = fig.add_subplot(gs[1, 1], sharex=ax_map)
    for th0_target, col in zip(cuts_theta, cut_styles):
        i = find_index(theta0, th0_target)
        ax_bot.plot(theta0, map_arr[:, find_index(phi, np.pi / 2)],
                    color='white', alpha=0)   # placeholder for axis range
        ax_bot.plot(theta0, map_arr[:, i % len(phi)] * 0,
                    color='white', alpha=0)
    # Actually plot ϑ₀-cuts at fixed ϕ ∈ {π/4, π/2, π}
    cuts_phi = (np.pi / 4, np.pi / 2, np.pi)
    for ph_target, col in zip(cuts_phi, cut_styles):
        i = find_index(phi, ph_target)
        ax_bot.plot(theta0, map_arr[:, i], color=col,
                    label=fr'$\varphi={ph_target/np.pi:.2f}\pi$')
    ax_bot.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_bot.set_ylabel(ylabel)
    ax_bot.set_ylim(-vlim * 1.1, +vlim * 1.1)
    ax_bot.axhline(0, color='k', lw=0.4)
    ax_bot.legend(loc='lower right', fontsize=7, framealpha=0.9)

    # Left panel: cuts along ϕ at fixed ϑ₀
    ax_left = fig.add_subplot(gs[0, 0], sharey=ax_map)
    for th0_target, col in zip(cuts_theta, cut_styles):
        i = find_index(theta0, th0_target)
        ax_left.plot(map_arr[i, :], phi, color=col,
                     label=fr'$\vartheta_0={th0_target/np.pi:.2f}\pi$')
    ax_left.set_xlabel(ylabel)
    ax_left.set_xlim(+vlim * 1.1, -vlim * 1.1)   # invert to mirror Hasse
    ax_left.axvline(0, color='k', lw=0.4)
    ax_left.legend(loc='lower left', fontsize=7, framealpha=0.9)

    fig.suptitle(title, fontsize=10)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, fname)
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")


def main():
    with h5py.File(H5, 'r') as f:
        theta0 = f['theta0_rad'][:]
        phi    = f['phi_rad'][:]
        sz_map = f['sigma_z_map'][:]
        dn_map = f['delta_n_map'][:]
        alpha  = float(f.attrs['alpha'])

    title6a = (rf'Hasse Fig 6a reproduction — $\langle\sigma_z\rangle$, '
               rf'$|\alpha|={alpha:.0f}$, $\eta=0.397$ (engine '
               r'$\sigma_x\cos\varphi + \sigma_y\sin\varphi$)')
    title6b = (rf'Hasse Fig 6b reproduction — back-action $\delta\langle n\rangle$, '
               rf'$|\alpha|={alpha:.0f}$ (basis-independent in engine frame)')

    render(sz_map, theta0, phi, title6a, 'fig6a_sigma_z.png',
           cmap='RdBu_r', vlim=max(0.9, np.abs(sz_map).max()),
           ylabel=r'$\langle\sigma_z\rangle$')
    render(dn_map, theta0, phi, title6b, 'fig6b_back_action.png',
           cmap='PRGn', vlim=max(0.9, np.abs(dn_map).max()),
           ylabel=r'$\delta\langle n\rangle$')


if __name__ == '__main__':
    main()
