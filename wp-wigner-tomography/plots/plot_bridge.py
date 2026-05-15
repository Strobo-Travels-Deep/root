"""WP-W D4 bridge plot — two-panel figure.

Left panel:  Layer A — native Raman engine vs WP-E reference.
             σ_z (top), Re C (middle), Im C (bottom) at three
             δ/ω_m grid points near each comb tooth, with bar pairs
             (engine vs reference) and the residual annotated.

Right panel: Layer B — engine-measured χ FFT reconstruction at
             |α=3, θ_α=0⟩. W_rec(α) heatmap with α_truth (★),
             α_hat^W (✕), and α_hat^TOM (+) markers, plus the
             centroid residuals printed in the legend.

Usage:
    python plots/plot_bridge.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np


def load_layer_a(path: str) -> dict:
    with open(path) as f:
        data = json.load(f)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--layer-a", type=str,
                        default="numerics/bridge_native.json")
    parser.add_argument("--layer-b", type=str,
                        default="numerics/bridge_inversion.h5")
    parser.add_argument("--output", type=str,
                        default="plots/bridge.png")
    parser.add_argument("--alpha-window", type=float, default=4.0,
                        help="|α| window for the W_rec heatmap")
    args = parser.parse_args()

    A = load_layer_a(args.layer_a)
    cmp1 = A["comparison_1_nearest_grid"]
    eng_list = cmp1["engine"]
    ref_list = cmp1["reference"]

    fig = plt.figure(figsize=(13.5, 6.2), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, width_ratios=[1.0, 1.05], hspace=0.25)
    ax_sz = fig.add_subplot(gs[0, 0])
    ax_re = fig.add_subplot(gs[1, 0], sharex=ax_sz)
    ax_im = fig.add_subplot(gs[2, 0], sharex=ax_sz)
    ax_w = fig.add_subplot(gs[:, 1])

    # ---------- Layer A panel ----------
    det = np.array([e["det_rel"] for e in eng_list])
    width = 0.012
    x_left = det - width / 2
    x_right = det + width / 2

    for ax, key, title in [
        (ax_sz, "sigma_z", r"$\langle\sigma_z\rangle$"),
        (ax_re, "C_real", r"$\mathrm{Re}\,C = \langle\sigma_x\rangle$"),
        (ax_im, "C_imag", r"$\mathrm{Im}\,C = \langle\sigma_y\rangle$"),
    ]:
        e_vals = np.array([e[key] for e in eng_list])
        r_vals = np.array([r[key] for r in ref_list])
        ax.bar(x_left, e_vals, width=width, color="C0",
               label="WP-W engine", edgecolor="black", linewidth=0.5)
        ax.bar(x_right, r_vals, width=width, color="C3",
               label="WP-E reference", edgecolor="black", linewidth=0.5,
               alpha=0.85)
        ax.axhline(0, color="black", lw=0.4)
        ax.set_ylabel(title, fontsize=10)
        ax.grid(True, alpha=0.3)
        for d, e, r in zip(det, e_vals, r_vals):
            delta = abs(e - r)
            ax.annotate(f"|Δ|={delta:.1e}", xy=(d, max(e, r)),
                         xytext=(0, 4), textcoords="offset points",
                         ha="center", fontsize=7,
                         color="C2" if delta < 1e-3 else "C3")

    ax_im.set_xlabel(r"$\delta / \omega_m$ (WP-E nearest grid)", fontsize=10)
    ax_sz.legend(loc="upper right", fontsize=8, ncol=2)
    max_res = float(cmp1["max_residual"])
    pass_ = bool(cmp1["pass"])
    pass_str = "PASS" if pass_ else "FAIL"
    ax_sz.set_title(
        f"Layer A — Native Raman convention check  "
        f"(max |Δ| = {max_res:.2e}, gate 10⁻³: {pass_str})",
        fontsize=11
    )

    # ---------- Layer B panel ----------
    with h5py.File(args.layer_b, "r") as h5:
        alpha = float(h5.attrs["alpha"])
        alpha_phase_deg = float(h5.attrs["alpha_phase_deg"])
        bridge_pass = bool(h5.attrs["bridge_pass"])
        r_W_fine = float(h5.attrs["r_W_fine"])
        r_W_coarse = float(h5.attrs["r_W_coarse"])
        r_TOM = float(h5.attrs["r_TOM"])
        centroid_stab = float(h5.attrs["centroid_stability_coarse_vs_fine"])

        # Fine pass for the heatmap
        fine = h5["fine"]
        alpha_axis = fine["alpha_axis"][:]
        W_rec = fine["W_rec"][:]
        ah_fine_re = float(fine.attrs["alpha_hat_real"])
        ah_fine_im = float(fine.attrs["alpha_hat_imag"])
        ah_coarse_re = float(h5["coarse"].attrs["alpha_hat_real"])
        ah_coarse_im = float(h5["coarse"].attrs["alpha_hat_imag"])
        ah_tom_re = float(h5["wp_tom"].attrs["alpha_hat_real"])
        ah_tom_im = float(h5["wp_tom"].attrs["alpha_hat_imag"])

    alpha_truth = alpha * np.exp(1j * np.radians(alpha_phase_deg))

    # Restrict to window
    mask = np.abs(alpha_axis) <= args.alpha_window
    idx = np.where(mask)[0]
    if len(idx):
        i0, i1 = idx[0], idx[-1] + 1
        W_disp = W_rec[i0:i1, i0:i1]
        axis_disp = alpha_axis[i0:i1]
    else:
        W_disp = W_rec
        axis_disp = alpha_axis

    extent = (axis_disp[0], axis_disp[-1], axis_disp[0], axis_disp[-1])
    vmax = float(max(abs(W_disp.max()), abs(W_disp.min())))
    im = ax_w.imshow(W_disp, origin="lower", extent=extent,
                     cmap="RdBu_r", vmin=-vmax, vmax=+vmax,
                     interpolation="nearest", aspect="equal")
    ax_w.axhline(0, color="gray", lw=0.4)
    ax_w.axvline(0, color="gray", lw=0.4)

    ax_w.plot(alpha_truth.real, alpha_truth.imag, "*",
              color="black", ms=15, mec="white", mew=0.9,
              label=fr"ground truth  $\alpha = {alpha:.1f} + 0i$")
    ax_w.plot(ah_fine_re, ah_fine_im, "x",
              color="black", ms=11, mew=2.0,
              label=fr"$\hat\alpha^{{W,\mathrm{{fine}}}}$  ($|\Delta|={r_W_fine:.2e}$)")
    ax_w.plot(ah_coarse_re, ah_coarse_im, "o",
              color="black", ms=7, mfc="none", mew=1.2,
              label=fr"$\hat\alpha^{{W,\mathrm{{coarse}}}}$  ($|\Delta|={r_W_coarse:.2e}$)")
    ax_w.plot(ah_tom_re, ah_tom_im, "+",
              color="C2", ms=14, mew=2.5,
              label=fr"$\hat\alpha^{{TOM}}$  (saturated, $|\Delta|={r_TOM:.0e}$)")

    bridge_str = "PASS" if bridge_pass else "FAIL"
    ax_w.set_title(
        f"Layer B — Engine-measured $\\chi$ FFT centroid at $|\\alpha=3⟩$\n"
        f"(coarse↔fine stability = {centroid_stab:.2e}; bridge {bridge_str})",
        fontsize=11
    )
    ax_w.set_xlabel(r"$\mathrm{Re}\,\alpha$")
    ax_w.set_ylabel(r"$\mathrm{Im}\,\alpha$")
    ax_w.legend(loc="lower left", fontsize=8, framealpha=0.9)
    cb = fig.colorbar(im, ax=ax_w, shrink=0.85, pad=0.02)
    cb.set_label(r"$W_{\mathrm{rec}}(\alpha)$  [engine-measured $\chi$]",
                 fontsize=9)

    fig.suptitle("WP-W D4 bridge: native engine (WP-E) ↔ ideal SDF (WP-W) ↔ saturated template (WP-TOM)",
                 fontsize=12)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
