#!/usr/bin/env python3
"""
run_fig8_v3.py — Hasse Fig 8 with Hasse-matched (N, δt, Ω) regime.

Same parameter matching as run_fig6_v3.py:
    N        = 30
    δt/T_m   = 0.13
    Ω/ω_m    ≈ 0.069  (Ω derived to keep π/2 budget at the new δt)
    intra_pulse_motion = True

Sweeps |α| ∈ [0, 8] at three LF tilts, n_thermal = 0.15 with 24
thermal trajectories. The Round-2 question: does shifting the engine
into the smearing regime (ω_m·δt = 0.82 rad/pulse) recover Hasse
Fig 8b's smooth monotonic contrast decay?

Output: numerics/fig8_calibrations_v3.h5
        plots/fig8a_position_v3.png
        plots/fig8b_momentum_v3.png
"""

import os, sys, time
from datetime import datetime, timezone
import numpy as np
import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts'))
PLOTS_DIR  = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
sys.path.insert(0, ENGINE_DIR)
import stroboscopic_sweep as ss


ETA_LF      = 0.397
TILT_DEG    = (-5.0, 0.0, +5.0)
ALPHA_GRID  = np.linspace(0.0, 8.0, 17)
OMEGA_M     = 1.3

# Hasse-matched timing
T_M           = 2 * np.pi / OMEGA_M
DELTA_T_FRAC  = 0.13
DELTA_T       = DELTA_T_FRAC * T_M
N_PULSES      = 30
N_THERMAL     = 0.15
N_TH_TRAJ     = 24

INTRA_MOTION  = True
MW_PHASE_DEG  = 0.0


def omega_for_eta(eta):
    """Choose Ω per tilt so that N·Ω_eff·δt = π/2."""
    debye_waller = np.exp(-eta ** 2 / 2)
    omega_eff = np.pi / (2 * N_PULSES * DELTA_T)
    return omega_eff / debye_waller


def nmax_for_alpha(alpha):
    a = float(alpha)
    if a <= 1.0: return 30
    if a <= 3.0: return 60
    if a <= 5.0: return 100
    return 140


def run_single_alpha_eta(alpha, eta):
    p = dict(
        alpha=float(alpha), alpha_phase_deg=0.0,
        eta=float(eta), omega_m=OMEGA_M,
        omega_r=omega_for_eta(eta),
        n_pulses=N_PULSES, n_thermal=N_THERMAL,
        n_thermal_traj=N_TH_TRAJ,
        nmax=nmax_for_alpha(alpha),
        det_min=0.0, det_max=0.0, npts=1,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0,
        T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_rep=0,
        mw_pi2_phase_deg=MW_PHASE_DEG,
        intra_pulse_motion=INTRA_MOTION,
        delta_t_us=DELTA_T,
    )
    d, conv = ss.run_single(p, verbose=False)
    return d['sigma_x'][0], d['sigma_y'][0], d['sigma_z'][0], conv['max_fock_leakage']


def main():
    out_path = os.path.join(SCRIPT_DIR, 'fig8_calibrations_v3.h5')
    n_a, n_t = len(ALPHA_GRID), len(TILT_DEG)

    print(f"Hasse-matched parameters (engine v{ss.CODE_VERSION}):")
    print(f"  T_m         = {T_M:.3f}")
    print(f"  δt          = {DELTA_T:.3f}  ({DELTA_T_FRAC*100:.0f}% of T_m)")
    print(f"  N_pulses    = {N_PULSES}")
    print(f"  ω_m·δt      = {OMEGA_M*DELTA_T:.3f} rad")
    print()

    sx_arr = np.zeros((n_t, n_a)); sy_arr = np.zeros((n_t, n_a))
    sz_arr = np.zeros((n_t, n_a)); leak   = np.zeros((n_t, n_a))

    t0 = time.time()
    for j, tilt in enumerate(TILT_DEG):
        eta_j = ETA_LF * np.cos(np.radians(tilt))
        print(f"\n=== tilt {tilt:+.0f}°  η = {eta_j:.4f}  Ω = {omega_for_eta(eta_j):.4f} ===")
        for i, a in enumerate(ALPHA_GRID):
            sx_arr[j,i], sy_arr[j,i], sz_arr[j,i], leak[j,i] = run_single_alpha_eta(a, eta_j)
            print(f"  |α|={a:4.1f}  σ_x={sx_arr[j,i]:+.3f}  σ_y={sy_arr[j,i]:+.3f}  "
                  f"σ_z={sz_arr[j,i]:+.3f}  |C|={np.hypot(sx_arr[j,i], sy_arr[j,i]):.3f}  "
                  f"leak={leak[j,i]:.1e}", flush=True)
    elapsed = time.time() - t0

    C_abs = np.hypot(sx_arr, sy_arr)
    C_arg = np.arctan2(sy_arr, sx_arr)
    phi0  = np.unwrap(C_arg, axis=1); phi0 -= phi0[:, :1]
    contrast_norm = C_abs / np.maximum(C_abs[:, :1], 1e-12)

    print(f"\n  total time {elapsed:.1f} s for {n_t}×{n_a} = {n_t*n_a} runs")

    with h5py.File(out_path, 'w') as f:
        f.create_dataset('alpha',         data=ALPHA_GRID)
        f.create_dataset('tilt_deg',      data=np.array(TILT_DEG))
        f.create_dataset('eta_per_tilt',  data=ETA_LF * np.cos(np.radians(TILT_DEG)))
        f.create_dataset('omega_per_tilt',
                          data=np.array([omega_for_eta(ETA_LF*np.cos(np.radians(t))) for t in TILT_DEG]))
        f.create_dataset('sigma_x', data=sx_arr)
        f.create_dataset('sigma_y', data=sy_arr)
        f.create_dataset('sigma_z', data=sz_arr)
        f.create_dataset('C_abs',   data=C_abs)
        f.create_dataset('C_arg_rad', data=C_arg)
        f.create_dataset('phi0_rad', data=phi0)
        f.create_dataset('contrast_norm', data=contrast_norm)
        f.create_dataset('max_fock_leakage', data=leak)
        f.attrs['eta_LF']     = ETA_LF
        f.attrs['omega_m']    = OMEGA_M
        f.attrs['n_pulses']   = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['delta_t_frac_Tm'] = DELTA_T_FRAC
        f.attrs['n_thermal']  = N_THERMAL
        f.attrs['n_thermal_traj'] = N_TH_TRAJ
        f.attrs['mw_pi2_phase_deg'] = MW_PHASE_DEG
        f.attrs['intra_pulse_motion'] = int(INTRA_MOTION)
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()

    TILT_COLORS = {-5.0: 'tab:green', 0.0: 'tab:blue', +5.0: 'tab:orange'}

    fig, ax = plt.subplots(figsize=(5.4, 4.2))
    for j, tilt in enumerate(TILT_DEG):
        c = TILT_COLORS.get(float(tilt), 'k')
        ax.plot(phi0[j], ALPHA_GRID, color=c,
                label=fr'tilt {tilt:+.0f}°  ($\eta={ETA_LF*np.cos(np.radians(tilt)):.4f}$)')
    ax.set_xlabel(r'Analysis-phase shift $\varphi_0$ (rad)')
    ax.set_ylabel(r'$|\alpha|$')
    ax.axhline(0, color='k', lw=0.3); ax.axvline(0, color='k', lw=0.3)
    ax.set_xlim(-2*np.pi, +2*np.pi)
    ax.set_xticks([-2*np.pi, -np.pi, 0, np.pi, 2*np.pi])
    ax.set_xticklabels([r'$-2\pi$', r'$-\pi$', '0', r'$\pi$', r'$2\pi$'])
    ax.set_ylim(0, ALPHA_GRID.max() * 1.05)
    ax.legend(fontsize=8)
    ax.set_title(f'Hasse Fig 8a v3 — Hasse-matched (N=30, $\\delta t/T_m$=0.13, $n_\\mathrm{{th}}$=0.15)',
                 fontsize=9)
    out = os.path.join(PLOTS_DIR, 'fig8a_position_v3.png')
    fig.tight_layout(); fig.savefig(out, dpi=140); plt.close(fig)
    print(f"  wrote {out}")

    fig, ax = plt.subplots(figsize=(5.4, 4.2))
    for j, tilt in enumerate(TILT_DEG):
        c = TILT_COLORS.get(float(tilt), 'k')
        ax.plot(contrast_norm[j], ALPHA_GRID, color=c,
                label=fr'tilt {tilt:+.0f}°  ($\eta={ETA_LF*np.cos(np.radians(tilt)):.4f}$)')
    ax.set_xlabel('Contrast  $C / C(\\alpha=0)$')
    ax.set_ylabel(r'$|\alpha|$')
    ax.set_xlim(-0.05, 1.10); ax.set_ylim(0, ALPHA_GRID.max()*1.05)
    ax.legend(fontsize=8)
    ax.set_title(f'Hasse Fig 8b v3 — Hasse-matched (N=30, $\\delta t/T_m$=0.13, $n_\\mathrm{{th}}$=0.15)',
                 fontsize=9)
    out = os.path.join(PLOTS_DIR, 'fig8b_momentum_v3.png')
    fig.tight_layout(); fig.savefig(out, dpi=140); plt.close(fig)
    print(f"  wrote {out}")

    print("\nHasse Fig 8 anchor numbers (v3 vs published):")
    for j, tilt in enumerate(TILT_DEG):
        print(f"  tilt {tilt:+.0f}°: ϕ₀(α=8)={phi0[j,-1]:+.3f} rad (Hasse ≈ ±2π);  "
              f"C(α=8)/C(α=0)={contrast_norm[j,-1]:.3f} (Hasse ≈ 0)")


if __name__ == '__main__':
    main()
