# WP-W — Native-engine 𝒪(η²) squeezing re-audit (scope)

**WP-W · Rank 2 §9 step 3 · 2026-05-18**

**Status.** *PROPOSED — doc-only checkpoint.* No runner code until the
user locks §3 (the `cb850a5` / `3b3db78` discipline: scope → user
lock → execute). This is the deferred follow-up named in
[`squeezed_eta2_scope.md`](./squeezed_eta2_scope.md) §0/§5/§8 D-4/§9
step 3 ("Native-engine 𝒪(η²) squeezing re-audit on the §4 ξ_tot
comb — its own pre-registered run when reopened"). The user's
direction (2026-05-18) is **strengthen the science before any
publication deliberation**: this re-audit converts the η² thread from
analytic-only into a *quantified native result*.

It is **bounded, not open**: the parent scope §4–§6 already fixed the
ξ_tot comb map, the mechanism, the sign of dependence, and the ≈16 %
scale. This note promotes those into *falsifiable pre-registered
predictions* and locks the run decisions. It adds **no new derivation
and no engine physics** — it re-uses the validated engine + the
η-exact ideal leg.

-----

## 0. What this settles (and does not)

**Settles (on lock → execution):**

1. Whether the native monochromatic engine, driven at the App. E
   two-phonon timing (Δt=T_m/2), produces the squeezing-type
   back-action that [`squeezed_eta2_scope.md`](./squeezed_eta2_scope.md)
   §4–§5 predicts — quantitatively, vs the η-exact ideal leg.
2. Whether the structural ideal↔native residual for a squeezed input
   is (a) relative size ~η² ≈ 16 % at η=0.397, (b)
   quadrature-angle-dependent, (c) modulated by the input squeezing
   (largest when the anti-squeezed quadrature aligns with the SDF
   axis) — the three §5 pre-registered claims.
3. The squeezed analogue of the D4 Layer B / `back_action_scope.md`
   §4a *structural* residual (matched physical drive, no ξ_eff
   calibration).

**Does not:**

- Re-open any derivation (§4–§6 of the parent scope are locked).
- Touch the ideal leg (η-exact; `cd22ef6` gate stands) or any parked
  artefact.
- GKP (separate WP, unchanged).
- Decide publication — that deliberation resumes *after* this result,
  per the user's sequencing.

## 1. Pre-registered predictions (from parent §4–§6, made falsifiable)

Logged before any run. Each is a sharp, falsifiable claim; the run
either confirms or refutes it and the logbook reports honestly.

- **P-A (scale).** At η=0.397 the ideal↔native structural residual
  for squeezed vacuum is of relative order η² ≈ 0.16 — i.e.
  *materially larger* than the same residual for the displaced-state
  inputs at matched drive (the back-action family's vacuum/coherent
  rows), and **dominated by the two-phonon $a^2{+}a^{\dagger2}$
  channel**, not the first-order displacement term.
- **P-B (angle dependence).** The residual is **quadrature-angle
  dependent**: scanning the squeeze angle θ (or equivalently the SDF
  axis vs the squeezed quadrature) modulates it, with an extremum
  when the **anti-squeezed quadrature aligns with the SDF axis** and
  the conjugate extremum a quarter-turn away. A flat (θ-independent)
  residual **refutes** the §5 mechanism.
- **P-C (squeezing modulation).** The residual **grows with r**: at
  r=0 (vacuum) it reduces to the back-action family's vacuum
  structural residual; at r=0.5 it is enhanced by the squeezing in
  the predicted direction. Monotone-in-r over r∈{0, 0.25, 0.5} is
  the pre-registered shape.
- **P-D (ideal leg invariant).** The ideal squeezed-vacuum leg at the
  App. E timing reproduces the `cd22ef6` η-exact reconstruction
  (F≥0.99 Gaussian tier; max|Im W| at the complex128 floor) — the
  timing change is a *native-protocol* device, the ideal χ readout is
  unaffected (parent §2/§4). This is the **machinery self-consistency
  check** (the P0/P1 analogue), and is the *only* hard PASS/FAIL.
- **P-E (systematic ordering).** The finite-pulse-duration
  $\mathcal O((\delta t/T_m)^2)\approx1.7\%$ two-phonon term (parent
  §6) is *same-symmetry* with the η² channel and sub-dominant; it is
  carried as a reported systematic, never subtracted.

## 2. Native leg — App. E timing & matched control

Inherited verbatim from [`squeezed_eta2_scope.md`](./squeezed_eta2_scope.md)
§4 and the `back_action_scope.md` §4a matched-control discipline:

- **Timing:** Δt = 2π/(2ω_m) = T_m/2; the two-phonon detuning phase
  $\tilde x=(\delta-k\omega_m)\,T_m/2$; accumulated squeezing
  $\xi_\text{tot}=\xi_0 e^{i\varphi_\text{train}}\mathcal D_N(\tilde x)$,
  *same Dirichlet kernel*, doubled fundamental, $\xi_0=\mathcal O(\eta^2\Omega_r\Delta t)$.
  Inverse-Dirichlet targeting and central-branch monotonicity
  transfer with $\tilde x$ for $x$.
- **Matched physical control, not ξ_eff.** The ξ_tot probe is defined
  on the **ideal leg**; the native leg runs the *same*
  $(\delta-k\omega_m,\varphi_\text{train},N)$ at Δt=T_m/2 — no
  ξ_eff calibration (the structural residual *is* the diagnostic; the
  legs generally produce different ξ_tot, consistent with parent §5).
  Uniform lab frame, identical squeezed input both legs (no
  input-state phase shift — `back_action_scope.md` §4a).
- **Pinned engine parameters** as the D4-Layer-A WP-E v0.9.1 train:
  η=0.397, ω_m/2π=1.300 MHz, Ω_r=0.0902, N=30, δt=0.13 T_m, no
  separate MW π/2. Only the *gap* changes (T_m → T_m/2) to sync the
  train to the 2ω_m quadrature evolution.

## 3. Proposed decisions (the locks the user confirms before any code)

- **N-1 — Test states.** Squeezed vacuum, r ∈ {0, 0.25, 0.5}
  (r=0 = the vacuum back-action control; r=0.5 = the `cd22ef6`
  headline), squeeze angle θ ∈ {0, π/4, π/2} (the §5 angle scan; θ=0
  squeezed-in-X, π/2 perp, π/4 the intermediate that maximises the
  predicted modulation). Pure Gaussian, lab-frame, matched both legs.
- **N-2 — Probe point.** The on-resonance two-phonon **peak**
  ($\tilde x=0$, $|\xi_\text{tot}|=N\xi_0$) — maximum two-phonon
  back-action — plus one **mid-branch** point (the
  back-action-family two-point convention). Not a phase-space scan.
- **N-3 — Metric.** The *structural* ideal-vs-native residual: (i)
  state-space — purity drop & fidelity-to-pre of the post-train
  motional state (the `back_action_scope.md` primary metrics,
  generalised — squeezed pre-state is pure); (ii) Wigner $L^1$
  (the §4a structural residual). Reported with the §1 predictions
  as the pre-registered comparison. **Reported, not gated** (the
  bridge policy: a structural diagnostic, not a fidelity gate).
- **N-4 — Gate.** One hard PASS/FAIL only: **P-D** (ideal leg
  invariance at the App. E timing) at the `cd22ef6` Gaussian tier +
  max|Im W| floor. Everything native/η²/pulse-duration is reported,
  not gated (consistent with `back_action_scope.md` Decision 5 and
  the close-out bridge policy).
- **N-5 — Implementation surface (honest).** This is **not** a
  trivial re-run. `run_back_action.py` has the native leg +
  weighted-ket (Gaussian-as-ket-list) + matched-control machinery,
  but every existing native leg uses the **Δt=T_m carrier/sideband**
  teeth. The **Δt=T_m/2 two-phonon timing is new code** — a
  `--two-phonon`/`--app-e-timing` path that (a) halves the gap, (b)
  builds the ξ_tot inverse-Dirichlet on $\tilde x$, (c) adds the
  squeezed-vacuum ket to the input set. The ideal/η-exact path and
  the hard vacuum gate are reused verbatim (regression: the existing
  back-action artefacts must reproduce bit-for-bit, as in `be90a21`).
- **N-6 — Pre-registered engine-capability risk (must be checked
  first).** At the pinned (Ω_r, η) the two-phonon $a^2{+}a^{\dagger2}$
  resonance may be weak or contaminated by the off-resonant carrier
  / first-sideband terms (RWA validity at Δt=T_m/2). The run **must**
  first verify, on vacuum, that the native engine at the App. E
  timing produces a *recognisable squeezing* action (variance
  asymmetry growing with N along the predicted quadrature) before any
  ideal-vs-native residual is interpreted. If it does not, that is
  itself the headline finding (the monochromatic engine does not
  cleanly engineer the 2ω_m squeezing channel at the pinned
  parameters) — a sharpening of the parent §2 "structural, not a
  regime limit" conclusion, *strengthening* the eventual paper, and
  is reported as such, not worked around.

## 4. Recommended execution plan (only on lock)

One clean commit each, WP-W discipline; new artefact family, parked
artefacts untouched:

0. **Lock.** User confirms §3 (or amends). Promote, doc-only.
1. **Engine-capability smoke (N-6) + helper.** Verify the Δt=T_m/2
   native engine squeezes vacuum (variance-asymmetry-vs-N), and add
   the ξ_tot inverse-Dirichlet on $\tilde x$ + smoke test. Commit.
2. **Native re-audit run.** r∈{0,0.25,0.5} × θ∈{0,π/4,π/2} × {peak,
   mid} × {ideal, native} → `squeezed_native_audit.h5`; the P-D hard
   gate; pre-reg → run → comparison vs P-A…P-E; dated logbook;
   commit. New artefact family; parked back-action / reconstruction
   artefacts untouched (explicit `--output`).
3. **Reassess publication** (the deferred deliberation) with the η²
   thread now quantified.

-----

*Source of truth: [`squeezed_eta2_scope.md`](./squeezed_eta2_scope.md)
§4–§6 (LOCKED) for the ξ_tot map / mechanism / sign / scale;
[`back_action_scope.md`](./back_action_scope.md) §4a/Decision 5 for
the matched-control + bridge-policy discipline;
[`analytic_chain.md`](./analytic_chain.md) §5 for the structural
ideal↔native argument. This note adds no derivation; it locks the
re-audit run decisions. PROPOSED — no code until §3 is locked.*
