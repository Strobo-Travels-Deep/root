#!/usr/bin/env python3
"""
run_fig6_v5.py — Hasse Fig 6 (a, b) on the restructured stroboscopic package.

Reproduces the same physics as run_fig6_v4.py (v0.9.1 intra_pulse_motion +
center_pulses_at_phase, MW π/2 at phase 0 before the AC train) but runs
on the new scripts/stroboscopic/ API. Shares the HDF5 schema so diffs
against fig6_alpha3_v4.h5 are meaningful.

Loop structure avoids rebuilding U_pulse inside the inner (ϑ₀) loop by
precomputing the 64 (φ_AC-dependent) pulse propagators once at δ=0.

Output:
    numerics/fig6_alpha3_v5.h5
    plots/fig6a_sigma_z_v5.png
    plots/fig6b_back_action_v5.png
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone

import h5py
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
sys.path.insert(0, os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts')))

from stroboscopic import HilbertSpace, StroboTrain, backend
from stroboscopic import operators as ops
from stroboscopic import hamiltonian as ham
from stroboscopic import propagators as prop
from stroboscopic.defaults import CODE_VERSION

ALPHA = 3.0
ETA = 0.397
OMEGA_M = 1.3
NMAX = 60
DELTA_T_FRAC = 0.13
T_M = 2 * np.pi / OMEGA_M
DELTA_T = DELTA_T_FRAC * T_M
N_PULSES = 30
DEBYE_WALLER = np.exp(-ETA ** 2 / 2)
OMEGA_EFF = np.pi / (2 * N_PULSES * DELTA_T)
OMEGA_R = OMEGA_EFF / DEBYE_WALLER

N_THETA0 = 64
N_PHI = 64
MW_PHASE_DEG = 0.0


def build_heatmap(map_arr, theta0_grid, phi_grid, title, fname, cmap,
                  ylabel, vlim_floor=0.9):
    cuts_theta = (np.pi / 4, np.pi / 2, np.pi)
    cuts_phi = (np.pi / 4, np.pi / 2, np.pi)
    cut_styles = ('lightgray', 'dimgray', 'black')

    fig = plt.figure(figsize=(7.0, 5.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 3], height_ratios=[3, 1],
                          hspace=0.30, wspace=0.30)
    vlim = max(vlim_floor, float(np.abs(map_arr).max()))

    ax_map = fig.add_subplot(gs[0, 1])
    im = ax_map.imshow(map_arr.T, origin='lower',
                       extent=[theta0_grid[0], theta0_grid[-1],
                               phi_grid[0], phi_grid[-1]],
                       aspect='auto', cmap=cmap, vmin=-vlim, vmax=+vlim)
    ax_map.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_map.set_ylabel(r'$\varphi_\mathrm{AC}$ (rad)')
    ax_map.set_xticks([0, np.pi, 2 * np.pi])
    ax_map.set_xticklabels(['0', r'$\pi$', r'$2\pi$'])
    ax_map.set_yticks([0, np.pi, 2 * np.pi])
    ax_map.set_yticklabels(['0', r'$\pi$', r'$2\pi$'])
    cb = fig.colorbar(im, ax=ax_map, shrink=0.85, pad=0.02)
    cb.set_label(ylabel)

    ax_bot = fig.add_subplot(gs[1, 1], sharex=ax_map)
    for ph_t, col in zip(cuts_phi, cut_styles):
        j = int(np.argmin(np.abs(phi_grid - ph_t)))
        ax_bot.plot(theta0_grid, map_arr[:, j], color=col,
                    label=fr'$\varphi={ph_t/np.pi:.2f}\pi$')
    ax_bot.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_bot.set_ylabel(ylabel)
    ax_bot.set_ylim(-vlim * 1.1, +vlim * 1.1)
    ax_bot.axhline(0, color='k', lw=0.4)
    ax_bot.legend(loc='lower right', fontsize=7, framealpha=0.9)

    ax_left = fig.add_subplot(gs[0, 0], sharey=ax_map)
    for th_t, col in zip(cuts_theta, cut_styles):
        i = int(np.argmin(np.abs(theta0_grid - th_t)))
        ax_left.plot(map_arr[i, :], phi_grid, color=col,
                     label=fr'$\vartheta_0={th_t/np.pi:.2f}\pi$')
    ax_left.set_xlabel(ylabel)
    ax_left.set_xlim(+vlim * 1.1, -vlim * 1.1)
    ax_left.axvline(0, color='k', lw=0.4)
    ax_left.legend(loc='lower left', fontsize=7, framealpha=0.9)

    fig.suptitle(title, fontsize=10)
    out = os.path.join(PLOTS_DIR, fname)
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', choices=['numpy', 'jax'], default='numpy')
    ap.add_argument('--output', default=None)
    args = ap.parse_args()
    backend.set_backend(args.backend)

    out_h5 = args.output or os.path.join(SCRIPT_DIR, 'fig6_alpha3_v5.h5')

    print(f"Hasse Fig 6 v5 — engine v{CODE_VERSION}, centered convention "
          f"(backend={args.backend}):")
    print(f"  T_m={T_M:.3f}  δt={DELTA_T:.3f} ({DELTA_T_FRAC*100:.0f}% of T_m)")
    print(f"  N={N_PULSES}  Ω={OMEGA_R:.4f}  ω_m·δt={OMEGA_M*DELTA_T:.3f} rad")
    print(f"  mw_pi2_phase_deg={MW_PHASE_DEG}  intra_pulse_motion=True  "
          f"center_pulses_at_phase=True\n")

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX); Cdag = C.conj().T

    theta0_grid = np.linspace(0.0, 2.0 * np.pi, N_THETA0, endpoint=False)
    phi_grid = np.linspace(0.0, 2.0 * np.pi, N_PHI, endpoint=False)

    # Pulse-centering shift: prepared motional phase = ϑ₀ + ω_m·δt/2
    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))

    # Precompute the 64 pulse propagators (depend on φ_AC only; δ=0 fixed).
    t0 = time.time()
    U_pulses = []
    for ph in phi_grid:
        H_pulse = ham.build_pulse_hamiltonian(
            ETA, OMEGA_R, 0.0, NMAX, C, Cdag,
            ac_phase_rad=float(ph),
            omega_m=OMEGA_M, intra_pulse_motion=True,
        )
        U_pulses.append(prop.build_U_pulse(H_pulse, DELTA_T))
    print(f"  built {N_PHI} U_pulse matrices in {time.time()-t0:.1f}s")

    # U_gap is identical across the whole grid (δ=0, intra_motion=True).
    T_gap = T_M - DELTA_T
    U_gap_diag = prop.build_U_gap(
        NMAX, OMEGA_M, T_gap, delta=0.0,
        include_motion=True, include_spin_detuning=True,
    )

    sigma_z_map = np.zeros((N_THETA0, N_PHI))
    sigma_x_map = np.zeros((N_THETA0, N_PHI))
    sigma_y_map = np.zeros((N_THETA0, N_PHI))
    nbar_map = np.zeros((N_THETA0, N_PHI))

    t0 = time.time()
    for i, th0 in enumerate(theta0_grid):
        # Prepare initial state once per ϑ₀, apply MW π/2 once.
        psi0 = hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': ALPHA,
                    'alpha_phase_deg': float(np.degrees(th0)) + shift_deg}],
        )
        psi_start = hs.apply_mw_pi2(psi0, MW_PHASE_DEG)

        for j in range(N_PHI):
            train = StroboTrain(
                U_pulse=U_pulses[j], U_gap_diag=U_gap_diag,
                n_pulses=N_PULSES,
            )
            psi = train.evolve(psi_start)
            obs = hs.observables(psi)
            sigma_z_map[i, j] = obs['sigma_z']
            sigma_x_map[i, j] = obs['sigma_x']
            sigma_y_map[i, j] = obs['sigma_y']
            nbar_map[i, j] = obs['nbar']

        if (i + 1) % 8 == 0:
            print(f"  ϑ₀ {i+1}/{N_THETA0}  σ_z range "
                  f"[{sigma_z_map[i].min():+.3f}, {sigma_z_map[i].max():+.3f}]  "
                  f"⟨n⟩ range [{nbar_map[i].min():.2f}, {nbar_map[i].max():.2f}]",
                  flush=True)
    elapsed = time.time() - t0
    print(f"  done — {elapsed:.1f} s for {N_THETA0*N_PHI} runs\n")

    delta_n_map = nbar_map - ALPHA ** 2

    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('theta0_rad', data=theta0_grid)
        f.create_dataset('phi_rad', data=phi_grid)
        f.create_dataset('sigma_z_map', data=sigma_z_map)
        f.create_dataset('sigma_x_map', data=sigma_x_map)
        f.create_dataset('sigma_y_map', data=sigma_y_map)
        f.create_dataset('nbar_map', data=nbar_map)
        f.create_dataset('delta_n_map', data=delta_n_map)
        f.attrs['alpha'] = ALPHA
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['omega_r'] = OMEGA_R
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['delta_t_frac_Tm'] = DELTA_T_FRAC
        f.attrs['nmax'] = NMAX
        f.attrs['mw_pi2_phase_deg'] = MW_PHASE_DEG
        f.attrs['intra_pulse_motion'] = 1
        f.attrs['center_pulses_at_phase'] = 1
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['engine'] = 'stroboscopic (restructured)'
        f.attrs['backend'] = args.backend
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('Fig 6 v5 on the restructured stroboscopic '
                            'package. Physics: v0.9.1 intra_pulse_motion + '
                            'center_pulses_at_phase. Should match '
                            'fig6_alpha3_v4.h5 within FP reassociation noise.')
    print(f"  wrote {out_h5}")

    sz_range = (sigma_z_map.min(), sigma_z_map.max())
    dn_range = (delta_n_map.min(), delta_n_map.max())
    print(f"\n  σ_z map range:  [{sz_range[0]:+.3f}, {sz_range[1]:+.3f}]  (Hasse ±0.9)")
    print(f"  δ⟨n⟩ map range: [{dn_range[0]:+.3f}, {dn_range[1]:+.3f}]  (Hasse ±0.9)")

    extras = (rf'N={N_PULSES}, $\delta t/T_m$={DELTA_T_FRAC:.2f}, '
              r'centered pulses, v5 (new API)')
    build_heatmap(sigma_z_map, theta0_grid, phi_grid,
                  f'Hasse Fig 6a v5 — engine v{CODE_VERSION} ({extras})',
                  'fig6a_sigma_z_v5.png',
                  cmap='RdBu_r', ylabel=r'$\langle\sigma_z\rangle$',
                  vlim_floor=0.9)
    build_heatmap(delta_n_map, theta0_grid, phi_grid,
                  f'Hasse Fig 6b v5 — engine v{CODE_VERSION} ({extras})',
                  'fig6b_back_action_v5.png',
                  cmap='PRGn', ylabel=r'$\delta\langle n\rangle$',
                  vlim_floor=0.9)


if __name__ == '__main__':
    main()
