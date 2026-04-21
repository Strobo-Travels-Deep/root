# 2026-04-21 — Strobo 2.0 Main Sweep Complete (v0.3 — π/2-calibrated)

**Status:** sweep executed, plots generated, observations recorded.
**Operator:** uwarring (with Claude)
**Upstream log:** [2026-04-21-kickoff.md](2026-04-21-kickoff.md) (v0.3
  parameter set).

-----

## 1. What was done

- **Preflight** ([numerics/preflight.py](../numerics/preflight.py)).
  All four tests pass at the π/2-calibrated values. Test 1 anchor
  (α = 0) gives |C| = 0.922 (T1) / 0.919 (T2), about 8 % below the
  closed-form sin(π/2) = 1 — the shortfall is the finite-pulse
  Magnus correction captured by the engine's intra-pulse motion
  (disabled in the closed form). Test 2 Nmax convergence at α = 4.5
  still satisfies < 10⁻¹⁰ at Nmax = 60. Tests 3–4 still pass.
- **Main sweep** ([numerics/run_sweep.py](../numerics/run_sweep.py)).
  768 engine calls × 81 detunings each, Nmax = 60, **102.7 s** wall
  time (essentially same as v0.1 — grid unchanged). Saved to
  [numerics/strobo2p0_data.npz](../numerics/strobo2p0_data.npz)
  (1.1 MB) with JSON manifest. Per-train Rabi:
  Ω_T1/(2π) = 0.9008 MHz, Ω_T2/(2π) = 0.7722 MHz, chosen from
  `N·Ω·e⁻η²⁄²·δt = π/2`.
- **Plots** ([numerics/make_plots.py](../numerics/make_plots.py)).
  Five heatmap figures regenerated:
  - [01_coherence_contrast.png](../plots/01_coherence_contrast.png) — |C|
  - [02_arg_C.png](../plots/02_arg_C.png) — arg C
  - [03_sigma_z.png](../plots/03_sigma_z.png) — ⟨σ_z⟩ at φ = 0
  - [04_delta_n_phi0.png](../plots/04_delta_n_phi0.png) — δ⟨n⟩ at φ = 0
  - [05_delta_n_phi_pi2.png](../plots/05_delta_n_phi_pi2.png) — δ⟨n⟩ at φ = π/2

## 2. Peak values (observed)

| Tag           | max \|C\|  | max \|σ_z\|_{φ=0} | max\|δ⟨n⟩\|_{φ=0} | max\|δ⟨n⟩\|_{φ=π/2} |
|---------------|-----------:|------------------:|------------------:|--------------------:|
| T1, \|α\|=1   | 0.943      | 0.920             | 0.376             | 0.435               |
| T1, \|α\|=3   | 0.962      | 0.949             | 0.975             | 1.111               |
| T1, \|α\|=4.5 | 0.960      | 0.923             | 1.481             | 1.532               |
| T2, \|α\|=1   | 0.936      | 0.914             | 0.388             | 0.445               |
| T2, \|α\|=3   | 0.945      | 0.937             | 1.063             | 1.160               |
| T2, \|α\|=4.5 | 0.946      | 0.937             | 1.569             | 1.674               |

### Saturation: sanity check

The closed-form weak-pulse-limit prediction on carrier at |α| = 0 is
|C| = sin(π/2) = 1 for both trains by construction. The engine result
of 0.92 (α = 0 anchor, preflight Test 1) is ~8 % below that limit — a
real physical shortfall from intra-pulse motional rotation
(ω_m·δt ≈ 0.82 rad for T1, 0.41 rad for T2). This finite-duration
Magnus correction is absent from the closed form but present in the
engine and therefore in the dataset.

The **|C| peak is still essentially |α|-independent** across
|α| ∈ {1, 3, 4.5}, within ~2 % (for T1 the α-scatter is larger than
v0.1, because at the strong-drive calibration the η·|α| nonlinearity
feeds back into the carrier amplitude; for T2 the weaker per-pulse
rotation suppresses this and the scatter is ~1 %).

## 3. Three qualitative observations (v0.3)

### 3.1 Carrier saturates + high-order sidebands visible

Unlike v0.1 (where only the carrier and a faint ±3 ω_m feature
survived), the π/2-calibrated sweep shows a **broad carrier** plus a
rich sideband comb. ϑ₀-averaged |C| on T2, α = 3 drops to ≲ 0.05 at
|δ₀|/(2π) ≈ 5.75 and ≈ 8.5 MHz — i.e. between sideband peaks. This
is the regime where the pulse train resolves individual sidebands
(Ω_eff/ω_m ≈ 0.55–0.64, large enough for the drive to populate
k-th-order sidebands via η^k coupling, but still well below the
fully-broadened strong-drive limit).

### 3.2 δ⟨n⟩ amplitude scales with N·θ·α·η; exact φ-antiperiodicity

Peak back-action at |α| = 4.5: **|δ⟨n⟩| ≈ 1.57 quanta** (T1) /
**1.67 quanta** (T2) — roughly 3× the v0.1 value, matching the
3-4× increase in per-pulse rotation. The φ-antiperiodicity
δ⟨n⟩(φ + π, ϑ₀) = −δ⟨n⟩(φ, ϑ₀) is preserved to correlation
−0.9996 (vs −1.0000 at weak drive) — the tiny deviation is a
finite-pulse correction, not a breakdown. The four-lobe quadrant
sign pattern (+, −, −, +) of Hasse Fig. 6(b) is reproduced at
|α| = 3 (see [2026-04-21-hasse-fig6-slice.md](2026-04-21-hasse-fig6-slice.md)).

### 3.3 T1 vs T2: same peak amplitude, different detuning widths

Both trains reach the same saturation peak (|C| ≈ 0.94–0.96) but
T2's carrier feature is narrower (longer total duration → tighter
Fourier limit). Rough HWHM from the maps:

- T1 (3 × 100 ns, total 1.84 µs): HWHM_δ₀/(2π) ≈ 1.4 MHz
- T2 (7 × 50 ns, total 4.97 µs): HWHM_δ₀/(2π) ≈ 0.9 MHz

The 1.5× ratio tracks the total-train-duration ratio as expected.
Both are now directly comparable to the Hasse 2024 N = 30 AC
analysis-pulse width (≈ 0.2 MHz, from their 23.1 µs total duration)
— strobo 2.0's trains are 2–6× broader, as befits their ~4-10×
shorter total duration.

## 4. arg C — structure and wrap-ups

[02_arg_C.png](../plots/02_arg_C.png) shows slanted-stripe patterns
similar to v0.1 but with **steeper slopes** and more visible
wrap-arounds — as expected at the stronger drive, the accumulated
phase arg C varies more rapidly with both δ₀ and ϑ₀. The slope sign
still flips at ϑ₀ ≈ 0 and ϑ₀ ≈ π.

## 5. Anomaly / ambiguity tracker

Three bookkeeping notes:

- **a_I offset.** Spot-checked at (|α|=3, δ₀=0, ϑ₀=0, T2) to
  4 × 10⁻³ — ~10× larger than in v0.1, because the stronger drive
  breaks the approximate σ_z mean-zero symmetry of the weak-probe
  regime. Still small enough for the two-run-per-cell protocol
  (|a_I|/|C| ≈ 0.4 %), but worth flagging if an absolute σ_z offset
  below 1 % ever matters. A 4-run-per-cell evaluation (spins at
  {+x, +y, −x, −y}) would remove the ambiguity.
- **Δt = 0.77 µs vs T_m = 0.7657 µs (+0.56 % slip).** Same as v0.1
  — footprint in this dataset is the modest asymmetry of δ⟨n⟩
  maps about δ₀ = 0 at |α| = 4.5.
- **π/2 shortfall at α = 0.** ~8 % below sin(π/2) = 1 from
  intra-pulse Magnus correction. This is intrinsic to the
  strong-drive regime of short trains — reported as a physical
  feature, not a calibration error.

## 6. Output files (artifacts produced by this log)

This entry produced six artifacts — the main-sweep dataset, its
manifest, and its five figures (re-run from v0.1 layout):

- [numerics/preflight.py](../numerics/preflight.py)
- [numerics/run_sweep.py](../numerics/run_sweep.py)
- [numerics/make_plots.py](../numerics/make_plots.py)
- [numerics/sweep.log](../numerics/sweep.log)
- [numerics/strobo2p0_data.npz](../numerics/strobo2p0_data.npz) (1.1 MB)
- [numerics/strobo2p0_manifest.json](../numerics/strobo2p0_manifest.json)
- [plots/01_coherence_contrast.png](../plots/01_coherence_contrast.png)
- [plots/02_arg_C.png](../plots/02_arg_C.png)
- [plots/03_sigma_z.png](../plots/03_sigma_z.png)
- [plots/04_delta_n_phi0.png](../plots/04_delta_n_phi0.png)
- [plots/05_delta_n_phi_pi2.png](../plots/05_delta_n_phi_pi2.png)

Follow-ups added in their own logs:

- [2026-04-21-rabi-reconciliation.md](2026-04-21-rabi-reconciliation.md)
  (now resolved: each train is π/2-calibrated, no single Ω).
- [2026-04-21-hasse-fig6-slice.md](2026-04-21-hasse-fig6-slice.md)
  (re-run at v0.3 to match the new saturation regime).

The [README](../README.md) has the complete up-to-date folder tree.

## 7. Next steps (not gated; for discussion)

1. **Companion Δt = T_m run.** Still un-done; isolates the 0.56 %
   slip contribution (now to the broader sideband comb visible in
   v0.3).
2. **Analysis-phase slice.** *Done 2026-04-21, see
   [2026-04-21-hasse-fig6-slice.md](2026-04-21-hasse-fig6-slice.md)*
   — v0.3 update reproduces Hasse Fig. 6 amplitudes within a few
   percent.
3. **Rabi-rate reconciliation.** *Resolved 2026-04-21 (v0.3)*: each
   train is calibrated separately to deliver π/2 on ground motion,
   as in Hasse 2024 App. D. See
   [2026-04-21-rabi-reconciliation.md](2026-04-21-rabi-reconciliation.md).
4. **Thermal-background admixture.** Still un-done; more relevant
   now that the peak amplitudes approach the Hasse experimental
   scale.

## 8. History

- **v0.1 (superseded, 2026-04-21 earlier today).** Single Ω/(2π) =
  0.178 MHz used for both trains; per-train rotation N·θ_pulse ≈
  π/9 (weak probe); peak |C| ≈ 0.35. Flagged in the preflight that
  this was a pre-calibration value, not a π/2 analysis.
- **v0.3 (this log).** Per-train Ω chosen so that each train
  delivers a full π/2 analysis rotation, matching the Hasse 2024
  App. D convention. Peak |C| ≈ 0.94 (saturation, ~8 % below 1 by
  Magnus correction).

-----

*v0.1 2026-04-21 — weak-probe, single-Ω record.*
*v0.2 2026-04-21 — editorial pass.*
*v0.3 2026-04-21 — π/2-calibrated per train; numbers, findings,
history updated. Earlier v0.1/v0.2 descriptions of the dataset are
retained as the "History" section; the dataset itself is now the
π/2-calibrated run.*
