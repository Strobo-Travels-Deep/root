# `data/` — Simulation outputs

Two layers live here:

## `data/runs/` — current, shipping

JSON simulation manifests conforming to
[`schemas/manifest_v2.schema.json`](../schemas/manifest_v2.schema.json).

- `run_index.json` — canonical index of all included runs (id, alpha, label, path).
- `alpha_{0,1,3,5}_default.json` — coherent-state default scans, 22 pulses, N_max = 50.
- `carrier_zoom_alpha0.json`, `red_sb1_alpha0.json`, `blue_sb1_alpha0.json` — zoom scans.
- `full_alpha1_fine.json` — fine α = 1 scan (301 pts).
- `sideband_comb_alpha0.json` — full sideband comb (401 pts).

Each manifest carries: `schema_version`, `mode`, `status` (`exploratory` /
`systematic`), `code_version`, `repository`, `execution.{engine,precision,timestamp}`,
`provenance_hash` (SHA-256), and a `payload` whose shape is mode-specific.

To consume a run programmatically:

```python
import json
from pathlib import Path

idx = json.loads(Path("data/runs/run_index.json").read_text())
for r in idx["runs"]:
    run = json.loads(Path(r["path"]).read_text())
    # validate against schemas/manifest_v2.schema.json before trusting fields
```

## `data/alpha_{0,1,3,5}/` — archival, non-shipping

These directories were produced by an earlier adaptive-learner HDF5 pipeline.
The `.h5` files themselves are **not included** in this repository. The
top-level `data/manifest.json` is a stub retained only for provenance
continuity and is explicitly marked `_status: "ARCHIVAL — NON-SHIPPING"`.

Do not author new code that consumes `data/manifest.json`. Use
`data/runs/run_index.json` instead.
