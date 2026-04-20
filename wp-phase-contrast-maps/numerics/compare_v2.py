#!/usr/bin/env python3
"""Compare scan_2d_alpha3_v2_quick.h5 against a legacy-engine recomputation."""
from __future__ import annotations

import os, sys, numpy as np, h5py
from scipy.linalg import expm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', 'scripts')))

import stroboscopic_sweep as ss

# Must match the v2 quick grid exactly.
OMEGA_M = 1.3
T_M = 2*np.pi/OMEGA_M
DELTA_T = 0.13*T_M
N_PULSES = 30
ETA = 0.397
NMAX = 60
ALPHA = 3.0
OMEGA_EFF = np.pi/(2*N_PULSES*DELTA_T)
OMEGA_R = OMEGA_EFF/np.exp(-ETA**2/2)
DET_MAX_REL = 15.0/OMEGA_M
N_DET, N_PHI = 51, 8


def legacy_grid():
    det_rel = np.linspace(-DET_MAX_REL, +DET_MAX_REL, N_DET)
    phi_deg = np.linspace(0.0, 360.0, N_PHI, endpoint=False)

    _, _, X = ss.build_operators(NMAX)
    C = ss.build_coupling(ETA, NMAX, X); Cdag = C.conj().T
    shift_deg = float(np.degrees(OMEGA_M*DELTA_T/2))

    psi0_list = []
    for phi in phi_deg:
        pp = dict(ss.DEFAULTS)
        pp.update(alpha=ALPHA, alpha_phase_deg=float(phi)+shift_deg,
                  eta=ETA, nmax=NMAX)
        pp = ss._enforce_types(pp)
        psi_m = ss.prepare_motional(pp)
        psi0_list.append(ss.tensor_spin_motion(0.0, 0.0, psi_m, NMAX))

    T_gap = T_M - DELTA_T
    dim = 2*NMAX
    sx = np.zeros((N_PHI, N_DET)); sy = np.zeros_like(sx); sz = np.zeros_like(sx)

    for i, d in enumerate(det_rel):
        delta = d*OMEGA_M
        H = ss.build_hamiltonian(ETA, OMEGA_R, delta, NMAX, C, Cdag,
                                 ac_phase_rad=0.0, omega_m=OMEGA_M,
                                 intra_pulse_motion=True)
        U_pulse = expm(-1j*H*DELTA_T)

        ph_d = np.exp(+1j*delta/2*T_gap); ph_u = np.exp(-1j*delta/2*T_gap)
        U_gap = np.zeros((dim, dim), dtype=complex)
        for n in range(NMAX):
            ph_mot = np.exp(-1j*OMEGA_M*n*T_gap)
            U_gap[n, n] = ph_mot*ph_d
            U_gap[NMAX+n, NMAX+n] = ph_mot*ph_u

        for j, psi0 in enumerate(psi0_list):
            psi = psi0.copy()
            for k in range(N_PULSES):
                psi = U_pulse @ psi
                if k < N_PULSES - 1:
                    psi = U_gap @ psi
            o = ss.compute_observables(psi, NMAX)
            sx[j, i] = o['sigma_x']; sy[j, i] = o['sigma_y']; sz[j, i] = o['sigma_z']
    return det_rel, phi_deg, sx, sy, sz


def main():
    print('Running legacy engine on 51×8 grid...')
    det_L, phi_L, sx_L, sy_L, sz_L = legacy_grid()

    with h5py.File(os.path.join(HERE, 'scan_2d_alpha3_v2_quick.h5'), 'r') as f:
        det_V = f['detuning_rel'][:]
        phi_V = f['phi_alpha_deg'][:]
        sx_V = f['sigma_x'][:]; sy_V = f['sigma_y'][:]; sz_V = f['sigma_z'][:]

    assert np.allclose(det_L, det_V), 'detuning grid mismatch'
    assert np.allclose(phi_L, phi_V), 'phi grid mismatch'

    diffs = {'sigma_x': np.max(np.abs(sx_V - sx_L)),
             'sigma_y': np.max(np.abs(sy_V - sy_L)),
             'sigma_z': np.max(np.abs(sz_V - sz_L))}
    for k, d in diffs.items():
        print(f'  max |Δ{k}| = {d:.3e}')
    if all(d < 1e-12 for d in diffs.values()):
        print('PASS — v2 matches legacy bit-for-bit')
        return 0
    print('FAIL')
    return 1


if __name__ == '__main__':
    sys.exit(main())
