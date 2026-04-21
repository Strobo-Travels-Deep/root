#!/usr/bin/env python3
"""
run_rabi_scan_v5.py — Diamond amplitude and back-action vs Ω.

Follow-up 1 from 2026-04-21-coh-theta0-det-rabi5x.md. Scans the Rabi
scale factor ∈ [0.2, 5] at δ = 0 and over a ϑ₀ grid, then extracts the
Fig-6a diamond amplitude and the δ⟨n⟩ peak per Ω.

Outputs:
    numerics/rabi_scan_v5.h5
    plots/rabi_scan_v5.png   (3-panel: diamond σ_z, δ⟨n⟩ peak, |C| mean)
"""
from __future__ import annotations

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

MW_PHASE_DEG = 0.0
AC_PHASE_DEG = 0.0
N_THETA0 = 64
N_RABI = 25
RABI_SCALE_MIN = 0.2
RABI_SCALE_MAX = 5.0


def main():
    print(f"Rabi scan — engine v{CODE_VERSION}")
    print(f"  α={ALPHA}  η={ETA}  ω_m={OMEGA_M}  N={N_PULSES}  δ=0")
    print(f"  Ω_baseline={OMEGA_R_BASELINE:.4f}  "
          f"RABI_SCALE ∈ [{RABI_SCALE_MIN}, {RABI_SCALE_MAX}], "
          f"{N_RABI} points\n")

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX); Cdag = C.conj().T
    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))

    theta0_grid = np.linspace(0.0, 2 * np.pi, N_THETA0, endpoint=False)
    rabi_scales = np.linspace(RABI_SCALE_MIN, RABI_SCALE_MAX, N_RABI)

    psi_starts = []
    for th0 in theta0_grid:
        psi0 = hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': ALPHA,
                    'alpha_phase_deg': float(np.degrees(th0)) + shift_deg}],
        )
        psi_starts.append(hs.apply_mw_pi2(psi0, MW_PHASE_DEG))

    T_gap = T_M - DELTA_T
    # δ = 0, so U_gap has no spin content either; identical across RABI.
    U_gap_diag = prop.build_U_gap(
        NMAX, OMEGA_M, T_gap, delta=0.0,
        include_motion=True, include_spin_detuning=True,
    )
    ac_phase_rad = float(np.radians(AC_PHASE_DEG))

    sigma_z = np.zeros((N_RABI, N_THETA0))
    sigma_x = np.zeros_like(sigma_z); sigma_y = np.zeros_like(sigma_z)
    nbar = np.zeros_like(sigma_z); coh_abs = np.zeros_like(sigma_z)

    t0 = time.time()
    for k, rs in enumerate(rabi_scales):
        omega_r = rs * OMEGA_R_BASELINE
        H_pulse = ham.build_pulse_hamiltonian(
            ETA, omega_r, 0.0, NMAX, C, Cdag,
            ac_phase_rad=ac_phase_rad,
            omega_m=OMEGA_M, intra_pulse_motion=True,
        )
        U_pulse = prop.build_U_pulse(H_pulse, DELTA_T)
        train = StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag,
                            n_pulses=N_PULSES)
        for i, psi in enumerate(psi_starts):
            obs = hs.observables(train.evolve(psi))
            sigma_z[k, i] = obs['sigma_z']
            sigma_x[k, i] = obs['sigma_x']
            sigma_y[k, i] = obs['sigma_y']
            nbar[k, i] = obs['nbar']
            coh_abs[k, i] = np.sqrt(obs['sigma_x']**2 + obs['sigma_y']**2)
    elapsed = time.time() - t0
    print(f"  done — {elapsed:.1f} s for {N_RABI*N_THETA0} evolutions\n")

    delta_n = nbar - ALPHA ** 2

    diamond_amp_sz = 0.5 * (sigma_z.max(axis=1) - sigma_z.min(axis=1))
    dn_peak = np.max(np.abs(delta_n), axis=1)
    dn_amp = 0.5 * (delta_n.max(axis=1) - delta_n.min(axis=1))
    coh_mean = coh_abs.mean(axis=1)
    coh_min = coh_abs.min(axis=1)
    sz_mean = sigma_z.mean(axis=1)

    print("  RABI_SCALE | diamond |⟨σ_z⟩ amp | |δ⟨n⟩|_peak | mean |C| | min |C|")
    print("  -----------|----------|----------|-----------|----------|---------")
    for k, rs in enumerate(rabi_scales):
        print(f"   {rs:7.3f}   |  {diamond_amp_sz[k]:+.3f}  |  "
              f"{dn_peak[k]:+.3f}  |  {coh_mean[k]:.3f}   |  {coh_min[k]:.3f}")

    out_h5 = os.path.join(SCRIPT_DIR, 'rabi_scan_v5.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('rabi_scale', data=rabi_scales)
        f.create_dataset('theta0_rad', data=theta0_grid)
        f.create_dataset('sigma_z_map', data=sigma_z)
        f.create_dataset('sigma_x_map', data=sigma_x)
        f.create_dataset('sigma_y_map', data=sigma_y)
        f.create_dataset('nbar_map', data=nbar)
        f.create_dataset('delta_n_map', data=delta_n)
        f.create_dataset('coh_abs_map', data=coh_abs)
        f.create_dataset('diamond_amp_sigma_z', data=diamond_amp_sz)
        f.create_dataset('dn_peak', data=dn_peak)
        f.create_dataset('dn_amp', data=dn_amp)
        f.create_dataset('coh_mean', data=coh_mean)
        f.create_dataset('coh_min', data=coh_min)
        f.attrs['alpha'] = ALPHA; f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['omega_r_baseline'] = OMEGA_R_BASELINE
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['nmax'] = NMAX
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['notes'] = ('Rabi-amplitude scan at δ=0 over ϑ₀ grid. '
                            'Follow-up 1 of 2026-04-21-coh-theta0-det-rabi5x.md')
    print(f"\n  wrote {out_h5}")

    # Plot
    fig, ax = plt.subplots(3, 1, figsize=(6.5, 7.0), sharex=True,
                           gridspec_kw={'hspace': 0.12})
    ax[0].plot(rabi_scales, diamond_amp_sz, 'o-', color='darkred', lw=1.5)
    ax[0].set_ylabel(r'$\frac{1}{2}(\max - \min)\,\langle\sigma_z\rangle$'
                     r' over $\vartheta_0$')
    ax[0].set_title(r'Fig 6a diamond amplitude vs drive')
    ax[0].grid(alpha=0.3)
    ax[0].axvline(1.0, color='gray', lw=0.5, ls='--')
    ax[0].axhline(0.9, color='gray', lw=0.5, ls=':')

    ax[1].plot(rabi_scales, dn_peak, 'o-', color='darkgreen', lw=1.5,
               label=r'$|\delta\langle n\rangle|_\mathrm{peak}$')
    ax[1].plot(rabi_scales, dn_amp, 's--', color='gray', lw=1.0,
               label=r'$\frac{1}{2}(\max - \min)$ amp.')
    ax[1].set_ylabel(r'$\delta\langle n\rangle$ (phonons)')
    ax[1].set_title('Back-action vs drive')
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    ax[1].axvline(1.0, color='gray', lw=0.5, ls='--')

    ax[2].plot(rabi_scales, coh_mean, 'o-', color='navy', lw=1.5,
               label=r'$\langle |C|\rangle_{\vartheta_0}$')
    ax[2].plot(rabi_scales, coh_min, 's--', color='gray', lw=1.0,
               label=r'$\min_{\vartheta_0} |C|$')
    ax[2].set_ylabel(r'$|C|$'); ax[2].set_xlabel(r'$\Omega / \Omega_\mathrm{baseline}$')
    ax[2].set_title(r'Coherence at $\delta=0$ vs drive')
    ax[2].legend(fontsize=8); ax[2].grid(alpha=0.3)
    ax[2].axvline(1.0, color='gray', lw=0.5, ls='--')

    fig.suptitle(rf'Drive-strength scan at $\delta=0$  '
                 rf'($|\alpha|=${ALPHA}, N={N_PULSES}, $\delta t/T_m$={DELTA_T_FRAC:.2f})',
                 fontsize=10)
    out = os.path.join(PLOTS_DIR, 'rabi_scan_v5.png')
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")


if __name__ == '__main__':
    main()
