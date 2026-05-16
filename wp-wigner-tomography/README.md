# WP-W — Wigner-Like Reconstruction in the Lamb–Dicke / Idealised-Train Limit

**Status:** v0.6 (2026-05-16). P0 + D2 + D3 + P1 + D4 cleared (ideal-SDF primitive in place; engine bridge demonstrated); v0.5 doc-correction pass applied (ideal SDF is FH20-style σ_x not σ_z, direct χ = ⟨σ_y⟩ − i⟨σ_z⟩ readout, §4 D4 native convention). **v0.6: Rank-1 motional back-action diagnostic delivered** — `run_back_action.py` (vacuum analytic gate PASS at machine precision, the back-action analogue of P0/P1) + `plot_back_action.py`; ideal-vs-native structural Wigner L¹ as the third bridge residual. See [WORK-PROGRAM.md](./WORK-PROGRAM.md) §8, [`notes/back_action_scope.md`](./notes/back_action_scope.md), and the two 2026-05-16 back-action logbook entries. D1 analytical note ([`notes/analytic_chain.md`](./notes/analytic_chain.md)) standalone; all §4 deliverables complete.

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

## Quick start (execution)

```bash
cd wp-wigner-tomography
python numerics/run_reach_ladder.py        # D2 reach ladder (analytic)
python numerics/run_p0_preflight.py        # P0 self-consistency gate
python numerics/run_reconstruction_demo.py # D3 reconstruction on 7 states
python numerics/run_p1_preflight.py        # P1 engine-bridge sentinel
python numerics/run_bridge_native.py       # D4 Layer A — native vs WP-E
python numerics/run_bridge_inversion.py    # D4 Layer B — engine χ FFT (~18 min)
python numerics/test_back_action_helpers.py # v0.6 — 8 helper smoke locks
python numerics/run_back_action.py         # v0.6 — back-action (vacuum gate + sweep, ~2 min)
python plots/plot_reach_ladder.py
python plots/plot_p0_preflight.py
python plots/plot_reconstruction_demo.py
python plots/plot_bridge.py                # D4 bridge figure
python plots/plot_back_action.py           # v0.6 back-action figure
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
| D5 | logbook | live; D2/P0, D3, ideal-SDF, D4 (all 2026-05-15), close-out + ranked follow-ups, [`2026-05-16-back-action-scope.md`](./logbook/2026-05-16-back-action-scope.md) (v0.6 scope), [`2026-05-16-back-action-run.md`](./logbook/2026-05-16-back-action-run.md) (v0.6 execution + post-run review) |
| P0 | analytic-grid gate | ✅ PASS (vacuum + coherent $|\alpha=1\rangle$) |
| P1 | engine-bridge gate | ✅ PASS at $10^{-14}$ (vacuum + coherent $|\alpha=1\rangle$, N=20 and 80, FH20 σ_x SDF) |
| v0.6 | back-action diagnostic | ✅ Rank-1 follow-up. Vacuum analytic gate **PASS at machine precision** (purity ½(1+e⁻\|β\|²) Δ≤2e-14, fidelity e⁻\|β\|²/4 Δ≤1.5e-14, W vs W_mixed_cat(β_tot/2) Δ≤1.3e-10 — the P0/P1 analogue); ideal σ_x-branch fidelity = 1.0000 vs native ≪1 (§7#3 structural bridge quantified); ideal-vs-native Wigner L¹ = third bridge residual |
