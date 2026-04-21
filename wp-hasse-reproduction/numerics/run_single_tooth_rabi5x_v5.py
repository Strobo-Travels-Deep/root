#!/usr/bin/env python3
"""
run_single_tooth_rabi5x_v5.py — Single-tooth zoom at 5× Rabi.

Follow-up 2 from 2026-04-21-coh-theta0-det-rabi5x.md. Zooms into the
δ = 0 tooth with δ/ω_m ∈ [−0.3, +0.3] at 201 points to resolve the
internal ϑ₀-substructure that appeared in the ±3 broad scan.

Outputs:
    numerics/single_tooth_rabi5x_v5.h5
    plots/single_tooth_rabi5x_{sigma_z,coh_abs,delta_n}_v5.png
"""
from __future__ import annotations

import os, sys, time
from datetime import datetime, timezone
import h5py, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
sys.path.insert(0, os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts')))

from stroboscopic import HilbertSpace, StroboTrain
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
OMEGA_R_BASELINE = (np.pi / (2 * N_PULSES * DELTA_T)) / DEBYE_WALLER
RABI_SCALE = 5.0
OMEGA_R = RABI_SCALE * OMEGA_R_BASELINE

MW_PHASE_DEG = 0.0
AC_PHASE_DEG = 0.0
N_THETA0 = 64
N_DET = 201
DET_REL_MAX = 0.3


def heatmap(map_arr, theta0_grid, det_rel_grid, title, fname, cmap,
            ylabel, vlim=None, symmetric=True):
    fig = plt.figure(figsize=(7.2, 5.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[3, 1], wspace=0.10)
    if vlim is None:
        vlim = max(0.9, float(np.abs(map_arr).max()))
    if symmetric:
        vmin, vmax = -vlim, +vlim
    else:
        vmin, vmax = float(map_arr.min()), float(map_arr.max())

    ax_map = fig.add_subplot(gs[0, 0])
    im = ax_map.imshow(map_arr.T, origin='lower',
                       extent=[theta0_grid[0], theta0_grid[-1],
                               det_rel_grid[0], det_rel_grid[-1]],
                       aspect='auto', cmap=cmap, vmin=vmin, vmax=vmax)
    ax_map.set_xlabel(r'$\vartheta_0$ (rad)')
    ax_map.set_ylabel(r'$\delta / \omega_m$')
    ax_map.set_xticks([0, np.pi, 2 * np.pi])
    ax_map.set_xticklabels(['0', r'$\pi$', r'$2\pi$'])
    ax_map.axhline(0, color='white', lw=0.3, alpha=0.4)
    cb = fig.colorbar(im, ax=ax_map, shrink=0.85, pad=0.02)
    cb.set_label(ylabel)

    ax_cuts = fig.add_subplot(gs[0, 1], sharey=ax_map)
    for th_t, col, lbl in zip(
        (np.pi / 4, np.pi / 2, np.pi, 3 * np.pi / 2),
        ('lightgray', 'dimgray', 'black', 'teal'),
        (r'\pi/4', r'\pi/2', r'\pi', r'3\pi/2'),
    ):
        i = int(np.argmin(np.abs(theta0_grid - th_t)))
        ax_cuts.plot(map_arr[i, :], det_rel_grid, color=col, lw=1.2,
                     label=fr'$\vartheta_0={lbl}$')
    if symmetric:
        ax_cuts.set_xlim(+vlim * 1.1, -vlim * 1.1)
        ax_cuts.axvline(0, color='k', lw=0.4)
    ax_cuts.legend(loc='lower left', fontsize=7, framealpha=0.9)
    ax_cuts.set_xlabel(ylabel)
    plt.setp(ax_cuts.get_yticklabels(), visible=False)

    fig.suptitle(title, fontsize=10)
    out = os.path.join(PLOTS_DIR, fname)
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")


def main():
    print(f"Single-tooth zoom at 5× Rabi  (δ/ω_m ∈ [−{DET_REL_MAX}, +{DET_REL_MAX}])")
    print(f"  grid: {N_THETA0} × {N_DET}\n")

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX); Cdag = C.conj().T
    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))

    theta0_grid = np.linspace(0.0, 2 * np.pi, N_THETA0, endpoint=False)
    det_rel_grid = np.linspace(-DET_REL_MAX, +DET_REL_MAX, N_DET)

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

    sx = np.zeros((N_THETA0, N_DET)); sy = np.zeros_like(sx)
    sz = np.zeros_like(sx); nbar = np.zeros_like(sx)

    t0 = time.time()
    for j, d_rel in enumerate(det_rel_grid):
        delta = d_rel * OMEGA_M
        H_pulse = ham.build_pulse_hamiltonian(
            ETA, OMEGA_R, delta, NMAX, C, Cdag,
            ac_phase_rad=ac_phase_rad, omega_m=OMEGA_M,
            intra_pulse_motion=True,
        )
        U_pulse = prop.build_U_pulse(H_pulse, DELTA_T)
        U_gap_diag = prop.build_U_gap(
            NMAX, OMEGA_M, T_gap, delta=delta,
            include_motion=True, include_spin_detuning=True,
        )
        train = StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag,
                            n_pulses=N_PULSES)
        for i, psi in enumerate(psi_starts):
            obs = hs.observables(train.evolve(psi))
            sx[i, j] = obs['sigma_x']; sy[i, j] = obs['sigma_y']
            sz[i, j] = obs['sigma_z']; nbar[i, j] = obs['nbar']
    print(f"  done — {time.time()-t0:.1f} s\n")

    coh_abs = np.sqrt(sx ** 2 + sy ** 2)
    delta_n = nbar - ALPHA ** 2

    out_h5 = os.path.join(SCRIPT_DIR, 'single_tooth_rabi5x_v5.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('theta0_rad', data=theta0_grid)
        f.create_dataset('detuning_rel', data=det_rel_grid)
        f.create_dataset('sigma_x_map', data=sx)
        f.create_dataset('sigma_y_map', data=sy)
        f.create_dataset('sigma_z_map', data=sz)
        f.create_dataset('nbar_map', data=nbar)
        f.create_dataset('delta_n_map', data=delta_n)
        f.create_dataset('coh_abs_map', data=coh_abs)
        f.attrs['alpha'] = ALPHA; f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M; f.attrs['omega_r'] = OMEGA_R
        f.attrs['rabi_scale'] = RABI_SCALE
        f.attrs['n_pulses'] = N_PULSES; f.attrs['delta_t_us'] = DELTA_T
        f.attrs['nmax'] = NMAX
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['notes'] = ('Single-tooth zoom at 5× Rabi, δ=0 tooth. '
                            'Follow-up 2 of 2026-04-21-coh-theta0-det-rabi5x.md')
    print(f"  wrote {out_h5}")

    print(f"  σ_z range: [{sz.min():+.3f}, {sz.max():+.3f}]")
    print(f"  |C|  range: [{coh_abs.min():.3f}, {coh_abs.max():.3f}]")
    print(f"  δ⟨n⟩ range: [{delta_n.min():+.3f}, {delta_n.max():+.3f}]\n")

    suffix = (rf'N={N_PULSES}, $\delta t/T_m$={DELTA_T_FRAC:.2f}, '
              rf'$|\alpha|$={ALPHA}, η={ETA:.3f}, $\Omega\times${RABI_SCALE:g}, '
              r'δ-zoom')
    heatmap(sz, theta0_grid, det_rel_grid,
            rf'$\langle\sigma_z\rangle$ — single tooth, 5× Rabi  ({suffix})',
            'single_tooth_rabi5x_sigma_z_v5.png',
            cmap='RdBu_r', ylabel=r'$\langle\sigma_z\rangle$')
    heatmap(coh_abs, theta0_grid, det_rel_grid,
            rf'$|C|$ — single tooth, 5× Rabi  ({suffix})',
            'single_tooth_rabi5x_coh_abs_v5.png',
            cmap='magma', ylabel=r'$|C|$', vlim=1.0, symmetric=False)
    heatmap(delta_n, theta0_grid, det_rel_grid,
            rf'$\delta\langle n\rangle$ — single tooth, 5× Rabi  ({suffix})',
            'single_tooth_rabi5x_delta_n_v5.png',
            cmap='PRGn', ylabel=r'$\delta\langle n\rangle$',
            vlim=max(1.0, float(np.abs(delta_n).max())), symmetric=True)


if __name__ == '__main__':
    main()
