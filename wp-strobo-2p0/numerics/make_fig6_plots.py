#!/usr/bin/env python3
"""Hasse-Fig-6-style figures for the (phi, theta_0) slice at delta_0 = 0.

Two figures (one per |alpha|), each a 2x2 grid:
    top row:    <sigma_z>  for T1 (left) and T2 (right)
    bottom row: delta<n>   for T1 (left) and T2 (right)

Layout and cuts follow Hasse 2024 Fig. 6: three theta_0 cuts at
{pi/4, pi/2, pi} (light gray, dark gray, black) are overlaid on each
bottom-edge and left-edge marginal panel.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
PLOTS = HERE.parent / "plots"
PLOTS.mkdir(exist_ok=True)


def nearest_idx(arr: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(arr - target)))


def make_fig(data: np.ndarray, alpha: float, out_name: str) -> None:
    phi = data["PHI_DEG"]
    th = data["THETA0_DEG"]
    phi_ext = np.concatenate([phi, [360.0]])
    th_ext = np.concatenate([th, [360.0]])

    tag_T1 = f"T1_alpha{alpha:g}".replace(".", "p")
    tag_T2 = f"T2_alpha{alpha:g}".replace(".", "p")

    sz_T1 = data[f"{tag_T1}_sz"]
    sz_T2 = data[f"{tag_T2}_sz"]
    dn_T1 = data[f"{tag_T1}_delta_n"]
    dn_T2 = data[f"{tag_T2}_delta_n"]

    # cuts
    th_cuts = [45.0, 90.0, 180.0]   # in deg for theta_0
    phi_cuts = [45.0, 90.0, 180.0]  # in deg for phi (vertical cuts)
    cut_colors = ["#bbbbbb", "#666666", "#000000"]

    def extend(Z):
        # extend over phi axis (rows) then theta axis (cols) to match phi_ext, th_ext
        Z = np.concatenate([Z, Z[:1, :]], axis=0)
        Z = np.concatenate([Z, Z[:, :1]], axis=1)
        return Z

    fig = plt.figure(figsize=(14.5, 9.2), constrained_layout=True)
    gs = fig.add_gridspec(
        2, 2,
        height_ratios=[1, 1], width_ratios=[1, 1], hspace=0.12, wspace=0.14,
    )
    subs = []
    for row in range(2):
        for col in range(2):
            sub = gs[row, col].subgridspec(
                2, 2, height_ratios=[1, 3], width_ratios=[3, 1],
                hspace=0.04, wspace=0.04,
            )
            subs.append(sub)

    datasets = [
        ("$\\langle\\sigma_z\\rangle$", sz_T1, "T1:  N=3, $\\delta t$=100 ns",
         "RdBu_r", -max(abs(sz_T1).max(), abs(sz_T2).max()),
         +max(abs(sz_T1).max(), abs(sz_T2).max())),
        ("$\\langle\\sigma_z\\rangle$", sz_T2, "T2:  N=7, $\\delta t$= 50 ns",
         "RdBu_r", -max(abs(sz_T1).max(), abs(sz_T2).max()),
         +max(abs(sz_T1).max(), abs(sz_T2).max())),
        ("$\\delta\\langle n\\rangle$", dn_T1, "T1:  N=3, $\\delta t$=100 ns",
         "PRGn", -max(abs(dn_T1).max(), abs(dn_T2).max()),
         +max(abs(dn_T1).max(), abs(dn_T2).max())),
        ("$\\delta\\langle n\\rangle$", dn_T2, "T2:  N=7, $\\delta t$= 50 ns",
         "PRGn", -max(abs(dn_T1).max(), abs(dn_T2).max()),
         +max(abs(dn_T1).max(), abs(dn_T2).max())),
    ]

    for idx, ((obs_label, Z, subtitle, cmap, vmin, vmax), sub) in enumerate(
            zip(datasets, subs)):
        ax_top = fig.add_subplot(sub[0, 0])
        ax_main = fig.add_subplot(sub[1, 0], sharex=ax_top)
        ax_right = fig.add_subplot(sub[1, 1], sharey=ax_main)

        Z_ext = extend(Z)
        im = ax_main.pcolormesh(th_ext, phi_ext, Z_ext,
                                shading="auto", cmap=cmap, vmin=vmin, vmax=vmax)

        # overlay cut-lines
        for th_cut, col in zip(th_cuts, cut_colors):
            ax_main.axvline(th_cut, color=col, lw=0.9, alpha=0.9)
        for phi_cut, col in zip(phi_cuts, cut_colors):
            ax_main.axhline(phi_cut, color=col, lw=0.9, alpha=0.9)

        ax_main.set_xlim(0, 360)
        ax_main.set_ylim(0, 360)
        ax_main.set_xticks([0, 90, 180, 270, 360])
        ax_main.set_yticks([0, 90, 180, 270, 360])
        ax_main.set_xlabel(r"motional phase $\vartheta_0$ [deg]")
        ax_main.set_ylabel(r"analysis phase $\varphi$ [deg]")

        # top marginal: Z vs theta_0 at the three phi cuts
        for phi_cut, col in zip(phi_cuts, cut_colors):
            i = nearest_idx(phi, phi_cut)
            line = np.concatenate([Z[i], Z[i, :1]])
            ax_top.plot(th_ext, line, color=col, lw=1.4)
        ax_top.axhline(0, color="k", lw=0.5, alpha=0.4)
        ax_top.set_ylim(vmin, vmax)
        ax_top.tick_params(labelbottom=False)
        ax_top.set_ylabel(obs_label, fontsize=9)
        ax_top.set_title(subtitle, fontsize=10)

        # right marginal: Z vs phi at the three theta_0 cuts
        for th_cut, col in zip(th_cuts, cut_colors):
            j = nearest_idx(th, th_cut)
            line = np.concatenate([Z[:, j], Z[:1, j]])
            ax_right.plot(line, phi_ext, color=col, lw=1.4)
        ax_right.axvline(0, color="k", lw=0.5, alpha=0.4)
        ax_right.set_xlim(vmin, vmax)
        ax_right.tick_params(labelleft=False)
        ax_right.set_xlabel(obs_label, fontsize=9)

        # colorbar, pulled out of the subpanel
        cbar = fig.colorbar(im, ax=[ax_top, ax_main, ax_right],
                            shrink=0.75, aspect=20, pad=0.02,
                            location="right" if idx % 2 == 1 else "right")
        cbar.set_label(obs_label)

    fig.suptitle(
        f"Hasse-Fig.-6-style  $(\\varphi, \\vartheta_0)$ slice  at  "
        f"$\\delta_0 = 0,\\ |\\alpha|={alpha}$,  "
        f"$\\eta={0.395}$,  $\\Delta t = 0.77\\ \\mu$s  "
        f"(near-stroboscopic)",
        fontsize=13,
    )
    out = PLOTS / out_name
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out.relative_to(out.parents[2])}")


def main() -> None:
    data = np.load(HERE / "hasse_fig6_slice.npz")
    print("strobo 2.0  —  Hasse-Fig-6 figures")
    make_fig(data, alpha=3.0, out_name="06_hasse_fig6_alpha3.png")
    make_fig(data, alpha=4.5, out_name="07_hasse_fig6_alpha4p5.png")


if __name__ == "__main__":
    main()
