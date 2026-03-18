#!/usr/bin/env python3
"""
export_hdf5.py — Convert adaptive-learner data → HDF5 for the Harbour numerics viewer.

Usage:
    # Single dataset
    export_learner(learner, alpha=3, outdir="data/alpha_3")

    # Batch all amplitudes
    export_all(learners_dict, outdir="data")

HDF5 layout (per file):
    /detuning    float64 (N,)   detuning in units of 2π ω_LF
    /sigma_x     float64 (N,)
    /sigma_y     float64 (N,)
    /sigma_z     float64 (N,)
    /entropy     float64 (N,)
    /coherence   float64 (N,)   √(σx² + σy² + σz²)

Root-group attributes:
    alpha, eta, omega_m, omega_rabi, omega_eff_carrier,
    n_thermal, aom_setup, contrast_x, contrast_y, contrast_z,
    n_points, export_version
"""

import json
import numpy as np
from pathlib import Path

try:
    import h5py
except ImportError:
    raise ImportError("h5py is required: pip install h5py")


# ── Default simulation parameters (override via kwargs) ──────
# v0.7: n_pulses corrected from 326 to 22 (1 per motional cycle)
DEFAULTS = dict(
    eta=0.397,
    omega_m=1.3,           # 2π MHz
    omega_rabi=0.300,      # 2π MHz
    n_thermal=0.001,
    aom_setup="fast",
    pulse_duration_us=0.04,
    duty_cycle=0.052,
    n_pulses=22,           # v0.7: corrected from 326
    strobo_pi2_us=17.0,
)


def export_learner(learner, alpha, outdir="data",
                   filename="detuning_scan.h5", **params):
    """
    Export a single adaptive-learner run to HDF5.

    Parameters
    ----------
    learner  : object with .data dict  {detuning: [σx, σy, σz, S]}
    alpha    : float, displacement amplitude
    outdir   : output directory (created if needed)
    filename : HDF5 filename
    **params : override any DEFAULTS key
    """
    cfg = {**DEFAULTS, **params}

    # ── Extract & sort ──────────────────────────────────────────
    data = learner.data
    xs = np.array(list(data.keys()))
    ys = np.array(list(data.values()))
    order = np.argsort(xs)
    xs, ys = xs[order], ys[order]

    sigma_x = ys[:, 0]
    sigma_y = ys[:, 1]
    sigma_z = ys[:, 2]
    entropy = ys[:, 3]
    coherence = np.sqrt(sigma_x**2 + sigma_y**2 + sigma_z**2)

    # ── Contrasts ───────────────────────────────────────────────
    cx = float((sigma_x.max() - sigma_x.min()) / 2)
    cy = float((sigma_y.max() - sigma_y.min()) / 2)
    cz = float((sigma_z.max() - sigma_z.min()) / 2)

    # ── Write HDF5 ──────────────────────────────────────────────
    outpath = Path(outdir)
    outpath.mkdir(parents=True, exist_ok=True)
    filepath = outpath / filename

    with h5py.File(filepath, 'w') as f:
        f.create_dataset('detuning',  data=xs,        dtype='float64')
        f.create_dataset('sigma_x',   data=sigma_x,   dtype='float64')
        f.create_dataset('sigma_y',   data=sigma_y,   dtype='float64')
        f.create_dataset('sigma_z',   data=sigma_z,   dtype='float64')
        f.create_dataset('entropy',   data=entropy,    dtype='float64')
        f.create_dataset('coherence', data=coherence,  dtype='float64')

        # Attributes
        f.attrs['alpha']             = float(alpha)
        f.attrs['n_mean']            = float(alpha)**2
        f.attrs['eta']               = cfg['eta']
        f.attrs['omega_m']           = cfg['omega_m']
        f.attrs['omega_rabi']        = cfg['omega_rabi']
        f.attrs['omega_eff_carrier'] = cfg['omega_rabi'] * np.exp(-cfg['eta']**2 / 2)
        f.attrs['n_thermal']         = cfg['n_thermal']
        f.attrs['aom_setup']         = cfg['aom_setup']
        f.attrs['contrast_x']        = cx
        f.attrs['contrast_y']        = cy
        f.attrs['contrast_z']        = cz
        f.attrs['n_points']          = len(xs)
        f.attrs['pulse_duration_us'] = cfg['pulse_duration_us']
        f.attrs['duty_cycle']        = cfg['duty_cycle']
        f.attrs['n_pulses']          = cfg['n_pulses']
        f.attrs['strobo_pi2_us']     = cfg['strobo_pi2_us']
        f.attrs['export_version']    = '0.7'

    print(f"  ✓  {filepath}  ({len(xs)} points, α={alpha}, C(σz)={cz:.2f})")
    return filepath


def export_all(learners, alphas=(0, 1, 3, 5), base_dir="data", **params):
    """
    Batch export.

    Parameters
    ----------
    learners : dict {alpha: learner} or list aligned with alphas
    alphas   : tuple of alpha values
    base_dir : root data directory
    """
    if isinstance(learners, dict):
        learners_list = [learners[a] for a in alphas]
    else:
        learners_list = learners

    paths = []
    for alpha, lrn in zip(alphas, learners_list):
        outdir = f"{base_dir}/alpha_{alpha}"
        p = export_learner(lrn, alpha, outdir=outdir, **params)
        paths.append(p)

    # ── Write / update manifest ─────────────────────────────────
    manifest = []
    for alpha, p in zip(alphas, paths):
        manifest.append({
            "alpha": int(alpha),
            "label": "Ground state" if alpha == 0 else f"⟨n⟩ = {int(alpha**2)}",
            "nbar": int(alpha**2),
            "path": str(p),
        })

    manifest_path = Path(base_dir) / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"  ✓  {manifest_path}")

    return paths


# ── CLI ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Usage:")
    print("  from export_hdf5 import export_learner, export_all")
    print("  export_learner(learner, alpha=3)")
    print("  export_all({0: l0, 1: l1, 3: l3, 5: l5})")
