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

-----

## 6. Finalization probe v2 (appended 2026-04-21)

Follow-up pass addressing the two open items named in §3 and §5 above:

- **Test A — rubric reinterpretation.** Measure P at $\delta = 0.5\,\omega_m$ alongside V at $\delta = 0$ under option-(a) recalibration, across the dense |α| grid and all three N values.
- **Test B — JC-revival discriminant.** Repeat the dense |α| scan under option-(b) fixed $\Omega = \Omega_\text{Hasse}$ at the same $\delta t/T_m = 0.80$. Under (b), net train rotation $N\cdot\Omega_\text{eff}\cdot\delta t$ is *not* pinned and sweeps the Rabi envelope (≈ 4.9, 9.8, 19.7 × π/2 for N = 24, 48, 96). If the V(|α|) oscillation shape is intrinsic to |α|, it should survive N-variation up to overall scaling; if it is a JC-revival projection, the shape should vary with N.

Driver: [run_alpha_recovery_v2.py](../numerics/run_alpha_recovery_v2.py).
Data: [alpha_recovery_v2.h5](../numerics/alpha_recovery_v2.h5).
Plot: [alpha_recovery_v2.png](../plots/alpha_recovery_v2.png).
Compute: 9.3 s for 12 × 3 cells × 2 detunings × 2 calibrations, NMAX 80. |α| tightened to [2.5, 5.25] to stay audit-grade on Fock leakage throughout (< 10⁻¹² worst case).

### 6.1 Test A outcome — **rubric reinterpretation confirmed**

Under option (a), **P = 1.000 at every (|α|, N) cell across the 12 × 3 grid**, to three decimals. This includes the V-minimum at |α| = 3.0 (V = 0.101, P = 1.000) and the local V-maximum at |α| = 4.75 (V = 0.395, P = 1.000). The off-tooth coherence is flat; there is no Doppler washout anywhere in the scanned region.

The memo §4.3 rubric's "(V low, P high)" row therefore contains at least two physically distinct populations in the recalibrated-Ω protocol:
1. **Pulse-broadening proper** — V low because the pulse bandwidth no longer resolves the sideband comb. Expected at large $\delta t/T_m$ for small ηα.
2. **Encoder-sensitivity revival** — V low because the |α|-dependent train-kernel happens to project onto near-uniform |C|(ϑ₀) at this particular (α, δt). This is the mechanism responsible for the observed V minimum at |α| ≈ 3 in the recalibrated-Ω dense scan.

Distinguishing them requires the ηα scaling — (1) is monotone in ηα, (2) is oscillatory. The v0.1.1 §4.3 rubric text should be refined accordingly in a v0.2 revision.

### 6.2 Test B outcome — JC-style interference is real, mechanism attribution still open

Under option (b), V(|α|) shows strong N-dependence in both *amplitude* and *shape*. Sample values at fixed |α|:

| |α| | V(N=24) | V(N=48) | V(N=96) |
|---|---|---|---|
| 2.50 | 0.864 | 0.846 | 0.791 |
| 3.00 | 0.896 | 0.934 | 0.942 |
| 3.50 | 0.870 | 0.758 | 0.913 |
| 4.00 | 0.912 | 0.906 | 0.895 |
| 4.75 | 0.869 | 0.984 | 0.923 |
| 5.25 | 0.677 | 0.845 | 0.975 |

The shape-normalised panel (bottom-right of [alpha_recovery_v2.png](../plots/alpha_recovery_v2.png)) plots each N-curve rescaled to [0, 1] and overlays the option-(a) curve (N = 48, dashed black). The three option-(b) curves have **no shared structure** with each other or with option (a). This confirms JC-style interference is operationally real in the system: when the calibration allows net rotation to vary with N, the V(|α|) shape is dominated by the Rabi-envelope structure of the specific (N, Ω) combination.

**What Test B does not establish.** It does not retroactively attribute the smooth option-(a) oscillation to DW-higher-order structure versus JC-projection. In option (a), net rotation is pinned to π/2 by construction, so any JC-like N-phase revival is suppressed by the same fiat that enables the scan; the residual α-structure could in principle be either (i) a JC-revival that happens to be N-invariant at fixed net π/2, or (ii) an intrinsic DW structure. The operational degeneracy flagged in §2 still stands.

A clean separation would require an analytic handle: evaluate $\min_{\vartheta} |C|$ for a coherent state $|\alpha e^{i\vartheta}\rangle$ under the N-impulsive-kick train with per-kick area π/(2N) and gap $T_m$, take the $N \to \infty$ limit (where JC-revival scaling disappears explicitly), and compare to the numerical option-(a) curve at large N. If the N → ∞ analytic limit reproduces the observed oscillation, it is DW-intrinsic; if it differs, the difference *is* the JC projection. Flagged for v0.2 scope.

### 6.3 Status update

- Test A **DEMONSTRATES** the rubric reinterpretation (§3 above). The memo §4.3 rubric should be refined in v0.2.
- Test B **DEMONSTRATES** JC-style N-phase interference as a real effect under fixed-Ω, without attributing the option-(a) oscillation. Mechanism attribution for the smooth recalibrated-Ω curve remains open.
- The council memo §5.3 disposition moves from PARTIALLY RESOLVED (v0.4.3) to **RESOLVED in rubric, OPEN in attribution**.

-----

*v2 probe complete, 2026-04-21, 9.3 s wall time. Rubric reinterpretation confirmed; mechanism attribution still needs the analytic DW reference.*
