#!/usr/bin/env python3
"""
run_alpha_recovery_v1.py — Dense |α| scan at δt/T_m = 0.80.

Addresses §5.3 of council memo v0.4.1: the v0.1 sweep showed
V(|α|=3)=0.101 < V(|α|=5)=0.377 at δt/T_m = 0.80 — a non-monotonic
recovery that the memo flags as either (i) a JC-like revival at large
ηα, (ii) finite-δt Debye–Waller higher-order structure, or (iii)
genuine motional-LD-regime physics. This driver resolves between them
by running a dense |α| grid ∈ [2.5, 6.0] at δ=0, δt/T_m=0.80, over
three N values ∈ {24, 48, 96} to check N-independence.

Output : numerics/alpha_recovery_v1.h5
         plots/alpha_recovery.png

Uses the same engine conventions and option-(a) Ω recalibration as
run_coastline_v1.py. NMAX 80 across the whole scan (|α| up to 6 is
well within the |α|=5 pre-audit margin of 3 × 10⁻¹³ at NMAX 80).
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
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

DT_FRAC = 0.80
DT = DT_FRAC * T_M
N_LIST = np.array([24, 48, 96], dtype=np.int64)
ALPHA_LIST = np.linspace(2.5, 6.0, 15)
N_THETA0 = 64
NMAX = 80
MW_PHASE_DEG = 0.0
AC_PHASE_DEG = 0.0


def omega_calibrated(N_p: int, dt: float) -> float:
    return (np.pi / (2 * N_p * dt)) / DEBYE_WALLER


def run_cell(alpha: float, N_p: int, hs, C, Cdag):
    omega_r = omega_calibrated(N_p, DT)
    shift_deg = float(np.degrees(OMEGA_M * DT / 2))
    theta0_grid = np.linspace(0.0, 2 * np.pi, N_THETA0, endpoint=False)

    H_pulse = ham.build_pulse_hamiltonian(
        ETA, omega_r, 0.0, NMAX, C, Cdag,
        ac_phase_rad=float(np.radians(AC_PHASE_DEG)),
        omega_m=OMEGA_M, intra_pulse_motion=True,
    )
    U_pulse = prop.build_U_pulse(H_pulse, DT)
    T_gap = T_M - DT
    U_gap_diag = prop.build_U_gap(
        NMAX, OMEGA_M, T_gap, delta=0.0,
        include_motion=True, include_spin_detuning=True,
    )
    train = StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag,
                        n_pulses=int(N_p))

    coh = np.zeros(N_THETA0)
    sz = np.zeros_like(coh); nbar = np.zeros_like(coh)
    leak5_worst = 0.0
    for i, th0 in enumerate(theta0_grid):
        psi0 = hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': alpha,
                    'alpha_phase_deg': float(np.degrees(th0)) + shift_deg}],
        )
        psi0 = hs.apply_mw_pi2(psi0, MW_PHASE_DEG)
        psi = train.evolve(psi0)
        obs = hs.observables(psi)
        coh[i] = np.sqrt(obs['sigma_x'] ** 2 + obs['sigma_y'] ** 2)
        sz[i] = obs['sigma_z']; nbar[i] = obs['nbar']
        lk = hs.fock_leakage(psi, top_k=5)
        if lk > leak5_worst: leak5_worst = lk
    V = 1.0 - float(coh.min())
    diamond = 0.5 * float(sz.max() - sz.min())
    dn_peak = float(np.max(np.abs(nbar - alpha ** 2)))
    return V, diamond, dn_peak, leak5_worst, coh


def main():
    t0 = time.time()
    print(f"α-recovery probe — engine v{CODE_VERSION}")
    print(f"  |α| ∈ [{ALPHA_LIST.min():.2f}, {ALPHA_LIST.max():.2f}]  "
          f"({len(ALPHA_LIST)} points) at δt/Tm=0.80, δ=0\n"
          f"  N ∈ {list(N_LIST)}   NMAX={NMAX}\n")

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX); Cdag = C.conj().T

    nA, nN = len(ALPHA_LIST), len(N_LIST)
    V_arr = np.zeros((nA, nN))
    diamond_arr = np.zeros_like(V_arr)
    dn_arr = np.zeros_like(V_arr)
    leak5_arr = np.zeros_like(V_arr)
    coh_curves = np.zeros((nA, nN, N_THETA0))

    for a, alpha in enumerate(ALPHA_LIST):
        for b, N_p in enumerate(N_LIST):
            V, dmd, dn, lk, coh = run_cell(float(alpha), int(N_p), hs, C, Cdag)
            V_arr[a, b] = V
            diamond_arr[a, b] = dmd
            dn_arr[a, b] = dn
            leak5_arr[a, b] = lk
            coh_curves[a, b] = coh
        print(f"  α={alpha:5.2f}  V(N=24)={V_arr[a,0]:.3f}  "
              f"V(N=48)={V_arr[a,1]:.3f}  V(N=96)={V_arr[a,2]:.3f}  "
              f"leak5_max={leak5_arr[a].max():.2e}")

    elapsed = time.time() - t0
    print(f"\n  done in {elapsed:.1f} s\n")

    out_h5 = os.path.join(SCRIPT_DIR, 'alpha_recovery_v1.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('alpha', data=ALPHA_LIST)
        f.create_dataset('N_list', data=N_LIST)
        f.create_dataset('V', data=V_arr)
        f.create_dataset('diamond_amp_sigma_z', data=diamond_arr)
        f.create_dataset('dn_peak', data=dn_arr)
        f.create_dataset('fock_leakage_top5', data=leak5_arr)
        f.create_dataset('coh_abs_theta0', data=coh_curves)
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['dt_frac'] = DT_FRAC
        f.attrs['nmax'] = NMAX
        f.attrs['detuning_rel'] = 0.0
        f.attrs['n_theta0'] = N_THETA0
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('α-recovery probe for council memo §5.3. '
                            'Option-(a) recalibrated Ω; δt/Tm=0.80.')
    print(f"  wrote {out_h5}")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    for b, N_p in enumerate(N_LIST):
        ax1.plot(ALPHA_LIST, V_arr[:, b], 'o-',
                 label=rf'$N={int(N_p)}$')
    ax1.axhline(0.865, color='darkorange', ls='--', lw=1,
                label=r'impulsive floor $V_\mathrm{imp}\approx 0.865$')
    # Reference points from v0.1 main sweep at δt/Tm=0.80, N=48 (approx, from
    # the coastline_v1.h5 row-means reported in results §2.3):
    ref_pts = {3.0: 0.101, 5.0: 0.377}
    for a, v in ref_pts.items():
        ax1.plot(a, v, 'rX', markersize=12, zorder=5)
    ax1.annotate('v0.1 anchors\n(α=3, 5)', xy=(5.0, 0.377), xytext=(5.3, 0.55),
                 fontsize=8, color='red',
                 arrowprops=dict(arrowstyle='->', color='red', lw=0.8))
    ax1.set_xlabel(r'$|\alpha|$'); ax1.set_ylabel(r'$V = 1 - \min_\vartheta |C|$')
    ax1.set_title(r'$V(|\alpha|)$ at $\delta t / T_m = 0.80$, $\delta=0$, '
                  r'option-(a) recalibrated $\Omega$', fontsize=10)
    ax1.grid(alpha=0.3); ax1.legend(fontsize=8); ax1.set_ylim(-0.05, 1.0)

    for b, N_p in enumerate(N_LIST):
        ax2.plot(ALPHA_LIST, diamond_arr[:, b], 'o-',
                 label=rf'$N={int(N_p)}$')
    ax2.set_xlabel(r'$|\alpha|$')
    ax2.set_ylabel(r'$\frac{1}{2}(\max-\min)\,\langle\sigma_z\rangle$')
    ax2.set_title(r'Diamond $\sigma_z$ amplitude vs $|\alpha|$',
                  fontsize=10)
    ax2.grid(alpha=0.3); ax2.legend(fontsize=8)

    fig.suptitle(r'α-recovery probe (council memo §5.3) — '
                 'physics vs artefact discriminant', fontsize=11)
    out_png = os.path.join(PLOTS_DIR, 'alpha_recovery.png')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_png, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out_png}")


if __name__ == '__main__':
    main()
