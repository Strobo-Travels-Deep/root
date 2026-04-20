#!/usr/bin/env python3
"""
run_2d_alpha3_unsynced_v2.py — Port of run_2d_alpha3_unsynced.py to the
restructured stroboscopic package.

Physics convention: v0.9.1 engine-native (motional-only U_gap, NO spin
detuning phase in the gap). Same grid, same parameters as the synced
variant, so the two can be diffed at the heatmap level.

Usage:
    python run_2d_alpha3_unsynced_v2.py           # full grid
    python run_2d_alpha3_unsynced_v2.py --quick   # 51 × 8
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import h5py
import numpy as np

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts')))

from stroboscopic import HilbertSpace, build_strobo_train, backend
from stroboscopic import operators as ops
from stroboscopic.defaults import CODE_VERSION

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

OMEGA_M = 1.3
T_M = 2 * np.pi / OMEGA_M
DELTA_T = 0.13 * T_M
N_PULSES = 30
ETA = 0.397
NMAX = 60
ALPHA = 3.0
OMEGA_EFF = np.pi / (2 * N_PULSES * DELTA_T)
OMEGA_R = OMEGA_EFF / np.exp(-ETA**2 / 2)

DET_MAX_MHz = 15.0
DET_MAX_REL = DET_MAX_MHz / OMEGA_M


def run(n_det: int, n_phi: int, output_path: str, backend_name: str):
    backend.set_backend(backend_name)

    det_rel = np.linspace(-DET_MAX_REL, +DET_MAX_REL, n_det)
    det_MHz = det_rel * OMEGA_M
    phi_deg = np.linspace(0.0, 360.0, n_phi, endpoint=False)

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))

    C = ops.coupling(ETA, NMAX); Cdag = C.conj().T

    print(f'Preparing {n_phi} initial states...')
    psi0_list = [
        hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': ALPHA, 'alpha_phase_deg': float(phi) + shift_deg}],
        )
        for phi in phi_deg
    ]

    sx = np.zeros((n_phi, n_det)); sy = np.zeros((n_phi, n_det))
    sz = np.zeros((n_phi, n_det))

    print(f'Engine-native scan: {n_det} × {n_phi} (motional U_gap only, '
          f'no spin δ phase in gap)… (backend={backend_name})')
    t0 = time.time()
    for i, d_rel in enumerate(det_rel):
        delta = d_rel * OMEGA_M
        train = build_strobo_train(
            hs=hs, eta=ETA, omega_r=OMEGA_R, omega_m=OMEGA_M,
            delta=delta, n_pulses=N_PULSES, delta_t=DELTA_T,
            t_sep_factor=1.0, ac_phase_rad=0.0,
            intra_pulse_motion=True,
            gap_includes_spin_detuning=False,   # engine-native
            C=C, Cdag=Cdag,
        )
        for j, psi0 in enumerate(psi0_list):
            obs = hs.observables(train.evolve(psi0))
            sx[j, i] = obs['sigma_x']
            sy[j, i] = obs['sigma_y']
            sz[j, i] = obs['sigma_z']

        if (i + 1) % max(1, n_det // 20) == 0:
            eta_s = (n_det - i - 1) * (time.time() - t0) / (i + 1)
            print(f'  {i+1}/{n_det}  ETA {eta_s:.0f}s', flush=True)
    print(f'Done — {time.time()-t0:.1f}s total.')

    C_abs = np.sqrt(sx**2 + sy**2)
    C_arg_deg = np.degrees(np.arctan2(sy, sx))

    with h5py.File(output_path, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi', data=det_MHz)
        f.create_dataset('phi_alpha_deg', data=phi_deg)
        f.create_dataset('sigma_x', data=sx)
        f.create_dataset('sigma_y', data=sy)
        f.create_dataset('sigma_z', data=sz)
        f.create_dataset('C_abs', data=C_abs)
        f.create_dataset('C_arg_deg', data=C_arg_deg)
        f.attrs['slice'] = '2D_alpha3_unsynced'
        f.attrs['alpha'] = ALPHA
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['omega_r'] = OMEGA_R
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['nmax'] = NMAX
        f.attrs['intra_pulse_motion'] = 1
        f.attrs['center_pulses_at_phase'] = 1
        f.attrs['convention'] = ('engine-native v0.9.1 (motional U_gap only, '
                                 'no spin δ phase in gap)')
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['engine'] = 'stroboscopic (restructured)'
        f.attrs['backend'] = backend_name
        f.attrs['det_step_kHz'] = float(det_MHz[1] - det_MHz[0]) * 1000
    print(f'Wrote {output_path}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--quick', action='store_true')
    p.add_argument('--n-det', type=int, default=1001)
    p.add_argument('--n-phi', type=int, default=64)
    p.add_argument('--backend', choices=['numpy', 'jax'], default='numpy')
    p.add_argument('--output', default=None)
    args = p.parse_args()

    if args.quick:
        n_det, n_phi = 51, 8
        default_out = 'scan_2d_alpha3_unsynced_v2_quick.h5'
    else:
        n_det, n_phi = args.n_det, args.n_phi
        default_out = 'scan_2d_alpha3_unsynced_v2.h5'
    output = args.output or os.path.join(SCRIPT_DIR, default_out)

    run(n_det, n_phi, output, args.backend)


if __name__ == '__main__':
    main()
