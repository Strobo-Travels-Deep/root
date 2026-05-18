# WP-W — Paper outline (built against the locked claim scope)

**WP-W · publication outline · 2026-05-18**

**Status.** *Outline — not a draft.* Section-by-section structure,
abstract sketch, and figure list for the WP-W paper. It inherits
**exactly** [`publication_assessment.md`](./publication_assessment.md)
§8 (the locked claim contract) and §3/§6 (claims, figure→artefact
map). No new claims; every figure maps to an already-committed
artefact (no new runs). Honest framing is structural here, not
decorative: the paper is a *theory/numerics methods+characterisation*
contribution, framed as continuation of the group's own [Hasse24]
²⁵Mg⁺ programme, explicitly subordinate to [FH20] and [Hasse24].

**Target venue.** Phys. Rev. A (regular article) — primary; New
J. Phys. — alternative. *Not* PRL/PRX (no experiment; incremental on
two known papers). **Author line:** U. Warring *et al.* (provisional;
final list + the [Hasse24] author overlap to be set before
submission).

**Working title (no banned words; §8).**
*Characteristic-function tomography under a high-Lamb–Dicke
monochromatic stroboscopic drive: forward map, validated
reconstruction, and the native engine's quantitative departure from
the ideal SDF.*

-----

## Abstract (sketch — honest, subordinate)

> Direct characteristic-function (χ) tomography [FH20] reconstructs a
> motional state by 2D-Fourier-transforming $\langle D(\beta)\rangle$.
> [FH20] realised this on Ca⁺ with a *bichromatic* SDF at
> $\eta\!\approx\!0.05$; the [Hasse24] ²⁵Mg⁺ programme instead drives
> a *monochromatic* stroboscopic AC train at $\eta=0.40$, measuring
> position/momentum and outlining back-action and squeezed-state
> extensions. We adapt the χ-FFT framework to that monochromatic
> stroboscopic regime: an inverse-Dirichlet rule maps the physical
> $(\delta,\varphi_\text{train})$ scan onto FFT-ready Cartesian
> $\beta$ nodes, and we validate the full chain numerically at
> $\eta=0.40$ against analytic truth (machine-precision preflight
> gates; engine-vs-analytic χ residual $3.75\times10^{-4}$). We then
> *quantify* — where [Hasse24] gave qualitative or conceptual
> sketches — (i) the Wigner-resolved ideal-vs-native back-action
> across seven input states on the carrier and first sideband,
> exhibiting a tooth-robust quantum/classical discriminator, and
> (ii) the $\mathcal O(\eta^2)$ two-phonon (squeezing) channel: at
> the [Hasse24] App.-E timing the monochromatic engine does not
> cleanly engineer it — a gate-anchored, $(r,\theta)$-robust null,
> with the η-exact ideal reconstruction as reference. The work is
> numerical; it cites the [Hasse24] experiment as motivation, not as
> a demonstrated match.

(Banned-word check: no "first/novel/structural impossibility/not
previously stated"; "structural" used only engine-bounded.)

## §I. Introduction

- The χ-tomography lineage: [CG69]/[Wal95]/[LD97]/[Bertet02] →
  **[FH20]** (the direct trapped-ion precedent: χ → 2D-FFT → W,
  incl. squeezed/squeezed-cat/GKP, Ca⁺, η≈0.05, *bichromatic* SDF).
- The Freiburg ²⁵Mg⁺ programme: **[Hasse24]** — the *monochromatic*
  stroboscopic AC-train protocol, the Hamiltonian, the 2D
  $(\varphi,\vartheta_0)$ scan, position/momentum readout,
  back-action (App. D) and squeezed-state (App. E) outlines.
  **State plainly:** this paper continues that programme.
- The gap this paper fills (claims §3 1–4), each one sentence,
  each subordinated. Explicitly: *not* a new framework (FH20),
  *not* the protocol (Hasse24), *not* first back-action/squeezing
  (Hasse24 App. D/E) — the contribution is the stroboscopic-comb
  adaptation + the high-η *quantitative characterisation*.
- One paragraph owning the scope: numerical study; engine and bridge
  are simulations; experiment is [Hasse24]'s.

## §II. Protocol and the inverse-Dirichlet forward map  *(claim 1)*

- The monochromatic engine Hamiltonian ([Hasse24] C1 = `scripts/stroboscopic`).
- The σ_x-SDF/|+y⟩ direct-χ readout chain (analytic_chain.md §1–§2);
  the v0.5 convention locks (σ_x not σ_z; no $e^{-|\beta|^2/2}$).
- **The contribution:** the Dirichlet kernel $\mathcal D_N$ and the
  inverse-Dirichlet Cartesian targeting (§2 / analytic_chain.md §3),
  turning Hasse's polar scan into FFT-ready Cartesian $\beta$ — the
  stroboscopic-monochromatic-specific piece absent from [FH20] (CW)
  and [Hasse24] (no χ frame).
- **Fig 1** = forward-map schematic + reach ladder (`reach_ladder_ideal.h5`, D2).

## §III. Validated reconstruction at η = 0.40  *(claim 2)*

- Preflight gates P0 (analytic χ→FFT, machine precision) and P1
  (engine χ vs analytic, ~1e−14).
- D3 reconstruction of the seven §7#4 states; the quantum/classical
  mixed-cat control (no invented fringes).
- D4 ideal↔native bridge: Layer A bit-exact to the WP-E reference
  scan; Layer B engine-vs-analytic χ $=3.75\times10^{-4}$ over 6481
  nodes (FFT-centroid reported only with its Δα pixel size — never a
  bare gate).
- The η²≈16 % approximation hierarchy (analytic_chain.md §6;
  ideal-limit-principles.md) — frame as the *known regime issue*
  this high-η validation addresses, not a discovery.
- **Fig 2** = reconstruction gallery + F/L¹ table
  (`reconstruction_demo.h5`); **Fig 3** = the D4 bridge
  (`bridge_inversion.h5`).

## §IV. Quantitative ideal-vs-native back-action  *(claim 3)*

- [Hasse24] App. D/Fig 6b gave $\delta\langle n\rangle$
  *qualitatively* — state this up front.
- The matched-physical-control discipline (no $\beta_\text{eff}$;
  back_action_scope.md §4a) and the single hard gate (vacuum analytic
  anchor, machine precision, tooth-independent).
- Result: Wigner-resolved ideal-vs-native residual across the full
  §7#4 set, carrier (k=0) and first sideband (k=1); the
  **tooth-robust quantum/classical discriminator** (pure-cat L¹ 1.87
  > mixed-cat 1.47); sideband signature concentrated in the
  conditional channel.
- **Fig 4** = ideal-vs-native W panels + discriminator, k=0/k=1
  (`back_action_full.h5`, `back_action_k1_full.h5`).

## §V. The native 𝒪(η²) squeezing-channel result  *(claim 4)*

- [Hasse24] App. E gave the squeezed-state *concept* + the
  Δt=2π/2ω_m timing — state up front; we re-derive that timing as
  the §3 Dirichlet map at the 2ω_m fundamental (squeezed_eta2_scope.md
  §4), and close the long-open δt/T_m order.
- The ideal-SDF χ chain is **η-exact** for squeezed vacuum (the
  P-D gate: bit-for-bit vs the η-exact reconstruction).
- Result: at the App.-E timing the monochromatic engine does **not**
  cleanly engineer the 2ω_m two-phonon channel — N-6 vacuum null
  (anisotropy ≈2 %, purity-coupled) generalised to a
  $(r,\theta)$-robust systematic null (fidelity-to-input
  0.996→0.93→0.76); engine adds ~no squeezing, the post-train
  ratio ≈ the *input* ratio (pass-through, not engineered).
- **Engine-specific, not universal:** [FH20]'s bichromatic SDF
  *does* realise the squeezing chain — restate the §8 bound here.
- **Fig 5** = P-D η-exact reconstruction + native null vs (r,θ)
  (`squeezed_recon.h5`, `squeezed_native_audit.h5`). *(Strongest
  figure: the two-part ideal-sound / native-fails structure.)*

## §VI. Discussion

- What this means for the [Hasse24] platform: a precise, quantified
  map of where the monochromatic stroboscopic drive departs from the
  ideal FH20 SDF, and the 𝒪(η²) squeezing ceiling — useful to anyone
  planning high-η stroboscopic CF-tomography/squeezing.
- Limits, stated honestly: numerical only; grid-resolution caveats
  (GKP deferred, D4 centroid sub-pixel — carry Δα); the result is
  engine-specific.
- Relation to WP-TOM (saturated-regime template matching) — the
  perturbative/saturated bridge as outlook, not a claim.

## §VII. Conclusion & outlook

- Recap claims 1–4 in subordinate language.
- Outlook: bichromatic realisation (FH20-style) on the Mg⁺ platform;
  the WP-TOM bridge; GKP at finer grid; an experimental test against
  [Hasse24]-class data.

## Appendices / Supplementary

- A: the analytic chain (`analytic_chain.md`) + convention locks.
- B: the 𝒪(η²)/δt derivation (`squeezed_eta2_scope.md`); the App.-E
  timing re-derivation; the pulse-duration order closure.
- C: pre-registration logbooks + reproducibility manifests
  (the numerical-WP discipline, §5a) — a methods-paper strength.
- D: the native-audit scope + the N-6 capability smoke
  (`squeezed_native_audit_scope.md`; the honest null methodology).

## Drafting risk-controls (carried from the memo)

- **R-1/R-5:** lead each results section with *data*; never a
  conceptual-novelty sentence. The contribution noun is
  "characterisation/adaptation", not "finding".
- **R-2:** §I and §VI each carry one explicit no-experiment sentence;
  [Hasse24] experiment cited as motivation/consistency only.
- **R-3:** every Wigner-side number prints its Δα; D4 centroid never
  a bare gate.
- **R-4:** done (`605c212`); §8 banned-word check before submission.
- Fix the non-gating runner aggregate-print confound (logged in
  `3f9f7dd`) **before** any number is quoted from that runner into a
  figure/table — to avoid accidental misquotation.

-----

*Built against [`publication_assessment.md`](./publication_assessment.md)
§8 (locked claim contract), §3 (claims), §6 (figure→artefact map).
No new claims; no new runs. This is an outline; a draft is the next
artifact, on explicit direction, against this structure.*
