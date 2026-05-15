"""WP-W D3 plot — reconstruction demo grid figure.

Reads numerics/reconstruction_demo.h5 and produces a 3 × N_states
panel figure:
- Top row:    W_true(α)
- Middle row: W_rec(α)
- Bottom row: |W_rec − W_true|  (L¹ error map)

State name + metric annotations on the bottom-row x-axis label.

Usage:
    python plots/plot_reconstruction_demo.py \\
        --input numerics/reconstruction_demo.h5 \\
        --output plots/reconstruction_demo.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np


def short_label(name: str) -> str:
    """Compact display label."""
    return name.replace("_", " ").replace("coherent", "coh").replace("thermal", "th").replace("mixed cat", "mcat")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=str, default="numerics/reconstruction_demo.h5")
    parser.add_argument("--output", type=str, default="plots/reconstruction_demo.png")
    parser.add_argument("--alpha-window", type=float, default=3.0)
    args = parser.parse_args()

    with h5py.File(args.input, "r") as h5:
        metric_window = float(h5.attrs.get("metric_window", args.alpha_window))
        overall_pass = bool(h5.attrs.get("overall_pass", False))
        F_geomean = float(h5.attrs.get("F_geomean", float("nan")))
        deciding_pass = bool(h5.attrs.get("deciding_pass", False))

        state_names = [k for k in h5.keys() if k != "beta_axis"]

        # Preserve a deterministic display order matching the runner default.
        canonical_order = [
            "vacuum", "coherent_1.5", "thermal_0.5", "fock_1",
            "fock_2", "cat_1.5", "mixed_cat_1.5",
        ]
        state_names = [s for s in canonical_order if s in state_names]

        n = len(state_names)
        fig, axes = plt.subplots(3, n, figsize=(2.6 * n, 7.4),
                                 constrained_layout=True)

        for col, name in enumerate(state_names):
            grp = h5[name]
            W_rec = grp["W_rec"][:]
            W_true = grp["W_true"][:]
            L1 = grp["L1_map"][:]
            alpha_axis = grp["alpha_axis"][:]
            F = float(grp.attrs.get("metric_fidelity", float("nan")))
            try:
                F_norm = float(grp.attrs["metric_fidelity_normalised"])
            except KeyError:
                F_norm = None
            try:
                rho_neg = float(grp.attrs["metric_rho_neg"])
            except KeyError:
                rho_neg = None
            try:
                state_pass = bool(grp.attrs["pass"])
            except KeyError:
                state_pass = None

            # crop to display window
            mask = np.abs(alpha_axis) <= args.alpha_window
            idx = np.where(mask)[0]
            i_lo, i_hi = idx[0], idx[-1] + 1
            ax_axis = alpha_axis[i_lo:i_hi]
            W_rec_c = W_rec[i_lo:i_hi, i_lo:i_hi]
            W_true_c = W_true[i_lo:i_hi, i_lo:i_hi]
            L1_c = L1[i_lo:i_hi, i_lo:i_hi]

            vmax = max(abs(W_true_c.min()), abs(W_true_c.max()),
                       abs(W_rec_c.min()), abs(W_rec_c.max()))

            extent = [ax_axis[0], ax_axis[-1], ax_axis[0], ax_axis[-1]]

            # row 0: W_true
            ax = axes[0, col]
            ax.imshow(W_true_c, origin="lower", extent=extent,
                      cmap="RdBu_r", vmin=-vmax, vmax=+vmax)
            ax.set_title(short_label(name), fontsize=9)
            if col == 0:
                ax.set_ylabel(r"$W_\mathrm{true}$" + "\n" + r"Im $\alpha$",
                              fontsize=9)
            ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
            ax.set_aspect("equal")

            # row 1: W_rec
            ax = axes[1, col]
            ax.imshow(W_rec_c, origin="lower", extent=extent,
                      cmap="RdBu_r", vmin=-vmax, vmax=+vmax)
            if col == 0:
                ax.set_ylabel(r"$W_\mathrm{rec}$" + "\n" + r"Im $\alpha$",
                              fontsize=9)
            ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
            ax.set_aspect("equal")

            # row 2: L¹
            ax = axes[2, col]
            l1_max = max(L1_c.max(), 1e-6)
            ax.imshow(L1_c, origin="lower", extent=extent,
                      cmap="viridis", vmin=0, vmax=l1_max)
            if col == 0:
                ax.set_ylabel(r"$|W_\mathrm{rec} - W_\mathrm{true}|$" + "\n"
                              + r"Im $\alpha$", fontsize=9)
            # Annotate metrics
            pass_str = ""
            if state_pass is True:
                pass_str = "  ✓"
            elif state_pass is False:
                pass_str = "  ✗"

            metric_lines = []
            if F_norm is not None:
                metric_lines.append(f"F = {F:.3f}")
                metric_lines.append(f"F/Tr(ρ²) = {F_norm:.3f}{pass_str}")
            else:
                metric_lines.append(f"F = {F:.3f}{pass_str}")
            metric_lines.append(f"L¹ = {L1_c.sum() * (ax_axis[1]-ax_axis[0])**2:.3f}")
            if rho_neg is not None:
                metric_lines.append(f"ρ_neg = {rho_neg:+.3f}")

            ax.set_xlabel("Re α\n" + "\n".join(metric_lines), fontsize=7.5)
            ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
            ax.set_aspect("equal")

        suptitle = (f"WP-W D3 — reconstruction demo   "
                    f"deciding-state PASS = {deciding_pass}, "
                    f"overall PASS = {overall_pass}, "
                    f"F̄_geom = {F_geomean:.3f}   "
                    f"metric window |α| ≤ {metric_window}")
        fig.suptitle(suptitle, y=1.02, fontsize=10)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=140, bbox_inches="tight")
        print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
