# Logbook — 2026-04-13 — Architect-stance note: WP-E renaming before v0.4

**[Stance: Architect]** — the design question Guardian raised twice and
the v0.3 framing cannot carry unchanged into v0.4.

## The question

Should WP-E, currently titled **"Forward Map and Observability: Phase
and Contrast Maps of the Stroboscopic Analysis Pulse"**, be renamed
before v0.4 lands?

Guardian noted in the R2 review:

> *"The original 'Forward Map and Observability' framing presumed a
> three-axis forward map with nontrivial structure in each axis. The
> actual finding is that the map factorises (|C| is one-dimensional in
> δ₀; arg C carries all the (|α|, φ_α) information on the unit circle
> via a closed-form identity) and that the R2 'alternative forward
> map' is a theoretical sideline."*

And in the S2 falsification review:

> *"There is a version of v0.4 in which WP-E is no longer 'Forward Map
> and Observability' but rather 'The Position-Phase Channel of
> Stroboscopic Analysis' — a tighter, more specific object."*

The question has been deferred twice. It must be resolved before v0.4
drafting, not after.

## Architect reading

Four things have happened since v0.3:

1. **Preflight.** Closed motivation 3 at the data-artefact level (HDF5
   synthetic, JSON legacy = engine). No physics residual.
2. **S1 + R1.** Confirmed |C|(δ_0) is α-independent at the carrier and
   showed position-phase (arg C) tracks k_eff · ⟨x⟩ linearly in R1.
3. **S2 falsification + expansion.** Matrix-element-magnitude theorem:
   |C|(δ_0, |α|, φ_α) is φ_α-independent to machine precision.
   arg C(δ_0 = 0, |α|, φ_α) = 90° + 2η|α|·cos φ_α exactly (10⁻¹¹ deg
   residual) in both engines.
4. **H1 + R2.** Lock tolerance is |α|-dependent (FWHM 3.3 % in ε at
   |α| = 3). R2 reveals a frame-convention choice; Δt decomposition is
   not well-posed in the original v0.3 sense.

The three nouns in the v0.3 title — "Forward Map", "Observability",
"Phase and Contrast Maps" — have fared differently:

- **"Forward Map":** the map *exists*, but it factorises. It is
  one-dimensional in the contrast direction and one-dimensional (with
  a trivial 2D embedding onto the unit circle) in the phase direction.
  Calling it a "map" overclaims its structure.
- **"Observability":** operationalised cleanly by H1 (lock tolerance)
  and the S2 confirmation that arg C is the measurable signal. Still
  meaningful.
- **"Phase and Contrast Maps":** accurate but generic. The contrast
  "map" is trivial (flat in α, φ_α); the phase "map" is a closed-form
  cosine. A single figure suffices for each — calling them "maps" sets
  up an expectation of rich 2D structure that the data do not match.

The three motivations originally listed have collapsed:

| v0.3 motivation                                   | v0.4 status             |
|---------------------------------------------------|-------------------------|
| 1. arg C as position channel                      | ✓ confirmed and closed  |
| 2. φ_α axis as stroboscopic-lock diagnostic       | ✓ delivered via H1      |
| 3. Doppler broadening for coherent states         | ✗ falsified, not applicable |

What remains, concretely, is one closed-form result about the spin
response — `arg C(δ_0 = 0) = 90° + 2η|α| · cos φ_α` — and two
supporting-cast observations (Magnus bias at η · 518 kHz, lock FWHM
3.3 % at |α| = 3). That is a narrower object than "forward map".

## Renaming options

Three candidates, in descending order of scope reduction:

### Option A — *"The Position-Phase Channel of Stroboscopic Analysis"*

Guardian's proposed name. Describes exactly what the WP delivered: a
closed-form identity for the measurement phase in terms of motional
amplitude and phase. Drops "forward map" entirely.

- **Pros:** Reflects the actual result. Reader arrives with the right
  expectation. The injectivity question (v0.3 §4 deliverable 5) becomes
  natural: "is arg C(|α|, φ_α) injective on the unit circle?"
- **Cons:** Reads as if Doppler-channel work was out of scope from the
  start, whereas in fact it was *attempted* and *failed*. Loses the
  historical narrative that the scope reduction was earned.
- **Mitigation:** the v0.4 text narrates the 3 → 1 reduction explicitly
  in the introduction, crediting the preflight and S2 falsification.
  The title reflects the final object; the body reflects the history.

### Option B — *"Forward Map of Phase and Contrast; Position-Phase Channel"*

Compound title retaining both framings. Acknowledges that the WP began
as a forward-map exercise and ended as a position-phase characterisation.

- **Pros:** Honest about the history. A reader skimming the title gets
  both the original and final framings.
- **Cons:** Clunky. Two-part titles rarely survive casual reference;
  the WP will be referred to as whichever half dominates. In practice
  it will become "the phase-contrast WP" or "the position-phase WP"
  within a week.

### Option C — Keep v0.3 title, subtitle the scope reduction

Keep "Forward Map and Observability". Add a subtitle like
"*(position-phase channel closed; velocity channel demonstrated
inapplicable for coherent states)*".

- **Pros:** Zero cross-reference churn. The architecture doc, dossier,
  and preflight entries already name "WP-E — Forward Map and
  Observability"; renaming would require syncing all of them.
- **Cons:** The body of the v0.4 README will clearly say "this is about
  the position-phase channel", producing a title/body mismatch the
  reader has to translate each time.

## Recommendation

**Option A**, committed now, before v0.4 drafting.

Reasoning:

1. **The renaming cost is finite and bounded.** Cross-references are
   in [../README.md](../README.md) (the WP itself), its logbook entries
   (historical, need not be changed — they logged what was true at
   their writing), and the commit history. The dossier and
   ARCHITECTURE.md have not yet been updated to reference WP-E; the
   v0.3 preflight-results entry noted this update as an outstanding
   action and it was never done. So the renaming is internal to WP-E's
   own folder.

2. **The title-body mismatch cost is unbounded.** Every future reader,
   reviewer, and derivative work sees a mismatch that needs explaining.
   The cumulative tax exceeds the one-time renaming cost within two or
   three reads.

3. **Council meta-lesson ("one worked example beats three revision
   cycles") applies.** Commit to the framing now so v0.4 is written
   against it, rather than drafted under one framing and re-drafted
   under another.

4. **The historical narrative survives.** The title reflects the
   terminal object; the introduction narrates the 3 → 1 reduction.
   This is how every published paper works — the abstract describes
   what was found, not the path to finding it. Nobody expects the
   title of a paper to encode its authors' previous hypotheses.

## Commitments for v0.4 under Option A

If Option A is adopted:

- **New title:** `WP-E — The Position-Phase Channel of Stroboscopic Analysis`
- **Numbering unchanged:** still "WP-E" in the Breakwater architecture.
- **Subtitle remains:** "Work Program — v0.4 — 2026-XX-XX".
- **Introduction narrates the history:** 3 motivations in v0.3 → 1
  motivation delivered in v0.4. The preflight and S2 findings are
  named as the scope-altering discoveries.
- **§3 Purpose:** "map the closed-form identity
  arg C(δ_0 = 0, |α|, φ_α) = 90° + 2η|α|·cos φ_α and its deviations
  at η ≠ 0; characterise the stroboscopic-lock tolerance |C|(ε);
  localise the Magnus carrier bias."
- **§4 Deliverables:** renumbered/trimmed. The 6-item v0.3 list
  reduces to:
  1. Dataset (S1, S2 at α ∈ {1,3,5}, R1, R2 reference, H1, fine-grid
     confirmations).
  2. Figures: `S2_combined.png` as headline; `S1_carrier_summary.png`,
     `H1_lock_tolerance.png`, `R2_vs_full.png`, `S1_carrier_zoom.png`,
     `R2_fine_tooth.png` as supporting.
  3. Short note (≤ 2 pp) summarising the position-phase identity and
     three measured deviations.
  4. Logbook (done).
- **§8 Q-list:** most questions now closed; remaining open items are
  the experimental-team correspondence (Flag 1) and the WP-C pointer
  to thermal states.

## Veto assessment (Architect-internal)

Option A is the clean choice. No structural objection. Adopted with
the commitments above pending user confirmation.

## Action

**Gate on user confirmation.** Before drafting v0.4, the WP author
(user) is asked to confirm Option A (rename to "The Position-Phase
Channel of Stroboscopic Analysis") or prefer a different option.

If Option A is confirmed:

- v0.4 drafting proceeds under the new title.
- This entry is cited from v0.4 §1 as the record of the renaming
  decision.
- No README edit until v0.4 lands.

If Option B or C is preferred: revise this entry, no further action
needed.

*Guardian cadence still: no README edit until v0.4.*
