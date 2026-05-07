# `scripts/` — Python utilities

## `stroboscopic_sweep.py` — primary sweep engine

QuTiP/scipy-based engine. Emits manifests conforming to
[`../schemas/manifest_v2.schema.json`](../schemas/manifest_v2.schema.json)
with `status: "systematic"` and `precision: "float64"`.

```bash
python scripts/stroboscopic_sweep.py --mode single_run --alpha 3
python scripts/stroboscopic_sweep.py --mode sweep_1d \
    --sweep-param n_pulses --sweep-values 5,10,22,50
python scripts/stroboscopic_sweep.py --mode state_comparison
```

Outputs are written under `data/runs/` and indexed in
`data/runs/run_index.json`.

## `build_site.py` — static-site builder

Stitches the HTML pages (`index.html`, `tutorial.html`, …) and embeds the
default-run JSONs into `numerics.html`. Intended to be run after data
regeneration, before publishing the dossier.

## `export_hdf5.py`, `plot_detuning_harbour.py` — legacy

Retained for provenance with the older adaptive-learner HDF5 pipeline.
Not part of the current shipping path; do not depend on these for new work.

## `stroboscopic/` — engine modules

Internal package imported by `stroboscopic_sweep.py`. Not a public API.
