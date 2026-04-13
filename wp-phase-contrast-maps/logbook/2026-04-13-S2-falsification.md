# Logbook — 2026-04-13 — S2 sheet at |α|=3 — falsification of the Doppler-broadening hypothesis

**Context.** Sequel to `2026-04-13-S1-plots.md`. Guardian explicitly
invited the test: *"if [the |α|·|sin φ_α| broadening prediction] fails:
stop, post a logbook entry naming the failure mode."* It failed. The
mechanism is now understood and is more interesting than the failed
prediction would have been.

**Verdict.** Hypothesis **falsified to numerical precision**. The
|C|(δ₀, φ_α) lineshape is φ_α-independent at |α| = 3 — worst |Δ|C||
across 64 φ_α values vs the φ_α = 0 reference is **6.6 × 10⁻¹³**, i.e.
machine precision. The Doppler-broadening picture from dossier §1.4 does
*not* apply to coherent states in the stroboscopic limit; the matrix
element ⟨α|exp(iηX̂)|α⟩ has magnitude exp(−η²/2) **independent of α and
φ_α**, so the spin-only effective coupling magnitude is constant.

The φ_α dependence is real and substantial — but it lives entirely in
**arg C**, not in |C|. The position-phase channel maps the matrix-element
phase 2η|α| cos φ_α (η-dressed) and matches the closed-form prediction.

This sharpens, rather than weakens, the WP-E framing.

-----

## 1. Pre-registered hypothesis (from `2026-04-13-S1-plots.md` §2)

*"At φ_α = π/2, ⟨P̂⟩ = 2|α| (maximum), and we expect maximum Doppler
broadening of |C|(δ₀) scaling with α. At intermediate φ_α, the
broadening should scale as |α| · |sin φ_α|."*

**Quantitative target.** δ_D^peak at α = 3, φ_α = π/2:
2η · ω_m · |α| = 2 × 0.397 × 1.3 × 3 = **3.10 MHz/(2π)**, with
δ_D / Ω_eff ≈ 11.2 — deeply Doppler-dominated.

If the hypothesis were correct, HWHM of |C|(δ₀) at φ_α = π/2 would be
roughly half this peak shift (~1.5 MHz/(2π)), shrinking to the
underlying finite-time width (~0.77 MHz/(2π)) at φ_α = 0, π. Predicted
fit:

```
W(φ_α) = W_0 + b · |sin φ_α|,   with W_0 ≈ 0.77 MHz, b ≈ 1.5 MHz.
```

## 2. Measurement

Driver: [../numerics/run_slices.py](../numerics/run_slices.py)
`execute_S2_sheet`. Output: [../numerics/S2_delta_phi_alpha3.h5](../numerics/S2_delta_phi_alpha3.h5).
Grid: 64 φ_α × 121 δ₀ × 2 engines (full η = 0.397 + R1 η = 0.04). Wall
time 96 s; worst Fock leakage 1.2 × 10⁻⁹.

**HWHM fit result:**

```
W(φ_α) = W_0 + b · |sin φ_α|
W_0 = 0.7710 MHz/(2π)        (matches finite-time-only width at φ_α = 0)
b   = 0.0000 MHz/(2π)        (Doppler-broadening amplitude — vanishes)
fit residual rms = 0.0000     (HWHM is constant to printout precision)
```

The Doppler amplitude is zero. Predicted: 1.55 MHz/(2π). **Ratio measured /
predicted = 0.000.**

**Stronger test — full lineshape:**

```
worst |Δ|C|(δ, φ_α)| vs φ_α = 0 reference, all 64 φ_α: 6.6 × 10⁻¹³
```

The lineshape is φ_α-independent to machine precision, not just within
some fitting tolerance. This is a hard falsification, not a marginal
miss.

**Symmetry test:** |C|(δ, φ_α) = |C|(δ, φ_α + π) to ≤ 2 × 10⁻¹⁵ across
all (δ, φ_α). Confirms the cos(φ_α)-only structure of the underlying
matrix element (period π in any quantity that depends on cos² or |cos|).

## 3. Mechanism — what was wrong with the hypothesis

The naïve picture conflated continuous Doppler-driven dynamics with the
stroboscopic protocol. In the stroboscopic case, between pulses the
motion is *not* free-evolved (`t_sep_factor = 1.0` ⇒ `need_free = False`
in [../../scripts/stroboscopic_sweep.py:382](../../scripts/stroboscopic_sweep.py#L382));
each pulse hits the ion at the same point in phase space. The "velocity
distribution" picture of dossier §1.4 — each detuning class selecting a
velocity class — applies to a *thermal mixture* with a velocity spread,
not to a coherent state with a definite (X̂, P̂) at the sampling phase.

For a coherent state |α e^{iφ_α}⟩, the carrier matrix element is

```
⟨α|exp(iη(a + a†))|α⟩ = exp(-η² / 2) · exp(i · 2η|α| cos φ_α)
```

via the displacement-operator identity D(α)†(a + a†)D(α) = (a + a†) +
2 Re(α). Critically:

- |⟨α|C|α⟩| = exp(−η²/2) ≈ 0.9242 — constant in α and φ_α.
- arg ⟨α|C|α⟩ = 2η|α| cos φ_α — depends on the position quadrature
  ⟨X̂⟩ = 2|α| cos φ_α, not the velocity quadrature.

To leading order, the spin's effective rotation amplitude per pulse
scales with this magnitude, accumulates linearly across N = 22 pulses,
and gives π/2 at carrier resonance — α- and φ_α-independent. Hence the
contrast magnitude has no Doppler signature in this protocol. The whole
lineshape, not just the carrier, is invariant.

This is in fact **the design property** that makes the protocol work
across motional states: the magnitude of the spin response is robust to
|α| and φ_α; all the information lives in arg C. We had
re-discovered it by negation.

Verification of the closed-form theory against measurement at α = 3,
η = 0.397:

| φ_α  | 2η|α| cos φ_α (rad) | (deg)       |
|------|---------------------|-------------|
| 0°   | +2.382              | +136.5°     |
| 90°  | 0                   | 0°          |
| 180° | −2.382              | −136.5°     |
| 270° | 0                   | 0°          |

The measured arg C(δ_0=0) traces this cos-shaped curve plus an overall
carrier offset, η-dressed by N-pulse accumulation (visible as wrapping
in the bottom-right panel of [../plots/S2_alpha3_summary.png](../plots/S2_alpha3_summary.png)).
At η = 0.04 (R1), the wrapping is absent — the ramp is gentle —
confirming the η-dressing interpretation.

## 4. Honest scope assessment — implications for WP-E

This is the second motivation reduction in two days, both honest:

1. **Preflight (2026-04-13):** dossier §1.4's "HDF5 vs JSON contrast
   provenance mismatch" was a synthetic-data artefact, not a physics
   disagreement. Externalised to dossier maintainers.
2. **S2 (this entry):** dossier §1.4's "Doppler-broadening as a function
   of motional amplitude" doesn't apply to coherent states under
   stroboscopic locking. The whole velocity-channel motivation, as
   originally framed for *coherent states*, does not exist for this
   protocol.

Therefore: **WP-E's three motivations have collapsed to one-and-a-half**:

- ✓ **arg C as position channel** (motivation 1) — confirmed strongly by
  S1 and S2; matches closed-form 2η|α| cos φ_α theory.
- ½ **φ_α as stroboscopic-lock diagnostic** (motivation 2) — still alive,
  but now repurposed: instead of testing Doppler-broadening tolerance,
  it tests how arg C varies with strobe alignment (closely related to
  the Floquet stretch deliverable H1 from v0.3).
- ✗ **Doppler-broadening signature** (motivation 3) — falsified at the
  protocol level for coherent states. *Not WP-E's failure*; the dossier
  picture this motivation cited was the wrong picture.

The Doppler signature DOES presumably appear for **thermal mixtures** —
where ⟨n⟩ encodes an actual velocity spread rather than a definite
phase-space coordinate. Testing this is *out of scope* (v0.3 §3.3:
"non-coherent motional states deferred to WP-C"), but the pointer is
recorded for WP-C's framing.

This is a *strengthening* of WP-E, not a weakening:

- The forward map C(δ₀, |α|, φ_α) for coherent states is now known to
  factorise: |C| depends only on δ₀ (and η, ω_m, etc.); arg C carries
  all (|α|, φ_α) information.
- The injectivity probe (P7 / WP-E §4 deliverable 5) becomes simpler:
  the Jacobian along the |α| and φ_α axes vanishes for |C| but not for
  arg C. Conditioning analysis reduces to "is arg C(δ₀, |α|, φ_α) an
  injective map from (|α|, φ_α) to (Re C, Im C)?" — a 2D-to-2D question
  on the unit circle, much cleaner than the original 3D map question.
- The "Δη / Δt / cross" decomposition becomes sharper: Δη is a pure
  phase effect at the carrier; Δt is the small finite-pulse-duration
  contrast bias seen as the ±0.20 MHz/(2π) carrier shift in S1.

## 5. Plots produced

Both written by [../numerics/plot_S2.py](../numerics/plot_S2.py) to
[../plots/](../plots/):

- **[S2_alpha3_summary.png](../plots/S2_alpha3_summary.png).** Headline.
  Top-left: |C|_full vertical bands (the falsification, made visual).
  Top-right: arg C_full HSV map showing rich φ_α structure.
  Bottom-left: |C|(δ₀) at 8 φ_α values, all overlapping (the
  φ_α-independence at line-cut level).
  Bottom-right: arg C(δ_0 = 0) vs φ_α with theory overlay
  +2η|α| cos φ_α + offset for both engines. The R1 (η = 0.04) trace
  matches the linear theory; the full trace shows η-dressing wrapping.
- **[S2_alpha3_residuals.png](../plots/S2_alpha3_residuals.png).** Δ_η
  decomposition. Top-left: Δ_η|C| vertical bands (φ_α-independent, as
  expected since both engines individually are φ_α-independent in |C|).
  Top-right: Δ_η arg C strong cos-φ_α structure modulated by detuning.
  Bottom-left: |C|(φ_α) flat at two δ₀ values, full and R1 — visual
  Doppler-flat confirmation.
  Bottom-right: Δ_η arg C(δ_0=0) clean cos-shaped curve with amplitude
  ≈ 130° — the full η-driven phase signal.

## 6. Honest self-criticism

- The mechanism — that |⟨α|C|α⟩| = exp(−η²/2) is α- and φ_α-independent
  — is *immediately derivable* from the displacement-operator identity
  D(α)† X̂ D(α) = X̂ + 2 Re(α). I should have done this calculation
  before writing the S1-plots logbook §2 prediction. I did not. The
  prediction was made by analogy to "Doppler shift broadens lineshapes",
  without checking that the analogy carried over from continuous Rabi
  driving to stroboscopic protocols.
- Guardian's framing — "rather see a failed prediction at S2 than a
  successful one with a hidden error" — is exactly the right insurance.
  The execution discipline of "stop, post a logbook entry naming the
  failure mode" is what kept this honest. Without the pre-registered
  hypothesis, the S2 result would read as a routine confirmation; with
  it, the result is a sharper finding.
- The "promote S2 priority" recommendation in the S1-plots logbook §2
  was correct in operational terms (S2 was the next thing to run) even
  though it was wrong in motivational terms (it was supposed to expose
  Doppler, not eliminate it).

## 7. v0.4 README amendments — additional staging

In addition to the amendments staged in `2026-04-13-S1-and-R1.md` §5
and `2026-04-13-S1-plots.md`:

- **§3.1 motivation 3.** Drop entirely from the WP-E framing for
  coherent states. Replace with a forward-pointing note: "Doppler
  signatures of thermal motional states are deferred to WP-C; for
  coherent states, the matrix-element-magnitude theorem (this entry §3)
  shows that |C|(δ₀) is independent of (|α|, φ_α), and the velocity
  channel as originally framed does not apply."
- **§3.1 (new framing).** WP-E now has 1.5 motivations, not 2.5: the
  position channel (confirmed) and the stroboscopic-lock /
  φ_α-dependence diagnostic (alive but repurposed).
- **§4 deliverable 5 (injectivity).** Reframe: the Jacobian factorises
  as J = diag(0, J_arg) on (|α|, φ_α) for |C|; conditioning analysis
  reduces to whether arg C is injective from (|α|, φ_α) to the unit
  circle.
- **§4a (gate amendment).** Add a "matrix-element-magnitude theorem"
  pre-check: any future protocol claim involving Doppler broadening of
  coherent states should be checked against ⟨α|C|α⟩ closed form before
  running large sweeps.
- **Credit attribution.** Per Guardian's note: the WP started at 3
  motivations and *earned* the reduction to 1.5 through the preflight
  (½ off) and S2 (1 off). v0.4 should narrate that history, not present
  the reduced scope as if it were the original plan.

## 8. Outstanding actions (updated)

Reordered after this entry:

- [ ] **Decide S2 sheet expansion.** With |C| φ_α-independence proven,
      the |α| ∈ {1, 5} sheets of S2 add little for the contrast
      observable; they would test only the η-dressing of arg C at
      different |α|. Cheap (~3 min total) — recommend running them for
      completeness of the arg C(α, φ_α) map, since that is now the
      central object.
- [ ] **Reconsider S3.** Per Guardian flag 3, S3 may be redundant after
      S2. Specifically: S3 is (|α|, φ_α) at fixed δ₀. With
      φ_α-independence of |C| established, S3 reduces to mapping
      arg C(|α|, φ_α) at carrier — which can be extracted from the
      |α| ∈ {1, 3, 5} S2 sheets directly. **Defer S3 indefinitely**
      pending demonstrated need.
- [ ] R2 (instantaneous-pulse) implementation — interpretation reframed:
      R2 will quantify the small finite-pulse-duration contrast bias
      (the carrier offset to −0.20 MHz/(2π)), the only place Δt has
      visible work to do.
- [ ] Floquet stretch deliverable H1 — promote: with |C| robust to
      coherent-state parameters, H1 is the cleanest test of the
      stroboscopic-lock tolerance, and the engine already supports it
      via `t_sep_factor`.
- [ ] v0.4 README — *after* S2 sheets at |α| ∈ {1, 5} and either R2 or
      H1 lands.

## 9. Files added in this entry

- [../numerics/S2_delta_phi_alpha3.h5](../numerics/S2_delta_phi_alpha3.h5)
  — S2 dataset, |α|=3, full + R1.
- [../numerics/plot_S2.py](../numerics/plot_S2.py) — S2 plot driver.
- [../plots/S2_alpha3_summary.png](../plots/S2_alpha3_summary.png).
- [../plots/S2_alpha3_residuals.png](../plots/S2_alpha3_residuals.png).
- This entry.

Engine [../../scripts/stroboscopic_sweep.py](../../scripts/stroboscopic_sweep.py)
unchanged. README.md unchanged (Guardian cadence).

*Next entry: S2 at |α| ∈ {1, 5}, then R2 or H1, then v0.4.*
