"""Bit-for-bit reproduction of the R2 impulsive-kick physics.

Target: wp-phase-contrast-maps/numerics/run_slices.run_R2_single.
Expected tolerance: 0.0.
"""
from __future__ import annotations

import numpy as np
import pytest
from scipy.linalg import expm

import stroboscopic_sweep as ss
from stroboscopic import HilbertSpace, StroboTrain
from stroboscopic import operators as ops_new
from stroboscopic import propagators as prop_new


def _legacy(alpha, alpha_phase_deg, p, det_rel_grid):
    NMAX = p['NMAX']; dim = 2 * NMAX
    _, _, X = ss.build_operators(NMAX)
    C = ss.build_coupling(p['ETA'], NMAX, X); Cdag = C.conj().T

    omega_eff = p['OMEGA_R'] * np.exp(-p['ETA']**2 / 2)
    pulse_area = p['OMEGA_R'] * np.pi / (2 * p['N_PULSES'] * omega_eff)
    K_gen = np.zeros((dim, dim), dtype=complex)
    K_gen[:NMAX, NMAX:] = C
    K_gen[NMAX:, :NMAX] = Cdag
    K = expm(-1j * (pulse_area / 2) * K_gen)

    pp = dict(ss.DEFAULTS)
    pp.update(alpha=float(alpha), alpha_phase_deg=float(alpha_phase_deg),
              eta=float(p['ETA']), nmax=NMAX)
    pp = ss._enforce_types(pp)
    psi_m = ss.prepare_motional(pp)
    psi0 = ss.tensor_spin_motion(0.0, 0.0, psi_m, NMAX)

    Tm = p['T_M']
    sx = np.zeros(len(det_rel_grid)); sy = np.zeros_like(sx); sz = np.zeros_like(sx)
    for i, d in enumerate(det_rel_grid):
        delta = d * p['OMEGA_M']
        ph_d = np.exp(+1j * delta / 2 * Tm); ph_u = np.exp(-1j * delta / 2 * Tm)
        Ufree = np.zeros((dim, dim), dtype=complex)
        for n in range(NMAX):
            Ufree[n, n] = ph_d
            Ufree[NMAX + n, NMAX + n] = ph_u
        psi = psi0.copy()
        for k in range(p['N_PULSES']):
            psi = K @ psi
            if k < p['N_PULSES'] - 1:
                psi = Ufree @ psi
        o = ss.compute_observables(psi, NMAX)
        sx[i] = o['sigma_x']; sy[i] = o['sigma_y']; sz[i] = o['sigma_z']
    return sx, sy, sz


def _new(alpha, alpha_phase_deg, p, det_rel_grid):
    NMAX = p['NMAX']
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    psi0 = hs.prepare_state(
        spin={'theta_deg': 0.0, 'phi_deg': 0.0},
        modes=[{'alpha': float(alpha), 'alpha_phase_deg': float(alpha_phase_deg)}],
    )
    omega_eff = p['OMEGA_R'] * np.exp(-p['ETA']**2 / 2)
    pulse_area = p['OMEGA_R'] * np.pi / (2 * p['N_PULSES'] * omega_eff)
    C = ops_new.coupling(p['ETA'], NMAX); Cdag = C.conj().T
    K = prop_new.build_impulsive_pulse(pulse_area, NMAX, C, Cdag)
    Tm = p['T_M']
    sx = np.zeros(len(det_rel_grid)); sy = np.zeros_like(sx); sz = np.zeros_like(sx)
    for i, d in enumerate(det_rel_grid):
        delta = d * p['OMEGA_M']
        U_gap = prop_new.build_U_gap(NMAX, p['OMEGA_M'], Tm, delta=delta,
                                     include_motion=False, include_spin_detuning=True)
        train = StroboTrain(U_pulse=K, U_gap_diag=U_gap, n_pulses=p['N_PULSES'])
        o = hs.observables(train.evolve(psi0))
        sx[i] = o['sigma_x']; sy[i] = o['sigma_y']; sz[i] = o['sigma_z']
    return sx, sy, sz


@pytest.mark.parametrize('alpha,phi', [
    (0.0, 0.0), (1.0, 0.0), (3.0, 0.0),
    (0.0, 45.0), (3.0, 45.0), (3.0, 90.0),
])
def test_r2_impulsive_bit_for_bit(physics_params, alpha, phi):
    det_rel = np.linspace(-6.0 / physics_params['OMEGA_M'],
                          +6.0 / physics_params['OMEGA_M'], 21)
    a = _legacy(alpha, phi, physics_params, det_rel)
    b = _new(alpha, phi, physics_params, det_rel)
    for name, arr_a, arr_b in zip(('sigma_x', 'sigma_y', 'sigma_z'), a, b):
        assert np.array_equal(arr_a, arr_b), \
            f'{name} diverged (α={alpha}, φ={phi}): max|Δ| = {np.max(np.abs(arr_a - arr_b)):.3e}'
