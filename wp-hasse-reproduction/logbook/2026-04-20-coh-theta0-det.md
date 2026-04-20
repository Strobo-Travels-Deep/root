# Logbook — 2026-04-20 — Spin coherence over (ϑ₀, δ)

**Context.** First real physics run on top of the restructured
[`scripts/stroboscopic/`](../../scripts/stroboscopic/) package
(v1.0.0-restructure, committed at `1c09918`). After reproducing Hasse
Fig 6a/6b from the new API and validating bit-identical output against
[fig6_alpha3_v4.h5](../numerics/fig6_alpha3_v4.h5) (Δ ≤ 3.4e-14,
pure FP reassociation noise), we took the same Hasse-matched parameters
and scanned the **train detuning δ** instead of the AC analysis phase
φ_AC, holding φ_AC = 0.

Driver: [run_coh_theta0_det_v5.py](../numerics/run_coh_theta0_det_v5.py).
Output: [coh_theta0_det_v5.h5](../numerics/coh_theta0_det_v5.h5).
Compute: 20.0 s wall for 64 × 201 = 12 864 evolutions.

Parameters (unchanged from Fig 6):

| | |
|---|---|
| `|α|` | 3.0 |
| η | 0.397 |
| ω_m | 1.3 |
| N pulses | 30 |
| δt / T_m | 0.13 |
| Ω (π/2 budget) | 0.0902 |
| MW π/2 phase | 0° (pre-train) |
| AC analysis phase | 0° |
| intra_pulse_motion | on |
| center_pulses_at_phase | on |
| n_max | 60 |

Grid:

- ϑ₀ ∈ [0, 2π), 64 points
- δ/ω_m ∈ [−3, +3], 201 points (step 3·10⁻² ≈ 40 kHz, so each
  comb tooth is sampled at ~6 points across its HWHM).

-----

## 1. Headline result — the Fig 6 diamond lives only at comb teeth

The `|C|` heatmap
([coh_theta0_det_coh_abs_v5.png](../plots/coh_theta0_det_coh_abs_v5.png))
shows **five bright horizontal bands of `|C| ≈ 1` separated by narrow
dark stripes at integer δ/ω_m** (comb teeth at δ = 0, ±ω_m, ±2ω_m). The
MW π/2 at phase 0° plants the Bloch vector at +ŷ before the AC train;
off-resonance the train does almost nothing to that coherence, so `|C|`
stays ~1. On-resonance (at each tooth) the coherence drops to ~0.08 and
the full Fig 6a ϑ₀-structure reappears — i.e., the diamond pattern of
Fig 6a is the edge-on ϑ₀-cross-section of a single comb tooth.

| field | range |
|---|---|
| `⟨σ_x⟩` | [−1.000, +1.000] |
| `⟨σ_y⟩` | [−0.999, +1.000] |
| `⟨σ_z⟩` | [−0.949, +0.948] |
| `|C|` | [0.075, 1.000] |

-----

## 2. What the four panels show

### 2.1 `|C|(ϑ₀, δ)`  — canonical comb picture
[coh_theta0_det_coh_abs_v5.png](../plots/coh_theta0_det_coh_abs_v5.png).
Tooth positions δ/ω_m ∈ {0, ±1, ±2} are consistent with a stroboscopic
train of period T_m. Tooth HWHM in δ/ω_m is ≈ 1/N = 1/30 ≈ 0.033, the
expected sinc-like response of a finite N-pulse train. Each tooth
encodes the Fig 6a diamond in ϑ₀ — both the sign and depth of the
`|C|` drop track the ϑ₀-modulated spin–motion coupling.

### 2.2 `⟨σ_z⟩(ϑ₀, δ)`  — detuning-resolved Fig 6a
[coh_theta0_det_sigma_z_v5.png](../plots/coh_theta0_det_sigma_z_v5.png).
σ_z is ≈ 0 in the off-tooth regions (the MW π/2 kept the Bloch vector
in the equatorial plane and the train never reaches it) and shows the
antisymmetric ±0.95 diamond *within each tooth*. This is the clearest
view of where Fig 6a's structure lives in δ-space.

### 2.3 `⟨σ_x⟩(ϑ₀, δ)` and `⟨σ_y⟩(ϑ₀, δ)` — rapid Larmor stripes
[coh_theta0_det_sigma_x_v5.png](../plots/coh_theta0_det_sigma_x_v5.png),
[coh_theta0_det_sigma_y_v5.png](../plots/coh_theta0_det_sigma_y_v5.png).
Both are dominated by global spin precession: δ shifts the rotating-frame
phase by δ · T_total with T_total = N · T_m, giving ~30 full wraps
across the δ/ω_m ∈ [−3, +3] window. The comb-tooth envelope is visible
as a modulation of the stripe brightness.

### 2.4 `arg C(ϑ₀, δ)`
[coh_theta0_det_coh_arg_v5.png](../plots/coh_theta0_det_coh_arg_v5.png).
Same rapid winding as the individual components, dominated by the global
phase. The alpha-by-|C| mask was intended to suppress off-tooth noise,
but here **the signal is reversed**: `|C| ≈ 1` off-tooth (clean winding)
and `|C| → 0` at the teeth (phase undefined). An alpha mask by
`(1 − |C|)` or by a notch around the teeth would be the cleaner version.
Left uncorrected in this first pass so the raw behaviour is on record.

-----

## 3. Tie-back to Fig 6

The 2026-04-13 Fig 6 v4 run ([fig6_alpha3_v4.h5](../numerics/fig6_alpha3_v4.h5),
logbook entry [2026-04-13-engine-v0.9.1-centered.md](2026-04-13-engine-v0.9.1-centered.md))
fixed δ = 0 and scanned (ϑ₀, φ_AC). The present run fixes φ_AC = 0
and scans (ϑ₀, δ). The two scans complete each other: Fig 6 is a slice
across the δ = 0 tooth; each horizontal band in the present `|C|` map
is the image of the same Hasse rotation-amplitude landscape, repeated
at every stroboscopic resonance k·ω_m.

**Bit-for-bit validation of the new-API Fig 6 reproduction.**
[fig6_alpha3_v5.h5](../numerics/fig6_alpha3_v5.h5) vs v4:

| field | max \|Δ\| |
|---|---|
| σ_z map | 2.37e-14 |
| σ_x map | 1.74e-14 |
| σ_y map | 1.54e-14 |
| ⟨n⟩ map | 3.38e-14 |
| δ⟨n⟩ map | 3.38e-14 |
| ϑ₀, φ grids | 0.000 (exact) |

All maps match to ~10× machine epsilon — the restructured package
reproduces the v0.9.1 engine physics on the standard target.

-----

## 4. What enabled the 20 s wall

Precomputation, made accessible by the new API. `StroboTrain` is a
plain dataclass of (`U_pulse`, `U_gap_diag`, `n_pulses`), so the outer
loop can build these once per δ and apply them across all 64 ϑ₀-states
without rebuilding propagators or going through legacy-style
`ss.run_single` per point. Per-point cost:

- 201 × `expm(−iH_pulse·δt)` (Hamiltonian depends on δ, φ_AC) = ~6 s
- 201 × diagonal `U_gap_diag` construction (near-free)
- 12 864 × 30 matmuls of 120-dim = ~14 s

Equivalent legacy-engine layout would rebuild H_pulse, U_pulse, U_gap
inside `run_single`'s δ-loop 12 864 times — an estimated 30× slower
(~10 min).

-----

## 5. Loose ends

1. **arg C alpha-mask inversion**: off-tooth regions should be
   suppressed, not bright. Apply `alpha = (1 − |C|)` or notch at comb
   teeth in a v2 plot.
2. **Zoomed single-tooth view**. δ/ω_m ∈ [−0.05, +0.05] with N_det = 201
   would give ~70 samples per HWHM and resolve the ϑ₀-structure inside
   one tooth. Trivial re-run; ~4 s wall.
3. **3D (ϑ₀, δ, φ_AC)** or a compact `(φ_AC, δ)` scan at fixed ϑ₀ would
   give the full comb lineshape vs analysis phase. Probably the next
   useful map.
4. The `⟨σ_x⟩`, `⟨σ_y⟩` rapid winding is not physics-bearing at the
   current δ range — worth cropping to a single tooth before showing
   them in any public figure.

-----

## 6. Status

WP-V and WP-E remain closed at their respective versions. This is the
first "take it for a spin" run on the restructured package — the scaling
pattern (U-pulse precompute + lightweight `StroboTrain` composition) is
worth locking in as the template for future comb-resolved scans.

Code path: `HilbertSpace` + `build_pulse_hamiltonian` + `build_U_pulse` +
`build_U_gap` + `StroboTrain`, all under
[scripts/stroboscopic/](../../scripts/stroboscopic/). MW π/2 helper
added to the package as `HilbertSpace.apply_mw_pi2` / `states.apply_mw_pi2`
to support the Hasse pre-train convention.
