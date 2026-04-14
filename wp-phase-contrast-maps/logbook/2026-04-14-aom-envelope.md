# Logbook — 2026-04-14 — AOM erf-envelope softens v0.9.1 corrections

**Context.** Sequel to [2026-04-14-flag1-synced-phase.md](2026-04-14-flag1-synced-phase.md).
User authorised: τ_rise ≈ 50 ns typical, erf/Gaussian edge,
driver-level wrapper. This entry swaps the rectangular pulse for an
erf-shaped envelope and measures the effect on lineshape, |C|(φ_α)
spread, and the γ-corrections.

**Verdict.** Finite AOM edges **reduce** the v0.9.1 first-order
corrections — they do not introduce new distortions, they push the
protocol back toward the v0.8 frozen-motion ideal. Monotonic with
edge softness, smooth. Lineshape (comb at δ = k·ω_m) is essentially
unchanged to < 0.5% across the ±500 kHz grid.

-----

## 1. Envelope and implementation

Erf-shaped Gaussian-edge envelope:

```
f(t) = 0.25 · [1 + erf((t − t_L) / (σ√2))] · [1 + erf((t_R − t) / (σ√2))]
t_L = 3σ,   t_R = δt_total − 3σ
```

Sub-slice discretisation M = 20 per pulse. Each sub-propagator:

```
U_sub(k) = exp(−i · [ω_m·a†a + (δ/2)σ_z + f(t_k)·(Ω/2)(Cσ₋ + h.c.)] · Δt)
```

Motion and detuning act throughout; coupling scales with f(t_k). Between
pulses, the synced-phase U_gap from
[run_synced_phase.py](../numerics/run_synced_phase.py) is reused.

**Two Ω calibrations** ("amplitude-kept" vs "area-preserved"): the
amplitude-kept case shows the pulse loses rotation because ∫f < δt;
the area-preserved case rescales Ω to match the rectangular-pulse
area (what a lab would calibrate). All physics results below use
area-preservation.

Driver: [../numerics/run_aom_envelope.py](../numerics/run_aom_envelope.py).
Wall time ≈ 40 s per α per Ω-calibration per 201-point detuning scan.
Carrier-only γ_c measurement: 0.1–0.7 s per envelope.

## 2. Two envelope cases

σ is the Gaussian kernel std-dev. For an erf step, 10%–90% rise time
τ_rise ≈ 2.563 · σ. Two cases examined:

| case              | σ (ns) | 6σ edge (ns) | flat-top (ns) | area fraction | τ_rise 10–90% (ns) |
|-------------------|-------:|-------------:|--------------:|---------------:|-------------------:|
| rectangular       | 0      | 0            | 628           | 1.000         | 0 (instant)        |
| σ = 20 ns         | 20     | 120          | 508           | 0.809         | ≈ 51 ns            |
| σ = 50 ns         | 50     | 300          | 328           | 0.522         | ≈ 128 ns (slow AOM)|

"Typical" AOM (τ_rise 10-90% ≈ 50 ns) corresponds to σ ≈ 20 ns. The
σ = 50 ns case is a slow-AOM outlier included to map the trend.

## 3. Lineshape: envelope is nearly irrelevant

Sample |C|(δ₀) at |α| = 0 over ±500 kHz comparing rectangular synced
vs σ = 50 ns erf-envelope (area-preserved):

| δ (kHz) | \|C\|_rect | \|C\|_envelope | ratio |
|--------:|----------:|---------------:|-------|
| 0       | 0.92348   | 0.91908        | 0.995 |
| ±50     | 0.23018   | 0.23031        | 1.001 |
| ±100    | 0.18370   | 0.18373        | 1.000 |
| ±300    | 0.01777   | 0.01780        | 1.002 |
| ±500    | 0.05529   | 0.05544        | 1.003 |

Tooth HWHM: rect 30.1 kHz, envelope 30.2 kHz (same). Same pattern at
α = 3. **The envelope does not alter the comb structure** — the comb
is set by the inter-pulse spacing T_m and the N-pulse coherent
accumulation, which the envelope does not change under area
preservation.

## 4. Carrier (δ = 0) γ-corrections — the interesting effect

| envelope          | area frac | \|C\| φ-spread | γ_c      | arg RMS (°) | sin fit (°) | (cos−1) fit (°) |
|-------------------|----------:|---------------:|---------:|------------:|------------:|----------------:|
| rectangular       | 1.000     | 5.43 × 10⁻²    | 0.97256  | 4.53        | −0.465      | −3.627          |
| σ = 20 ns         | 0.809     | 3.75 × 10⁻²    | 0.98157  | 3.06        | −0.411      | −2.460          |
| σ = 50 ns         | 0.522     | 2.22 × 10⁻²    | 0.99030  | 1.62        | −0.320      | −1.301          |

All three metrics — |C| spread, γ_c deviation from 1, arg RMS residual —
shrink monotonically as edges soften. The trend is smooth; no
discontinuity or resonance.

**Physical mechanism.** The v0.9.1 corrections scale as (ω_m·δt_eff)²
where δt_eff is the effective duration over which coupling and motion
overlap. With rectangular pulses, δt_eff = δt_total = 628 ns and
ω_m·δt_eff = 0.817 rad (a substantial intra-pulse motion). As edges
soften, the coupling is concentrated into a shorter flat-top window
(flat_top = δt_total − 6σ), and during the ramp-up/ramp-down the
coupling is weak. The *coupling-weighted* intra-pulse motion is smaller
→ less mixing of ⟨X̂⟩ and ⟨P̂⟩ → γ_c closer to 1.

Numerically: for σ = 20 ns, flat-top fraction is 508/628 = 0.809 (same
as area fraction). The γ_c shortfall ratio between rect and σ=20:
(1 − 0.9726) / (1 − 0.9816) = 0.0274 / 0.0184 = 1.49. Expected from
flat-top ratio (628/508)² = 1.53. Matches within 3%. Similarly for
σ=50: (1 − 0.9726) / (1 − 0.9903) = 2.82; expected (628/328)² = 3.66.
Slightly less good — at σ=50 the edges are no longer small and the
linearisation breaks down, but the direction is right.

## 5. Consequence for v0.4

**The published v0.9.1 γ corrections (γ_c = 0.9726) overestimate the
physical deviation from the v0.8 ideal identity** because they use a
rectangular pulse. A realistic AOM with τ_rise 10-90% ≈ 50 ns (σ ≈ 20
ns) gives γ_c = 0.9816 — only a 1.8% shortfall rather than 2.7%. The
position-phase channel identity

```
arg C(δ_0=0, |α|, φ_α) = 90° + 2η|α|·cos φ_α
```

holds to within ~2% when the AOM envelope is modeled, not 3%. This is
a mild tightening — the physics story is unchanged, and the correction
factor is now a known function of the AOM pulse envelope.

**|C| φ-spread at σ=20 ns: 3.75%**. At σ=0 (rectangular): 5.43%. The
"velocity channel" signature the S2-revisited entry reported as "5%
spread" is an overestimate; with finite-edge pulses it's closer to
3.75% at typical AOM parameters. Still real, but smaller.

For v0.4 the right framing is: *the corrections γ_c, γ_s are set by
the protocol parameters (N, δt, ω_m) AND the pulse envelope f(t);
rectangular-pulse numbers are an upper bound on the deviation from
the ideal identity.*

## 6. Lineshape robustness — why?

The comb structure at δ = k·ω_m arises because the inter-pulse gap
contributes exp(−i·δ·σ_z·T_gap/2) per gap; over N−1 gaps the spin
phase closes when δ · T_gap is a multiple of 2π. This mechanism is
independent of what happens *during* the pulse — the pulse's role is
to provide the per-pulse rotation around the (coupling-dressed) axis,
and under area preservation this rotation is the same for any envelope
shape.

The envelope does affect the per-pulse rotation's *axis* direction
(2η|α|·cos φ_α is replaced by something slightly different for non-
trivial envelopes). But it doesn't affect the comb tooth positions or
width. Hence the lineshape robustness.

This is good news for experimental calibration: an AOM with unknown
rise time will still produce the comb at the correct frequencies;
only the peak amplitude and φ_α-dependence of arg C depend weakly on
the envelope.

## 7. Envelope affects Ω calibration, not just physics

"Area-preserved" means Ω is rescaled as 1/area_fraction. At σ = 50 ns
this is a ~2× boost (Ω goes from 0.090 MHz to 0.173 MHz). In practice
the lab calibrates Ω to hit π/2 total rotation; this calibration
automatically compensates for the envelope. So the "amplitude-kept"
case is a theoretical curiosity, not a lab configuration.

## 8. Plots

- [../plots/aom_envelope_carrier.png](../plots/aom_envelope_carrier.png) —
  four-panel summary: envelope shapes, arg-C residuals, |C|(φ_α), and
  γ_c/|C|-spread vs area fraction.

The area-fraction trend panel is the "money plot": γ_c and |C|-spread
vary smoothly and monotonically with envelope softness, with both
extrapolating to the v0.8 ideal in the zero-flat-top limit.

## 9. Files added

- [../numerics/run_aom_envelope.py](../numerics/run_aom_envelope.py) —
  detuning-scan driver with envelope wrapper.
- [../numerics/aom_envelope_alpha0and3.h5](../numerics/aom_envelope_alpha0and3.h5) —
  lineshape data at σ=50 ns (area-preserved and amplitude-kept).
- [../numerics/aom_envelope_carrier_phi.h5](../numerics/aom_envelope_carrier_phi.h5) —
  arg C(φ_α) at δ=0, α=3, σ=50 ns.
- [../numerics/aom_envelope_carrier_phi_sigma20.h5](../numerics/aom_envelope_carrier_phi_sigma20.h5) —
  same at σ=20 ns.
- [../numerics/plot_aom_envelope.py](../numerics/plot_aom_envelope.py)
- [../plots/aom_envelope_carrier.png](../plots/aom_envelope_carrier.png)
- This entry.

Engine, WP-V, prior WP-E results untouched.

## 10. Outstanding

- Ask experimental team for Hasse2024's actual AOM τ_rise value. σ
  likely 10–30 ns for a typical Gooch & Housego / Isomet AOM on the
  ion-trap timescale.
- If σ is known, quote the corresponding γ_c, γ_s in v0.4 as the
  representative value. Otherwise quote rectangular + AOM-envelope
  upper/lower bounds.
- Consider whether to add `pulse_envelope="erf"`, `envelope_sigma_us`
  keys to the engine proper (opt-in, backward-compatible). Lower
  priority than v0.4 drafting.

*Flag 1 convention + AOM envelope: the WP's physical observables
are now cleanly parameterised. Ready for v0.4 drafting.*
