#!/usr/bin/env python3
"""
run_coastline_doppler_v1.py — §9.1 Doppler-merging probe.

Scope: memo §9.1 asked to re-run the coastline grid with δ scaled per
cell to land inside the Doppler-broadened sideband envelope, in order
to exercise the (V low, P low) quadrant of the §4.3 rubric that v0.1
never reached (P was near 1 everywhere because δ=0.5·ω_m sat between
teeth where the Doppler envelope had not yet flooded).

Approach: reuse the v0.1 6×6 (N, δt/T_m) × 4 |α| grid at option-(a)
recalibrated Ω, but sweep a seven-point detuning ladder
δ/ω_m ∈ {0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0} per cell. For each (|α|,
N, δt/T_m) cell this produces a spectral-P vector. Reduce to:

  V             = 1 − min_ϑ |C|                      at δ = 0
  P_half        = ⟨|C|⟩_ϑ                            at δ = 0.5·ω_m  (v0.1 compatible)
  P_mid_min     = min over mid-sideband detunings    δ/ω_m ∈ {0.25, 0.5, 0.75, 1.25, 1.5, 1.75}
                                                      (we use available
                                                       0.25, 0.5, 0.75, 1.5 points)
  P_spectrum    = full seven-point |C|̄(δ) trace per cell (kept for plots)

A (V low, P_mid_min low) cell is the Doppler-merging regime proper.

Compute budget: 36 cells × 7 detunings × 64 ϑ₀ × 4 |α| ≈ 65 k
evolutions. At v0.1's rate (≈ 1300 evolutions/s on this hardware),
expected wall time ≈ 50 s — comfortably under the two-minute memo §6
cap.

Outputs:
    numerics/coastline_doppler_v1.h5
    plots/coastline_doppler.png
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
from matplotlib.patches import Rectangle

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

N_LIST = np.array([3, 6, 12, 24, 48, 96], dtype=np.int64)
DT_FRAC_LIST = np.array([0.02, 0.05, 0.10, 0.20, 0.40, 0.80])
DET_REL_LIST = np.array([0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
# Mid-sideband subset used for P_mid_min reduction (excludes the tooth-
# coincidence points at δ/ω_m ∈ {0, 1.0, 2.0}).
MID_SIDEBAND_IDX = np.array([1, 2, 3, 5], dtype=np.int64)  # 0.25, 0.5, 0.75, 1.5
ALPHA_LIST = np.array([0.0, 1.0, 3.0, 5.0])
N_THETA0 = 64
MW_PHASE_DEG = 0.0
AC_PHASE_DEG = 0.0

OMEGA_EFF_CEILING = 0.3
MOTIONAL_LD_THRESHOLD = 1.0


def nmax_for_alpha(alpha: float) -> int:
    return 80 if alpha >= 4.5 else 60


def omega_calibrated(N: int, dt: float) -> float:
    return (np.pi / (2 * N * dt)) / DEBYE_WALLER


def evolve_cell(alpha, N_p, dt, omega_r, hs, C, Cdag):
    """Return (coh_spectrum, V, diamond, dn_peak, leak5_worst).

    coh_spectrum has shape (len(DET_REL_LIST), N_THETA0).
    """
    nmax = hs.nmax
    ac_phase_rad = float(np.radians(AC_PHASE_DEG))
    shift_deg = float(np.degrees(OMEGA_M * dt / 2))
    T_gap = T_M - dt
    theta0_grid = np.linspace(0.0, 2 * np.pi, N_THETA0, endpoint=False)

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
    sz0 = np.zeros(N_THETA0); nbar0 = np.zeros(N_THETA0)
    leak5_worst = 0.0

    for j, d_rel in enumerate(DET_REL_LIST):
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
                            n_pulses=int(N_p))
        for i, psi in enumerate(psi_starts):
            psi_f = train.evolve(psi)
            obs = hs.observables(psi_f)
            coh[j, i] = np.sqrt(obs['sigma_x'] ** 2 + obs['sigma_y'] ** 2)
            if j == 0:
                sz0[i] = obs['sigma_z']; nbar0[i] = obs['nbar']
            lk = hs.fock_leakage(psi_f, top_k=5)
            if lk > leak5_worst: leak5_worst = lk

    V = 1.0 - float(coh[0].min())
    diamond = 0.5 * float(sz0.max() - sz0.min())
    dn_peak = float(np.max(np.abs(nbar0 - alpha ** 2)))
    return coh, V, diamond, dn_peak, leak5_worst


def sweep_alpha(alpha):
    nmax = nmax_for_alpha(alpha)
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(nmax,))
    C = ops.coupling(ETA, nmax); Cdag = C.conj().T

    nN, ndt = len(N_LIST), len(DT_FRAC_LIST)
    V = np.zeros((nN, ndt))
    P_spectrum = np.zeros((nN, ndt, len(DET_REL_LIST)))
    diamond = np.zeros_like(V)
    dn_peak = np.zeros_like(V)
    leak5 = np.zeros_like(V)
    omega_eff = np.zeros_like(V)
    ld_drive_flag = np.zeros_like(V, dtype=bool)
    ld_motional_param = np.zeros_like(V)
    ld_motional_flag = np.zeros_like(V, dtype=bool)

    eta_sqrt_alpha = ETA * np.sqrt(alpha ** 2 + 1.0)

    for a, N_p in enumerate(N_LIST):
        for b, dt_frac in enumerate(DT_FRAC_LIST):
            dt = float(dt_frac) * T_M
            omega_r = omega_calibrated(int(N_p), dt)
            om_eff = omega_r * DEBYE_WALLER
            coh, Vv, dmd, dn, lk = evolve_cell(
                alpha, int(N_p), dt, omega_r, hs, C, Cdag)
            V[a, b] = Vv
            P_spectrum[a, b] = coh.mean(axis=1)
            diamond[a, b] = dmd; dn_peak[a, b] = dn
            leak5[a, b] = lk
            omega_eff[a, b] = om_eff / OMEGA_M
            ld_drive_flag[a, b] = (om_eff / OMEGA_M) > OMEGA_EFF_CEILING
            ld_motional_param[a, b] = eta_sqrt_alpha
            ld_motional_flag[a, b] = eta_sqrt_alpha > MOTIONAL_LD_THRESHOLD
        print(f"    |α|={alpha:>3}  N={int(N_p):>3}  "
              f"V̄={V[a].mean():.3f}  "
              f"P_half̄={P_spectrum[a,:,2].mean():.3f}  "
              f"P_mid_min̄={P_spectrum[a][:, MID_SIDEBAND_IDX].min(axis=1).mean():.3f}  "
              f"leak5_max={leak5[a].max():.2e}")

    P_half = P_spectrum[:, :, 2]  # δ/ω_m = 0.5, matches v0.1
    P_mid_min = P_spectrum[:, :, MID_SIDEBAND_IDX].min(axis=2)
    return dict(V=V, P_spectrum=P_spectrum, P_half=P_half,
                P_mid_min=P_mid_min, diamond_amp_sigma_z=diamond,
                dn_peak=dn_peak, fock_leakage_top5=leak5,
                omega_eff_over_omega_m=omega_eff,
                ld_flag_drive=ld_drive_flag,
                ld_motional_param=ld_motional_param,
                ld_flag_motional=ld_motional_flag,
                nmax_used=np.full_like(V, nmax, dtype=np.int64))


def main():
    t_start = time.time()
    print(f"Doppler-merging probe — engine v{CODE_VERSION}")
    print(f"  6×6 (N, δt/Tm) × 4 |α| × 7 detunings, NMAX policy 60/80\n")

    out_h5 = os.path.join(SCRIPT_DIR, 'coastline_doppler_v1.h5')
    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('N_list', data=N_LIST)
        f.create_dataset('dt_frac_list', data=DT_FRAC_LIST)
        f.create_dataset('det_rel_list', data=DET_REL_LIST)
        f.create_dataset('mid_sideband_idx', data=MID_SIDEBAND_IDX)
        f.create_dataset('alpha_list', data=ALPHA_LIST)
        f.attrs['eta'] = ETA
        f.attrs['omega_m'] = OMEGA_M
        f.attrs['calibration_mode'] = 'option_a_recalibrated_omega'
        f.attrs['omega_eff_ceiling'] = OMEGA_EFF_CEILING
        f.attrs['motional_ld_threshold'] = MOTIONAL_LD_THRESHOLD
        f.attrs['code_version'] = CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['probe'] = 'memo-v0.4.4-§9.1-doppler-merging'

        for alpha in ALPHA_LIST:
            tag = f"alpha_{alpha:.1f}".replace('.', 'p')
            print(f"  sweeping α = {alpha} …")
            t0 = time.time()
            res = sweep_alpha(float(alpha))
            dt_a = time.time() - t0
            print(f"    α={alpha} done in {dt_a:.1f} s\n")
            g = f.create_group(tag)
            for k, v in res.items():
                g.create_dataset(k, data=np.asarray(v))
            g.attrs['alpha'] = float(alpha)
            g.attrs['nmax'] = int(res['nmax_used'].flat[0])
            g.attrs['elapsed_seconds'] = dt_a
    elapsed = time.time() - t_start
    print(f"  TOTAL elapsed: {elapsed:.1f} s")
    print(f"  wrote {out_h5}")

    # ── Plot ─────────────────────────────────────────────────────
    fig = plt.figure(figsize=(15, 3.0 * len(ALPHA_LIST)))
    for ai, alpha in enumerate(ALPHA_LIST):
        tag = f"alpha_{alpha:.1f}".replace('.', 'p')
        with h5py.File(out_h5, 'r') as f:
            V = f[tag]['V'][:]
            P_half = f[tag]['P_half'][:]
            P_mid_min = f[tag]['P_mid_min'][:]
            ld_drive = f[tag]['ld_flag_drive'][:]
            ld_mot = f[tag]['ld_flag_motional'][:]

        def overlay(ax, mask, edgecolor, hatch, lw=0.0):
            nrow, ncol = mask.shape
            for i in range(nrow):
                for j in range(ncol):
                    if mask[i, j]:
                        ax.add_patch(Rectangle(
                            (j - 0.5, i - 0.5), 1.0, 1.0,
                            facecolor='none', edgecolor=edgecolor,
                            hatch=hatch, linewidth=lw))

        for col, (name, arr) in enumerate(
                [('V', V), ('P at δ=0.5·ω_m', P_half),
                 ('P_min over mid-sideband', P_mid_min)]):
            ax = plt.subplot(len(ALPHA_LIST), 3,
                             ai * 3 + col + 1)
            im = ax.imshow(arr, origin='lower', aspect='auto',
                           vmin=0.0, vmax=1.0, cmap='viridis')
            overlay(ax, ld_drive, 'white', '///')
            overlay(ax, ld_mot, 'red', '...', lw=0.5)
            ax.set_xticks(range(len(DT_FRAC_LIST)))
            ax.set_xticklabels([f'{x:.2f}' for x in DT_FRAC_LIST],
                               fontsize=7)
            ax.set_yticks(range(len(N_LIST)))
            ax.set_yticklabels([f'{int(n)}' for n in N_LIST], fontsize=7)
            if ai == len(ALPHA_LIST) - 1:
                ax.set_xlabel(r'$\delta t/T_m$', fontsize=8)
            if col == 0:
                ax.set_ylabel(r'$N$', fontsize=8)
            ax.set_title(rf'$|\alpha|={alpha:.0f}$:  {name}', fontsize=9)
            for i in range(arr.shape[0]):
                for j in range(arr.shape[1]):
                    v = arr[i, j]
                    color = 'white' if v < 0.5 else 'black'
                    ax.text(j, i, f'{v:.2f}', ha='center', va='center',
                            fontsize=6, color=color)
            plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    fig.suptitle(r'WP-C §9.1 Doppler-merging probe — $V$, $P_{\delta=0.5\omega_m}$, '
                 r'$P_{\min}$ over mid-sideband detunings',
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    out_png = os.path.join(PLOTS_DIR, 'coastline_doppler.png')
    fig.savefig(out_png, dpi=130, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out_png}")


if __name__ == '__main__':
    main()
