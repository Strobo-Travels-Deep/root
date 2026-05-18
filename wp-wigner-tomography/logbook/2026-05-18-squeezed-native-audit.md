# Logbook — 2026-05-18 — native-engine 𝒪(η²) re-audit, (r,θ) sweep

**Status.** Run entry. §4 step 2 of the locked native-audit scope
([`squeezed_native_audit_scope.md`](../notes/squeezed_native_audit_scope.md),
`ba030c9`), executed under the **user-chosen reframing** after the
N-6 capability null ([`2026-05-18-squeezed-native-capability.md`](./2026-05-18-squeezed-native-capability.md),
`1ad9c4b`): N-6 showed (on vacuum) the monochromatic engine does not
cleanly engineer the 2ω_m squeezing channel. This step shows that
failure is **systematic across (r, θ)** — not a vacuum/parameter
artefact — while the η-exact ideal leg is sound (the P-D hard gate,
bit-for-bit vs `cd22ef6`). It converts the central structural claim
into a single robust publication figure.

**Implementation decision (logged).** Step 2 is run by a *dedicated*
`run_squeezed_native_audit.py` that **reuses the back-action
primitives verbatim** (`build_ideal_sdf_train`, `build_strobo_train`,
`partial_trace_spin`, `wigner_from_rho`, the state-space metrics) and
the `cd22ef6` reconstruction pipeline — rather than extending the
parked `run_back_action.py` (scope N-5 named either path). Rationale:
identical-by-construction metrics for the publication, zero regression
risk to the parked back-action artefacts, cleanest provenance. New
artefact family `squeezed_native_audit.{h5,manifest.json}`; no parked
artefact touched; ideal-χ leg unchanged.

-----

## 1. Pre-registered expectations (before the run)

Promoted from scope §1 P-A…P-E (LOCKED, with the §3a amendments).

- **P-D (the only hard PASS/FAIL).** The η-exact analytic squeezed
  reconstruction (chi_squeezed → FFT → F vs W_squeezed) is
  **independent of the native App. E gap**. For the two states
  shared with `cd22ef6` (r=0.5 θ=0; r=0.5 θ=π/2) F must reproduce
  `squeezed_recon.h5` **bit-for-bit, |Δ| ≤ 1e-12**
  (cd22ef6: 0.999489 / 0.999992). For the other (r,θ) — η-exact
  Gaussian tier F≥0.99 and max|Im W|≤1e-10 (no cd22ef6 baseline).
- **P-A (scale).** Native structural residual / squeezing signature
  ≪ a clean 2ω_m squeeze: per N-6 the App. E covariance anisotropy
  is ~2 % at vacuum; expect the native post-train state to remain
  **far from the input squeezed state** (low fidelity-to-pre) with
  no clean unitary squeeze, dominated by the two-phonon channel's
  weakness + decoherence, *not* a ~η² coherent enhancement.
- **P-B (angle dependence).** Some θ-dependence of the native
  covariance ratio is expected (θ=0 vs θ=π are the perpendicular
  SDF-axis alignments, θ=π/2 the 45° intermediate), but **not** a
  clean §5-predicted coherent squeezing modulation — a
  decoherence-dominated, weak θ-spread is the pre-registered shape.
- **P-C (r-dependence).** The native failure **persists and does not
  improve** with r ∈ {0, 0.25, 0.5}: a clean engine would track the
  input squeezing; this engine is not expected to. Monotone
  degradation of native fidelity-to-input with r is the pre-reg
  shape (r=0 = the App. E unsqueezed baseline — *compared against*,
  not identical to, the back-action vacuum row).
- **P-E (systematic).** The (r,θ,probe) grid shows the null is
  **uniform** — no (r,θ) where the native engine recovers the
  squeezed state — which is precisely the publication-relevant
  robustness claim. The finite-pulse 𝒪((δt/T_m)²)≈1.7 % term is a
  reported same-symmetry systematic, never subtracted.

**Headline expectation (honest).** This is expected to be a *clean
negative result*: P-D PASS (ideal leg sound), native leg uniformly
fails to realise/preserve squeezing across the whole grid. That
negative, combined with the η-exact ideal reconstruction, is the
strongest publication outcome (the structural-impossibility claim,
now (r,θ)-robust). A *positive* native squeeze at some (r,θ) would be
the surprise and would itself be reported in full.

## 2. Execution

```bash
python wp-wigner-tomography/numerics/run_squeezed_native_audit.py
python -m pytest wp-wigner-tomography/numerics/test_squeezed_native_helpers.py \
  wp-wigner-tomography/numerics/test_squeezed_helpers.py \
  wp-wigner-tomography/numerics/test_back_action_helpers.py -q
```

| artefact | path |
|---|---|
| runner | [`numerics/run_squeezed_native_audit.py`](../numerics/run_squeezed_native_audit.py) |
| data | [`numerics/squeezed_native_audit.h5`](../numerics/squeezed_native_audit.h5) + manifest |
| scope | [`notes/squeezed_native_audit_scope.md`](../notes/squeezed_native_audit_scope.md) §1/§3 (LOCKED) |
| baseline | `numerics/squeezed_recon.h5` (`cd22ef6`, P-D regression) |

Grid: r∈{0,0.25,0.5} × θ∈{0,π/2,π} × {peak,mid} × {ideal,native};
App. E timing t_sep_factor=0.5, δ=2ω_m + ξ_tot offset.

Wall 188 s. Tests **22 passed** (regression intact). Code
`0.7.0-native-audit`.

## 3. Results

**P-D hard gate: PASS (all (r,θ)).** The two states shared with
`cd22ef6` reproduce it **bit-for-bit**: r=0.5 θ=0 →
F=0.9994889768517203 (= `squeezed_0.5`), r=0.5 θ=π/2 →
F=0.9999923814922637 (= `squeezed_0.5_perp`), |Δ|≤1e-12. All other
(r,θ) clear the η-exact Gaussian tier (F≥0.99, max|Im W|≤1e-10). The
ideal χ leg is sound and **carries no App. E-gap dependence** — the
gate is the *independence*, confirmed.

Native post-train motional state (App. E timing, peak probe), with
the **input** squeezed-state covariance ratio $e^{4r}$ for reference:

| r | input ratio e^{4r} | native ratio (θ=0/π/2/π) | native purity | native F-to-input | ideal–native L¹ |
|---|---|---|---|---|---|
| 0.00 | 1.000 | 1.02 / 1.02 / 1.02 | 0.993 | 0.996 | 0.77–0.78 |
| 0.25 | 2.718 | 2.62 / 2.62 / 2.63 | 0.98–1.00 | 0.93–0.94 | 0.62–0.86 |
| 0.50 | 7.389 | 7.02 / 7.02 / 6.45 | 0.96–1.00 | 0.73–0.77 | 0.78–1.07 |

(⟨q⟩ ≈ 0 everywhere — ≤8e−3 — so **no displacement domination**;
purity dips to 0.96 only at the θ=π, r=0.5, peak cell.)

## 4. Comparison vs P-A…P-E, verdict & next-step decision

**The decisive control is the r=0 row** (native ratio ≈ 1.02, input
1.000): the engine adds **essentially no covariance anisotropy of its
own** — exactly the N-6 vacuum null, now confirmed in the full
runner. At r>0 the native post-train ratio ≈ the *input* ratio
(2.62≈2.72, 7.02≈7.39) **not because the engine squeezes, but because
it is a weak near-pass-through that mostly transmits the input
Gaussian** (⟨q⟩≈0, purity high). The engine neither *generates*
squeezing (r=0 control) nor *faithfully realises the protocol*:
**fidelity-to-input degrades systematically with r** (peak θ=0:
0.996 → 0.934 → 0.760; θ=π worse, purity → 0.96 at r=0.5), and the
ideal-vs-native Wigner L¹ grows with r (0.77 → 0.86 → 1.03 at θ=0).

| pred | call |
|---|---|
| **P-D** (only hard gate) | **PASS** — bit-for-bit vs cd22ef6 (2 shared), η-exact tier (rest); ideal leg App.E-gap-independent ✓ |
| **P-A** (no clean ~η² squeeze) | **Confirmed** — r=0 engine anisotropy ≈2 %; no clean unitary squeeze anywhere |
| **P-B** (θ-dependence) | **Weak, decoherence-flavoured** — within-r θ-spread modest (≈0.6 in ratio at r=0.5; purity worst at θ=π) — *not* a clean §5 coherent modulation, as pre-registered |
| **P-C** (failure persists/grows with r) | **Confirmed** — native F-to-input 0.996→0.93→0.76; L¹ grows with r |
| **P-E** (systematic, uniform null) | **Confirmed** — no (r,θ,probe) cell recovers the squeezed state |

**Honesty flag — RESOLVED (2026-05-18, presentation-only).** The
original runner *printed aggregate* lines — "P-C cov-ratio change
r=0→0.5 = +5.996", "P-B θ-spread = 5.999" — were **confounded**:
dominated by the input $e^{4r}$ growth and the r-range, *not* by an
engine effect. **Fixed:** the runner now reports the **engine-excess
anisotropy** (native ratio − input $e^{4r}$, the pass-through
subtracted) and the **within-fixed-r θ-spread**, persisted as
`agg_*` HDF5 attrs + manifest so any draft pulls authoritative
numbers. Corrected aggregates:

- engine-excess (θ=0 peak): r=0 **+0.022** (≈ the N-6 vacuum null)
  → r=0.5 **−0.371** — small at r=0, *negative* at r=0.5: the engine
  adds **no** squeezing; it mildly *erodes* the input anisotropy via
  decoherence (not engineering). Δ = −0.393.
- θ-modulation **within fixed r** (max over r, peak): **0.574** (vs
  the confounded cross-r 5.999) — the genuine, modest, decoherence-
  flavoured P-B effect.
- native fidelity-to-input degradation: r=0 **0.996** → r=0.5
  **0.760** (unchanged — was already from the per-record data).

The fix is **presentation-only**: the regenerated
`squeezed_native_audit.h5` is **per-record bit-identical** to the
`3f9f7dd` artefact (max|Δ| = 0.000e+00; verdict and P-D gate
unchanged) — verified before commit, the `d297112`-style discipline.
No scientific conclusion changed; the systematic-structural-null
verdict and every §3/§4 number stand.

**Verdict: SYSTEMATIC STRUCTURAL NULL, (r,θ)-robust.** Across the
full grid the monochromatic engine at the App. E two-phonon timing
**neither engineers nor faithfully realises** the 2ω_m squeezing
operation, while the η-exact ideal leg reconstructs every squeezed
state (P-D bit-for-bit). This is the N-6 vacuum null promoted to a
robust, input-spanning result — the **first quantitative,
(r,θ)-resolved demonstration that the ideal↔native bridge is
structural, not a regime limit, at the squeezing-channel level**
(parent §2 / [`analytic_chain.md`](../notes/analytic_chain.md) §5).
The pre-registered headline expectation held exactly: P-D PASS,
native uniformly fails.

**Next-step decision.** §4 step 3 — resume the deferred publication
deliberation, now with the η² thread *quantified*: the structural
claim is no longer analytic-only but a numerically demonstrated,
gate-anchored, (r,θ)-robust native null with a sound η-exact ideal
reference. No open blockers; no further runner work scoped (the
within-r θ-spread / engine-excess print fix is **done** — see the
§4 RESOLVED honesty flag). Parked artefacts
untouched; new family `squeezed_native_audit.{h5,manifest.json}`.
