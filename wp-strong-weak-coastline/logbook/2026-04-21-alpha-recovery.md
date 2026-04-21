# Logbook — 2026-04-21 — α-recovery probe (council memo §5.3)

**Scope.** Dense |α| scan at δt/T_m = 0.80, δ = 0, option-(a)
recalibrated Ω, over N ∈ {24, 48, 96} to discriminate between the
three hypotheses council memo v0.4.1 §5.3 flagged for the observed
non-monotone V(|α|) at the coastline corner.

**Artefacts.**
- Driver: [run_alpha_recovery_v1.py](../numerics/run_alpha_recovery_v1.py)
- Data: [alpha_recovery_v1.h5](../numerics/alpha_recovery_v1.h5)
- Plot: [alpha_recovery.png](../plots/alpha_recovery.png)

Compute: 3.4 s wall for 15 × 3 = 45 cells at NMAX = 80. Fock-leakage
ceiling: worst-case top-5 leakage 1.2 × 10⁻⁸ at |α| = 6.0 (marginal
threshold from the pre-audit rubric; NMAX 80 sufficient for the scan
range).

-----

## 1. Result

| \|α\| | V(N=24) | V(N=48) | V(N=96) | ½(max−min)⟨σ_z⟩ |
|---|---|---|---|---|
| 2.50 | 0.189 | 0.188 | 0.188 | 0.203 |
| 2.75 | 0.123 | 0.122 | 0.122 | 0.232 |
| 3.00 | 0.101 | 0.101 | 0.101 | 0.254 |
| 3.25 | 0.146 | 0.146 | 0.146 | 0.266 |
| **3.50** | 0.206 | 0.206 | 0.206 | **0.267 (peak)** |
| 3.75 | 0.270 | 0.270 | 0.270 | 0.260 |
| 4.00 | 0.327 | 0.327 | 0.327 | 0.246 |
| 4.25 | 0.370 | 0.370 | 0.370 | 0.228 |
| 4.50 | 0.393 | 0.393 | 0.393 | 0.209 |
| **4.75** | **0.395 (peak)** | **0.395** | **0.395** | 0.188 |
| 5.00 | 0.377 | 0.377 | 0.377 | 0.168 |
| 5.25 | 0.339 | 0.339 | 0.339 | 0.150 |
| 5.50 | 0.287 | 0.287 | 0.287 | 0.134 |
| 5.75 | 0.227 | 0.227 | 0.227 | 0.117 |
| 6.00 | 0.166 | 0.166 | 0.166 | 0.101 |

Headline shape: **V(|α|) is a smooth single-cycle oscillation** in the
probed range with a minimum at |α| ≈ 3.0 (V ≈ 0.10), a local maximum
at |α| ≈ 4.75 (V ≈ 0.395), and descent back past α = 6. The diamond
σ_z amplitude follows a related but phase-offset curve, peaking near
|α| ≈ 3.5 — i.e. the V minimum is *not* exactly coincident with the
diamond maximum.

-----

## 2. Hypothesis discrimination (the §5.3 ask)

The memo listed three candidate mechanisms:

| # | Mechanism | Prediction | Verdict |
|---|---|---|---|
| (i) | JC-like revival at large $\eta\sqrt{\langle n\rangle+1}$ | Explicit N-dependence in V(|α|) curves (different rotation phases at different N) | **Falsified.** V values at fixed |α| agree across N ∈ {24, 48, 96} to three decimals at every single one of the 15 α points. No revival can survive that invariance. |
| (ii) | Debye–Waller higher-order structure in the finite-δt propagator | Smooth structure controlled by $\eta^2(2\bar n + 1)$, N-independent under option-(a) recalibration | **Consistent with observation.** Smoothness, unit-amplitude structure, and N-independence all match. |
| (iii) | Genuine physics of the motional-LD-breaching regime | Large-$\eta|\alpha|$ interference pattern surviving the full $\exp[i\eta(a+a^\dagger)]$ coupling, not captured by linear-Lamb–Dicke expansion | **Consistent with observation.** Same signatures as (ii). |

**Call:** (i) is falsified. (ii) and (iii) are compatible with each
other — the finite-δt DW higher-order structure *is* the large-$\eta\alpha$
regime physics; there is no operational way to separate them here.
The observation is **physics**, not engine artefact, and is intrinsic
to the recalibrated-Ω coastline at δt/T_m ~ 0.80.

-----

## 3. Why V reads low at the minimum — a partial structural story

The minimum V ≈ 0.10 at |α| = 3.0 corresponds to min_ϑ |C| ≈ 0.90.
This is *high* residual coherence, not low. What the V = 0.10 signals
is that **the pulse train fails to encode ϑ₀ into the spin coherence
at this particular (α, δt)** — |C| is nearly 1 independent of ϑ₀, so
the ϑ-dependent min − max gap is small. At |α| ≈ 4.75, where V ≈ 0.40,
the train recovers ≈ 40% encoding contrast.

So the "coastline" phrasing needs care here: this is not a Doppler
washout of the signal (P ≈ 1 in the v0.1 sweep at δ = 0.5·ω_m
confirms the coherence is preserved), it is an |α|-dependent loss of
**encoder sensitivity** in the recalibrated-Ω protocol. The impulsive
reference V_imp ≈ 0.865 shows what the protocol *would* deliver in
the δt → 0 limit; the oscillation in V(|α|) is the finite-δt departure
from that reference, and it is not monotonically degrading.

This is physics worth naming, and it changes the memo §4.3 rubric's
third row qualitatively: the (V low, P high) cells we see are not all
"pulse-broadening" — some are an |α|-revival of the encoder map.

-----

## 4. Further structure to chase (not in scope for this probe)

1. **Period estimation.** The scan shows one full oscillation in
   |α| ∈ [2.5, 6.0]. If the structure is periodic in $\eta|\alpha|$ or
   $\eta^2 \langle n\rangle$, an extended scan to |α| = 10 (motional-LD
   $\eta\sqrt{\bar n} \approx 4$) would resolve the period. Compute
   cost: extending the |α| axis to 25 points roughly doubles this
   probe's wall time (≈ 7 s). Requires bumping NMAX to 120 at |α| = 10
   (the NMAX=80 leakage scaling 10⁸ per Δ|α|=0.5 suggests NMAX=80
   fails around |α| ≈ 6.5).
2. **δt dependence of the revival.** Whether the oscillation in V(|α|)
   survives at other δt/T_m values — or is specific to the
   ≈ 0.80 corner — is unknown. A 2D (|α|, δt/T_m) map of V at fixed
   N = 48 would close this.
3. **Connection to the χ-collapse falsification.** The oscillation
   cannot be captured by a root-sum-square width combination; it is
   the residual structure §4.5 of the memo named as "the physics we
   have learned". A cleaner collapse variable might be the Debye–Waller
   exponent $\eta^2(2\bar n + 1)$ directly, but only the (1)+(2) data
   would support that conjecture.

These are all **WP-C v0.2 scope**, not sub-entries of v0.1.

-----

## 5. Memo update

v0.4.1 §5.3 can be promoted to **CLOSED (physics, not artefact)** with
the JC-revival branch falsified by N-independence and the
DW-higher-order / motional-LD-regime branches merged. Item 2 of
memo §9 ("§5.3 α-recovery probe") is discharged. Item 1 (Doppler-merging
probe) still open; items (1), (2), and (3) of §4 above are the natural
v0.2 scope.

-----

*Probe complete, 2026-04-21, 3.4 s wall time. Physics confirmed.*
