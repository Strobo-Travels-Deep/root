#!/usr/bin/env python3
"""Generate heatmap figures for strobo 2.0 sweep.

Each figure: 2 rows (T1, T2) x 3 cols (alpha = 1, 3, 4.5), sharing a
common colorbar. Five observables -> five figures, 30 heatmap panels
total:

    01_coherence_contrast.png   |C| = sqrt(sz_A^2 + sz_B^2)
    02_arg_C.png                arg C = atan2(sz_B, sz_A)  [deg]
    03_sigma_z.png              <sigma_z> at canonical phi = 0
    04_delta_n_phi0.png         delta<n> at phi = 0        (raw quanta)
    05_delta_n_phi_pi2.png      delta<n> at phi = pi/2     (raw quanta)
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
PLOTS = HERE.parent / "plots"
PLOTS.mkdir(exist_ok=True)


def load() -> tuple[dict, dict]:
    data = np.load(HERE / "strobo2p0_data.npz")
    manifest = json.loads((HERE / "strobo2p0_manifest.json").read_text())
    return data, manifest


def compute_derived(data, tag: str, alpha: float) -> dict:
    sz_A = data[f"{tag}_sz_A"]
    sz_B = data[f"{tag}_sz_B"]
    nbar_A = data[f"{tag}_nbar_A"]
    nbar_B = data[f"{tag}_nbar_B"]
    coh = np.hypot(sz_A, sz_B)
    arg = np.degrees(np.arctan2(sz_B, sz_A))  # [-180, 180]
    dn_A = nbar_A - alpha ** 2
    dn_B = nbar_B - alpha ** 2
    return dict(coh=coh, arg=arg, sz=sz_A, dn_A=dn_A, dn_B=dn_B)


def make_figure(data, observable_key: str, title: str, cmap: str,
                vmin: float | None, vmax: float | None, out_name: str,
                cbar_label: str, center_zero: bool = False) -> None:
    trains = [("T1", "T1:  N=3, $\\delta t$=100 ns"), ("T2", "T2:  N=7, $\\delta t$=50 ns")]
    alphas = [1.0, 3.0, 4.5]

    # Collect all panels to find common limits if requested
    panels = {}
    for train_label, _ in trains:
        for alpha in alphas:
            tag = f"{train_label}_alpha{alpha:g}".replace(".", "p")
            panels[(train_label, alpha)] = compute_derived(data, tag, alpha)[observable_key]

    if vmin is None or vmax is None:
        if center_zero:
            amax = max(abs(p).max() for p in panels.values())
            vmin = vmin if vmin is not None else -amax
            vmax = vmax if vmax is not None else +amax
        else:
            vmin = min(p.min() for p in panels.values()) if vmin is None else vmin
            vmax = max(p.max() for p in panels.values()) if vmax is None else vmax

    det_mhz = data["DET_MHZ"]
    theta0_deg = data["THETA0_DEG"]
    # For periodic axis display, append 360 row
    theta_ext = np.concatenate([theta0_deg, [360.0]])

    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.5), sharex=True, sharey=True,
                             constrained_layout=True)
    for r, (train_label, train_title) in enumerate(trains):
        for c, alpha in enumerate(alphas):
            ax = axes[r, c]
            Z = panels[(train_label, alpha)]
            Z_ext = np.concatenate([Z, Z[:1]], axis=0)
            im = ax.pcolormesh(det_mhz, theta_ext, Z_ext,
                               shading="auto", cmap=cmap, vmin=vmin, vmax=vmax)
            # Mark motional sideband lines
            for k in range(-7, 8):
                d = k * 1.306
                if abs(d) <= 10.0:
                    ax.axvline(d, color="white", lw=0.4, alpha=0.35)
            if r == 0:
                ax.set_title(f"$|\\alpha| = {alpha}$")
            if c == 0:
                ax.set_ylabel(f"{train_title}\n$\\vartheta_0$ [deg]")
            if r == 1:
                ax.set_xlabel("detuning $\\delta_0/(2\\pi)$ [MHz]")
            ax.set_yticks([0, 90, 180, 270, 360])
            ax.set_xticks(np.arange(-10, 11, 2.5))

    cbar = fig.colorbar(im, ax=axes, shrink=0.85, aspect=30, pad=0.02)
    cbar.set_label(cbar_label)
    fig.suptitle(title, fontsize=13)
    out_path = PLOTS / out_name
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path.name}")


def main() -> None:
    data, manifest = load()
    print("strobo 2.0 plots")
    print(f"  Loaded: det={len(data['DET_MHZ'])} pts,  theta0={len(data['THETA0_DEG'])} pts")
    print(f"  Output dir: {PLOTS}")

    make_figure(
        data, "coh",
        title="Coherence contrast $|C| = \\sqrt{a_x^2 + a_y^2}$   (strobo 2.0)",
        cmap="viridis", vmin=0.0, vmax=1.0,
        out_name="01_coherence_contrast.png",
        cbar_label="$|C|$",
    )
    make_figure(
        data, "arg",
        title="Analysis phase that maximises $\\langle\\sigma_z\\rangle$:  $\\arg C = \\mathrm{atan2}(a_y, a_x)$",
        cmap="twilight", vmin=-180.0, vmax=+180.0,
        out_name="02_arg_C.png",
        cbar_label="$\\arg C$  [deg]",
    )
    make_figure(
        data, "sz",
        title="$\\langle\\sigma_z\\rangle$ at canonical analysis phase $\\varphi = 0$",
        cmap="RdBu_r", vmin=-1.0, vmax=+1.0,
        out_name="03_sigma_z.png",
        cbar_label="$\\langle\\sigma_z\\rangle$",
        center_zero=True,
    )
    make_figure(
        data, "dn_A",
        title="Back-action $\\delta\\langle n\\rangle = \\langle n\\rangle_\\mathrm{fin} - |\\alpha|^2$  at  $\\varphi = 0$",
        cmap="PRGn", vmin=None, vmax=None, center_zero=True,
        out_name="04_delta_n_phi0.png",
        cbar_label="$\\delta\\langle n\\rangle$  (quanta)",
    )
    make_figure(
        data, "dn_B",
        title="Back-action $\\delta\\langle n\\rangle$  at  $\\varphi = \\pi/2$",
        cmap="PRGn", vmin=None, vmax=None, center_zero=True,
        out_name="05_delta_n_phi_pi2.png",
        cbar_label="$\\delta\\langle n\\rangle$  (quanta)",
    )


if __name__ == "__main__":
    main()
