# WP-W — Wigner-Like Reconstruction in the Lamb–Dicke / Idealised-Train Limit

**Status:** v0.4 design closed; execution started 2026-05-15. P0 + D2 + D3 cleared.

This is a pointer file. The full work-program document is
[WORK-PROGRAM.md](./WORK-PROGRAM.md) (verified bibliography, design
decisions, deliverables, fidelity targets, conduct conventions).

## Folder layout

| Path | Contents |
|---|---|
| [`WORK-PROGRAM.md`](./WORK-PROGRAM.md) | The WP document. |
| [`numerics/`](./numerics/) | Runner scripts (`run_reach_ladder.py`, `run_p0_preflight.py`) and their HDF5 + `wp_manifest_v1` outputs. |
| [`plots/`](./plots/) | Plot scripts (`plot_reach_ladder.py`, `plot_p0_preflight.py`) and their PNG outputs. |
| [`logbook/`](./logbook/) | Dated logbook entries with pre-registered expectations + comparison tables (per §5a discipline). |
| [`notes/`](./notes/) | Analytical derivations (D1 — to be written). |
| [`refs/`](./refs/) | Per-paper extractions + contextual notes + lit-review tracker. |

## Quick start (execution)

```bash
cd wp-wigner-tomography
python numerics/run_reach_ladder.py        # D2 reach ladder (analytic)
python numerics/run_p0_preflight.py        # P0 self-consistency gate
python numerics/run_reconstruction_demo.py # D3 reconstruction on 7 states
python plots/plot_reach_ladder.py
python plots/plot_p0_preflight.py
python plots/plot_reconstruction_demo.py
```

Each runner writes an HDF5 artefact and a sidecar
`*.manifest.json` envelope per [schemas/wp_manifest_v1.schema.json](../schemas/wp_manifest_v1.schema.json).

## Status of deliverables (§4)

| D | name | status |
|---|---|---|
| D1 | analytical note | pending (`notes/analytic_chain.md`) |
| D2 | reach ladder | ✅ runner + outputs + figure |
| D3 | reconstruction demo | ✅ PASS — all six gated states clear §7#5; deciding-state criterion satisfied |
| D4 | WP-E / WP-TOM bridge | gated on the FH20-style `ideal_sdf` primitive |
| D5 | logbook | live; entries [`2026-05-15-D2-and-P0.md`](./logbook/2026-05-15-D2-and-P0.md), [`2026-05-15-D3-reconstruction.md`](./logbook/2026-05-15-D3-reconstruction.md) |
| P0 | analytic-grid gate | ✅ PASS (vacuum + coherent $|\alpha=1\rangle$) |
| P1 | engine-bridge gate | pending — gated on the FH20-style `ideal_sdf` primitive |
