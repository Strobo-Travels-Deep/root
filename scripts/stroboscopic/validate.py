"""Bit-for-bit validation against legacy stroboscopic_sweep.py engine.

Reproduces the run_2d_alpha3.py inner loop on a small grid with both the
legacy engine and the new package (numpy and JAX backends), then asserts
matching arrays within tight tolerance.

Usage:
    python -m scripts.stroboscopic.validate
    python -m scripts.stroboscopic.validate --backend jax
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np

# Make 'scripts/' importable so we can load legacy stroboscopic_sweep.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.dirname(_HERE)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import stroboscopic_sweep as ss  # legacy engine

from scipy.linalg import expm as _scipy_expm

from . import backend, HilbertSpace, build_strobo_train
from . import operators as ops_new


# Mirror run_2d_alpha3.py fixed parameters
OMEGA_M = 1.3
T_M = 2 * np.pi / OMEGA_M
DELTA_T = 0.13 * T_M
N_PULSES = 30
ETA = 0.397
NMAX = 40
ALPHA = 3.0
OMEGA_EFF = np.pi / (2 * N_PULSES * DELTA_T)
OMEGA_R = OMEGA_EFF / np.exp(-ETA**2 / 2)


def _legacy_run(det_rel_grid, phi_deg_grid):
    """Replicate the run_2d_alpha3.py inner loop using the legacy ss API."""
    dim = 2 * NMAX
    _, _, X = ss.build_operators(NMAX)
    C = ss.build_coupling(ETA, NMAX, X); Cdag = C.conj().T

    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))
    psi0_list = []
    for phi in phi_deg_grid:
        pp = dict(ss.DEFAULTS)
        pp.update(alpha=ALPHA, alpha_phase_deg=float(phi) + shift_deg,
                  eta=ETA, nmax=NMAX)
        pp = ss._enforce_types(pp)
        psi_m = ss.prepare_motional(pp)
        psi0_list.append(ss.tensor_spin_motion(0.0, 0.0, psi_m, NMAX))

    T_gap = T_M - DELTA_T
    sx = np.zeros((len(phi_deg_grid), len(det_rel_grid)))
    sy = np.zeros_like(sx); sz = np.zeros_like(sx)

    for i, d_rel in enumerate(det_rel_grid):
        delta = d_rel * OMEGA_M
        H_pulse = ss.build_hamiltonian(
            ETA, OMEGA_R, delta, NMAX, C, Cdag,
            ac_phase_rad=0.0, omega_m=OMEGA_M,
            intra_pulse_motion=True,
        )
        U_pulse = _scipy_expm(-1j * H_pulse * DELTA_T)

        ph_d = np.exp(+1j * delta / 2 * T_gap)
        ph_u = np.exp(-1j * delta / 2 * T_gap)
        U_gap = np.zeros((dim, dim), dtype=complex)
        for n in range(NMAX):
            ph_mot = np.exp(-1j * OMEGA_M * n * T_gap)
            U_gap[n, n] = ph_mot * ph_d
            U_gap[NMAX + n, NMAX + n] = ph_mot * ph_u

        for j, psi0 in enumerate(psi0_list):
            psi = psi0.copy()
            for k in range(N_PULSES):
                psi = U_pulse @ psi
                if k < N_PULSES - 1:
                    psi = U_gap @ psi
            obs = ss.compute_observables(psi, NMAX)
            sx[j, i] = obs['sigma_x']
            sy[j, i] = obs['sigma_y']
            sz[j, i] = obs['sigma_z']
    return sx, sy, sz


def _new_run(det_rel_grid, phi_deg_grid):
    """Same loop, using the new package."""
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    shift_deg = float(np.degrees(OMEGA_M * DELTA_T / 2))

    psi0_list = []
    for phi in phi_deg_grid:
        psi0 = hs.prepare_state(
            spin={"theta_deg": 0.0, "phi_deg": 0.0},
            modes=[{"alpha": ALPHA, "alpha_phase_deg": float(phi) + shift_deg}],
        )
        psi0_list.append(psi0)

    C = ops_new.coupling(ETA, NMAX)
    Cdag = C.conj().T

    sx = np.zeros((len(phi_deg_grid), len(det_rel_grid)))
    sy = np.zeros_like(sx); sz = np.zeros_like(sx)

    for i, d_rel in enumerate(det_rel_grid):
        delta = d_rel * OMEGA_M
        train = build_strobo_train(
            hs=hs, eta=ETA, omega_r=OMEGA_R, omega_m=OMEGA_M,
            delta=delta, n_pulses=N_PULSES, delta_t=DELTA_T,
            t_sep_factor=1.0, ac_phase_rad=0.0,
            intra_pulse_motion=True, gap_includes_spin_detuning=True,
            C=C, Cdag=Cdag,
        )
        for j, psi0 in enumerate(psi0_list):
            psi = train.evolve(psi0)
            obs = hs.observables(psi)
            sx[j, i] = obs["sigma_x"]
            sy[j, i] = obs["sigma_y"]
            sz[j, i] = obs["sigma_z"]
    return sx, sy, sz


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["numpy", "jax"], default="numpy")
    parser.add_argument("--n-det", type=int, default=5)
    parser.add_argument("--n-phi", type=int, default=4)
    parser.add_argument("--atol", type=float, default=1e-12)
    args = parser.parse_args()

    backend.set_backend(args.backend)
    print(f"[validate] backend = {args.backend}")

    det_rel = np.linspace(-1.0, 1.0, args.n_det) * (15.0 / OMEGA_M)
    phi_deg = np.linspace(0.0, 360.0, args.n_phi, endpoint=False)

    t0 = time.time()
    sx_legacy, sy_legacy, sz_legacy = _legacy_run(det_rel, phi_deg)
    t_legacy = time.time() - t0

    t0 = time.time()
    sx_new, sy_new, sz_new = _new_run(det_rel, phi_deg)
    t_new = time.time() - t0

    diffs = {
        "sigma_x": np.max(np.abs(sx_new - sx_legacy)),
        "sigma_y": np.max(np.abs(sy_new - sy_legacy)),
        "sigma_z": np.max(np.abs(sz_new - sz_legacy)),
    }
    print(f"  legacy wall: {t_legacy:.2f}s   new wall: {t_new:.2f}s")
    for k, d in diffs.items():
        status = "OK" if d < args.atol else "FAIL"
        print(f"  max |Δ{k}| = {d:.3e}  [{status}]")

    if all(d < args.atol for d in diffs.values()):
        print("[validate] PASS")
        return 0
    print("[validate] FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
