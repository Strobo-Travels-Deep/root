# WP-W — Wigner-Like Reconstruction in the Lamb–Dicke / Idealised-Train Limit

**Status:** v0.4 design closed; execution started 2026-05-15. P0 + D2 + D3 + P1 + D4 cleared (ideal-SDF primitive in place; engine bridge demonstrated). v0.5 doc correction pass queued (5 items, see [`logbook/2026-05-15-D4-bridge.md`](./logbook/2026-05-15-D4-bridge.md) §4).

This is a pointer file. The full work-program document is
[WORK-PROGRAM.md](./WORK-PROGRAM.md) (verified bibliography, design
decisions, deliverables, fidelity targets, conduct conventions).

## Folder layout

| Path | Contents |
|---|---|
| [`WORK-PROGRAM.md`](./WORK-PROGRAM.md) | The WP document. |
| [`numerics/`](./numerics/) | Runner scripts (`run_reach_ladder.py`, `run_p0_preflight.py`, `run_reconstruction_demo.py`, `run_p1_preflight.py`, `run_bridge_native.py`, `run_bridge_inversion.py`) and their HDF5 + `wp_manifest_v1` outputs. |
| [`plots/`](./plots/) | Plot scripts (`plot_reach_ladder.py`, `plot_p0_preflight.py`, `plot_reconstruction_demo.py`, `plot_bridge.py`) and their PNG outputs. |
| [`logbook/`](./logbook/) | Dated logbook entries with pre-registered expectations + comparison tables (per §5a discipline). |
| [`notes/`](./notes/) | Analytical derivations (D1 — to be written). |
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
python plots/plot_reach_ladder.py
python plots/plot_p0_preflight.py
python plots/plot_reconstruction_demo.py
python plots/plot_bridge.py                # D4 bridge figure
```

Each runner writes an HDF5 artefact and a sidecar
`*.manifest.json` envelope per [schemas/wp_manifest_v1.schema.json](../schemas/wp_manifest_v1.schema.json).

## Status of deliverables (§4)

| D | name | status |
|---|---|---|
| D1 | analytical note | pending (`notes/analytic_chain.md`) |
| D2 | reach ladder | ✅ runner + outputs + figure |
| D3 | reconstruction demo | ✅ PASS — all six gated states clear §7#5; deciding-state criterion satisfied |
| D4 | WP-E / WP-TOM bridge | ✅ Layer A PASS @ machine precision; Layer B substantive PASS (engine χ ↔ analytic χ at $3.75\times10^{-4}$ on 81² fine grid; centroid sub-pixel) |
| D5 | logbook | live; entries [`2026-05-15-D2-and-P0.md`](./logbook/2026-05-15-D2-and-P0.md), [`2026-05-15-D3-reconstruction.md`](./logbook/2026-05-15-D3-reconstruction.md), [`2026-05-15-ideal-sdf-primitive.md`](./logbook/2026-05-15-ideal-sdf-primitive.md), [`2026-05-15-D4-bridge.md`](./logbook/2026-05-15-D4-bridge.md) |
| P0 | analytic-grid gate | ✅ PASS (vacuum + coherent $|\alpha=1\rangle$) |
| P1 | engine-bridge gate | ✅ PASS at $10^{-14}$ (vacuum + coherent $|\alpha=1\rangle$, N=20 and 80, FH20 σ_x SDF) |
