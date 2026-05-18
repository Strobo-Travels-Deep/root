# Logbook — 2026-05-19 — squeezed-vacuum reconstruction (Rank 2, §9 step 2)

**Status.** Run entry. The Rank 2 payload: ideal squeezed-vacuum
reconstruction, executing
[`squeezed_eta2_scope.md`](../notes/squeezed_eta2_scope.md) §9 step 2
under the locked §8 decisions (scope LOCKED 2026-05-19, commit
`2d74ba1`; helpers + smoke locks `5474fce`). Per D-2 the **ideal-SDF
χ chain is η-exact for squeezed vacuum**, so this reuses
`run_reconstruction_demo.py`'s analytic/ideal path verbatim with the
locked closed-form χ of §3 — **no engine code, no native leg**. The
native-engine 𝒪(η²) re-audit (§9 step 3) stays deferred.

New artefact family `squeezed_recon.{h5,manifest.json}` via explicit
`--output`; the parked D3 `reconstruction_demo.h5` and all other
parked artefacts are left **untouched** (provenance discipline, as in
the back-action runs). `DEFAULT_STATES` is kept frozen at the
original seven D3 states; the squeezed gate is added without changing
the bare-D3-demo behaviour.

-----

## 1. Pre-registered expectations (before the run)

Logged before declaring, per the §8 locks and the WP-W run
discipline.

- **Test states (D-1).** `squeezed_0.5` (r=0.5, θ=0, squeezed in X —
  headline) and `squeezed_0.5_perp` (r=0.5, θ=π/2, the
  anisotropy-orientation control). Both pure Gaussian.
- **Pipeline (D-2).** Identical D3 ideal path: analytic χ on the v0.2
  Cartesian grid (81² over [−B,B]², B=N|β₀|=80·0.05=4, Δβ=0.10),
  no taper, zero-pad to 161², 2-D FFT inversion; F = π∫W_recW_true
  over |α|≤3. χ is the locked §3 closed form
  (`_common.chi_squeezed`, machine-precision verified `5474fce`).
- **Hard gate (D-5).** One PASS/FAIL: reconstruction fidelity at the
  **§7#5 Gaussian/coherent tier F ≥ 0.99** (squeezed vacuum is a
  *pure* Gaussian, the coherent-state analogue — `coherent_1.5`
  carries F_min=0.99; not the thermal mixed tier). Plus the §4
  convention sentinel **max|Im W| ≤ 1e-10** (machine floor expected,
  Gaussian χ is real). Everything η²/native/pulse-duration is
  *reported, not gated* (scope D-5; deferred anyway here).
- **Quantitative expectation (reported, not the gate).** Exact χ +
  exact pipeline ⇒ F is grid-truncation-limited only. The θ=0
  squeezed χ is broad along β_y (support ∝ e^{+r}, §3): along β_y it
  decays as exp[−½β_y²e^{−2r}] with e^{−2r}=e^{−1}≈0.368, i.e. ≈e
  wider in variance than vacuum, so **more χ-tail truncation at the
  B=4 window than vacuum** (vacuum F=0.999). Expect F high but
  **below vacuum's 0.999**; pre-registered to still clear the 0.99
  Gaussian tier (consistent with scope §3's locked "no grid
  escalation required at r~0.5"). θ=π/2 (χ broad along β_x instead)
  expected to reconstruct **at least as well** as θ=0 on the
  symmetric grid. No Wigner negativity (pure Gaussian) ⇒ ρ_neg N/A.
- **Decision-relevant pre-commitment.** If F **fails** 0.99, the
  threshold is **not** silently relaxed: a sub-0.99 result would
  directly challenge the scope §3 locked claim "no grid escalation
  required at r~0.5" and would be reported as a substantive finding
  requiring a follow-up scope note (grid escalation or a
  squeezed-specific tier), not a quiet pass. Pre-registering this
  keeps the gate honest.

## 2. Execution

Runner `run_reconstruction_demo.py` (D3, code v0.4.0) unchanged
except an **additive** `PASS_THRESHOLDS` update for the two squeezed
names, applied *after* `DEFAULT_STATES` is frozen (bare D3 demo
behaviour and the parked `reconstruction_demo.h5` provenance
unaffected).

```bash
python wp-wigner-tomography/numerics/run_reconstruction_demo.py \
  --states squeezed_0.5 squeezed_0.5_perp \
  --output wp-wigner-tomography/numerics/squeezed_recon.h5
python -m pytest \
  wp-wigner-tomography/numerics/test_squeezed_helpers.py \
  wp-wigner-tomography/numerics/test_back_action_helpers.py -q
```

| artefact | path |
|---|---|
| runner | [`numerics/run_reconstruction_demo.py`](../numerics/run_reconstruction_demo.py) (D3, +squeezed gate) |
| helpers | [`numerics/_common.py`](../numerics/_common.py) `chi_squeezed`/`W_squeezed` (`5474fce`) |
| data | [`numerics/squeezed_recon.h5`](../numerics/squeezed_recon.h5) + manifest |
| scope | [`notes/squeezed_eta2_scope.md`](../notes/squeezed_eta2_scope.md) §8 (LOCKED) |

Wall 0.03 s (analytic/ideal path; no engine). Tests **16 passed**
(`test_squeezed_helpers.py` 8 + `test_back_action_helpers.py` 8
regression — unaffected). Runner code v0.4.0.

## 3. Results

**Hard gate (D-5): PASS for both states.**

| state | r, θ | F (|α|≤3) | L¹ | max\|Im W\| | gate F≥0.99 |
|---|---|---|---|---|---|
| `squeezed_0.5` (headline) | 0.5, 0 | **0.999489** | 0.0417 | 1.6e-16 | **PASS** |
| `squeezed_0.5_perp` (ctrl) | 0.5, π/2 | **0.999992** | 0.0052 | 2.1e-16 | **PASS** |

- Fidelity clears the §7#5 Gaussian/coherent tier (0.99) by ~1.5
  orders for θ=0 and is at unity for θ=π/2.
- max|Im W| at the `complex128` floor (≤2.1e-16 ≪ 1e-10) — the §4
  convention sentinel passes; Gaussian χ is real, no convention
  error.
- ρ_neg N/A (pure Gaussian, no Wigner negativity) — as
  pre-registered.

*Aggregate-line caveat (honesty).* The D3 runner's vestigial
`deciding_pass`/`F_geomean` aggregate keys refer to the D3 deciding
set (`fock_2`,`cat_1.5`), which were **not** run here; `deciding_pass`
is a vacuous `all([])=True` for a squeezed-only run and is **not**
the Rank 2 gate. The Rank 2 gate is exactly the per-state F≥0.99 +
Im-floor table above.

## 4. Comparison & interpretation

- **Pre-registration vs outcome.** Gate expectation (F≥0.99, both)
  **held decisively**. The *quantitative* heuristic ("F high but
  below vacuum's 0.999 due to broader β_y χ-tail truncation at B=4")
  was **conservative**: θ=0 landed at 0.9995, not below 0.999. The
  zero-pad-to-161² + the *integrated* overlap fidelity absorb the
  broad-β_y tail far better than the L∞ truncation heuristic
  implied — the recorded expectation was directional but pessimistic
  on magnitude; logged as a calibration note, not a failure.
- **θ=π/2 ≥ θ=0, as pre-registered.** The control reconstructs
  essentially perfectly (F=0.99999, L¹=0.0052 vs θ=0's 0.0417):
  with the squeeze ellipse rotated, the broad χ direction aligns
  more favourably with the square v0.2 grid. The anisotropy
  orientation behaves exactly as the §3 derivation predicts — a
  clean positive control on the closed form and the θ handling.
- **Scope §3 locked claim confirmed.** "No grid escalation required
  at r~0.5 (unlike GKP)" is **validated**: r=0.5 reconstructs at the
  pure-Gaussian tier on the *unmodified* v0.2 grid/window. The
  decision-relevant pre-commitment (a sub-0.99 result would have
  forced a follow-up scope note) is **not triggered**.
- **D-2 confirmed empirically.** The ideal-SDF χ chain is η-exact
  for squeezed vacuum: reusing the D3 analytic path *verbatim* with
  only the locked closed-form χ added reproduces the squeezed Wigner
  at machine-floor imaginary error and pure-Gaussian fidelity — no
  𝒪(η²) correction is needed on the ideal leg, exactly as the scope
  §2 argued.

## 5. Next-step decision

Rank 2's ideal-leg payload is **delivered and gated PASS**
(squeezed_eta2_scope.md §9 step 2 complete). New artefact family
`squeezed_recon.{h5,manifest.json}`; parked `reconstruction_demo.h5`
and all other parked artefacts untouched; `DEFAULT_STATES` frozen
(bare D3 demo provenance stable).

**Open / deferred (unchanged):**
- **§9 step 3 — native-engine 𝒪(η²) squeezing re-audit** on the §4
  ξ_tot comb. This is the separate deferred scope (the
  scope-breadth decision); reopen with its own pre-registered run.
  The scope note §5 already fixes its mechanism, sign, and ≈16 %
  scale so that follow-up is bounded.
- GKP remains a separate future WP (unchanged).

No open blockers for the locked Rank 2 ideal deliverable.
