"""WP-W D2 — Forward-map reach ladder.

For each N in {20, 40, 60, 80}, builds the Cartesian β grid via the
inverse-Dirichlet rule of §2, computes the analytic characteristic
function χ(β) and observable C(β) = e^{-|β|²/2} χ(β) for vacuum and
coherent |α|=1, and stores everything (including the physical scan
recipe (δ - kω_m)·T_m, φ_train per β-node) in HDF5 with a
wp_manifest_v1 sidecar.

This is the *ideal-SDF / analytic-χ* layer of §4 D2; the optional
P1 native-engine extension is deferred to a separate session (see
§8 v0.4 close — `ideal_sdf` primitive).

Usage:
    python numerics/run_reach_ladder.py \\
        --beta0 0.05 \\
        --n-values 20 40 60 80 \\
        --states vacuum coherent \\
        --alpha 1.0 \\
        --grid-size 81 \\
        --output numerics/reach_ladder_ideal.h5
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
    inverse_dirichlet,
    write_manifest,
)


REPOSITORY = "https://github.com/Strobo-Travels-Deep/root"
WP_ID = "wigner-tomography"
CODE_VERSION = "0.4.0"  # tracks WP-W document version


def build_inverse_dirichlet_recipe(
    N: int,
    beta0: float,
    beta_axis: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Compute the physical scan recipe for each Cartesian β node.

    Returns
    -------
    delta_x : (Ng, Ng) ndarray
        Dimensionless detuning x = (δ - kω_m)·T_m per node, NaN where
        the node lies outside the accessible disk |β| > N·|β₀|.
    phi_train : (Ng, Ng) ndarray
        Train phase φ_train per node, NaN outside the disk. Stored in
        the range [0, 2π).
    n_in_disk : int
        Number of β nodes inside the disk.
    """
    Ng = len(beta_axis)
    B_N = N * beta0
    delta_x = np.full((Ng, Ng), np.nan, dtype=np.float64)
    phi_train = np.full((Ng, Ng), np.nan, dtype=np.float64)
    n_in_disk = 0

    # Loop over the 2D grid. Vectorising the inverse-Dirichlet root-find
    # is awkward; for 81² = 6561 nodes the explicit loop is well under a
    # second.
    for j in range(Ng):  # row = Im β
        for k in range(Ng):  # col = Re β
            bg = beta_axis[k] + 1j * beta_axis[j]
            r = abs(bg)
            if r > B_N + 1e-12:
                continue
            theta = np.angle(bg)
            ratio = r / beta0  # ∈ [0, N]
            x = inverse_dirichlet(N, ratio)
            # arg β₀ = 0 (taking β₀ real positive); arg 𝒟_N(x) = (N-1)x/2
            phi = (theta - (N - 1) * x / 2.0) % (2.0 * np.pi)
            delta_x[j, k] = x
            phi_train[j, k] = phi
            n_in_disk += 1
    return delta_x, phi_train, n_in_disk


def evaluate_chi(state: str, beta_grid: np.ndarray, alpha: float) -> np.ndarray:
    """Return the analytic χ(β) for the named state."""
    if state == "vacuum":
        return chi_vacuum(beta_grid)
    if state == "coherent":
        return chi_coherent(beta_grid, alpha + 0.0j)
    raise ValueError(f"Unknown state: {state!r}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--beta0", type=float, default=0.05,
                        help="per-pulse displacement magnitude (default 0.05)")
    parser.add_argument("--n-values", type=int, nargs="+", default=[20, 40, 60, 80],
                        help="train lengths (default 20 40 60 80)")
    parser.add_argument("--states", nargs="+", default=["vacuum", "coherent"],
                        help="input states (default vacuum coherent)")
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="coherent-state amplitude (real, default 1.0)")
    parser.add_argument("--grid-size", type=int, default=81,
                        help="Cartesian β grid size (default 81)")
    parser.add_argument("--output", type=str, default="numerics/reach_ladder_ideal.h5",
                        help="output HDF5 path (default numerics/reach_ladder_ideal.h5)")
    args = parser.parse_args()

    t0 = time.time()

    # The β grid is shared across N; B is set by the largest N.
    N_max = max(args.n_values)
    B_grid = N_max * args.beta0
    beta_axis = np.linspace(-B_grid, B_grid, args.grid_size)
    d_beta = float(beta_axis[1] - beta_axis[0])
    beta_grid = beta_axis[None, :] + 1j * beta_axis[:, None]  # rows = Im β

    print(f"Grid: {args.grid_size} × {args.grid_size} on β ∈ [-{B_grid}, {B_grid}]²,  Δβ = {d_beta:.4f}")
    print(f"States: {args.states}    α (coherent) = {args.alpha}")
    print(f"N values: {args.n_values}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload_per_n = {}

    with h5py.File(output_path, "w") as h5:
        h5.attrs["wp_id"] = WP_ID
        h5.attrs["code_version"] = CODE_VERSION
        h5.attrs["runner_version"] = RUNNER_VERSION
        h5.attrs["beta0"] = args.beta0
        h5.attrs["grid_size"] = args.grid_size
        h5.attrs["B_grid"] = B_grid
        h5.attrs["d_beta"] = d_beta
        h5.create_dataset("beta_axis", data=beta_axis)

        for N in args.n_values:
            t_n = time.time()
            grp = h5.create_group(f"N_{N}")
            grp.attrs["n_pulses"] = N
            grp.attrs["B_N"] = N * args.beta0

            # Physical scan recipe (inverse-Dirichlet)
            delta_x, phi_train, n_in_disk = build_inverse_dirichlet_recipe(
                N, args.beta0, beta_axis
            )
            grp.create_dataset("delta_x", data=delta_x)
            grp.create_dataset("phi_train", data=phi_train)
            grp.attrs["n_in_disk"] = n_in_disk

            # χ and C for each state on the same β grid (state physics is
            # independent of N for the analytic layer)
            for state in args.states:
                sgrp = grp.create_group(f"state_{state}")
                if state == "coherent":
                    sgrp.attrs["alpha"] = args.alpha
                chi = evaluate_chi(state, beta_grid, args.alpha)
                C = contrast_from_chi(beta_grid, chi)
                sgrp.create_dataset("chi_real", data=chi.real)
                sgrp.create_dataset("chi_imag", data=chi.imag)
                sgrp.create_dataset("C_real", data=C.real)
                sgrp.create_dataset("C_imag", data=C.imag)

            elapsed_n = time.time() - t_n
            payload_per_n[f"N_{N}"] = {
                "n_pulses": N,
                "B_N": N * args.beta0,
                "n_in_disk": n_in_disk,
                "elapsed_s": round(elapsed_n, 3),
            }
            print(f"  N = {N:>3}  B = {N * args.beta0:.2f}  "
                  f"n_in_disk = {n_in_disk:>5}/{args.grid_size**2}  "
                  f"({elapsed_n:.2f} s)")

    elapsed_total = time.time() - t0
    print(f"Total: {elapsed_total:.2f} s — wrote {output_path}")

    # Sidecar manifest
    payload = {
        "physical_parameters": {
            "beta0": args.beta0,
            "alpha_coherent": args.alpha,
        },
        "grid": {
            "size": args.grid_size,
            "B_grid": B_grid,
            "d_beta": d_beta,
            "axis": "linspace(-B_grid, B_grid, grid_size)",
        },
        "states": args.states,
        "n_pulses_values": args.n_values,
        "per_n_summary": payload_per_n,
        "convention": {
            "beta0_phase": "real positive (arg β₀ = 0)",
            "dirichlet_branch": "monotone central lobe 0 ≤ x ≤ 2π/N",
            "phi_train_formula": "(θ − (N−1) x / 2) mod 2π",
            "C_chi_relation": "C(β) = exp(-|β|²/2) · χ(β)  [ideal σ_z SDF]",
        },
        "tags": ["WP-W", "D2", "reach-ladder", "ideal-SDF", "analytic-chi"],
    }
    manifest = canonical_manifest(
        wp_id=WP_ID,
        code_version=CODE_VERSION,
        runner_version=RUNNER_VERSION,
        repository=REPOSITORY,
        artifact_path=str(output_path),
        artifact_format="hdf5",
        elapsed_s=elapsed_total,
        payload=payload,
    )
    manifest_path = output_path.with_suffix(".manifest.json")
    write_manifest(manifest, manifest_path)
    print(f"Wrote manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    # Ensure local imports work when run from numerics/ or from the WP root.
    sys.path.insert(0, str(Path(__file__).parent))
    raise SystemExit(main())
