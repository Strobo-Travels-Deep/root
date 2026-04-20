#!/usr/bin/env python3
"""
run_synced_phase_v2.py — Port of run_synced_phase.py to the restructured
stroboscopic package.

Runs the three physics configurations side-by-side and saves in the same
HDF5 layout as the original:
    synced  — continuous pulse + gap with motion AND spin detuning
    engine  — v0.9.1 engine-native: continuous pulse + motion-only gap
    R2      — Monroe-style impulsive kick + spin-only gap
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

from stroboscopic import (
    HilbertSpace, StroboTrain, build_strobo_train, backend,
)
from stroboscopic import operators as ops
from stroboscopic import propagators as prop
from stroboscopic.defaults import CODE_VERSION

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

OMEGA_M = 1.3
T_M = 2 * np.pi / OMEGA_M
DELTA_T_FRAC = 0.13
DELTA_T = DELTA_T_FRAC * T_M
N_PULSES = 30
ETA = 0.397
NMAX = 60
ALPHAS = [0.0, 3.0]

OMEGA_EFF = np.pi / (2 * N_PULSES * DELTA_T)
OMEGA_R = OMEGA_EFF / np.exp(-ETA**2 / 2)


def _prepare_psi0(hs, alpha, alpha_phase_deg):
    return hs.prepare_state(
        spin={'theta_deg': 0.0, 'phi_deg': 0.0},
        modes=[{'alpha': float(alpha), 'alpha_phase_deg': float(alpha_phase_deg)}],
    )


def _run_synced(hs, alpha, det_rel_grid, C, Cdag):
    """Continuous pulse + motion+spin gap (v0.9.1 Flag-1 closure)."""
    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))
    psi0 = _prepare_psi0(hs, alpha, shift_deg)
    sx = np.zeros(len(det_rel_grid))
    sy = np.zeros_like(sx); sz = np.zeros_like(sx)
    for i, d_rel in enumerate(det_rel_grid):
        delta = d_rel * OMEGA_M
        train = build_strobo_train(
            hs=hs, eta=ETA, omega_r=OMEGA_R, omega_m=OMEGA_M,
            delta=delta, n_pulses=N_PULSES, delta_t=DELTA_T,
            intra_pulse_motion=True, gap_includes_spin_detuning=True,
            C=C, Cdag=Cdag,
        )
        obs = hs.observables(train.evolve(psi0))
        sx[i], sy[i], sz[i] = obs['sigma_x'], obs['sigma_y'], obs['sigma_z']
    return sx, sy, sz


def _run_engine_native(hs, alpha, det_rel_grid, C, Cdag):
    """v0.9.1 engine-native: continuous pulse + motion-only gap."""
    # Legacy run_v09_current_engine uses alpha_phase_deg=0.0 and relies on the
    # engine's center_pulses_at_phase=True shift internally.
    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))
    psi0 = _prepare_psi0(hs, alpha, shift_deg)
    sx = np.zeros(len(det_rel_grid))
    sy = np.zeros_like(sx); sz = np.zeros_like(sx)
    for i, d_rel in enumerate(det_rel_grid):
        delta = d_rel * OMEGA_M
        train = build_strobo_train(
            hs=hs, eta=ETA, omega_r=OMEGA_R, omega_m=OMEGA_M,
            delta=delta, n_pulses=N_PULSES, delta_t=DELTA_T,
            intra_pulse_motion=True, gap_includes_spin_detuning=False,
            C=C, Cdag=Cdag,
        )
        obs = hs.observables(train.evolve(psi0))
        sx[i], sy[i], sz[i] = obs['sigma_x'], obs['sigma_y'], obs['sigma_z']
    return sx, sy, sz


def _run_r2_impulsive(hs, alpha, det_rel_grid, C, Cdag):
    """R2 Monroe impulsive kick + spin-only gap."""
    psi0 = _prepare_psi0(hs, alpha, 0.0)
    omega_eff = OMEGA_R * np.exp(-ETA**2 / 2)
    pulse_area = OMEGA_R * np.pi / (2 * N_PULSES * omega_eff)
    K = prop.build_impulsive_pulse(pulse_area, hs.nmax, C, Cdag)
    sx = np.zeros(len(det_rel_grid))
    sy = np.zeros_like(sx); sz = np.zeros_like(sx)
    for i, d_rel in enumerate(det_rel_grid):
        delta = d_rel * OMEGA_M
        U_gap = prop.build_U_gap(
            hs.nmax, OMEGA_M, T_M, delta=delta,
            include_motion=False, include_spin_detuning=True,
        )
        train = StroboTrain(U_pulse=K, U_gap_diag=U_gap, n_pulses=N_PULSES)
        obs = hs.observables(train.evolve(psi0))
        sx[i], sy[i], sz[i] = obs['sigma_x'], obs['sigma_y'], obs['sigma_z']
    return sx, sy, sz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', choices=['numpy', 'jax'], default='numpy')
    ap.add_argument('--output', default=None)
    args = ap.parse_args()
    backend.set_backend(args.backend)

    det_rel_max = 0.5 / OMEGA_M
    n_det = 201
    det_rel = np.linspace(-det_rel_max, +det_rel_max, n_det)

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX); Cdag = C.conj().T

    results = {}
    for a in ALPHAS:
        print(f'\n=== |α| = {a} ===')
        t0 = time.time(); sx_s, sy_s, sz_s = _run_synced(hs, a, det_rel, C, Cdag)
        t1 = time.time(); sx_e, sy_e, sz_e = _run_engine_native(hs, a, det_rel, C, Cdag)
        t2 = time.time(); sx_r, sy_r, sz_r = _run_r2_impulsive(hs, a, det_rel, C, Cdag)
        t3 = time.time()
        print(f'  synced-phase: {t1-t0:.1f}s')
        print(f'  v0.9.1 current engine: {t2-t1:.1f}s')
        print(f'  R2 Monroe impulsive: {t3-t2:.1f}s')
        results[a] = {
            'synced': dict(sx=sx_s, sy=sy_s, sz=sz_s),
            'engine': dict(sx=sx_e, sy=sy_e, sz=sz_e),
            'R2':     dict(sx=sx_r, sy=sy_r, sz=sz_r),
        }
        i0 = int(np.argmin(np.abs(det_rel)))
        for k, d in results[a].items():
            Cmag = np.sqrt(d['sx']**2 + d['sy']**2)
            print(f'    {k:8s}:  |C|(δ=0) = {Cmag[i0]:.5f}   max|C| on grid = {Cmag.max():.5f}')

    out = args.output or os.path.join(SCRIPT_DIR, 'synced_phase_alpha0and3_v2.h5')
    with h5py.File(out, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi', data=det_rel * OMEGA_M)
        f.attrs['alpha_values'] = ALPHAS
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['omega_r'] = OMEGA_R
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['T_gap_us'] = T_M - DELTA_T
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['engine'] = 'stroboscopic (restructured)'
        f.attrs['backend'] = args.backend
        f.attrs['purpose'] = ('Flag 1 closure: synced-phase convention '
                              'vs v0.9.1 current engine (no inter-pulse δ) '
                              'vs R2 Monroe impulsive.')
        for a in ALPHAS:
            g = f.create_group(f'alpha_{a:g}')
            for k, d in results[a].items():
                gg = g.create_group(k)
                for kk, vv in d.items():
                    gg.create_dataset(kk, data=vv)
    print(f'\nWrote {out}')


if __name__ == '__main__':
    main()
