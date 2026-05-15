"""WP-W D2 plot — reach ladder figure.

Reads numerics/reach_ladder_ideal.h5 and produces a multi-panel figure:
- Top row: |C(β)| heatmaps for N ∈ {20, 40, 60, 80} on the coherent
  state. The accessible disk |β| ≤ N|β₀| is overlaid.
- Bottom row: Re[χ(β)] heatmaps on the same N grid, for visual
  intuition of the χ structure.
- Bottom-right inset: peak height of |D_N(x)| / N vs. 1/N
  (theoretical: identically 1; serves as a sanity check that the
  inverse-Dirichlet recipe lands on the correct ratio scale).

Usage:
    python plots/plot_reach_ladder.py \\
        --input numerics/reach_ladder_ideal.h5 \\
        --output plots/reach_ladder_residuals.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=str, default="numerics/reach_ladder_ideal.h5")
    parser.add_argument("--output", type=str, default="plots/reach_ladder_residuals.png")
    parser.add_argument("--state", type=str, default="coherent",
                        help="state to plot (default 'coherent')")
    args = parser.parse_args()

    with h5py.File(args.input, "r") as h5:
        beta_axis = h5["beta_axis"][:]
        N_list = sorted(
            int(g.split("_")[1]) for g in h5.keys() if g.startswith("N_")
        )
        beta0 = float(h5.attrs["beta0"])
        B_grid = float(h5.attrs["B_grid"])

        C_per_N = {}
        chi_per_N = {}
        n_in_disk_per_N = {}
        for N in N_list:
            grp = h5[f"N_{N}"]
            sgrp = grp[f"state_{args.state}"]
            C = sgrp["C_real"][:] + 1j * sgrp["C_imag"][:]
            chi = sgrp["chi_real"][:] + 1j * sgrp["chi_imag"][:]
            C_per_N[N] = C
            chi_per_N[N] = chi
            n_in_disk_per_N[N] = int(grp.attrs["n_in_disk"])

    n_panels = len(N_list)
    fig, axes = plt.subplots(2, n_panels, figsize=(2.8 * n_panels, 5.4), constrained_layout=True)
    if n_panels == 1:
        axes = axes.reshape(2, 1)

    extent = [beta_axis[0], beta_axis[-1], beta_axis[0], beta_axis[-1]]

    for col, N in enumerate(N_list):
        B_N = N * beta0
        C = C_per_N[N]
        chi = chi_per_N[N]

        # Top: |C(β)|
        ax = axes[0, col]
        im = ax.imshow(np.abs(C), origin="lower", extent=extent,
                       cmap="magma", vmin=0, vmax=1)
        ax.add_patch(Circle((0, 0), B_N, fill=False, lw=1.0, ls="--",
                            edgecolor="cyan", label=f"|β|≤{B_N:g}"))
        ax.set_title(f"|C(β)|   N={N}   B={B_N:.1f}")
        ax.set_xlabel("Re β")
        if col == 0:
            ax.set_ylabel("Im β")
        ax.set_aspect("equal")

        # Bottom: Re χ(β)
        ax = axes[1, col]
        vmax = max(abs(chi.real.min()), abs(chi.real.max()))
        im = ax.imshow(chi.real, origin="lower", extent=extent,
                       cmap="RdBu_r", vmin=-vmax, vmax=+vmax)
        ax.add_patch(Circle((0, 0), B_N, fill=False, lw=1.0, ls="--",
                            edgecolor="black"))
        ax.set_title(f"Re χ(β)   N={N}")
        ax.set_xlabel("Re β")
        if col == 0:
            ax.set_ylabel("Im β")
        ax.set_aspect("equal")

    fig.suptitle(
        f"WP-W D2 — reach ladder    state = {args.state}    β₀ = {beta0}    "
        f"grid {len(beta_axis)}² on [-{B_grid},{B_grid}]²",
        y=1.02, fontsize=10,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=140, bbox_inches="tight")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
