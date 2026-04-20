# Logbook — 2026-04-14 — 2D scan at |α|=3 without synced-phase (engine native)

**Context.** User request: "do the same without synced-phase". Same
grid as [2026-04-14-2d-scan-alpha3.md](2026-04-14-2d-scan-alpha3.md)
(±15 MHz × [0, 2π), |α| = 3, 1001 × 64 pts) under the engine's native
v0.9.1 convention instead of synced-phase.

**Subtlety encountered.** A first cut of the driver naively dropped
ALL inter-pulse evolution (no motional, no spin U_gap). That gives
garbage — |C|(δ=0) = 0.04 — because the motional phase doesn't close
per cycle and coherence is destroyed. Checking the engine code
([stroboscopic_sweep.py:486-498](../../scripts/stroboscopic_sweep.py#L486))
confirmed the engine's native convention is actually **motional Ufree
applied, spin δ-phase Ufree NOT applied** — a "mixed-frame" convention
in which motion evolves in the lab frame but detuning is pulse-only.
Driver corrected to match.

**Verdict.** Engine-native and synced-phase produce **dramatically
different** 2D maps:

- **Engine-native:** single sharp carrier tooth at k = 0 with |C| ≈ 0.9;
  sidebands (k = ±1, …) at |C| ~ 0.02–0.05. Bright stripes at k = ±10
  where motional-phase closure hits a secondary resonance.
- **Synced-phase:** broad Bessel-like comb envelope centred on k = 0;
  all |k| ≤ 4 teeth at |C| ~ 0.5–0.9; clear φ_α-dependent sideband
  asymmetry (the velocity signature).

At the carrier (δ = 0, φ_α = 0), both agree: |C| = 0.924. Off-carrier
they diverge by an order of magnitude. The difference **is the
laser-frame detuning phase accumulated between pulses** — present in
synced-phase, absent in engine-native.

-----

## 1. Three conventions, now explicit

The v0.9.1 engine allows the user to dial between two kinds of
inter-pulse evolution:

| convention       | motion U_gap | spin-δ U_gap | physical interpretation                                   |
|------------------|:------------:|:------------:|-----------------------------------------------------------|
| "null" (broken)  | no           | no           | unphysical; motion doesn't close cycle → coherence lost   |
| engine-native    | **yes**      | no           | lab-frame motion, pulse-only detuning (engine default)    |
| synced-phase     | yes          | **yes**      | laser rotating frame maintained through train (Flag 1)    |

The "null" convention gave the 0.04 carrier number in my earlier cut
and was rejected. The interesting comparison is engine-native vs
synced-phase — two internally-consistent physical pictures that differ
in where the laser phase reference lives.

## 2. Numerical comparison at selected (k, φ_α)

| φ_α  | conv       | k=0   | k=+1  | k=+2  | k=+5  | k=−1  | k=−5  |
|:----:|------------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
|   0° | engine     | 0.924 | 0.048 | 0.032 | 0.025 | 0.048 | 0.025 |
|   0° | synced     | 0.924 | 0.932 | 0.919 | 0.580 | 0.914 | 0.563 |
|  90° | engine     | 0.894 | 0.048 | 0.036 | 0.048 | 0.036 | 0.003 |
|  90° | synced     | 0.894 | 0.907 | 0.924 | 0.891 | 0.805 | 0.064 |
| 180° | engine     | 0.924 | 0.048 | 0.032 | 0.025 | 0.048 | 0.025 |
| 180° | synced     | 0.924 | 0.933 | 0.919 | 0.580 | 0.914 | 0.564 |
| 270° | engine     | 0.943 | 0.036 | 0.020 | 0.003 | 0.048 | 0.048 |
| 270° | synced     | 0.943 | 0.840 | 0.701 | 0.064 | 0.931 | 0.856 |

At the carrier, the two conventions agree to within 0.001. At the
sidebands, the engine-native amplitudes are ~20× smaller than
synced-phase. Both show φ_α-dependent asymmetry between k = ±1 sidebands;
the synced version shows it strongly (30% amplitude swing) while the
engine version shows it weakly (10% amplitude swing on tiny baselines).

## 3. Where does the signal go?

Under synced-phase at |α| = 3:
- Sum of |C|² over k ∈ {−11, …, +11} at φ_α = 0: ≈ 8.5 (dominant contribution
  from k ∈ [−4, +4]). Coherence spreads across many sidebands.

Under engine-native:
- Sum of |C|² over k ∈ {−11, …, +11} at φ_α = 0: ≈ 0.87 (dominated by
  the single k = 0 spike with |C| = 0.924; all other sidebands summed
  contribute ~0.02). Coherence concentrated at carrier.

The engine-native case's "lost" signal (between teeth) presumably goes
into σ_z (|Bloch| unchanged) — under engine-native the detuning rotates
the spin only during pulses, producing a smooth Rabi-response centred
at δ = 0 with width ~Ω_eff that looks nothing like a comb when
oversampled at 30 kHz step (the "broad single peak" we recognised in
earlier scans). The comb's "teeth" at k·ω_m are still there but
narrow and weak.

## 4. Which convention is the lab seeing?

Under the user's statement "phase is kept synced for all pulses of a
train" (2026-04-14), the **synced-phase** picture is the physically
correct one. The engine-native convention is a modeling simplification
that would be accurate only if the laser phase reference were reset
per pulse.

If Hasse2024 reports a Rabi scan with a broad single peak at δ = 0 and
no visible comb, there are two reconciliations:

1. The scan range is narrow (|δ| < 100 kHz), in which case both
   conventions look similar — the central tooth dominates in both.
2. The lab has in practice a mixed convention: phase is synced over
   pulses (by design), but some mechanism (phase noise, pulse-envelope
   modulation, probe-linewidth averaging) suppresses the comb
   structure below detection. The engine-native treatment might
   incidentally match the *observed* lineshape while being
   microscopically wrong.

This is the experimental question for the Schätz/Hasse correspondence:
*at what detuning range are scans reported, and is the comb observed?*
Until settled, v0.4 should present both conventions with explicit
caveats.

## 5. Files

- [../numerics/run_2d_alpha3_unsynced.py](../numerics/run_2d_alpha3_unsynced.py) —
  corrected to match engine convention (motional U_gap only).
- [../numerics/scan_2d_alpha3_unsynced.h5](../numerics/scan_2d_alpha3_unsynced.h5) —
  engine-native 2D data, 1001 × 64.
- [../numerics/plot_2d_alpha3_compare.py](../numerics/plot_2d_alpha3_compare.py)
- [../plots/scan_2d_alpha3_compare_overview.png](../plots/scan_2d_alpha3_compare_overview.png) —
  three-row × two-column side-by-side (|C|, arg C, σ_z).
- [../plots/scan_2d_alpha3_compare_tooth_envelope.png](../plots/scan_2d_alpha3_compare_tooth_envelope.png) —
  per-tooth |C|(k, φ_α) heatmaps and traces.
- This entry.

## 6. Outstanding

- Which convention v0.4 presents as "canonical" depends on the
  experimental correspondence. Default stance: report synced-phase as
  the physics, document engine-native as the simulation simplification.
- Possibly add a `inter_pulse_spin_evolution` toggle to the engine
  (opt-in, backward-compatible) so the synced-phase path becomes a
  first-class engine option rather than a driver-level patch. Worth
  discussing before v0.4 drafting.

*Engine-native behaviour at α = 3 is fully characterised; the comb and
its asymmetry are now unambiguously products of inter-pulse spin-δ
phase accumulation.*
