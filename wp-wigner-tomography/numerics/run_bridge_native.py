"""WP-W D4 Layer A — native Raman convention check.

Per §4 D4 / §7#7. Two comparisons:

  1. **Engine-consistency check** (gated, 10⁻³ tolerance). Run the
     native `build_strobo_train` at the §7#7 anchor
     |α=3, θ_α=0⟩ at parameters matching WP-E's
     `wp-phase-contrast-maps/numerics/scan_2d_alpha3_v2.h5`
     (N=30, η=0.397, ω_m=1.3, ϑ_0 = 0). Extract (⟨σ_z⟩, Re C, Im C)
     at WP-E's three closest-to-tooth detuning grid points
     (δ/ω_m ≈ ±0.9923, 0). Compare to WP-E values at the same points.

  2. **Exact-anchor diagnostic** (NOT gated). Same engine, same
     state, evaluated at exactly δ/ω_m ∈ {−1, 0, +1}. WP-E doesn't
     have grid points there, so these values are reported as-is for
     downstream comparison once the WP-E grid is refined or a fresh
     reference run is generated.

**Spec deviation logged**: WP-W §4 D4 reads "N=22" (Hasse paper) but
the WP-E reference at this anchor uses N=30. Running at N=30 to
match WP-E directly. The §4 D4 wording will be reconciled in the
v0.5 doc pass.

Usage:
    python numerics/run_bridge_native.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import h5py
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from stroboscopic import HilbertSpace, build_strobo_train
from stroboscopic import operators as ops


WPE_REF = str(REPO / "wp-phase-contrast-maps" / "numerics" / "scan_2d_alpha3_v2.h5")


def run_native_at_detunings(*, hs, alpha: float, alpha_phase_deg: float,
                             eta: float, omega_r: float, omega_m: float,
                             delta_t: float, n_pulses: int,
                             detunings_rel: list[float],
                             C, Cdag) -> list[dict]:
    """Run native Raman engine at each detuning (relative to ω_m).

    Matches WP-E `run_2d_alpha3_v2.py` conventions exactly:
      - initial spin via `prepare_state(theta_deg=0, phi_deg=0)` (|↓⟩);
        the train itself accumulates the π/2 spin rotation through
        OMEGA_R calibration (no separate `apply_mw_pi2`).
      - motional phase carries the v0.9.1 pulse-centering shift
        `shift_deg = ω_m · δt / 2` so pulse #1 is centered on φ_α.
      - `intra_pulse_motion=True`, `gap_includes_spin_detuning=True`.

    χ readout convention: (Re C, Im C) ≡ (⟨σ_x⟩, ⟨σ_y⟩) — matches
    the WP-E HDF5 schema `C_abs = √(σ_x²+σ_y²)`, `C_arg = atan2(σ_y, σ_x)`.

    Returns list of dicts {det_rel, sigma_z, C_real, C_imag, C_abs, C_arg_deg}.
    """
    nmax = hs.nmax
    shift_deg = float(np.degrees(omega_m * delta_t / 2.0))
    psi_init = hs.prepare_state(
        spin={"theta_deg": 0.0, "phi_deg": 0.0},
        modes=[{"alpha": float(alpha),
                "alpha_phase_deg": float(alpha_phase_deg) + shift_deg}],
    )

    results = []
    for det_rel in detunings_rel:
        delta = float(det_rel) * omega_m
        train = build_strobo_train(
            hs=hs, eta=eta, omega_r=omega_r, omega_m=omega_m,
            delta=delta, n_pulses=int(n_pulses), delta_t=delta_t,
            t_sep_factor=1.0, ac_phase_rad=0.0,
            intra_pulse_motion=True, gap_includes_spin_detuning=True,
            C=C, Cdag=Cdag,
        )
        psi_out = train.evolve(psi_init)
        obs = hs.observables(psi_out)
        sx = float(obs["sigma_x"])
        sy = float(obs["sigma_y"])
        sz = float(obs["sigma_z"])
        C_complex = complex(sx, sy)
        results.append({
            "det_rel": float(det_rel),
            "sigma_z": sz,
            "sigma_x": sx,
            "sigma_y": sy,
            "C_real": float(C_complex.real),
            "C_imag": float(C_complex.imag),
            "C_abs": float(abs(C_complex)),
            "C_arg_deg": float(np.degrees(np.angle(C_complex))) if abs(C_complex) > 1e-12 else 0.0,
        })
    return results


def pull_wpe_reference(detunings_rel: list[float], phi_alpha_deg: float = 0.0) -> tuple[list[dict], dict]:
    """Read WP-E reference values at the nearest-grid points to detunings_rel.

    Returns (list_of_ref_dicts, meta) where meta documents any snap-to-grid
    discrepancies (per the D4 guardrail: don't silently interpolate).
    """
    with h5py.File(WPE_REF, "r") as f:
        det_rel_grid = f["detuning_rel"][:]
        phi_alpha_grid = f["phi_alpha_deg"][:]
        idx_phi = int(np.argmin(np.abs(phi_alpha_grid - float(phi_alpha_deg))))
        phi_actual = float(phi_alpha_grid[idx_phi])

        results = []
        snap_diffs = []
        for target in detunings_rel:
            idx = int(np.argmin(np.abs(det_rel_grid - float(target))))
            actual = float(det_rel_grid[idx])
            sz = float(f["sigma_z"][idx_phi, idx])
            sx = float(f["sigma_x"][idx_phi, idx])
            sy = float(f["sigma_y"][idx_phi, idx])
            results.append({
                "det_rel_target": float(target),
                "det_rel_actual": actual,
                "phi_alpha_deg_actual": phi_actual,
                "sigma_z": sz,
                "sigma_x": sx,
                "sigma_y": sy,
                "C_real": sx,
                "C_imag": sy,
                "C_abs": float(np.hypot(sx, sy)),
                "C_arg_deg": float(np.degrees(np.arctan2(sy, sx))) if (sx*sx + sy*sy) > 1e-24 else 0.0,
            })
            snap_diffs.append(abs(target - actual))

        meta = {
            "wpe_attrs": {k: (float(v) if isinstance(v, (np.floating, np.integer)) else (str(v) if not isinstance(v, (str, int, float)) else v))
                          for k, v in f.attrs.items()},
            "phi_alpha_target_deg": float(phi_alpha_deg),
            "phi_alpha_actual_deg": phi_actual,
            "snap_to_grid_max_offset": float(max(snap_diffs)),
            "det_rel_grid_step": float(det_rel_grid[1] - det_rel_grid[0]),
        }
    return results, meta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--alpha", type=float, default=3.0)
    parser.add_argument("--alpha-phase-deg", type=float, default=0.0)
    parser.add_argument("--output", type=str,
                        default="numerics/bridge_native.json")
    args = parser.parse_args()

    t0 = time.time()

    # Engine parameters matching wp-phase-contrast-maps/numerics/scan_2d_alpha3_v2.h5
    OMEGA_M = 1.3
    ETA = 0.397
    OMEGA_R = 0.09016606431708851  # WP-E reference value
    DELTA_T = 0.6283185307179586   # = 0.13 * T_m
    N_PULSES = 30                  # WP-E uses 30; WP-W §4 D4 said 22 (Hasse) — see header note
    NMAX = 60

    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX)
    Cdag = C.conj().T

    # ----- Comparison 1: nearest-grid (gated, 10⁻³) -----
    # WP-E grid step is 0.023 in δ/ω_m; closest to ±1, 0 are at ±0.9923, 0.
    DET_WPE = [-0.9923076923076923, 0.0, +0.9923076923076923]
    print("=" * 64)
    print("Comparison 1: native engine vs WP-E reference at WP-E grid points")
    print("  (gated at 10⁻³; engine-consistency check)")
    print("=" * 64)
    engine_at_wpe = run_native_at_detunings(
        hs=hs, alpha=args.alpha, alpha_phase_deg=args.alpha_phase_deg,
        eta=ETA, omega_r=OMEGA_R, omega_m=OMEGA_M, delta_t=DELTA_T,
        n_pulses=N_PULSES, detunings_rel=DET_WPE,
        C=C, Cdag=Cdag,
    )
    wpe_ref, wpe_meta = pull_wpe_reference(DET_WPE, phi_alpha_deg=args.alpha_phase_deg)

    print(f"\nWP-E reference φ_α target = {args.alpha_phase_deg}°; "
          f"actual = {wpe_meta['phi_alpha_actual_deg']:.4f}°")
    print(f"Snap-to-grid max offset on δ/ω_m: {wpe_meta['snap_to_grid_max_offset']:.6f} "
          f"(grid step = {wpe_meta['det_rel_grid_step']:.6f})")
    print()

    consistency_residuals = []
    print(f"{'δ/ω_m':>10}  {'sigma_z':>22}  {'Re C':>22}  {'Im C':>22}")
    print(f"{'(target)':>10}  {'(engine, ref, |Δ|)':>22}  {'(engine, ref, |Δ|)':>22}  {'(engine, ref, |Δ|)':>22}")
    layer_a_pass = True
    for eng, ref in zip(engine_at_wpe, wpe_ref):
        dsz = abs(eng["sigma_z"] - ref["sigma_z"])
        dCr = abs(eng["C_real"] - ref["C_real"])
        dCi = abs(eng["C_imag"] - ref["C_imag"])
        print(f"{eng['det_rel']:>+10.4f}  "
              f"{eng['sigma_z']:>+7.4f}/{ref['sigma_z']:>+7.4f}/{dsz:.2e}  "
              f"{eng['C_real']:>+7.4f}/{ref['C_real']:>+7.4f}/{dCr:.2e}  "
              f"{eng['C_imag']:>+7.4f}/{ref['C_imag']:>+7.4f}/{dCi:.2e}")
        consistency_residuals.append({
            "det_rel": eng["det_rel"],
            "sigma_z_residual": float(dsz),
            "C_real_residual": float(dCr),
            "C_imag_residual": float(dCi),
            "max_residual": float(max(dsz, dCr, dCi)),
        })
        if max(dsz, dCr, dCi) >= 1e-3:
            layer_a_pass = False

    print(f"\nLayer A engine-consistency PASS @ 10⁻³: {layer_a_pass}")
    max_res = max(r["max_residual"] for r in consistency_residuals)
    print(f"  max residual = {max_res:.2e}")

    # ----- Comparison 2: exact tooth centres (diagnostic, no reference) -----
    DET_EXACT = [-1.0, 0.0, +1.0]
    print()
    print("=" * 64)
    print("Comparison 2: native engine at EXACT tooth centres δ/ω_m ∈ {-1, 0, +1}")
    print("  (diagnostic only; WP-E grid has no exact-tooth points)")
    print("=" * 64)
    engine_at_exact = run_native_at_detunings(
        hs=hs, alpha=args.alpha, alpha_phase_deg=args.alpha_phase_deg,
        eta=ETA, omega_r=OMEGA_R, omega_m=OMEGA_M, delta_t=DELTA_T,
        n_pulses=N_PULSES, detunings_rel=DET_EXACT,
        C=C, Cdag=Cdag,
    )
    print(f"{'δ/ω_m':>8}  {'sigma_z':>10}  {'Re C':>10}  {'Im C':>10}  {'|C|':>8}  {'arg C (°)':>10}")
    for eng in engine_at_exact:
        print(f"{eng['det_rel']:>+8.4f}  "
              f"{eng['sigma_z']:>+10.4f}  {eng['C_real']:>+10.4f}  {eng['C_imag']:>+10.4f}  "
              f"{eng['C_abs']:>8.4f}  {eng['C_arg_deg']:>+10.4f}")

    elapsed = time.time() - t0
    print()
    print("=" * 64)
    print(f"Wall time: {elapsed:.2f} s")

    # ----- Convention alignment notes (per guardrail) -----
    convention_notes = {
        "engine_version": str(wpe_meta["wpe_attrs"].get("code_version", "?")),
        "wpe_attrs_subset": {
            k: wpe_meta["wpe_attrs"][k] for k in ["alpha", "eta", "omega_m", "omega_r",
                                                   "delta_t_us", "n_pulses", "nmax",
                                                   "convention", "code_version"]
            if k in wpe_meta["wpe_attrs"]
        },
        "wpw_d4_spec_deviation": (
            "WP-W §4 D4 reads N=22 (Hasse paper). WP-E scan_2d_alpha3_v2.h5 "
            "is at N=30. Ran at N=30 to match WP-E. §4 D4 wording will be "
            "reconciled in the v0.5 doc pass."
        ),
        "mw_pi2_phase_alignment": (
            "WP-E does NOT apply a separate MW π/2 pulse. Initial spin is "
            "|↓⟩ via prepare_state(theta_deg=0, phi_deg=0); the train itself "
            "accumulates the π/2 spin rotation through the OMEGA_R "
            "calibration (OMEGA_EFF = π/(2·N·δt)). The first attempt at "
            "Layer A applied apply_mw_pi2 before the train (residuals ≈ 1.3) "
            "— removing it and using WP-E's prepare_state convention is what "
            "aligns the two engines. Logged per the D4 guardrail."
        ),
        "pulse_centering_alignment": (
            "WP-E v0.9.1 applies shift_deg = ω_m·δt/2 to alpha_phase_deg so "
            "pulse #1 is centered on the requested φ_α. This runner adopts "
            "the same shift_deg compensation."
        ),
        "train_flags": (
            "intra_pulse_motion=True, gap_includes_spin_detuning=True, "
            "t_sep_factor=1.0, ac_phase_rad=0.0 — matched to "
            "run_2d_alpha3_v2.py."
        ),
        "comparison_1_label": "nearest-grid diagnostic (per D4 guardrail); "
                              "gated at 10⁻³ as engine-consistency check",
        "comparison_2_label": "exact-anchor diagnostic; no reference available",
    }

    # Write output JSON
    output = {
        "engine_parameters": {
            "alpha": args.alpha,
            "alpha_phase_deg": args.alpha_phase_deg,
            "eta": ETA,
            "omega_m": OMEGA_M,
            "omega_r": OMEGA_R,
            "delta_t": DELTA_T,
            "n_pulses": N_PULSES,
            "nmax": NMAX,
        },
        "comparison_1_nearest_grid": {
            "label": "native engine vs WP-E nearest-grid",
            "wpe_reference_file": WPE_REF,
            "wpe_meta": wpe_meta,
            "detunings_rel": DET_WPE,
            "engine": engine_at_wpe,
            "reference": wpe_ref,
            "residuals": consistency_residuals,
            "max_residual": max_res,
            "pass_threshold": 1e-3,
            "pass": bool(layer_a_pass),
        },
        "comparison_2_exact_tooth_centres": {
            "label": "native engine at exact teeth (diagnostic)",
            "detunings_rel": DET_EXACT,
            "engine": engine_at_exact,
            "note": "no reference available; report-only",
        },
        "convention_alignment": convention_notes,
        "elapsed_s": elapsed,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {output_path}")
    return 0 if layer_a_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
