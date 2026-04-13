#!/usr/bin/env python3
"""
run_S2_v09_compare.py — S2 sheet at |α|=3 under v0.9 D1 (Hasse-matched).

Sequel to the published S2 result
([../logbook/2026-04-13-S2-falsification.md](../logbook/2026-04-13-S2-falsification.md))
which proved |C| φ_α-independence at machine precision under v0.8.
This driver re-runs the same (δ₀, φ_α) sheet at |α|=3 with
intra_pulse_motion=True and Hasse-matched (N=30, δt=0.13·T_m, Ω
re-derived to the π/2 budget at the new δt) to quantify the
v0.8 → v0.9 |C| spread.

Output: numerics/S2_v09_alpha3.h5 + plots/S2_alpha3_v09_compare.png
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


ALPHA       = 3.0
ETA         = 0.397
OMEGA_M     = 1.3
T_M         = 2 * np.pi / OMEGA_M
DELTA_T     = 0.13 * T_M
N_PULSES    = 30
DEBYE       = np.exp(-ETA ** 2 / 2)
OMEGA_R     = (np.pi / (2 * N_PULSES * DELTA_T)) / DEBYE
NMAX        = 60

N_PHI       = 64
N_DET       = 121
DET_REL_MAX = 6.0 / OMEGA_M


def main():
    out_h5 = os.path.join(SCRIPT_DIR, 'S2_v09_alpha3.h5')

    print(f"S2 v0.9 comparison sheet at |α| = {ALPHA}")
    print(f"  N={N_PULSES}, δt={DELTA_T:.4f}, Ω={OMEGA_R:.4f}, Ω/ω_m={OMEGA_R/OMEGA_M:.3f}")
    print(f"  ω_m·δt = {OMEGA_M*DELTA_T:.3f} rad   (intra-pulse smearing on)")
    print()

    det_rel = np.linspace(-DET_REL_MAX, +DET_REL_MAX, N_DET)
    phi_deg = np.linspace(0.0, 360.0, N_PHI, endpoint=False)

    sx = np.zeros((N_PHI, N_DET))
    sy = np.zeros((N_PHI, N_DET))
    sz = np.zeros((N_PHI, N_DET))
    leak = np.zeros(N_PHI)

    base = dict(
        alpha=ALPHA, eta=ETA, omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES, n_thermal=0.0, nmax=NMAX,
        det_min=float(det_rel[0]), det_max=float(det_rel[-1]), npts=N_DET,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0,
        T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_thermal_traj=1, n_rep=0,
        intra_pulse_motion=True,
        delta_t_us=DELTA_T,
        center_pulses_at_phase=True,
    )

    t0 = time.time()
    for j, phi in enumerate(phi_deg):
        p = dict(base, alpha_phase_deg=float(phi))
        d, conv = ss.run_single(p, verbose=False)
        sx[j] = d['sigma_x']
        sy[j] = d['sigma_y']
        sz[j] = d['sigma_z']
        leak[j] = conv['max_fock_leakage']
        if (j + 1) % 8 == 0:
            print(f"  φ_α {j+1}/{N_PHI}  worst leak {leak[j]:.1e}", flush=True)
    elapsed = time.time() - t0
    print(f"  done — {elapsed:.1f} s  worst Fock leakage {leak.max():.2e}")

    C_abs = np.sqrt(sx**2 + sy**2)
    C_arg_deg = np.degrees(np.arctan2(sy, sx))

    # The headline number: |C|(δ₀, φ_α) spread vs the φ_α=0 reference
    delta_C_abs = C_abs - C_abs[0:1]
    worst_dC = float(np.abs(delta_C_abs).max())
    print(f"\n  worst |Δ|C|(δ, φ_α)| vs φ=0: {worst_dC:.4e}")
    print(f"  S2-v0.8 published: 6.6e-13 (machine precision)")

    # The headline 1D:  |C|(φ_α) at carrier (δ=0)
    j_carrier = N_DET // 2
    print(f"  |C|(δ=0, φ_α) — at carrier:")
    Cabs_carrier = C_abs[:, j_carrier]
    print(f"    min {Cabs_carrier.min():.5f}  max {Cabs_carrier.max():.5f}  "
          f"spread {Cabs_carrier.max()-Cabs_carrier.min():.4e}")

    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('detuning_rel', data=det_rel)
        f.create_dataset('detuning_MHz_over_2pi', data=det_rel * OMEGA_M)
        f.create_dataset('phi_alpha_deg', data=phi_deg)
        f.create_dataset('sigma_x', data=sx)
        f.create_dataset('sigma_y', data=sy)
        f.create_dataset('sigma_z', data=sz)
        f.create_dataset('C_abs',   data=C_abs)
        f.create_dataset('C_arg_deg', data=C_arg_deg)
        f.create_dataset('max_fock_leakage', data=leak)
        f.attrs['slice']    = 'S2_v09_compare'
        f.attrs['alpha']    = ALPHA
        f.attrs['eta']      = ETA
        f.attrs['omega_m']  = OMEGA_M
        f.attrs['omega_r']  = OMEGA_R
        f.attrs['n_pulses'] = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['delta_t_frac_Tm'] = 0.13
        f.attrs['intra_pulse_motion'] = 1
        f.attrs['mw_pi2_phase_deg'] = -1   # off
        f.attrs['center_pulses_at_phase'] = 1
        f.attrs['nmax']     = NMAX
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = (
            'S2 (δ₀, φ_α) at |α|=3 under v0.9 D1 + Hasse-matched (N=30, '
            'δt=0.13·T_m). Compare against published S2_delta_phi_alpha3.h5 '
            'which uses v0.8 (intra_pulse_motion=False, default N=22, δt auto).'
        )

    # Plot — three-panel layout
    fig = plt.figure(figsize=(13, 4.4), constrained_layout=True)
    gs = fig.add_gridspec(1, 3)

    det_axis = det_rel * OMEGA_M  # MHz/(2π)

    # Left: |C|(δ, φ_α) heatmap
    ax = fig.add_subplot(gs[0, 0])
    vmax = float(C_abs.max())
    im = ax.imshow(
        C_abs, origin='lower', aspect='auto',
        extent=[det_axis[0], det_axis[-1], phi_deg[0], phi_deg[-1]],
        cmap='magma', vmin=0, vmax=vmax)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
    ax.set_title(r'$|C|(\delta_0, \varphi_\alpha)$  v0.9 D1, Hasse-matched',
                 fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.85)

    # Middle: Δ|C| vs φ=0 reference
    ax = fig.add_subplot(gs[0, 1])
    vlim = float(np.abs(delta_C_abs).max())
    im = ax.imshow(
        delta_C_abs, origin='lower', aspect='auto',
        extent=[det_axis[0], det_axis[-1], phi_deg[0], phi_deg[-1]],
        cmap='RdBu_r', vmin=-vlim, vmax=+vlim)
    ax.set_xlabel(r'$\delta_0/(2\pi)$  (MHz)')
    ax.set_ylabel(r'$\varphi_\alpha$ (deg)')
    ax.set_title(rf'$\Delta|C|$ vs $\varphi_\alpha=0$  (max $|\Delta| = {vlim:.2e}$)',
                 fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.85)

    # Right: |C|(δ=0) vs φ_α — line plot
    ax = fig.add_subplot(gs[0, 2])
    ax.plot(phi_deg, Cabs_carrier, color='tab:purple', lw=1.5,
            label=fr'v0.9 D1, Hasse-matched (spread {Cabs_carrier.max()-Cabs_carrier.min():.3f})')
    # Overlay the v0.8 published value as a flat reference
    try:
        v08 = h5py.File(os.path.join(SCRIPT_DIR, 'S2_delta_phi_alpha3.h5'), 'r')
        Cabs_v08 = v08['full']['C_abs'][:, N_DET//2]
        phi_v08  = v08['phi_alpha_deg'][:]
        ax.plot(phi_v08, Cabs_v08, '--', color='gray', lw=1.0,
                label=fr'v0.8 published (spread {Cabs_v08.max()-Cabs_v08.min():.2e})')
        v08.close()
    except (KeyError, OSError) as e:
        print(f'  (v0.8 reference not loaded: {e})')
    ax.set_xlabel(r'$\varphi_\alpha$ (deg)')
    ax.set_ylabel(r'$|C|(\delta_0=0)$')
    ax.set_title(r'Carrier $|C|$ vs $\varphi_\alpha$', fontsize=10)
    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    fig.suptitle(rf'WP-E S2 revisited — $|\alpha|={ALPHA}$, engine v{ss.CODE_VERSION}, '
                 r'D1 + Hasse-matched',
                 fontsize=10)

    out_png = os.path.join(PLOTS_DIR, 'S2_alpha3_v09_compare.png')
    fig.savefig(out_png, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out_png}")


if __name__ == '__main__':
    main()
