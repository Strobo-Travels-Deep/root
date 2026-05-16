# WP-W — Motional back-action diagnostic (v0.6 scope)

**WP-W · back-action scope · 2026-05-16**

**Status.** *Scoping pass only — proposed, pending user lock.* No
runner work until the five decisions below are locked. This note
settles the WORK-PROGRAM §8 "open v0.5 items" and the
[close-out logbook](../logbook/2026-05-16-wpw-closeout-and-followups.md)
Rank 1 first step. It is the back-action analogue of
[`analytic_chain.md`](./analytic_chain.md): a convention-locked,
self-contained scope a future session can execute without re-deriving
the landscape.

-----

## 1. What the diagnostic is (and is not)

The back-action diagnostic measures the **post-train motional state**
$\rho_m^{(\mathrm{post})}$, *not* the χ readout. The χ chain
([`analytic_chain.md`](./analytic_chain.md) §2) extracts spin
coherence $\langle\sigma_y\rangle-i\langle\sigma_z\rangle$ and traces
the motion *away*. The back-action diagnostic instead keeps the
motion and asks: **what did the measurement cost the oscillator?**

Two objects, both from the *same* forward propagator that already
drives χ (this is why Rank 1 reuses existing engine outputs):

- **Unconditional** reduced motional state
  $\rho_m^{(\mathrm{post})}=\operatorname{Tr}_\text{spin}\!\big[U(\rho_m\!\otimes\!\rho_s)U^\dagger\big]$
  — measurement-induced decoherence, no spin readout assumed.
- **Conditional** state after a chosen spin readout — a
  post-selected Kraus map; the conditioned motional state **depends
  on the readout basis** (§4 decision 1).

## 2. Convention anchor (load-bearing)

Locked to the v0.5-corrected FH20-style σ_x SDF
([`analytic_chain.md`](./analytic_chain.md) §1):

$$U_\text{SDF}(\beta_\text{tot})=D\!\big(\sigma_x\,\beta_\text{tot}/2\big),$$

with $\beta_\text{tot}$ the **branch separation** (WP-W §2). The
$|{+}x\rangle$ branch is displaced by $+\beta_\text{tot}/2$, the
$|{-}x\rangle$ branch by $-\beta_\text{tot}/2$. Therefore, for the
ideal SDF with initial $|{+}y\rangle$ spin, the **unconditional**
reduced motional state is the 50/50 mixture of branches displaced by
**half the separation**:

$$\boxed{\;\rho_m^{(\mathrm{post})}=\tfrac12\Big(
  D(\tfrac{\beta_\text{tot}}{2})\,\rho_m\,D^\dagger(\tfrac{\beta_\text{tot}}{2})
  +D(-\tfrac{\beta_\text{tot}}{2})\,\rho_m\,D^\dagger(-\tfrac{\beta_\text{tot}}{2})
  \Big)\;}$$

**Doc-inconsistency found (and corrected).** WORK-PROGRAM §Analytical
bullet "Measurement back-action (ideal SDF)" wrote this mixture and
the conditional Kraus operator with the *full* $\beta_\text{tot}$
(stale pre-v0.5 $D(\sigma_z\beta)$ convention), while §8's v0.5 sketch
already used the correct $\beta_\text{tot}/2$. The §Analytical bullet
is corrected to $\beta_\text{tot}/2$ in this same scoping pass for
internal consistency with [`analytic_chain.md`](./analytic_chain.md)
§1 and §8. Recorded explicitly, not silently — see the
[scope logbook](../logbook/2026-05-16-back-action-scope.md).

Conditional Kraus operator under an orthogonal-equator (σ_y/σ_z)
readout, outcome $s=\pm1$, also at half-separation:

$$M_s\;\propto\;D(\tfrac{\beta_\text{tot}}{2})\;+\;s\,e^{i\phi}\,D(-\tfrac{\beta_\text{tot}}{2}).$$

## 3. Scope decisions — proposed lock

All five are determined by the physics + prior WP-W analysis; each is
a *proposed* lock the user confirms before any runner work.

### Decision 1 — Readout basis: **compute all three**

Once the post-train state vector $\psi=[\,\text{down};\text{up}\,]$
exists, all three readouts are near-free linear post-processing of
the *same* $\psi$. Compute and report all three; headline the first
and third.

| readout | conditioned motional state (ideal SDF, $|{+}y\rangle$ in) | role |
|---|---|---|
| **unconditional** | rank-2 mixture, eq. §2 box | headline — "cost of measurement" |
| **σ_x** (SDF axis) | single branch $D(\pm\beta_\text{tot}/2)\,|\psi_m\rangle$ | validates the branch picture |
| **σ_y / σ_z** (equator) | coherent branch sum $\propto D(+)\,\pm\,e^{i\phi}D(-)$ — cat-like | headline — the protocol-relevant conditioned state |

Rationale: the three tell orthogonal stories (decoherence vs branch
selection vs cat conditioning) and cost essentially nothing extra
given one propagation. Restricting to one basis would discard free
information and pre-empt the most interesting comparison
(branch-select vs coherent-sum).

### Decision 2 — Input subset: **minimal three** {vacuum, Fock $|2\rangle$, cat $|\alpha|=1.5$}

Not the full §7#4 headline set for the first execution. Rationale:

- **vacuum** — closed-form $\rho_m^{(\mathrm{post})}$ (50/50 mixture
  of $|\pm\beta_\text{tot}/2\rangle$): exact purity and Wigner, so it
  is the diagnostic's *own* correctness anchor (§6).
- **Fock $|2\rangle$** — negativity-rich; the D3 deciding state;
  exercises the Wigner-negativity-change metric.
- **cat $|\alpha|=1.5$** — the state where the readout-basis
  dependence is most dramatic (single displaced branch vs coherent
  cat-of-cats sum).

These three span Gaussian / Fock-negativity / coherence-sensitive,
and are all **pure** → the runner stays in ket-space except for the
rank-2 unconditional state (which needs the explicit ρ matrix +
parity-form Wigner; see §5). The full §7#4 set (coherent, thermal,
Fock $|1\rangle$, pure+mixed cat) is a documented **no-new-physics
extension**, deferred to keep the first pass tight (thermal is the
only one needing density-matrix propagation).

### Decision 3 — Metrics: **grid-free state-space primary, Wigner diagnostic**

- **Primary (grid-free, exact):**
  1. **Purity drop** $1-\operatorname{Tr}[(\rho_m^{(\mathrm{post})})^2]$.
  2. **Fidelity to the pre-train state**
     $\mathcal F=\langle\psi_m^\text{pre}|\rho_m^{(\mathrm{post})}|\psi_m^\text{pre}\rangle$
     (pure pre-state; the §7#4 subset is pure).
  3. **Branch separation** $|\beta_\text{tot}|$ — the analytic ruler
     (an *input knob* via the inverse-Dirichlet rule, not a measured
     output for the ideal leg).
- **Diagnostic figure (reported, never gated):** parity-form Wigner
  $W(\rho_m^{(\mathrm{post})})$ panels, ideal-SDF vs native-engine;
  **Wigner-negativity-volume change** $\int\min(0,W)\,d^2\alpha$
  before vs after; and the **ideal-vs-native Wigner $L^1$ distance**
  — the third bridge residual, a *structural* matched-control
  residual (native leg parameterised per §4a, not a $\beta_\text{eff}$
  calibration).

The Wigner-side numbers carry the **same caveat as the χ bridge
metric** ([feedback memory]; D4-bridge §3.3): grid-resolution-limited
Wigner differences are a *diagnostic residual*, not a fidelity gate.
The parity form (§5) sidesteps the v0.4 FFT $\Delta\alpha$ floor but
does not earn a hard threshold — only the state-space metrics (1)–(3)
are exact, and only the vacuum anchor (§6) is gated.

### Decision 4 — Artefacts

Mirrors the WP-E-aligned §5 folder layout exactly:

| kind | path | content |
|---|---|---|
| runner | `numerics/run_back_action.py` | per (input × β_tot point × {ideal, native}) propagate $|{+}y\rangle\!\otimes\!\rho_m$; emit unconditional ρ + three conditional kets + metrics |
| data | `numerics/back_action.h5` + `.manifest.json` | `wp_manifest_v1` envelope via `_common.canonical_manifest` / `write_manifest` |
| plot | `plots/plot_back_action.py` → `plots/back_action.png` | one row per input: pre-$W$ │ unconditional post-$W$ (ideal) │ unconditional post-$W$ (native) │ conditional σ_y/σ_z $W$; purity-drop & $\mathcal F$ annotated |
| logbook | `logbook/2026-05-16-back-action-scope.md` (this scope) + a later dated run entry | pre-registered expectations → run → comparison |

**New shared helpers** (in `numerics/_common.py`, smoke-tested
alongside the existing `scripts/stroboscopic/tests` style):

- `partial_trace_spin(psi, nmax)` → correctly-oriented
  $\rho_m=|{\downarrow}\rangle\langle{\downarrow}|\!+\!|{\uparrow}\rangle\langle{\uparrow}|$
  blocks. **Do not reuse `observables.compute`'s internal `rho_m`**:
  it is built as `outer(conj(down),down)+outer(conj(up),up)`, i.e.
  the *conjugate-transpose* of the physical reduced state — harmless
  for its only use (transpose-invariant purity) but wrong for Wigner
  / fidelity. See §5.
- `conditional_motional_ket(psi, nmax, basis, outcome)` — σ_x/σ_y/σ_z
  post-select + renormalise (pure-in ⇒ pure-out).
- `wigner_from_rho(rho, alpha_grid)` — parity form
  $W(\alpha)=\tfrac{2}{\pi}\operatorname{Tr}[\rho\,D(\alpha)\Pi D^\dagger(\alpha)]$,
  $\Pi=(-1)^{a^\dagger a}$. **Prefactor is $2/\pi$, not $\pi^{-1}$**:
  the WP-W convention anchors $W_\text{vac}(0)=2/\pi$ (P0:
  $0.636555$; `analytic_chain.md` §4). The $D(\alpha)\Pi D^\dagger(\alpha)$
  vs $D^\dagger\Pi D$ displacement order is fixed by a smoke test
  against analytic $W_\text{vac}$ / $W_\text{coherent}$ (parity is
  even, so the prefactor is the load-bearing choice).
- `cat_ket(alpha, nmax, parity)` — **no cat builder exists** in
  `scripts/stroboscopic/states.py` (only coherent/Fock/thermal/
  squeezed); build the normalised $(|\alpha\rangle\pm|{-}\alpha\rangle)$
  superposition here.

### Decision 5 — Gating: **exploratory diagnostic, one internal PASS**

Consistent with the §8 bridge-policy framing and the close-out
logbook ("a third bridge residual … not a fidelity gate"):

- **The only hard PASS/FAIL** is the **vacuum analytic
  self-consistency anchor** for the *ideal-SDF* leg (§6): a
  correctness check on the diagnostic's own machinery, not a physics
  claim.
- Everything else — Fock $|2\rangle$, cat; the native-engine leg;
  every readout-basis-conditional state; the ideal-vs-native Wigner
  $L^1$ — is **reported, not gated**. This is a characterisation
  diagnostic ([Hasse24] App. D / Fig. 6b mapped $\delta\langle n\rangle$
  qualitatively; WP-W's contribution is the *quantitative*
  ideal-vs-native Wigner-resolved difference), not a tomography
  fidelity gate.

## 4. β_tot sampling — not a phase-space scan

Back-action is a **per-(state, β_tot) probe**, not the
inverse-Dirichlet Cartesian β-grid of D3/D4 (that grid exists only
for the χ→FFT reconstruction). Sample two representative points:

1. **on-resonance peak** $|\beta_\text{tot}|=N\beta_0$ — maximum
   back-action;
2. one **mid-branch** point $|\beta_\text{tot}|\approx N\beta_0/2$ —
   the back-action–vs–information trade-off mid-scale.

This makes the runner ~$O(\text{states}\times2\times2)$ propagations
— milliseconds for the native engine per point, far below the 18-min
D4 inversion. No wall-time concern.

### 4a. Native leg — matched physical control, not β_eff

`build_strobo_train` has **no $\beta_\text{tot}$ knob**, and
[`analytic_chain.md`](./analytic_chain.md) §5 / §7#3 establish that
the bridge is *structural* — **there is no native
$\Omega_r\delta t\mapsto\beta_0$ conversion** and a calibrated
$\beta_\text{eff}$ match would contradict that finding. The
reproducible native-leg convention is therefore **matched physical
control, not matched $\beta_\text{tot}$**:

- The β_tot probe points of §4 are defined on the **ideal leg only**
  (via the inverse-Dirichlet rule → $(\delta-k\omega_m,\varphi_\text{train})$).
- The **native leg runs the D4 Layer A pinned WP-E v0.9.1 train** at
  the *same* $(\delta-k\omega_m,\varphi_\text{train},N)$ the
  inverse-Dirichlet rule assigns to each probe point: $N=30$,
  $\delta t=0.13\,T_m$, $\eta=0.397$, $\omega_m/2\pi=1.300$ MHz,
  $\Omega_r=0.0902$, **no separate MW π/2**, motional-phase shift
  $\texttt{shift\_deg}=\omega_m\delta t/2$ (WP-E v0.9.1; §7#7,
  D4-bridge §2.1). Peak → on-resonance tooth $x=0$; mid-branch →
  the $x$ solving $|\mathcal D_N(x)|=N\beta_0/2$ on the central
  monotone branch.
- The **ideal-vs-native Wigner $L^1$ is then a *structural*
  back-action residual at matched physical drive** — "given the
  same drive program, how differently is the oscillator disturbed?"
  — the back-action analogue of D4 Layer B's structural χ residual,
  **not** a $\beta_\text{eff}$-calibrated comparison. The two legs
  generally produce *different* $\beta_\text{tot}$; that gap is
  precisely the structural diagnostic, consistent with §7#3.

(The ideal leg keeps the v0.2 nominal $\beta_0=0.05$; the difference
between the ideal $\beta_0$ and the native effective per-pulse kick
is part of the measured structural residual, never calibrated away.)

## 5. Implementation surface & risks

- **Reuses the engine wholesale.** `ideal_sdf.build_ideal_sdf_train`
  / `IdealSDFTrain.evolve` (ideal leg) and `build_strobo_train`
  (native leg) already return the full $\psi$. No new physics.
- **Risk — reduced-DM orientation.** `observables.compute` builds
  `rho_m = outer(conj(down),down)+outer(conj(up),up)` ⇒ that array
  is $(\rho_m)^{*}$/$(\rho_m)^{T}$. Purity is unaffected; Wigner and
  fidelity are *not*. The new `partial_trace_spin` must use the
  physical convention $\rho_m[i,j]=\text{down}[i]\,\text{down}[j]^{*}+\text{up}[i]\,\text{up}[j]^{*}$.
- **Risk — cat input.** No ket builder; construct
  $(|\alpha\rangle\pm|{-}\alpha\rangle)/\mathcal N$ from two
  `states.coherent_state` calls; verify against `_common.chi_cat` /
  `_common.W_cat` at one point.
- **Risk — Fock cutoff.** Displaced Fock $|2\rangle$ at the peak
  $|\beta_\text{tot}|/2$ needs adequate `nmax`; reuse the D3/D4
  cutoff and add a `fock_leakage` guard.
- **Pure vs mixed.** §7#4-subset inputs are pure ⇒ conditional
  states are pure kets; only the *unconditional* state is rank-2
  (needs the explicit ρ + `wigner_from_rho`). Thermal (full-set
  extension) is the only input forcing full density-matrix
  propagation — deferred with Decision 2.

## 6. Provenance anchor (the diagnostic's own correctness)

Vacuum, ideal SDF, $|{+}y\rangle$ in: $\rho_m^{(\mathrm{post})}$ is
the 50/50 mixture of coherent states $|\pm\beta_\text{tot}/2\rangle$.
Closed forms to gate against (branches at $\gamma=\beta_\text{tot}/2$;
$\langle\gamma|{-}\gamma\rangle=e^{-2|\gamma|^2}=e^{-|\beta_\text{tot}|^2/2}$,
so $|\langle\gamma|{-}\gamma\rangle|^2=e^{-|\beta_\text{tot}|^2}$):

- **Purity** $\operatorname{Tr}[(\rho_m^{(\mathrm{post})})^2]
  =\tfrac12\big(1+e^{-|\beta_\text{tot}|^2}\big)$
  (purity *drop* $=\tfrac12\big(1-e^{-|\beta_\text{tot}|^2}\big)$).
- **Fidelity to pre-state** (vacuum)
  $\mathcal F=\langle0|\rho_m^{(\mathrm{post})}|0\rangle
  =\tfrac12\big(|\langle0|\gamma\rangle|^2+|\langle0|{-}\gamma\rangle|^2\big)
  =e^{-|\gamma|^2}=e^{-|\beta_\text{tot}|^2/4}$ — closed form, exact.
- **Wigner** = sum of two Gaussians at $\pm\beta_\text{tot}/2$ (no
  interference — the unconditional mixture is *incoherent*; fringes
  appear only in the σ_y/σ_z conditional cat), each normalised by the
  $2/\pi$ parity-form prefactor above.

PASS = parity-form `wigner_from_rho` + state-space purity reproduce
these to the `complex128` floor (cf. P0's $\sim10^{-16}$). This is
the back-action analogue of P0/P1: it validates the machinery before
any native-engine comparison is interpreted.

## 7. Recommended first execution plan (when user says "go")

One clean commit, one session — matching the WP-W execution
discipline.

0. **Lock.** User confirms this note → promote §3 decisions into
   WORK-PROGRAM §8 as the v0.6 scope (currently a forward pointer).
1. **Helpers + smoke tests.** Add the four `_common` helpers;
   smoke-test: `wigner_from_rho` vs analytic for vacuum / coherent /
   Fock $|2\rangle$; `partial_trace_spin` of a product state returns
   the input; σ_x post-select of ideal-SDF $|{+}y\rangle|0\rangle$
   equals $D(\pm\beta_\text{tot}/2)|0\rangle$; `cat_ket` vs
   `_common.W_cat`.
2. **Vacuum gate (§6).** Implement and pass the only hard PASS/FAIL
   before anything else.
3. **`run_back_action.py`.** Loop {vacuum, Fock $|2\rangle$, cat} ×
   {peak, mid-branch} × {ideal, native}; emit unconditional ρ +
   three conditional kets + metrics → `back_action.h5` + manifest.
4. **`plot_back_action.py`** + dated run logbook entry (pre-reg →
   run → comparison) + commit.

-----

*Source of truth for conventions:
[`analytic_chain.md`](./analytic_chain.md) §1–§2 (σ_x SDF, branches
at $\pm\beta_\text{tot}/2$). This note adds no new physics; it locks
the back-action protocol decisions left open in WORK-PROGRAM §8.*
