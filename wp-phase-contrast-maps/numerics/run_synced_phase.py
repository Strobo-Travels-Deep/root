#!/usr/bin/env python3
"""
run_synced_phase.py — Driver-level "synced-phase" propagator.

Closes Flag 1 (engine-vs-experiment frame convention). Under the
assumption that the laser/AC phase reference is maintained across the
full pulse train (user statement 2026-04-14), the spin picks up
exp(−i·δ·σ_z·T_m/2) per inter-pulse gap in the AC rotating frame.

The engine (v0.9.1) omits this inter-pulse free evolution at
t_sep_factor = 1.0. This driver calls the engine's finite-δt pulse
propagator and inserts the missing spin free evolution explicitly
between pulses — keeping the v0.9.1 D1 (intra-pulse motion) and
pulse-centering toggles active.

Output:
  numerics/synced_phase_alpha0and3.h5
  (Includes synced-full, v0.9.1 engine (wrong), and R2 Monroe impulsive
   on the same fine grid.)
"""

import os, sys, time, numpy as np, h5py
sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts')))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stroboscopic_sweep as ss
from scipy.linalg import expm
from run_slices import NOMINAL, run_R2_single

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

OMEGA_M = 1.3
T_M = 2 * np.pi / OMEGA_M                   # μs
DELTA_T_FRAC = 0.13
DELTA_T = DELTA_T_FRAC * T_M                # μs
N_PULSES = 30
ETA = 0.397
NMAX = 60
ALPHAS = [0.0, 3.0]

# Pulse area so N·Ω_eff·δt = π/2
OMEGA_EFF = np.pi / (2 * N_PULSES * DELTA_T)
OMEGA_R = OMEGA_EFF / np.exp(-ETA**2 / 2)


def run_synced_phase_single(alpha, det_rel_grid, eta=ETA,
                            n_pulses=N_PULSES, delta_t=DELTA_T,
                            omega_m=OMEGA_M, omega_r=OMEGA_R,
                            intra_pulse_motion=True,
                            center_pulses_at_phase=True,
                            nmax=NMAX):
    """One detuning scan under the synced-phase convention.

    Pulse k: evolve for δt under H_v0.9 = (δ/2)σ_z + (Ω/2)(Cσ₋+h.c.)
                                         + ω_m·a†a  (if intra toggle).
    Gap k→k+1: evolve spin freely under exp(-i(δ/2)σ_z · (T_m − δt)).
               Motion is identity in the strobe frame (integer cycles).
    """
    dim = 2 * nmax
    _, _, X = ss.build_operators(nmax)
    C = ss.build_coupling(eta, nmax, X)
    Cdag = C.conj().T

    # Apply centering: shift prepared motional phase by +ω_m·δt/2 so
    # pulse 1 is centered on alpha_phase_deg (v0.9.1 convention).
    alpha_phase_rad = 0.0
    if center_pulses_at_phase:
        alpha_phase_rad = omega_m * delta_t / 2
    p_prep = dict(ss.DEFAULTS)
    p_prep.update(alpha=float(alpha),
                  alpha_phase_deg=float(np.degrees(alpha_phase_rad)),
                  eta=float(eta), nmax=nmax)
    p_prep = ss._enforce_types(p_prep)
    psi_m = ss.prepare_motional(p_prep)
    psi0 = ss.tensor_spin_motion(0.0, 0.0, psi_m, nmax)

    T_gap = T_M - delta_t          # inter-pulse dark time (spin-only)
    n_det = len(det_rel_grid)
    sx = np.zeros(n_det); sy = np.zeros(n_det); sz = np.zeros(n_det)

    for i, d_rel in enumerate(det_rel_grid):
        delta = d_rel * omega_m
        H_pulse = ss.build_hamiltonian(
            eta, omega_r, delta, nmax, C, Cdag,
            ac_phase_rad=0.0, omega_m=omega_m,
            intra_pulse_motion=intra_pulse_motion,
        )
        U_pulse = expm(-1j * H_pulse * delta_t)

        # Inter-pulse free evolution: full H_0·T_gap with H_0 = ω_m·a†a + (δ/2)σ_z
        # Spin: exp(-iδ·σ_z·T_gap/2) → ph_down (|↓⟩) and ph_up (|↑⟩).
        # Motion: exp(-iω_m·n·T_gap) per Fock level n, applied to both spin blocks.
        # Combined with intra_pulse_motion=True during pulses, per full cycle
        # the motional phase advances by ω_m·T_m = 2π → strobe closes.
        ph_down_spin = np.exp(+1j * delta / 2 * T_gap) if intra_pulse_motion else np.exp(+1j * delta / 2 * T_gap)
        ph_up_spin   = np.exp(-1j * delta / 2 * T_gap) if intra_pulse_motion else np.exp(-1j * delta / 2 * T_gap)
        U_gap = np.zeros((dim, dim), dtype=complex)
        for n in range(nmax):
            ph_mot = np.exp(-1j * omega_m * n * T_gap) if intra_pulse_motion else 1.0
            U_gap[n, n]             = ph_mot * ph_down_spin
            U_gap[nmax + n, nmax + n] = ph_mot * ph_up_spin

        psi = psi0.copy()
        for k in range(n_pulses):
            psi = U_pulse @ psi
            if k < n_pulses - 1:
                psi = U_gap @ psi
        obs = ss.compute_observables(psi, nmax)
        sx[i] = obs['sigma_x']; sy[i] = obs['sigma_y']; sz[i] = obs['sigma_z']
    return sx, sy, sz


def run_v09_current_engine(alpha, det_rel_grid):
    """Reference: v0.9.1 engine as-is (no inter-pulse spin evolution)."""
    p = dict(ss.DEFAULTS)
    p.update(
        alpha=alpha, alpha_phase_deg=0.0, eta=ETA,
        omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES, n_thermal=0.0, nmax=NMAX,
        det_min=float(det_rel_grid[0]), det_max=float(det_rel_grid[-1]),
        npts=len(det_rel_grid),
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0,
        T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_thermal_traj=1, n_rep=0,
        intra_pulse_motion=True,
        delta_t_us=DELTA_T,
        center_pulses_at_phase=True,
    )
    d, _ = ss.run_single(p, verbose=False)
    return (np.array(d['sigma_x']),
            np.array(d['sigma_y']),
            np.array(d['sigma_z']))


def main():
    # Fine grid ±500 kHz (to resolve the comb tooth)
    det_rel_max = 0.5 / OMEGA_M
    n_det = 201
    det_rel = np.linspace(-det_rel_max, +det_rel_max, n_det)

    results = {}
    for a in ALPHAS:
        print(f'\n=== |α| = {a} ===')
        t0 = time.time()
        sx_s, sy_s, sz_s = run_synced_phase_single(a, det_rel)
        t1 = time.time()
        sx_e, sy_e, sz_e = run_v09_current_engine(a, det_rel)
        t2 = time.time()
        r2 = run_R2_single(a, 0.0, ETA, det_rel,
                           n_pulses=N_PULSES, nmax=NMAX,
                           omega_m=OMEGA_M, omega_r=OMEGA_R)
        t3 = time.time()
        print(f'  synced-phase: {t1-t0:.1f}s')
        print(f'  v0.9.1 current engine: {t2-t1:.1f}s')
        print(f'  R2 Monroe impulsive: {t3-t2:.1f}s')
        results[a] = {
            'synced':  dict(sx=sx_s, sy=sy_s, sz=sz_s),
            'engine':  dict(sx=sx_e, sy=sy_e, sz=sz_e),
            'R2':      dict(sx=r2['sigma_x'], sy=r2['sigma_y'], sz=r2['sigma_z']),
        }
        # Summary at carrier
        i0 = int(np.argmin(np.abs(det_rel)))
        for k, d in results[a].items():
            C = np.sqrt(d['sx']**2 + d['sy']**2)
            print(f'    {k:8s}:  |C|(δ=0) = {C[i0]:.5f}   max|C| on grid = {C.max():.5f}')

    # Save
    out = os.path.join(SCRIPT_DIR, 'synced_phase_alpha0and3.h5')
    with h5py.File(out, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi', data=det_rel * OMEGA_M)
        f.attrs['alpha_values'] = ALPHAS
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['omega_r'] = OMEGA_R
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['T_gap_us'] = T_M - DELTA_T
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['purpose'] = ('Flag 1 closure: synced-phase convention '
                              'vs v0.9.1 current engine (no inter-pulse δ) '
                              'vs R2 Monroe impulsive.')
        for a in ALPHAS:
            g = f.create_group(f'alpha_{a:g}')
            for k, d in results[a].items():
                gg = g.create_group(k)
                for kk, vv in d.items():
                    gg.create_dataset(kk, data=vv)
    print(f'\nWrote {out}')


if __name__ == '__main__':
    main()
