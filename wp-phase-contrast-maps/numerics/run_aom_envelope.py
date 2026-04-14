#!/usr/bin/env python3
"""
run_aom_envelope.py — Finite-edge AOM envelope on the synced-phase
propagator.

Extends run_synced_phase.py by replacing the rectangular pulse with
an erf-shaped envelope (Gaussian edges):

    f(t) = 0.25 · [1 + erf((t − t_L)/(σ√2))] · [1 + erf((t_R − t)/(σ√2))]

with t_L = 3σ, t_R = δt_total − 3σ. σ is the Gaussian kernel std-dev
(~= τ_rise / 2.56 for 10%–90% convention).

The pulse is discretised into M sub-slices; each sub-propagator is
expm(−i · H_sub(t_k) · Δt) with

    H_sub(t_k) = ω_m·a†a·I + (δ/2)·σ_z + f(t_k)·(Ω/2)·(Cσ₋ + C†σ₊).

Motion and detuning act throughout; coupling scales with f(t). Between
pulses, the inter-pulse U_gap from run_synced_phase.py is applied
(full T_m − δt_total duration).

Two Ω calibrations compared:
  • "area-preserved": Ω rescaled so ∫f(t)dt = δt_total (matches
    rectangular pulse area, so final |C|(δ=0, α=0) reproduces the
    nominal π/2 rotation).
  • "amplitude-kept":  Ω unchanged from rectangular; pulse area reduced
    by the edge-loss factor.

Output:
  numerics/aom_envelope_alpha0and3.h5
"""

import os, sys, time, numpy as np, h5py
from scipy.special import erf
from scipy.linalg import expm

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts')))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stroboscopic_sweep as ss
from run_slices import NOMINAL

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

OMEGA_M = 1.3
T_M = 2 * np.pi / OMEGA_M
DELTA_T_FRAC = 0.13
DELTA_T = DELTA_T_FRAC * T_M                 # μs, full on-to-off window
N_PULSES = 30
ETA = 0.397
NMAX = 60
ALPHAS = [0.0, 3.0]
SIGMA_US = 0.050                             # 50 ns Gaussian σ
M_SUB = 20                                   # sub-slices per pulse

OMEGA_EFF = np.pi / (2 * N_PULSES * DELTA_T)
OMEGA_R_RECT = OMEGA_EFF / np.exp(-ETA**2 / 2)


def aom_envelope(t, delta_t_total, sigma):
    """Smoothly symmetric erf envelope, value in [0, 1]."""
    t_L = 3 * sigma
    t_R = delta_t_total - 3 * sigma
    rise = 0.5 * (1 + erf((t - t_L) / (sigma * np.sqrt(2))))
    fall = 0.5 * (1 + erf((t_R - t) / (sigma * np.sqrt(2))))
    return rise * fall


def envelope_area_factor(delta_t_total, sigma, n=2000):
    """∫f(t)dt / delta_t_total — fraction of rectangular area."""
    t = np.linspace(0, delta_t_total, n)
    return np.trapz(aom_envelope(t, delta_t_total, sigma), t) / delta_t_total


def sub_slice_centers(delta_t_total, M):
    """Midpoint t_k of each of M equal sub-slices over [0, δt_total]."""
    dt_sub = delta_t_total / M
    return (np.arange(M) + 0.5) * dt_sub, dt_sub


def run_aom_single(alpha, det_rel_grid,
                   eta=ETA, n_pulses=N_PULSES, delta_t=DELTA_T,
                   sigma_us=SIGMA_US, M=M_SUB,
                   omega_m=OMEGA_M, area_preserved=True,
                   center_pulses=True, nmax=NMAX):
    """One detuning scan under the finite-edge synced-phase convention."""
    dim = 2 * nmax
    _, _, X = ss.build_operators(nmax)
    C = ss.build_coupling(eta, nmax, X); Cdag = C.conj().T

    # Rescale Ω if we want area preservation.
    af = envelope_area_factor(delta_t, sigma_us)
    if area_preserved:
        omega_r = OMEGA_R_RECT / af            # compensate edge loss
    else:
        omega_r = OMEGA_R_RECT

    # Pulse sub-slice timing and envelope values
    t_k, dt_sub = sub_slice_centers(delta_t, M)
    f_k = aom_envelope(t_k, delta_t, sigma_us)

    # Pulse centering (v0.9.1): shift prepared motional phase by ω_m·δt/2
    alpha_phase_rad = omega_m * delta_t / 2 if center_pulses else 0.0
    p_prep = dict(ss.DEFAULTS)
    p_prep.update(alpha=float(alpha),
                  alpha_phase_deg=float(np.degrees(alpha_phase_rad)),
                  eta=float(eta), nmax=nmax)
    p_prep = ss._enforce_types(p_prep)
    psi_m = ss.prepare_motional(p_prep)
    psi0 = ss.tensor_spin_motion(0.0, 0.0, psi_m, nmax)

    T_gap = T_M - delta_t
    n_det = len(det_rel_grid)
    sx = np.zeros(n_det); sy = np.zeros(n_det); sz = np.zeros(n_det)

    # Precompute the M sub-propagators per detuning (reused across pulses).
    # Each sub-slice has H = H_0 (motion+δ) + f_k · H_coup.
    # Motion+detuning base: build once per detuning, coupling once per f_k.
    for i, d_rel in enumerate(det_rel_grid):
        delta = d_rel * omega_m

        H_base = np.zeros((dim, dim), dtype=complex)
        for n in range(nmax):
            # Motion ω_m·a†a · I
            H_base[n, n] = omega_m * n
            H_base[nmax + n, nmax + n] = omega_m * n
            # Spin detuning ±δ/2
            H_base[n, n] += -delta / 2
            H_base[nmax + n, nmax + n] += delta / 2

        # Build sub-propagators: U_sub[k] = expm(−i · (H_base + f_k · H_coup) · dt_sub)
        U_subs = []
        for k in range(M):
            Hc_coef = f_k[k] * (omega_r / 2)
            H_sub = H_base.copy()
            H_sub[:nmax, nmax:] += Hc_coef * C
            H_sub[nmax:, :nmax] += Hc_coef * Cdag
            U_subs.append(expm(-1j * H_sub * dt_sub))

        # Per-pulse propagator
        U_pulse = U_subs[0]
        for k in range(1, M):
            U_pulse = U_subs[k] @ U_pulse

        # Inter-pulse U_gap (synced-phase): motion + spin detuning
        ph_d = np.exp(+1j * delta / 2 * T_gap)
        ph_u = np.exp(-1j * delta / 2 * T_gap)
        U_gap = np.zeros((dim, dim), dtype=complex)
        for n in range(nmax):
            ph_mot = np.exp(-1j * omega_m * n * T_gap)
            U_gap[n, n]           = ph_mot * ph_d
            U_gap[nmax + n, nmax + n] = ph_mot * ph_u

        # Pulse train
        psi = psi0.copy()
        for p in range(n_pulses):
            psi = U_pulse @ psi
            if p < n_pulses - 1:
                psi = U_gap @ psi
        obs = ss.compute_observables(psi, nmax)
        sx[i] = obs['sigma_x']; sy[i] = obs['sigma_y']; sz[i] = obs['sigma_z']
    return sx, sy, sz


def main():
    # Fine grid ±500 kHz (detuning)
    det_rel_max = 0.5 / OMEGA_M
    n_det = 201
    det_rel = np.linspace(-det_rel_max, +det_rel_max, n_det)

    # Diagnostic print: envelope sanity
    af = envelope_area_factor(DELTA_T, SIGMA_US)
    print(f'AOM envelope: δt_total = {DELTA_T*1e3:.1f} ns  σ = {SIGMA_US*1e3:.1f} ns  '
          f'area fraction = {af:.4f}  flat-top = {DELTA_T - 6*SIGMA_US:.4f} μs '
          f'({(DELTA_T - 6*SIGMA_US)/DELTA_T*100:.1f}% of δt_total)')
    print(f'Ω area-preserved: {OMEGA_R_RECT/af:.5f} MHz vs Ω rect = {OMEGA_R_RECT:.5f} MHz')

    results = {}
    for a in ALPHAS:
        print(f'\n=== |α| = {a}  (M={M_SUB} sub-slices) ===')
        t0 = time.time()
        sx_ap, sy_ap, sz_ap = run_aom_single(a, det_rel, area_preserved=True)
        print(f'  area-preserved:  {time.time()-t0:.1f}s')
        t1 = time.time()
        sx_ak, sy_ak, sz_ak = run_aom_single(a, det_rel, area_preserved=False)
        print(f'  amplitude-kept:  {time.time()-t1:.1f}s')
        results[a] = {
            'area_preserved': dict(sx=sx_ap, sy=sy_ap, sz=sz_ap),
            'amplitude_kept': dict(sx=sx_ak, sy=sy_ak, sz=sz_ak),
        }
        # summaries
        i0 = int(np.argmin(np.abs(det_rel)))
        for k, d in results[a].items():
            C = np.sqrt(d['sx']**2 + d['sy']**2)
            print(f'    {k:16s}: |C|(δ=0)={C[i0]:.5f}  max|C|={C.max():.5f}')

    out = os.path.join(SCRIPT_DIR, 'aom_envelope_alpha0and3.h5')
    with h5py.File(out, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi', data=det_rel * OMEGA_M)
        f.attrs['alpha_values'] = ALPHAS
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['sigma_us'] = SIGMA_US
        f.attrs['M_sub'] = M_SUB
        f.attrs['envelope'] = 'erf (Gaussian σ = 50 ns)'
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['purpose'] = ('AOM erf-envelope + synced-phase; compared to '
                              'rectangular synced-phase (see synced_phase_alpha0and3.h5).')
        for a in ALPHAS:
            g = f.create_group(f'alpha_{a:g}')
            for k, d in results[a].items():
                gg = g.create_group(k)
                for kk, vv in d.items():
                    gg.create_dataset(kk, data=vv)
    print(f'\nWrote {out}')


if __name__ == '__main__':
    main()
