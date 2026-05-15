"""WP-W P0 plot — reconstructed Wigner side-by-side.

Reads numerics/p0_preflight.h5 and produces a two-panel figure with
W_vac(γ) and W_coh(γ; α=1) on the reconstructed α grid, with
predicted peak locations marked.

Usage:
    python plots/plot_p0_preflight.py \\
        --input numerics/p0_preflight.h5 \\
        --output plots/p0_preflight.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=str, default="numerics/p0_preflight.h5")
    parser.add_argument("--output", type=str, default="plots/p0_preflight.png")
    parser.add_argument("--alpha-window", type=float, default=3.5,
                        help="display window in α-units (default ±3.5)")
    args = parser.parse_args()

    with h5py.File(args.input, "r") as h5:
        d_alpha = float(h5.attrs["d_alpha"])
        overall_pass = bool(h5.attrs["overall_pass"])

        W_v = h5["vacuum/W"][:]
        alpha_v = h5["vacuum/alpha_axis"][:]
        peak_v = (h5["vacuum"].attrs["peak_alpha_x"],
                  h5["vacuum"].attrs["peak_alpha_y"])
        vac_pass = bool(h5["vacuum"].attrs["pass"])

        W_c = h5["coherent/W"][:]
        alpha_c = h5["coherent/alpha_axis"][:]
        alpha_true = float(h5["coherent"].attrs["alpha"])
        peak_c = (h5["coherent"].attrs["peak_alpha_x"],
                  h5["coherent"].attrs["peak_alpha_y"])
        coh_pass = bool(h5["coherent"].attrs["pass"])

    fig, (ax_v, ax_c) = plt.subplots(1, 2, figsize=(11.0, 4.8), constrained_layout=True)

    # Crop to display window
    aw = args.alpha_window
    def crop_indices(axis):
        i_lo = int(np.searchsorted(axis, -aw))
        i_hi = int(np.searchsorted(axis, +aw))
        return i_lo, i_hi

    i_lo, i_hi = crop_indices(alpha_v)
    Wv_crop = W_v[i_lo:i_hi, i_lo:i_hi]
    av_crop = alpha_v[i_lo:i_hi]
    extent_v = [av_crop[0], av_crop[-1], av_crop[0], av_crop[-1]]
    vmax_v = max(abs(Wv_crop.min()), abs(Wv_crop.max()))
    im_v = ax_v.imshow(Wv_crop, origin="lower", extent=extent_v,
                       cmap="RdBu_r", vmin=-vmax_v, vmax=+vmax_v)
    ax_v.plot(0, 0, "k+", ms=12, mew=1.5, label="α_true = 0")
    ax_v.plot(peak_v[0], peak_v[1], "ko", mfc="none", ms=10, mew=1.5,
              label=f"peak ({peak_v[0]:+.3f}, {peak_v[1]:+.3f})")
    ax_v.set_title(f"Vacuum   PASS={vac_pass}   Δα={d_alpha:.3f}", fontsize=10)
    ax_v.set_xlabel(r"Re $\alpha$")
    ax_v.set_ylabel(r"Im $\alpha$")
    ax_v.set_aspect("equal")
    ax_v.legend(loc="lower right", fontsize=8)
    fig.colorbar(im_v, ax=ax_v, label=r"$W(\alpha)$")

    i_lo, i_hi = crop_indices(alpha_c)
    Wc_crop = W_c[i_lo:i_hi, i_lo:i_hi]
    ac_crop = alpha_c[i_lo:i_hi]
    extent_c = [ac_crop[0], ac_crop[-1], ac_crop[0], ac_crop[-1]]
    vmax_c = max(abs(Wc_crop.min()), abs(Wc_crop.max()))
    im_c = ax_c.imshow(Wc_crop, origin="lower", extent=extent_c,
                       cmap="RdBu_r", vmin=-vmax_c, vmax=+vmax_c)
    ax_c.plot(alpha_true, 0, "k+", ms=12, mew=1.5,
              label=f"α_true = {alpha_true:+.3f}")
    ax_c.plot(peak_c[0], peak_c[1], "ko", mfc="none", ms=10, mew=1.5,
              label=f"peak ({peak_c[0]:+.3f}, {peak_c[1]:+.3f})")
    ax_c.set_title(f"Coherent |α={alpha_true:g}⟩   PASS={coh_pass}", fontsize=10)
    ax_c.set_xlabel(r"Re $\alpha$")
    ax_c.set_ylabel(r"Im $\alpha$")
    ax_c.set_aspect("equal")
    ax_c.legend(loc="lower right", fontsize=8)
    fig.colorbar(im_c, ax=ax_c, label=r"$W(\alpha)$")

    fig.suptitle(
        f"WP-W P0 preflight   overall PASS = {overall_pass}",
        y=1.02, fontsize=11,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=140, bbox_inches="tight")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
