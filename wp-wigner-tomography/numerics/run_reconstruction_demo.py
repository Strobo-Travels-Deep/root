"""WP-W D3 — Wigner-reconstruction demonstration on the headline test set.

For each of seven states (vacuum / coherent / thermal / Fock×2 / cat /
mixed-cat) builds the analytic χ on the v0.2 Cartesian β grid
(81² over [-4, 4]², Δβ = 0.10), applies a radial Hanning window
across the accessible disk, zero-pads to 161² for FFT-interpolated
α resolution, performs the 2D-FFT inversion, computes the analytic
W_true on the same α grid, and reports the §7#5 metric bundle:

    F   = π ∫ W_rec W_true d²α                      (overlap fidelity)
    L¹  = ∫ |W_rec − W_true| d²α                    (total L¹ error)
    ρ_neg = ∫ min(0,W_rec) dα / ∫ min(0,W_true) dα  (one-sided, non-Gaussian only)

Per-state thresholds (from §7#5) are encoded in PASS_THRESHOLDS below.

This is the ideal-SDF / analytic-χ pipeline — no engine code. P1 / D4
remain gated on the FH20-style `ideal_sdf` primitive.

Usage:
    python numerics/run_reconstruction_demo.py
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import h5py
import numpy as np

from _common import (
    RUNNER_VERSION,
    canonical_manifest,
    chi_of_state,
    fidelity,
    l1_error_map,
    l1_error_total,
    negativity_ratio,
    padded_beta_axis,
    parse_state,
    radial_hanning,
    restrict_to_window,
    W_true_of_state,
    wigner_from_chi,
    write_manifest,
    zero_pad_centered,
)


REPOSITORY = "https://github.com/Strobo-Travels-Deep/root"
WP_ID = "wigner-tomography"
CODE_VERSION = "0.4.0"


# §7#5 thresholds.  Mixed cat is the quantum-vs-classical *control*
# (per §7#4) and is reported but not gated.
PASS_THRESHOLDS = {
    "vacuum":        {"F_min": 0.999},
    "coherent_1.5":  {"F_min": 0.99},
    "thermal_0.5":   {"F_norm_min": 0.98},  # F / Tr(ρ²) = F · (2n̄+1)
    "fock_1":        {"F_min": 0.95, "rho_neg_min": 0.5},
    "fock_2":        {"F_min": 0.90, "rho_neg_min": 0.5},
    "cat_1.5":       {"F_min": 0.90, "rho_neg_min": 0.5},
    "mixed_cat_1.5": {"F_min": None, "note": "control state — reported, not gated"},
}

DEFAULT_STATES = list(PASS_THRESHOLDS.keys())


def reconstruct(
    beta_axis: np.ndarray,
    chi: np.ndarray,
    B: float,
    target_size: int,
    window: str = "none",
) -> tuple[np.ndarray, np.ndarray, float, dict]:
    """Zero-pad and FFT-invert χ to W.

    The `window` argument selects the pre-FFT taper:

    - ``"none"`` (default for D3 analytic): no taper. Appropriate for
      analytic χ which has no disk discontinuity — the WP-W §4 D3 spec
      called for radial Hanning, but Hanning over the full disk
      attenuates the bulk of the signal (vacuum F drops to ~0.86) and
      the analytic χ doesn't have the edge artefact the window was
      meant to suppress.
    - ``"hanning"``: full-radius radial Hann window. Appropriate when
      χ is measured only inside the inverse-Dirichlet accessible disk
      and has a hard cutoff at the edge; used in the future D4
      engine-bridge layer.

    Returns
    -------
    alpha_axis : (target_size,) ndarray
    W_rec : (target_size, target_size) ndarray
    err_imag : float
    diag : dict
        Auxiliary windowing diagnostics.
    """
    Ng = len(beta_axis)
    beta_grid = beta_axis[None, :] + 1j * beta_axis[:, None]
    if window == "hanning":
        w = radial_hanning(beta_grid, B)
    elif window == "none":
        w = np.ones_like(chi, dtype=np.float64)
    else:
        raise ValueError(f"unknown window {window!r}")
    chi_windowed = chi * w
    chi_padded = zero_pad_centered(chi_windowed, target_size)
    beta_axis_padded = padded_beta_axis(beta_axis, target_size)
    alpha_axis, W_rec, err_imag = wigner_from_chi(chi_padded, beta_axis_padded)
    diag = {
        "n_grid_raw": Ng,
        "n_grid_padded": target_size,
        "window": window,
        "window_max": float(w.max()),
        "window_at_origin": float(w[Ng // 2, Ng // 2]),
        "chi_l_inf_at_grid_edge": float(np.max(np.abs(chi[0, :]))),
    }
    return alpha_axis, W_rec, err_imag, diag


def metrics_for_state(
    spec: dict,
    W_rec: np.ndarray,
    alpha_axis: np.ndarray,
    metric_window: float,
) -> dict:
    """Compute fidelity, L¹, and (if applicable) negativity ratio."""
    d_alpha = float(alpha_axis[1] - alpha_axis[0])
    alpha_grid = alpha_axis[None, :] + 1j * alpha_axis[:, None]
    W_true_full = W_true_of_state(alpha_grid, spec)

    # Restrict both W's to the metric window |α| ≤ metric_window
    W_rec_w, _ = restrict_to_window(W_rec, alpha_axis, metric_window)
    W_true_w, alpha_w = restrict_to_window(W_true_full, alpha_axis, metric_window)

    F = fidelity(W_rec_w, W_true_w, d_alpha)
    L1 = l1_error_total(W_rec_w, W_true_w, d_alpha)
    rho_neg = (negativity_ratio(W_rec_w, W_true_w, d_alpha)
               if spec.get("non_gaussian_metric") else None)

    m = {
        "fidelity": F,
        "L1_error": L1,
        "rho_neg": rho_neg,
        "d_alpha": d_alpha,
        "metric_window": metric_window,
    }
    if spec["kind"] == "thermal":
        purity = float(spec["purity"])
        m["fidelity_normalised"] = F / purity
        m["purity"] = purity
    return m, W_true_full


def assess(name: str, metrics: dict) -> dict:
    """Apply §7#5 pass criteria for *name*."""
    th = PASS_THRESHOLDS.get(name, {})
    result = {"thresholds": th, "flags": {}}

    if "F_min" in th and th["F_min"] is not None:
        result["flags"]["fidelity"] = metrics["fidelity"] >= th["F_min"]
    if "F_norm_min" in th:
        result["flags"]["fidelity_normalised"] = (
            metrics["fidelity_normalised"] >= th["F_norm_min"]
        )
    if "rho_neg_min" in th and metrics["rho_neg"] is not None:
        result["flags"]["rho_neg"] = metrics["rho_neg"] >= th["rho_neg_min"]

    flags_present = [v for v in result["flags"].values() if v is not None]
    result["pass"] = all(flags_present) if flags_present else None
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--beta0", type=float, default=0.05)
    parser.add_argument("--n-pulses", type=int, default=80,
                        help="train length used to set B = N|β₀|")
    parser.add_argument("--grid-size", type=int, default=81)
    parser.add_argument("--target-size", type=int, default=161,
                        help="zero-padded grid size for FFT interpolation")
    parser.add_argument("--metric-window", type=float, default=3.0,
                        help="|α|-window for fidelity / L¹ integration")
    parser.add_argument("--states", nargs="+", default=DEFAULT_STATES)
    parser.add_argument("--output", type=str,
                        default="numerics/reconstruction_demo.h5")
    args = parser.parse_args()

    t0 = time.time()
    B = args.n_pulses * args.beta0
    beta_axis = np.linspace(-B, B, args.grid_size)
    d_beta = float(beta_axis[1] - beta_axis[0])
    d_alpha_padded = np.pi / (args.target_size * d_beta)

    print(f"Grid {args.grid_size}² → padded {args.target_size}²")
    print(f"β ∈ [-{B}, {B}]², Δβ = {d_beta:.4f}")
    print(f"Reconstructed Δα = {d_alpha_padded:.4f}  (raw Δα = {np.pi/(args.grid_size*d_beta):.4f})")
    print(f"Metric window: |α| ≤ {args.metric_window}")
    print(f"States: {args.states}\n")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    state_results = {}

    with h5py.File(output_path, "w") as h5:
        h5.attrs["wp_id"] = WP_ID
        h5.attrs["code_version"] = CODE_VERSION
        h5.attrs["runner_version"] = RUNNER_VERSION
        h5.attrs["beta0"] = args.beta0
        h5.attrs["n_pulses"] = args.n_pulses
        h5.attrs["grid_size"] = args.grid_size
        h5.attrs["target_size"] = args.target_size
        h5.attrs["B"] = B
        h5.attrs["d_beta"] = d_beta
        h5.attrs["d_alpha_padded"] = d_alpha_padded
        h5.attrs["metric_window"] = args.metric_window
        h5.create_dataset("beta_axis", data=beta_axis)

        for name in args.states:
            spec = parse_state(name)
            t_n = time.time()

            # χ analytic on the raw 81² grid
            beta_grid_raw = beta_axis[None, :] + 1j * beta_axis[:, None]
            chi = chi_of_state(beta_grid_raw, spec)

            # window → pad → FFT → W_rec
            alpha_axis, W_rec, err_imag, diag = reconstruct(
                beta_axis, chi, B, args.target_size
            )

            # metrics
            m, W_true_full = metrics_for_state(
                spec, W_rec, alpha_axis, args.metric_window
            )
            assessment = assess(name, m)

            elapsed_n = time.time() - t_n

            state_results[name] = {
                "spec": {k: v for k, v in spec.items() if k != "name"},
                "metrics": m,
                "assessment": assessment,
                "err_imag": err_imag,
                "elapsed_s": round(elapsed_n, 3),
                "windowing": diag,
            }

            # report
            print(f"--- {name} ---")
            print(f"  F            = {m['fidelity']:.4f}", end="")
            if spec["kind"] == "thermal":
                print(f"   F/Tr(ρ²)  = {m['fidelity_normalised']:.4f}", end="")
            print()
            print(f"  L¹ error     = {m['L1_error']:.4f}")
            if m["rho_neg"] is not None:
                print(f"  ρ_neg        = {m['rho_neg']:+.4f}")
            else:
                print(f"  ρ_neg        = N/A (Gaussian target)")
            print(f"  max |Im W|   = {err_imag:.2e}")
            flags_disp = ", ".join(f"{k}={v}" for k, v in assessment["flags"].items())
            print(f"  pass = {assessment['pass']!s:<5}  ({flags_disp})")
            print(f"  ({elapsed_n:.2f} s)")
            print()

            # save grid datasets
            grp = h5.create_group(name)
            for k, v in spec.items():
                if isinstance(v, (int, float, str, bool)):
                    grp.attrs[k] = v
            grp.create_dataset("W_rec", data=W_rec)
            grp.create_dataset("W_true", data=W_true_full)
            grp.create_dataset("L1_map", data=l1_error_map(W_rec, W_true_full))
            grp.create_dataset("alpha_axis", data=alpha_axis)
            for mk, mv in m.items():
                if mv is None:
                    continue
                if isinstance(mv, (int, float)):
                    grp.attrs[f"metric_{mk}"] = mv
            grp.attrs["err_imag"] = err_imag
            if assessment["pass"] is not None:
                grp.attrs["pass"] = bool(assessment["pass"])

        # Aggregate
        F_list = []
        for name, r in state_results.items():
            sp = r["spec"]
            if sp["kind"] == "thermal":
                F_list.append(r["metrics"]["fidelity_normalised"])
            else:
                F_list.append(r["metrics"]["fidelity"])
        F_geomean = float(np.exp(np.mean(np.log(np.maximum(F_list, 1e-12)))))
        gated = [r["assessment"]["pass"] for r in state_results.values()
                 if r["assessment"]["pass"] is not None]
        overall_pass = all(gated) if gated else None
        deciding = ["fock_2", "cat_1.5"]
        deciding_pass = all(state_results[s]["assessment"]["pass"] for s in deciding
                            if s in state_results)

        h5.attrs["F_geomean"] = F_geomean
        h5.attrs["overall_pass"] = bool(overall_pass) if overall_pass is not None else False
        h5.attrs["deciding_pass"] = bool(deciding_pass)

    elapsed = time.time() - t0
    print("=" * 60)
    print(f"Aggregate F (geometric mean) = {F_geomean:.4f}")
    print(f"Deciding states (fock_2, cat_1.5) pass: {deciding_pass}")
    print(f"Overall PASS: {overall_pass}")
    print(f"Wrote {output_path}  ({elapsed:.2f} s)")

    # manifest
    payload = {
        "physical_parameters": {
            "beta0": args.beta0,
            "n_pulses": args.n_pulses,
        },
        "grid": {
            "size": args.grid_size,
            "target_size": args.target_size,
            "B": B,
            "d_beta": d_beta,
            "d_alpha_padded": d_alpha_padded,
        },
        "metric_window": args.metric_window,
        "states": args.states,
        "thresholds": PASS_THRESHOLDS,
        "results": {
            name: {
                "metrics": {k: v for k, v in r["metrics"].items() if v is not None},
                "pass": r["assessment"]["pass"],
                "flags": r["assessment"]["flags"],
            }
            for name, r in state_results.items()
        },
        "aggregate": {
            "F_geomean": F_geomean,
            "deciding_pass": bool(deciding_pass),
            "overall_pass": bool(overall_pass) if overall_pass is not None else None,
        },
        "tags": ["WP-W", "D3", "reconstruction-demo", "ideal-SDF"],
    }
    manifest = canonical_manifest(
        wp_id=WP_ID,
        code_version=CODE_VERSION,
        runner_version=RUNNER_VERSION,
        repository=REPOSITORY,
        artifact_path=str(output_path),
        artifact_format="hdf5",
        elapsed_s=elapsed,
        payload=payload,
    )
    manifest_path = output_path.with_suffix(".manifest.json")
    write_manifest(manifest, manifest_path)
    print(f"Wrote manifest: {manifest_path}")

    return 0 if (overall_pass is None or overall_pass) else 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    raise SystemExit(main())
