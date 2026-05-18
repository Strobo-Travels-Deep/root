# WP-W — 𝒪(η²) analytic extension & squeezed-vacuum scope

**WP-W · Rank 2 prerequisite · 2026-05-19**

**Status.** *PROPOSED — doc-only derivation/scope checkpoint.* No
runner code until the user locks §8 (mirroring the
[`back_action_scope.md`](./back_action_scope.md) / `cb850a5`
discipline: derive → user lock → execute). This note is the Rank 2
first step recorded in
[`2026-05-16-wpw-closeout-and-followups.md`](../logbook/2026-05-16-wpw-closeout-and-followups.md)
§5 ("𝒪(η²) extension of the analytic chain … then re-audit the
σ_x-SDF bridge at that order; test state ideal squeezed vacuum at
r∼0.5; update D1 §6") **plus** the user-requested closure of the
open pulse-duration δt/T_m order ([`analytic_chain.md`](./analytic_chain.md)
§6 point 4 / WORK-PROGRAM §Analytical bullet 5 `[TBD]`). It is the
foundational analytical pass Rank 2 is gated on; it adds **no new
physics to the engine** — it derives consequences and locks the
protocol decisions a squeezed-vacuum runner would need.

Conventions are inherited verbatim from
[`analytic_chain.md`](./analytic_chain.md) §1–§5 (σ_x SDF, branches
at $\pm\beta/2$, symmetric χ, the Dirichlet β-map, the LD-expanded
monochromatic engine). Symbols as there:
$D(\beta)=e^{\beta a^\dagger-\beta^*a}$, $X=a+a^\dagger$,
$\sigma_\varphi=\cos\varphi\,\sigma_x+\sin\varphi\,\sigma_y$,
$T_m=2\pi/\omega_m$, $x=(\delta-k\omega_m)T_m$.

-----

## 0. What this note settles (and what it does not)

**Settles (analytically, proposed):**

1. The 𝒪(η²) operator content and *which sector of the protocol the
   η² term actually gates* — the central correction to the close-out
   framing (§2).
2. The squeezed-vacuum symmetric χ closed form and its
   grid/β-window consequences (§3).
3. The [Hasse24] App. E timing change $\Delta t=2\pi/(2\omega_m)$
   re-derived as the §3 Dirichlet map for the **2ω_m quadrature
   dynamics** — the squeezed-state analogue of $\beta_\text{tot}$ (§4).
4. The leading finite pulse-duration order in $\delta t/T_m$, its
   relation to the documented `shift_deg`, and how it composes with
   η² — closing the long-standing `[TBD]` (§6).
5. A proposed D1 §6 approximation-hierarchy rewrite (§7) and the
   proposed locks for a squeezed-vacuum runner (§8).

**Does not (deferred, explicitly):**

- The **native-engine bridge re-audit at 𝒪(η²)** — the structural
  ideal↔native squeezing residual (the §5 sketch flags its size and
  mechanism but the full Layer-B-style audit is the follow-up the
  user deferred in the scope-breadth decision).
- Any runner / gate execution. Squeezed-vacuum reconstruction stays
  parked until §8 is locked.
- GKP (separate future WP, unchanged).

## 1. The 𝒪(η²) Lamb–Dicke content

[`analytic_chain.md`](./analytic_chain.md) §5 already carries the
expansion to second order:

$$
  \frac{\Omega_r}{2}\Big[\sigma_\varphi+\eta X\,\sigma_{\varphi+\pi/2}
   -\tfrac{\eta^2X^2}{2}\,\sigma_\varphi+\mathcal O(\eta^3)\Big].
$$

Resolve the quadratic operator:

$$
  X^2=(a+a^\dagger)^2=\underbrace{a^2+a^{\dagger2}}_{\text{two-phonon}}
   +\underbrace{2a^\dagger a+1}_{\text{number + c-number}}.
$$

Three physically distinct 𝒪(η²) channels, by resonance:

| term | rotating-frame frequency | resonance | effect |
|---|---|---|---|
| $a^2,\;a^{\dagger2}$ | $\pm2\omega_m$ | $\delta=\pm2\omega_m$ (2nd sideband) | **two-phonon (squeezing) coupling** $\propto\eta^2\Omega_r(a^2+a^{\dagger2})\sigma_\varphi$ |
| $2a^\dagger a$ | $0$ (DC) | always | number-dependent Stark / cross-Kerr shift |
| $1$ | $0$ | always | spin-only c-number (absorbable) |

The **two-phonon term is the squeezing generator**: under a
second-sideband resonance and the RWA it is the trapped-ion
parametric (Bogoliubov) coupling, and it evolves at $2\omega_m$ — the
origin of the [Hasse24] App. E timing change (§4). Its coefficient is
$\mathcal O(\eta^2)$: at the WP-E pinned $\eta=0.397$ (D4 Layer A),
$\eta^2\approx0.158$ — **≈16 %**, *not* a negligible tail (WORK-PROGRAM
line 282). This is why squeezing cannot ride the first-order chain:
the first-order term $\eta X\sigma_{\varphi+\pi/2}$ is strictly
single-phonon (displacement-type) and **cannot generate
quadrature-variance dynamics at any order of comb sharpening**
(the §5 structural argument of [`analytic_chain.md`](./analytic_chain.md),
extended: comb selection picks a term, it does not change its phonon
order).

## 2. Where η² gates — and, crucially, where it does **not**

The close-out logbook says squeezed vacuum is "gated on the 𝒪(η²)
chain." That is correct but must be attributed precisely, or the
runner is scoped wrong:

**The ideal-SDF tomography chain is η-EXACT for a squeezed input.**
$U_\text{SDF}(\beta)=D(\sigma_x\beta/2)$ is an *exact* displacement
— it carries no η expansion (it is the `ideal_sdf` primitive, not a
regime limit of the engine; [`analytic_chain.md`](./analytic_chain.md)
§5). The §2 readout

$$
  \langle{+}x|\rho_\text{spin}|{-}x\rangle\propto
  \langle\psi_m|D(\beta)|\psi_m\rangle=\chi_{\rho_m}(\beta)
  =\langle\sigma_y\rangle-i\langle\sigma_z\rangle
$$

is **state-independent in its derivation** — it holds for *any*
$\rho_m$, squeezed vacuum included, with no Gaussian prefactor and no
η. Likewise the §4 χ→Wigner FFT is exact. So:

- **P0/P1/D1 §1–§4 transfer unchanged to squeezed vacuum.** The
  ideal-leg reconstruction of a squeezed state needs *no* 𝒪(η²)
  correction. (This sharpens — and partially corrects — the WP §7#4
  wording "not captured by the first-order LD chain": the *ideal*
  chain captures it exactly; the **native realisation** and the
  **stroboscopic timing** are what carry the η² dependence.)

The 𝒪(η²) gate is therefore exactly two things, and only these:

1. **Protocol timing / comb (DERIVED HERE, §4).** The displaced-state
   stroboscopic comb (§3) syncs the train to the *ω_m* phase-space
   orbit. A squeezed state's information-bearing structure — the
   quadrature-variance ellipse — rotates/breathes at **2ω_m**. The
   §3 Dirichlet map must be re-derived for the doubled fundamental
   ([Hasse24] App. E, $\Delta t=2\pi/2\omega_m$). This is a *protocol
   structure* change, present even for an idealised SDF, and is the
   load-bearing analytic deliverable of this note.

2. **Native-engine structural residual at η² (FLAGGED, §5; full
   audit deferred).** The native surrogate's
   $-\tfrac{\eta^2}{2}X^2\sigma_\varphi$ term injects a genuine
   ≈16 % two-phonon (squeezing-type) back-action absent from the
   first-order bridge audit. The *ideal* leg is clean; the
   ideal↔native structural residual acquires a new, quadrature-
   dependent component. Quantifying it is the deferred follow-up.

## 3. Squeezed-vacuum χ and grid/window consequences

Squeezed vacuum $|r,\theta\rangle=S(\xi)|0\rangle$,
$S(\xi)=\exp[\tfrac12(\xi^*a^2-\xi a^{\dagger2})]$, $\xi=re^{i\theta}$.
Its symmetric (Cahill–Glauber) characteristic function is the
zero-mean Gaussian

$$
  \boxed{\;\chi_{|r,\theta\rangle}(\beta)
   =\exp\!\Big[-\tfrac12\big(|\beta|^2\cosh2r
   -\operatorname{Re}(\beta^2e^{-i\theta})\,\sinh2r\big)\Big]\;}
$$

(derived from $\langle0|S^\dagger D(\beta)S|0\rangle$ with
$S^\dagger aS=a\cosh r-a^\dagger e^{i\theta}\sinh r$; reduces to the
vacuum $e^{-|\beta|^2/2}$ at $r=0$). For $\theta=0$ this is
$\exp[-\tfrac12(\beta_x^2e^{-2r}+\beta_y^2e^{+2r})]$ — narrow along
the anti-squeezed χ-axis, **broad by $e^{+2r}$ along the other**.

The phase-dependent $\operatorname{Re}(\beta^2e^{-i\theta})$ term is
the "quadratic structure" the WP text refers to: it is the angular
β² anisotropy that a *displacement* probe (the SDF) reads out
perfectly, but that the stroboscopic *comb* (§4) must be oriented to
resolve.

**Grid/window consequence (provenance: same logic as the GKP
deferral, close-out §5 Rank 3).** χ support extends to
$|\beta|\sim e^{+r}$ along the anti-squeezed quadrature. At $r\sim0.5$,
$e^{+r}\approx1.65$ — well inside the validated $B=N\beta_0$ reach and
the $[-3,3]$ Wigner window, so **no grid escalation is required at
$r\sim0.5$** (unlike GKP). This is recorded as a *proposed* gate
input, to be re-checked at runtime against the inverse-Dirichlet
reach (§8 D-3).

## 4. The App. E timing change — §3 Dirichlet map at 2ω_m

This is the load-bearing derivation. [Hasse24] App. E asserts the
timing change $\Delta t=2\pi/(2\omega_m)$ for squeezed-state
stroboscopic reconstruction; here it is re-derived as the §3 map
with the squeezing fundamental.

In the §3 displaced-state protocol, between pulses the rotating-frame
SDF axis advances by the single-phonon detuning phase
$x=(\delta-k\omega_m)T_m$; the per-pulse contribution
$\beta_0e^{i(\varphi_\text{train}+nx)}$ sums to the Dirichlet kernel
$\mathcal D_N(x)$ at fundamental $\omega_m$ (because a *displacement*
orbits phase space once per $T_m$).

For the squeezing channel the relevant generator is the two-phonon
operator $a^2,a^{\dagger2}$ (§1), whose free-evolution phase advances
at $2\omega_m$: under $H_0=\omega_m a^\dagger a$,
$a^2(t)=e^{-2i\omega_m t}a^2$. Repeating the §3 construction with the
two-phonon phase $\;\tilde x\equiv(\delta-k\omega_m)\,\Delta t\;$
accumulated over a gap $\Delta t$, the coherent stroboscopic build-up
of the squeezing interaction requires the gap to be an integer
fraction of the **2ω_m** period, i.e.

$$
  \boxed{\;\Delta t=\frac{2\pi}{2\omega_m}=\frac{T_m}{2}
   \quad(\text{App. E timing}),\qquad
   \tilde x=(\delta-k\omega_m)\,\tfrac{T_m}{2}\;}
$$

so that the per-pulse two-phonon kicks add along a controlled
direction. The accumulated **squeezing parameter** is then the
direct analogue of $\beta_\text{tot}$:

$$
  \xi_\text{tot}(\delta,\varphi_\text{train};N)
   =\xi_0\,e^{i\varphi_\text{train}}\,\mathcal D_N(\tilde x),
   \qquad \xi_0=\mathcal O(\eta^2\,\Omega_r\,\Delta t),
$$

with the **same Dirichlet kernel** $\mathcal D_N$ — the comb-sharpening
mathematics of §3 carries over verbatim; only the fundamental
($\omega_m\!\to\!2\omega_m$, hence $T_m\!\to\!T_m/2$) and the
per-pulse scale ($\beta_0=\mathcal O(\eta)\!\to\!\xi_0=\mathcal O(\eta^2)$)
change. The inverse-Dirichlet targeting (§3.1) and the central-branch
monotonicity transfer unchanged with $\tilde x$ in place of $x$.

*Consequence for the ideal leg.* The ideal-SDF reconstruction still
reads χ exactly (§2); the App. E timing is what a squeezed-state
*native* engineering / probe protocol requires. The note records the
$\xi_\text{tot}$ map so the eventual runner's ideal squeezed-vacuum
target and its native counterpart are defined on the **same** comb
algebra as the displaced case — preserving the matched-control
discipline of `back_action_scope.md` §4a.

## 5. Native-engine 𝒪(η²) back-action (flagged; full audit deferred)

For a squeezed input the native surrogate's
$-\tfrac{\eta^2}{2}X^2\sigma_\varphi$ term is not phase-symmetric: its
$a^2+a^{\dagger2}$ part couples to the squeezed quadrature variance,
so the ideal↔native structural residual gains a **quadrature-angle-
dependent** component of relative size $\sim\eta^2=16\%$ (η=0.397),
*modulated by* the input squeezing (largest when the anti-squeezed
quadrature aligns with the SDF axis). This is the squeezed analogue
of the `back_action_scope.md` structural residual and is expected to
be the dominant ideal↔native discriminator for squeezed inputs. Per
the user's scope-breadth decision the **full Layer-B-style native
re-audit at 𝒪(η²) is the deferred follow-up**; this note only fixes
its mechanism, sign of dependence, and ≈16 % scale so the follow-up
is a bounded, pre-registered run, not an open derivation.

## 6. Pulse-duration δt/T_m order — closing the `[TBD]`

The `ideal_sdf` primitive idealises each kick as an instantaneous
$D(\sigma_x\beta_0)$ with a full-period motional gap (identity at
$t_\text{sep}=T_m$; [`analytic_chain.md`](./analytic_chain.md) §3,
§6 point 1). A finite SDF duration $\delta t$ acts *while* the mode
rotates. Magnus expansion of the finite-duration SDF generator
(motion $H_0=\omega_m a^\dagger a$ active during $\delta t$):

- **Leading, 𝒪(δt/T_m):** the displacement direction rotates by the
  motional phase swept during the pulse, contributing a net carrier
  phase $\tfrac12\omega_m\delta t$. **This is exactly the documented
  `shift_deg`** $=\omega_m\delta t/2$ used (and validated bit-exact)
  in D4 Layer A. So the leading finite-duration term is *not* an
  uncontrolled error — it is a pure, already-absorbed displacement
  phase. (This identifies the long-unlabelled `[TBD]` term.)
- **Next, 𝒪((δt/T_m)²):** the Magnus second-order
  $[\,\cdot\,,\,\cdot\,]$ of the finite-duration force with the free
  rotation yields a small **quadrature-asymmetric (squeezing-type)**
  area term — *not* removable by a phase. Magnitude at the WP-E
  $\delta t=0.13\,T_m$: $(\delta t/T_m)^2\approx1.7\times10^{-2}$.

**Hierarchy placement (the closure).** For *displaced* states the
𝒪(δt/T_m) phase is absorbed by `shift_deg` and the 𝒪((δt/T_m)²)
squeezing-type residual is phase-symmetric-suppressed and negligible
— which is *why the v0.4 displaced-state results never needed it*.
For a **squeezed** target the 𝒪((δt/T_m)²)≈1.7 % term has the *same
operator character* (two-phonon, quadrature-dependent) as the η²≈16 %
native term (§5) and the App. E 2ω_m channel (§4); it therefore must
be carried as a **sub-dominant but same-symmetry correction**, not
dropped. Ordering at the pinned parameters:

$$
  \underbrace{\eta^2\approx16\%}_{\text{native two-phonon, §5}}
  \;>\;
  \underbrace{(\delta t/T_m)^2\approx1.7\%}_{\text{finite-duration two-phonon, §6}}
  \;\gg\;
  \underbrace{\mathcal O(\eta^3),\,\mathcal O((\delta t/T_m)^3)}_{\text{dropped}}.
$$

The 𝒪(δt/T_m) phase term remains exactly absorbed (not dropped) via
`shift_deg`. This resolves D1 §6 point 4 / WORK-PROGRAM §Analytical
bullet 5.

## 7. Proposed D1 §6 approximation-hierarchy rewrite

Replace the open `[TBD]` in [`analytic_chain.md`](./analytic_chain.md)
§6 point 4 with (proposed; applied only on lock):

> 4. **Native-engine departure.** (a) *LD order:* the first-order
>    term is single-phonon (displacement); the 𝒪(η²) $X^2\sigma_\varphi$
>    term is two-phonon (squeezing-type), relative size $\eta^2$
>    (≈16 % at η=0.397) — negligible for displaced-state χ readout
>    (ideal leg η-exact, §2 of the η² scope) but the dominant
>    structural residual for squeezed inputs. (b) *Pulse duration:*
>    the leading 𝒪(δt/T_m) effect is a pure displacement phase
>    $\omega_m\delta t/2$, exactly absorbed by the D4 `shift_deg`;
>    the residual is 𝒪((δt/T_m)²)≈1.7 % at δt=0.13 T_m, two-phonon
>    in character, sub-dominant to (a). Both are quantified, never
>    assumed; see [`squeezed_eta2_scope.md`](./squeezed_eta2_scope.md).

A one-line forward pointer is also proposed for §6 point 1 (ideal-SDF
instantaneity) → §6.4(b).

## 8. Proposed decisions (the locks the user confirms before any code)

Each is determined by §1–§7; none is acted on until the user locks
this note (the `back_action_scope.md` discipline).

- **D-1 — Test state.** Ideal squeezed vacuum, $r=0.5$, squeeze
  angle $\theta=0$ (squeezed quadrature on the real β-axis, so the
  anisotropy aligns with the existing Cartesian grid; the
  matched-control "no input phase shift either leg" rule of
  `back_action_scope.md` §4a is retained). A second angle
  $\theta=\pi/2$ is a *reported, non-gated* anisotropy-orientation
  control.
- **D-2 — Ideal leg uses the v0.4 chain unchanged.** §2: the
  ideal-SDF χ readout + FFT is η-exact for squeezed vacuum. The
  squeezed run reuses `run_reconstruction_demo.py`'s ideal path
  verbatim with the closed-form χ of §3 added to `_common.chi_*`;
  P0/P1 are not re-derived.
- **D-3 — Reconstruction grid.** Keep the validated v0.2 Cartesian
  grid + $[-3,3]$ Wigner window; §3 shows $e^{+r}\!\approx\!1.65$ at
  $r=0.5$ is inside reach. A runtime assertion that the anti-squeezed
  χ support is within $B=N\beta_0$ is the only new guard (no grid
  escalation — explicitly *unlike* GKP).
- **D-4 — Squeezing comb defined, not yet executed.** The
  $\xi_\text{tot}=\xi_0e^{i\varphi}\mathcal D_N(\tilde x)$ map (§4) and
  the App. E $\Delta t=T_m/2$ timing are *recorded* for the native
  counterpart; the **native-engine 𝒪(η²) re-audit is the deferred
  follow-up** (§5) and is *out of scope for the first squeezed run*,
  which is ideal-leg reconstruction + the closed-form bridge sanity
  only.
- **D-5 — Gate.** One hard PASS/FAIL, analogue of P0/P1: ideal
  squeezed-vacuum reconstruction overlap fidelity vs. the §3
  closed-form χ at the §7#5 threshold tier for Gaussian states;
  $\max|\operatorname{Im}W|$ at the `complex128` floor. Everything
  native / η² / pulse-duration is *reported, not gated* (consistent
  with `back_action_scope.md` Decision 5 and the close-out bridge
  policy).
- **D-6 — Pulse-duration term.** Applied as the §7 D1 §6.4(b) text
  (doc) on lock; `shift_deg` already carries the 𝒪(δt/T_m) phase, so
  no runner change for the ideal leg.

## 9. Recommended execution plan (only on lock)

One clean commit each, WP-W discipline:

0. **Lock.** User confirms §8 → apply the §7 D1 §6 rewrite (doc-only
   commit; the analogue of the `cb850a5` scope promotion).
1. **χ helper + smoke test.** Add `_common.chi_squeezed(beta,r,θ)`
   (§3 closed form) + smoke test vs. (i) $r\!\to\!0$ → vacuum χ, (ii)
   the squeezed Wigner Gaussian via the existing `wigner_from_chi`,
   (iii) Hermiticity $\chi(-\beta)=\chi^*(\beta)$.
2. **Ideal squeezed-vacuum reconstruction.** Reuse the D3 ideal path;
   add $r=0.5$ ($\theta\in\{0,\pi/2\}$); the §8 D-5 gate; dated
   logbook (pre-reg → run → comparison) + commit. *(This is the
   whole first squeezed deliverable.)*
3. **(Deferred follow-up, separate scope/lock.)** Native-engine
   𝒪(η²) squeezing re-audit on the §4 $\xi_\text{tot}$ comb — its own
   pre-registered run when reopened.

-----

*Source of truth for conventions:
[`analytic_chain.md`](./analytic_chain.md) §1–§5 and WORK-PROGRAM
§Analytical / §7#3 / §7#4 (squeezed-vacuum carry-over) / §8. This
note adds no engine physics; it derives the 𝒪(η²) and δt/T_m
consequences and locks the squeezed-vacuum protocol decisions left
open at WP-W close-out. [Hasse24] App. E (Δt=2π/2ω_m squeezing
timing) and [FH20] (η=0.05 squeezed-state demonstration) are the
external precedents; the high-η stroboscopic adaptation and the
δt/T_m closure are derived here. PROPOSED — no code until §8 is
locked.*
