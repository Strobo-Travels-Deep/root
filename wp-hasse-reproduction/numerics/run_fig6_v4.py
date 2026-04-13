#!/usr/bin/env python3
"""
run_fig6_v4.py — Hasse Fig 6 with v0.9.1 centered-pulse convention.

Same Hasse-matched (N=30, δt=0.13·T_m, Ω derived to π/2 budget) as
run_fig6_v3.py, but now with `center_pulses_at_phase=True` so pulse 1
(and every stroboscopic pulse) is centered on the user-specified
φ_α_AC rather than starting at it. This is the physically natural
"pulse timed to position extremum" convention agreed in the
2026-04-13 session.

Output: numerics/fig6_alpha3_v4.h5 + plots/fig6{a,b}_v4.png
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


ALPHA      = 3.0
ETA        = 0.397
OMEGA_M    = 1.3
NMAX       = 60

DELTA_T_FRAC = 0.13
T_M          = 2 * np.pi / OMEGA_M
DELTA_T      = DELTA_T_FRAC * T_M
N_PULSES     = 30

DEBYE_WALLER = np.exp(-ETA ** 2 / 2)
OMEGA_EFF    = np.pi / (2 * N_PULSES * DELTA_T)
OMEGA_R      = OMEGA_EFF / DEBYE_WALLER

N_THETA0   = 64
N_PHI      = 64

MW_PHASE_DEG      = 0.0
INTRA_MOTION      = True
CENTER_PULSES     = True


def main():
    out_h5 = os.path.join(SCRIPT_DIR, 'fig6_alpha3_v4.h5')

    print(f"Hasse Fig 6 v4 — engine v{ss.CODE_VERSION}, centered convention:")
    print(f"  T_m={T_M:.3f}  δt={DELTA_T:.3f} ({DELTA_T_FRAC*100:.0f}% of T_m)")
    print(f"  N={N_PULSES}  Ω={OMEGA_R:.4f}  ω_m·δt={OMEGA_M*DELTA_T:.3f} rad")
    print(f"  mw_pi2_phase_deg={MW_PHASE_DEG}  intra_pulse_motion={INTRA_MOTION}  "
          f"center_pulses_at_phase={CENTER_PULSES}")
    print()

    theta0_grid = np.linspace(0.0, 2.0 * np.pi, N_THETA0, endpoint=False)
    phi_grid    = np.linspace(0.0, 2.0 * np.pi, N_PHI,    endpoint=False)

    sigma_z_map = np.zeros((N_THETA0, N_PHI))
    sigma_x_map = np.zeros((N_THETA0, N_PHI))
    sigma_y_map = np.zeros((N_THETA0, N_PHI))
    nbar_map    = np.zeros((N_THETA0, N_PHI))

    base = dict(
        alpha=ALPHA, eta=ETA, omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES, n_thermal=0.0, nmax=NMAX,
        det_min=0.0, det_max=0.0, npts=1,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0, T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_thermal_traj=1, n_rep=0,
        mw_pi2_phase_deg=MW_PHASE_DEG,
        intra_pulse_motion=INTRA_MOTION,
        delta_t_us=DELTA_T,
        center_pulses_at_phase=CENTER_PULSES,
    )

    t0 = time.time()
    for i, th0 in enumerate(theta0_grid):
        for j, ph in enumerate(phi_grid):
            p = dict(base,
                     alpha_phase_deg=float(np.degrees(th0)),
                     ac_phase_deg=float(np.degrees(ph)))
            d, _ = ss.run_single(p, verbose=False)
            sigma_z_map[i, j] = d['sigma_z'][0]
            sigma_x_map[i, j] = d['sigma_x'][0]
            sigma_y_map[i, j] = d['sigma_y'][0]
            nbar_map[i, j]    = d['nbar'][0]
        if (i + 1) % 8 == 0:
            print(f"  ϑ₀ {i+1}/{N_THETA0}  σ_z range "
                  f"[{sigma_z_map[i].min():+.3f}, {sigma_z_map[i].max():+.3f}]  "
                  f"⟨n⟩ range [{nbar_map[i].min():.2f}, {nbar_map[i].max():.2f}]",
                  flush=True)
    elapsed = time.time() - t0
    print(f"  done — {elapsed:.1f} s for {N_THETA0*N_PHI} runs")

    delta_n_map = nbar_map - ALPHA ** 2

    with h5py.File(out_h5, 'w') as f:
        f.create_dataset('theta0_rad', data=theta0_grid)
        f.create_dataset('phi_rad',    data=phi_grid)
        f.create_dataset('sigma_z_map', data=sigma_z_map)
        f.create_dataset('sigma_x_map', data=sigma_x_map)
        f.create_dataset('sigma_y_map', data=sigma_y_map)
        f.create_dataset('nbar_map',    data=nbar_map)
        f.create_dataset('delta_n_map', data=delta_n_map)
        f.attrs['alpha']      = ALPHA
        f.attrs['eta']        = ETA
        f.attrs['omega_m']    = OMEGA_M
        f.attrs['omega_r']    = OMEGA_R
        f.attrs['n_pulses']   = N_PULSES
        f.attrs['delta_t_us'] = DELTA_T
        f.attrs['delta_t_frac_Tm'] = DELTA_T_FRAC
        f.attrs['nmax']       = NMAX
        f.attrs['mw_pi2_phase_deg']     = MW_PHASE_DEG
        f.attrs['intra_pulse_motion']   = int(INTRA_MOTION)
        f.attrs['center_pulses_at_phase'] = int(CENTER_PULSES)
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('Round 4: Hasse-matched + centered pulses. '
                            'Compare against fig6_alpha3_v3.h5 (same Hasse-matched, '
                            'but center_pulses_at_phase=False).')

    # Amplitudes
    sz_range = (sigma_z_map.min(), sigma_z_map.max())
    dn_range = (delta_n_map.min(), delta_n_map.max())
    dn_phi_amp_at_th0  = (nbar_map[0].max()    - nbar_map[0].min())    / 2
    dn_th0_amp_at_phi0 = (nbar_map[:, 0].max() - nbar_map[:, 0].min()) / 2

    print(f"\n  σ_z map range:  [{sz_range[0]:+.3f}, {sz_range[1]:+.3f}]  (Hasse ±0.9)")
    print(f"  δ⟨n⟩ map range: [{dn_range[0]:+.3f}, {dn_range[1]:+.3f}]  (Hasse ±0.9)")
    print(f"  δ⟨n⟩ ϕ-amplitude at ϑ₀=0:   {dn_phi_amp_at_th0:.3f}")
    print(f"  δ⟨n⟩ ϑ₀-amplitude at ϕ=0:   {dn_th0_amp_at_phi0:.3f}")
    print(f"  amplitude ratio ϕ:ϑ₀ = {dn_phi_amp_at_th0/max(dn_th0_amp_at_phi0, 1e-12):.3f}")

    # Plotting helper (same layout as v3)
    def heatmap(map_arr, title, fname, cmap, ylabel, vlim_floor=0.9):
        cuts_theta = (np.pi/4, np.pi/2, np.pi)
        cuts_phi   = (np.pi/4, np.pi/2, np.pi)
        cut_styles = ('lightgray', 'dimgray', 'black')

        fig = plt.figure(figsize=(7.0, 5.5))
        gs  = fig.add_gridspec(2, 2, width_ratios=[1, 3], height_ratios=[3, 1],
                               hspace=0.30, wspace=0.30)
        vlim = max(vlim_floor, float(np.abs(map_arr).max()))
        ax_map = fig.add_subplot(gs[0, 1])
        im = ax_map.imshow(map_arr.T, origin='lower',
                           extent=[theta0_grid[0], theta0_grid[-1],
                                   phi_grid[0], phi_grid[-1]],
                           aspect='auto', cmap=cmap, vmin=-vlim, vmax=+vlim)
        ax_map.set_xlabel(r'$\vartheta_0$ (rad)')
        ax_map.set_ylabel(r'$\varphi_\mathrm{AC}$ (rad)')
        ax_map.set_xticks([0, np.pi, 2*np.pi]); ax_map.set_xticklabels(['0', r'$\pi$', r'$2\pi$'])
        ax_map.set_yticks([0, np.pi, 2*np.pi]); ax_map.set_yticklabels(['0', r'$\pi$', r'$2\pi$'])
        cb = fig.colorbar(im, ax=ax_map, shrink=0.85, pad=0.02); cb.set_label(ylabel)

        ax_bot = fig.add_subplot(gs[1, 1], sharex=ax_map)
        for ph_t, col in zip(cuts_phi, cut_styles):
            j = int(np.argmin(np.abs(phi_grid - ph_t)))
            ax_bot.plot(theta0_grid, map_arr[:, j], color=col,
                        label=fr'$\varphi={ph_t/np.pi:.2f}\pi$')
        ax_bot.set_xlabel(r'$\vartheta_0$ (rad)')
        ax_bot.set_ylabel(ylabel)
        ax_bot.set_ylim(-vlim*1.1, +vlim*1.1); ax_bot.axhline(0, color='k', lw=0.4)
        ax_bot.legend(loc='lower right', fontsize=7, framealpha=0.9)

        ax_left = fig.add_subplot(gs[0, 0], sharey=ax_map)
        for th_t, col in zip(cuts_theta, cut_styles):
            i = int(np.argmin(np.abs(theta0_grid - th_t)))
            ax_left.plot(map_arr[i, :], phi_grid, color=col,
                         label=fr'$\vartheta_0={th_t/np.pi:.2f}\pi$')
        ax_left.set_xlabel(ylabel)
        ax_left.set_xlim(+vlim*1.1, -vlim*1.1); ax_left.axvline(0, color='k', lw=0.4)
        ax_left.legend(loc='lower left', fontsize=7, framealpha=0.9)

        fig.suptitle(title, fontsize=10)
        out = os.path.join(PLOTS_DIR, fname)
        fig.savefig(out, dpi=140, bbox_inches='tight'); plt.close(fig)
        print(f"  wrote {out}")

    extras = (rf'N={N_PULSES}, $\delta t/T_m$={DELTA_T_FRAC:.2f}, '
              r'centered pulses')
    heatmap(sigma_z_map,
            f'Hasse Fig 6a v4 — engine v{ss.CODE_VERSION} ({extras})',
            'fig6a_sigma_z_v4.png',
            cmap='RdBu_r', ylabel=r'$\langle\sigma_z\rangle$', vlim_floor=0.9)
    heatmap(delta_n_map,
            f'Hasse Fig 6b v4 — engine v{ss.CODE_VERSION} ({extras})',
            'fig6b_back_action_v4.png',
            cmap='PRGn', ylabel=r'$\delta\langle n\rangle$', vlim_floor=0.9)


if __name__ == '__main__':
    main()
