#!/usr/bin/env python3
"""
check_fock_leakage_rabi5x_v5.py — Fock-cutoff leakage at 5× Rabi.

Follow-up 4 from 2026-04-21-coh-theta0-det-rabi5x.md. At strong drive
the motional state can spread further, so we explicitly confirm that
the NMAX = 60 truncation used in the (ϑ₀, δ) and single-tooth scans
is still safe.

Strategy: exhaustively scan the single-tooth zoom grid (64 × 201 at
5× Rabi), recording top-3 and top-5 Fock leakage per point, and
report the worst case + distribution.

Writes numerics/fock_leakage_rabi5x_v5.h5 and prints a compact summary.
"""
from __future__ import annotations

import os, sys
from datetime import datetime, timezone
import h5py, numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts')))

from stroboscopic import HilbertSpace, StroboTrain
from stroboscopic import operators as ops
from stroboscopic import hamiltonian as ham
from stroboscopic import propagators as prop
from stroboscopic.defaults import CODE_VERSION

ALPHA = 3.0
ETA = 0.397
OMEGA_M = 1.3
DELTA_T_FRAC = 0.13
T_M = 2 * np.pi / OMEGA_M
DELTA_T = DELTA_T_FRAC * T_M
N_PULSES = 30
DEBYE_WALLER = np.exp(-ETA ** 2 / 2)
OMEGA_R_BASELINE = (np.pi / (2 * N_PULSES * DELTA_T)) / DEBYE_WALLER
RABI_SCALE = 5.0
OMEGA_R = RABI_SCALE * OMEGA_R_BASELINE

MW_PHASE_DEG = 0.0
N_THETA0 = 64
N_DET = 81
DET_REL_MAX = 0.3


def run_at_nmax(nmax: int):
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(nmax,))
    C = ops.coupling(ETA, nmax); Cdag = C.conj().T
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

    T_gap = T_M - DELTA_T
    leak3 = np.zeros((N_THETA0, N_DET))
    leak5 = np.zeros_like(leak3)
    nbar_max = 0.0; nbar_min = 1e9

    for j, d_rel in enumerate(det_rel_grid):
        delta = d_rel * OMEGA_M
        H_pulse = ham.build_pulse_hamiltonian(
            ETA, OMEGA_R, delta, nmax, C, Cdag,
            ac_phase_rad=0.0, omega_m=OMEGA_M, intra_pulse_motion=True,
        )
        U_pulse = prop.build_U_pulse(H_pulse, DELTA_T)
        U_gap_diag = prop.build_U_gap(
            nmax, OMEGA_M, T_gap, delta=delta,
            include_motion=True, include_spin_detuning=True,
        )
        train = StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag,
                            n_pulses=N_PULSES)
        for i, psi in enumerate(psi_starts):
            psi_final = train.evolve(psi)
            leak3[i, j] = hs.fock_leakage(psi_final, top_k=3)
            leak5[i, j] = hs.fock_leakage(psi_final, top_k=5)
            nb = float(hs.observables(psi_final)['nbar'])
            if nb > nbar_max: nbar_max = nb
            if nb < nbar_min: nbar_min = nb
    return theta0_grid, det_rel_grid, leak3, leak5, nbar_max, nbar_min


def main():
    print(f"Fock-leakage probe at 5× Rabi  (α={ALPHA}, η={ETA})")
    print(f"  grid: {N_THETA0} × {N_DET} at δ/ω_m ∈ [−{DET_REL_MAX}, +{DET_REL_MAX}]\n")

    results = {}
    for nmax in (40, 60, 80):
        print(f"  NMAX = {nmax}")
        th, det, l3, l5, nmax_b, nmin_b = run_at_nmax(nmax)
        print(f"    ⟨n⟩ range on grid: [{nmin_b:.3f}, {nmax_b:.3f}]")
        print(f"    leak3: max {l3.max():.3e}   mean {l3.mean():.3e}")
        print(f"    leak5: max {l5.max():.3e}   mean {l5.mean():.3e}\n")
        results[nmax] = dict(theta0=th, det_rel=det, leak3=l3, leak5=l5,
                             nbar_max=nmax_b, nbar_min=nmin_b)

    out = os.path.join(SCRIPT_DIR, 'fock_leakage_rabi5x_v5.h5')
    with h5py.File(out, 'w') as f:
        for nmax, d in results.items():
            g = f.create_group(f'nmax_{nmax}')
            g.create_dataset('theta0_rad', data=d['theta0'])
            g.create_dataset('detuning_rel', data=d['det_rel'])
            g.create_dataset('leak_top3', data=d['leak3'])
            g.create_dataset('leak_top5', data=d['leak5'])
            g.attrs['nbar_max'] = d['nbar_max']
            g.attrs['nbar_min'] = d['nbar_min']
            g.attrs['leak3_max'] = float(d['leak3'].max())
            g.attrs['leak3_mean'] = float(d['leak3'].mean())
            g.attrs['leak5_max'] = float(d['leak5'].max())
            g.attrs['leak5_mean'] = float(d['leak5'].mean())
        f.attrs['alpha'] = ALPHA
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['rabi_scale'] = RABI_SCALE
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
    print(f"  wrote {out}\n")

    # Headline verdict
    leak60_max_top5 = results[60]['leak5'].max()
    if leak60_max_top5 < 1e-8:
        print(f"  VERDICT  NMAX=60 is safe at 5× Rabi: worst top-5 leakage "
              f"{leak60_max_top5:.3e}  < 1e-8.")
    elif leak60_max_top5 < 1e-4:
        print(f"  VERDICT  NMAX=60 is marginal at 5× Rabi: worst top-5 "
              f"leakage {leak60_max_top5:.3e}.")
    else:
        print(f"  VERDICT  NMAX=60 is INSUFFICIENT at 5× Rabi: worst top-5 "
              f"leakage {leak60_max_top5:.3e}. Increase NMAX.")


if __name__ == '__main__':
    main()
