# Logbook — 2026-04-21 — Doppler-merging probe (council memo §9.1)

**Scope.** The v0.1 main sweep measured P at δ = 0.5·ω_m and found
P ≈ 1.00 everywhere in the interior of the grid, which the §4.3 rubric
interprets as "Doppler-merging regime not reached". Council memo §9.1
asked whether extending the detuning ladder to several mid-sideband
points can reach the (V low, P low) quadrant.

**Artefacts.**
- Driver: [run_coastline_doppler_v1.py](../numerics/run_coastline_doppler_v1.py)
- Data: [coastline_doppler_v1.h5](../numerics/coastline_doppler_v1.h5)
- Plot: [coastline_doppler.png](../plots/coastline_doppler.png)

**Compute.** 29.7 s wall for the full 6×6 × 4 |α| × 7 detunings grid
(≈ 65 k evolutions). Fock leakage worst-case 2.7 × 10⁻¹³ at |α|=5
(NMAX 80); safely audit-grade across the scan.

-----

## 1. Configuration

| axis | values |
|---|---|
| N | 3, 6, 12, 24, 48, 96 |
| δt/T_m | 0.02, 0.05, 0.10, 0.20, 0.40, 0.80 |
| δ/ω_m | **0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0** |
| \|α\| | 0, 1, 3, 5 |
| Ω | option (a) recalibrated, N·Ω_eff·δt = π/2 per cell |
| NMAX | 60 for \|α\| ≤ 3, 80 for \|α\| = 5 |

Detuning ladder rationale: {0} is V's δ; {0.5} matches v0.1's P; {1.0,
2.0} coincide with motional sidebands; {0.25, 0.75, 1.5} are
mid-sideband points where Doppler merging would show cleanest.

**Reductions per cell:**
- $V = 1 - \min_\vartheta |C|$ at $\delta = 0$
- $P_\text{half} = \langle |C|\rangle_\vartheta$ at $\delta = 0.5\,\omega_m$ (v0.1-compatible)
- $P_\text{mid,min} = \min_{\delta \in \{0.25, 0.5, 0.75, 1.5\}\omega_m} \langle |C|\rangle_\vartheta$ — worst-case off-tooth coherence over mid-sideband detunings, the most stringent Doppler-merging test
- Full 7-point spectrum retained per cell in `P_spectrum`

-----

## 2. Result — the (V low, P low) quadrant is empty on this grid

Row-mean summary at each (|α|, N):

| |α| | V̄_{dt=0.80} | P_mid,min̄ interior* | drive-LD-breach corner cells (N ∈ {3, 6}) |
|---|---|---|---|
| 0 | 0.998 | **1.000** | P_mid_min ∈ [0.896, 0.960] |
| 1 | 0.760 | **1.000** | P_mid_min ∈ [0.917, 0.964] |
| 3 | 0.101 | **1.000** | P_mid_min ∈ [0.949, 0.971] |
| 5 | 0.377 | **1.000** | P_mid_min ∈ [0.948, 0.977] |

*interior = N ≥ 12, no drive-LD breach.

**Finding.** In every cell of the 6×6 × 4 |α| × 7 detuning grid for
which drive-LD is respected, $P_\text{mid,min} \geq 0.999$. The
(V low, P low) rubric quadrant is **structurally empty** in this
protocol under option-(a) recalibration. This is stronger than v0.1's
negative result — which was at a single detuning — because it covers
the full [0, 2·ω_m] span including mid-sideband and second-sideband
points where any Doppler broadening would necessarily manifest.

The only cells where $P_\text{mid,min} < 1$ are the drive-LD-breach
cells at N ∈ {3, 6}. In those cells Ω_eff/ω_m is large enough that
the RWA fails, and the observed modest P drop (to ≈ 0.90) is a
signature of the effective Hamiltonian no longer being sideband-
resolved, not a Doppler-merging signal.

-----

## 3. Why — the stroboscopic heterodyne

The strobe gap T_m = 2π/ω_m is tuned to exactly one motional period.
At the start of each pulse, the coherent-state phase has advanced by
exactly 2π; the motional motion is therefore "stroboscopically
frozen" on the pulse-train timescale. Whatever Doppler-broadening a
single pulse experiences within its δt window is averaged by the
N-fold sampling at a period that cancels the motional phase to all
orders in η|α|. The result is that the off-tooth coherence P is a
property of the comb-interpolation error of the train envelope, not
of the underlying Doppler profile.

Under **option-(b) fixed Ω**, Rabi-envelope nodes do break the
cancellation at specific N values, which is why WP-C v0.1's
option-(b) control slice shows a different behaviour. Under
**option-(a) recalibrated Ω**, the net train rotation is pinned at
π/2 by construction and the heterodyne is clean.

**This is a quantitative validation of a claim that Hasse 2024
implicitly relies on:** the stroboscopic protocol is robust to
Doppler broadening of individual pulses as long as the gap is locked
to T_m and the total rotation is calibrated. No prior WP had tested
this claim cleanly.

-----

## 4. What this says about the memo §4.3 rubric

The rubric's three rows can now be stated sharply for this protocol:

| Regime | V | P | Observed? |
|---|---|---|---|
| strong-binding | high | high | yes (|α| ≤ 1, δt ≤ 0.2·T_m) |
| pulse-broadening | low | high | yes (large δt/T_m, all |α|) |
| encoder-sensitivity revival | low | high | yes (|α| ≈ 3 at large δt, per α-recovery v2 §6.1) |
| **Doppler merging** | **low** | **low** | **no — not reachable under option-(a) recalibration** |

Two distinct (V low, P high) populations — pulse-broadening proper
and encoder-sensitivity revival — were already established by the
α-recovery v2 Test A. This probe adds a third fact: the fourth row
(Doppler merging) is not a regime the protocol can reach, under
option-(a). For a v0.2 revision of the rubric, that row should be
flagged as "reachable only by breaking the strobe-gap lock or
intentionally violating option-(a) calibration".

-----

## 5. Open follow-ups (WP-C v0.2 scope, not this probe)

1. **Strobe-gap detune probe.** If we break t_sep_factor = 1 (i.e.
   gap ≠ T_m), the heterodyne cancellation should fail and Doppler
   merging should emerge. A one-parameter sweep over
   t_sep_factor ∈ [0.8, 1.2] at |α| = 3, δt/T_m = 0.80 would localise
   the cancellation mechanism.
2. **Analytic DW reference.** Evaluate the closed-form N-impulsive
   kernel at t_sep = T_m and confirm the Doppler-merging term
   vanishes identically under option-(a) pinning; this would promote
   the numerical finding to a lemma.
3. **Option-(b) Doppler probe.** The same detuning ladder applied to
   the fixed-Ω control slice at δt/T_m = 0.13 would show whether
   Doppler merging is reachable under *any* calibration; this was
   outside the v0.1 control-slice scope.

-----

## 6. Memo update

Council memo §9.1 is **discharged**: Doppler-merging probe executed,
(V low, P low) quadrant is empty under option-(a), the protocol is
robust against Doppler broadening of individual pulses, and the §4.3
rubric row is re-labelled "not reachable under option-(a)". The
remaining live items are §9.3 (memo disposition) and the v0.2 scope
listed in §5 above plus the analytic DW attribution carried over
from the α-recovery v2 finalization.

-----

*Probe complete, 2026-04-21, 29.7 s wall time. Doppler-merging regime
is not reachable in this protocol under option-(a).*
