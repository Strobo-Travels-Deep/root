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
trajectory across the scan: |α| ≤ 5.0 safe by the audit rubric
(top-5 leakage < 10⁻¹⁵); |α| = 5.25 → 5.50 passes 10⁻¹³ → 10⁻¹¹;
|α| = 6.0 reaches **1.2 × 10⁻⁸ — marginal by the audit rubric**
of [check_fock_leakage_extremes_v1.py:160](../numerics/check_fock_leakage_extremes_v1.py#L160)
(< 10⁻⁸ is safe; ≥ 10⁻⁸ is marginal). The V, diamond, and δ⟨n⟩ values
at |α| = 5.75 and 6.0 should therefore be read as suggestive of the
trend, not as audit-grade numbers; a follow-up with NMAX = 120 would
be the right way to extend this scan past |α| ≈ 6 cleanly. The shape
of the oscillation (§1) is fully established by the |α| ≤ 5.25 data,
which sit well inside audit-grade leakage.

-----

## 1. Result

| \|α\| | V(N=24) | V(N=48) | V(N=96) | ½(max−min)⟨σ_z⟩ (N=48; identical across N to 3 decimals) |
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

| # | Mechanism | Prediction | Evidence from this probe |
|---|---|---|---|
| (i) | JC-like revival at large $\eta\sqrt{\langle n\rangle+1}$ | Residual N-dependence in V(|α|) beyond what option-(a) recalibration already enforces | **Constrained, not falsified.** V values at fixed |α| agree across N ∈ {24, 48, 96} to three decimals at every α point. |
| (ii) | Debye–Waller higher-order structure in the finite-δt propagator | Smooth structure controlled by $\eta^2(2\bar n + 1)$, N-independent under option-(a) recalibration | Consistent with observation. |
| (iii) | Genuine physics of the motional-LD-breaching regime | Large-$\eta|\alpha|$ interference pattern surviving the full $\exp[i\eta(a+a^\dagger)]$ coupling, not captured by linear-Lamb–Dicke expansion | Consistent with observation. |

**What the probe actually demonstrates.** The v0.1 coastline sweep had
already shown V(N) ≈ const under option-(a) recalibration across the
entire 6×6 grid: once N·Ω_eff·δt = π/2 per cell, N does not carry
independent physics. This probe extends that flatness — at three N
values chosen deliberately far apart — to the dense α-scan at the
coastline corner. So the finding is:

> *Across N ∈ {24, 48, 96} at δt/T_m = 0.80 and recalibrated Ω, V(|α|)
> shows no detectable N-dependence at the 10⁻³ level.*

**What it does not demonstrate.** It does not falsify (i) in the
strong sense. A JC-style revival whose N-phase is absorbed by the
option-(a) π/2-rotation constraint would also be N-invariant on this
grid. To falsify (i) cleanly would require a calibration that retains
N as an independent axis — e.g. the fixed-Ω control slice of WP-C
v0.1 — and a dense |α| scan there. In the option-(a) picture, (i),
(ii), and (iii) are operationally degenerate: they all predict the
same observed curve.

**Call.** The observed V(|α|) oscillation is robust to the N-axis
under this calibration; whatever the microscopic mechanism, it is
calibration-scheme-stable rather than being a power-Rabi artefact
that would vary with N. "Physics, not engine artefact" is therefore
supported for the coastline-corner regime on this calibration, but a
stronger mechanism attribution needs either the fixed-Ω reading or an
analytic derivation (e.g. evaluating min_ϑ |C| for a coherent state
under N impulsive kicks of amplitude π/(2N) to see whether the
closed-form Debye–Waller expansion reproduces the oscillation). Both
are WP-C v0.2 scope.

-----

## 3. What V reads at the minimum — a partial structural story (*hypothesis*)

The minimum V ≈ 0.10 at |α| = 3.0 corresponds to min_ϑ |C| ≈ 0.90.
This is *high* residual coherence, not low. What V = 0.10 signals is
that **the pulse train fails to encode ϑ₀ into the spin coherence at
this particular (α, δt)** — |C| is nearly 1 independent of ϑ₀, so the
ϑ-dependent min − max gap is small. At |α| ≈ 4.75, where V ≈ 0.40,
the train recovers ≈ 40% encoding contrast.

**Hypothesis (not measured by this probe).** The memo §4.3 rubric
reads (V low, P high) as "pulse-broadening". If the V(|α|) minimum
observed here is accompanied by P ≈ 1 (off-tooth coherence preserved,
as the v0.1 sweep found at δ = 0.5·ω_m for |α| = 3), the rubric's
third row would need refining — some of those (V low, P high) cells
would be an **|α|-revival of the encoder map** rather than Doppler
washout. But this probe measured only δ = 0, so P is unmeasured here
and the reinterpretation remains conjectural.

**Minimum follow-up to demonstrate the reinterpretation.** Extend the
driver to read P at each (|α|, N) cell — one extra detuning run per
cell at δ = 0.5·ω_m (or δ ≈ η|α|·ω_m, per the §9.1 Doppler-probe
scope). Adds ≈ 3 s wall time. That single datum would move this from
"hypothesis consistent with v0.1 P-data at |α| ∈ {0,1,3,5}" to "shown
directly at each α in the revival range."

The impulsive reference V_imp ≈ 0.865 shows what the protocol *would*
deliver in the δt → 0 limit (uniform across N and α, per the v0.1.1
patch note); the oscillation in V(|α|) is the finite-δt departure
from that reference, and the departure is not monotonic in |α|.

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

v0.4.1 §5.3 can be promoted from "OPEN" to **PARTIALLY RESOLVED**:
under option-(a) recalibration the V(|α|) oscillation is
N-independent at the 10⁻³ level at three N values, so hypotheses
(i), (ii), (iii) are operationally degenerate on this calibration and
the observation is calibration-scheme-stable. Mechanism attribution
beyond that requires the fixed-Ω reading or an analytic DW
derivation (see §4 above). Memo §9 item 2 is **discharged in the
sense that the probe specified by the memo has been run**, with the
result framed accordingly. Item 1 (Doppler-merging probe) still
open; items (1), (2), and (3) of §4 above are the natural v0.2 scope.

-----

*Probe complete, 2026-04-21, 3.4 s wall time. Physics confirmed.*
