"""Bit-for-bit validation of the R2 impulsive-pulse path.

Reproduces wp-phase-contrast-maps/numerics/run_slices.run_R2_single with
(a) the legacy scripts/stroboscopic_sweep.py helpers + hand-rolled loop
(b) the new package's build_impulsive_train

Usage:
    python -m scripts.stroboscopic.validate_r2
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
from scipy.linalg import expm

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.dirname(_HERE)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import stroboscopic_sweep as ss

from . import backend, HilbertSpace, StroboTrain
from . import operators as ops_new
from . import propagators as prop_new


def _legacy_r2(alpha, alpha_phase_deg, eta, det_rel_grid,
               n_pulses, nmax, omega_m, omega_r):
    """Re-implementation of wp-.../run_slices.run_R2_single."""
    dim = 2 * nmax
    _, _, X = ss.build_operators(nmax)
    C = ss.build_coupling(eta, nmax, X); Cdag = C.conj().T

    omega_eff = omega_r * np.exp(-eta**2 / 2)
    pulse_area = omega_r * np.pi / (2 * n_pulses * omega_eff)
    K_gen = np.zeros((dim, dim), dtype=complex)
    K_gen[:nmax, nmax:] = C
    K_gen[nmax:, :nmax] = Cdag
    K = expm(-1j * (pulse_area / 2) * K_gen)

    p = dict(ss.DEFAULTS)
    p.update(alpha=float(alpha), alpha_phase_deg=float(alpha_phase_deg),
             eta=float(eta), nmax=nmax)
    p = ss._enforce_types(p)
    psi_m = ss.prepare_motional(p)
    psi0 = ss.tensor_spin_motion(0.0, 0.0, psi_m, nmax)

    Tm = 2 * np.pi / omega_m
    sx = np.zeros(len(det_rel_grid)); sy = np.zeros_like(sx); sz = np.zeros_like(sx)

    for i, d_rel in enumerate(det_rel_grid):
        delta = d_rel * omega_m
        ph_d = np.exp(+1j * delta / 2 * Tm)
        ph_u = np.exp(-1j * delta / 2 * Tm)
        Ufree = np.zeros((dim, dim), dtype=complex)
        for n in range(nmax):
            Ufree[n, n] = ph_d
            Ufree[nmax + n, nmax + n] = ph_u

        psi = psi0.copy()
        for k in range(n_pulses):
            psi = K @ psi
            if k < n_pulses - 1:
                psi = Ufree @ psi
        obs = ss.compute_observables(psi, nmax)
        sx[i] = obs['sigma_x']; sy[i] = obs['sigma_y']; sz[i] = obs['sigma_z']
    return sx, sy, sz


def _new_r2(alpha, alpha_phase_deg, eta, det_rel_grid,
            n_pulses, nmax, omega_m, omega_r):
    """Recommended pattern: K is δ-independent, build it once outside the loop."""
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(nmax,))
    psi0 = hs.prepare_state(
        spin={'theta_deg': 0.0, 'phi_deg': 0.0},
        modes=[{'alpha': float(alpha), 'alpha_phase_deg': float(alpha_phase_deg)}],
    )
    omega_eff = omega_r * np.exp(-eta**2 / 2)
    pulse_area = omega_r * np.pi / (2 * n_pulses * omega_eff)

    C = ops_new.coupling(eta, nmax); Cdag = C.conj().T
    K = prop_new.build_impulsive_pulse(pulse_area, nmax, C, Cdag)
    Tm = 2 * np.pi / omega_m

    sx = np.zeros(len(det_rel_grid)); sy = np.zeros_like(sx); sz = np.zeros_like(sx)

    for i, d_rel in enumerate(det_rel_grid):
        delta = d_rel * omega_m
        U_gap = prop_new.build_U_gap(
            nmax, omega_m, Tm, delta=delta,
            include_motion=False, include_spin_detuning=True,
        )
        train = StroboTrain(U_pulse=K, U_gap_diag=U_gap, n_pulses=n_pulses)
        obs = hs.observables(train.evolve(psi0))
        sx[i] = obs['sigma_x']; sy[i] = obs['sigma_y']; sz[i] = obs['sigma_z']
    return sx, sy, sz


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--backend', choices=['numpy', 'jax'], default='numpy')
    p.add_argument('--atol', type=float, default=1e-12)
    args = p.parse_args()
    backend.set_backend(args.backend)

    ETA = 0.397
    OMEGA_M = 1.3
    OMEGA_R = 0.300
    N_PULSES = 22
    NMAX = 30
    DET_MAX_REL = 6.0 / OMEGA_M
    N_DET = 41

    det_rel = np.linspace(-DET_MAX_REL, +DET_MAX_REL, N_DET)

    diffs_all = {}
    for alpha in (0.0, 1.0, 3.0):
        for phi in (0.0, 45.0):
            t = time.time()
            a_sx, a_sy, a_sz = _legacy_r2(alpha, phi, ETA, det_rel,
                                          N_PULSES, NMAX, OMEGA_M, OMEGA_R)
            t_l = time.time() - t
            t = time.time()
            b_sx, b_sy, b_sz = _new_r2(alpha, phi, ETA, det_rel,
                                       N_PULSES, NMAX, OMEGA_M, OMEGA_R)
            t_n = time.time() - t
            d = {
                'sigma_x': np.max(np.abs(a_sx - b_sx)),
                'sigma_y': np.max(np.abs(a_sy - b_sy)),
                'sigma_z': np.max(np.abs(a_sz - b_sz)),
            }
            tag = f'α={alpha}  φ={phi}'
            print(f'  [{tag:18s}]  legacy {t_l:.2f}s  new {t_n:.2f}s  '
                  f'max|Δ|: sx {d["sigma_x"]:.1e}  sy {d["sigma_y"]:.1e}  sz {d["sigma_z"]:.1e}')
            diffs_all[tag] = d

    worst = max(d_[k] for d_ in diffs_all.values() for k in d_)
    status = 'PASS' if worst < args.atol else 'FAIL'
    print(f'[validate_r2] {status}  (worst = {worst:.3e}, atol = {args.atol:.0e})')
    return 0 if worst < args.atol else 1


if __name__ == '__main__':
    sys.exit(main())
