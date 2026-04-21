#!/usr/bin/env python3
"""
run_alpha_recovery_v2.py — §5.3 finalization probe.

Two targeted extensions of run_alpha_recovery_v1.py to address the
reviewer walk-back of the 2026-04-21-alpha-recovery entry:

  Test A (rubric reinterpretation — demonstrate or refute):
    Under option-(a) recalibrated Ω at δt/T_m = 0.80, measure *both*
    V (at δ=0) and P (at δ=0.5·ω_m) across the dense |α| grid. If
    P ≈ 1 across the V oscillation, the (V low, P high) rubric row
    contains an |α|-revival of the encoder map rather than being
    pure pulse-broadening.

  Test B (JC-revival hypothesis — cleanly falsify or confirm):
    Repeat the dense |α| scan under option-(b) fixed Ω = Ω_Hasse at
    the *same* δt/T_m = 0.80 across N ∈ {24, 48, 96}. In option-(b),
    net train rotation N·Ω_eff·δt is N-dependent (sweeps the Rabi
    envelope), so if a JC-like revival is a confounder of the V(|α|)
    shape, the *shape* (not just amplitude) will vary with N. If the
    shape is invariant to N up to overall scaling, the oscillation is
    intrinsic to |α|, not an N-phase revival.

|α| grid tightened to [2.5, 5.25] (12 points) to stay inside
audit-grade Fock leakage (< 10⁻⁸ at NMAX 80).

Outputs:
    numerics/alpha_recovery_v2.h5
    plots/alpha_recovery_v2.png
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
ALPHA_LIST = np.linspace(2.5, 5.25, 12)
DET_REL_LIST = np.array([0.0, 0.5])
N_THETA0 = 64
NMAX = 80
MW_PHASE_DEG = 0.0
AC_PHASE_DEG = 0.0


def omega_calibrated(N_p: int, dt: float) -> float:
    return (np.pi / (2 * N_p * dt)) / DEBYE_WALLER


def omega_hasse_baseline() -> float:
    dt_hasse = 0.13 * T_M
    return (np.pi / (2 * 30 * dt_hasse)) / DEBYE_WALLER


def run_cell(alpha: float, N_p: int, omega_r: float, hs, C, Cdag):
    """Run (θ₀ × δ) grid at one (α, N, Ω). Return V, P, sz_map, nbar_map, leak5."""
    shift_deg = float(np.degrees(OMEGA_M * DT / 2))
    theta0_grid = np.linspace(0.0, 2 * np.pi, N_THETA0, endpoint=False)
    ac_phase_rad = float(np.radians(AC_PHASE_DEG))
    T_gap = T_M - DT

    # Pre-build initial states per ϑ₀ (independent of δ).
    psi_starts = []
    for th0 in theta0_grid:
        psi0 = hs.prepare_state(
            spin={'theta_deg': 0.0, 'phi_deg': 0.0},
            modes=[{'alpha': alpha,
                    'alpha_phase_deg': float(np.degrees(th0)) + shift_deg}],
        )
        psi_starts.append(hs.apply_mw_pi2(psi0, MW_PHASE_DEG))

    n_det = len(DET_REL_LIST)
    coh = np.zeros((n_det, N_THETA0))
    sz = np.zeros_like(coh); nbar = np.zeros_like(coh)
    leak5_worst = 0.0

    for j, d_rel in enumerate(DET_REL_LIST):
        delta = float(d_rel) * OMEGA_M
        H_pulse = ham.build_pulse_hamiltonian(
            ETA, omega_r, delta, NMAX, C, Cdag,
            ac_phase_rad=ac_phase_rad, omega_m=OMEGA_M,
            intra_pulse_motion=True,
        )
        U_pulse = prop.build_U_pulse(H_pulse, DT)
        U_gap_diag = prop.build_U_gap(
            NMAX, OMEGA_M, T_gap, delta=delta,
            include_motion=True, include_spin_detuning=True,
        )
        train = StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag,
                            n_pulses=int(N_p))
        for i, psi in enumerate(psi_starts):
            psi_f = train.evolve(psi)
            obs = hs.observables(psi_f)
            coh[j, i] = np.sqrt(obs['sigma_x'] ** 2 + obs['sigma_y'] ** 2)
            sz[j, i] = obs['sigma_z']; nbar[j, i] = obs['nbar']
            lk = hs.fock_leakage(psi_f, top_k=5)
            if lk > leak5_worst: leak5_worst = lk

    # Reductions. δ=0 row for V, diamond, dn; δ=0.5 row for P.
    j0 = int(np.argmin(np.abs(DET_REL_LIST - 0.0)))
    jhalf = int(np.argmin(np.abs(DET_REL_LIST - 0.5)))
    V = 1.0 - float(coh[j0].min())
    P = float(coh[jhalf].mean())
    diamond = 0.5 * float(sz[j0].max() - sz[j0].min())
    dn_peak = float(np.max(np.abs(nbar[j0] - alpha ** 2)))
    return V, P, diamond, dn_peak, leak5_worst


def sweep(label: str, omega_getter):
    """Run the (α, N) grid for one calibration scheme."""
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX); Cdag = C.conj().T

    nA, nN = len(ALPHA_LIST), len(N_LIST)
    V = np.zeros((nA, nN)); P = np.zeros_like(V)
    diamond = np.zeros_like(V); dn = np.zeros_like(V)
    leak5 = np.zeros_like(V); net_rot = np.zeros_like(V)

    print(f"\n[{label}]")
    for a, alpha in enumerate(ALPHA_LIST):
        for b, N_p in enumerate(N_LIST):
            omega_r = omega_getter(int(N_p))
            V[a,b], P[a,b], diamond[a,b], dn[a,b], leak5[a,b] = \
                run_cell(float(alpha), int(N_p), omega_r, hs, C, Cdag)
            om_eff = omega_r * DEBYE_WALLER
            net_rot[a,b] = (int(N_p) * om_eff * DT) / (np.pi / 2)
        print(f"  α={alpha:5.2f}  "
              f"V(N=24,48,96)=[{V[a,0]:.3f} {V[a,1]:.3f} {V[a,2]:.3f}]  "
              f"P=[{P[a,0]:.3f} {P[a,1]:.3f} {P[a,2]:.3f}]  "
              f"leak5_max={leak5[a].max():.2e}")
    return dict(V=V, P=P, diamond_amp_sigma_z=diamond, dn_peak=dn,
                fock_leakage_top5=leak5, net_rotation_pi2=net_rot)


def main():
    t0 = time.time()
    print(f"α-recovery v2 (§5.3 finalization) — engine v{CODE_VERSION}")
    print(f"  |α| ∈ [{ALPHA_LIST.min():.2f}, {ALPHA_LIST.max():.2f}]  "
          f"({len(ALPHA_LIST)} points) at δt/Tm={DT_FRAC}")
    print(f"  N ∈ {list(int(n) for n in N_LIST)}  NMAX={NMAX}  "
          f"detunings δ/ω_m ∈ {list(DET_REL_LIST)}")

    # Option (a) — recalibrated Ω per cell (same as v1, plus P).
    res_a = sweep('option (a): recalibrated Ω',
                  lambda N_p: omega_calibrated(N_p, DT))
    # Option (b) — fixed Ω_Hasse (carrier rotation varies with N).
    om_hasse = omega_hasse_baseline()
    res_b = sweep(f'option (b): fixed Ω_Hasse  (Ω_eff/ω_m={om_hasse*DEBYE_WALLER/OMEGA_M:.4f})',
                  lambda N_p: om_hasse)

    elapsed = time.time() - t0
    print(f"\n  total wall: {elapsed:.1f} s")

    out_h5 = os.path.join(SCRIPT_DIR, 'alpha_recovery_v2.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('alpha', data=ALPHA_LIST)
        f.create_dataset('N_list', data=N_LIST)
        f.create_dataset('det_rel_list', data=DET_REL_LIST)
        for label, res in [('option_a_recalibrated', res_a),
                           ('option_b_fixed_omega_hasse', res_b)]:
            g = f.create_group(label)
            for k, v in res.items():
                g.create_dataset(k, data=np.asarray(v))
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['dt_frac'] = DT_FRAC
        f.attrs['nmax'] = NMAX
        f.attrs['n_theta0'] = N_THETA0
        f.attrs['omega_hasse'] = om_hasse
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('α-recovery §5.3 finalization: option-(a) with P, '
                            'option-(b) fixed Ω_Hasse for JC-revival test.')
    print(f"  wrote {out_h5}")

    # ── Plot: 2×3 grid ───────────────────────────────────────────
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.5))
    fig.suptitle(r'α-recovery v2 — §5.3 finalization', fontsize=12)

    # Row 1 — option (a): V, P, diamond
    for b, N_p in enumerate(N_LIST):
        axes[0,0].plot(ALPHA_LIST, res_a['V'][:,b], 'o-',
                       label=rf'$N={int(N_p)}$')
    axes[0,0].axhline(0.865, color='darkorange', ls='--', lw=1,
                      label=r'$V_\mathrm{imp}\approx 0.865$')
    axes[0,0].set_ylabel(r'$V=1-\min_\vartheta|C|$  at $\delta=0$')
    axes[0,0].set_title('(a) recalibrated Ω: V', fontsize=10)
    axes[0,0].grid(alpha=0.3); axes[0,0].legend(fontsize=7)
    axes[0,0].set_ylim(-0.05, 1.0)

    for b, N_p in enumerate(N_LIST):
        axes[0,1].plot(ALPHA_LIST, res_a['P'][:,b], 's-',
                       label=rf'$N={int(N_p)}$')
    axes[0,1].set_ylabel(r'$P=\langle|C|\rangle_\vartheta$  at $\delta=0.5\,\omega_m$')
    axes[0,1].set_title('(a) recalibrated Ω: P  (rubric test)', fontsize=10)
    axes[0,1].grid(alpha=0.3); axes[0,1].legend(fontsize=7)
    axes[0,1].set_ylim(-0.05, 1.1)

    for b, N_p in enumerate(N_LIST):
        axes[0,2].plot(ALPHA_LIST, res_a['diamond_amp_sigma_z'][:,b], '^-',
                       label=rf'$N={int(N_p)}$')
    axes[0,2].set_ylabel(r'$\frac{1}{2}(\max-\min)\,\langle\sigma_z\rangle$')
    axes[0,2].set_title('(a) recalibrated Ω: diamond', fontsize=10)
    axes[0,2].grid(alpha=0.3); axes[0,2].legend(fontsize=7)

    # Row 2 — option (b): V, P, V-shape normalisation
    for b, N_p in enumerate(N_LIST):
        net = res_b['net_rotation_pi2'][0,b]
        axes[1,0].plot(ALPHA_LIST, res_b['V'][:,b], 'o-',
                       label=rf'$N={int(N_p)}$ (net rot $\approx{net:.1f}\,\pi/2$)')
    axes[1,0].set_xlabel(r'$|\alpha|$')
    axes[1,0].set_ylabel(r'$V$  at $\delta=0$')
    axes[1,0].set_title(r'(b) fixed $\Omega_\mathrm{Hasse}$: V', fontsize=10)
    axes[1,0].grid(alpha=0.3); axes[1,0].legend(fontsize=6.5)
    axes[1,0].set_ylim(-0.05, 1.0)

    for b, N_p in enumerate(N_LIST):
        axes[1,1].plot(ALPHA_LIST, res_b['P'][:,b], 's-',
                       label=rf'$N={int(N_p)}$')
    axes[1,1].set_xlabel(r'$|\alpha|$')
    axes[1,1].set_ylabel(r'$P$  at $\delta=0.5\,\omega_m$')
    axes[1,1].set_title(r'(b) fixed $\Omega_\mathrm{Hasse}$: P', fontsize=10)
    axes[1,1].grid(alpha=0.3); axes[1,1].legend(fontsize=7)
    axes[1,1].set_ylim(-0.05, 1.1)

    # Shape-normalised V(|α|) — each N-curve rescaled to [0, 1] for
    # shape comparison (JC-revival test).
    for b, N_p in enumerate(N_LIST):
        Vb = res_b['V'][:,b]
        rng = Vb.max() - Vb.min()
        Vb_norm = (Vb - Vb.min()) / rng if rng > 1e-6 else Vb * 0
        axes[1,2].plot(ALPHA_LIST, Vb_norm, 'o-',
                       label=rf'$N={int(N_p)}$')
    Va_norm_ref = res_a['V'][:,1]
    rng_a = Va_norm_ref.max() - Va_norm_ref.min()
    axes[1,2].plot(ALPHA_LIST, (Va_norm_ref - Va_norm_ref.min()) / rng_a,
                   'k--', lw=1, label='(a) recalibrated, N=48')
    axes[1,2].set_xlabel(r'$|\alpha|$')
    axes[1,2].set_ylabel(r'$V$  (rescaled to $[0,1]$)')
    axes[1,2].set_title('(b) shape test — JC-revival discriminant',
                        fontsize=10)
    axes[1,2].grid(alpha=0.3); axes[1,2].legend(fontsize=7)
    axes[1,2].set_ylim(-0.05, 1.05)

    out_png = os.path.join(PLOTS_DIR, 'alpha_recovery_v2.png')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_png, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out_png}")


if __name__ == '__main__':
    main()
