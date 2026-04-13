#!/usr/bin/env python3
"""
run_slices.py — WP-E driver for slice sweeps S1, S2, S3.

Imports `stroboscopic_sweep` as a library (no engine modification per
preflight Q5 decision). Iterates `run_single()` over the outer axis,
applies α-dependent nmax, and writes one HDF5 file per slice containing
both the full simulation and any reference-model evaluations on the same
grid (R1 = small-η, R2 deferred).

Slice conventions (v0.3 §8 Q2):
  S1: (δ₀, |α|) at φ_α = 0
  S2: (δ₀, φ_α) at |α| ∈ {1, 3, 5}      (3 sheets)
  S3: (|α|, φ_α) at δ₀ ∈ {0, ω_m}        (2 sheets)

Detuning convention: det_rel = δ / ω_m, native to stroboscopic_sweep.
Spec: ±6 MHz/(2π) → ±6/ω_m in det_rel units (≈ ±4.615 at ω_m = 1.3 MHz).
121 points → 0.077 in det_rel ≈ 0.10 MHz/(2π) step (within Q4 spec).

Output schema (HDF5):
  /detuning_rel               (n_det,)         det / ω_m
  /detuning_MHz_over_2pi      (n_det,)         absolute MHz/(2π)
  /alpha                      (n_alpha,)       coherent-state amplitude
  /full/sigma_x               (n_alpha, n_det) full simulation, η = 0.397
  /full/sigma_y               (n_alpha, n_det)
  /full/sigma_z               (n_alpha, n_det)
  /full/C_abs                 (n_alpha, n_det) = sqrt(sx² + sy²)
  /full/C_arg_deg             (n_alpha, n_det) = atan2(sy, sx) in deg
  /full/max_fock_leakage      (n_alpha,)       per-α convergence diagnostic
  /R1/...                     same shape, η = R1_eta (small-η reference)
  attrs: code_version, slice, eta_full, R1_eta, datetime, git_commit
"""

import os, sys, time, json, subprocess
from datetime import datetime, timezone
import numpy as np
import h5py

# Engine import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts'))
sys.path.insert(0, ENGINE_DIR)
import stroboscopic_sweep as ss


# ═══════════════════════════════════════════════════════════════
# Parameter defaults (v0.3 §2 nominal)
# ═══════════════════════════════════════════════════════════════

NOMINAL = dict(
    eta=0.397, omega_m=1.3, omega_r=0.3,
    n_thermal=0.0, theta_deg=0.0, phi_deg=0.0,
    n_pulses=22, t_sep_factor=1.0,
    T1=0.0, T2=0.0, heating=0.0,
    n_traj=1, n_thermal_traj=1, n_rep=0,
)

R1_ETA = 0.04   # small-η linear reference (preflight §3 decision)


def nmax_for_alpha(alpha):
    """α-dependent Fock cutoff per preflight §6."""
    a = float(alpha)
    if a <= 1.0: return 30
    if a <= 3.0: return 40
    if a <= 5.0: return 80
    return int(8 * a + 30)   # heuristic for larger; verify via leakage


def run_one_alpha(alpha, det_rel_grid, eta, alpha_phase_deg=0.0,
                  npts_override=None, verbose=False):
    """One detuning scan at fixed |α|, φ_α."""
    p = dict(NOMINAL)
    p.update(dict(
        alpha=float(alpha),
        alpha_phase_deg=float(alpha_phase_deg),
        eta=float(eta),
        nmax=nmax_for_alpha(alpha),
        det_min=float(det_rel_grid[0]),
        det_max=float(det_rel_grid[-1]),
        npts=int(len(det_rel_grid)) if npts_override is None else npts_override,
    ))
    t0 = time.time()
    data, conv = ss.run_single(p, verbose=verbose)
    t1 = time.time()
    return data, conv, t1 - t0


def git_commit_hash():
    try:
        out = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                      cwd=os.path.dirname(SCRIPT_DIR)).decode().strip()
        return out
    except Exception:
        return 'unknown'


# ═══════════════════════════════════════════════════════════════
# S1 — (δ₀, |α|) at φ_α = 0
# ═══════════════════════════════════════════════════════════════

def execute_S1(out_path, alphas=(0.0, 1.0, 3.0, 5.0), n_det=121,
               det_rel_max=6.0/1.3, eta_full=0.397, eta_R1=R1_ETA):
    """
    Run S1 slice: (δ₀, |α|) at φ_α = 0.
    det_rel_max = 6.0/1.3 ≈ 4.615 → ±6 MHz/(2π) per v0.3 spec.
    """
    det_rel = np.linspace(-det_rel_max, +det_rel_max, n_det)
    n_alpha = len(alphas)

    arrays = {}
    for tag in ('full', 'R1'):
        arrays[tag] = {
            'sigma_x': np.zeros((n_alpha, n_det)),
            'sigma_y': np.zeros((n_alpha, n_det)),
            'sigma_z': np.zeros((n_alpha, n_det)),
            'max_fock_leakage': np.zeros(n_alpha),
        }

    timing = {'full': 0.0, 'R1': 0.0}

    for tag, eta in (('full', eta_full), ('R1', eta_R1)):
        print(f'\n=== S1 / {tag}  (η = {eta}) ===')
        for i, a in enumerate(alphas):
            d, conv, dt = run_one_alpha(a, det_rel, eta=eta,
                                        alpha_phase_deg=0.0)
            arrays[tag]['sigma_x'][i] = d['sigma_x']
            arrays[tag]['sigma_y'][i] = d['sigma_y']
            arrays[tag]['sigma_z'][i] = d['sigma_z']
            arrays[tag]['max_fock_leakage'][i] = conv['max_fock_leakage']
            timing[tag] += dt
            print(f'  |α|={a}  nmax={nmax_for_alpha(a)}  '
                  f'time={dt:.2f}s  leak={conv["max_fock_leakage"]:.2e}  '
                  f'converged={conv["converged"]}')

    # Derived
    for tag in ('full', 'R1'):
        sx = arrays[tag]['sigma_x']; sy = arrays[tag]['sigma_y']
        arrays[tag]['C_abs'] = np.sqrt(sx**2 + sy**2)
        arrays[tag]['C_arg_deg'] = np.degrees(np.arctan2(sy, sx))

    # Write HDF5
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with h5py.File(out_path, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi',
                         data=det_rel * NOMINAL['omega_m'])
        f.create_dataset('alpha', data=np.array(alphas))
        for tag in ('full', 'R1'):
            g = f.create_group(tag)
            for k, v in arrays[tag].items():
                g.create_dataset(k, data=v)
        f.attrs['slice'] = 'S1'
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['eta_full'] = eta_full
        f.attrs['eta_R1'] = eta_R1
        f.attrs['phi_alpha_deg'] = 0.0
        f.attrs['n_pulses'] = NOMINAL['n_pulses']
        f.attrs['omega_m'] = NOMINAL['omega_m']
        f.attrs['omega_r'] = NOMINAL['omega_r']
        f.attrs['datetime'] = datetime.now(timezone.utc).isoformat()
        f.attrs['git_commit'] = git_commit_hash()
        f.attrs['driver'] = 'wp-phase-contrast-maps/numerics/run_slices.py'
        f.attrs['timing_full_s'] = timing['full']
        f.attrs['timing_R1_s'] = timing['R1']

    print(f'\nWrote {out_path}')
    print(f'  total wall: full={timing["full"]:.1f}s, R1={timing["R1"]:.1f}s')
    return out_path


# ═══════════════════════════════════════════════════════════════
# S2 — (δ₀, φ_α) at fixed |α|
# ═══════════════════════════════════════════════════════════════

def execute_S2_sheet(out_path, alpha, n_phi=64, n_det=121,
                     det_rel_max=6.0/1.3, eta_full=0.397, eta_R1=R1_ETA):
    """
    Run one S2 sheet: (δ₀, φ_α) at fixed |α|.
    φ_α grid: 0 to 2π exclusive of the endpoint (n_phi points), to avoid
    duplicate sampling at φ_α = 2π ≡ 0.
    """
    det_rel = np.linspace(-det_rel_max, +det_rel_max, n_det)
    phi_deg = np.linspace(0.0, 360.0, n_phi, endpoint=False)
    nm = nmax_for_alpha(alpha)

    arrays = {}
    for tag in ('full', 'R1'):
        arrays[tag] = {
            'sigma_x': np.zeros((n_phi, n_det)),
            'sigma_y': np.zeros((n_phi, n_det)),
            'sigma_z': np.zeros((n_phi, n_det)),
            'max_fock_leakage': np.zeros(n_phi),
        }

    timing = {'full': 0.0, 'R1': 0.0}

    for tag, eta in (('full', eta_full), ('R1', eta_R1)):
        print(f'\n=== S2 / |α|={alpha} / {tag}  (η = {eta}, nmax = {nm}) ===')
        for j, phi in enumerate(phi_deg):
            d, conv, dt = run_one_alpha(alpha, det_rel, eta=eta,
                                        alpha_phase_deg=float(phi))
            arrays[tag]['sigma_x'][j] = d['sigma_x']
            arrays[tag]['sigma_y'][j] = d['sigma_y']
            arrays[tag]['sigma_z'][j] = d['sigma_z']
            arrays[tag]['max_fock_leakage'][j] = conv['max_fock_leakage']
            timing[tag] += dt
        worst_leak = float(arrays[tag]['max_fock_leakage'].max())
        print(f'  total time {timing[tag]:.1f}s  worst leak {worst_leak:.2e}')

    # Derived
    for tag in ('full', 'R1'):
        sx = arrays[tag]['sigma_x']; sy = arrays[tag]['sigma_y']
        arrays[tag]['C_abs'] = np.sqrt(sx**2 + sy**2)
        arrays[tag]['C_arg_deg'] = np.degrees(np.arctan2(sy, sx))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with h5py.File(out_path, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi',
                         data=det_rel * NOMINAL['omega_m'])
        f.create_dataset('phi_alpha_deg', data=phi_deg)
        for tag in ('full', 'R1'):
            g = f.create_group(tag)
            for k, v in arrays[tag].items():
                g.create_dataset(k, data=v)
        f.attrs['slice'] = 'S2'
        f.attrs['alpha'] = float(alpha)
        f.attrs['nmax'] = nm
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['eta_full'] = eta_full
        f.attrs['eta_R1'] = eta_R1
        f.attrs['n_pulses'] = NOMINAL['n_pulses']
        f.attrs['omega_m'] = NOMINAL['omega_m']
        f.attrs['omega_r'] = NOMINAL['omega_r']
        f.attrs['datetime'] = datetime.now(timezone.utc).isoformat()
        f.attrs['git_commit'] = git_commit_hash()
        f.attrs['driver'] = 'wp-phase-contrast-maps/numerics/run_slices.py'
        f.attrs['timing_full_s'] = timing['full']
        f.attrs['timing_R1_s'] = timing['R1']

    print(f'\nWrote {out_path}')
    return out_path


# ═══════════════════════════════════════════════════════════════
# R1 convergence cross-check (Guardian flag 1)
# ═══════════════════════════════════════════════════════════════

def execute_R1_convergence(out_path, alphas=(0.0, 3.0), n_det=41,
                           det_rel_max=6.0/1.3, etas=(0.04, 0.02)):
    """
    Cross-check that R1 = numerical small-η is converged: compare η=0.04
    to η=0.02 over a coarse grid. If the residuals are small compared to
    the η=0.397 → η=0.04 residual scale, R1 is safely linear.
    """
    det_rel = np.linspace(-det_rel_max, +det_rel_max, n_det)
    n_alpha = len(alphas)
    out = {}
    for eta in etas:
        print(f'\n=== R1-conv / η = {eta} ===')
        sx = np.zeros((n_alpha, n_det))
        sy = np.zeros((n_alpha, n_det))
        sz = np.zeros((n_alpha, n_det))
        for i, a in enumerate(alphas):
            d, conv, dt = run_one_alpha(a, det_rel, eta=eta)
            sx[i] = d['sigma_x']; sy[i] = d['sigma_y']; sz[i] = d['sigma_z']
            print(f'  |α|={a}  time={dt:.2f}s  leak={conv["max_fock_leakage"]:.2e}')
        out[eta] = dict(sigma_x=sx, sigma_y=sy, sigma_z=sz)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with h5py.File(out_path, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('alpha', data=np.array(alphas))
        for eta in etas:
            g = f.create_group(f'eta_{eta:.2f}')
            for k, v in out[eta].items():
                g.create_dataset(k, data=v)
        f.attrs['purpose'] = 'R1 convergence cross-check (Guardian flag 1)'
        f.attrs['etas'] = list(etas)
        f.attrs['datetime'] = datetime.now(timezone.utc).isoformat()
        f.attrs['git_commit'] = git_commit_hash()
    print(f'\nWrote {out_path}')


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--slice', choices=['S1', 'S2', 'R1conv'], default='S1')
    ap.add_argument('--out', default=None)
    ap.add_argument('--n-det', type=int, default=121)
    ap.add_argument('--n-phi', type=int, default=64,
                    help='φ_α grid size for S2 (default 64; minimum 48)')
    ap.add_argument('--alpha', type=float, default=3.0,
                    help='|α| value for S2 sheet (default 3.0)')
    args = ap.parse_args()

    DEFAULT_OUT = {
        'S1': os.path.join(SCRIPT_DIR, 'S1_delta_alpha.h5'),
        'S2': os.path.join(SCRIPT_DIR, f'S2_delta_phi_alpha{args.alpha:g}.h5'),
        'R1conv': os.path.join(SCRIPT_DIR, 'R1_convergence.h5'),
    }
    out = args.out or DEFAULT_OUT[args.slice]

    if args.slice == 'S1':
        execute_S1(out, n_det=args.n_det)
    elif args.slice == 'S2':
        execute_S2_sheet(out, alpha=args.alpha,
                         n_phi=args.n_phi, n_det=args.n_det)
    elif args.slice == 'R1conv':
        execute_R1_convergence(out)
