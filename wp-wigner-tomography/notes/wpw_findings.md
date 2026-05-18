# WP-W — Overall findings (program synthesis)

**WP-W · findings synthesis · 2026-05-18**

**Status.** Standalone, citable synthesis of the *entire* WP-W
program. This is the reader's **first stop**: every load-bearing
conclusion with its gate number, commit, and dated logbook. It
supersedes [`logbook/2026-05-16-wpw-closeout-and-followups.md`](../logbook/2026-05-16-wpw-closeout-and-followups.md)
as the entry point (that close-out predates the back-action
diagnostic family, the 𝒪(η²)/δt lock, and the Rank 2 squeezed-vacuum
delivery). It introduces no new results — for derivations see
[`analytic_chain.md`](./analytic_chain.md) (the convention-locked
chain), [`back_action_scope.md`](./back_action_scope.md), and
[`squeezed_eta2_scope.md`](./squeezed_eta2_scope.md); for execution
detail see the dated logbooks cited inline.

**One-paragraph outcome.** WP-W delivers a convention-locked
characteristic-function tomography chain (ideal FH20-style σ_x SDF →
direct χ readout → Dirichlet β-map → FFT Wigner inversion), validated
end-to-end against analytic truth and the native stroboscopic engine;
a quantitative ideal-vs-native **structural back-action diagnostic**
exercised across the full §7#4 input set on both the carrier (k=0)
and first sideband (k=1) teeth; and the **Rank 2** squeezed-vacuum
extension — the 𝒪(η²)/δt analytic pass (locked) and an ideal-leg
squeezed-vacuum reconstruction that passes the Gaussian-tier gate.
Every hard gate ever set has passed; the one substantive caveat
(D4 Layer B FFT centroid) was correctly re-attributed to grid
resolution, not engine error. The only open work is the deliberately
deferred native-engine 𝒪(η²) re-audit and the separate-WP GKP probe.

-----

## 1. The validated tomography chain (P0/P1/D1–D5)

The protocol and its anchors, in execution order. Commit hashes are
the one-clean-commit-per-session record (close-out §1).

| stage | what it establishes | load-bearing number | commit / logbook |
|---|---|---|---|
| **P0** | analytic χ → FFT → Wigner self-consistency | vacuum $W(0)=0.636555$ vs $2/\pi=0.636620$ (Δ=−6.5e−5, finite-grid windowing); coherent peak on the closest grid node to 1 part in 10⁴; $\max|\mathrm{Im}\,W|\sim$1.5e−16 | `4e34ef8` · [D2-and-P0](../logbook/2026-05-15-D2-and-P0.md) |
| **D2** | inverse-Dirichlet reach ladder | `n_in_disk` = {317, 1257, 2821, 5025} for N={20,40,60,80}; **5025 exactly matches** the independent WORK-PROGRAM §2 value | `4e34ef8` · same |
| **D3** | reconstruction on the 7 §7#4 states | all 6 gated states clear §7#5; deciding states Fock\|2⟩ F=0.9997, cat F=0.9664 pass; $\bar F_\text{geom}=0.9013$; mixed-cat control shows **no invented fringes** | `1b63cd0` · [D3](../logbook/2026-05-15-D3-reconstruction.md) |
| **ideal_sdf + P1** | FH20-style σ_x SDF primitive vs analytic χ, single sentinel | 28 smoke tests ≤1e−9; P1 $\beta_\star=0.5e^{i\pi/4}$, vacuum+coherent, N∈{20,80} → rel. residual **~1e−14** (5 % gate cleared by 13 orders) | `9d5360a` · [ideal-sdf](../logbook/2026-05-15-ideal-sdf-primitive.md) |
| **D4 Layer A** | native engine vs WP-E `scan_2d_alpha3_v2.h5` | max\|Δ\| on (σ_z, Re C, Im C) at 3 grid points = **0.00e+00** (bit-exact) under the WP-E v0.9.1 convention | `71027b6` · [D4](../logbook/2026-05-15-D4-bridge.md) |
| **D4 Layer B** | engine-measured χ vs analytic χ over the 81² grid at \|α=3⟩ | max\|χ_eng−χ_an\| = **3.75e−04** over 6481 nodes (canonical bridge metric) | `71027b6` · same |
| **v0.5 doc pass + D1** | 5 execution-surfaced conventions corrected; standalone derivation | doc-only; [`analytic_chain.md`](./analytic_chain.md) tied to the four anchors above | `fe8f8b0` (doc) / `64a2e10` (D1) |

**P0** validates the FFT/Wigner convention (the
$\Delta\alpha=\pi/(N_g\Delta\beta)$ Nyquist relation — *not* the
textbook $2\pi/\ldots$ — from the $2i$ kernel). **P1** validates the
σ_x-SDF + direct-χ readout at a point. **D4 Layer A** validates the
native-engine provenance (bit-exact to the WP-E reference). **D4
Layer B** is the load-bearing bridge number — the ideal-SDF primitive
reproducing the analytic forward map at sub-1e−3 over the *full*
reconstruction grid.

**The D4 Layer B caveat (correctly resolved).** The FFT centroid
$\hat\alpha^W=2.980$ ($|\Delta|=1.99\text{e}{-}2$) missed a pre-set
$10^{-2}$ gate by 2×, but that gate was tighter than the grid
resolution ($\Delta\alpha=0.388$; the residual is ~5 % of one pixel).
The correct bridge metric is the 3.75e−4 χ residual, which passes by
≥5 orders. The centroid is reported *only* with its Δα pixel size
attached, never as a bare gate — a discipline carried into every
later Wigner-side number.

## 2. Conventions that proved load-bearing

Five conventions were surfaced *by execution* and corrected (the v0.5
doc pass `fe8f8b0`); they are now locked in
[`analytic_chain.md`](./analytic_chain.md) and recur as the reason
later work is correct:

1. **σ_x SDF, not σ_z.** A σ_z-conditioned displacement commutes with
   the σ_z detuning precession and never builds the Dirichlet kernel:
   σ_z gave a **165 %** P1 residual, σ_x gave 1e−14. The ideal layer
   *is* exactly FH20's protocol; the native deviation is a clean
   σ_z(Hasse)/σ_x(FH20) operator mismatch.
2. **No $e^{-|\beta|^2/2}$ prefactor.** The σ_x-SDF/\|+y⟩ chain reads
   χ *directly*: $\chi=\langle\sigma_y\rangle-i\langle\sigma_z\rangle$.
   The old prefactor was a WP-E Doppler-contrast artefact.
3. **$\Delta\alpha=\pi/(N_g\Delta\beta)$** (the $2i$-kernel Nyquist
   relation) — validated bit-on by the P0 coherent peak landing
   exactly on the predicted node.
4. **Cat off-diagonal is $\cosh(2\,\mathrm{Re}(\alpha^*\beta))$**, not
   $\cosh(2\alpha^*\beta)$ — the BCH phase cancels the imaginary part;
   getting it wrong gave $\max|\mathrm{Im}\,W|\sim0.22$ on the cat
   (a real D3 bug, caught by the Im-W sentinel, fixed).
5. **Parity-form Wigner prefactor $2/\pi$**, not $\pi^{-1}$ — anchors
   $W_\text{vac}(0)=2/\pi$ consistent with P0 (the back-action
   scoping correction).

The recurring quality mechanism: **$\max|\mathrm{Im}\,W|$ as a
convention sentinel** (machine floor for correct χ; ~0.2 for a
Hermiticity bug) caught real bugs in D3 and guards every later run.

## 3. Back-action diagnostic family (Rank 1)

The "cost of measurement" — the post-train motional state, a third
bridge residual orthogonal to the χ readout. Scope locked doc-only
first (`cb850a5`; the discipline reused everywhere since), then four
executed runs:

| run | inputs · tooth | key result | logbook |
|---|---|---|---|
| **k=0 minimal** | vacuum/Fock\|2⟩/cat · k=0 | vacuum analytic gate PASS at machine precision (the only hard gate); ideal-vs-native structural $L^1$ established | [2026-05-16-run](../logbook/2026-05-16-back-action-run.md) (`1b90f92`) |
| **k=1 single-point** | +coherent $\|\alpha\|{=}2$ · k=1 | gate tooth-safe (ideal leg tooth-independent); coherent is the cleanest sideband witness | [2026-05-17](../logbook/2026-05-17-back-action-k1-sideband.md) (`339690b`) |
| **k=0 full §7#4** | all 7 (incl. mixed-cat control) · k=0 | 3 parked inputs reproduce `back_action.h5` **bit-for-bit (0.0e0 / 240 fields)**; quantum/classical discriminator carries into back-action: pure cat $L^1$=1.87 > mixed cat 1.47; thermal most robust 0.49 | [2026-05-18](../logbook/2026-05-18-back-action-full-set.md) |
| **k=1 full §7#4** | all 7 · k=1 | bit-for-bit vs parked k=1 (0.0e0 / 225 fields); **L¹ ordering tooth-robust**; sideband signature concentrated in the *coherent σ_x-branch fidelity* (+0.078 k1−k0), unconditional metrics ≤1e−2 | [2026-05-18-k1-full](../logbook/2026-05-18-back-action-k1-full-set.md) (`f0cec92`) |

**Findings.** (i) The **vacuum analytic anchor** (purity
$\tfrac12(1{+}e^{-|\beta|^2})$, fidelity $e^{-|\beta|^2/4}$,
$W=W_\text{mixed-cat}(\beta_\text{tot}/2)$) is PASS at machine
precision and is *tooth-independent* (ideal leg invariant after the
inverse-Dirichlet $k\omega_m$ subtraction). (ii) The
**quantum/classical discriminator** (pure cat's structural residual
> mixed cat's) survives carrier→sideband — it is a robust feature of
the protocol, not a tooth artefact. (iii) The native sideband
signature lives in the *conditional* (branch-selected) channel, not
the headline purity/fidelity, so k=1 does not retroactively change
the k=0 conclusion. (iv) Mixed-input propagation reuses the validated
pure path verbatim (weighted-ket layer) — **bit-for-bit** backward
compatibility proven twice.

## 4. Rank 2 — squeezed vacuum (𝒪(η²)/δt analytic pass + ideal reconstruction)

The natural FH20/Hasse extension, gated on a foundational analytic
pass. Delivered as scope-lock → helpers → ideal reconstruction.

**4.1 The 𝒪(η²)/δt scope, LOCKED** ([`squeezed_eta2_scope.md`](./squeezed_eta2_scope.md);
proposed `3b3db78`, locked `2d74ba1`). Key derived results:

- **The ideal-SDF chain is η-EXACT for squeezed vacuum.** $D(\sigma_x\beta/2)$
  is an exact displacement; the §2 χ readout and §4 FFT carry no η
  expansion. This sharpens (and partly corrects) the WP §7#4 wording
  "not captured by the first-order chain": the 𝒪(η²) gate is the
  *protocol timing* and the *native surrogate*, not the readout.
- **[Hasse24] App. E timing re-derived** as the §3 Dirichlet map at
  the 2ω_m two-phonon fundamental:
  $\xi_\text{tot}=\xi_0e^{i\varphi}\mathcal D_N(\tilde x)$, same
  kernel, doubled fundamental, $\xi_0=\mathcal O(\eta^2)$.
- **Pulse-duration [TBD] closed.** The leading $\mathcal O(\delta t/T_m)$
  effect *is* the documented bit-exact `shift_deg`$=\omega_m\delta t/2$
  (a pure displacement phase, already absorbed in D4 Layer A); the
  residual is $\mathcal O((\delta t/T_m)^2)\approx1.7\%$, two-phonon,
  sub-dominant to $\eta^2\approx16\%$. Resolves the long-open D1 §6
  point 4 / WP §Analytical bullet 5.
- A review-pass **sign correction** to the boxed squeezed-vacuum χ
  (committed cross term was −, correct is +; verified numerically to
  machine precision three independent ways) — recorded explicitly per
  the "record, don't silently fix" convention; conclusions unaffected
  (depend only on the $e^{+r}$ magnitude).

**4.2 Ideal squeezed-vacuum reconstruction — gate PASS**
([2026-05-18-squeezed](../logbook/2026-05-18-squeezed-vacuum-reconstruction.md);
helpers `5474fce`, run `cd22ef6`). Reuses the D3 ideal path verbatim
(confirming the η-exactness claim empirically):

| state | r, θ | F (\|α\|≤3) | max\|Im W\| | gate F≥0.99 |
|---|---|---|---|---|
| `squeezed_0.5` (headline) | 0.5, 0 | **0.999489** | 1.6e−16 | **PASS** |
| `squeezed_0.5_perp` (control) | 0.5, π/2 | **0.999992** | 2.1e−16 | **PASS** |

Cleared the §7#5 Gaussian/coherent tier by ~1.5 orders (θ=0) / to
unity (θ=π/2); the θ=π/2 control is a clean positive check on the
anisotropy handling. **Confirms the scope §3 locked claim** "no grid
escalation required at r~0.5 (unlike GKP)" on the unmodified v0.2
grid. Helpers verified to machine precision (8 smoke locks incl. an
axis-orientation guard against a sign regression).

## 5. Provenance anchors (the load-bearing numbers, one place)

| gate | metric | result |
|---|---|---|
| P0 | vacuum $W(0)$ vs $2/\pi$ | 0.636555 vs 0.636620 (Δ=−6.5e−5) |
| P1 | engine χ vs analytic, sentinel | ~1e−14 |
| D3 | deciding states Fock\|2⟩ / cat | F = 0.9997 / 0.9664 (both PASS) |
| D4 Layer A | native vs WP-E, 3 pts × 3 obs | **0.00e+00** (bit-exact) |
| D4 Layer B | engine χ vs analytic, 6481 nodes | **3.75e−04** |
| back-action | vacuum analytic anchor (k=0 & k=1) | machine precision; tooth-independent |
| back-action | quantum/classical $L^1$ (pure vs mixed cat) | 1.87 > 1.47 (tooth-robust) |
| back-action | refactor backward-compat | 0.0e0 / 240 (k0) & 225 (k1) fields |
| Rank 2 | squeezed-vacuum reconstruction F | 0.999489 (θ=0) / 0.999992 (θ=π/2) |

D4 Layer B is the load-bearing bridge number; its FFT centroid is
always quoted with the Δα pixel size attached.

## 6. Cross-cutting structural conclusion

**For the monochromatic stroboscopic engine specifically**, the
ideal↔native bridge is *structural*, not a regime limit: no limit of
the monochromatic Raman engine recovers the bichromatic FH20 σ_x SDF
([`analytic_chain.md`](./analytic_chain.md) §5) — the first-order
term is single-phonon (displacement), the 𝒪(η²) $X^2\sigma_\varphi$
term is two-phonon (squeezing-type, ≈16 % at η=0.397). This is
**engine-specific, not a universal tomography limitation**: [FH20]'s
*bichromatic* SDF natively realises the ideal chain — WP-W's
contribution is the *quantitative characterisation* of the
monochromatic departure, subordinate to [FH20]/[Hasse24] (see
[`publication_assessment.md`](./publication_assessment.md)).
Consequently every
ideal-vs-native comparison is run as a **matched physical control**
(same drive program, no $\beta_\text{eff}$ calibration —
`back_action_scope.md` §4a), and the residual *is* the diagnostic.
WP-W's contribution over [Hasse24] App. D (qualitative
$\delta\langle n\rangle$) is the *quantitative* Wigner-resolved
ideal-vs-native difference, and the *quantum/classical discriminator*
in the measurement-cost channel.

## 7. Open / deferred (no execution blockers)

- **Native-engine 𝒪(η²) squeezing re-audit** (`squeezed_eta2_scope.md`
  §9 step 3): the structural ideal↔native residual for squeezed
  inputs on the §4 $\xi_\text{tot}$ comb. Deliberately deferred (the
  scope-breadth decision); the scope §5 pins its mechanism, sign, and
  ≈16 % scale so the follow-up is bounded and pre-registerable. Its
  own scope/lock when reopened.
- **GKP-lattice probe** — a *grid-resolution* deferral ([FH20] Fig. 4
  already demonstrated it at η=0.05): needs Δα ÷10 → Δβ ÷10 → N ×10
  and a re-audited perturbativity at larger \|α\|. Separate future WP,
  not a WP-W extension.
- **D3 polish (non-gating, noted at D3):** (i) widen B to fully
  contain the cat off-diagonal (the "modest margin" §2 wording is
  optimistic — at \|α\|=1.5 the off-diagonal is ~0.3 of peak at the
  B=4 edge, the source of the cat's 0.034 F deficit); (ii) a
  symmetric $|\rho_\text{neg}-1|\le0.5$ criterion (the one-sided
  ≥0.5 test only catches under-estimation; the cat over-shoots +27 %).
  Neither blocks anything.

## 8. Commit map

```
4e34ef8  D2 reach ladder + P0 gate
1b63cd0  D3 reconstruction demo (7 states)
9d5360a  ideal_sdf primitive + P1 sentinel
71027b6  D4 bridge (Layer A bit-exact, Layer B 3.75e-4)
fe8f8b0  v0.5 doc-correction pass (doc-only)
64a2e10  D1 standalone analytic note
cb850a5  back-action scope (doc-only checkpoint)
1b90f92  back-action k=0 minimal execution
339690b  back-action k=1 single-point sideband
298dbcc/be90a21/d297112/a33bbc0  back-action k=0 full §7#4 (scope→run→fix→logbook)
f0cec92  back-action k=1 full §7#4   ·  c1f7d3b  WP chronology index
3b3db78  𝒪(η²)/δt scope (PROPOSED)   ·  2d74ba1  LOCK (+§3 sign fix, D1 §6 rewrite)
5474fce  squeezed χ/W helpers + locks
cd22ef6  ideal squeezed-vacuum reconstruction (gate PASS)
```

-----

*Source of truth for conventions:
[`analytic_chain.md`](./analytic_chain.md). Scopes:
[`back_action_scope.md`](./back_action_scope.md),
[`squeezed_eta2_scope.md`](./squeezed_eta2_scope.md). Execution
detail: the dated logbooks cited inline. This synthesis introduces no
new results; where a number appears here it is quoted from the
primary logbook and is reproducible from the committed artefact.*
