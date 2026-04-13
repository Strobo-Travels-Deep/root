# Logbook — 2026-04-13 — S2 revisited under engine v0.9.0

**Context.** Sequel to
[2026-04-13-S2-falsification.md](2026-04-13-S2-falsification.md). That
entry proved the matrix-element-magnitude theorem
`|⟨α|C|α⟩| = exp(−η²/2)` and concluded that |C| is φ_α-independent for
coherent states under the stroboscopic protocol. Falsification was at
machine precision (worst Δ|C| = 6.6 × 10⁻¹³).

WP-V's engine audit
([../../wp-hasse-reproduction/logbook/2026-04-13-engine-audit.md](../../wp-hasse-reproduction/logbook/2026-04-13-engine-audit.md))
identified that the v0.8 engine *drops* `ω_m a†a` from the per-pulse
Hamiltonian (audit item D1). Engine v0.9.0 added the
`intra_pulse_motion=True` toggle that restores it. Question: does the
matrix-element-magnitude theorem survive D1?

**Answer: no — it survives only at the level of the v0.8
approximation.**

-----

## 1. Quick numerical re-check at α = 3

Driver: ad-hoc φ_α scan at three engine configurations,
α = 3, η = 0.397, ω_m = 1.3, n_thermal = 0.

| Configuration                                   | |C| min   | |C| max   | spread       |
|-------------------------------------------------|-----------|-----------|--------------|
| v0.8-equivalent (intra_pulse_motion=False)      | 0.916566  | 0.916566  | **3 × 10⁻¹⁵** |
| v0.9 D1 on, default WP-E params (N=22, δt auto) | 0.915912  | 0.927576  | **1.17 × 10⁻²** |
| v0.9 D1 on, Hasse-matched (N=30, δt=0.13·T_m)   | 0.894060  | 0.948126  | **5.41 × 10⁻²** |

The first row reproduces the published S2 falsification number: the
theorem holds at machine precision under v0.8. The second and third
rows show the theorem broken at the **1 % and 5 % levels** when
intra-pulse motion is included.

The 5 % case is the more physically faithful one (it matches Hasse's
Appendix D protocol regime). Motivation 3 of the original WP-E
framing (Doppler-broadening signature in |C|) is therefore **not
falsified at the protocol level** — it was falsified only against the
v0.8 stroboscopic-frame approximation, where ω_m·a†a was dropped from
the per-pulse Hamiltonian.

-----

## 2. Why the theorem fails under D1

The displacement-operator identity
`D(α)†(a + a†) D(α) = (a + a†) + 2 Re(α)` is unchanged. The proof of
the theorem in the S2 falsification entry §3 used:

```
⟨α|exp(iη(a + a†))|α⟩ = exp(−η²/2) · exp(i · 2η|α| cos φ_α)
```

i.e., the matrix element of a single, instantaneous coupling operator
C between displaced ground states. This is exact.

The v0.8 engine evolves each pulse by exp(−i δt · H_eng) with
H_eng = (Ω/2)(C σ_- + C† σ_+) (no ω_m·a†a). For coherent input |α⟩,
the leading-order spin response per pulse is set by ⟨α|C|α⟩ — which
has the φ_α-independent magnitude. Higher-order corrections involve
matrix elements between |α⟩ and shifted states, but these contribute
only at O((ηΩδt)²) above the leading O(ηΩδt) term, and the per-pulse
budget here is (Ω_eff·δt) ≈ π/(2N) ≈ 0.071 rad — small. Hence the
theorem is *protected by the smallness of per-pulse rotation* in the
v0.8 frame.

Under v0.9 D1, the per-pulse evolution becomes
H_v0.9 = ω_m·a†a + (Ω/2)(C σ_- + C† σ_+). Now during δt the motional
state rotates by ω_m·δt (~0.34 rad in the default regime, ~0.82 in the
Hasse-matched regime). The coupling operator effectively averages over
this rotation:

```
C̄(δt) = (1/δt) ∫₀^δt exp[iη(a e^{−iω_m t} + a† e^{+iω_m t})] dt
```

`|⟨α|C̄(δt)|α⟩|` is **no longer φ_α-independent**: the phase under the
integral mixes ⟨X̂⟩ = 2|α| cos φ_α and ⟨P̂⟩ = 2|α| sin φ_α
contributions in a φ_α-asymmetric way. This is exactly the regime
where Hasse's velocity-encoded contrast comes from.

In our numerics: the v0.9 spread is about (η · |α| · ω_m · δt) ≈
0.397·3·1.3·0.628 ≈ 0.97 rad → contrast variation of order
1 − cos(0.97)/cos(0) ≈ 47 %; the actual measured spread of 5.4 % is
reduced by the Bessel-like averaging over δt, but not to zero. Order
of magnitude consistent.

-----

## 3. Implications for WP-E

The S2 falsification entry §4 reduced WP-E to "1.5 motivations" by
eliminating motivation 3 (Doppler signature). Under v0.9 D1, that
elimination must be **partially reversed**:

| Motivation              | v0.8 status       | v0.9 D1 status                        |
|-------------------------|-------------------|---------------------------------------|
| 1: arg C as position    | ✓ confirmed       | ✓ confirmed (theorem on phase intact) |
| 2: φ_α as lock probe    | ½ alive           | ½ alive — same role                   |
| 3: |C|(δ₀) Doppler sig  | ✗ falsified (10⁻¹³)| **¼ — small (1–5 %) but real signal** |

Motivation 3 is now: "|C|(δ₀) carries a small (1–5 %) φ_α-dependent
signature whose magnitude is set by η·|α|·ω_m·δt; that signature is
the Doppler velocity channel as predicted by the dossier §1.4
analytical sketch, but suppressed by stroboscopic time-averaging
relative to a non-stroboscopic continuous Rabi reading."

So the dossier's velocity-channel intuition was *qualitatively right*.
The v0.8 falsification was a quantitative artefact of the missing
ω_m·a†a term — exactly the audit item D1 that WP-V identified
independently.

-----

## 4. What this changes operationally

### Existing S1, S2 (|α|=1,3,5), R2, H1 datasets

Were generated under v0.8 (intra_pulse_motion=False, default).
**They remain valid** — they correctly characterise the engine's
v0.8-mode behaviour, which is what the published WP-E plots and
deliverables describe. They do **not** characterise the corrected
Hasse-protocol behaviour.

### WP-E v0.4 README

Must address this gap directly. Two options:

(a) **Re-run S1, S2 sheets under v0.9 D1** and replace the published
    plots. Larger compute (~factor 2 over v0.8 since the per-pulse
    propagator is now 2nmax × 2nmax with non-zero diagonal, but
    expm scaling unchanged); preserves WP-E's data products as
    canonical.

(b) **Keep v0.8 plots, add a v0.9 comparison panel.** Cheaper. A
    single sheet at α = 3 under v0.9 D1 + Hasse-matched is enough to
    document the 5 % φ_α-dependence and bound it; the rest of the
    WP-E claims about arg C remain valid as published.

Option (b) is the lighter path; option (a) is the more rigorous one.
**Recommend (b)** because:
- The S2 falsification's primary finding (theorem at machine
  precision) is a clean v0.8 result that should not be overwritten —
  the v0.8 → v0.9 contrast is the *interesting* finding.
- WP-V already demonstrated the difference at the panel level
  (Fig 6/8). Re-deriving it inside WP-E adds little.
- Compute budget: option (a) is roughly 30 min wall; (b) is ~2 min.

### Deliverable 5 (Jacobian + cond-J)

The reframed simplification in the S2 falsification §8 ("J = diag(0,
J_arg) on (|α|, φ_α) for |C|") needed the theorem. Under v0.9 the
J_|C| row is no longer identically zero — it has small but non-zero
entries ∂|C|/∂|α| and ∂|C|/∂φ_α. Conditioning analysis must include
these. Adds one row to the cond(J) heatmap; doesn't change the
deliverable scope.

### S3 (|α|, φ_α at fixed δ₀)

Was deferred indefinitely as redundant after S2. Under v0.9 it is
**no longer redundant**: the (|α|, φ_α) → |C| map has 5 %-level
structure that S3 is the cleanest probe of. Recommend
**un-deferring S3** for execution under v0.9 D1.

-----

## 5. Recommendations

1. Add a §3.1bis paragraph to WP-E v0.4 README naming the
   v0.8 → v0.9 motivation reversal and citing this entry.
2. Run S2 |α|=3 under v0.9 D1 + Hasse-matched as a single comparison
   sheet (option (b) above), tagged S2_v09.
3. Un-defer S3 in v0.4 §8 outstanding actions; queue it for execution.
4. Update Deliverable 5 to read "J on (|α|, φ_α) under both engine
   modes" so the v0.8/v0.9 contrast is preserved.
5. Footnote in the short note (Deliverable 4) acknowledging that
   WP-V's audit findings retroactively change WP-E's motivation 3.

None of this invalidates published WP-E results. It adds context.

-----

## 6. Update (engine v0.9.1 — pulse-centering convention)

Subsequent exchange raised the question: is pulse 1 timed to the
motional position extremum when φ_α = 0? Under v0.9.0, pulse 1
*starts* at φ_α = 0 but spans into negative phase territory during
δt (ω_m·δt ≈ 47° at Hasse-matched parameters). The physically natural
convention is to have pulse 1 *centered* on φ_α = 0 — a symmetric
reading of "pulse timed at position max".

Engine v0.9.1 adds `center_pulses_at_phase` (opt-in, default False).
When True, the engine shifts the prepared motional phase by
`+ω_m·δt/2` internally so that every stroboscopically-synchronous
pulse (including pulse 1) is centered on the user-specified
`alpha_phase_deg`. Backward compatibility preserved at defaults.

### S2 v0.9 comparison rerun under centered convention

Driver: [run_S2_v09_compare.py](../numerics/run_S2_v09_compare.py)
(updated to set `center_pulses_at_phase=True`).
Output: same H5 path (overwritten) + updated plot
[S2_alpha3_v09_compare.png](../plots/S2_alpha3_v09_compare.png).

| Quantity                               | v0.8    | v0.9.0 D1 Hasse-matched | v0.9.1 +centered |
|----------------------------------------|---------|-------------------------|-------------------|
| worst \|Δ\|C\|(δ, φ)\| vs φ=0          | 6.6×10⁻¹³ | 6.93×10⁻²             | **7.01×10⁻²**     |
| carrier \|C\|(δ=0, φ_α) spread         | —       | 5.40×10⁻²               | **5.43×10⁻²**     |

**Verdict.** The 5 % |C| spread is **real physics**, not a timing
artefact. Pulse-centering shifts *where* in φ_α the min/max of |C|
occur, but not the spread magnitude — the |C|(φ_α) envelope is a
closed loop over [0, 2π), and both conventions traverse the same loop
from different starting angles.

This is the cleaner version of the S2 v0.9 revisited finding: WP-E's
motivation 3 (Doppler signature in |C|) is partially restored at
~5 % under the corrected protocol, invariant under the pulse-centering
convention. The canonical number for WP-E v0.4 is
**worst |Δ|C|| = 7.0 × 10⁻²** — eleven orders of magnitude above the
v0.8 falsification.

-----

## 7. Status

Engine: v0.9.1 (adds `center_pulses_at_phase`; v0.9.0 behaviour default).
Files added/updated: this entry + the comparison driver + HDF5 + plot.
WP-E published deliverables: unchanged; reinterpreted.

*Next entry: WP-E v0.4 README, incorporating S2 falsification, v0.9
re-evaluation, S3 un-deferral, and WP-V cross-references.*
