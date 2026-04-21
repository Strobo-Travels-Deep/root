#!/usr/bin/env python3
"""
check_fock_leakage_extremes_v1.py — Pre-audit of NMAX at |α| × δt/T_m
extremes of the coastline grid.

Per §2.3 of the council memo and §2.2 of the WP README: before the full
6×6×3×Nα sweep, confirm NMAX=60 is safe at the corners where motional
spread is worst. Strategy mirrors check_fock_leakage_rabi5x_v5.py: run
at two NMAX values (60, 80), report top-5 Fock leakage, and declare a
verdict. Corners audited:

    |α| = 3      × δt/T_m ∈ {0.02, 0.80}   (drive-LD extremes at α-max)
    |α| = 5      × δt/T_m ∈ {0.02, 0.80}   (motional-LD extremes)
    |α| = 1      × δt/T_m = 0.80           (weak-binding mid point)

At each corner we sweep N ∈ {3, 96} (extremes) and δ ∈ {0, 0.5·ω_m},
taking the worst-case leakage over the ϑ₀ grid.

Writes numerics/fock_leakage_extremes_v1.h5.
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone

import h5py
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts')))

from stroboscopic import HilbertSpace, StroboTrain
from stroboscopic import operators as ops
from stroboscopic import hamiltonian as ham
from stroboscopic import propagators as prop
from stroboscopic.defaults import CODE_VERSION

ETA = 0.397
OMEGA_M = 1.3
T_M = 2 * np.pi / OMEGA_M
DEBYE_WALLER = np.exp(-ETA ** 2 / 2)

N_THETA0 = 16  # coarse — this is a pre-audit, not the full grid
MW_PHASE_DEG = 0.0
AC_PHASE_DEG = 0.0
OMEGA_EFF_CEILING = 0.3

# Corner set: (alpha, dt_frac, N) — extremes of interest
CORNERS = [
    (3.0, 0.02, 3),   (3.0, 0.02, 96),
    (3.0, 0.80, 3),   (3.0, 0.80, 96),
    (5.0, 0.02, 3),   (5.0, 0.02, 96),
    (5.0, 0.80, 3),   (5.0, 0.80, 96),
    (1.0, 0.80, 96),  (1.0, 0.02, 96),
]


def omega_calibrated(N, dt):
    """Option (a): Ω such that N·Ω_eff·δt = π/2."""
    return (np.pi / (2 * N * dt)) / DEBYE_WALLER


def run_corner(alpha, dt_frac, N_p, nmax):
    dt = dt_frac * T_M
    omega_r = omega_calibrated(N_p, dt)
    omega_eff = omega_r * DEBYE_WALLER
    ld_drive = omega_eff / OMEGA_M
    breach = ld_drive > OMEGA_EFF_CEILING

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(nmax,))
    C = ops.coupling(ETA, nmax); Cdag = C.conj().T
    shift_deg = float(np.degrees(OMEGA_M * dt / 2))
    theta0_grid = np.linspace(0.0, 2 * np.pi, N_THETA0, endpoint=False)

    ac_phase_rad = float(np.radians(AC_PHASE_DEG))
    T_gap = T_M - dt
    leak5_worst = 0.0
    nbar_worst = 0.0

    for d_rel in (0.0, 0.5):
        delta = d_rel * OMEGA_M
        H_pulse = ham.build_pulse_hamiltonian(
            ETA, omega_r, delta, nmax, C, Cdag,
            ac_phase_rad=ac_phase_rad,
            omega_m=OMEGA_M, intra_pulse_motion=True,
        )
        U_pulse = prop.build_U_pulse(H_pulse, dt)
        U_gap_diag = prop.build_U_gap(
            nmax, OMEGA_M, T_gap, delta=delta,
            include_motion=True, include_spin_detuning=True,
        )
        train = StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag,
                            n_pulses=N_p)
        for th0 in theta0_grid:
            psi0 = hs.prepare_state(
                spin={'theta_deg': 0.0, 'phi_deg': 0.0},
                modes=[{'alpha': alpha,
                        'alpha_phase_deg': float(np.degrees(th0)) + shift_deg}],
            )
            psi = hs.apply_mw_pi2(psi0, MW_PHASE_DEG)
            psi = train.evolve(psi)
            leak5 = hs.fock_leakage(psi, top_k=5)
            nbar = hs.observables(psi)['nbar']
            if leak5 > leak5_worst: leak5_worst = leak5
            if nbar > nbar_worst: nbar_worst = nbar
    return dict(leak5=leak5_worst, nbar=nbar_worst,
                omega_eff_over_om=ld_drive, drive_ld_breach=breach)


def main():
    print(f"Fock-leakage pre-audit (coastline v0.1)  —  engine v{CODE_VERSION}")
    print(f"  corners: {len(CORNERS)}   NMAX ∈ (60, 80)\n")
    t0 = time.time()

    rows = []
    for (alpha, dt_frac, N_p) in CORNERS:
        r60 = run_corner(alpha, dt_frac, N_p, nmax=60)
        r80 = run_corner(alpha, dt_frac, N_p, nmax=80)
        rows.append(dict(alpha=alpha, dt_frac=dt_frac, N=N_p,
                         leak5_60=r60['leak5'], leak5_80=r80['leak5'],
                         nbar_max=max(r60['nbar'], r80['nbar']),
                         omega_eff_over_om=r60['omega_eff_over_om'],
                         drive_breach=r60['drive_ld_breach']))
        tag = 'BREACH' if r60['drive_ld_breach'] else '  ok  '
        print(f"  |α|={alpha:>3}  δt/Tm={dt_frac:.2f}  N={N_p:>3}  "
              f"Ω_eff/ωm={r60['omega_eff_over_om']:6.3f} [{tag}]  "
              f"leak5(60)={r60['leak5']:.2e}  leak5(80)={r80['leak5']:.2e}  "
              f"⟨n⟩_max={max(r60['nbar'], r80['nbar']):6.2f}")

    elapsed = time.time() - t0
    print(f"\n  pre-audit complete in {elapsed:.1f} s")

    out_h5 = os.path.join(SCRIPT_DIR, 'fock_leakage_extremes_v1.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('alpha',         data=np.array([r['alpha'] for r in rows]))
        f.create_dataset('dt_frac',       data=np.array([r['dt_frac'] for r in rows]))
        f.create_dataset('N',             data=np.array([r['N'] for r in rows]))
        f.create_dataset('leak5_nmax60',  data=np.array([r['leak5_60'] for r in rows]))
        f.create_dataset('leak5_nmax80',  data=np.array([r['leak5_80'] for r in rows]))
        f.create_dataset('nbar_max',      data=np.array([r['nbar_max'] for r in rows]))
        f.create_dataset('omega_eff_over_omega_m',
                         data=np.array([r['omega_eff_over_om'] for r in rows]))
        f.create_dataset('drive_ld_breach',
                         data=np.array([r['drive_breach'] for r in rows]))
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['n_theta0'] = N_THETA0
        f.attrs['omega_eff_ceiling'] = OMEGA_EFF_CEILING
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('Pre-audit of NMAX at coastline corners per WP-C §2.3.')
    print(f"  wrote {out_h5}")

    worst60 = max(r['leak5_60'] for r in rows)
    worst80 = max(r['leak5_80'] for r in rows)
    print(f"\n  worst top-5 leakage @ NMAX=60 : {worst60:.3e}")
    print(f"  worst top-5 leakage @ NMAX=80 : {worst80:.3e}")
    if worst60 < 1e-8:
        print("  VERDICT  NMAX=60 is safe across all corners (< 1e-8).")
    elif worst60 < 1e-4:
        print("  VERDICT  NMAX=60 is marginal; consider NMAX=80 for Doppler-dominated cells.")
    else:
        print("  VERDICT  NMAX=60 is INSUFFICIENT at at least one corner. Increase NMAX.")


if __name__ == '__main__':
    main()
