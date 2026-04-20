#!/usr/bin/env python3
"""
run_coh_theta0_det_v5.py — Spin coherence over (ϑ₀, δ).

Hasse-matched parameters of Fig 6, but scanning the train detuning δ
instead of the AC analysis phase φ_AC. φ_AC is held at 0. The MW π/2
pulse at phase 0 precedes the AC train.

Grid: ϑ₀ ∈ [0, 2π), 64 points × δ/ω_m ∈ [-3, +3], 201 points.
Total: 12 864 evolutions. Wall ≈ 30 s.

Outputs:
    numerics/coh_theta0_det_v5.h5
    plots/coh_theta0_det_sigma_x_v5.png
    plots/coh_theta0_det_sigma_y_v5.png
    plots/coh_theta0_det_coh_abs_v5.png
    plots/coh_theta0_det_coh_arg_v5.png
    plots/coh_theta0_det_sigma_z_v5.png
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

AC_PHASE_DEG = 0.0
MW_PHASE_DEG = 0.0

N_THETA0 = 64
N_DET = 201
DET_REL_MAX = 3.0   # in units of ω_m (so δ/(2π) spans ±3.9 MHz)


def heatmap(map_arr, theta0_grid, det_rel_grid, title, fname, cmap,
            ylabel, vlim=None, symmetric=True, alpha_map=None,
            det_ticks=(-3, -2, -1, 0, 1, 2, 3)):
    cuts_theta = (np.pi / 4, np.pi / 2, np.pi)
    cuts_det = (0.0, 1.0, 2.0)
    cut_styles = ('lightgray', 'dimgray', 'black')

    fig = plt.figure(figsize=(7.2, 5.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 3], height_ratios=[3, 1],
                          hspace=0.30, wspace=0.30)
    if vlim is None:
        vlim = max(0.9, float(np.abs(map_arr).max()))
    if symmetric:
        vmin, vmax = -vlim, +vlim
    else:
        vmin, vmax = float(map_arr.min()), float(map_arr.max())

    ax_map = fig.add_subplot(gs[0, 1])
    img_kwargs = dict(origin='lower',
                      extent=[theta0_grid[0], theta0_grid[-1],
                              det_rel_grid[0], det_rel_grid[-1]],
                      aspect='auto', cmap=cmap, vmin=vmin, vmax=vmax)
    if alpha_map is not None:
        a_norm = np.clip(alpha_map / max(1e-12, float(alpha_map.max())),
                         0.0, 1.0).T
        im = ax_map.imshow(map_arr.T, alpha=a_norm, **img_kwargs)
    else:
        im = ax_map.imshow(map_arr.T, **img_kwargs)
    ax_map.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_map.set_ylabel(r'$\delta / \omega_m$')
    ax_map.set_xticks([0, np.pi, 2 * np.pi])
    ax_map.set_xticklabels(['0', r'$\pi$', r'$2\pi$'])
    ax_map.set_yticks(list(det_ticks))
    # Dotted guides at integer multiples of ω_m (comb teeth)
    for n in det_ticks:
        ax_map.axhline(n, color='white', lw=0.3, alpha=0.3)
    cb = fig.colorbar(im, ax=ax_map, shrink=0.85, pad=0.02)
    cb.set_label(ylabel)

    ax_bot = fig.add_subplot(gs[1, 1], sharex=ax_map)
    for d_t, col in zip(cuts_det, cut_styles):
        j = int(np.argmin(np.abs(det_rel_grid - d_t)))
        ax_bot.plot(theta0_grid, map_arr[:, j], color=col,
                    label=fr'$\delta/\omega_m={d_t:.1f}$')
    ax_bot.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_bot.set_ylabel(ylabel)
    if symmetric:
        ax_bot.set_ylim(-vlim * 1.1, +vlim * 1.1)
        ax_bot.axhline(0, color='k', lw=0.4)
    ax_bot.legend(loc='lower right', fontsize=7, framealpha=0.9)

    ax_left = fig.add_subplot(gs[0, 0], sharey=ax_map)
    for th_t, col in zip(cuts_theta, cut_styles):
        i = int(np.argmin(np.abs(theta0_grid - th_t)))
        ax_left.plot(map_arr[i, :], det_rel_grid, color=col,
                     label=fr'$\vartheta_0={th_t/np.pi:.2f}\pi$')
    ax_left.set_xlabel(ylabel)
    if symmetric:
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

    out_h5 = args.output or os.path.join(SCRIPT_DIR, 'coh_theta0_det_v5.h5')

    print(f"(ϑ₀, δ) coherence scan — engine v{CODE_VERSION}, backend={args.backend}")
    print(f"  α={ALPHA}  η={ETA}  ω_m={OMEGA_M}  N={N_PULSES}  "
          f"δt={DELTA_T:.3f}  Ω={OMEGA_R:.4f}")
    print(f"  MW π/2 phase = {MW_PHASE_DEG}°  AC phase = {AC_PHASE_DEG}°  "
          f"intra_pulse_motion=True  centered=True")
    print(f"  grid: {N_THETA0} × {N_DET}   δ/ω_m ∈ [−{DET_REL_MAX}, +{DET_REL_MAX}]\n")

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX); Cdag = C.conj().T
    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))

    theta0_grid = np.linspace(0.0, 2.0 * np.pi, N_THETA0, endpoint=False)
    det_rel_grid = np.linspace(-DET_REL_MAX, +DET_REL_MAX, N_DET)
    det_MHz = det_rel_grid * OMEGA_M

    # Precompute 64 post-MW initial states (depend on ϑ₀ only).
    psi_starts = []
    for th0 in theta0_grid:
        psi0 = hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': ALPHA,
                    'alpha_phase_deg': float(np.degrees(th0)) + shift_deg}],
        )
        psi_starts.append(hs.apply_mw_pi2(psi0, MW_PHASE_DEG))

    ac_phase_rad = float(np.radians(AC_PHASE_DEG))
    T_gap = T_M - DELTA_T

    sigma_x = np.zeros((N_THETA0, N_DET))
    sigma_y = np.zeros_like(sigma_x)
    sigma_z = np.zeros_like(sigma_x)
    nbar = np.zeros_like(sigma_x)

    t0 = time.time()
    for j, d_rel in enumerate(det_rel_grid):
        delta = d_rel * OMEGA_M
        H_pulse = ham.build_pulse_hamiltonian(
            ETA, OMEGA_R, delta, NMAX, C, Cdag,
            ac_phase_rad=ac_phase_rad,
            omega_m=OMEGA_M, intra_pulse_motion=True,
        )
        U_pulse = prop.build_U_pulse(H_pulse, DELTA_T)
        U_gap_diag = prop.build_U_gap(
            NMAX, OMEGA_M, T_gap, delta=delta,
            include_motion=True, include_spin_detuning=True,
        )
        train = StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag,
                            n_pulses=N_PULSES)

        for i, psi_start in enumerate(psi_starts):
            obs = hs.observables(train.evolve(psi_start))
            sigma_x[i, j] = obs['sigma_x']
            sigma_y[i, j] = obs['sigma_y']
            sigma_z[i, j] = obs['sigma_z']
            nbar[i, j] = obs['nbar']

        if (j + 1) % max(1, N_DET // 10) == 0:
            eta_s = (N_DET - j - 1) * (time.time() - t0) / (j + 1)
            print(f"  δ {j+1}/{N_DET}  ETA {eta_s:.0f}s", flush=True)
    elapsed = time.time() - t0
    print(f"  done — {elapsed:.1f}s for {N_THETA0*N_DET} evolutions\n")

    coh_abs = np.sqrt(sigma_x ** 2 + sigma_y ** 2)
    coh_arg_deg = np.degrees(np.arctan2(sigma_y, sigma_x))
    delta_n = nbar - ALPHA ** 2

    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('theta0_rad', data=theta0_grid)
        f.create_dataset('detuning_rel', data=det_rel_grid)
        f.create_dataset('detuning_MHz_over_2pi', data=det_MHz)
        f.create_dataset('sigma_x_map', data=sigma_x)
        f.create_dataset('sigma_y_map', data=sigma_y)
        f.create_dataset('sigma_z_map', data=sigma_z)
        f.create_dataset('nbar_map', data=nbar)
        f.create_dataset('delta_n_map', data=delta_n)
        f.create_dataset('coh_abs_map', data=coh_abs)
        f.create_dataset('coh_arg_deg_map', data=coh_arg_deg)
        f.attrs['alpha'] = ALPHA
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['omega_r'] = OMEGA_R
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['delta_t_frac_Tm'] = DELTA_T_FRAC
        f.attrs['nmax'] = NMAX
        f.attrs['mw_pi2_phase_deg'] = MW_PHASE_DEG
        f.attrs['ac_phase_deg'] = AC_PHASE_DEG
        f.attrs['intra_pulse_motion'] = 1
        f.attrs['center_pulses_at_phase'] = 1
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['engine'] = 'stroboscopic (restructured)'
        f.attrs['backend'] = args.backend
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('Spin coherences as a function of (ϑ₀, δ) for '
                            'Hasse Fig 6 parameters with φ_AC = 0.')
    print(f"  wrote {out_h5}\n")

    print(f"  ⟨σ_x⟩ range: [{sigma_x.min():+.3f}, {sigma_x.max():+.3f}]")
    print(f"  ⟨σ_y⟩ range: [{sigma_y.min():+.3f}, {sigma_y.max():+.3f}]")
    print(f"  ⟨σ_z⟩ range: [{sigma_z.min():+.3f}, {sigma_z.max():+.3f}]")
    print(f"  |C|   range: [{coh_abs.min():.3f}, {coh_abs.max():.3f}]\n")

    title_suffix = (rf'N={N_PULSES}, $\delta t/T_m$={DELTA_T_FRAC:.2f}, '
                    rf'$|\alpha|$={ALPHA:.0f}, η={ETA:.3f}, '
                    rf'$\varphi_\mathrm{{AC}}$=0')

    heatmap(sigma_x, theta0_grid, det_rel_grid,
            rf'$\langle\sigma_x\rangle(\vartheta_0, \delta)$   ({title_suffix})',
            'coh_theta0_det_sigma_x_v5.png',
            cmap='RdBu_r', ylabel=r'$\langle\sigma_x\rangle$')
    heatmap(sigma_y, theta0_grid, det_rel_grid,
            rf'$\langle\sigma_y\rangle(\vartheta_0, \delta)$   ({title_suffix})',
            'coh_theta0_det_sigma_y_v5.png',
            cmap='RdBu_r', ylabel=r'$\langle\sigma_y\rangle$')
    heatmap(sigma_z, theta0_grid, det_rel_grid,
            rf'$\langle\sigma_z\rangle(\vartheta_0, \delta)$   ({title_suffix})',
            'coh_theta0_det_sigma_z_v5.png',
            cmap='RdBu_r', ylabel=r'$\langle\sigma_z\rangle$')
    heatmap(coh_abs, theta0_grid, det_rel_grid,
            rf'$|C|(\vartheta_0, \delta) = \sqrt{{\sigma_x^2+\sigma_y^2}}$   ({title_suffix})',
            'coh_theta0_det_coh_abs_v5.png',
            cmap='magma', ylabel=r'$|C|$', vlim=1.0, symmetric=False)
    heatmap(coh_arg_deg, theta0_grid, det_rel_grid,
            rf'$\arg C (\vartheta_0, \delta)$   ({title_suffix})',
            'coh_theta0_det_coh_arg_v5.png',
            cmap='twilight', ylabel=r'$\arg(C)$ (deg)',
            vlim=180.0, symmetric=True, alpha_map=coh_abs)


if __name__ == '__main__':
    main()
