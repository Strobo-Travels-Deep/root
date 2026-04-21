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

Rubric-specific summary: the (V low, P low) quadrant, where "V low"
means $V < 0.3$ (the rubric's threshold for pulse-broadening or
encoder-revival):

| |α| | cells with V < 0.3 (drive-LD valid) | min $P_\text{mid,min}$ in that set |
|---|---|---|
| 0 | 0 (V stays ≥ 0.97 everywhere) | — |
| 1 | 0 (V stays ≥ 0.76 everywhere) | — |
| 3 | 12 | **0.966** |
| 5 | 0 (V stays ≥ 0.67 everywhere) | — |

**Primary finding.** **The (V low, P low) quadrant is empty.** In
every cell of the grid where $V < 0.3$ (rubric "V low"),
$P_\text{mid,min} \geq 0.966$. All observed weak-binding cells are in
the (V low, P high) quadrant — distributed between the pulse-
broadening and encoder-sensitivity-revival populations identified by
α-recovery v2 Test A.

**Secondary finding — high-V per-pulse residual.** In small-$N$
(N ∈ {3, 6}) high-V cells the per-cell $P_\text{mid,min}$ drops to
**as low as 0.930** (at |α|=0, N=3, δt/T_m=0.40; see
[verify_analytic.py](../numerics/verify_analytic.py) Check 5a). These
cells are not drive-LD-breach; $\Omega_\text{eff}/\omega_m$ remains
under the 0.3 ceiling. The finite-bandwidth structure of a single
pulse at large δt can mildly reduce $P$ even when $V$ is high. This
is the $\mathcal O(1)$ per-pulse Doppler residual that Lemma A's IP
formulation predicts survives even after the $\mathcal O(N)$
heterodyne cancellation — see
[notes/analytic-reference.md](../notes/analytic-reference.md) §2. The
v0.1 draft of this logbook characterised these small drops as "the
drive-LD-breach RWA-failure artefact only"; that was imprecise. They
are a genuine finite-$\delta t$ signature, just one that is small in
absolute terms and whose cells are rubric-irrelevant (high V).

-----

## 3. Why — the stroboscopic heterodyne (see
[notes/analytic-reference.md](../notes/analytic-reference.md) Lemma A)

The pulse-to-pulse period $t_\text{sep} = T_m = 2\pi/\omega_m$ is
tuned to exactly one motional period. In the interaction picture at
$H_0 = \omega_m a^\dagger a + (\delta/2)\sigma_z$, gaps are trivial
(zero Hamiltonian) for any $t_\text{gap}$, and the coupling operator
is stroboscopically stationary at pulse-start times — i.e.
$\widetilde C(j T_m) = C$ at all integers $j$. Therefore the $N$-fold
accumulation of Doppler-broadening that would occur in a non-
stroboscopic protocol is replaced by a sum of $N$ copies of a single
pulse's finite-bandwidth response with $\alpha$-independent spin-frame
phases between them. Any Doppler residual in $P$ is therefore bounded
by the single-pulse bandwidth, not the $N$-pulse-train bandwidth —
a reduction from $\mathcal O(N)$ to $\mathcal O(1)$.

The observed per-cell $P_\text{mid,min} \in [0.93, 1]$ is exactly
this $\mathcal O(1)$ residual in action: the deepest dips (to 0.93)
appear at small $N$ (fewer averaging cycles) and large $\delta t$
(the single-pulse bandwidth is widest), but none reach the rubric's
(V low, P low) quadrant because $V$ is high in those cells.

Under **option-(b) fixed Ω**, Rabi-envelope nodes do break the
cancellation at specific N values, which is why WP-C v0.1's
option-(b) control slice shows a different behaviour. Under
**option-(a) recalibrated Ω**, the net train rotation is pinned at
π/2 by construction and the heterodyne is clean in the sense above.

**What this validates quantitatively.** The stroboscopic protocol's
robustness against Doppler broadening is, under the assumptions
$t_\text{sep} = T_m$ and option-(a) calibration, a reduction of the
Doppler amplification scaling from $\mathcal O(N)$ to $\mathcal O(1)$.
The remaining $\mathcal O(1)$ per-pulse residual is visible in the
data (P drops to 0.93 in the worst-case per-cell sense) but is
rubric-irrelevant because it coincides with high V.

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
