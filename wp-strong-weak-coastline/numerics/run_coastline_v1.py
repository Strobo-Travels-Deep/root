#!/usr/bin/env python3
"""
run_coastline_v1.py — Strong/weak-binding coastline driver.

WP-C v0.1 main sweep. See ../README.md and the v0.3 council memo for
scope. Per §3 of the WP README:

  N ∈ {3, 6, 12, 24, 48, 96}
  δt/T_m ∈ {0.02, 0.05, 0.10, 0.20, 0.40, 0.80}
  δ/ω_m ∈ {0, 0.25, 0.5}
  |α| ∈ {0, 1, 3} (scientific baseline) + 5 (stretch)
  ϑ₀ : 64 points, phase-shifted by ω_m·δt/2
  Ω calibrated per-cell via N·Ω_eff·δt = π/2 (option (a) primary)

On-disk schema of coastline_v1.h5 (what this driver actually writes):

  /                                — root, coordinate datasets + global attrs
    N_list, dt_frac_list, det_rel_list, theta0_grid, alpha_list
    attrs: eta, omega_m, omega_eff_ceiling, motional_ld_threshold,
           debye_waller, calibration_mode, ac_phase_deg, mw_phase_deg,
           code_version, datetime_utc, wp

  /alpha_{X}pY/                    — one group per |α| value
    V, P, diamond_amp_sigma_z, dn_peak           (all (nN, ndt) datasets)
    omega_eff_over_omega_m                        — drive-LD diagnostic
    ld_flag_drive                                 — bool (nN, ndt)
    ld_motional_param, ld_flag_motional           — motional-LD diagnostic
    fock_leakage_top5, nmax_used                  — Fock-cutoff diagnostics
    attrs: alpha, nmax, elapsed_seconds

  /alpha_{X}pY/control_fixed_omega_hasse/        — nested option-(b) slice
    V, P, diamond_amp_sigma_z, dn_peak, net_rotation_pi2,
    ld_motional_param       (all (nN,) datasets)
    attrs: alpha, dt_frac=0.13, omega_r, omega_eff

Validity diagnostics live as (nN, ndt) datasets (not scalar attributes)
because they vary per (N, δt/T_m) cell. Downstream rendering consumes
ld_flag_drive and ld_flag_motional for hatching overlays; observables
themselves remain raw engine output.

Observables (per (N, δt, |α|, δ) cell, reduced over ϑ₀):
  V                  = 1 − min_ϑ |C|     (at δ=0)
  P                  = ⟨|C|⟩_ϑ           (at δ=0.5·ω_m)
  diamond_amp_sigma_z= ½(max−min)⟨σ_z⟩   (at δ=0)
  dn_peak            = max_ϑ |⟨n⟩ − |α|²|(at δ=0)
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

# ── Physics anchors ────────────────────────────────────────────────────
ETA = 0.397
OMEGA_M = 1.3
T_M = 2 * np.pi / OMEGA_M
DEBYE_WALLER = np.exp(-ETA ** 2 / 2)

# ── Grid specification ────────────────────────────────────────────────
N_LIST = np.array([3, 6, 12, 24, 48, 96], dtype=np.int64)
DT_FRAC_LIST = np.array([0.02, 0.05, 0.10, 0.20, 0.40, 0.80])
DET_REL_LIST = np.array([0.0, 0.25, 0.5])
ALPHA_SCIENTIFIC = [0.0, 1.0, 3.0]
ALPHA_STRETCH = [5.0]                # run contingent on time budget
N_THETA0 = 64
MW_PHASE_DEG = 0.0
AC_PHASE_DEG = 0.0

# ── Validity diagnostics ──────────────────────────────────────────────
OMEGA_EFF_CEILING = 0.3                # drive-LD ceiling (§3.1)
MOTIONAL_LD_THRESHOLD = 1.0            # η·√(⟨n⟩+1) > 1 → flag (§2.3)

# ── Fock-basis policy (from pre-audit) ────────────────────────────────
# |α| ≤ 3 : NMAX 60 is safe.
# |α| = 5 : NMAX 60 marginal (leak5 ≈ 4e-6 at δt/Tm=0.02); NMAX 80 → 3e-13.
def nmax_for_alpha(alpha: float) -> int:
    return 80 if alpha >= 4.5 else 60


def omega_calibrated(N: int, dt: float) -> float:
    """Option (a): Ω such that N·Ω_eff·δt = π/2."""
    return (np.pi / (2 * N * dt)) / DEBYE_WALLER


def omega_hasse_baseline() -> float:
    """Option (b) control slice: fixed Ω = Ω_Hasse from WP-V (α=3 anchor)."""
    dt_hasse = 0.13 * T_M
    return (np.pi / (2 * 30 * dt_hasse)) / DEBYE_WALLER


def evolve_grid(alpha: float, N_p: int, dt: float, omega_r: float,
                det_rel_list, theta0_grid, hs, C, Cdag):
    """Run the (ϑ₀ × δ) grid at fixed (α, N, δt, Ω). Return raw maps."""
    nmax = hs.nmax
    ac_phase_rad = float(np.radians(AC_PHASE_DEG))
    T_gap = T_M - dt
    shift_deg = float(np.degrees(OMEGA_M * dt / 2))

    psi_starts = []
    for th0 in theta0_grid:
        psi0 = hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': alpha,
                    'alpha_phase_deg': float(np.degrees(th0)) + shift_deg}],
        )
        psi_starts.append(hs.apply_mw_pi2(psi0, MW_PHASE_DEG))

    n_det = len(det_rel_list)
    n_th = len(theta0_grid)
    coh = np.zeros((n_det, n_th))
    sz = np.zeros_like(coh)
    nbar = np.zeros_like(coh)
    leak5_worst = 0.0

    for j, d_rel in enumerate(det_rel_list):
        delta = float(d_rel) * OMEGA_M
        H_pulse = ham.build_pulse_hamiltonian(
            ETA, omega_r, delta, nmax, C, Cdag,
            ac_phase_rad=ac_phase_rad, omega_m=OMEGA_M,
            intra_pulse_motion=True,
        )
        U_pulse = prop.build_U_pulse(H_pulse, dt)
        U_gap_diag = prop.build_U_gap(
            nmax, OMEGA_M, T_gap, delta=delta,
            include_motion=True, include_spin_detuning=True,
        )
        train = StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag,
                            n_pulses=N_p)
        for i, psi in enumerate(psi_starts):
            psi_final = train.evolve(psi)
            obs = hs.observables(psi_final)
            coh[j, i] = np.sqrt(obs['sigma_x'] ** 2 + obs['sigma_y'] ** 2)
            sz[j, i] = obs['sigma_z']
            nbar[j, i] = obs['nbar']
            lk5 = hs.fock_leakage(psi_final, top_k=5)
            if lk5 > leak5_worst: leak5_worst = lk5
    return coh, sz, nbar, leak5_worst


def reduce_cell(coh, sz, nbar, alpha: float, det_rel_list: np.ndarray):
    """Reduce (δ, ϑ₀) maps to scalar cell observables."""
    # Find δ=0 row and δ=0.5·ω_m row.
    j0 = int(np.argmin(np.abs(det_rel_list - 0.0)))
    jhalf = int(np.argmin(np.abs(det_rel_list - 0.5)))
    V = 1.0 - float(np.min(coh[j0]))
    P = float(np.mean(coh[jhalf]))
    diamond = 0.5 * float(sz[j0].max() - sz[j0].min())
    dn = nbar[j0] - alpha ** 2
    dn_peak = float(np.max(np.abs(dn)))
    return V, P, diamond, dn_peak


def sweep_alpha(alpha: float, N_list, dt_frac_list, det_rel_list,
                theta0_grid, verbose=True):
    """Sweep the full (N, δt/T_m) grid at fixed α. Returns dict of arrays."""
    nmax = nmax_for_alpha(alpha)
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(nmax,))
    C = ops.coupling(ETA, nmax); Cdag = C.conj().T

    nN, ndt = len(N_list), len(dt_frac_list)
    V = np.zeros((nN, ndt))
    P = np.zeros_like(V)
    diamond = np.zeros_like(V)
    dn_peak = np.zeros_like(V)
    omega_eff = np.zeros_like(V)
    ld_drive_flag = np.zeros_like(V, dtype=bool)
    ld_motional_param = np.zeros_like(V)
    ld_motional_flag = np.zeros_like(V, dtype=bool)
    leak5 = np.zeros_like(V)

    eta_sqrt_alpha = ETA * np.sqrt(alpha ** 2 + 1.0)

    for a, N_p in enumerate(N_list):
        for b, dt_frac in enumerate(dt_frac_list):
            dt = float(dt_frac) * T_M
            omega_r = omega_calibrated(int(N_p), dt)
            om_eff = omega_r * DEBYE_WALLER
            ld_d = om_eff / OMEGA_M
            coh, sz, nb, lk5 = evolve_grid(
                alpha, int(N_p), dt, omega_r, det_rel_list,
                theta0_grid, hs, C, Cdag)
            V[a, b], P[a, b], diamond[a, b], dn_peak[a, b] = \
                reduce_cell(coh, sz, nb, alpha, det_rel_list)
            omega_eff[a, b] = ld_d
            ld_drive_flag[a, b] = ld_d > OMEGA_EFF_CEILING
            ld_motional_param[a, b] = eta_sqrt_alpha
            ld_motional_flag[a, b] = eta_sqrt_alpha > MOTIONAL_LD_THRESHOLD
            leak5[a, b] = lk5
        if verbose:
            flags = int(np.sum(ld_drive_flag[a]))
            print(f"    |α|={alpha:>3}  N={int(N_p):>3}  "
                  f"drive-LD breaches in row: {flags}/{ndt}  "
                  f"V̄={V[a].mean():.3f}  P̄={P[a].mean():.3f}")

    return dict(V=V, P=P, diamond_amp_sigma_z=diamond, dn_peak=dn_peak,
                omega_eff_over_omega_m=omega_eff,
                ld_flag_drive=ld_drive_flag,
                ld_motional_param=ld_motional_param,
                ld_flag_motional=ld_motional_flag,
                fock_leakage_top5=leak5,
                nmax_used=np.full_like(V, nmax, dtype=np.int64))


def sweep_control(alpha: float, N_list, det_rel_list, theta0_grid,
                  verbose=True):
    """Option (b) control slice at δt/T_m = 0.13 with fixed Ω = Ω_Hasse."""
    nmax = nmax_for_alpha(alpha)
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(nmax,))
    C = ops.coupling(ETA, nmax); Cdag = C.conj().T
    dt_frac = 0.13
    dt = dt_frac * T_M
    omega_r = omega_hasse_baseline()
    om_eff = omega_r * DEBYE_WALLER

    nN = len(N_list)
    V = np.zeros(nN); P = np.zeros_like(V)
    diamond = np.zeros_like(V); dn_peak = np.zeros_like(V)
    net_rot = np.zeros_like(V)

    eta_sqrt_alpha = ETA * np.sqrt(alpha ** 2 + 1.0)

    for a, N_p in enumerate(N_list):
        coh, sz, nb, _ = evolve_grid(
            alpha, int(N_p), dt, omega_r, det_rel_list,
            theta0_grid, hs, C, Cdag)
        V[a], P[a], diamond[a], dn_peak[a] = \
            reduce_cell(coh, sz, nb, alpha, det_rel_list)
        # Net carrier rotation over the train, in π/2 units.
        net_rot[a] = (int(N_p) * om_eff * dt) / (np.pi / 2)

    if verbose:
        print(f"    [control] |α|={alpha:>3}  δt/Tm=0.13  Ω fixed.")
        for a, N_p in enumerate(N_list):
            print(f"       N={int(N_p):>3}  N·Ω_eff·δt/(π/2)={net_rot[a]:5.2f}  "
                  f"V={V[a]:.3f}  P={P[a]:.3f}")
    return dict(V=V, P=P, diamond_amp_sigma_z=diamond, dn_peak=dn_peak,
                net_rotation_pi2=net_rot,
                omega_r=omega_r, omega_eff=om_eff,
                ld_motional_param=np.full_like(V, eta_sqrt_alpha))


def main():
    t_start = time.time()
    print(f"WP-Coastline v0.1 driver  —  engine v{CODE_VERSION}")
    print(f"  η={ETA}  ω_m={OMEGA_M:.3f} rad/(engine time unit, angular); "
          f"Hasse anchor ω_m/(2π)=1.3 MHz recovered at engine unit = 2π μs\n"
          f"  grid: {len(N_LIST)}×{len(DT_FRAC_LIST)}×{len(DET_REL_LIST)} "
          f"× |α|∈{ALPHA_SCIENTIFIC}+{ALPHA_STRETCH}\n")

    theta0_grid = np.linspace(0.0, 2 * np.pi, N_THETA0, endpoint=False)

    out_h5 = os.path.join(SCRIPT_DIR, 'coastline_v1.h5')
    alphas_all = list(ALPHA_SCIENTIFIC) + list(ALPHA_STRETCH)

    with h5py.File(out_h5, 'w') as f:
        # Grid coordinates at root.
        f.create_dataset('N_list', data=N_LIST)
        f.create_dataset('dt_frac_list', data=DT_FRAC_LIST)
        f.create_dataset('det_rel_list', data=DET_REL_LIST)
        f.create_dataset('theta0_grid', data=theta0_grid)
        f.create_dataset('alpha_list', data=np.array(alphas_all))

        # Global attributes.
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['omega_eff_ceiling'] = OMEGA_EFF_CEILING
        f.attrs['motional_ld_threshold'] = MOTIONAL_LD_THRESHOLD
        f.attrs['debye_waller'] = DEBYE_WALLER
        f.attrs['calibration_mode'] = 'option_a_recalibrated_omega'
        f.attrs['ac_phase_deg'] = AC_PHASE_DEG
        f.attrs['mw_phase_deg'] = MW_PHASE_DEG
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['wp'] = 'wp-strong-weak-coastline'

        for alpha in alphas_all:
            tag = f"alpha_{alpha:.1f}".replace('.', 'p')
            print(f"  sweeping α = {alpha} …")
            t0 = time.time()
            result = sweep_alpha(alpha, N_LIST, DT_FRAC_LIST, DET_REL_LIST,
                                 theta0_grid, verbose=True)
            dt_alpha = time.time() - t0
            print(f"    α={alpha} done in {dt_alpha:.1f} s\n")

            g = f.create_group(tag)
            for k, v in result.items():
                g.create_dataset(k, data=np.asarray(v))
            g.attrs['alpha'] = alpha
            g.attrs['nmax'] = int(result['nmax_used'].flat[0])
            g.attrs['elapsed_seconds'] = dt_alpha

            # Control slice at δt/Tm = 0.13 (option b).
            t0 = time.time()
            ctl = sweep_control(alpha, N_LIST, DET_REL_LIST,
                                theta0_grid, verbose=True)
            dt_ctl = time.time() - t0
            print(f"    α={alpha} control-slice in {dt_ctl:.1f} s\n")
            gc = f.create_group(f"{tag}/control_fixed_omega_hasse")
            for k, v in ctl.items():
                gc.create_dataset(k, data=np.asarray(v)) \
                    if hasattr(v, '__len__') else gc.attrs.__setitem__(k, v)
            gc.attrs['alpha'] = alpha
            gc.attrs['dt_frac'] = 0.13

    elapsed = time.time() - t_start
    print(f"  TOTAL elapsed: {elapsed:.1f} s")
    print(f"  wrote {out_h5}")


if __name__ == '__main__':
    main()
