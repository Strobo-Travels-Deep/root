# WP-W — Wigner-Like Reconstruction in the Lamb–Dicke / Idealised-Train Limit

**Status:** v0.6 (2026-05-16; k=1 sideband follow-up 2026-05-17).
P0 + D2 + D3 + P1 + D4 cleared (ideal-SDF primitive in place; engine
bridge demonstrated); v0.5 doc-correction pass applied (ideal SDF is
FH20-style σ_x not σ_z, direct χ = ⟨σ_y⟩ − i⟨σ_z⟩ readout, §4 D4
native convention). **v0.6: Rank-1 motional back-action diagnostic
delivered** — `run_back_action.py` (vacuum analytic gate PASS at
machine precision, the back-action analogue of P0/P1) +
`plot_back_action.py`; ideal-vs-native structural Wigner L¹ as the
third bridge residual. The k=1 sideband follow-up adds
`back_action_k1.h5` / `back_action_k1.png` with a coherent
`|alpha|=2` witness. See [WORK-PROGRAM.md](./WORK-PROGRAM.md) §8,
[`notes/back_action_scope.md`](./notes/back_action_scope.md), and the
2026-05-16 / 2026-05-17 back-action logbook entries. D1 analytical
note ([`notes/analytic_chain.md`](./notes/analytic_chain.md))
standalone; all §4 deliverables complete.

This is a pointer file. The full work-program document is
[WORK-PROGRAM.md](./WORK-PROGRAM.md) (verified bibliography, design
decisions, deliverables, fidelity targets, conduct conventions).

## Folder layout

| Path | Contents |
|---|---|
| [`WORK-PROGRAM.md`](./WORK-PROGRAM.md) | The WP document. |
| [`numerics/`](./numerics/) | Runner scripts (`run_reach_ladder.py`, `run_p0_preflight.py`, `run_reconstruction_demo.py`, `run_p1_preflight.py`, `run_bridge_native.py`, `run_bridge_inversion.py`, **`run_back_action.py`** v0.6) + `_common.py` helpers + `test_back_action_helpers.py` (8 smoke locks) and their HDF5 + `wp_manifest_v1` outputs. |
| [`plots/`](./plots/) | Plot scripts (`plot_reach_ladder.py`, `plot_p0_preflight.py`, `plot_reconstruction_demo.py`, `plot_bridge.py`, **`plot_back_action.py`** v0.6) and their PNG outputs. |
| [`logbook/`](./logbook/) | Dated logbook entries with pre-registered expectations + comparison tables (per §5a discipline). |
| [`notes/`](./notes/) | Analytical derivations: [`analytic_chain.md`](./notes/analytic_chain.md) (D1, standalone) and [`back_action_scope.md`](./notes/back_action_scope.md) (v0.6 back-action scope, locked + executed). |
| [`refs/`](./refs/) | Per-paper extractions + contextual notes + lit-review tracker. |
| [`../notebooks/wpw_chi_to_wigner.ipynb`](../notebooks/wpw_chi_to_wigner.ipynb) | **Explanatory notebook** (repo-root `notebooks/`, source + `.executed` pair): the core chain — ideal σ_x SDF → direct χ readout → FFT Wigner; live analytic examples, the factor-of-two FFT convention, and the committed D3 reconstruction. Synthesis artefact — not a source of truth. |
| [`../notebooks/wpw_dirichlet_targeting.ipynb`](../notebooks/wpw_dirichlet_targeting.ipynb) | **Explanatory notebook** (repo-root `notebooks/`, source + `.executed` pair): how $(\delta,\varphi_\text{train},N)$ place a probe point β via the Dirichlet kernel, inverse-Dirichlet Cartesian targeting (5025/6561 reach cross-check), and the committed-P1 closed-loop on the ideal-SDF engine. Synthesis artefact — not a source of truth. |
| [`../notebooks/wpw_back_action.ipynb`](../notebooks/wpw_back_action.ipynb) | **Explanatory notebook** (repo-root `notebooks/`, source + `.executed` pair): plain-language definitions, the vacuum-gate machinery check, the readout-dependence figure, and the ideal-vs-native structural residual for v0.6. Synthesis artefact — not a source of truth. |
| [`../notebooks/wpw_native_bridge.ipynb`](../notebooks/wpw_native_bridge.ipynb) | **Explanatory notebook** (repo-root `notebooks/`, source + `.executed` pair): the capstone — why the native monochromatic Raman engine is a *different operator* than the FH20 SDF (structural, not calibration), via the three executed evidence layers P1 / D4-A / D4-B+back-action. Synthesis artefact — not a source of truth. |

## Quick start (execution)

```bash
# D2-D4 runners use paths relative to the WP-W folder.
cd wp-wigner-tomography
python numerics/run_reach_ladder.py        # D2 reach ladder (analytic)
python numerics/run_p0_preflight.py        # P0 self-consistency gate
python numerics/run_reconstruction_demo.py # D3 reconstruction on 7 states
python numerics/run_p1_preflight.py        # P1 engine-bridge sentinel
python numerics/run_bridge_native.py       # D4 Layer A — native vs WP-E
python numerics/run_bridge_inversion.py    # D4 Layer B — engine χ FFT (~18 min)
python numerics/test_back_action_helpers.py # v0.6 — 8 helper smoke locks
python plots/plot_reach_ladder.py
python plots/plot_p0_preflight.py
python plots/plot_reconstruction_demo.py
python plots/plot_bridge.py                # D4 bridge figure

# Back-action runners use repo-root-relative defaults.
cd ..
python wp-wigner-tomography/numerics/run_back_action.py # v0.6 carrier back-action (~2 min)
python wp-wigner-tomography/plots/plot_back_action.py   # v0.6 carrier figure
python wp-wigner-tomography/numerics/run_back_action.py --k-sideband 1 \
  --inputs vacuum coherent2 fock2 cat1.5
python wp-wigner-tomography/plots/plot_back_action.py \
  --h5 wp-wigner-tomography/numerics/back_action_k1.h5

# Explanatory synthesis notebooks (repo-root notebooks/; or just open in Jupyter).
jupyter nbconvert --to notebook --execute notebooks/wpw_chi_to_wigner.ipynb \
  --output wpw_chi_to_wigner.executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/wpw_dirichlet_targeting.ipynb \
  --output wpw_dirichlet_targeting.executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/wpw_back_action.ipynb \
  --output wpw_back_action.executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/wpw_native_bridge.ipynb \
  --output wpw_native_bridge.executed.ipynb
```

Each runner writes an HDF5 artefact and a sidecar
`*.manifest.json` envelope per [schemas/wp_manifest_v1.schema.json](../schemas/wp_manifest_v1.schema.json).

## Status of deliverables (§4)

| D | name | status |
|---|---|---|
| D1 | analytical note | ✅ standalone derivation [`notes/analytic_chain.md`](./notes/analytic_chain.md) (σ_x SDF + direct χ → Dirichlet map → FFT/Wigner → bridge → P0/P1/D4 anchors) |
| D2 | reach ladder | ✅ runner + outputs + figure |
| D3 | reconstruction demo | ✅ PASS — all six gated states clear §7#5; deciding-state criterion satisfied |
| D4 | WP-E / WP-TOM bridge | ✅ Layer A PASS @ machine precision; Layer B substantive PASS (engine χ ↔ analytic χ at $3.75\times10^{-4}$ on 81² fine grid; centroid sub-pixel) |
| D5 | logbook | live; D2/P0, D3, ideal-SDF, D4 (all 2026-05-15), close-out + ranked follow-ups, [`2026-05-16-back-action-scope.md`](./logbook/2026-05-16-back-action-scope.md) (v0.6 scope), [`2026-05-16-back-action-run.md`](./logbook/2026-05-16-back-action-run.md) (v0.6 execution + post-run review), [`2026-05-17-back-action-k1-sideband.md`](./logbook/2026-05-17-back-action-k1-sideband.md) (k=1 sideband follow-up) |
| P0 | analytic-grid gate | ✅ PASS (vacuum + coherent $|\alpha=1\rangle$) |
| P1 | engine-bridge gate | ✅ PASS at $10^{-14}$ (vacuum + coherent $|\alpha=1\rangle$, N=20 and 80, FH20 σ_x SDF) |
| v0.6 | back-action diagnostic | ✅ Rank-1 follow-up. Vacuum analytic gate **PASS at machine precision** (purity ½(1+e⁻\|β\|²) Δ≤2e-14, fidelity e⁻\|β\|²/4 Δ≤1.5e-14, W vs W_mixed_cat(β_tot/2) Δ≤1.3e-10 — the P0/P1 analogue); ideal σ_x-branch fidelity = 1.0000 vs native ≪1 (§7#3 structural bridge quantified); ideal-vs-native Wigner L¹ = third bridge residual. k=1 sideband follow-up executed on 2026-05-17 with coherent `|alpha|=2` witness (`F_pre=0.0486`, σ_x-branch `F=0.0372` at the peak native point). |
