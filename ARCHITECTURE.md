# Simulation Architecture — Design Note

**Breakwater Dossier · v0.8**
**Date:** 2026-03-23
**Status:** Council-cleared (Guardian, Architect, Integrator)

-----

## Boundary Rule

> The browser instrument remains the primary exploratory interface for single runs
> and bounded 1D sweeps. Systematic multi-parameter surveys are delegated to a
> Python/QuTiP sweep engine. Comparative state-analysis is treated as a distinct
> mode with its own manifest structure and validation logic.

This boundary is **hard**. Browser output is labelled `exploratory`. Python output
is labelled `systematic`. The distinction is not about correctness of the physics
engine (both use the same Hamiltonian and exact Fock-basis expm) but about
**numerical status**: browser/GPU uses Float32 on the hot path; Python uses Float64
throughout. When students interpret small differences (purity 0.997 vs. 0.995,
distinguishability margins), they must use the systematic engine.

-----

## Three Modes

### Mode 1: Single Run (interactive exploratory)

**Execution:** Browser (simulate.html)
**Purpose:** Exploration, teaching, hypothesis formation, quick checks.
**Input:** One parameter set via sliders/inputs.
**Output:** 1D detuning spectrum with observables. Single provenance hash.
**Manifest type:** `single_run` (existing schema v1.2).
**Status label:** `exploratory`
**Constraints:** One run. N_max ≤ 80. N_pts ≤ 801. No batching.

### Mode 2: 1D Sweep (bounded survey)

**Execution:** Browser (simulate.html, sweep tab) for ≤ 20 parameter values.
Python (`stroboscopic_sweep.py`) for larger sweeps or multi-dimensional grids.
**Purpose:** Parameter sensitivity studies. WP-B (N_p sweep), WP-A.3 (η sweep).
**Input:** One sweep parameter with range + step. All other parameters fixed.
Fixed detuning grid per run.
**Output:** Array of 1D spectra indexed by sweep parameter value.
**Manifest type:** `sweep_1d`
**Status label:** `exploratory` (browser) or `systematic` (Python)
**Constraints (browser):** ≤ 20 sweep values. Single sweep dimension.
Auto-export to Python config if threshold exceeded.
**Constraints (Python):** No artificial limit. Multi-dimensional grids supported
via nested `sweep_1d` or dedicated `sweep_nd` extension.

### Mode 3: State Comparison (distinguishability analysis)

**Execution:** Browser (simulate.html, compare tab) for ≤ 6 states.
Python for systematic state families.
**Purpose:** WP-C. Forward measurement comparison. Spectral distinguishability.
Observational injectivity testing.
**Input:** List of initial motional states (from gallery or custom).
One fixed parameter set. One fixed detuning grid.
**Output:** Overlaid spectra. Pairwise distance matrix (trace distance or
integrated spectral difference). Rank/sensitivity summary.
**Manifest type:** `state_comparison`
**Status label:** `exploratory` (browser) or `systematic` (Python)
**Constraints (browser):** ≤ 6 states from gallery. Fixed parameter set.

**Note:** This mode is *distinguishability analysis*, not tomography. It tests
whether the measurement map M: ρ → spectrum is injective over a target state
family. It does not reconstruct ρ from data. The word "tomography" is reserved
for the full inverse problem (WP-C.3 and beyond).

-----

## Manifest Schema

All three modes share a common envelope with mode-specific payload.

### Common envelope

```json
{
  "schema_version": "2.0",
  "mode": "single_run | sweep_1d | state_comparison",
  "status": "exploratory | systematic",
  "code_version": "0.8.0",
  "repository": "https://github.com/threehouse-plus-ec/open-research-platform",
  "source_paper": { ... },
  "endorsement_marker": "Local candidate framework",
  "execution": {
    "timestamp": "ISO 8601",
    "engine": "browser-js | browser-webgpu | python-scipy | python-qutip",
    "precision": "float32 | float64",
    "elapsed_s": 0.0
  },
  "provenance_hash": "SHA-256 hex",
  "payload": { ... }
}
```

### Mode: single_run

```json
"payload": {
  "parameters": { ... },
  "derived": { ... },
  "convergence": { "max_fock_leakage": 0.0, "converged": true },
  "data": {
    "detuning": [...],
    "sigma_x": [...], "sigma_y": [...], "sigma_z": [...],
    "coherence": [...], "entropy": [...],
    "nbar": [...], "mot_purity": [...], "mot_fidelity": [...]
  }
}
```

Backward compatible with schema v1.2 (existing runs).

### Mode: sweep_1d

```json
"payload": {
  "fixed_parameters": { ... },
  "sweep": {
    "parameter": "eta | alpha | n_pulses | omega_r | ...",
    "values": [0.1, 0.2, 0.3, ...],
    "n_values": 10
  },
  "derived_per_value": [{ "omega_eff": ..., ... }, ...],
  "convergence_per_value": [{ "max_fock_leakage": ..., "converged": ... }, ...],
  "data": {
    "detuning": [...],
    "runs": [
      { "sweep_value": 0.1, "sigma_x": [...], ... },
      { "sweep_value": 0.2, "sigma_x": [...], ... },
      ...
    ]
  },
  "summary": {
    "contrast_z": [...],
    "coherence_fwhm": [...],
    "peak_purity": [...],
    "peak_fidelity": [...]
  }
}
```

The hash covers: code_version, fixed_parameters, sweep definition, all output arrays.

### Mode: state_comparison

```json
"payload": {
  "parameters": { ... },
  "states": [
    { "id": "ground", "label": "Ground |0⟩", "alpha": 0, "squeeze_r": 0, ... },
    { "id": "coherent_3", "label": "Coherent α=3", "alpha": 3, ... },
    { "id": "fock_3", "label": "Fock |3⟩", "fock_n": 3, ... },
    { "id": "squeezed_1", "label": "Squeezed r=1.0", "squeeze_r": 1.0, ... },
    ...
  ],
  "convergence_per_state": [{ ... }, ...],
  "data": {
    "detuning": [...],
    "spectra": [
      { "state_id": "ground", "sigma_x": [...], ... },
      { "state_id": "coherent_3", "sigma_x": [...], ... },
      ...
    ]
  },
  "distinguishability": {
    "metric": "integrated_spectral_distance | trace_distance_proxy",
    "matrix": [[0, 0.34, ...], [0.34, 0, ...], ...],
    "state_ids": ["ground", "coherent_3", ...]
  }
}
```

-----

## Implementation Phases

### Phase 1 (now)
- Formalise this architecture note ✓
- Define manifest schemas (above) ✓
- Build `stroboscopic_sweep.py`: real QuTiP implementation with single_run,
  sweep_1d, and state_comparison modes
- Add browser → Python config export from simulate.html

### Phase 2
- Add lightweight 1D sweep tab to simulate.html (≤ 20 values, one parameter)
- Strict "exploratory" labelling on all browser output
- Sweep parameter selector: dropdown from N_p, α, η, Ω, ω_m

### Phase 3
- Add state comparison tab to simulate.html (≤ 6 states from gallery)
- Pairwise distance matrix display
- Only after Phase 1 Python engine is validated against browser single-run output

-----

## Boundary Rules (Summary)

| Rule | Rationale |
|------|-----------|
| Browser output is always labelled `exploratory` | Float32 GPU path; not publication-grade |
| Python output is labelled `systematic` | Float64; reproducible; suitable for WP deliverables |
| Browser sweep ≤ 20 values, 1 dimension | Runtime cap; prevents abandoned runs |
| State comparison ≤ 6 states in browser | UI clarity; larger families → Python |
| A sweep is not "many single runs glued together" | It is a higher-level artefact with its own manifest |
| No 2D browser heatmaps in this iteration | Deferred until Python engine is validated |
| "Tomography" reserved for inverse problem | WP-C mode is "distinguishability analysis" |

-----

## File Layout

```
scripts/
  stroboscopic_sweep.py     — Python/QuTiP sweep engine (Phase 1)
  export_hdf5.py            — legacy HDF5 exporter (retained)
schemas/
  manifest_v2.schema.json   — JSON Schema for v2.0 manifests
js/
  simulate-engine.js        — browser engine (existing, single-run)
  sweep-engine.js           — browser 1D sweep (Phase 2)
data/runs/
  manifest.json             — existing v1.2 single-run manifest
```
