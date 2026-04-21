# 2026-04-21 — Hasse-Fig.-6-style (φ, ϑ₀) slice

**Status:** executed.
**Upstream:** [2026-04-21-sweep-complete.md §7 next-step 2](2026-04-21-sweep-complete.md).
**Operator:** uwarring (with Claude).

-----

## 1. Purpose

Produce the direct visual analogue of Hasse 2024 Fig. 6(a,b) for
strobo 2.0's two short trains — i.e., at fixed δ₀ = 0 (carrier),
scan the AC-train analysis phase φ and the initial motional-state
phase ϑ₀, and map ⟨σ_z⟩ and δ⟨n⟩ = ⟨n⟩_fin − |α|². Qualitative
overlay with the Hasse paper + ϑ₀-π-periodicity claim recorded in
[sweep-complete §3.2](2026-04-21-sweep-complete.md) are both
verified quantitatively.

## 2. Protocol

| Axis            | Range                | Points |
|-----------------|----------------------|--------|
| analysis phase φ | [0, 2π), uniform    | 32     |
| motional phase ϑ₀| [0, 2π), uniform    | 64     |

Each grid cell is one engine call with `npts = 1` (single-point at
δ₀ = 0); 32 × 64 = 2048 cells per sheet. Four sheets total
(T1 × {α=3, α=4.5}, T2 × {α=3, α=4.5}). All other parameters fixed
at the strobo 2.0 canonical set:
ω_m/(2π) = 1.306 MHz, Ω/(2π) = 0.178 MHz, η = 0.395,
Δt = 0.77 µs, N_max = 60.

Wall time: **17.3 s** on laptop (~2 ms / cell).

## 3. Observed features

### 3.1 Peak values

| Tag           | max \|⟨σ_z⟩\| | max \|δ⟨n⟩\| | N·θ_pulse·e⁻η²⁄² (rad) |
|---------------|---------------:|-------------:|-----------------------:|
| T1, \|α\|=3   | 0.304          | 0.302        | 0.3103                 |
| T1, \|α\|=4.5 | 0.302          | 0.369        | 0.3103                 |
| T2, \|α\|=3   | 0.353          | 0.398        | 0.3620                 |
| T2, \|α\|=4.5 | 0.353          | 0.556        | 0.3620                 |

max|⟨σ_z⟩| is exactly sin(N·θ_pulse·e⁻η²⁄²) at α = 3 and decreases
by ≲ 1 % at α = 4.5 (from the η-nonlinearity's coherent-state
averaging). This is consistent with the |α|-independence of |C|_peak
reported in
[sweep-complete §2](2026-04-21-sweep-complete.md).

max|δ⟨n⟩| scales as **linear + mild nonlinear** in |α|:
 ratio α = 4.5 / α = 3 = **1.38** (T2) and **1.22** (T1), vs the
naive-linear ratio of 1.50. The shortfall is the η-induced
coherent-state averaging.

### 3.2 Symmetry checks

Pure-state unitary dynamics impose two exact symmetries that the
data reproduces to machine precision:

- **φ-antiperiodicity** δ⟨n⟩(φ + π, ϑ₀) = −δ⟨n⟩(φ, ϑ₀). Measured
  correlation coefficient = **−1.0000** across all four sheets.
- **ϑ₀-π-periodicity at the φ = 0 cut** δ⟨n⟩(0, ϑ₀ + π) =
  δ⟨n⟩(0, ϑ₀). Measured correlation coefficient = **+1.0000** across
  all four sheets. This is the rigorous form of the "π-periodic
  four-lobe pattern" qualitative claim made in
  [sweep-complete §3.2](2026-04-21-sweep-complete.md): it holds
  along the φ = 0 cut — which is the cut that corresponds to
  sheet `04_delta_n_phi0.png` of the main sweep — but not globally
  across the φ axis (where the φ-antiperiodicity above dominates
  the symmetry structure).
- **Four-lobe quadrant sign pattern.** Quadrant-mean of
  δ⟨n⟩(T2, |α|=3):
    Q1 (0 < φ < π, 0 < ϑ₀ < π):   **+0.062**
    Q2 (0 < φ < π, π < ϑ₀ < 2π):  **−0.053**
    Q3 (π < φ < 2π, 0 < ϑ₀ < π):  **−0.053**
    Q4 (π < φ < 2π, π < ϑ₀ < 2π): **+0.062**
  I.e., the (+, −, −, +) pattern of Hasse 2024 Fig. 6(b).

### 3.3 Qualitative ⟨σ_z⟩ pattern

Both T1 and T2 at |α| = 3 show the characteristic "diagonal-V"
structure of Hasse Fig. 6(a): ⟨σ_z⟩ alternates red/blue along
diagonals in the (ϑ₀, φ) plane. At |α| = 4.5, the V develops
secondary ripple structure near the extrema — the η³-nonlinearity
signature. T2 shows sharper V-edges than T1 because its longer
total train (4.97 vs 1.84 µs) averages more uniformly over the
motional trajectory.

## 4. Output files

- [numerics/hasse_fig6_slice.py](../numerics/hasse_fig6_slice.py) —
  runner (4 sheets × 2048 cells).
- [numerics/make_fig6_plots.py](../numerics/make_fig6_plots.py) —
  figure generator with marginal cuts at φ, ϑ₀ ∈ {π/4, π/2, π}
  (light gray / dark gray / black curves).
- [numerics/hasse_fig6_slice.npz](../numerics/hasse_fig6_slice.npz)
  (139 KB).
- [plots/06_hasse_fig6_alpha3.png](../plots/06_hasse_fig6_alpha3.png)
  — main deliverable, Hasse-Fig.-6 analogue.
- [plots/07_hasse_fig6_alpha4p5.png](../plots/07_hasse_fig6_alpha4p5.png)
  — same layout at |α| = 4.5; higher η·|α| nonlinearity visible.

## 5. Relation to Hasse 2024 Fig. 6

- **Geometry:** match. Our axes are identical to Hasse (analysis
  phase φ vs motional phase ϑ₀, full 2π × 2π sheet).
- **Sign pattern:** match. Red-blue diagonal-V in ⟨σ_z⟩ and
  four-lobe purple-green pattern in δ⟨n⟩.
- **Amplitude:** smaller than Hasse's |⟨σ_z⟩| ≤ 0.9 and
  |δ⟨n⟩| ≤ 0.9 because Hasse uses N = 30 × 100 ns to form a
  ~π/2 analysis pulse, whereas strobo 2.0's trains deliver
  N·θ_pulse ≈ 0.33–0.39 rad (~1/5 of π/2). The peak amplitudes
  scale as sin(N·θ·e⁻η²⁄²) for ⟨σ_z⟩ and roughly linearly in
  (N·θ·e⁻η²⁄²)·|α|·η for δ⟨n⟩, so rescaling to match Hasse would
  require ~5× stronger coupling (which is precisely the Rabi-rate
  question of
  [2026-04-21-rabi-reconciliation.md](2026-04-21-rabi-reconciliation.md)).
- **Cut-lines:** Hasse shows ϑ₀ = {π/4, π/2, π} and
  φ = {π/4, π/2, π} marginal cuts in light/dark/black gray. Our
  figures reproduce the same cuts.

## 6. Notes for follow-ups

- **Rabi dependence is trivial.** Because the forward map factorises
  into sin(Ω·N·δt·e⁻η²⁄²) × (η-nonlinearity) at leading order, raising
  Ω/(2π) from 0.178 → 0.300 → 0.446 MHz rescales the color amplitudes
  ~1.6× → ~2.3× without changing any pattern geometry. So the
  qualitative finding of this log (diagonal-V in σ_z, four-lobe in
  δ⟨n⟩, the symmetry checks of §3.2) is **robust** against the
  open Rabi-rate question.
- **30-pulse companion.** If a follow-up wants to directly reproduce
  Hasse's amplitudes rather than the pattern, the same runner can
  be called with N = 30, δt = 100 ns, matching Hasse App. D. Cost:
  one additional sheet ~5 s.
- **Δt = T_m exact.** A slip-free run (t_sep_factor = 1.0 exactly)
  would isolate how much of the V-tilt in σ_z at δ₀ = 0 comes from
  the +0.56 % stroboscopic slip. Not done here; remains on the
  [sweep-complete §7 next-step 1](2026-04-21-sweep-complete.md)
  list.

-----

*v0.1 2026-04-21 — initial entry.*
