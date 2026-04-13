# Logbook — 2026-04-13 — Lock-tolerance wedge (t_sep, |α|)

**Context.** Follow-up suggested in
[2026-04-13-sigmaz-native-scan.md §4](2026-04-13-sigmaz-native-scan.md):
map the σ_z fringe amplitude on the full `(t_sep_factor, |α|)` plane and
compare against Hasse's experimentally measured Δω_m/ω_m ≲ 0.7 % bound.

Driver: [run_lock_tolerance_wedge.py](../numerics/run_lock_tolerance_wedge.py).
Output: [lock_tolerance_wedge.h5](../numerics/lock_tolerance_wedge.h5),
[lock_tolerance_wedge.png](../plots/lock_tolerance_wedge.png),
[lock_tolerance_curves.png](../plots/lock_tolerance_curves.png).

Grid: `t_sep ∈ [0.98, 1.02]` (21 pts, 0.2 % step), `|α| ∈ [0, 8]` (17 pts),
`ϑ₀ ∈ [0, 2π)` (24 pts) → 8568 runs, 166.5 s wall.

-----

## 1. Headline structure

| ε = (t_sep − 1) × 100 % | argmax α of sz_amp | max sz_amp |
|--------------------------|--------------------|-----------|
| −2.00 %                  | 2.5                | 0.389     |
| −1.00 %                  | 5.0                | 0.497     |
| −0.60 %                  | 8.0                | 0.520     |
| −0.20 %                  | 8.0                | 0.138     |
| **0.00 %**               | —                  | **1.7 × 10⁻¹⁵** |
| +0.20 %                  | 8.0                | 0.138     |
| +0.60 %                  | 8.0                | 0.520     |
| +1.00 %                  | 5.0                | 0.497     |
| +2.00 %                  | 2.5                | 0.389     |

Three observations:

1. **Perfect symmetry in ε.** Sign of mismatch doesn't matter; the
   physics depends only on |ε|. Numbers at ε = −x match ε = +x to four
   decimals.
2. **Identically zero at ε = 0.** Floor 1.7 × 10⁻¹⁵ is round-off, not
   physics. Previous scan finding confirmed at higher resolution.
3. **The argmax-α moves inward as |ε| grows.** At small |ε| (≲ 0.6 %)
   the fringe is largest at the highest |α| sampled; at larger |ε| the
   peak retreats toward smaller |α|. Signature of a characteristic
   amplitude ⟨α_c⟩(ε): below ⟨α_c⟩ the fringe grows with α, above it
   over-smearing collapses the fringe back down.

-----

## 2. At Hasse's experimentally quoted bound ε = ±0.7 %

Sampled at the nearest grid point ε = ±0.6 %:

| `|α|` | sz_amplitude |
|------|--------------|
| 3    | 0.174        |
| 5    | 0.361        |
| 8    | 0.520        |

A 0.7 %-class mismatch produces sz_amp ~ 0.17 at α = 3 — comparable in
size to the engine's mean σ_z (≈ 0.128 at perfect lock). In other
words: **at the published lock tolerance, the σ_z fringe amplitude is
already comparable to the carrier signal**. Hasse's experimental bound
is therefore not a comfortable margin in this engine; it is essentially
the largest mismatch at which σ_z can still be read cleanly without
ϑ₀-dependent fringe contamination.

This is consistent with Hasse's stated motivation for active phase
stabilisation (Appendix B): without it, the wedge structure mapped here
would dominate the readout for any α ≳ 3.

-----

## 3. Power-law / scaling check

The log–log panel (right) of
[lock_tolerance_curves.png](../plots/lock_tolerance_curves.png) shows
sz_amp vs |ε| at fixed |α|. For small |ε| the curves are roughly
linear-in-ε; for large |ε| they roll over and decay. This is a
ε·|α|·(stuff) → saturation crossover, not a pure power law over the
sampled range. A clean fit would need finer ε sampling near zero
(e.g. logarithmically spaced ε ∈ [10⁻⁴, 10⁻²]).

Quick numbers from the table: at α = 5, sz_amp grows from 0.000 to
0.497 over ε ∈ [0, 1 %], which is roughly linear. At α = 8 the curve
has clearly rolled over by ε = 1.5 %.

-----

## 4. What the wedge confirms about the engine

- The engine **does** carry stroboscopic-lock-tolerance information in
  σ_z directly — but only through the t_sep_factor knob, exactly as
  diagnosed in [2026-04-13-sigmaz-native-scan.md](2026-04-13-sigmaz-native-scan.md).
- The lock-tolerance wedge is a clean, fast, ϑ₀-resolved diagnostic
  (167 s for an 8.5 k-run sweep). It is a usable engine consistency
  check independent of the |C|-style contrast definition.
- The wedge is **structural**: the position of the fringe peak in |α|
  is set by ε. This is the engine's analog of the lab "phase walks
  through nodes" effect.

-----

## 5. Suggested next probes (not gating, not run)

1. **Logarithmic ε sweep** over ε ∈ [10⁻⁴, 10⁻²] at fixed α = 3 to
   extract the small-ε scaling exponent cleanly.
2. **η-dependence of the wedge.** Repeat at η ∈ {0.1, 0.4, 0.6} to
   check whether the characteristic ε·|α| crossover scales as expected.
3. **Comparison with Hasse Fig 2(c) raster.** Hasse Fig 2(c) is a
   spatial scan of the AC pattern in (Δx, Δz); under the convention
   mapping it should be related to the wedge by a coordinate change.
   Worth a side-by-side if the convention is firmed up.

-----

## 6. Status

Appendix entry, complementing the t_sep discriminator and the σ_z native
scan. WP-V remains closed at v0.1. The wedge plot is the cleanest
single-figure summary of the engine's stroboscopic behaviour produced
under WP-V.
