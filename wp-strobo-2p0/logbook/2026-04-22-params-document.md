# 2026-04-22 — Experimental parameter document format

**Status:** schema v1.0 adopted; strobo 2.0 v0.3 parameters migrated;
`run_sweep.py` consumes the document.
**Operator:** uwarring (with Claude).

-----

## 1. Motivation

Experiment-simulation comparison requires one authoritative source of
truth for the calibrated apparatus. Over the last day of strobo 2.0
work we accumulated three separate Rabi-rate values, two separate η
values consistent with Hasse 2024, and various handwave statements
about what the "lab uses" for Δt. Each sat in a different logbook
entry or hard-coded constant at the top of a Python file. That is
unsustainable as the simulation-to-experiment feedback loop tightens.

The fix: **the lab emits one JSON file per calibration; the simulation
reads that file; no hand-copying**. This entry records the schema
design and the v0.3 migration.

## 2. Design

### 2.1 Three invariants

- **Every number is `{value, unit, stderr, source}`**. Bare floats are
  forbidden at the schema level — a file that parses must carry
  provenance for every quantity it declares.
- **Hierarchical by physical scope** — `ion → trap.modes → beams →
  pulse_sequences → decoherence → initial_state`. Each level maps 1-to-1
  onto a lab reality (an ion, a trap mode, a beam, a pulse sequence…)
  so the document is legible as a list of calibration facts rather than
  an opaque blob.
- **Schema is versioned** (`schema_version: "1.0"`). Additive changes
  stay at `1.x`; breaking changes bump to `2.0` and get a new schema
  file + new loader. Old loaders keep working for old documents.

### 2.2 What is in / what is out

**In:** calibrated lab quantities — ω_m, η, Ω, beam wavelengths, pulse
durations, inter-pulse spacing, spin T2, motional heating, coherent
displacement amplitudes.

**Out (numerical method choices, kept in runner):** detuning range,
grid resolution, Fock-cutoff N_max, which analysis-phase cuts to
compute.

**Out (outputs, covered by manifest schema):** observable arrays,
code version, elapsed time, hash.

**Out (derived values):** Ω_eff, N·θ_pulse, Δφ_strobo, t_sep_factor
— the loader computes these at read time.

### 2.3 Rabi override per sequence

One subtle design choice: a pulse sequence may override the beam's
default Ω via an optional `rabi_override` field. This accommodates the
strobo 2.0 v0.3 convention where each train is tuned to a full π/2
analysis rotation (different Ω per train), without forcing us to
invent fictional "beams" for each sequence.

## 3. Migration

The v0.3 parameter set is now encoded in
[../params/strobo2p0_params.json](../params/strobo2p0_params.json). The
loader ([../params/load_params.py](../params/load_params.py)) confirms
both trains round-trip correctly:

```
T1_short_pi2:  Omega/(2pi) = 0.9008 MHz,  N*Omega*DW*dt = 1.5705 rad  (target pi/2 = 1.5708)  -> pi/2-calibrated
T2_short_pi2:  Omega/(2pi) = 0.7722 MHz,  N*Omega*DW*dt = 1.5707 rad  (target pi/2 = 1.5708)  -> pi/2-calibrated
```

(Small deficits — a few parts in 10³ — are from rounding the JSON Ω
values to 4 decimals; sufficient for the simulation.)

## 4. Integration with `run_sweep.py`

[`run_sweep.py`](../numerics/run_sweep.py) now accepts
`--params <path.json>`. When given, it:

1. Loads the document, validates `schema_version`.
2. Reads `omega_m`, `eta`, and per-sequence `omega_r`, `n_pulses`,
   `delta_t_us`, `t_sep_factor` from the document.
3. Enforces that all sequences share the same η and `t_sep_factor`
   (the strobo 2.0 sweep mixes T1 and T2 on one mode; separate
   configurations would be separate runs).
4. Records `{path, document_id, calibration_date}` in the output
   manifest under `parameter_document`, so any downstream analysis
   can trace back to the exact calibration file.

Running without `--params` keeps the previously-committed in-file
defaults, which exactly match `strobo2p0_params.json` by construction.

## 5. Not yet done

- **No re-run of the sweep under `--params`.** The committed v0.3
  `strobo2p0_data.npz` was produced from the in-file constants; the
  round-trip through the JSON would produce the same data to rounding
  precision. A future commit can re-run via `--params` and confirm
  the NPZ is byte-identical (expected) or bit-level close.
- **Rabi reconciliation memo** still lives in the logbook — it is
  now redundant with the `source` fields in the JSON. Kept as a
  narrative history entry rather than the single source of truth.
- **No schema enforcement at load time.** The loader validates
  `schema_version`, unit strings, and cross-references (beam/mode
  keys), but not the full JSON-Schema contract. A `jsonschema`
  dependency would cover this; not added to avoid a new runtime
  dependency on CI.
- **No sibling-WP migration.** WP-E and WP-C still use their own
  conventions; the schema is general enough to absorb them if/when
  those WPs adopt the same pattern.

## 6. Files committed by this entry

- [schemas/experimental_params_v1.schema.json](../../schemas/experimental_params_v1.schema.json)
- [params/strobo2p0_params.json](../params/strobo2p0_params.json)
- [params/load_params.py](../params/load_params.py)
- [params/README.md](../params/README.md)
- Changes to [numerics/run_sweep.py](../numerics/run_sweep.py) to
  accept `--params`.

-----

*v0.1 2026-04-22 — initial entry.*
