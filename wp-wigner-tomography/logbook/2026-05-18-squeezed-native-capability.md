# Logbook — 2026-05-18 — squeezed native-engine capability smoke (N-6)

**Status.** Run entry. The **critical first execution step** of the
native-engine 𝒪(η²) re-audit
([`squeezed_native_audit_scope.md`](../notes/squeezed_native_audit_scope.md)
§4 step 1, LOCKED `ba030c9`). Per N-6: *before any ideal-vs-native
residual is interpreted*, characterise the native post-train **vacuum**
state at the App. E two-phonon timing (Δt=T_m/2) as a full Gaussian
state, to discriminate a genuine 2ω_m squeezing channel from
first-order displacement leakage or heating/decoherence. **If the
channel is not cleanly engineered, that null is itself the headline
finding** (a sharpening of the parent §2 "structural, not a regime
limit" conclusion) — pre-registered, not worked around.

New artefact `squeezed_native_capability.{h5,manifest.json}`; no
parked artefact touched; ideal leg untouched.

-----

## 1. Pre-registered expectations (before the run)

- **Drive.** Native engine, pinned WP-E v0.9.1 params (η=0.397,
  Ω_r=0.09017, ω_m/2π=1.3 MHz, δt=0.13 T_m, no separate MW π/2),
  input |↓⟩⊗|0⟩. **App. E timing `t_sep_factor=0.5` (Δt=T_m/2)**,
  second-sideband two-phonon resonance **δ=2ω_m** (on-resonance peak
  x̃=0, φ_train=0). Reference row at `t_sep_factor=1.0` (non-App.-E,
  same δ) to show the timing is load-bearing.
- **Characterisation** vs N ∈ {10, 20, 30}: first moments ⟨X⟩,⟨P⟩;
  covariance eigenvalues λ_max/λ_min and ratio; principal-axis
  orientation; purity (X=a+a†, P=−i(a−a†); vacuum variance 1).
- **Pre-registered N-6 discriminator (the falsifiable call):**
  - **Squeezing channel present** ⟺ λ_max/λ_min−1 ≥ **0.10** at
    N=30, **growing with N**, with ⟨X⟩,⟨P⟩ ≈ 0 and purity ≈ 1
    (a clean unitary two-phonon squeeze).
  - **Displacement-dominated** ⟺ |⟨X⟩| or |⟨P⟩| grows with N and is
    comparable to / exceeds the squeezing scale (first-order
    single-phonon leakage wins).
  - **Heating/decoherence-dominated** ⟺ covariance grows
    ≈isotropically (ratio→1 with both λ rising) and **purity falls**
    with N.
- **Expectation (honest, not the gate).** η²≈0.16 is sizeable, so a
  *detectable* anisotropy is plausible — but the monochromatic engine
  has no bichromatic two-phonon term by construction
  ([`analytic_chain.md`](../notes/analytic_chain.md) §5), so
  off-resonant carrier/first-sideband contamination and the
  σ_φ-conditioned (branch) structure may dominate. **Either outcome
  is a publishable result**; the run reports whichever, with numbers.

## 2. Execution

```bash
python wp-wigner-tomography/numerics/squeezed_native_capability.py
python -m pytest wp-wigner-tomography/numerics/test_squeezed_native_helpers.py \
  wp-wigner-tomography/numerics/test_squeezed_helpers.py \
  wp-wigner-tomography/numerics/test_back_action_helpers.py -q
```

| artefact | path |
|---|---|
| runner | [`numerics/squeezed_native_capability.py`](../numerics/squeezed_native_capability.py) |
| helpers | [`numerics/_common.py`](../numerics/_common.py) `gaussian_moments`, `xi_tot_target_appE`, angle-general `parse_state` |
| data | [`numerics/squeezed_native_capability.h5`](../numerics/squeezed_native_capability.h5) + manifest |
| scope | [`notes/squeezed_native_audit_scope.md`](../notes/squeezed_native_audit_scope.md) §3 N-6 (LOCKED) |

Wall 0.1 s. Tests **22 passed** (7 native-audit helper + 8 squeezed +
8 back-action regression — unaffected). Code `0.7.0-capability`.

## 3. Results

Native post-train vacuum, Gaussian characterisation (X=a+a†,
P=−i(a−a†); vacuum variance 1):

| timing | N | ⟨X⟩ | ⟨P⟩ | λ_max | λ_min | ratio | orient° | purity |
|---|--|--|--|--|--|--|--|--|
| **App. E T/2** | 10 | −1.4e−3 | −3.3e−3 | 1.0032 | 0.9994 | **1.0037** | 158 | 0.99935 |
| **App. E T/2** | 20 | −2.5e−3 | −5.7e−3 | 1.0121 | 0.9992 | **1.0129** | 157 | 0.99722 |
| **App. E T/2** | 30 | −2.9e−3 | −6.7e−3 | 1.0251 | 1.0031 | **1.0219** | 156 | 0.99314 |
| ref T (non-App.E) | 10 | −1.8e−2 | −4.3e−2 | 1.0251 | 1.0005 | 1.0246 | 66 | 0.98782 |
| ref T (non-App.E) | 20 | −6.9e−2 | −1.6e−1 | 1.0739 | 1.0020 | 1.0718 | 66 | 0.96379 |
| ref T (non-App.E) | 30 | −1.4e−1 | −3.2e−1 | 1.0936 | 1.0046 | 1.0887 | 66 | 0.95304 |

## 4. Verdict (pre-registered discriminator) & next-step decision

**N-6 verdict: NO CLEAN 2ω_m SQUEEZING CHANNEL.** The classifier
returned `HEATING-DOMINATED`; the precise, honest reading:

- **The pre-registered "squeezing present" criterion is *not* met.**
  At the App. E timing the covariance anisotropy grows with N but
  only to **λ_max/λ_min−1 = 0.022 at N=30 — 5× below the
  pre-registered 0.10 threshold** — and it is *entangled with purity
  loss* (0.99935 → 0.99314), i.e. it is not a clean unitary squeeze.
- **Not displacement-dominated.** ⟨X⟩,⟨P⟩ stay ≈0 (~1e−3) at the
  App. E timing — δ=2ω_m correctly off-resonates the first-order
  single-phonon term, so the timing change *does* do something
  structural (the reference T row, by contrast, grows a clear
  displacement ⟨P⟩→−0.32 with worse purity 0.953).
- **The App. E timing suppresses displacement but does not convert
  that into squeezing.** The residual ~2 % anisotropy is weak and
  decoherence-coupled, not a coherent two-phonon squeeze.

**This is the pre-registered N-6 headline, not a workaround.** The
monochromatic Hasse-type Raman engine, at the pinned WP-E parameters,
**cannot cleanly engineer the bichromatic 2ω_m squeezing interaction**
even with the App. E timing — a *quantitative, native-level
sharpening* of the parent §2 / [`analytic_chain.md`](../notes/analytic_chain.md)
§5 conclusion that the ideal↔native bridge is **structural, not a
regime limit**. Until now that was an analytic argument (first-order
term is single-phonon); this is the first numerical demonstration at
the squeezing-channel level: the engine off-resonates the
displacement but yields only weak, decoherence-entangled anisotropy,
never a clean squeeze. For the eventual publication this is the
*strongest* outcome — it converts the η² thread from analytic-only
into a quantified native null that **strengthens the central
structural claim** (parent §5 anticipated exactly this).

**Next-step decision (scope §4).** N-6 has reported; per the locked
scope this null *is* the result. The full step-2 r×θ ideal-vs-native
residual run was predicated on a squeezing channel *to audit*; with
no clean channel its purpose shifts from "quantify the residual" to
"confirm the structural null is robust across (r, θ) and quantify how
far the native leg falls short." That is still a worthwhile single
publication figure, but it is now an **interpretation/scope fork for
the user**, not an automatic next run:

- **(a)** Proceed to a *reframed* step 2 — full (r,θ) grid, native
  vs the η-exact ideal leg, to show the failure is systematic (not a
  vacuum artefact) and bound its size. One more run + logbook.
- **(b)** Treat the N-6 null as sufficient evidence and go directly
  to step 3 (publication reassessment) with the structural-null as a
  headline result, leaving the (r,θ) sweep as future work.

No parked artefact touched; ideal leg untouched; the P-D ideal-leg
gate is not exercised here (it belongs to step 2). Awaiting the (a)/(b)
decision before any further runner work.
