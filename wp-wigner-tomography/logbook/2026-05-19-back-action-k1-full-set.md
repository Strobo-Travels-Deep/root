# Logbook — 2026-05-19 — back-action: k=1 sideband, full §7#4 input set

**Status.** Run entry. Designated next-session pick-up (user decision
2026-05-18, recorded in [`2026-05-18-back-action-full-set.md`](./2026-05-18-back-action-full-set.md)
§5). Runs the **k=1 first sideband** at the **full §7#4 input set**
(thermal + mixed-cat included) — the JC-regime counterpart of the
2026-05-18 carrier (k=0) full-set run. Expected to be a *trivial
re-run on the existing v0.6.2 runner*: both the tooth-aware
`--k-sideband` (validated 2026-05-17) and the weighted-ket
mixed-input path (validated 2026-05-18) are already in place. New
artefact family `back_action_k1_full.{h5,manifest.json}` +
`back_action_k1_full.png`; the three parked artefacts
(`back_action.h5` k=0 3-input, `back_action_k1.h5` k=1 3-input+coh2,
`back_action_full.h5` k=0 7-input) stay **untouched** via explicit
`--output`.

-----

## 1. Pre-registered expectations (before the run)

Logged before declaring, per scope §8 and the 2026-05-18 §5 pick-up
brief.

- **No code change.** v0.6.2 runner is unchanged; both required
  features (tooth-aware comb-tooth selection, weighted-ket mixed
  inputs) were validated in the two prior runs. Pure single-term path
  reused verbatim.

- **Vacuum hard gate must still PASS at machine precision.** The
  ideal leg is tooth-independent after the inverse-Dirichlet
  subtraction of `k·omega_m`; the gate machinery is pure-vacuum and
  tooth-independent. Expect the **identical** residuals seen at both
  k=0 (2026-05-18 §3) and k=1 single-point (2026-05-17 §3):
  peak `|β_tot|=1.50` → purityΔ `6.66e-16`, fidΔ `3.33e-16`, WΔ
  `1.28e-10`; mid `|β_tot|=0.75` → `1.83e-14 / 1.34e-14 / 2.36e-12`.
  This is the only hard PASS/FAIL.

- **Bit-for-bit reproduction of the 3 inputs shared with the parked
  k=1 single-point** (`back_action_k1.h5`): vacuum, Fock $|2\rangle$,
  cat $|\alpha|{=}1.5$. Same tooth (k=1), same matched-control policy,
  same v0.6.2 path, per-input propagation is independent of the input
  list ⇒ expect **max |this − back_action_k1.h5| = 0.000e+00** on
  every shared field/array (the k=1 analogue of the 2026-05-18
  backward-compat clause). If not exactly 0, ≤1e-12 (harmless
  trace/dot reassociation) would still pass, but bit-for-bit is the
  pre-registered expectation since the pure path is byte-retained.

- **ideal σ_x-branch F = 1.0000 for all five pure inputs**
  (vacuum, coherent$|1.5\rangle$, Fock$|1\rangle$, Fock$|2\rangle$,
  cat$|1.5\rangle$): the branch picture is an ideal-SDF property,
  tooth-independent. **N/A** (attr omitted) for the two mixed inputs
  (thermal, mixed-cat) — no single $\psi_\text{pre}$; scope §8 C.

- **Input preparation is tooth-independent** ⇒ identical to k=0
  full set (2026-05-18 §3): thermal $\bar n{=}0.5$ = 13 terms
  ($n{=}0..12$), discarded tail **6.27e-07** (≤1e-6 ✓), pre-purity
  **0.5000006**; mixed-cat pre-purity **0.5000617** =
  $\tfrac12(1{+}e^{-4\cdot2.25})$; `branch_fidelity` absent for both
  mixed inputs.

- **New-at-k=1 inputs** (coherent$|1.5\rangle$, thermal$\bar n{=}0.5$,
  Fock$|1\rangle$, mixed-cat$|1.5\rangle$ — coherent here is
  $|\alpha|{=}1.5$, *not* the 2026-05-17 $|\alpha|{=}2$): the
  **quantum/classical $L^1$ ordering of 2026-05-18 §4 must persist**
  — pure cat structural residual > mixed cat; coherence-bearing
  states (coherent, cat) pay the largest structural cost; thermal the
  smallest residual and tiniest purity drop — but with the **JC-type
  native back-action of the sideband** (k=1 native leg differs from
  the k=0 native leg, so absolute numbers shift; the *ordering* is
  the pre-registered invariant, not the values).

- **k=1 does not retroactively change the k=0 carrier conclusion.**
  Consistent with 2026-05-17 §4, the inputs shared with the k=0 full
  set are expected to shift only modestly (~`1e-3`–`1e-2` at peak)
  between teeth; the carrier full-set interpretation stands.

- **Artefacts.** New `back_action_k1_full.h5` + `wp_manifest_v1` +
  `back_action_k1_full.png` (plotter derives the PNG stem from the h5
  stem → no parked PNG clobbered). One clean commit; **no parked
  artefact regenerated.**

## 2. Execution

Exact pick-up commands (from repo root), runner v0.6.2 unchanged:

```bash
python wp-wigner-tomography/numerics/run_back_action.py --k-sideband 1 \
  --inputs vacuum coherent1.5 thermal0.5 fock1 fock2 cat1.5 mixed_cat1.5 \
  --output wp-wigner-tomography/numerics/back_action_k1_full.h5
python wp-wigner-tomography/plots/plot_back_action.py \
  --h5 wp-wigner-tomography/numerics/back_action_k1_full.h5
python -m pytest \
  wp-wigner-tomography/numerics/test_back_action_helpers.py \
  scripts/stroboscopic/tests/test_ideal_sdf.py -q
```

| artefact | path |
|---|---|
| runner | [`numerics/run_back_action.py`](../numerics/run_back_action.py) (v0.6.2, unchanged) |
| data | [`numerics/back_action_k1_full.h5`](../numerics/back_action_k1_full.h5) + manifest |
| figure | [`plots/back_action_k1_full.png`](../plots/back_action_k1_full.png) |
| scope | [`notes/back_action_scope.md`](../notes/back_action_scope.md) §8 (locked, executed k=0) |

Inputs: vacuum · coherent$|\alpha|{=}1.5$ · thermal $\bar n{=}0.5$ ·
Fock$|1\rangle$ · Fock$|2\rangle$ · cat$|\alpha|{=}1.5$ ·
mixed-cat$|\alpha|{=}1.5$. **k=1**, N=30, β₀=0.05, nmax=60.

Wall 268.3 s (cf. k=0 full 262 s). Tests **36 passed**
(`test_back_action_helpers.py` + `test_ideal_sdf.py`). Code version
`0.6.2` (unchanged); `k_sideband=1`.

## 3. Results

**Gate:** PASS — peak `|β_tot|=1.50` purityΔ **6.66e-16**, fidΔ
**3.33e-16**, WΔ **1.28e-10** (W_im 3.5e-17); mid `|β_tot|=0.75`
**1.83e-14 / 1.34e-14 / 2.36e-12**. **Bit-identical to both the k=0
full set (2026-05-18 §3) and the k=1 single-point (2026-05-17 §3)** —
the ideal leg + gate machinery are tooth-independent, exactly as
pre-registered.

**Input preparation:** thermal $\bar n{=}0.5$ = **13 terms**,
discarded tail **6.272254744e-07** (≤1e-6 ✓); pre-purity
**0.5000006272**; mixed-cat pre-purity **0.5000617049**. All seven
pre-purities are **bit-identical** to the k=0 full set
(Δ = 0.000e+00) — input prep is tooth-independent (pre-reg ✓).

Peak probe, native leg (drop **relative to the input's own
pre-purity**); ideal σ_x-branch F = **1.0000** for all five pure
inputs, **N/A** (attr omitted) for the two mixed:

| input | pre-purity | native purity | native drop/pre | native $F_\text{pre}$ | native σ_x-F | ideal–native $L^1$ |
|---|---|---|---|---|---|---|
| vacuum                  | 1.0000 | 0.9440 | 0.0560 | 0.9326 | 0.3023 | 0.8103 |
| coherent $|1.5\rangle$  | 1.0000 | 0.9482 | 0.0518 | 0.1582 | 0.1106 | 1.6254 |
| thermal $\bar n{=}0.5$  | 0.5000 | 0.4893 | 0.0107 | 0.4843 | N/A    | 0.4895 |
| Fock $|1\rangle$        | 1.0000 | 0.8201 | 0.1799 | 0.8058 | 0.0722 | 1.4435 |
| Fock $|2\rangle$        | 1.0000 | 0.7234 | 0.2766 | 0.7092 | 0.0530 | 1.8075 |
| cat $|1.5\rangle$       | 1.0000 | 0.6077 | 0.3923 | 0.1465 | 0.1937 | 1.8656 |
| mixed-cat $|1.5\rangle$ | 0.5001 | 0.4720 | 0.0281 | 0.1384 | N/A    | 1.4723 |

(Mid-probe rows in `back_action_k1_full.h5`; `back_action_k1_full.png`
shows the seven-row peak panel grid.)

## 4. Comparison vs k=0 full set and k=1 single-point

**Backward-compat (k=1), bit-for-bit.** The three inputs shared with
the parked k=1 single-point (`back_action_k1.h5`: vacuum, Fock
$|2\rangle$, cat $|1.5\rangle$) reproduce it with **max
|k1_full − back_action_k1.h5| = 0.000e+00** over **225**
committed-schema fields/arrays (gate, rec attrs, W, cond subgroups,
W_pre). The only excluded attrs are the v0.6.2-only `pre_purity` /
`purity_drop_vs_pre`, legitimately absent from the pre-v0.6.2 parked
file (the legacy-fallback note, 2026-05-18 §6); the legacy identity
(pure ⇒ pre_purity = 1, `purity_drop` ≡ `purity_drop_vs_pre`) was
verified to hold in `back_action_k1_full.h5` for every shared rec.
This is the k=1 analogue of the 2026-05-18 backward-compat clause.

**Tooth-independence of input prep.** All seven pre-purities are
bit-identical to `back_action_full.h5` (k=0); thermal 13-term / tail
6.27e-07 identical. Independent of comb tooth, as expected.

**k=1 vs k=0 full set (peak, native leg):** every unconditional
metric shifts only at the `1e-3`–`1e-2` level — the carrier
conclusion is **not** retroactively changed:

| input | Δ drop/pre | Δ $F_\text{pre}$ | Δ σ_x-F | Δ $L^1$ |
|---|---|---|---|---|
| vacuum                  | −0.0104 | +0.0097 | −0.0440 | −0.0031 |
| coherent $|1.5\rangle$  | −0.0094 | +0.0052 | **+0.0781** | −0.0063 |
| thermal $\bar n{=}0.5$  | −0.0060 | +0.0042 | N/A     | −0.0020 |
| Fock $|1\rangle$        | −0.0048 | +0.0143 | +0.0266 | −0.0049 |
| Fock $|2\rangle$        | −0.0011 | +0.0178 | +0.0102 | −0.0053 |
| cat $|1.5\rangle$       | +0.0014 | +0.0044 | +0.0192 | −0.0065 |
| mixed-cat $|1.5\rangle$ | −0.0053 | +0.0001 | N/A     | +0.0003 |

The single largest sideband signature is the **coherent input's
σ_x-branch fidelity** (+0.078, k1−k0) — the conditional channel, not
the unconditional metrics, carries the JC-regime mismatch. This is
the seven-input confirmation of the 2026-05-17 single-point finding
("coherent is the useful sideband anchor"; there at $|\alpha|{=}2$,
here at $|\alpha|{=}1.5$).

**Quantum/classical $L^1$ ordering persists at k=1.** Pure cat
($L^1=1.866$) > mixed cat ($1.472$); coherence-bearing states
(coherent 1.625, cat 1.866) pay the largest structural cost; thermal
the smallest residual (0.490) and tiniest purity drop (drop/pre
0.0107). The 2026-05-18 §4 ordering is reproduced — the
quantum/classical discriminator is **tooth-robust**, carrying into
the sideband/JC back-action channel.

## 5. Interpretation & next-step decision

1. **Trivial re-run, as predicted.** No code change; v0.6.2 runner
   ran the sideband at the full set verbatim. The hard gate is
   tooth-safe at machine precision; the pure path is bit-for-bit vs
   the parked k=1 single-point; mixed-input preparation is
   tooth-independent. Every §1 pre-registered expectation held.
2. **The quantum/classical discriminator is tooth-robust.** The pure
   cat's structural residual exceeds the mixed cat's at k=1 just as
   at k=0 (1.87 vs 1.47); coherence-bearing states pay the largest
   structural cost; mixed/thermal stay featureless. D3's
   quantum/classical control survives the carrier→sideband change of
   native dynamics.
3. **The sideband signature lives in the conditional channel.** All
   unconditional metrics for the carrier-shared inputs move ≤1e-2
   between teeth; the one materially larger k1−k0 shift is the
   *coherent* σ_x-branch fidelity (+0.078). The seven-input run
   confirms the 2026-05-17 single-point conclusion: a coherent input
   is the cleanest sideband witness, and the mismatch is in the
   branch-conditioned readout, not the headline purity/fidelity. k=1
   does **not** retroactively change the k=0 carrier interpretation.
4. **Branch picture intact for every pure input at the sideband**
   (ideal σ_x-F = 1.000000000000) and correctly **N/A** for the two
   mixed inputs — scope §8 C honesty preserved at k=1.

**Next-step decision.** This closes the designated 2026-05-18 §5
pick-up (k=1 sideband, full §7#4 set). No open blockers. Re-park —
new artefact family `back_action_k1_full.{h5,manifest.json,png}`;
parked `back_action.h5`, `back_action_k1.h5`, `back_action_full.h5`
and their PNGs left untouched.

Decision-gated items unchanged: Rank 2 squeezed-vacuum still needs
the $\mathcal O(\eta^2)$ analytic extension first (separate,
foundational); GKP is a separate future WP. *Optional* (not required
to close anything) follow-up, echoing 2026-05-17 §5: a small
coherent-input sideband map varying one of $(N,\ \delta\text{-offset},\ 
\text{coherent phase})$ with state-space fidelity as the primary
observable — only if a deeper sideband characterisation is wanted.
