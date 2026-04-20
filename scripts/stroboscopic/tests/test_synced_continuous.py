"""Bit-for-bit reproduction of the synced-phase continuous-pulse physics.

Target: wp-phase-contrast-maps/numerics/run_2d_alpha3.py inner loop.
Expected tolerance: 0.0 (machine-identical operation order).
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm

import stroboscopic_sweep as ss
from stroboscopic import HilbertSpace, build_strobo_train
from stroboscopic import operators as ops_new


def _legacy(physics, small_grid):
    p = physics
    NMAX = p['NMAX']
    T_gap = p['T_M'] - p['DELTA_T']
    dim = 2 * NMAX

    _, _, X = ss.build_operators(NMAX)
    C = ss.build_coupling(p['ETA'], NMAX, X); Cdag = C.conj().T
    shift_deg = float(np.degrees(p['OMEGA_M'] * p['DELTA_T'] / 2))

    psi0_list = []
    for phi in small_grid['phi_deg']:
        pp = dict(ss.DEFAULTS)
        pp.update(alpha=p['ALPHA'], alpha_phase_deg=float(phi) + shift_deg,
                  eta=p['ETA'], nmax=NMAX)
        pp = ss._enforce_types(pp)
        psi_m = ss.prepare_motional(pp)
        psi0_list.append(ss.tensor_spin_motion(0.0, 0.0, psi_m, NMAX))

    n_phi = len(small_grid['phi_deg'])
    n_det = len(small_grid['det_rel'])
    sx = np.zeros((n_phi, n_det)); sy = np.zeros_like(sx); sz = np.zeros_like(sx)
    for i, d in enumerate(small_grid['det_rel']):
        delta = d * p['OMEGA_M']
        H = ss.build_hamiltonian(p['ETA'], p['OMEGA_R'], delta, NMAX, C, Cdag,
                                 ac_phase_rad=0.0, omega_m=p['OMEGA_M'],
                                 intra_pulse_motion=True)
        U_pulse = expm(-1j * H * p['DELTA_T'])

        ph_d = np.exp(+1j * delta / 2 * T_gap); ph_u = np.exp(-1j * delta / 2 * T_gap)
        U_gap = np.zeros((dim, dim), dtype=complex)
        for n in range(NMAX):
            ph_mot = np.exp(-1j * p['OMEGA_M'] * n * T_gap)
            U_gap[n, n] = ph_mot * ph_d
            U_gap[NMAX + n, NMAX + n] = ph_mot * ph_u
        for j, psi0 in enumerate(psi0_list):
            psi = psi0.copy()
            for k in range(p['N_PULSES']):
                psi = U_pulse @ psi
                if k < p['N_PULSES'] - 1:
                    psi = U_gap @ psi
            o = ss.compute_observables(psi, NMAX)
            sx[j, i] = o['sigma_x']; sy[j, i] = o['sigma_y']; sz[j, i] = o['sigma_z']
    return sx, sy, sz


def _new(physics, small_grid):
    p = physics
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(p['NMAX'],))
    shift_deg = float(np.degrees(p['OMEGA_M'] * p['DELTA_T'] / 2))
    C = ops_new.coupling(p['ETA'], p['NMAX']); Cdag = C.conj().T

    psi0_list = [
        hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': p['ALPHA'],
                    'alpha_phase_deg': float(phi) + shift_deg}],
        )
        for phi in small_grid['phi_deg']
    ]

    n_phi = len(small_grid['phi_deg'])
    n_det = len(small_grid['det_rel'])
    sx = np.zeros((n_phi, n_det)); sy = np.zeros_like(sx); sz = np.zeros_like(sx)
    for i, d in enumerate(small_grid['det_rel']):
        delta = d * p['OMEGA_M']
        train = build_strobo_train(
            hs=hs, eta=p['ETA'], omega_r=p['OMEGA_R'], omega_m=p['OMEGA_M'],
            delta=delta, n_pulses=p['N_PULSES'], delta_t=p['DELTA_T'],
            intra_pulse_motion=True, gap_includes_spin_detuning=True,
            C=C, Cdag=Cdag,
        )
        for j, psi0 in enumerate(psi0_list):
            o = hs.observables(train.evolve(psi0))
            sx[j, i] = o['sigma_x']; sy[j, i] = o['sigma_y']; sz[j, i] = o['sigma_z']
    return sx, sy, sz


def test_synced_continuous_bit_for_bit(physics_params, small_grid):
    a = _legacy(physics_params, small_grid)
    b = _new(physics_params, small_grid)
    for name, arr_a, arr_b in zip(('sigma_x', 'sigma_y', 'sigma_z'), a, b):
        assert np.array_equal(arr_a, arr_b), \
            f'{name} diverged: max|Δ| = {np.max(np.abs(arr_a - arr_b)):.3e}'
