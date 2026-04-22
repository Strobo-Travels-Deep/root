# Experimental parameter documents for strobo 2.0

This directory holds machine-readable parameter documents that describe
the calibrated experimental apparatus, in the form the simulation
consumes. The intent is that **the lab runs a calibration sequence and
emits a JSON file of this format, then the simulation runs against that
file — no hand-copying of numbers between notebook margins and
`run_sweep.py`.**

## Files

| File                         | Purpose                                                        |
|------------------------------|----------------------------------------------------------------|
| [strobo2p0_params.json](strobo2p0_params.json) | Current configuration for the strobo 2.0 sweep (v0.3, π/2-calibrated). |
| [load_params.py](load_params.py)       | Loader: JSON → engine kwargs. Also a CLI validator/summariser. |
| [../../schemas/experimental_params_v1.schema.json](../../schemas/experimental_params_v1.schema.json) | JSON Schema definition (v1.0). |

## Shape of the document

```
schema_version, document_id, calibration_date, operator, apparatus_reference
ion:                 species, qubit_transition
trap.motional_modes: omega_m, eta, <n>_thermal, ...              (per mode)
beams:               rabi, eta_per_mode, wavelength, ...         (per beam)
pulse_sequences:     beam, mode, n_pulses, pulse_duration,
                     inter_pulse_spacing, rabi_override,
                     analysis_phase_deg                          (per sequence)
decoherence:         spin_T2, motional_heating_rate, ...
initial_state:       spin_preparation, motional_preparation,
                     displacement_amplitudes
notes:               free-form audit trail
```

**Every quantity is `{value, unit, stderr, source, notes}`** — bare
floats are forbidden by design. `stderr` may be `null` (unknown) or `0`
(exact by construction). `source` names the calibration routine, the
design choice, or the literature citation that fixed the value.

## Using it

### As a CLI sanity check / summary

```sh
python3 load_params.py strobo2p0_params.json
```

Prints every measured value + its source, and for each pulse sequence
derives and prints the engine kwargs that it would produce.

### In Python

```python
from load_params import load_params, engine_kwargs_for_sequence

doc = load_params("strobo2p0_params.json")
kwargs = engine_kwargs_for_sequence(doc, "T2_short_pi2")
# kwargs -> omega_m, omega_r, eta, n_pulses, delta_t_us, t_sep_factor,
#           ac_phase_deg  (ready for stroboscopic_sweep.run_single)
```

### From the sweep runner

```sh
python3 ../numerics/run_sweep.py --params strobo2p0_params.json
```

`run_sweep.py` overrides its in-file defaults from the parameter
document and records the document's `document_id` + `calibration_date`
in the output manifest for provenance. Running without `--params`
keeps the current hard-coded defaults (identical to the committed v0.3
values).

## What belongs in a parameter document

**Yes**: calibrated lab parameters with a trace back to how they were
fixed (ω_m, η, Ω, δt, spacing, T2, n̄_th, |α| calibration amplitudes).

**No**: observation grids (detuning range, ϑ₀ density, Nmax) — those
are numerical-method choices and stay in `run_sweep.py` / plotting
scripts.

**No**: derived convenience values (Ω_eff, N·θ_pulse, Δφ_strobo) —
derive them at load time, don't store them.

**No**: observables / outputs — the manifest schema
(`schemas/manifest_v2.schema.json`) covers those.

## Adding another configuration

1. Copy `strobo2p0_params.json`, change `document_id` and
   `calibration_date`.
2. Edit the calibrated values. Keep `source` and `stderr` fields
   accurate — the history is the point.
3. Sanity-check with `python3 load_params.py your_new.json`.
4. Optionally run `python3 ../numerics/run_sweep.py --params your_new.json`
   to produce a companion sweep dataset.

## Version policy

The schema is versioned (`schema_version: "1.0"`). Additive changes
(new optional fields) can stay at `1.x`. Any breaking change requires
a `1.0 → 2.0` bump plus a `schemas/experimental_params_v2.schema.json`
file and a new `load_params_v2.py` loader — the old loader keeps
working for old documents.
