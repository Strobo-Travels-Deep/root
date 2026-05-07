# `schemas/` — JSON Schemas (Draft 2020-12)

Three schemas describe the machine-readable artifacts in this repository:
one for the dossier's default simulation runs, one for calibrated lab
configurations, and one for Work-Package-level numerics outputs (sidecar
manifests for binary `.npz` / `.h5` artifacts).

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

## `wp_manifest_v1.schema.json`

Validates Work-Package run manifests — provenance sidecars for the binary
data files (`.npz`, `.h5`) inside `wp-*/numerics/`. The envelope mirrors
`manifest_v2`'s shape:

`schema_version`, `wp_id`, `code_version`, `runner_version` (optional),
`repository`, `parameter_document` (optional ref into
`experimental_params_v1`), `artifact` (`{path, format, bytes, sha256}`),
`execution` (`{timestamp, engine, precision, elapsed_s}`),
`provenance_hash`, and a free-form `payload` for the WP-specific
scientific content (physical_parameters, grid, observables, tags, …).

The `artifact.sha256` field is the SHA-256 of the data file's raw bytes;
the top-level `provenance_hash` is the SHA-256 over a canonical JSON form
of `{wp_id, code_version, runner_version, payload, artifact_sha256}` and
so binds the manifest to the specific data file it describes.

| WP                              | Status                            |
|---------------------------------|-----------------------------------|
| `wp-strobo-2p0`                 | Adopted (run_sweep.py emits v1.0) |
| `wp-hasse-reproduction`         | Pending — `.h5` files have no sidecar manifest |
| `wp-phase-contrast-maps`        | Pending — `.h5` files have no sidecar manifest |
| `wp-strong-weak-coastline`      | Pending — `.h5` files have no sidecar manifest |

When a WP adopts the schema, its runner should emit a `<artifact>.meta.json`
(or single shared manifest if the WP produces one batch artifact) alongside
each `.h5` / `.npz`, validating against `wp_manifest_v1.schema.json`.

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
