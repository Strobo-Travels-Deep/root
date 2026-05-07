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
| `dossier.html` | Claim Analysis Ledger, Agreement / Mismatch Ledger, Risk Register |
| `tutorial.html` | Synthesis: Doppler mechanism, analytic estimates, Framework recap, Work Packages A–D |
| `reference.html` | Commented paper walk-through + annotated bibliography |
| `getting-started.html` | Student onboarding, task cards, deliverable formats |
| `wp-*/` | Per-work-package landing pages with three-lens (Experiment / Analytical / Numerical) jump-nav |
| `numerics.html` | Generic JSON-run viewer (de-emphasised; per-WP §Numerical tabs are now the primary path) |
| `framework.html`, `simulate.html`, `code.html` | Tombstone redirects → `tutorial.html` and `scripts/` (retired 2026-05-07) |

## Simulate

**Browser engine:** the interactive browser simulator is not included in this
snapshot pending restoration; see `REBUILD.md`. The `simulate.html` page is now
a tombstone redirect to the Tutorial.

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
detuning grids and yield `contrast_z ≈ 0.56` uniformly across α.

An earlier HDF5 pipeline (adaptive-learner sampling) produced different
contrast values; those `.h5` files are **not shipped** in this repository.
The legacy index `data/manifest.json` is retained only as a provenance
stub and is explicitly marked `ARCHIVAL — NON-SHIPPING`. See the Tutorial
provenance note for the historical comparison.

## Provenance

Each manifest carries a SHA-256 `provenance_hash` over `{code_version, mode,
payload}`. The payload includes the parameters, derived quantities, convergence
diagnostics, and output arrays for that mode, so the hash is sensitive to any
change in inputs or outputs. The hash deliberately does **not** cover
`repository`, `execution.timestamp`, or `execution.elapsed_s` — these fields
record context but vary between otherwise-identical runs and so are kept
outside the digest. To verify, recompute the hash over the same three keys
of a downloaded manifest.

Manifest schema v2.0 supports three modes: `single_run`, `sweep_1d`,
`state_comparison`. See `schemas/manifest_v2.schema.json`.

## Architecture notes

- The browser simulator was retired from primary navigation 2026-05-07; `simulate.html` is now a tombstone redirect (see REBUILD.md if you want to restore it).
- Python output is labelled `systematic` (Float64 throughout).
- `scripts/stroboscopic_sweep.py` is the systematic survey engine (Float64).
- `scripts/` also contains legacy Python utilities (export_hdf5.py,
  plot_detuning_harbour.py) — retained for reference.
- Per-WP `numerics/` outputs carry sidecar manifests validated by `schemas/wp_manifest_v1.schema.json` (currently shipped for `wp-strobo-2p0`; the other three WPs are pending — see `schemas/README.md`).

## Citation

A machine-readable citation is provided in `CITATION.cff`. Please cite both
this repository and the underlying experimental paper (Hasse et al., PRA 109,
053105 (2024)) when reusing data or code.

## Licence

MIT — see `LICENSE` for the full text.
