#!/usr/bin/env python3
"""Preflight checks for strobo 2.0 sweep.

Observable contract matches the dataset:
    |C|   = sqrt(sz_A**2 + sz_B**2)
    arg C = atan2(sz_B, sz_A)
with sz_A = <sigma_z> after train from spin |+x>, and
     sz_B = <sigma_z> after train from spin |+y>, both at engine
     ac_phase_deg = 0. See logbook 2026-04-21-kickoff.md sec. 4.

Tests:
1) Cross-check anchor: (delta_0 = 0, theta_0 = 0, alpha = 0). The
   weak-pulse prediction is |C| = sin(N * theta_pulse); also report
   the Bloch vector (sx, sy, sz) from Run A as a diagnostic.

2) Nmax convergence: at the convergence anchor
   (alpha = 4.5, delta_0 = 0, theta_0 = 0) with train T2, check |C|
   and delta<n> vs Nmax in {50, 60, 70, 80}.

3) Full phi_laser scan at (alpha = 3, delta_0 = 0, theta_0 = 0) with
   train T2: fit sz(phi) = a_I + a_x cos + a_y sin; confirm max
   residual at machine precision.

4) Two-run extraction equivalence: at the same cell, confirm that the
   (|+x>, |+y>) two-run protocol matches the 8-point fit and that the
   a_I offset is negligible.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from stroboscopic_sweep import run_single, DEFAULTS  # noqa: E402

OMEGA_M_MHZ = 1.306
OMEGA_R_MHZ = 0.178
ETA = 0.395
DELTA_T_US = 0.77
T_M_US = 1.0 / OMEGA_M_MHZ  # cyclic period
T_SEP_FACTOR = DELTA_T_US / T_M_US


def base_params(n_pulses: int, delta_t_pulse_us: float, nmax: int = 70) -> dict:
    return dict(
        alpha=0.0,
        alpha_phase_deg=0.0,
        eta=ETA,
        omega_m=2 * np.pi * OMEGA_M_MHZ,
        omega_r=2 * np.pi * OMEGA_R_MHZ,
        nmax=nmax,
        theta_deg=90.0,
        phi_deg=0.0,
        det_min=0.0,
        det_max=0.0,
        npts=1,
        n_pulses=n_pulses,
        delta_t_us=delta_t_pulse_us,
        t_sep_factor=T_SEP_FACTOR,
        intra_pulse_motion=True,
        ac_phase_deg=0.0,
        mw_pi2_phase_deg=None,
    )


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def run_two(p: dict) -> tuple[float, float, float, float, dict, dict]:
    """Run Run A (init |+x>) and Run B (init |+y>), return (sz_A, sz_B,
    nbar_A, nbar_B, conv_A, conv_B). Assumes p already has theta_deg=90."""
    pA = dict(p)
    pA["phi_deg"] = 0.0
    dA, cA = run_single(pA, verbose=False)
    pB = dict(p)
    pB["phi_deg"] = 90.0
    dB, cB = run_single(pB, verbose=False)
    return (dA["sigma_z"][0], dB["sigma_z"][0],
            dA["nbar"][0], dB["nbar"][0], cA, cB), dA


def test_1_anchor() -> None:
    print_header("TEST 1  Cross-check anchor (delta=0, theta_0=0, alpha=0)")
    for label, N, dt in [("T1: N=3, dt=100 ns", 3, 0.100), ("T2: N=7, dt= 50 ns", 7, 0.050)]:
        theta_pulse = 2 * np.pi * OMEGA_R_MHZ * dt  # Omega * dt in rad
        coh_pred = np.sin(N * theta_pulse)
        p = base_params(N, dt)
        (sz_A, sz_B, n_A, n_B, conv_A, _), dA = run_two(p)
        coh = np.hypot(sz_A, sz_B)
        print(f"  {label}    N*theta_pulse = {N * theta_pulse:.4f} rad")
        print(f"    Two-run |C| = sqrt(sz_A^2 + sz_B^2) = {coh:.6f}")
        print(f"    Weak-pulse prediction sin(N*theta_pulse) = {coh_pred:.6f}")
        print(f"    |C| - prediction = {coh - coh_pred:+.2e}")
        print(f"    Run A: sz_A = {sz_A:+.6f}   <n>_fin_A = {n_A:.6f}  (delta<n>_A = {n_A:.2e})")
        print(f"    Run B: sz_B = {sz_B:+.6f}   <n>_fin_B = {n_B:.6f}  (delta<n>_B = {n_B:.2e})")
        print(f"    Diagnostic Bloch (Run A): (sx, sy, sz) = ({dA['sigma_x'][0]:+.6f}, "
              f"{dA['sigma_y'][0]:+.6f}, {dA['sigma_z'][0]:+.6f})")
        print(f"    Fock leak (Run A) = {conv_A['max_fock_leakage']:.2e}  converged={conv_A['converged']}")


def test_2_nmax_convergence() -> None:
    print_header("TEST 2  Nmax convergence at convergence anchor "
                 "(alpha=4.5, delta=0, theta_0=0), T2")
    N, dt = 7, 0.050
    results = []
    for nmax in (50, 60, 70, 80):
        p = base_params(N, dt, nmax=nmax)
        p["alpha"] = 4.5
        t0 = time.time()
        (sz_A, sz_B, n_A, n_B, conv_A, _), _ = run_two(p)
        elapsed = time.time() - t0
        coh = np.hypot(sz_A, sz_B)
        dn_A = n_A - 4.5 ** 2
        dn_B = n_B - 4.5 ** 2
        results.append((nmax, coh, dn_A, dn_B, conv_A["max_fock_leakage"], elapsed))
        print(f"  Nmax={nmax:3d}   |C|={coh:.6f}   delta<n>_A={dn_A:+.6f}   "
              f"delta<n>_B={dn_B:+.6f}   leak={conv_A['max_fock_leakage']:.2e}   t={elapsed:.2f}s")
    print("\n  Convergence deltas (relative to Nmax=80 reference):")
    ref_C, ref_dnA, ref_dnB = results[-1][1], results[-1][2], results[-1][3]
    for nmax, coh, dn_A, dn_B, _, _ in results[:-1]:
        print(f"    Nmax={nmax:3d}   d|C|={coh - ref_C:+.2e}   "
              f"d(delta<n>_A)={dn_A - ref_dnA:+.2e}   "
              f"d(delta<n>_B)={dn_B - ref_dnB:+.2e}")


def test_3_phi_scan() -> None:
    print_header("TEST 3  Full phi_laser scan at (alpha=3, delta=0, theta_0=0), T2")
    N, dt = 7, 0.050
    p = base_params(N, dt, nmax=60)
    p["alpha"] = 3.0

    phis = np.arange(0.0, 360.0, 45.0)
    sz_vals = []
    for phi_deg in phis:
        pp = dict(p)
        pp["ac_phase_deg"] = float(phi_deg)
        d, _ = run_single(pp, verbose=False)
        sz_vals.append(d["sigma_z"][0])
    sz_vals = np.array(sz_vals)

    # Fit sz(phi) = a_I + a_x cos(phi) + a_y sin(phi)  via linear least-squares
    phi_rad = np.radians(phis)
    A_mat = np.column_stack([np.ones_like(phi_rad), np.cos(phi_rad), np.sin(phi_rad)])
    coefs, *_ = np.linalg.lstsq(A_mat, sz_vals, rcond=None)
    a_I, a_x, a_y = coefs
    fit = A_mat @ coefs
    max_resid_fit = float(np.max(np.abs(sz_vals - fit)))
    coh = np.hypot(a_x, a_y)
    phi_star = np.degrees(np.arctan2(a_y, a_x))
    print(f"  Full 8-point phi_laser scan, fit to sz(phi) = a_I + a_x cos + a_y sin:")
    print(f"    a_I = {a_I:+.6f}   a_x = {a_x:+.6f}   a_y = {a_y:+.6f}")
    print(f"    |C| = sqrt(a_x^2 + a_y^2) = {coh:.6f}   arg C = {phi_star:+.3f} deg")
    print(f"    Max residual of sinusoidal fit: {max_resid_fit:.2e}")


def test_4_two_run_equivalence() -> None:
    print_header("TEST 4  Two-run extraction vs full phi scan (alpha=3, delta=0, theta_0=0), T2")
    N, dt = 7, 0.050

    # Run A: initial |+x>
    pA = base_params(N, dt, nmax=60)
    pA["alpha"] = 3.0
    pA["theta_deg"] = 90.0
    pA["phi_deg"] = 0.0
    dA, _ = run_single(pA, verbose=False)
    sz_A, n_A = dA["sigma_z"][0], dA["nbar"][0]

    # Run B: initial |+y>
    pB = dict(pA)
    pB["phi_deg"] = 90.0
    dB, _ = run_single(pB, verbose=False)
    sz_B, n_B = dB["sigma_z"][0], dB["nbar"][0]

    # Run C: initial |-x>  (for a_I check)
    pC = dict(pA)
    pC["phi_deg"] = 180.0
    dC, _ = run_single(pC, verbose=False)
    sz_mx = dC["sigma_z"][0]

    a_I_check = 0.5 * (sz_A + sz_mx)
    a_x_2run = sz_A
    a_y_2run = sz_B
    a_x_3run = 0.5 * (sz_A - sz_mx)

    coh_2run = np.hypot(a_x_2run, a_y_2run)
    coh_3run = np.hypot(a_x_3run, a_y_2run)
    arg_2run = np.degrees(np.arctan2(a_y_2run, a_x_2run))
    arg_3run = np.degrees(np.arctan2(a_y_2run, a_x_3run))

    print(f"  Run A (init |+x>):  sz = {sz_A:+.6f}   nbar = {n_A:.6f}")
    print(f"  Run B (init |+y>):  sz = {sz_B:+.6f}   nbar = {n_B:.6f}")
    print(f"  Run C (init |-x>):  sz = {sz_mx:+.6f}")
    print(f"  a_I offset check:   a_I = (sz_A + sz_{{-x}})/2 = {a_I_check:+.6e}")
    print(f"  2-run (assume a_I=0):   |C| = {coh_2run:.6f}   arg C = {arg_2run:+.3f} deg")
    print(f"  3-run (explicit a_I):   |C| = {coh_3run:.6f}   arg C = {arg_3run:+.3f} deg")
    print(f"  Delta |C| (3 - 2):      {coh_3run - coh_2run:+.2e}")
    print(f"  Back-action at phi=0:   delta<n>_A = {n_A - pA['alpha']**2:+.6f}")
    print(f"  Back-action at phi=pi/2: delta<n>_B = {n_B - pA['alpha']**2:+.6f}")


if __name__ == "__main__":
    print("strobo 2.0 preflight")
    print(f"  omega_m/(2pi) = {OMEGA_M_MHZ} MHz   T_m = {T_M_US:.4f} us")
    print(f"  omega_r/(2pi) = {OMEGA_R_MHZ} MHz   eta = {ETA}")
    print(f"  Delta t = {DELTA_T_US} us   t_sep_factor = {T_SEP_FACTOR:.5f}")
    t_total = time.time()
    test_1_anchor()
    test_2_nmax_convergence()
    test_3_phi_scan()
    test_4_two_run_equivalence()
    print(f"\nTotal preflight time: {time.time() - t_total:.1f} s")
