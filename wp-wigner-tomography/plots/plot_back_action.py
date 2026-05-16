"""WP-W v0.6 — motional back-action figure.

Grid: one row per input (vacuum / Fock |2⟩ / cat |α|=1.5), four
columns at the **peak** probe point:

  col 0  W(ρ_m^pre)                  — the state before the train
  col 1  W(ρ_m^post) ideal SDF       — unconditional (headline)
  col 2  W(ρ_m^post) native engine   — unconditional (headline)
  col 3  W conditional σ_y=+1, ideal — the cat-/coherence readout

Each post panel is annotated with the purity drop and the fidelity
to the pre-train state; the ideal-vs-native structural Wigner L¹
(scope §4a) is printed per row. The vacuum-gate PASS (back-action
analogue of P0/P1) is shown in the supertitle.

Usage:
    python wp-wigner-tomography/plots/plot_back_action.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np


INPUT_LABELS = {"vacuum": "vacuum", "fock2": r"Fock $|2\rangle$",
                "cat1.5": r"cat $|\alpha|{=}1.5$"}


def _recs(h5) -> list[dict]:
    out = []
    for k in h5:
        if not k.startswith("rec_"):
            continue
        g = h5[k]
        d = {a: g.attrs[a] for a in g.attrs}
        d["W"] = g["W"][:]
        d["cond_W_sy_plus"] = (g["cond_W_sy_plus"][:]
                               if "cond_W_sy_plus" in g else None)
        sx = g["cond/x+"].attrs if "cond/x+" in g else {}
        d["sx_branch_fid"] = float(sx["branch_fidelity"]) \
            if "branch_fidelity" in sx else None
        out.append(d)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--h5", type=str,
                    default="wp-wigner-tomography/numerics/back_action.h5")
    ap.add_argument("--output", type=str,
                    default="wp-wigner-tomography/plots/back_action.png")
    args = ap.parse_args()

    with h5py.File(args.h5, "r") as h5:
        ax = h5["alpha_axis"][:]
        recs = _recs(h5)
        W_pre = {k.split("/")[-1]: h5[f"W_pre/{k.split('/')[-1]}"][:]
                 for k in (f"W_pre/{i}" for i in
                           ("vacuum", "fock2", "cat1.5"))}
        gate_pass = bool(h5.attrs["gate_pass"])
        N = int(h5.attrs["N"])
        b0 = float(h5.attrs["beta0"])
        k_sb = int(h5.attrs["k_sideband"])
        nmax = int(h5.attrs["nmax"])

    inputs = ["vacuum", "fock2", "cat1.5"]
    extent = (ax[0], ax[-1], ax[0], ax[-1])

    fig, axes = plt.subplots(3, 4, figsize=(15.0, 11.0),
                             constrained_layout=True)
    col_titles = [r"$W(\rho_m^{\rm pre})$",
                  r"$W(\rho_m^{\rm post})$ ideal SDF",
                  r"$W(\rho_m^{\rm post})$ native engine",
                  r"$W$ cond. $\sigma_y{=}{+}1$ (ideal)"]

    for ri, inp in enumerate(inputs):
        peak = {r["leg"]: r for r in recs
                if r["input"] == inp and r["point"] == "peak"}
        ideal, native = peak["ideal"], peak["native"]
        panels = [W_pre[inp], ideal["W"], native["W"],
                  ideal["cond_W_sy_plus"]]
        vmax = max(np.max(np.abs(p)) for p in panels if p is not None)
        for ci, (W, ct) in enumerate(zip(panels, col_titles)):
            a = axes[ri, ci]
            if W is None:
                a.axis("off")
                continue
            im = a.imshow(W, origin="lower", extent=extent,
                          cmap="RdBu_r", vmin=-vmax, vmax=+vmax)
            if ri == 0:
                a.set_title(ct, fontsize=11)
            if ci == 0:
                a.set_ylabel(f"{INPUT_LABELS[inp]}\n" r"Im $\alpha$",
                             fontsize=11)
            a.set_xlabel(r"Re $\alpha$", fontsize=9)
            fig.colorbar(im, ax=a, shrink=0.82, pad=0.02)
        # annotate post panels with purity drop + F_pre
        for ci, r in ((1, ideal), (2, native)):
            axes[ri, ci].text(
                0.03, 0.97,
                f"drop {r['purity_drop']:.3f}\n"
                f"$F_{{\\rm pre}}$ {r['fidelity_to_pre']:.3f}\n"
                f"neg {r['neg_volume']:+.3f}",
                transform=axes[ri, ci].transAxes, va="top", ha="left",
                fontsize=8.5, color="black",
                bbox=dict(boxstyle="round", fc="white", alpha=0.7))
        l1 = float(ideal["ideal_vs_native_W_L1"])
        axes[ri, 2].text(
            0.97, 0.03, f"ideal–native\n$L^1$ = {l1:.3f}",
            transform=axes[ri, 2].transAxes, va="bottom", ha="right",
            fontsize=8.5, color="darkred",
            bbox=dict(boxstyle="round", fc="mistyrose", alpha=0.85))
        axes[ri, 1].text(
            0.97, 0.03,
            f"$\\sigma_x$-branch $F$ = {ideal['sx_branch_fid']:.3f}",
            transform=axes[ri, 1].transAxes, va="bottom", ha="right",
            fontsize=8.0, color="darkgreen",
            bbox=dict(boxstyle="round", fc="honeydew", alpha=0.85))

    gate_txt = ("vacuum gate PASS (machine precision)" if gate_pass
                else "vacuum gate FAIL")
    fig.suptitle(
        f"WP-W v0.6 — motional back-action  ·  peak probe "
        f"$|\\beta_{{\\rm tot}}|=N\\beta_0={N*b0:.2f}$  ·  "
        f"N={N}, $\\beta_0$={b0}, k={k_sb} (carrier), nmax={nmax}  ·  "
        f"{gate_txt}", fontsize=13)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
