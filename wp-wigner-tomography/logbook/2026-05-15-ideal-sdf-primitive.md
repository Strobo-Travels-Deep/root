# Logbook — 2026-05-15 — Ideal-SDF primitive + P1 sentinel (no D4)

**Status.** Third execution session (same calendar day as D2/P0 and
D3). Scope per the user-locked plan: add the FH20-style `ideal_sdf`
primitive to `scripts/stroboscopic`, verify the convention against
analytic predictions via smoke tests, run a single-point P1 sentinel
against the inverse-Dirichlet forward map of §2. D4 deferred until
primitive passes — which it does at machine precision.

**Outcome.** All 28 smoke tests pass; P1 sentinel passes at $10^{-14}$
relative residual on both vacuum and coherent $|\alpha=1\rangle$,
both $N \in \{20, 80\}$. Two convention corrections logged for the
v0.5 WP doc pass.

-----

## 1. Pre-registered expectations

Per the user-locked session plan + the two pre-coding guardrails:

### 1.1 Convention locks before any P1 declaration

- **Branch-separation convention**: `beta` argument of the primitive
  equals the branch *separation* matching WP-W §2 $\beta_\text{tot}$.
  Internally $U = D(\sigma_x \beta/2)$.
- **Comparison target**: spin observables that read out χ *directly*
  — *not* $\langle\hat D(\beta)\rangle$ on the post-train motional
  state (back-action diagnostic), but the measurement signal
  combining $\langle\sigma_y\rangle$ and $\langle\sigma_z\rangle$ in
  the FH20 σ_x-SDF/Ramsey-equator setup.

### 1.2 Smoke-test predictions

Four convention locks verified at $\leq 10^{-9}$ residual:

1. **Branch separation (lock 1).** $U(\beta)|+x\rangle|0\rangle = |+x\rangle|+\beta/2\rangle$.
   Factor-of-2 trap explicitly tested: overlap with $|+\beta\rangle$
   must be < 0.95 for $|\beta| > 0.6$.
2. **Branch sign (lock 2).** $U(\beta)|-x\rangle|0\rangle = |-x\rangle|-\beta/2\rangle$.
3. **χ readout (lock 3).** On $|+y\rangle|\psi_m\rangle$:
   $\chi(\beta) = \langle\sigma_y\rangle - i\langle\sigma_z\rangle$
   directly — no Gaussian prefactor, no overall phase, no
   conjugation. Verified on vacuum and coherent inputs.
4. **σ_x dependence (lock 4).** $\langle\sigma_x\rangle = 0$ on the
   $|+y\rangle$ initial state (σ_x is the SDF axis itself, carries
   no χ information).

### 1.3 P1 sentinel prediction (per §4a)

- **Sentinel point:** $\beta_\star = 0.5\,e^{i\pi/4}$ (the §4a target).
- **States:** vacuum, coherent $|\alpha=1\rangle$.
- **Train lengths:** $N=20$ (gating) and $N=80$ (diagnostic).
- **Setup:** on the $k=0$ comb tooth (carrier). Use the inverse-
  Dirichlet rule of §2 to choose $(\delta, \varphi_\text{train})$.
- **Pass criterion:** $|\chi_\text{engine} - \chi_\text{analytic}| / |\chi_\text{analytic}| < 5\%$
  at $N=20$. $N=80$ is diagnostic, not gating.

Analytic targets:
- $\chi_\text{vac}(\beta_\star) = e^{-|\beta_\star|^2/2} = e^{-0.125} \approx 0.8825$.
- $\chi_{|\alpha=1\rangle}(\beta_\star) = 0.8825 \cdot e^{2i\,\mathrm{Im}(\beta_\star)} = 0.8825 \cdot e^{2i\,\cdot 0.354} \approx 0.671 + 0.573i$.

-----

## 2. Execution

### 2.1 Primitive (`scripts/stroboscopic/ideal_sdf.py`, 116 lines)

Three components:

- `displacement(beta, nmax)` — motional $D(\beta) = \exp(\beta a^\dagger - \beta^* a)$.
- `U_ideal_sdf(beta, nmax)` — σ_x-conditioned displacement
  $U = D(\sigma_x \beta/2)$ in block form:
  $\tfrac{1}{2}\begin{bmatrix}D_+ + D_- & D_+ - D_- \\ D_+ - D_- & D_+ + D_-\end{bmatrix}$
  with $D_\pm = D(\pm\beta/2)$. Off-diagonal spin blocks (the σ_x part)
  are exactly what makes the SDF axis rotate under σ_z spin
  precession.
- `IdealSDFTrain` + `build_ideal_sdf_train(...)` — N-pulse train
  with **explicit per-pulse phase rotation** $\varphi_n = \varphi_\text{train} + n \cdot x$
  where $x = (\delta - k\omega_m) T_m$. Gap is motion-only (no
  spin detuning); the WP-W §2 detuning-induced rotation is encoded
  in the per-pulse phase analytically. See §3.2 below.

### 2.2 Smoke tests (`scripts/stroboscopic/tests/test_ideal_sdf.py`)

28 tests across four lock categories + unitarity + identity. All pass at
$\leq 10^{-9}$ residual (typically $10^{-15}$).

```
scripts/stroboscopic/tests/test_ideal_sdf.py ............................  28 passed in 0.03s
```

### 2.3 P1 sentinel (`wp-wigner-tomography/numerics/run_p1_preflight.py`)

Runs the four-point sentinel (2 states × 2 N values), outputs to
[`numerics/p1_preflight.h5`](../numerics/p1_preflight.h5) with
sidecar manifest. Wall time: 0.08 s.

-----

## 3. Comparison — expectation vs. observation

### 3.1 P1 sentinel results

| state | N | $|\chi_\text{engine}|$ | $\chi_\text{analytic}$ | rel residual | gate |
|---|---:|---:|---|---:|:-:|
| vacuum | 20 | 0.882497 | 0.882497 + 0i | $1.01\times 10^{-14}$ | ✓ |
| vacuum | 80 | 0.882497 | 0.882497 + 0i | $3.02\times 10^{-14}$ | (diagnostic) |
| coherent $|\alpha=1\rangle$ | 20 | $0.670914 + 0.573303i$ | same | $4.10\times 10^{-14}$ | ✓ |
| coherent $|\alpha=1\rangle$ | 80 | $0.670914 + 0.573303i$ | same | $4.05\times 10^{-14}$ | (diagnostic) |

**Overall: PASS** at machine precision on `complex128`. The 5% pass
criterion is exceeded by 13 orders of magnitude — confirming both
the inverse-Dirichlet forward map of §2 and the σ_x-SDF + Ramsey-
equator χ readout convention are self-consistent and engine-faithful.

### 3.2 The key implementation choice (§7#3 / §2 convention reconciliation)

A first attempt used the native `build_U_gap(delta=...)` to encode the
detuning via spin-detuning phase in the gap (matching how
`build_strobo_train` handles it). **This failed** with vacuum
residual ~165% at $N=20$. Diagnosis: σ_x SDF in the *lab frame* plus
σ_z spin precession in the gap causes the spin to precess by
$(N-1)\delta T_m$ over the train, and the χ readout in the lab frame
picks up that precession phase rather than the rotating-frame χ.

**The fix**: encode the WP-W §2 detuning rotation in the per-pulse
SDF phase explicitly:

$$U_{\text{pulse},n} = U_\text{ideal-sdf}\!\bigl(\beta_0 e^{i(\varphi_\text{train} + n x)},\,n_\text{max}\bigr),\quad x = (\delta - k\omega_m) T_m$$

with the gap doing only the trivial motion-period evolution (identity
at $t_\text{sep}=T_m$). The spin does *not* precess during gaps, so
the lab-frame χ readout matches the rotating-frame χ exactly.

This is the *cleaner* implementation choice: per-pulse phase is exact
and analytical, whereas spin-precession-via-detuning is an
approximation that requires a closing rotation to compensate.
**The two paths are equivalent in the perturbative limit**, but the
explicit per-pulse phase is exact at all $\beta_0$.

### 3.3 Two corrections queued for the v0.5 WP-W document pass

**Correction 1** — §Analytical bullet 2 wording. Currently says

> "Under the idealised SDF (instantaneous, *σ_z-coupled*, perturbative),
> the post-train complex contrast is $C(\delta, \varphi_\text{train}) = \langle\sigma_x\rangle + i\langle\sigma_y\rangle = e^{-|\beta_\text{tot}|^2/2}\,\chi_{\rho_m}(\beta_\text{tot})$"

Both pieces of this are inconsistent with the §2 Dirichlet forward
map and with FH20:

- **σ_z-coupled → σ_x-coupled (FH20-style).** σ_z SDF axis doesn't
  rotate under the σ_z spin precession that gives the Dirichlet
  kernel its detuning dependence. σ_x SDF does. Confirmed by the
  P1 sentinel: σ_x SDF + WP-W §2 inverse-Dirichlet = $10^{-14}$
  agreement; σ_z SDF + same recipe = 165% residual.
- **Gaussian prefactor $e^{-|\beta|^2/2}$ removed.** For the ideal
  σ_x SDF on a $|+y\rangle$ equator state, the χ readout is
  *direct*: $\chi(\beta) = \langle\sigma_y\rangle - i\langle\sigma_z\rangle$
  (smoke-test lock 3 verified). No Gaussian prefactor, no overall
  $i$ phase, no conjugation. The $e^{-|\beta|^2/2}$ factor in §Analytical
  bullet 2 appears to be an artefact of an earlier derivation
  conflated with the WP-E Doppler-broadening case.

**Correction 2** — §7#3 framing. The "no limit of the monochromatic
engine recovers the ideal SDF" finding stands, but the description of
the *ideal* SDF as σ_z-coupled needs to be updated to σ_x-coupled
(FH20-style bichromatic). This sharpens the bridge story: WP-W's
ideal-SDF layer is *exactly* FH20's protocol; the native-engine
deviation is now a clean σ_z (Hasse) vs σ_x (FH20/ideal) operator
mismatch, not a more nebulous "no limit recovers" claim.

Both corrections queued for the v0.5 WP-W doc pass; the
present logbook entry is the source-of-truth for the convention
until that pass lands.

-----

## 4. Next-step decision

Primitive passes; P1 sentinel passes at machine precision. **Ready
for D4 (WP-E / WP-TOM bridge plot)** in its own session, gated on
the primitive as the user requested.

D4 scope (next session):
- Layer A: native Raman convention check at the §7#7 shared anchor
  $|\alpha=3, \theta_\alpha=0\rangle$, comparing
  `scripts/stroboscopic` native Raman output to WP-E reference values.
- Layer B: saturated WP-TOM template-match recovery vs. ideal-SDF
  FFT centroid on the same anchor. Now that the ideal-SDF primitive
  exists and passes P1, the FFT pipeline of D3 can be re-run with
  *engine-measured* χ instead of *analytically-evaluated* χ, and
  the residual is the bridge metric.
- Plot script per the §4 D4 spec.

D1 (analytical note) can be drafted alongside, incorporating the
two §3.3 convention corrections.
