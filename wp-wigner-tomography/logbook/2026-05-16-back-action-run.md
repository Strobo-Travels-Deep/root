# Logbook — 2026-05-16 — back-action diagnostic (v0.6 execution)

**Status.** Run entry. WP-W follow-up Rank 1 executed end-to-end in
one session after the user locked
[`notes/back_action_scope.md`](../notes/back_action_scope.md):
4 `_common` helpers + 7 smoke tests, the vacuum analytic gate, the
`run_back_action.py` diagnostic sweep, and `plot_back_action.py`.
Scope §7 plan followed in order.

**Headline outcome.**

- **Vacuum analytic gate PASS at machine precision** — the only
  hard PASS/FAIL (back-action analogue of P0/P1). Purity and
  fidelity match the review-pass-corrected closed forms to
  $\le 2\times10^{-14}$; parity-form Wigner matches
  $W_\text{mixed-cat}(\beta_\text{tot}/2)$ to $\le 1.3\times10^{-10}$
  (nmax=60 Fock-truncation floor, **not** a defect).
- **Ideal-SDF σ_x branch fidelity = 1.0000 at every probe point**
  — the σ_x readout cleanly selects $D(\pm\beta_\text{tot}/2)|\psi_m\rangle$,
  confirming the branch picture. The native engine gives
  σ_x-branch $F\in[0.03,0.77]$ — it does **not** realise the SDF
  branch structure, quantifying the §7#3 structural bridge in the
  back-action observable for the first time.
- **Third bridge residual delivered**: the ideal-vs-native
  unconditional-Wigner $L^1$ (structural, matched-control), a
  diagnostic orthogonal to the spin-side §7#7 anchor.

-----

## 1. Pre-registered expectations & locked conventions

Logged *before* declaring (D4-Layer-A guardrail discipline). All
from the locked scope; the one choice the scope left symbolic is
recorded here explicitly:

- **Comb tooth k = 0 (carrier)** — chosen to match the established
  P1 / D3 / D4-Layer-B inverse-Dirichlet convention used throughout
  WP-W. *Consequence, pre-registered:* at the carrier tooth the
  monochromatic native engine performs a carrier spin rotation with
  weak motional coupling, so its back-action is small and the
  ideal-vs-native $L^1$ is dominated by "ideal displaces, native
  barely moves". This **is** the correct matched-control structural
  residual (§7#3: the native engine never realises $U_\text{SDF}$).
  The §8 native-prediction remark about collapse–revival is a
  *sideband* (k=1, JC) phenomenon; a k=1 variant is a documented
  future extension, **not** v0.6.
- **Matched physical control, not β_eff** (scope §4a). β_tot probe
  points defined on the ideal leg; native leg = D4-Layer-A pinned
  WP-E v0.9.1 train ($\eta{=}0.397$, $\Omega_r{=}0.09016606$,
  $\delta t{=}0.13\,T_m$, $N{=}30$) at the *same*
  $(\delta{-}k\omega_m,\varphi_\text{train},N)$.
- **Native state prep**: spin $|{\downarrow}\rangle$, **no separate
  MW π/2** (train accumulates π/2 via $\Omega_r$); motional input
  lab-frame ($\theta{=}0$). WP-E v0.9.1 `shift_deg` is
  phase-symmetric for vacuum/Fock (no-op) and logged for the cat.
  Reported, not gated — the unconditional $\rho_m^{(\rm post)}$ is
  readout-independent so this second-order phase convention does
  not move the headline.
- **Probe points**: peak $|\beta_\text{tot}|=N\beta_0=1.5$ (x=0);
  mid-branch $|\beta_\text{tot}|=N\beta_0/2=0.75$.
- **Inputs**: vacuum, Fock $|2\rangle$, cat $|\alpha|{=}1.5$ (pure).
- **GATE criterion (pre-set):** vacuum, ideal SDF, $|{+}y\rangle$:
  purity $=\tfrac12(1+e^{-|\beta_\text{tot}|^2})$,
  fidelity $=e^{-|\beta_\text{tot}|^2/4}$,
  $W=W_\text{mixed-cat}(\beta_\text{tot}/2)$, all $\le 10^{-6}$.
  Tolerance rationale: nmax=60 parity-form floor is $\lesssim4\times10^{-8}$;
  a convention/orientation bug (e.g. $\pi^{-1}$ vs $2/\pi$, or the
  transposed $\rho_m$) is $O(0.05$–$0.3)$ — $10^{-6}$ discriminates.

## 2. Execution

| artefact | path |
|---|---|
| helpers | [`numerics/_common.py`](../numerics/_common.py) (+`partial_trace_spin`, `conditional_motional_ket`, `wigner_from_rho`, `cat_ket`) |
| smoke tests | [`numerics/test_back_action_helpers.py`](../numerics/test_back_action_helpers.py) — **7/7 pass** |
| runner | [`numerics/run_back_action.py`](../numerics/run_back_action.py) → [`back_action.h5`](../numerics/back_action.h5) + manifest |
| figure | [`plots/plot_back_action.py`](../plots/plot_back_action.py) → [`plots/back_action.png`](../plots/back_action.png) |

Wall time: 116 s (parity-form Wigner on a $41^2$ grid at nmax=60
dominates; engine evolution is ms — as scope §4 anticipated).
Smoke-test lock 3 numerically confirms the **review-pass guardrail**:
the canonical $2/\pi$ parity form applied to the *mixed* ρ reproduces
`_common.W_mixed_cat`'s ½-folded $1/\pi$ closed form — neither is a
prefactor bug. The `partial_trace_spin` physical-orientation trap
(scope §5) is avoided and smoke-tested (lock 1).

## 3. Comparison — expectation vs observation

### 3.1 Vacuum gate (PASS, machine precision)

| point | $\lvert\beta_\text{tot}\rvert$ | purity vs $\tfrac12(1{+}e^{-\lvert\beta\rvert^2})$ | fidelity vs $e^{-\lvert\beta\rvert^2/4}$ | max$\lvert\Delta W\rvert$ |
|---|---|---|---|---|
| peak | 1.50 | $0.5526996123$ / $|\Delta|=6.7\times10^{-16}$ | $0.5697828247$ / $3.3\times10^{-16}$ | $1.3\times10^{-10}$ |
| mid  | 0.75 | $0.7848914124$ / $|\Delta|=2.0\times10^{-14}$ | $0.8688150563$ / $1.5\times10^{-14}$ | $2.4\times10^{-12}$ |

The corrected formulae are numerically confirmed
($0.5527=\tfrac12(1+e^{-2.25})$, $0.5698=e^{-0.5625}$). $\max|\operatorname{Im}W|\sim10^{-17}$
(Hermiticity preserved — no orientation/prefactor bug). This is the
back-action P0/P1: it validates the machinery before any
native-engine number is interpreted.

### 3.2 Diagnostic sweep (reported, not gated)

σ_x-branch fidelity (ideal leg) = **1.0000** for all
(state × point) — the SDF cleanly bisects into $D(\pm\beta_\text{tot}/2)$
branches. Native σ_x-branch $F$: vacuum 0.35/0.77, Fock 0.04/0.41,
cat 0.17/0.22 — structurally not an SDF (the §7#3 finding,
quantified).

Unconditional purity drop, fidelity-to-pre, and the structural
ideal-vs-native $L^1$ (peak / mid):

| input | ideal drop | native drop | ideal–native $W$ $L^1$ |
|---|---|---|---|
| vacuum | 0.447 / 0.215 | 0.066 / 0.030 | **0.813** / 0.251 |
| Fock $|2\rangle$ | 0.451 / 0.500 | 0.278 / 0.123 | **1.813** / 0.916 |
| cat $|1.5\rangle$ | 0.384 / 0.191 | 0.391 / 0.174 | **1.872** / 1.994 |

Observations: (i) the ideal SDF's back-action scales with
$|\beta_\text{tot}|$ (peak > mid) as the closed form predicts;
(ii) at the carrier tooth the native back-action is weak for
vacuum/Fock (small purity drop) but comparable-magnitude yet
*structurally different* for the cat (native $F_\text{pre}$ collapses
to 0.14–0.20 vs ideal 0.62–0.88 — the native JC-type coupling
shears the cat differently); (iii) Wigner-negativity is modified,
not destroyed, by both legs (Fock ideal neg $\approx-0.15$ to
$-0.23$, native $-0.27$ to $-0.33$). The $L^1$ column is the
**third bridge residual** — orthogonal to the spin-side §7#7
anchor, exactly the "cost-of-measurement" diagnostic Rank 1
targeted.

## 4. Convention notes / caveats

1. **k=0 carrier is a logged choice, not a scope omission.** The
   locked scope §4a pinned everything except the comb tooth; k=0
   matches all prior WP-W ideal-SDF work (P1/D3/D4-LayerB). The
   weak native carrier back-action is the *correct* structural
   result, not a runner defect. **k=1 sideband variant** (where the
   native JC collapse–revival of §8 would appear) is the natural
   next extension — recorded, not actioned (v0.6 scope is the
   locked minimal set).
2. **nmax=60 Fock-truncation floor** ($\lesssim4\times10^{-8}$ on
   the parity-form Wigner at the $|\alpha|\approx4.2$ box corner)
   is quoted with its regime attached, never as a bare gate —
   same discipline as P0's finite-grid windowing and the D4
   centroid-vs-$\Delta\alpha$ note.
3. **Native non-coherent state-prep `shift_deg`** is phase-symmetric
   for vacuum/Fock; for the cat the axis is on the real line and the
   shift is logged. Non-gated; does not affect the headline
   unconditional state.

## 5. Next-step decision

**WP-W v0.6 back-action delivered; re-park.** The locked scope is
fully executed: helpers + smoke tests, the hard vacuum gate (machine
precision), the diagnostic sweep, and the figure. Optional future
scope (none a blocker, all documented here and in scope §3 decision 2
/ §4a): (a) **k=1 sideband variant** to surface the native
collapse–revival back-action of §8; (b) the full §7#4 input set
(thermal forces density-matrix propagation); (c) Rank 2
squeezed-vacuum (needs the $\mathcal O(\eta^2)$ analytic extension
first, per the close-out logbook). No further action without a
specific follow-up decision.
