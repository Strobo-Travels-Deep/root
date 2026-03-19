# Hasse et al. — Breakwater Dossier

**Dossier v0.7 · Breakwater Layer · Rocket Science Demonstrator**

Claim Analysis Ledger and interactive simulation platform for:

> F. Hasse, D. Palani, R. Thomm, U. Warring, T. Schaetz,
> *Phase-stable travelling waves stroboscopically matched for super-resolved
> observation of trapped-ion dynamics*,
> [Phys. Rev. A **109**, 053105 (2024)](https://doi.org/10.1103/PhysRevA.109.053105)
> · [arXiv: 2309.15580](https://arxiv.org/abs/2309.15580)

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
| `simulate.html` | **In-browser quantum simulation** with GPU, decoherence, shot noise |

## Simulate (v0.7)

Run the full stroboscopic detuning scan in the browser:

- **Parameters:** alpha, eta, omega_m, Omega, N_max, detuning range, pulse count
- **Decoherence:** Spin T1/T2, motional heating via quantum trajectories
- **Projection noise:** Configurable N_rep with binomial sampling and error bars
- **Fock convergence:** Checked post-run, colour-coded banner (green/amber/red)
- **GPU acceleration:** WebGPU compute shader for complex matrix multiply on
  supported browsers (Chrome 113+, Edge 113+). CPU fallback otherwise.
  Badge in subtitle shows current engine.
- **Downloads:** JSON, CSV, Python/QuTiP script, manifest — all with SHA-256 hash

## Data

All data is JSON (no HDF5 dependency):

- `data/runs/manifest.json` — run index
- `data/runs/alpha_*_default.json` — default runs at alpha = 0, 1, 3, 5

Default runs use scipy expm (exact Fock-basis) with the same physics as the
browser engine. alpha=5 at N_max=40 shows 1.1% Fock leakage — this is correct
and the convergence diagnostic flags it.

## Provenance

SHA-256 hash covers: code version, repository URL, all parameters (including
decoherence, shot noise, GPU flag), timestamp, output fingerprints, and Fock
convergence diagnostics.

## Architecture notes

- `simulate.html` is self-contained (inline CSS/JS) for portability
- WebGPU path uses Float32 precision (~7 digits); CPU path uses Float64.
  For eta ~ 0.4 physics the difference is negligible.
- `scripts/` contains Python utilities from the original dossier (export_hdf5.py,
  plot_detuning_harbour.py) — retained for reference but not required.

## Licence

MIT · [Open Science Harbour](https://github.com/threehouse-plus-ec/open-research-platform)
