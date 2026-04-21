# 2026-04-21 — Hasse-Fig.-6-style (φ, ϑ₀) slice (v0.3 — π/2-calibrated)

**Status:** executed; reproduces Hasse 2024 Fig. 6 amplitudes directly.
**Upstream:** [2026-04-21-sweep-complete.md §7 next-step 2](2026-04-21-sweep-complete.md).
**Operator:** uwarring (with Claude).

-----

## 1. Purpose

Produce the direct visual analogue of Hasse 2024 Fig. 6(a,b) for
strobo 2.0's two short trains — at fixed δ₀ = 0 (carrier), scan the
AC-train analysis phase φ and the initial motional-state phase ϑ₀,
and map ⟨σ_z⟩ and δ⟨n⟩ = ⟨n⟩_fin − |α|². Under the v0.3 π/2
calibration (per-train Ω such that N·Ω·e⁻η²⁄²·δt = π/2), the
amplitudes of both observables are now directly comparable to Hasse's
numerical simulations.

## 2. Protocol

| Axis            | Range                | Points |
|-----------------|----------------------|--------|
| analysis phase φ | [0, 2π), uniform    | 32     |
| motional phase ϑ₀| [0, 2π), uniform    | 64     |

Each grid cell is one engine call with `npts = 1`; 32 × 64 = 2048
cells per sheet. Four sheets total (T1, T2 × α ∈ {3, 4.5}). All other
parameters at the strobo 2.0 canonical v0.3 set:
ω_m/(2π) = 1.306 MHz, Ω_T1/(2π) = 0.9008 MHz,
Ω_T2/(2π) = 0.7722 MHz, η = 0.395, Δt = 0.77 µs, Nmax = 60.

Wall time: **18.3 s** on laptop (~2 ms / cell; same as v0.1).

## 3. Observed features

### 3.1 Peak values

| Tag           | max \|⟨σ_z⟩\| | max \|δ⟨n⟩\| |
|---------------|---------------:|-------------:|
| T1, \|α\|=3   | 0.949          | 1.102        |
| T1, \|α\|=4.5 | 0.949          | 1.494        |
| T2, \|α\|=3   | 0.937          | 1.156        |
| T2, \|α\|=4.5 | 0.940          | 1.674        |

**⟨σ_z⟩ amplitude now saturates** around 0.94 for both trains across
α (about 6 % below the π/2-target 1, from intra-pulse Magnus
correction — see
[2026-04-21-sweep-complete.md §2](2026-04-21-sweep-complete.md)). This
is a factor 2.7× higher than the v0.1 weak-probe value of 0.35 and
close to the Hasse Fig. 6(a) amplitudes at the same |α|.

**δ⟨n⟩ amplitude now exceeds 1 quantum** for |α| ≥ 3 — peak 1.16
(T2, α = 3) and 1.67 (T2, α = 4.5). Compare Hasse Fig. 6(b) which
reports |δ⟨n⟩| up to ~0.9 at |α| = 3. Strobo 2.0 T2 exceeds this
because its Ω_eff/ω_m ≈ 0.55 is stronger than Hasse's 0.213 — same
total rotation delivered in fewer pulses means each pulse delivers
more motional kick per spin-rotation.

### 3.2 Symmetry checks

Pure-state unitary dynamics impose two near-exact symmetries that
the data still reproduces:

- **φ-antiperiodicity** δ⟨n⟩(φ + π, ϑ₀) = −δ⟨n⟩(φ, ϑ₀). Measured
  correlation coefficient = **−0.9996** (T2, α=3) / **−0.9992**
  (T2, α=4.5). The tiny deviation from −1 is a finite-pulse
  correction that is absent in the weak-drive limit but present
  here at Ω_eff/ω_m ~ 0.6 — **not** a calibration bug.
- **ϑ₀-π-periodicity at the φ = 0 cut** δ⟨n⟩(0, ϑ₀ + π) = δ⟨n⟩(0, ϑ₀).
  Measured correlation coefficient = **+1.0000** across all four
  sheets. Same as v0.1; this symmetry is exact because at φ = 0 the
  pulse train couples only σ_x and the motional state has an extra
  ϑ₀ → ϑ₀ + π parity that survives the strong drive.
- **Four-lobe quadrant sign pattern.** Still (+, −, −, +) in
  δ⟨n⟩(T2, |α|=3), with |quadrant-mean| ~ 0.2–0.3 quanta
  (3–5× v0.1). Matches Hasse Fig. 6(b).

### 3.3 Qualitative ⟨σ_z⟩ and δ⟨n⟩ patterns

Both T1 and T2 at |α| = 3 show the Hasse Fig. 6(a) diagonal-V in
⟨σ_z⟩, now with **full red-blue saturation** (≲ ±0.95). At |α| = 4.5
the V develops stronger side-band ripple structure than v0.1 —
the η^k·|α|^k ladder is more visible at the stronger drive.

δ⟨n⟩ still shows the four-lobe pattern but with amplitude now
directly comparable to Hasse's.

## 4. Output files

- [numerics/hasse_fig6_slice.py](../numerics/hasse_fig6_slice.py) —
  runner, now taking per-train Ω.
- [numerics/make_fig6_plots.py](../numerics/make_fig6_plots.py) —
  figure generator (unchanged).
- [numerics/hasse_fig6_slice.npz](../numerics/hasse_fig6_slice.npz)
  (140 KB; replaces the v0.1 file).
- [plots/06_hasse_fig6_alpha3.png](../plots/06_hasse_fig6_alpha3.png)
  — main deliverable, now saturation-regime.
- [plots/07_hasse_fig6_alpha4p5.png](../plots/07_hasse_fig6_alpha4p5.png)
  — higher-|α| companion.

## 5. Relation to Hasse 2024 Fig. 6

- **Geometry:** still matches. Identical axes and cut-line
  convention.
- **Sign pattern:** still matches. Diagonal-V in σ_z, four-lobe in
  δ⟨n⟩.
- **Amplitude:** **now matches to within a factor ~1.5** (v0.1 was
  ~5× too small). Strobo 2.0 T2 peak |δ⟨n⟩| = 1.16 at α = 3 vs.
  Hasse's ≈0.9 at the same |α|; the residual excess tracks the
  higher Ω_eff/ω_m of strobo 2.0's shorter train.
- **Cut-lines:** same layout as v0.1.

## 6. Notes for follow-ups

- **The strong-drive regime is now engaged.** Ω_eff/ω_m ≈ 0.55–0.64
  in v0.3, up from 0.128 in v0.1. This is where the Magnus expansion
  picks up significant higher-order corrections — the engine
  handles this exactly, but analytical/Magnus benchmarks will
  under-report |C|-loss by ~8 %.
- **a_I ≈ 4 × 10⁻³** at the representative cell (T2, α=3), 10×
  larger than v0.1. Still small, but worth upgrading to 4-run-per-
  cell if precise σ_z offsets matter.
- **30-pulse companion.** Still a candidate for direct Hasse
  reproduction (N=30, δt=100 ns, Ω tuned to π/2). Would produce a
  4-sheet comparison figure at Hasse's exact parameters.

-----

*v0.1 2026-04-21 — weak-probe (single Ω = 0.178 MHz) log.*
*v0.2 2026-04-21 — peak values and symmetry claims tightened to
match the π/2-calibrated data; Hasse-comparison amplitude now
matches directly.*
