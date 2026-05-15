"""WP-W P0 preflight — analytic-grid self-consistency.

Implements the P0 half of the §4a preflight gate. Insert analytic
χ(β) values on the v0.2 Cartesian grid for two reference states
(vacuum and coherent |α=1⟩), perform the 2D-FFT inversion, and verify

  1. Vacuum: W_vac(α = 0) ≈ 2/π within FFT precision;
  2. Coherent |α=1⟩: peak position within one raw Δα cell of α_true,
     no sign flip in the phase convention.

This is the *idealised* preflight — the engine half (P1) is gated on
the §7#3 `ideal_sdf` primitive and is run in a separate session.

Usage:
    python numerics/run_p0_preflight.py \\
        --beta0 0.05 \\
        --n-pulses 80 \\
        --grid-size 81 \\
        --alpha 1.0 \\
        --output numerics/p0_preflight.h5
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
    chi_coherent,
    chi_vacuum,
    contrast_from_chi,
    wigner_from_chi,
    write_manifest,
)


REPOSITORY = "https://github.com/Strobo-Travels-Deep/root"
WP_ID = "wigner-tomography"
CODE_VERSION = "0.4.0"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--beta0", type=float, default=0.05)
    parser.add_argument("--n-pulses", type=int, default=80)
    parser.add_argument("--grid-size", type=int, default=81)
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="coherent-state amplitude for the second test (default 1.0)")
    parser.add_argument("--output", type=str, default="numerics/p0_preflight.h5")
    args = parser.parse_args()

    t0 = time.time()

    B = args.n_pulses * args.beta0
    beta_axis = np.linspace(-B, B, args.grid_size)
    d_beta = float(beta_axis[1] - beta_axis[0])
    beta_grid = beta_axis[None, :] + 1j * beta_axis[:, None]

    # Pass criteria scales
    d_alpha = np.pi / (args.grid_size * d_beta)
    print(f"Grid: {args.grid_size}², β ∈ [-{B}, {B}]²,  Δβ = {d_beta:.4f},  Δα = {d_alpha:.4f}")
    print(f"Pass criterion: peak within one Δα cell ≈ {d_alpha:.4f}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = {}

    with h5py.File(output_path, "w") as h5:
        h5.attrs["wp_id"] = WP_ID
        h5.attrs["code_version"] = CODE_VERSION
        h5.attrs["runner_version"] = RUNNER_VERSION
        h5.attrs["beta0"] = args.beta0
        h5.attrs["n_pulses"] = args.n_pulses
        h5.attrs["grid_size"] = args.grid_size
        h5.attrs["B"] = B
        h5.attrs["d_beta"] = d_beta
        h5.attrs["d_alpha"] = d_alpha
        h5.create_dataset("beta_axis", data=beta_axis)

        # ----- Test 1: Vacuum -----
        chi_v = chi_vacuum(beta_grid)
        C_v = contrast_from_chi(beta_grid, chi_v)
        alpha_axis, W_v, err_imag_v = wigner_from_chi(chi_v, beta_axis)

        center = (args.grid_size - 1) // 2
        W_center = W_v[center, center]
        W_expected = 2.0 / np.pi

        # Find peak by absolute value. _common.wigner_from_chi returns
        # rows = Im α, cols = Re α (matches input χ convention).
        idx_peak = np.unravel_index(int(np.argmax(np.abs(W_v))), W_v.shape)
        alpha_y_peak = alpha_axis[idx_peak[0]]  # row → Im α
        alpha_x_peak = alpha_axis[idx_peak[1]]  # col → Re α
        W_peak = W_v[idx_peak]
        # Distance from expected peak (origin) in α units
        peak_offset = np.hypot(alpha_x_peak, alpha_y_peak)

        vac_pass = (abs(W_center - W_expected) < 5e-3) and (peak_offset < d_alpha + 1e-9)

        print()
        print("=== Test 1: Vacuum ===")
        print(f"  W(α=0) measured = {W_center:+.6f}")
        print(f"  W(α=0) expected = {W_expected:+.6f}")
        print(f"  residual        = {W_center - W_expected:+.2e}")
        print(f"  peak at (α_x, α_y) = ({alpha_x_peak:+.4f}, {alpha_y_peak:+.4f})  (expected origin)")
        print(f"  peak offset = {peak_offset:.4f}    (must be < Δα = {d_alpha:.4f})")
        print(f"  max |Im W|  = {err_imag_v:.2e}")
        print(f"  PASS: {vac_pass}")

        grp_v = h5.create_group("vacuum")
        grp_v.create_dataset("chi_real", data=chi_v.real)
        grp_v.create_dataset("chi_imag", data=chi_v.imag)
        grp_v.create_dataset("C_real", data=C_v.real)
        grp_v.create_dataset("C_imag", data=C_v.imag)
        grp_v.create_dataset("W", data=W_v)
        grp_v.create_dataset("alpha_axis", data=alpha_axis)
        grp_v.attrs["W_center"] = W_center
        grp_v.attrs["W_expected_at_origin"] = W_expected
        grp_v.attrs["peak_alpha_x"] = alpha_x_peak
        grp_v.attrs["peak_alpha_y"] = alpha_y_peak
        grp_v.attrs["peak_offset"] = peak_offset
        grp_v.attrs["err_imag"] = err_imag_v
        grp_v.attrs["pass"] = bool(vac_pass)

        results["vacuum"] = {
            "W_center": float(W_center),
            "W_expected": float(W_expected),
            "peak_alpha_x": float(alpha_x_peak),
            "peak_alpha_y": float(alpha_y_peak),
            "peak_offset": float(peak_offset),
            "err_imag": float(err_imag_v),
            "pass": bool(vac_pass),
        }

        # ----- Test 2: Coherent |α⟩ -----
        alpha_true = args.alpha + 0.0j
        chi_c = chi_coherent(beta_grid, alpha_true)
        C_c = contrast_from_chi(beta_grid, chi_c)
        alpha_axis, W_c, err_imag_c = wigner_from_chi(chi_c, beta_axis)

        idx_peak = np.unravel_index(int(np.argmax(np.abs(W_c))), W_c.shape)
        alpha_y_peak = alpha_axis[idx_peak[0]]  # row → Im α
        alpha_x_peak = alpha_axis[idx_peak[1]]  # col → Re α
        W_peak = W_c[idx_peak]

        # Distance from prepared α (real positive on the α_x axis)
        peak_offset = np.hypot(alpha_x_peak - args.alpha, alpha_y_peak)
        # Peak should be positive (a Gaussian, no sign flip)
        sign_flip = W_peak < 0
        coh_pass = (peak_offset < d_alpha + 1e-9) and not sign_flip

        # Expected discrete-grid peak: at the grid point closest to α=1
        idx_expected = int(np.argmin(np.abs(alpha_axis - args.alpha)))
        alpha_grid_at_expected = alpha_axis[idx_expected]
        W_expected_at_peak = (2.0 / np.pi) * np.exp(-2.0 * abs(alpha_grid_at_expected - args.alpha) ** 2)

        print()
        print(f"=== Test 2: Coherent |α={args.alpha}⟩ ===")
        print(f"  peak at (α_x, α_y) = ({alpha_x_peak:+.4f}, {alpha_y_peak:+.4f})")
        print(f"  expected at α_true = ({args.alpha:+.4f}, +0.0000)")
        print(f"  closest grid point  = ({alpha_grid_at_expected:+.4f}, +0.0000)")
        print(f"  peak offset from α_true = {peak_offset:.4f}    (must be < Δα = {d_alpha:.4f})")
        print(f"  peak value  measured = {W_peak:+.6f}")
        print(f"  peak value  expected (at closest grid pt) = {W_expected_at_peak:+.6f}")
        print(f"  sign flip?  {sign_flip}")
        print(f"  max |Im W|  = {err_imag_c:.2e}")
        print(f"  PASS: {coh_pass}")

        grp_c = h5.create_group("coherent")
        grp_c.attrs["alpha"] = args.alpha
        grp_c.create_dataset("chi_real", data=chi_c.real)
        grp_c.create_dataset("chi_imag", data=chi_c.imag)
        grp_c.create_dataset("C_real", data=C_c.real)
        grp_c.create_dataset("C_imag", data=C_c.imag)
        grp_c.create_dataset("W", data=W_c)
        grp_c.create_dataset("alpha_axis", data=alpha_axis)
        grp_c.attrs["peak_alpha_x"] = alpha_x_peak
        grp_c.attrs["peak_alpha_y"] = alpha_y_peak
        grp_c.attrs["peak_offset"] = peak_offset
        grp_c.attrs["W_peak"] = W_peak
        grp_c.attrs["W_expected_at_peak"] = W_expected_at_peak
        grp_c.attrs["err_imag"] = err_imag_c
        grp_c.attrs["pass"] = bool(coh_pass)

        results["coherent"] = {
            "alpha": float(args.alpha),
            "peak_alpha_x": float(alpha_x_peak),
            "peak_alpha_y": float(alpha_y_peak),
            "peak_offset": float(peak_offset),
            "W_peak": float(W_peak),
            "W_expected_at_peak": float(W_expected_at_peak),
            "err_imag": float(err_imag_c),
            "pass": bool(coh_pass),
        }

        overall_pass = vac_pass and coh_pass
        h5.attrs["overall_pass"] = bool(overall_pass)

    elapsed = time.time() - t0
    print()
    print(f"=== P0 OVERALL: {'PASS' if overall_pass else 'FAIL'} ===")
    print(f"Wrote {output_path}  ({elapsed:.2f} s)")

    # Manifest
    payload = {
        "physical_parameters": {
            "beta0": args.beta0,
            "n_pulses": args.n_pulses,
            "alpha_test": args.alpha,
        },
        "grid": {
            "size": args.grid_size,
            "B": B,
            "d_beta": d_beta,
            "d_alpha": d_alpha,
        },
        "pass_criteria": {
            "vacuum": "|W(α=0) − 2/π| < 5e-3 AND peak offset < Δα",
            "coherent": "peak offset from α_true < Δα AND no sign flip",
        },
        "results": results,
        "overall_pass": bool(overall_pass),
        "tags": ["WP-W", "P0", "preflight", "analytic-grid"],
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
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    raise SystemExit(main())
