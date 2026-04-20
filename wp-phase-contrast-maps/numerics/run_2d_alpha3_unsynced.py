#!/usr/bin/env python3
"""
run_2d_alpha3_unsynced.py — 2D (δ₀, φ_α) scan at |α|=3, ±15 MHz × [0, 2π),
v0.9.1 engine convention (NO inter-pulse U_gap).

Companion to run_2d_alpha3.py. Same grid, same parameters, same Hasse-
matched timing, except that between pulses NO free evolution is
applied — this is what the engine does natively at t_sep_factor = 1.0.

This isolates what the engine predicts without the synced-phase fix
Flag 1 installed. Direct comparison at the heatmap level reveals
whether/where the two conventions diverge.

Output: numerics/scan_2d_alpha3_unsynced.h5
"""

import os, sys, time, numpy as np, h5py
from scipy.linalg import expm

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts')))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stroboscopic_sweep as ss

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
N_DET = 1001
N_PHI = 64


def main():
    det_rel = np.linspace(-DET_MAX_REL, +DET_MAX_REL, N_DET)
    det_MHz = det_rel * OMEGA_M
    phi_deg = np.linspace(0.0, 360.0, N_PHI, endpoint=False)

    dim = 2 * NMAX
    _, _, X = ss.build_operators(NMAX)
    C = ss.build_coupling(ETA, NMAX, X); Cdag = C.conj().T

    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))

    print(f'Preparing {N_PHI} initial states...')
    psi0_list = []
    for phi in phi_deg:
        pp = dict(ss.DEFAULTS)
        pp.update(alpha=ALPHA, alpha_phase_deg=float(phi) + shift_deg,
                  eta=ETA, nmax=NMAX)
        pp = ss._enforce_types(pp)
        psi_m = ss.prepare_motional(pp)
        psi0_list.append(ss.tensor_spin_motion(0.0, 0.0, psi_m, NMAX))

    sx = np.zeros((N_PHI, N_DET)); sy = np.zeros((N_PHI, N_DET))
    sz = np.zeros((N_PHI, N_DET))

    # Engine-native inter-pulse Ufree: MOTIONAL-ONLY, closes 2π per cycle.
    # NO spin detuning phase accumulation during the gap (engine convention).
    T_gap = T_M - DELTA_T
    U_gap_motion_only = np.zeros((dim, dim), dtype=complex)
    for n in range(NMAX):
        ph_mot = np.exp(-1j * OMEGA_M * n * T_gap)
        U_gap_motion_only[n, n]           = ph_mot
        U_gap_motion_only[NMAX + n, NMAX + n] = ph_mot

    print(f'Engine-native scan: {N_DET} × {N_PHI} (motional U_gap only, no spin δ phase in gap)…')
    t0 = time.time()
    for i, d_rel in enumerate(det_rel):
        delta = d_rel * OMEGA_M
        H_pulse = ss.build_hamiltonian(
            ETA, OMEGA_R, delta, NMAX, C, Cdag,
            ac_phase_rad=0.0, omega_m=OMEGA_M,
            intra_pulse_motion=True,
        )
        U_pulse = expm(-1j * H_pulse * DELTA_T)

        for j, psi0 in enumerate(psi0_list):
            psi = psi0.copy()
            for k in range(N_PULSES):
                psi = U_pulse @ psi
                if k < N_PULSES - 1:
                    psi = U_gap_motion_only @ psi
            obs = ss.compute_observables(psi, NMAX)
            sx[j, i] = obs['sigma_x']
            sy[j, i] = obs['sigma_y']
            sz[j, i] = obs['sigma_z']

        if (i + 1) % max(1, N_DET // 20) == 0:
            eta = (N_DET - i - 1) * (time.time() - t0) / (i + 1)
            print(f'  {i+1}/{N_DET}  ETA {eta:.0f}s', flush=True)
    print(f'Done — {time.time()-t0:.1f}s total.')

    C_abs = np.sqrt(sx**2 + sy**2)
    C_arg_deg = np.degrees(np.arctan2(sy, sx))

    out = os.path.join(SCRIPT_DIR, 'scan_2d_alpha3_unsynced.h5')
    with h5py.File(out, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi', data=det_MHz)
        f.create_dataset('phi_alpha_deg', data=phi_deg)
        f.create_dataset('sigma_x', data=sx)
        f.create_dataset('sigma_y', data=sy)
        f.create_dataset('sigma_z', data=sz)
        f.create_dataset('C_abs',   data=C_abs)
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
        f.attrs['convention'] = 'engine-native v0.9.1 (motional U_gap only, no spin δ phase in gap)'
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['det_step_kHz'] = float(det_MHz[1] - det_MHz[0]) * 1000
    print(f'Wrote {out}')


if __name__ == '__main__':
    main()
