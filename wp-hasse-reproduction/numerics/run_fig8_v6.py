#!/usr/bin/env python3
"""
run_fig8_v6.py — Hasse Fig 8 via analysis-phase scan (experimental protocol).

Per Hasse Fig 2(b), Fig 3(b, c), Fig 4 captions: the experimental
"contrast C" is the amplitude of the Ramsey fringe in P_↓ (equivalently
⟨σ_z⟩) as the AC analysis-pulse phase ϕ is scanned at fixed δ=0.
Fig 8b plots this contrast as a function of |α|.

For each (|α|, tilt) we scan ac_phase_deg ∈ [0°, 360°) at fixed δ=0,
record σ_z at end of train, and compute:

    contrast = (max_ϕ σ_z − min_ϕ σ_z) / 2
    phi_0    = argmax_ϕ σ_z   (peak phase — encodes position)

Engine config (v0.9.1, Hasse fast-AOM regime):
    N=22, δt auto from π/2 budget, intra_pulse_motion + centered + MW π/2.
    Ω/(2π)=0.3 MHz, ω_m/(2π)=1.3 MHz, η=0.397, n_th=0.15 (Fig 8 caption).

Output: numerics/fig8_calibrations_v6.h5
        plots/fig8a_position_v6.png (|α| vs phi_0)
        plots/fig8b_contrast_v6.png (|α| vs contrast)
        plots/fig8_phase_scans_v6.png (σ_z(ϕ) curves family overlay)
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
OMEGA_R     = 0.3               # Hasse Table II
N_PULSES    = 22                # fast-AOM regime
N_THERMAL   = 0.15              # Hasse Fig 8 caption
N_TH_TRAJ   = 24

N_PHI       = 32                # AC analysis-phase scan points


def nmax_for_alpha(alpha):
    a = float(alpha)
    if a <= 1.0: return 30
    if a <= 3.0: return 60
    if a <= 5.0: return 100
    return 140


THETA0_DEG = 90.0   # ϑ₀ = π/2 — momentum extremum (Hasse Fig 8b condition)


def run_phase_scan(alpha, eta):
    """Returns sigma_z(ϕ) array of shape (N_PHI,) at end of train, δ=0."""
    phi_grid = np.linspace(0.0, 360.0, N_PHI, endpoint=False)
    sz = np.zeros(N_PHI)
    sx = np.zeros(N_PHI)
    sy = np.zeros(N_PHI)
    leak = 0.0
    base = dict(
        alpha=float(alpha), alpha_phase_deg=THETA0_DEG,   # ϑ_0 = π/2 (momentum max)
        eta=float(eta), omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES, n_thermal=N_THERMAL, n_thermal_traj=N_TH_TRAJ,
        nmax=nmax_for_alpha(alpha),
        det_min=0.0, det_max=0.0, npts=1,             # δ fixed at 0
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0, T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_rep=0,
        mw_pi2_phase_deg=0.0,
        intra_pulse_motion=True,
        center_pulses_at_phase=True,
    )
    for k, phi in enumerate(phi_grid):
        p = dict(base, ac_phase_deg=float(phi))
        d, conv = ss.run_single(p, verbose=False)
        sz[k] = d['sigma_z'][0]
        sx[k] = d['sigma_x'][0]
        sy[k] = d['sigma_y'][0]
        leak = max(leak, conv['max_fock_leakage'])
    return sx, sy, sz, phi_grid, leak


def main():
    out_path = os.path.join(SCRIPT_DIR, 'fig8_calibrations_v6.h5')
    n_a, n_t = len(ALPHA_GRID), len(TILT_DEG)

    print(f"Hasse Fig 8 v6 — analysis-phase scan (engine v{ss.CODE_VERSION})")
    print(f"  Ω/(2π)={OMEGA_R:.3f} MHz, ω_m/(2π)={OMEGA_M:.3f} MHz, η={ETA_LF:.3f}")
    print(f"  N={N_PULSES}, fast-AOM regime, n_th={N_THERMAL}")
    print(f"  phase scan: {N_PHI} points over [0, 360°), δ=0 fixed")
    print(f"  ϑ₀ = {THETA0_DEG}°  (momentum extremum if 90°, position extremum if 0°)")
    print(f"  CONTRAST = (max_ϕ σ_z − min_ϕ σ_z)/2   — Hasse experimental protocol")
    print()

    sz_full = np.zeros((n_t, n_a, N_PHI))
    sx_full = np.zeros((n_t, n_a, N_PHI))
    sy_full = np.zeros((n_t, n_a, N_PHI))
    contrast = np.zeros((n_t, n_a))
    phi0     = np.zeros((n_t, n_a))
    leak     = np.zeros((n_t, n_a))

    t0 = time.time()
    phi_grid = None
    for j, tilt in enumerate(TILT_DEG):
        eta_j = ETA_LF * np.cos(np.radians(tilt))
        print(f"=== tilt {tilt:+.0f}°  η={eta_j:.4f} ===")
        for i, a in enumerate(ALPHA_GRID):
            sx, sy, sz, phig, lk = run_phase_scan(a, eta_j)
            phi_grid = phig
            sx_full[j, i] = sx; sy_full[j, i] = sy; sz_full[j, i] = sz
            leak[j, i] = lk
            contrast[j, i] = 0.5 * (sz.max() - sz.min())
            # phi_0 = argmax via sinusoid fit: fit σ_z(ϕ) = A cos(ϕ − phi_0) + offset
            # robust estimate via complex-valued Fourier-1 component:
            z = sz - sz.mean()
            F1 = np.sum(z * np.exp(-1j * np.radians(phig)))
            phi0[j, i] = np.degrees(np.angle(F1))  # -180..+180 deg
            print(f"  |α|={a:4.1f}  contrast={contrast[j,i]:.4f}  "
                  f"phi_0={phi0[j,i]:+7.2f}°  leak={lk:.1e}", flush=True)
    elapsed = time.time() - t0
    print(f"\n  total {elapsed:.1f} s for {n_t}×{n_a}×{N_PHI} = {n_t*n_a*N_PHI} phase points")

    # Unwrap phi_0 along |α| axis for smooth calibration curves
    phi0_rad = np.radians(phi0)
    phi0_unwrap_rad = np.unwrap(phi0_rad, axis=1)
    phi0_unwrap_rad -= phi0_unwrap_rad[:, :1]     # ref at α=0

    contrast_norm = contrast / np.maximum(contrast[:, :1], 1e-12)

    with h5py.File(out_path, 'w') as f:
        f.create_dataset('alpha',          data=ALPHA_GRID)
        f.create_dataset('tilt_deg',       data=np.array(TILT_DEG))
        f.create_dataset('phi_grid_deg',   data=phi_grid)
        f.create_dataset('sigma_x',        data=sx_full)
        f.create_dataset('sigma_y',        data=sy_full)
        f.create_dataset('sigma_z',        data=sz_full)
        f.create_dataset('contrast',       data=contrast)
        f.create_dataset('contrast_norm',  data=contrast_norm)
        f.create_dataset('phi_0_deg',      data=phi0)
        f.create_dataset('phi_0_unwrap_rad', data=phi0_unwrap_rad)
        f.create_dataset('max_fock_leakage',data=leak)
        f.attrs['eta_LF']    = ETA_LF
        f.attrs['omega_m']   = OMEGA_M
        f.attrs['omega_r']   = OMEGA_R
        f.attrs['n_pulses']  = N_PULSES
        f.attrs['n_thermal'] = N_THERMAL
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('Hasse Fig 8 v6 — contrast and phi_0 from '
                            'ac_phase analysis-phase scan at fixed δ=0. '
                            'Engine v0.9.1 + Hasse fast-AOM regime + centered pulses.')

    TILT_COLORS = {-5.0: 'tab:green', 0.0: 'tab:blue', +5.0: 'tab:orange'}

    # Fig 8a: |α| vs phi_0
    fig, ax = plt.subplots(figsize=(5.4, 4.2))
    for j, tilt in enumerate(TILT_DEG):
        c = TILT_COLORS.get(float(tilt), 'k')
        ax.plot(phi0_unwrap_rad[j], ALPHA_GRID, marker='o', ms=3, color=c,
                label=fr'tilt {tilt:+.0f}°  ($\eta={ETA_LF*np.cos(np.radians(tilt)):.4f}$)')
    ax.axhline(0, color='k', lw=0.3); ax.axvline(0, color='k', lw=0.3)
    ax.set_xlabel(r'$\varphi_0$ (rad, unwrapped, ref at $\alpha=0$)')
    ax.set_ylabel(r'$|\alpha|$')
    ax.set_xlim(-2*np.pi, +2*np.pi)
    ax.set_xticks([-2*np.pi, -np.pi, 0, np.pi, 2*np.pi])
    ax.set_xticklabels([r'$-2\pi$', r'$-\pi$', '0', r'$\pi$', r'$2\pi$'])
    ax.set_ylim(0, ALPHA_GRID.max() * 1.05)
    ax.legend(fontsize=8)
    ax.set_title(f'Hasse Fig 8a v6 — position calibration '
                 r'($n_\mathrm{th}$=0.15, phase-scan)', fontsize=9)
    out = os.path.join(PLOTS_DIR, 'fig8a_position_v6.png')
    fig.tight_layout(); fig.savefig(out, dpi=140); plt.close(fig)
    print(f"  wrote {out}")

    # Fig 8b: |α| vs contrast
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), constrained_layout=True)
    ax = axs[0]
    for j, tilt in enumerate(TILT_DEG):
        c = TILT_COLORS.get(float(tilt), 'k')
        ax.plot(contrast[j], ALPHA_GRID, marker='o', ms=3, color=c,
                label=fr'tilt {tilt:+.0f}°')
    ax.set_xlabel(r'contrast $(\max_\varphi - \min_\varphi)\sigma_z / 2$')
    ax.set_ylabel(r'$|\alpha|$'); ax.set_xlim(-0.02, 1.10); ax.set_ylim(0, 8.2)
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    ax.set_title('raw contrast', fontsize=10)

    ax = axs[1]
    for j, tilt in enumerate(TILT_DEG):
        c = TILT_COLORS.get(float(tilt), 'k')
        ax.plot(contrast_norm[j], ALPHA_GRID, marker='o', ms=3, color=c,
                label=fr'tilt {tilt:+.0f}°')
    ax.set_xlabel(r'contrast $/$ contrast$(\alpha=0)$')
    ax.set_ylabel(r'$|\alpha|$'); ax.set_xlim(-0.02, 1.10); ax.set_ylim(0, 8.2)
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    ax.set_title('normalised (direct comparison to Hasse Fig 8b)', fontsize=10)

    fig.suptitle(f'Hasse Fig 8b v6 — momentum calibration via phase scan '
                 f'(engine v{ss.CODE_VERSION}, n_th=0.15)', fontsize=10)
    out = os.path.join(PLOTS_DIR, 'fig8b_contrast_v6.png')
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")

    # Companion: σ_z(ϕ) fringes at a few α values (tilt=0) to show the raw data
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    cmap = plt.get_cmap('viridis')
    alpha_picks = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)
    for k, ap in enumerate(alpha_picks):
        i = int(np.argmin(np.abs(ALPHA_GRID - ap)))
        ax.plot(phi_grid, sz_full[1, i],                # tilt=0° is index 1
                color=cmap(k/(len(alpha_picks)-1)),
                marker='o', ms=3, label=fr'$|\alpha|={ALPHA_GRID[i]:.1f}$')
    ax.set_xlabel(r'analysis phase $\varphi$ (deg)')
    ax.set_ylabel(r'$\langle\sigma_z\rangle$ at end of train, $\delta=0$')
    ax.axhline(0, color='k', lw=0.3)
    ax.grid(alpha=0.3); ax.legend(fontsize=7, loc='upper right', ncol=2)
    ax.set_title(r'Ramsey fringes $\sigma_z(\varphi)$ at tilt 0°, family by $|\alpha|$',
                 fontsize=10)
    out = os.path.join(PLOTS_DIR, 'fig8_phase_scans_v6.png')
    fig.tight_layout(); fig.savefig(out, dpi=140); plt.close(fig)
    print(f"  wrote {out}")

    # Summary
    print()
    print("Hasse anchor: contrast(α=0) ≈ 1, contrast(α=8) → 0 (smooth decay)")
    for j, tilt in enumerate(TILT_DEG):
        flips = int(np.sum(np.diff(np.sign(np.diff(contrast[j]))) != 0))
        print(f"  tilt {tilt:+.0f}°: contrast(α=0)={contrast[j,0]:.4f}  "
              f"contrast(α=8)={contrast[j,-1]:.4f}  "
              f"norm(α=8)={contrast_norm[j,-1]:.3f}  flips={flips}")


if __name__ == '__main__':
    main()
