#!/usr/bin/env python3
"""
run_fig6.py — Reproduce Hasse 2024 Fig 6 (panels a and b).

Scans alpha_phase_deg = ϑ₀ ∈ [0, 360°) at fixed |α| = 3, η = 0.397,
n_thermal = 0. Reads the engine's post-train (σ_x, σ_y, σ_z, nbar) at
zero detuning, then reconstructs the Hasse analysis-phase ϕ axis by
basis rotation:

    σ_z(ϕ, ϑ₀) = σ_x(ϑ₀) cos(ϕ) + σ_y(ϑ₀) sin(ϕ)
    δ⟨n⟩(ϑ₀)   = nbar(ϑ₀) − |α|²

The back-action δ⟨n⟩ does not depend on ϕ in the engine's frame (the
analysis-phase rotation is a measurement-basis choice and does not back-
react on the motional state). We tile it across ϕ for the heatmap.

Output: numerics/fig6_alpha3.h5
"""

import os
import sys
import time
from datetime import datetime, timezone
import numpy as np
import h5py

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts'))
sys.path.insert(0, ENGINE_DIR)
import stroboscopic_sweep as ss


ALPHA      = 3.0
ETA        = 0.397
OMEGA_M    = 1.3
OMEGA_R    = 0.3
N_PULSES   = 22       # engine's stroboscopic count (Hasse uses 30 flashes;
                      #   engine's N is the analysis-pulse count yielding π/2)
N_THERMAL  = 0.0
NMAX       = 50

N_THETA0   = 64       # ϑ₀ grid (Hasse Fig 6: 900 samples linearly interpolated)
N_PHI      = 64       # ϕ grid for Hasse axis reconstruction


def main():
    out_path = os.path.join(SCRIPT_DIR, 'fig6_alpha3.h5')

    theta0_grid = np.linspace(0.0, 2.0 * np.pi, N_THETA0, endpoint=False)
    phi_grid    = np.linspace(0.0, 2.0 * np.pi, N_PHI,    endpoint=False)

    sx = np.zeros(N_THETA0)
    sy = np.zeros(N_THETA0)
    sz = np.zeros(N_THETA0)
    nb = np.zeros(N_THETA0)

    base = dict(
        alpha=ALPHA, eta=ETA, omega_m=OMEGA_M, omega_r=OMEGA_R,
        n_pulses=N_PULSES, n_thermal=N_THERMAL, nmax=NMAX,
        det_min=0.0, det_max=0.0, npts=1,
        theta_deg=0.0, phi_deg=0.0,
        squeeze_r=0.0, squeeze_phi_deg=0.0,
        t_sep_factor=1.0,
        T1=0.0, T2=0.0, heating=0.0,
        n_traj=1, n_thermal_traj=1, n_rep=0,
    )

    t0 = time.time()
    for i, th0 in enumerate(theta0_grid):
        p = dict(base, alpha_phase_deg=float(np.degrees(th0)))
        d, conv = ss.run_single(p, verbose=False)
        sx[i] = d['sigma_x'][0]
        sy[i] = d['sigma_y'][0]
        sz[i] = d['sigma_z'][0]
        nb[i] = d['nbar'][0]
        if (i + 1) % 8 == 0:
            print(f"  ϑ₀ {i+1}/{N_THETA0}  σ_z={sz[i]:+.3f}  "
                  f"|C|={np.hypot(sx[i], sy[i]):.3f}  ⟨n⟩={nb[i]:.3f}  "
                  f"leak={conv['max_fock_leakage']:.1e}", flush=True)
    elapsed = time.time() - t0
    print(f"  done — {elapsed:.1f} s for {N_THETA0} runs")

    # Reconstruct (ϕ, ϑ₀) heatmaps
    SX, SY = np.meshgrid(sx, np.cos(phi_grid), indexing='ij')[0], None
    cos_phi = np.cos(phi_grid)[None, :]                 # (1, N_phi)
    sin_phi = np.sin(phi_grid)[None, :]
    sigma_z_map = sx[:, None] * cos_phi + sy[:, None] * sin_phi   # (ϑ₀, ϕ)

    # Back-action: δ⟨n⟩ does not depend on ϕ in the engine frame.
    delta_n_1d = nb - ALPHA ** 2
    delta_n_map = np.broadcast_to(delta_n_1d[:, None], (N_THETA0, N_PHI))

    with h5py.File(out_path, 'w') as f:
        f.create_dataset('theta0_rad', data=theta0_grid)
        f.create_dataset('phi_rad',    data=phi_grid)
        f.create_dataset('sigma_x_1d', data=sx)
        f.create_dataset('sigma_y_1d', data=sy)
        f.create_dataset('sigma_z_1d', data=sz)
        f.create_dataset('nbar_1d',    data=nb)
        f.create_dataset('sigma_z_map', data=sigma_z_map)   # (ϑ₀, ϕ)
        f.create_dataset('delta_n_map', data=delta_n_map)
        f.attrs['alpha']      = ALPHA
        f.attrs['eta']        = ETA
        f.attrs['omega_m']    = OMEGA_M
        f.attrs['omega_r']    = OMEGA_R
        f.attrs['n_pulses']   = N_PULSES
        f.attrs['n_thermal']  = N_THERMAL
        f.attrs['nmax']       = NMAX
        f.attrs['n_theta0']   = N_THETA0
        f.attrs['n_phi']      = N_PHI
        f.attrs['code_version'] = ss.CODE_VERSION
        f.attrs['datetime_utc'] = datetime.now(timezone.utc).isoformat()
        f.attrs['notes'] = ('σ_z(ϕ, ϑ₀) = σ_x cos ϕ + σ_y sin ϕ; '
                            'δ⟨n⟩ tiled over ϕ (basis-independent).')

    # Quick console summary
    sz_min, sz_max = sigma_z_map.min(), sigma_z_map.max()
    dn_min, dn_max = delta_n_map.min(), delta_n_map.max()
    contrast0 = np.hypot(sx, sy).max()
    print(f"  σ_z map range: [{sz_min:+.3f}, {sz_max:+.3f}] "
          f"(Hasse colour scale ≈ ±0.9)")
    print(f"  δ⟨n⟩ range:    [{dn_min:+.3f}, {dn_max:+.3f}] "
          f"(Hasse colour scale ≈ ±0.9)")
    print(f"  max |C|(ϑ₀):   {contrast0:.3f}")
    print(f"  written → {out_path}")


if __name__ == '__main__':
    main()
