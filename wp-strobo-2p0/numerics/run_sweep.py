#!/usr/bin/env python3
"""strobo 2.0 main sweep.

For each (train, alpha), sweep (detuning, motional phase theta_0) on a
81 x 64 grid, with two runs per cell (init |+x> and |+y>) to extract the
Hasse-style coherence contrast |C| = sqrt(a_x^2 + a_y^2) and arg C.

Outputs to numerics/strobo2p0_data.npz and numerics/strobo2p0_manifest.json.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from stroboscopic_sweep import run_single, CODE_VERSION  # noqa: E402

# ─────────── physical parameters ───────────
OMEGA_M_MHZ = 1.306
ETA = 0.395
DELTA_T_US = 0.77
T_M_US = 1.0 / OMEGA_M_MHZ
T_SEP_FACTOR = DELTA_T_US / T_M_US
NMAX = 60

# Debye-Waller factor used by the pi/2 calibration.
_DW = float(np.exp(-ETA ** 2 / 2))


def omega_for_pi2(n_pulses: int, delta_t_pulse_us: float) -> float:
    """Bare Omega/(2pi) [MHz] such that N*Omega*DW*dt = pi/2."""
    return 1.0 / (4.0 * n_pulses * delta_t_pulse_us * _DW)


# ─────────── scan grid ───────────
DET_MHZ_MIN = -10.0
DET_MHZ_MAX = +10.0
N_DET = 81
N_THETA = 64

DET_MHZ = np.linspace(DET_MHZ_MIN, DET_MHZ_MAX, N_DET)
THETA0_DEG = np.linspace(0.0, 360.0, N_THETA, endpoint=False)

ALPHAS = [1.0, 3.0, 4.5]
TRAINS = [
    {"label": "T1", "n_pulses": 3, "delta_t_pulse_us": 0.100},
    {"label": "T2", "n_pulses": 7, "delta_t_pulse_us": 0.050},
]
# Pre-compute per-train Omega to hit a pi/2 analysis rotation.
for _t in TRAINS:
    _t["omega_r_MHz"] = omega_for_pi2(_t["n_pulses"], _t["delta_t_pulse_us"])


def base_params(
    n_pulses: int, delta_t_pulse_us: float, alpha: float, omega_r_MHz: float
) -> dict:
    return dict(
        alpha=alpha,
        eta=ETA,
        omega_m=2 * np.pi * OMEGA_M_MHZ,
        omega_r=2 * np.pi * omega_r_MHz,
        nmax=NMAX,
        theta_deg=90.0,
        phi_deg=0.0,
        alpha_phase_deg=0.0,
        # detuning is in units of omega_m (engine convention)
        det_min=DET_MHZ_MIN / OMEGA_M_MHZ,
        det_max=DET_MHZ_MAX / OMEGA_M_MHZ,
        npts=N_DET,
        n_pulses=n_pulses,
        delta_t_us=delta_t_pulse_us,
        t_sep_factor=T_SEP_FACTOR,
        intra_pulse_motion=True,
        ac_phase_deg=0.0,
        mw_pi2_phase_deg=None,
    )


def run_one_sheet(
    n_pulses: int, delta_t_pulse_us: float, alpha: float, omega_r_MHz: float
) -> dict:
    """Run a (theta_0, detuning) sheet for one (train, alpha). Two runs per cell."""
    sz_A = np.zeros((N_THETA, N_DET))
    sz_B = np.zeros((N_THETA, N_DET))
    nbar_A = np.zeros((N_THETA, N_DET))
    nbar_B = np.zeros((N_THETA, N_DET))
    sx_A = np.zeros((N_THETA, N_DET))
    sy_A = np.zeros((N_THETA, N_DET))

    base = base_params(n_pulses, delta_t_pulse_us, alpha, omega_r_MHz)

    t0 = time.time()
    for i, theta0 in enumerate(THETA0_DEG):
        p_A = dict(base)
        p_A["alpha_phase_deg"] = float(theta0)
        p_A["phi_deg"] = 0.0         # spin |+x>
        d_A, conv_A = run_single(p_A, verbose=False)

        p_B = dict(p_A)
        p_B["phi_deg"] = 90.0        # spin |+y>
        d_B, conv_B = run_single(p_B, verbose=False)

        sz_A[i] = d_A["sigma_z"]
        sz_B[i] = d_B["sigma_z"]
        nbar_A[i] = d_A["nbar"]
        nbar_B[i] = d_B["nbar"]
        sx_A[i] = d_A["sigma_x"]
        sy_A[i] = d_A["sigma_y"]

        if (i + 1) % 8 == 0:
            elapsed = time.time() - t0
            pct = (i + 1) / N_THETA * 100
            eta = elapsed * (N_THETA - i - 1) / (i + 1)
            print(f"    theta_0 {i + 1:2d}/{N_THETA}  ({pct:4.1f} %)   "
                  f"elapsed {elapsed:5.1f}s   ETA {eta:5.1f}s", flush=True)

    return dict(
        sz_A=sz_A, sz_B=sz_B, nbar_A=nbar_A, nbar_B=nbar_B,
        sx_A=sx_A, sy_A=sy_A,
    )


def main() -> None:
    print("strobo 2.0 main sweep (pi/2-calibrated, v0.3)")
    print(f"  omega_m/(2pi) = {OMEGA_M_MHZ} MHz   eta = {ETA}")
    print(f"  Delta t       = {DELTA_T_US} us     t_sep_factor = {T_SEP_FACTOR:.5f}")
    print(f"  Nmax          = {NMAX}")
    for t in TRAINS:
        theta_pulse = 2 * np.pi * t["omega_r_MHz"] * _DW * t["delta_t_pulse_us"]
        print(f"  {t['label']}: N={t['n_pulses']}, dt={t['delta_t_pulse_us']*1e3:.0f} ns  ->  "
              f"Omega/(2pi) = {t['omega_r_MHz']:.4f} MHz,  theta_pulse = {theta_pulse:.4f} rad,  "
              f"N*theta = {t['n_pulses']*theta_pulse:.4f} rad (target pi/2 = {np.pi/2:.4f})")
    print(f"  Grid          = {N_DET} detunings x {N_THETA} theta_0  x {len(ALPHAS)} alpha x {len(TRAINS)} trains")
    print(f"  Grid cells    = {N_DET * N_THETA * len(ALPHAS) * len(TRAINS)}")
    print(f"  Engine calls  = {N_THETA * len(ALPHAS) * len(TRAINS) * 2}  "
          f"(2 initial-spin runs per (theta_0, alpha, train); each sweeps {N_DET} detunings internally)")

    out: dict = {}
    out_keys: list[str] = []
    t_total = time.time()

    for train in TRAINS:
        for alpha in ALPHAS:
            tag = f"{train['label']}_alpha{alpha:g}".replace(".", "p")
            print(f"\n[{tag}] N={train['n_pulses']}  dt={train['delta_t_pulse_us']*1e3:.0f} ns  "
                  f"|alpha|={alpha}  Omega/(2pi)={train['omega_r_MHz']:.4f} MHz")
            sheet = run_one_sheet(
                train["n_pulses"], train["delta_t_pulse_us"], alpha,
                train["omega_r_MHz"],
            )
            for k, v in sheet.items():
                out[f"{tag}_{k}"] = v
            out_keys.append(tag)

    out["DET_MHZ"] = DET_MHZ
    out["THETA0_DEG"] = THETA0_DEG
    out["ALPHAS"] = np.array(ALPHAS)

    elapsed_total = time.time() - t_total

    out_path = Path(__file__).parent / "strobo2p0_data.npz"
    np.savez_compressed(out_path, **out)
    print(f"\nSaved: {out_path}  ({out_path.stat().st_size / 1024:.0f} KB)")

    manifest = {
        "code_version_engine": CODE_VERSION,
        "runner_version": "0.3",
        "calibration": "pi/2 per-train: N*Omega*exp(-eta^2/2)*dt = pi/2",
        "physical_parameters": {
            "omega_m_MHz": OMEGA_M_MHZ,
            "eta": ETA,
            "Delta_t_us": DELTA_T_US,
            "T_m_us": T_M_US,
            "t_sep_factor": T_SEP_FACTOR,
            "N_max_fock": NMAX,
        },
        "grid": {
            "detuning_MHz_min": DET_MHZ_MIN,
            "detuning_MHz_max": DET_MHZ_MAX,
            "n_detuning": N_DET,
            "n_theta0": N_THETA,
            "theta0_range_deg": [0.0, 360.0],
            "alphas": ALPHAS,
            "trains": [{"label": t["label"], "n_pulses": t["n_pulses"],
                        "delta_t_pulse_us": t["delta_t_pulse_us"],
                        "omega_r_MHz": t["omega_r_MHz"]} for t in TRAINS],
        },
        "observables_per_cell": {
            "sz_A": "sigma_z after train, init spin |+x>",
            "sz_B": "sigma_z after train, init spin |+y>",
            "nbar_A": "<n> after train, init spin |+x>",
            "nbar_B": "<n> after train, init spin |+y>",
            "sx_A": "sigma_x after train, init spin |+x> (diagnostic)",
            "sy_A": "sigma_y after train, init spin |+x> (diagnostic)",
        },
        "derived_observables": {
            "|C|": "sqrt(sz_A^2 + sz_B^2)  (Hasse coherence contrast)",
            "arg_C": "atan2(sz_B, sz_A)  (AC phase that maximises sigma_z)",
            "sigma_z": "sz_A  (readout at canonical analysis phase phi=0)",
            "delta_n": "nbar_A - alpha^2  (back-action at phi=0)",
            "delta_n_pi2": "nbar_B - alpha^2  (back-action at phi=pi/2)",
        },
        "tags": out_keys,
        "elapsed_s": round(elapsed_total, 2),
    }
    manifest_path = Path(__file__).parent / "strobo2p0_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Saved: {manifest_path}")
    print(f"\nTotal wall time: {elapsed_total:.1f} s")


if __name__ == "__main__":
    main()
