# Logbook — 2026-04-14 — Flag 1 closed: synced-phase convention → comb lineshape

**Context.** The user's statement "*Phase is kept synced for all pulses
of a train*" (2026-04-14) closes Flag 1 from
[2026-04-13-flag-reruns.md §3](2026-04-13-flag-reruns.md). Under the
synced-phase convention, the laser/AC phase reference is maintained
across the full pulse train, and the spin picks up
`exp(−i·(δ/2)·σ_z·T_gap)` per inter-pulse gap.

**Consequence.** The engine (v0.9.1 at `t_sep_factor = 1.0`) omits
this inter-pulse free evolution. A driver-level fix is straightforward;
the resulting lineshape is not the engine's broad single peak but the
**comb at δ = k·ω_m** that R2 (Monroe impulsive) already produced.

**Verdict.** The comb is the physically correct |C|(δ₀) lineshape under
the synced-phase convention. The engine's reported Rabi lineshape
(HWHM ≈ 200 kHz/(2π), centred at δ₀ = 0) is a modeling artefact
specific to its `t_sep_factor = 1.0` path. All results at δ₀ = 0 stand
(see §4); all detuning-scan results from S1, S2, H1, S1-carrier-zoom,
R2-coarse need reinterpretation.

-----

## 1. Driver-level fix

Added a `U_gap` inter-pulse propagator in
[../numerics/run_synced_phase.py](../numerics/run_synced_phase.py):

```
U_gap[n, n]        = exp(−i·ω_m·n·T_gap) · exp(+i·δ/2·T_gap)
U_gap[nmax+n, ...] = exp(−i·ω_m·n·T_gap) · exp(−i·δ/2·T_gap)
```

with `T_gap = T_m − δt`. Combined with the engine's finite-δt pulse
(intra-pulse motion ω_m·a†a on), the total per-cycle motional phase is
`ω_m·δt + ω_m·(T_m − δt) = 2π`, so the strobe condition closes exactly.
The spin detuning phase accumulates only during the gap; during the
pulse it's already in the engine's Hamiltonian.

First attempt (iteration visible in git history of this file): missed
the motional factor, which broke the strobe closure and produced an
anomalous |C|(δ=0) = 0.9996 at α=0 (clean π/2 rotation; no entanglement
because the motional state's phase didn't close, so successive pulses
didn't coherently accumulate). Fixed by adding the Fock-indexed
motional phase. After fix, synced-phase matches the engine at δ = 0 to
numerical precision (0.92348 vs 0.92348 at α = 0; 0.92379 vs 0.92379 at
α = 3) — confirming δ = 0 observables are convention-invariant.

## 2. Lineshape comparison — α = 0

Sampled at selected detunings (±500 kHz around carrier):

| δ (kHz)  | \|C\|_engine | \|C\|_synced | \|C\|_R2 |
|:--------:|--------------|--------------|----------|
| 0        | 0.923        | 0.923        | 0.917    |
| ±100     | **0.912**    | **0.184**    | 0.184    |
| ±200     | 0.624        | 0.104        | 0.104    |
| ±300     | 0.100        | 0.018        | 0.018    |
| ±400     | 0.266        | 0.042        | 0.042    |
| ±500     | 0.322        | 0.055        | 0.055    |

The engine shows a broad lineshape (HWHM ≈ 200 kHz). Synced-phase and
R2 show a sharp central tooth (HWHM ≈ 30 kHz) with between-tooth |C|
at the 1–10% level. **Synced-phase overlaps R2 to within ~0.5%**
across the entire grid — the two conventions are essentially the same
physics at δ = 0 of a tooth, differing only at the 0.6% level in peak
height (0.923 vs 0.917) due to finite-δt vs impulsive pulses.

Identical pattern at α = 3. The |α|-dependence of the lineshape (if
any) is small — much smaller than the engine-vs-synced difference.

Plot: [../plots/flag1_synced_phase_lineshape.png](../plots/flag1_synced_phase_lineshape.png).

## 3. Why does the engine show a broad lineshape at all?

The engine's pulse Hamiltonian contains `(δ/2)·σ_z`, so during each
pulse the spin also picks up δ-dependent phase — for total duration
`N·δt = 18.85 μs` (at Hasse-matched δt). The resulting Rabi linewidth is
~Ω_eff ≈ 280 kHz, consistent with what we observed. This is a genuine
dynamics of the engine's protocol — just not the physically intended
one. The engine models **a continuous pulse of duration N·δt = 18.85 μs
with the laser on throughout**, rather than 30 stroboscopic flashes
totalling 17 μs of train with laser off for most of it.

Under the synced-phase convention, the spin feels δ:
- During pulses (total `N·δt = 18.85 μs`) via the pulse Hamiltonian.
- Between pulses (total `(N − 1)·T_gap = 175.2 μs`) via free evolution.

The *between*-pulse time dominates by factor ~10. The resulting
lineshape is the stroboscopic Fourier response, which has support at
δ = k·ω_m (aliasing) with tooth HWHM ≈ `1/((N−1)·T_m) ≈ 62 kHz` —
matching what we see (30–40 kHz, close to the sinc-amplitude HWHM of a
rectangular train).

## 4. What stands; what needs reinterpretation

### Stands (δ = 0 results — convention-invariant)

- **arg C identity** (both v0.8 and v0.9.1 forms):
  `arg C(0, |α|, φ_α) = 90° + 2η|α|·(γ_c cos + γ_s sin) + O(η³)`.
  Unchanged under synced-phase at δ = 0.
- **|C|(δ₀ = 0, φ_α)** 5% spread under v0.9.1 D1 Hasse-matched. Same.
- **H1 lock tolerance** — scans ε (pulse timing), not δ. At δ = 0 the
  inter-pulse Ufree is identity on spin; only the motional phase
  matters, and that's already in the engine's t_sep_factor ≠ 1 path.
  Stands.
- **Matrix-element-magnitude theorem** at v0.8 (machine precision).
  Property of the operator ⟨α|C|α⟩ itself, independent of protocol.

### Needs reinterpretation (δ ≠ 0 results)

- **S1 slice** (|C|(δ₀) at φ_α = 0) — the "Doppler-broadened"
  lineshape we reported is not the synced-phase physics. The true
  |C|(δ) has the comb structure with α-independent envelope (the
  α-dependence is in how individual tooth heights scale, not in the
  lineshape).
- **S2 residual at δ ≠ 0** — both full and R1 engine lineshapes are
  model-convention artefacts. The comb-to-comb comparison is what
  matters.
- **S1 carrier-zoom** (±500 kHz fine grid) — the peak bias at −206 kHz
  for full engine was a Magnus-like effect in the broad-lineshape
  regime. Under synced-phase, the central tooth is at δ = 0 exactly
  (|C|_synced has peak within 10 kHz of zero in the fine-grid data at
  both α values). So the reported "Magnus carrier-bias linear in η"
  (−206 vs −21 kHz pair) is a property of the engine's wrong
  convention, not synced-phase physics. Needs to be retracted or
  reframed.
- **R2 fine-tooth characterisation** (HWHM 41 kHz) — this IS
  synced-phase physics. The reported tooth shape is correct;
  interpretation as "theoretical sideline" was too conservative. R2
  is the correct lineshape under the user-confirmed convention.
- **R2 comb logbook** — the argument that "engine matches experiment
  because comb not reported" is weakened. The user's statement
  supports the comb being correct; the experimental question is
  whether Hasse2024 scans reach δ > 100 kHz (if they do and observe a
  single peak, that would challenge the synced-phase assumption).

## 5. Consequences for WP-E v0.4

The WP's position-phase channel framing strengthens:

- `arg C = 90° + 2η|α|·cos φ_α` holds at carrier regardless of convention.
- `|C|(δ₀)` lineshape is the synced-phase comb, not the engine's broad
  peak. This **simplifies** the WP's story — `|C|` no longer has a rich
  Rabi-like δ₀-dependence to report; it has sharp teeth at δ = k·ω_m,
  each with the same magnitude, and between-tooth the signal is ~0.
- The injectivity map `(|α|, φ_α) → (Re C, Im C)` at δ = 0 is
  unchanged by convention.
- WP-E's deliverables 1-3 (datasets, plots, logbook) need revised
  figure-captions and text footnotes, NOT a full recomputation — the
  carrier-column of each dataset is still valid; the rest of the
  detuning sweeps are "engine-convention probes" rather than "physics".

**Recommendation for v0.4:** Report the S1/S2 at δ = 0 slices as the
physical results (position channel, φ_α spread). Keep the full
(δ, |α|) heatmaps as engine-convention diagnostic plots with an
explicit "engine convention, not synced-phase physics" caveat.
Reference this entry and the Monroe/synced-phase comb as the correct
resolved-sideband spectrum.

## 6. Does this challenge Hasse2024's lineshape?

If Hasse2024 reports a Rabi scan with a broad peak (HWHM ~ Ω_eff), that
is inconsistent with the synced-phase assumption. Two possibilities:

- **Their scans don't cover δ > 100 kHz.** Within the central tooth
  the engine and synced lineshape are similar (both drop steeply near
  0); if they only scanned ±100 kHz they'd see the tooth and not the
  comb structure. No tension.
- **Their scans are wider but see a single broad peak.** Then the
  synced-phase assumption is wrong in their setup — e.g., the AC phase
  is reset per pulse, or there's a mechanism I haven't modeled that
  suppresses the comb (phase noise, intensity jitter, finite-duration
  analysis pulse envelope).

This is the experimental question Flag 1 was meant to answer. The user's
confirmation of "phase kept synced" resolves it in principle; resolving
the apparent tension with the engine's lineshape (if any) needs
experimental data. For v0.4: report the synced-phase prediction and
flag this as an open experimental comparison.

## 7. Files added in this entry

- [../numerics/run_synced_phase.py](../numerics/run_synced_phase.py)
- [../numerics/synced_phase_alpha0and3.h5](../numerics/synced_phase_alpha0and3.h5)
- [../numerics/plot_synced_phase.py](../numerics/plot_synced_phase.py)
- [../plots/flag1_synced_phase_lineshape.png](../plots/flag1_synced_phase_lineshape.png)
- This entry.

Engine and all prior numerics unchanged (Guardian cadence).

## 8. Outstanding for v0.4

Flag 1 status after this entry:

- ✓ Convention established: phase-synced, laser reference maintained.
- ✓ Synced-phase propagator implemented at driver level; matches R2.
- ✓ Δ-scan results reinterpreted (see §4).
- ? Experimental-team cross-check still worthwhile for Hasse2024
  lineshape breadth.
- ? Consider adding `inter_pulse_free_evolution=True` toggle to the
  engine itself (opt-in, backward-compatible), rather than driver-
  level patch — but this is an engine change and should be staged
  separately.

Subsuming Flag 1 into v0.4 as "user-confirmed synced-phase convention;
R2 lineshape is canonical; engine convention is a modeling
simplification documented here".

*Next step: Council checkpoint on whether v0.4 drafting should begin
now, or whether additional slices under synced-phase (S2 at α ∈ {1, 5}
reconfirmation? S3 un-deferred?) should run first. These are cheap
now that the propagator is validated.*
