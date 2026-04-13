# WP-V — Validation: Hasse 2024 Fig 6 & Fig 8 Reproduction

**Work Program · v0.1 · 2026-04-13**
**Status:** execution-ready. Self-contained consistency check.
**Source paper:** [refs/Hasse2024_PRA_109_053105.pdf](../refs/Hasse2024_PRA_109_053105.pdf)
([Phys. Rev. A 109, 053105 (2024)](https://doi.org/10.1103/PhysRevA.109.053105)).

-----

## 1. Purpose

The systematic engine [scripts/stroboscopic_sweep.py](../scripts/stroboscopic_sweep.py)
declares itself a reimplementation of the Hasse et al. simulation pipeline
(see its module docstring). This WP closes the loop: re-derive the two
purely numerical figures of that paper — **Fig 6** (encoding of position
and momentum into the spin observable) and **Fig 8** (numerical
calibration of position/momentum decoders) — from our engine, and confirm
that the published features are recovered.

This is **not** a pulse-detuning analysis (that is WP-E's job). It is a
single-pass code consistency check, kept short on purpose.

Rationale for choosing Fig 6 and Fig 8: both are entirely *numerical*
panels in the Hasse paper (no experimental data overlay), so any deviation
from the published image is unambiguously attributable to a difference in
our implementation, not to lab noise.

-----

## 2. Nominal parameters

Matched to Hasse Appendix D, ²⁵Mg⁺ axial (LF) mode:

| Symbol         | Value           | Meaning                                    |
|----------------|-----------------|--------------------------------------------|
| ω_m/(2π)       | 1.300 MHz       | LF axial mode                              |
| η_LF (0° tilt) | 0.397           | Effective Lamb–Dicke parameter (Hasse Tab II nominally 0.40) |
| Ω/(2π)         | 0.300 MHz       | Bare carrier Rabi frequency                |
| δt             | 100 ns          | Hasse stroboscopic flash duration (Fig 3a). Engine derives δt internally from N · θ_pulse = π/2 |
| N              | 30              | Hasse flash count (Appendix D)             |
| ⟨n⟩_thermal    | 0.15            | Hasse Fig 8 caption                        |
| LF tilt angles | {−5°, 0°, +5°}  | Hasse Fig 8 caption                        |

The engine uses the Debye–Waller-suppressed effective Rabi rate
Ω_eff = Ω · exp(−η²/2) and sets the per-pulse duration so that the train
totals a π/2 rotation on the carrier. WP-E (§2 Q8) treats the resulting
1.53 rad ≠ π/2 discrepancy explicitly; here we adopt the engine
convention as-is and report the actual accumulated rotation in the
results log, since this is a self-consistency check of *that* engine.

-----

## 3. Scope

### 3.1 In scope
- **Fig 6a** — ⟨σ_z⟩ over (ϕ, ϑ₀) at fixed |α| = 3, plus orthogonal cuts.
- **Fig 6b** — back-action δ⟨n⟩ = ⟨n⟩_fin − ⟨n⟩_ini over (ϕ, ϑ₀) at |α| = 3.
- **Fig 8a** — calibration |α| ↔ analysis-phase shift ϕ₀ at three η values.
- **Fig 8b** — calibration C ↔ |⟨P⟩| at the same three η values.

### 3.2 Out of scope
- Hasse **Fig 7** (experimental raw-data overlay) — not numerical-only.
- Hasse **Fig 9** (squeezed states) — engine supports squeezing but
  squeezed-state validation is reserved for a follow-up WP-C entry.
- Pulse-detuning maps over (δ₀, |α|, φ_α) — that is WP-E.

### 3.3 Convention-mapping note (read before interpreting plots)

Hasse's "analysis phase ϕ" is the phase of the AC π/2 analysis pulse
train relative to the MW π/2 synchronisation pulse. The engine has no
explicit analysis-phase argument; it returns the post-train coherence
C = ⟨σ_x⟩ + i ⟨σ_y⟩ in a fixed frame. We reconstruct the Hasse axis
by basis rotation:

```
σ_z(ϕ) = ⟨σ_x⟩ cos(ϕ) + ⟨σ_y⟩ sin(ϕ)        (analysis-phase Ramsey readout)
```

Equivalently ϕ₀ = arg C is the position-encoded phase shift, and
|C| / |C(α=0)| is the Hasse contrast. Both quantities are derived
purely from the engine's already-exposed (σ_x, σ_y) outputs — no
engine modification needed.

-----

## 4. Deliverables

1. **Code** — two scripts in [numerics/](numerics/):
   - `run_fig6.py` — Fig 6a/b at |α| = 3, η = 0.397, pure state.
   - `run_fig8.py` — Fig 8a/b sweep over |α| ∈ [0, 8] at three η values
     with n_thermal = 0.15.
2. **Datasets** — two HDF5 files in [numerics/](numerics/):
   - `fig6_alpha3.h5`
   - `fig8_calibrations.h5`
3. **Plots** — four PNGs in [plots/](plots/):
   - `fig6a_sigma_z.png` — Hasse Fig 6a layout (heatmap + 3 cuts).
   - `fig6b_back_action.png` — Hasse Fig 6b layout.
   - `fig8a_position.png` — |α| vs ϕ₀ at three tilt angles.
   - `fig8b_momentum.png` — contrast vs amplitude at three tilt angles.
4. **Logbook** — kickoff entry plus one results entry naming the largest
   per-figure deviation from the published panel and any open questions.

### Pass criterion
Each panel reproduces the published qualitative features:
- Fig 6a: V-shaped fringe structure, sign of ⟨σ_z⟩ at (ϕ = π/4, ϑ₀ = π).
- Fig 6b: Sign-alternating four-quadrant structure of δ⟨n⟩.
- Fig 8a: Near-linear |α| ↔ ϕ₀ relation through origin, weak tilt dependence.
- Fig 8b: Monotonically decreasing contrast vs |α|, three angle curves
  ordered as in Hasse Fig 8b.

Quantitative target: ≤ 5% deviation on the anchor numbers
(C(α = 0) and ϕ₀(α = 3)). Any larger deviation triggers a documented
follow-up question rather than a re-run.

-----

## 5. Folder layout

```
wp-hasse-reproduction/
├── README.md                  (this document)
├── numerics/
│   ├── run_fig6.py
│   ├── run_fig8.py
│   ├── fig6_alpha3.h5
│   └── fig8_calibrations.h5
├── plots/
│   ├── fig6a_sigma_z.png
│   ├── fig6b_back_action.png
│   ├── fig8a_position.png
│   └── fig8b_momentum.png
└── logbook/
    ├── 2026-04-13-kickoff.md
    └── 2026-04-13-results.md
```

-----

## 6. Relation to other WPs

- **WP-E** (Forward Map and Observability) studies the (δ₀, |α|, φ_α)
  *map*. WP-V studies the *fixed-grid panels* of the source paper — a
  much smaller computational job whose only purpose is to certify the
  engine before WP-E's larger sweeps are trusted.
- **WP-A.3** (η-sweep) and **WP-B** (N_p sweep) are orthogonal — they
  vary device parameters this WP holds fixed.

Result use: if WP-V passes, WP-E's preflight engine determination
(`stroboscopic_sweep.py` as candidate) gains an external anchor. If
WP-V fails, the failure mode (e.g. missing Debye–Waller factor, wrong
δt convention, pulse-train accumulation off by integer factor) localises
the engine bug *before* WP-E's larger sweeps can entrench it.

-----

## 7. References

- **[Hasse2024]** F. Hasse, D. Palani, R. Thomm, U. Warring, T. Schaetz,
  *Phase-stable travelling waves stroboscopically matched for
  super-resolved observation of trapped-ion dynamics*,
  Phys. Rev. A **109**, 053105 (2024). PDF stored at
  [refs/Hasse2024_PRA_109_053105.pdf](../refs/Hasse2024_PRA_109_053105.pdf).
- Engine: [scripts/stroboscopic_sweep.py](../scripts/stroboscopic_sweep.py)
  (CODE_VERSION declared in the module).

-----

*v0.1: initial scaffold. WP intentionally kept short; one execution pass,
two logbook entries.*
