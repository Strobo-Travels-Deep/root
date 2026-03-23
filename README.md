# Hasse et al. — Breakwater Dossier

**Dossier v0.8 · Breakwater Layer · Rocket Science Demonstrator**

Claim Analysis Ledger and interactive simulation platform for:

> F. Hasse, D. Palani, R. Thomm, U. Warring, T. Schaetz,
> *Phase-stable travelling waves stroboscopically matched for super-resolved
> observation of trapped-ion dynamics*,
> [Phys. Rev. A **109**, 053105 (2024)](https://doi.org/10.1103/PhysRevA.109.053105)
> · [arXiv: 2309.15580](https://arxiv.org/abs/2309.15580)

**Ion species:** ²⁵Mg⁺

**Endorsement Marker:** Local candidate framework (no parity implied with
externally validated laws).

## Pages

| Page | Description |
|------|-------------|
| `index.html` | Overview, navigation, quick summary |
| `dossier.html` | Claim Analysis Ledger (8 entries), Risk Register, Council Decisions |
| `framework.html` | Interaction Hamiltonian, measurement channels, Lock-Key assignments |
| `tutorial.html` | Doppler mechanism, analytic estimates, Work Packages A-D |
| `numerics.html` | Viewer for simulation JSON (default runs + user uploads) |
| `simulate.html` | Simulation page (browser engine not in this snapshot; see REBUILD.md) |
| `code.html` | Simulation engine documentation |
| `reference.html` | Commented paper walk-through + annotated bibliography |
| `getting-started.html` | Student onboarding, task cards, deliverable formats |

## Simulate

**Browser engine:** The full interactive browser simulator (`simulate.html` +
`js/simulate-engine.js`) is part of the dossier architecture but is **not
included in this packaged snapshot**. It will be restored from the source
repository in a future update. See `REBUILD.md` for patching instructions if
you have access to the original files.

**Python engine (included, primary tool):** `scripts/stroboscopic_sweep.py`
provides the same physics (exact Fock-basis matrix exponentiation, Float64)
in three modes: single run, 1D parameter sweep, and state comparison.

**Pre-computed data:** 9 default runs are included in `data/runs/` and viewable
on the Numerics page.

## Systematic Sweep Engine (v0.8)

Python/QuTiP engine for publication-grade parameter surveys:

```
python scripts/stroboscopic_sweep.py --mode single_run --alpha 3
python scripts/stroboscopic_sweep.py --mode sweep_1d --sweep-param n_pulses --sweep-values 5,10,22,50
python scripts/stroboscopic_sweep.py --mode state_comparison
```

See `ARCHITECTURE.md` for the three-mode design and manifest schema v2.0.

## Data

All data is JSON (no HDF5 dependency):

- `data/runs/run_index.json` — run index (9 default runs)
- `data/runs/alpha_*_default.json` — default runs at alpha = 0, 1, 3, 5
- `data/runs/*_alpha0.json` — sideband zoom and carrier zoom runs
- `data/runs/full_alpha1_fine.json` — fine-grid alpha=1 scan (301 pts)
- `data/runs/sideband_comb_alpha0.json` — sideband comb (401 pts)

Default runs use scipy expm (exact Fock-basis) with N_max=50.

### Cross-validation caveat

The default JSON runs use 22-pulse stroboscopic evolution with uniform
detuning grids. Earlier HDF5 data (referenced in `data/manifest.json`)
used an adaptive-learner method with different detuning-point sampling.
Contrast values may differ between methods:
- **JSON runs:** contrast_z ≈ 0.56 (uniform across α)
- **HDF5 adaptive-learner:** contrast_z = 0.61 → 0.71 → 0.84 → 0.75

Both are internally consistent. See the Tutorial provenance note for details.

## Provenance

SHA-256 hash covers: code version, repository URL, all parameters (including
decoherence, shot noise, GPU flag), timestamp, output fingerprints, and Fock
convergence diagnostics.

Manifest schema v2.0 supports three modes: `single_run`, `sweep_1d`,
`state_comparison`. See `schemas/manifest_v2.schema.json`.

## Architecture notes

- `simulate.html` browser engine is not included in this snapshot (see REBUILD.md)
- Python output is labelled `systematic` (Float64 throughout)
- `scripts/stroboscopic_sweep.py` is the systematic survey engine (Float64)
- `scripts/` also contains legacy Python utilities (export_hdf5.py,
  plot_detuning_harbour.py) — retained for reference

## Licence

MIT · [Open Science Harbour](https://github.com/threehouse-plus-ec/open-research-platform)
