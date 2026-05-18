# WP-W — Publication feasibility assessment

**WP-W · publication deliberation · 2026-05-18**

**Status.** *Decision-support memo — not a paper draft.* Records the
resolved novelty-gate verdict, the re-spined contribution, the
prerequisite corrections, venue analysis, a figure→artefact map, and
the referee-risk register. Output of the user-directed sequence:
deliberate → strengthen the science (native 𝒪(η²) re-audit,
`1ad9c4b`/`3f9f7dd`) → resolve the novelty gate → this memo. It makes
no edits to the WP doc or code; it states what *must* be done before
any drafting and what the honest paper can and cannot claim.

Evidence base: `refs/extractions/FH20.md`, `refs/extractions/Hasse24.md`,
[`../../ideal-limit-principles.md`](../../ideal-limit-principles.md),
the sibling-WP sweep (wp-hasse-reproduction / wp-phase-contrast-maps /
wp-analysis-train-tomography), and the committed WP-W artefact chain
([`wpw_findings.md`](./wpw_findings.md)).

-----

## 1. Novelty-gate verdict

**CONDITIONAL GO.** A paper is feasible **only** as a narrowly-framed
theory/numerics *methods & characterization* paper, explicitly
subordinated to [FH20] and [Hasse24] as prior art. The
"structural-impossibility / not-previously-stated" framing is a
**NO** — it would not survive review and is contradicted by WP-W's
own lit-review.

**The decisive fact.** The project's own extractions already
adjudicated novelty and the WP doc overclaims relative to them:

- `WORK-PROGRAM.md` §1.3 (≈L286–291) asserts the structural-bridge
  finding "has not been stated previously in the literature."
- `refs/extractions/FH20.md` §7.2–7.3 overrules this: the ideal SDF
  "exists in real experiments — FH20's bichromatic protocol. **Not a
  structural impossibility, just a different drive**"; recommends
  "soften 'no limit recovers the ideal SDF' … Hasse-engine-specific,
  not universal."

A referee familiar with [FH20] makes the same objection
unprompted. **This internal inconsistency must be resolved before
drafting** (see §4 R-4 / §6).

## 2. Prior art (what is *not* novel — state plainly in the paper)

| Element | Prior art | Source |
|---|---|---|
| Direct χ-function tomography + 2D-FFT → W | **[FH20]** (Ca⁺, η≈0.05), incl. squeezed, squeezed-cat, **GKP** | FH20.md §3–4, §8 |
| The stroboscopic AC-train protocol, Hamiltonian, 2D (φ,ϑ₀) scan | **[Hasse24]** (²⁵Mg⁺, *experimental*) | Hasse24.md §2–3 |
| Back-action *concept* / δ⟨n⟩ map (qualitative) | **[Hasse24]** App. D / Fig 6b | Hasse24.md §4.4 |
| Squeezed-state extension *concept* + Δt=2π/2ω_m timing | **[Hasse24]** App. E / Fig 9 | Hasse24.md §4.5 |
| "𝒪(η²)≈16–20% matters at η≈0.4; quadrature selectivity lost" | established **internal** principle | ideal-limit-principles.md §1.2 |

The χ-tomography reframe, the protocol, the back-action idea, the
squeezed-timing, and even "η² matters" are all antecedent. WP-W is a
*reinterpretation + quantitative extension*, not a discovery.

## 3. The re-spined contribution (what the honest paper claims)

Working title direction: *"Characteristic-function tomography under a
high-Lamb–Dicke monochromatic stroboscopic drive: forward map,
validated reconstruction, and the native engine's structural
ceiling."*

Defensible novel residue (narrow, incremental, real):

1. **The inverse-Dirichlet Cartesian forward map** (§2): the
   stroboscopic-monochromatic-specific construction that turns
   Hasse24's polar (φ,ϑ₀) scan into FFT-ready Cartesian χ sampling —
   absent from [FH20] (CW bichromatic) and [Hasse24] (no χ frame).
   *This is the genuine theoretical contribution.*
2. **Validated reconstruction at η=0.40** (P0/P1/D2/D3/D4) — the
   chain works in the non-perturbative regime [FH20] (η≈0.05)
   sidesteps, with the η²≈16 % deviation hierarchy made explicit.
3. **Quantitative, Wigner-resolved ideal-vs-native back-action map**
   across the full §7#4 set, carrier + first sideband, with a
   tooth-robust quantum/classical discriminator — vs [Hasse24]'s
   *qualitative* δ⟨n⟩.
4. **The native 𝒪(η²) squeezing-channel null** (N-6 + the (r,θ)
   re-audit, P-D-gated): the monochromatic engine does not cleanly
   engineer the 2ω_m two-phonon channel — a quantitative platform
   boundary where [Hasse24] App. E gave only the ideal-timing
   concept. *The science-strengthening step delivered this.*

**Honest one-line:** *the precise, quantified map of where and by how
much a high-η monochromatic stroboscopic drive departs from the ideal
FH20 SDF — including the 𝒪(η²) squeezing ceiling — built on, and
explicitly crediting, the [Hasse24] protocol and the [FH20]
framework.*

## 4. Referee-risk register

- **R-1 Novelty (high).** Even re-spined, (1)–(4) are
  adaptation/characterization, not discovery. *Mitigation:* pitch
  squarely as a methods/characterization paper; lead with the
  quantitative back-action + squeezing-null *data*, not a conceptual
  claim; never use "first/structural-impossibility."
- **R-2 No experimental anchor (high).** Theory/numerics only; the
  "native engine" is itself a simulation; D4 Layer A is bit-exact to
  a *sibling simulation* (WP-E), and `wp-hasse-reproduction`
  validates only Hasse's *numerical* figures (Fig 6/8 — the
  experimental Fig 7 is explicitly out of scope). *Mitigation:* own
  it; cite [Hasse24]'s experimental data as motivation and the
  same-Hamiltonian consistency, **without** claiming a demonstrated
  experimental match (it is by-construction, not validated).
- **R-3 Grid-resolution caveats (medium).** D4 Layer B FFT centroid,
  GKP deferral. *Mitigation:* the WP already reports Wigner-side
  numbers with Δα attached and never as bare gates — keep that
  discipline in the paper.
- **R-4 Internal overclaim (blocking until fixed).**
  `WORK-PROGRAM.md` §1.3/§7#3 contradicts `FH20.md`/`Hasse24.md`. A
  reviewer reading the repo — or just knowing [FH20] — sees it. Must
  be reconciled (soften §7#3 to engine-specific; drop "not
  previously stated"; credit FH20/Hasse24) **before** submission.
- **R-5 "η² matters" is pre-established (low/medium).**
  ideal-limit-principles.md already states it. *Mitigation:* the
  contribution is the *quantitative native null*, not the
  observation that η² is non-negligible — frame accordingly.

## 5. Positioning note (decision-relevant)

The repo metadata (git author `uwarring`, `u.j.warring@gmail.com`)
indicates the WP-W author overlaps the **[Hasse24] author set**
(F. Hasse, D. Palani, R. Thomm, **U. Warring**, T. Schaetz). If so,
the correct and lowest-risk framing is **deliberate continuation of
the group's own ²⁵Mg⁺ stroboscopic programme** — a theory/numerics
companion to Hasse24 — not novelty competition with prior art. This
*de-risks* R-1 substantially (extending one's own protocol with a
quantitative-characterization follow-up is a standard, publishable
mode) but does **not** waive the [FH20] citation/credit obligation or
the R-4 fix. Confirm the author set before framing.

## 6. Venue & figure map

**Realistic venue:** Phys. Rev. A (regular article) or New J. Phys. —
a solid methods/characterization paper. **Not** PRL/PRX/high-impact
(no experiment; incremental on two known papers). Quantum is possible
if the framing leans methods.

Figure → committed artefact (all exist; no new runs needed):

| fig | content | artefact |
|---|---|---|
| 1 | Forward map / inverse-Dirichlet schematic + reach ladder | D2 `reach_ladder_ideal.h5` |
| 2 | Reconstruction gallery (7 §7#4 states), F/L¹ table | D3 `reconstruction_demo.h5` |
| 3 | Ideal↔native bridge: Layer A bit-exact, Layer B χ residual | D4 `bridge_inversion.h5` |
| 4 | Back-action: ideal-vs-native W panels, q/c discriminator, k=0/k=1 | `back_action_full.h5`, `back_action_k1_full.h5` |
| 5 | Squeezed: η-exact reconstruction (P-D) + native 𝒪(η²) null vs (r,θ) | `squeezed_recon.h5`, `squeezed_native_audit.h5` |

Supplementary: P0/P1 gates, convention table, the analytic chain
(`analytic_chain.md`), the 𝒪(η²)/δt derivation
(`squeezed_eta2_scope.md`).

## 7. Prerequisites before any drafting (ordered)

1. **Fix R-4** — ✅ done (`605c212`): `WORK-PROGRAM.md` §1.3 item 3
   re-cast as engine-specific quantitative characterisation;
   "not previously stated" removed; forward-facing framing-discipline
   note added. §7#3 was already engine-bounded.
2. **Author set / program-continuation framing** — ✅ confirmed
   (user, 2026-05-18): **U. Warring et al. (provisional)**;
   program-continuation of the group's own [Hasse24] ²⁵Mg⁺
   programme. Positioning aid only — does **not** waive [FH20]/[Hasse24]
   credit (§5).
3. **Claim-scope lock** — ✅ done (§8 below): `wpw_findings.md` §6
   de-grandiosed + engine-bounded; sweep of forward-facing docs
   confirmed no other residual overclaim (the "out-of-scope/not
   claimed" disclaimer list and the corrected "not first
   characterisation" text are honest and stay).
4. **Outline/draft** — ✅ cleared to proceed →
   [`publication_outline.md`](./publication_outline.md).

No new science is required — the artefact chain is complete and the
η² thread is quantified. The gating work is *framing honesty and the
R-4 correction*, not more runs.

## 8. Locked claim scope (prereq 3 — the single reference for any draft)

Any outline, abstract, or draft inherits **exactly** this and nothing
broader:

- **Claims = §3 (1)–(4) only:** (1) the inverse-Dirichlet Cartesian
  forward map; (2) validated reconstruction at η=0.40; (3) the
  *quantitative* Wigner-resolved ideal-vs-native back-action map
  (carrier + first sideband, quantum/classical discriminator);
  (4) the native 𝒪(η²) two-phonon squeezing-channel null
  (N-6 + (r,θ) re-audit, P-D-gated). Nothing else is a claim.
- **Subordination (mandatory in every framing):** χ-FFT tomography =
  [FH20]; the stroboscopic protocol, the back-action concept (App. D),
  and the squeezed-state concept + Δt=2π/2ω_m timing (App. E) =
  [Hasse24]. WP-W = *reinterpretation + quantitative
  characterisation*, framed as continuation of the group's own
  [Hasse24] programme.
- **Banned in all external-facing text:** "first",
  "first characterisation", "structural impossibility",
  "not previously stated", "novel/novelty" as a headline, and any
  *unbounded* "structural, not a regime limit" (always carry the
  *engine-specific* qualifier + the [FH20]-bichromatic-realises-it
  credit).
- **No-experiment honesty:** theory/numerics; the native engine and
  the D4 bridge are simulations; [Hasse24]'s experiment is cited as
  motivation/consistency, never as a demonstrated experimental match.
- **Author line for drafts:** "U. Warring *et al.* (provisional)" —
  final list TBD; does not change the [FH20]/[Hasse24] credit.

This §8 is the contract; the outline (§7.4) is built against it.

-----

*Source of truth: `refs/extractions/{FH20,Hasse24}.md` and
`refs/contextual-notes.md` for prior-art adjudication;
[`wpw_findings.md`](./wpw_findings.md) for the artefact chain;
[`../../ideal-limit-principles.md`](../../ideal-limit-principles.md)
for the established η² deviation principle. This memo is
decision-support; it asserts no new results and authorises no code or
WP-doc edits — those are the §7 prerequisites, to be done on explicit
user direction.*
