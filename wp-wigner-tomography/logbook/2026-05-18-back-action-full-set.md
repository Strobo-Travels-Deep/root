# Logbook — 2026-05-18 — back-action: full §7#4 input set

**Status.** Run entry. Executed the full §7#4 input-set back-action
diagnostic (scope `back_action_scope.md` §8, corrected + locked
2026-05-18). Carrier k=0; new artefact `back_action_full.h5`; the
parked 3-input `back_action.h5` (k=0) and `back_action_k1.h5` are
left untouched. Mixed-input (thermal, mixed-cat) propagation added
to `run_back_action.py` via the weighted-ket-list path; the pure
path is reused **verbatim** (bit-for-bit backward-compatible).

**Headline outcome.**

- **Backward-compat is bit-for-bit.** Re-running the three committed
  inputs through the refactored runner reproduces every metric in
  `back_action.h5` with **max deviation exactly 0.000e+00** (240
  numeric fields/arrays incl. gate, rec attrs, W datasets, cond
  subgroups). The pure pipeline + the hard gate are untouched.
- **Vacuum gate still PASS at machine precision** (the only hard
  PASS/FAIL; unchanged — pure-vacuum, tooth-independent).
- The diagnostic now covers all seven §7#4 states including the two
  **mixed** ones (thermal $\bar n{=}0.5$, mixed-cat) via
  density-matrix propagation; the pure-cat vs mixed-cat structural
  residual is the quantum/classical discriminator carried into the
  back-action observable.

-----

## 1. Pre-registered expectations (before the run)

Per scope §8 (corrected). Logged before declaring:

- **Gate:** unchanged — vacuum/ideal/`|+y>` purity
  $\tfrac12(1{+}e^{-|\beta|^2})$, fidelity $e^{-|\beta|^2/4}$,
  $W{=}W_\text{mixed-cat}(\beta_\text{tot}/2)$ at $\le10^{-6}$.
  Must still PASS (pure, k-independent).
- **Backward-compat:** the 3 parked inputs must reproduce
  `back_action.h5` **bit-for-bit** (pure path byte-retained;
  scope §8, regression clause).
- **thermal $\bar n{=}0.5$:** 13 Fock terms ($n{=}0..12$), discarded
  tail $\le10^{-6}$; pre-purity $1/(2\bar n{+}1)=0.5$.
- **mixed-cat $|\alpha|{=}1.5$:** pre-purity
  $\tfrac12(1{+}e^{-4|\alpha|^2})\approx0.50006$; `branch_fidelity`
  **N/A** (omitted; no single $\psi_\text{pre}$).
- **Physics expectations (reported, not gated):** ideal σ_x-branch
  $F=1.000$ for every *pure* input (tooth-independent branch
  picture). Native carrier back-action: weak/decohering for
  vacuum/thermal (featureless), stronger structural residual for
  the coherence-bearing states (coherent, cat). Mixed-cat should
  show a *smaller* structural residual than the pure cat (no
  fringes to disturb) — the quantum/classical control, now in the
  back-action channel.

## 2. Execution

`run_back_action.py` (v0.6.2): added `motional_input_terms`
(weighted ket list), `thermal_terms` (renormalised, tail reported),
`rho_pre_of_terms`, `mixed_conditional_rho`; 1-term inputs dispatch
to the existing primitives unchanged. `plot_back_action.py`: guarded
the σ_x-branch annotation for `None` (renders "N/A (mixed input)").

| artefact | path |
|---|---|
| runner | [`numerics/run_back_action.py`](../numerics/run_back_action.py) |
| data | [`numerics/back_action_full.h5`](../numerics/back_action_full.h5) + manifest |
| figure | [`plots/back_action_full.png`](../plots/back_action_full.png) |
| scope | [`notes/back_action_scope.md`](../notes/back_action_scope.md) §8 (corrected, locked) |

Inputs: vacuum · coherent$|\alpha|{=}1.5$ · thermal $\bar n{=}0.5$ ·
Fock$|1\rangle$ · Fock$|2\rangle$ · cat$|\alpha|{=}1.5$ ·
mixed-cat$|\alpha|{=}1.5$. k=0, N=30, β₀=0.05, nmax=60. Wall 262 s.

## 3. Results

**Gate:** PASS — peak purityΔ=6.66e-16, fidΔ=3.33e-16, WΔ=1.28e-10;
mid 1.83e-14/1.34e-14/2.36e-12 (identical to the parked k=0 run).

**Backward-compat:** max |refactor − committed| over 240
fields/arrays = **0.000e+00** (bit-for-bit).

**thermal $\bar n{=}0.5$:** 13 terms, discarded tail
**6.27e-07** (≤1e-6 ✓); pre-purity 0.5000006.
**mixed-cat:** pre-purity **0.5000617** = $\tfrac12(1{+}e^{-4\cdot2.25})$ ✓;
`branch_fidelity` absent (mixed) ✓.

Peak, native leg vs ideal (σ_x-branch F: ideal = 1.0000 for all
pure; N/A for mixed):

| input | pre-purity | native purity | native $F_\text{pre}$ | native σ_x-F | ideal–native $L^1$ |
|---|---|---|---|---|---|
| vacuum            | 1.000 | 0.934 | 0.923 | 0.346 | 0.813 |
| coherent $|1.5\rangle$ | 1.000 | 0.939 | 0.153 | 0.033 | 1.632 |
| thermal $\bar n{=}0.5$ | 0.500 | 0.483 | 0.480 | N/A   | 0.492 |
| Fock $|1\rangle$  | 1.000 | 0.815 | 0.792 | 0.046 | 1.448 |
| Fock $|2\rangle$  | 1.000 | 0.722 | 0.691 | 0.043 | 1.813 |
| cat $|1.5\rangle$ | 1.000 | 0.609 | 0.142 | 0.175 | 1.872 |
| mixed-cat $|1.5\rangle$ | 0.500 | 0.467 | 0.138 | N/A | 1.472 |

(vacuum / Fock$|2\rangle$ / cat rows are bit-identical to the parked
`back_action.h5`.)

## 4. Interpretation

1. **The extension is sound and free.** Bit-for-bit reproduction of
   the parked states proves the weighted-ket layer changes nothing
   on the validated path; the gate is untouched. No new physics —
   exactly as scope §3 decision 2 / §8 anticipated.
2. **Quantum/classical discriminator carries into back-action.**
   The pure cat's structural residual ($L^1=1.87$) markedly exceeds
   the mixed cat's ($1.47$): the native engine disturbs the *coherent*
   cat (its fringes) far more than the incoherent two-hump mixture —
   the same discriminator D3 saw in reconstruction, now in the
   measurement-cost channel. Coherent$|1.5\rangle$ ($L^1=1.63$,
   $F_\text{pre}=0.15$) behaves like the cat: coherence-bearing
   states pay the largest structural cost.
3. **Mixed states are robust / featureless.** thermal $\bar n{=}0.5$
   has the smallest residual ($L^1=0.49$) and tiniest purity drop
   (0.017): a broad incoherent Gaussian has little structure for the
   native engine to mis-handle. Its absolute purity (~0.48) barely
   moves from the input's own 0.50.
4. **Branch picture intact for every pure input** (ideal σ_x-F =
   1.0000) and correctly **N/A for the two mixed inputs** — no
   silent zero; the conventional honesty of scope §8 C.

## 5. Next-step decision

Full §7#4 back-action set delivered (k=0). No open blockers. Re-park.

**>>> NEXT SESSION — designated pick-up (user decision 2026-05-18).**
Run the **k=1 sideband** at the full §7#4 input set (thermal +
mixed-cat included), the JC-regime counterpart of this carrier run.
It is a *trivial re-run on the existing v0.6.2 runner* — no code
change expected (the tooth-aware `--k-sideband` and the weighted-ket
mixed-input path are both already in place and validated here).

Exact command (writes its own artefact family; **parked
`back_action.h5` / `back_action_k1.h5` / `back_action_full.h5` must
stay untouched** — use the explicit `--output`):

```
python wp-wigner-tomography/numerics/run_back_action.py --k-sideband 1 \
  --inputs vacuum coherent1.5 thermal0.5 fock1 fock2 cat1.5 mixed_cat1.5 \
  --output wp-wigner-tomography/numerics/back_action_k1_full.h5
python wp-wigner-tomography/plots/plot_back_action.py \
  --h5 wp-wigner-tomography/numerics/back_action_k1_full.h5
```

Pre-registered expectations for that session: vacuum hard gate must
still PASS at machine precision (tooth-independent); the five pure
inputs reproduce the k=1 single-point witness trends from
`2026-05-17-back-action-k1-sideband.md` (coherent strong native
mismatch at the sideband); thermal/mixed-cat are *new* k=1 data —
expect the quantum/classical L¹ ordering of §4 to persist but with
the JC-type native back-action of the sideband. New logbook
`2026-05-18-…-k1-full-set.md` *[filename aligned post-hoc: this
designation predicted `2026-05-19-…`, but the pick-up executed
same-day; see [`../notes/wpw_findings.md`](../notes/wpw_findings.md)
provenance]*, pre-reg → run → comparison, one clean commit; do
**not** regenerate parked artefacts.

Other decision-gated items unchanged: Rank 2 squeezed-vacuum still
needs the $\mathcal O(\eta^2)$ analytic extension first (separate,
foundational); GKP is a separate future WP.

## 6. Post-run review corrections (user audit, same day)

A user audit of the execution commits (`298dbcc` + `be90a21`) found
one **presentation** defect; fixed in `d297112` (plot-only, no data).

- **Figure annotated the absolute purity drop for mixed inputs.**
  `plot_back_action.py` printed `drop = 1−purity` on every post
  panel. For the two *mixed* inputs this is the drop from a *pure*
  reference, not from the input's own (mixed) pre-purity: thermal
  showed `0.517`, mixed-cat `0.533`, when the scientifically
  relevant drops are **0.017** and **0.033**. The HDF5 / manifest /
  this logbook's §3 table already carried the correct
  `purity_drop_vs_pre`; **only the figure text was wrong**.
- **Fix (`d297112`).** Annotate `r.get("purity_drop_vs_pre",
  r["purity_drop"])`, label `drop/pre`, with a legacy fallback for
  pre-v0.6.2 all-pure h5 (where `drop ≡ drop/pre`). Pure rows
  numerically unchanged (vacuum 0.066, coherent 0.061, fock1 0.185,
  fock2 0.278, cat 0.391); mixed rows corrected
  (thermal 0.517→0.017, mixed-cat 0.533→0.033). Regenerated
  `back_action_full.png` only; parked `back_action.png` /
  `back_action_k1.png` left untouched (all-pure ⇒ never numerically
  wrong; not regenerated for a label-wording change, to preserve
  provenance stability).
- **Scope:** figure presentation only — no data, conventions, gate,
  or backward-compat claim affected; all §3 numbers stand.
