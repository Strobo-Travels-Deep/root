#!/usr/bin/env python3
"""
run_S2_v09_compare_v2.py — Port of run_S2_v09_compare.py to the restructured
stroboscopic package.

Physics mode: v0.9.1 engine-native (continuous pulse with intra_pulse_motion,
motion-only gap — no spin detuning phase in the gap). Reproduces the same
S2 (δ₀, φ_α) sheet and its HDF5 layout, including per-φ max_fock_leakage.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone

import h5py
import numpy as np

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts')))

from stroboscopic import HilbertSpace, build_strobo_train, backend
from stroboscopic import operators as ops
from stroboscopic.defaults import CODE_VERSION

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

ALPHA = 3.0
ETA = 0.397
OMEGA_M = 1.3
T_M = 2 * np.pi / OMEGA_M
DELTA_T = 0.13 * T_M
N_PULSES = 30
DEBYE = np.exp(-ETA**2 / 2)
OMEGA_R = (np.pi / (2 * N_PULSES * DELTA_T)) / DEBYE
NMAX = 60

N_PHI = 64
N_DET = 121
DET_REL_MAX = 6.0 / OMEGA_M


def run(output_path: str, backend_name: str):
    backend.set_backend(backend_name)

    det_rel = np.linspace(-DET_REL_MAX, +DET_REL_MAX, N_DET)
    phi_deg = np.linspace(0.0, 360.0, N_PHI, endpoint=False)

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX); Cdag = C.conj().T
    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))

    print(f'S2 v0.9 comparison sheet at |α| = {ALPHA}  (backend={backend_name})')
    print(f'  N={N_PULSES}, δt={DELTA_T:.4f}, Ω={OMEGA_R:.4f}, Ω/ω_m={OMEGA_R/OMEGA_M:.3f}')
    print(f'  ω_m·δt = {OMEGA_M*DELTA_T:.3f} rad   (intra-pulse smearing on)\n')

    sx = np.zeros((N_PHI, N_DET))
    sy = np.zeros((N_PHI, N_DET))
    sz = np.zeros((N_PHI, N_DET))
    leak = np.zeros(N_PHI)

    t0 = time.time()
    for j, phi in enumerate(phi_deg):
        psi0 = hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': ALPHA,
                    'alpha_phase_deg': float(phi) + shift_deg}],
        )
        worst = 0.0
        for i, d_rel in enumerate(det_rel):
            delta = d_rel * OMEGA_M
            train = build_strobo_train(
                hs=hs, eta=ETA, omega_r=OMEGA_R, omega_m=OMEGA_M,
                delta=delta, n_pulses=N_PULSES, delta_t=DELTA_T,
                intra_pulse_motion=True, gap_includes_spin_detuning=False,
                C=C, Cdag=Cdag,
            )
            psi = train.evolve(psi0)
            obs = hs.observables(psi)
            sx[j, i], sy[j, i], sz[j, i] = obs['sigma_x'], obs['sigma_y'], obs['sigma_z']
            lk = hs.fock_leakage(psi, top_k=3)
            if lk > worst:
                worst = lk
        leak[j] = worst
        if (j + 1) % 8 == 0:
            print(f'  φ_α {j+1}/{N_PHI}  worst leak {leak[j]:.1e}', flush=True)
    elapsed = time.time() - t0
    print(f'  done — {elapsed:.1f} s  worst Fock leakage {leak.max():.2e}')

    C_abs = np.sqrt(sx**2 + sy**2)
    C_arg_deg = np.degrees(np.arctan2(sy, sx))
    delta_C_abs = C_abs - C_abs[0:1]
    worst_dC = float(np.abs(delta_C_abs).max())
    print(f'\n  worst |Δ|C|(δ, φ_α)| vs φ=0: {worst_dC:.4e}')

    with h5py.File(output_path, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi', data=det_rel * OMEGA_M)
        f.create_dataset('phi_alpha_deg', data=phi_deg)
        f.create_dataset('sigma_x', data=sx)
        f.create_dataset('sigma_y', data=sy)
        f.create_dataset('sigma_z', data=sz)
        f.create_dataset('C_abs', data=C_abs)
        f.create_dataset('C_arg_deg', data=C_arg_deg)
        f.create_dataset('max_fock_leakage', data=leak)
        f.attrs['slice'] = 'S2_v09_compare'
        f.attrs['alpha'] = ALPHA
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['omega_r'] = OMEGA_R
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['delta_t_frac_Tm'] = 0.13
        f.attrs['intra_pulse_motion'] = 1
        f.attrs['mw_pi2_phase_deg'] = -1
        f.attrs['center_pulses_at_phase'] = 1
        f.attrs['nmax'] = NMAX
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['engine'] = 'stroboscopic (restructured)'
        f.attrs['backend'] = backend_name
        f.attrs['notes'] = (
            'S2 (δ₀, φ_α) at |α|=3 under v0.9 D1 + Hasse-matched (N=30, '
            'δt=0.13·T_m). Port of run_S2_v09_compare.py onto the '
            'restructured stroboscopic package.'
        )
    print(f'  wrote {output_path}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', choices=['numpy', 'jax'], default='numpy')
    ap.add_argument('--output', default=None)
    args = ap.parse_args()
    out = args.output or os.path.join(SCRIPT_DIR, 'S2_v09_alpha3_v2.h5')
    run(out, args.backend)


if __name__ == '__main__':
    main()
