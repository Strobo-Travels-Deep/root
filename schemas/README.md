# `schemas/` — JSON Schemas (Draft 2020-12)

Two schemas describe the machine-readable artifacts in this repository.

## `manifest_v2.schema.json`

Validates simulation-output manifests in `data/runs/`. Three modes:

| Mode               | Payload shape                          | Used for                                |
|--------------------|----------------------------------------|-----------------------------------------|
| `single_run`       | `parameters` + `data` (1D detuning)    | Default α scans, zoom runs              |
| `sweep_1d`         | `fixed_parameters` + `sweep` + `runs`  | Parameter-sensitivity studies           |
| `state_comparison` | `parameters` + `states[]` + `spectra`  | Distinguishability analysis (WP-C)      |

Common envelope: `schema_version`, `mode`, `status`
(`exploratory` | `systematic`), `code_version`, `execution`, `provenance_hash`.

See [`../ARCHITECTURE.md`](../ARCHITECTURE.md) for the design rationale and
the boundary between `exploratory` (browser, Float32) and `systematic`
(Python, Float64) outputs.

## `experimental_params_v1.schema.json`

Validates calibrated lab-configuration documents (one per lab setup), e.g.
[`../wp-strobo-2p0/params/strobo2p0_params.json`](../wp-strobo-2p0/params/strobo2p0_params.json).

Each numeric quantity is wrapped in a `measured_value` object carrying:

- `value` (number)
- `unit` (SI or shorthand: `Hz`, `MHz`, `GHz`, `us`, `ns`, `quanta`, `rad`, `nm`, `1`)
- `stderr` (number or null)
- `source` (`calibration:` / `design:` / `derived:` / `literature:` followed by a citation)
- `notes` (optional free text)

The schema covers ion species, motional modes, beams, pulse sequences,
decoherence times, and the prepared initial state.

## Validation

```bash
pip install jsonschema
python -c "
import json, jsonschema
schema = json.load(open('schemas/manifest_v2.schema.json'))
data   = json.load(open('data/runs/alpha_3_default.json'))
jsonschema.validate(data, schema)
print('OK')
"
```

## `$id` convention

Both schemas declare a `$id` rooted at the repository's GitHub URL. These
are stable identifiers, not browse URLs — the JSON itself is authoritative.
