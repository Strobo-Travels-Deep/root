# Logbook — 2026-05-16 — back-action diagnostic scoping pass

**Status.** Decision / milestone entry (not a run entry). WP-W
follow-up Rank 1 (motional back-action diagnostic) scoped. No runner
code written — scope proposed, **pending user lock** before any
implementation, per the session brief ("scoping pass only; do not
implement runners unless I explicitly say go").

**One-line outcome.** The five WORK-PROGRAM §8 open back-action items
are settled with physics/prior-analysis-grounded defaults and written
up as [`notes/back_action_scope.md`](../notes/back_action_scope.md);
review-pass corrections applied; WP-W stays parked at code level.

-----

## 1. What was read

WORK-PROGRAM §Analytical (back-action bullet) + §7#4/#5/#7 + §8 v0.5
outlook; close-out logbook Rank 1; `notes/analytic_chain.md`;
`scripts/stroboscopic/ideal_sdf.py`, `observables.py`, `states.py`,
`hilbert.py`; `numerics/_common.py`; `2026-05-15-D4-bridge.md`.

## 2. Scope decisions settled (proposed lock)

Full rationale in [`notes/back_action_scope.md`](../notes/back_action_scope.md)
§3. Summary:

1. **Readout basis** — compute *all three* (unconditional, σ_x
   branch-select, σ_y/σ_z equator); near-free post-processing of one
   propagation. Headline = unconditional + σ_y/σ_z cat.
2. **Input subset** — minimal three {vacuum, Fock $|2\rangle$, cat
   $|\alpha|=1.5$}; all pure; full §7#4 set is a documented
   no-new-physics extension (thermal is the only one needing
   density-matrix propagation).
3. **Metrics** — primary grid-free state-space (purity drop;
   fidelity to pre-train state; analytic $|\beta_\text{tot}|$);
   parity-form Wigner / negativity-change / ideal-vs-native $L^1$ as
   reported diagnostic, carrying the same "not a gate" caveat as the
   χ bridge metric.
4. **Artefacts** — `run_back_action.py` → `back_action.h5`+manifest;
   `plot_back_action.py` → `back_action.png`; this scope entry + a
   later run entry. Four new `_common` helpers (partial trace,
   conditional ket, parity-form Wigner, cat ket).
5. **Gating** — exploratory diagnostic; the *only* hard PASS/FAIL is
   the vacuum analytic self-consistency anchor (closed-form purity +
   Wigner of the 50/50 displaced-vacuum mixture), the back-action
   analogue of P0/P1.

## 3. Findings worth recording

- **Doc inconsistency (corrected this pass).** WORK-PROGRAM
  §Analytical "Measurement back-action" wrote the unconditional
  mixture and conditional Kraus operator with the *full*
  $\beta_\text{tot}$ (stale pre-v0.5 $D(\sigma_z\beta)$ convention);
  §8's v0.5 sketch already used the v0.5-correct $\beta_\text{tot}/2$.
  The §Analytical bullet is corrected to $\beta_\text{tot}/2$ for
  consistency with `analytic_chain.md` §1 and §8. Recorded here, not
  applied silently.
- **Engine reuse confirmed.** Both legs (`ideal_sdf` train,
  `build_strobo_train`) already return the full spin⊗motion ψ;
  back-action needs only post-processing — no new physics machinery,
  confirming the close-out logbook's Rank 1 value-to-effort claim.
- **Reduced-DM orientation gotcha.** `observables.compute`'s internal
  `rho_m = outer(conj(down),down)+outer(conj(up),up)` is the
  conjugate-transpose of the physical reduced state — fine for its
  only use (transpose-invariant purity), wrong for Wigner/fidelity.
  Flagged so the new `partial_trace_spin` uses the physical
  convention. Not a bug in existing code (its sole consumer is
  purity); a trap for the new consumer.
- **No cat ket builder** in `scripts/stroboscopic/states.py` — build
  in `_common`, verify against `_common.chi_cat`/`W_cat`.
- **β_tot is a per-point probe, not a phase-space scan** — back-action
  samples ~2 representative $|\beta_\text{tot}|$ (peak + mid-branch),
  not the D3/D4 inverse-Dirichlet grid. Runtime is milliseconds-scale,
  no wall-time concern.

## 3a. Review-pass corrections (post user review, same day)

User review caught three blockers in the first scope draft; all
corrected before lock. Math re-derived and confirmed independently:

1. **Vacuum-anchor factor-of-two errors (§6).** Branches at
   $\gamma=\beta_\text{tot}/2$ ⇒
   $|\langle\gamma|{-}\gamma\rangle|^2=e^{-|\beta_\text{tot}|^2}$
   (the draft used $e^{-|\beta_\text{tot}|^2/2}$ for the *squared*
   overlap). Corrected: purity
   $\operatorname{Tr}\rho^2=\tfrac12(1+e^{-|\beta_\text{tot}|^2})$;
   vacuum fidelity $\mathcal F=e^{-|\beta_\text{tot}|^2/4}$
   (the draft's "½(1+…)·single-branch overlap" was vague and wrong).
   Critical because this is the *only* hard gate.
2. **Parity-form Wigner prefactor (§4, §6).** Was $\pi^{-1}$ ⇒
   $W_\text{vac}(0)=1/\pi$, inconsistent with P0/D1
   ($W_\text{vac}(0)=2/\pi$). Corrected to $2/\pi$; displacement
   order pinned by a smoke test vs analytic $W_\text{vac}/W_\text{coh}$.
   **Same stale $\pi^{-1}$ found pre-existing in WORK-PROGRAM §8**
   (provisional-deliverable sketch) — corrected there too, parallel
   to the §Analytical $\beta_\text{tot}/2$ fix.
3. **Native-leg parameterization under-specified.** `build_strobo_train`
   has no $\beta_\text{tot}$ knob, and `analytic_chain.md` §5/§7#3
   forbid a $\beta_\text{eff}$ calibration (structural bridge). Added
   scope §4a: native leg = D4 Layer A pinned WP-E v0.9.1 train at the
   *same* $(\delta-k\omega_m,\varphi_\text{train},N)$ the
   inverse-Dirichlet rule assigns each ideal-leg probe point — a
   **matched-physical-control structural residual**, not matched
   $\beta_\text{tot}$. Makes the ideal-vs-native $L^1$ reproducible.

**Deferred non-blocking (noted, not actioned).** `_common.contrast_from_chi`
docstring still labels itself "ideal-SDF prefactor"; v0.5 demoted it
to a legacy radial-envelope diagnostic. Out of this scope diff; flag
for a later doc-hygiene pass.

## 4. Doc edits applied this pass (doc-only)

1. `notes/back_action_scope.md` — new; the proposed v0.6 scope
   (post-review-corrected: §4 prefactor, §4a native leg, §6 anchors).
2. WORK-PROGRAM §Analytical back-action bullet — $\beta_\text{tot}\!\to\!\beta_\text{tot}/2$
   in the unconditional mixture, branch-select, and Kraus operator
   (v0.5 σ_x-convention consistency).
3. WORK-PROGRAM §8 provisional-deliverable sketch — parity-form
   Wigner prefactor $\pi^{-1}\!\to\!2/\pi$ (P0/D1 consistency).
4. WORK-PROGRAM §8 "Open v0.5 items" → "v0.6 back-action scope"
   forward pointer to this note + a one-line summary of the locked
   decisions, marked *proposed — pending user lock*.

## 5. Next-step decision

**Hold.** Scope is proposed, post-review-corrected, and
self-contained. No runner work until the user reviews the corrected
`notes/back_action_scope.md` and explicitly says go. On "go", the
recommended first execution plan is
[`notes/back_action_scope.md`](../notes/back_action_scope.md) §7
(helpers + vacuum gate → runner → plot → one clean commit). The user
indicated the corrected scope is then ready to commit as a doc-only
v0.6 checkpoint.
