"""Engine-native (ss.run_single) vs the new package.

The legacy run_single path uses a slightly different FP operation order
for U_gap construction (`phase_per_n = ω_m·gap` precomputed, then
`exp(-i·n·phase_per_n)`), so the new package matches only to
floating-point reassociation noise (< 1e-13), not bit-for-bit.
"""
from __future__ import annotations

import numpy as np

import stroboscopic_sweep as ss
from stroboscopic import HilbertSpace, build_strobo_train
from stroboscopic import operators as ops_new


def _legacy(p, g):
    """ss.run_single path at t_sep_factor=1.0, intra_pulse_motion=True."""
    NMAX = p['NMAX']
    n_phi = len(g['phi_deg']); n_det = len(g['det_rel'])
    sx = np.zeros((n_phi, n_det)); sy = np.zeros_like(sx); sz = np.zeros_like(sx)
    for j, phi in enumerate(g['phi_deg']):
        pp = dict(
            alpha=p['ALPHA'], alpha_phase_deg=float(phi),
            eta=p['ETA'], omega_m=p['OMEGA_M'], omega_r=p['OMEGA_R'],
            n_pulses=p['N_PULSES'], n_thermal=0.0, nmax=NMAX,
            det_min=float(g['det_rel'][0]), det_max=float(g['det_rel'][-1]),
            npts=len(g['det_rel']),
            theta_deg=0.0, phi_deg=0.0,
            squeeze_r=0.0, squeeze_phi_deg=0.0,
            t_sep_factor=1.0,
            T1=0.0, T2=0.0, heating=0.0,
            n_traj=1, n_thermal_traj=1, n_rep=0,
            intra_pulse_motion=True,
            delta_t_us=p['DELTA_T'],
            center_pulses_at_phase=True,
        )
        d, _ = ss.run_single(pp, verbose=False)
        sx[j] = d['sigma_x']; sy[j] = d['sigma_y']; sz[j] = d['sigma_z']
    return sx, sy, sz


def _new(p, g):
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(p['NMAX'],))
    shift_deg = float(np.degrees(p['OMEGA_M'] * p['DELTA_T'] / 2))
    C = ops_new.coupling(p['ETA'], p['NMAX']); Cdag = C.conj().T
    psi0_list = [
        hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': p['ALPHA'],
                    'alpha_phase_deg': float(phi) + shift_deg}])
        for phi in g['phi_deg']
    ]
    n_phi = len(g['phi_deg']); n_det = len(g['det_rel'])
    sx = np.zeros((n_phi, n_det)); sy = np.zeros_like(sx); sz = np.zeros_like(sx)
    for i, d in enumerate(g['det_rel']):
        delta = d * p['OMEGA_M']
        train = build_strobo_train(
            hs=hs, eta=p['ETA'], omega_r=p['OMEGA_R'], omega_m=p['OMEGA_M'],
            delta=delta, n_pulses=p['N_PULSES'], delta_t=p['DELTA_T'],
            intra_pulse_motion=True, gap_includes_spin_detuning=False,
            C=C, Cdag=Cdag,
        )
        for j, psi0 in enumerate(psi0_list):
            o = hs.observables(train.evolve(psi0))
            sx[j, i] = o['sigma_x']; sy[j, i] = o['sigma_y']; sz[j, i] = o['sigma_z']
    return sx, sy, sz


def test_engine_native_within_fp_noise(physics_params, small_grid):
    a = _legacy(physics_params, small_grid)
    b = _new(physics_params, small_grid)
    for name, arr_a, arr_b in zip(('sigma_x', 'sigma_y', 'sigma_z'), a, b):
        diff = float(np.max(np.abs(arr_a - arr_b)))
        assert diff < 1e-13, f'{name} diverged: max|Δ| = {diff:.3e}'
