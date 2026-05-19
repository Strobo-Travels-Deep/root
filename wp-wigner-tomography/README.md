# WP-W — Characteristic-function tomography under a high-η monochromatic stroboscopic drive

> **Start here → [`notes/wpw_findings.md`](./notes/wpw_findings.md)** — the
> single citable entry point: every load-bearing conclusion paired with
> its gate number, commit, and primary logbook. Full design doc:
> [`WORK-PROGRAM.md`](./WORK-PROGRAM.md). Publication scope & honest
> framing: [`notes/publication_assessment.md`](./notes/publication_assessment.md).
> This README is a pointer file.

**What this WP is.** A numerical adaptation of the Flühmann–Home
([FH20], PRL 125 043602) direct characteristic-function → FFT Wigner
framework to the *monochromatic stroboscopic* AC-train drive of
[Hasse24] (PRA 109 053105), at the high Lamb–Dicke parameter
η = 0.40. It is a theory/numerics continuation of the Hasse-2024
²⁵Mg⁺ programme — **not** an experimental result, and explicitly
subordinate to [FH20] (the χ-FFT framework) and [Hasse24] (the
protocol, the back-action and squeezed-state concepts).

**Status (2026-05-19).**

- **Core chain validated** — P0 + D2 + D3 + P1 + D4 cleared
  (ideal-SDF σ_x primitive; engine bridge: Layer A bit-exact, Layer B
  engine-χ vs analytic-χ = 3.75×10⁻⁴ over 6481 nodes). v0.5
  convention-correction pass applied (FH20-style σ_x SDF, direct
  χ = ⟨σ_y⟩ − i⟨σ_z⟩).
- **Back-action diagnostic (Rank 1)** — vacuum analytic gate PASS at
  machine precision; the quantitative ideal-vs-native Wigner-resolved
  back-action map across the full §7#4 set on the carrier (k=0) and
  first sideband (k=1), with a tooth-robust quantum/classical
  discriminator; bit-for-bit backward-compatible.
- **Squeezed vacuum (Rank 2)** — the 𝒪(η²)/δt analytic pass (locked);
  ideal squeezed-vacuum reconstruction clears the §7#5 Gaussian tier;
  and the **native 𝒪(η²) re-audit**: the monochromatic engine does
  not cleanly engineer the 2ω_m two-phonon squeezing channel — a
  gate-anchored, (r,θ)-robust quantitative boundary (engine-specific;
  [FH20]'s bichromatic drive realises the ideal χ-measurement chain).
- **Publication-prep** — novelty gate resolved (CONDITIONAL GO as a
  methods/characterisation paper; memo
  [`notes/publication_assessment.md`](./notes/publication_assessment.md));
  the locked claim contract is §8 there. An **internal, in-progress**
  paper draft exists ([`notes/paper_draft.md`](./notes/paper_draft.md))
  — incomplete (§I/VI/VII key-paragraphs, no figures, stub
  references, provisional author list). **Not a preprint; not for
  external circulation.**

## Folder layout

| Path | Contents |
|---|---|
| [`WORK-PROGRAM.md`](./WORK-PROGRAM.md) | The full WP document (verified bibliography, design decisions, deliverables, fidelity targets, conduct conventions). |
| [`numerics/`](./numerics/) | Runners (`run_reach_ladder`, `run_p0_preflight`, `run_reconstruction_demo`, `run_p1_preflight`, `run_bridge_native`, `run_bridge_inversion`, `run_back_action`, `squeezed_native_capability`, `run_squeezed_native_audit`) + `_common.py` + `test_*_helpers.py` smoke locks + HDF5/`wp_manifest_v1` outputs. |
| [`plots/`](./plots/) | Plot scripts + PNG outputs. |
| [`logbook/`](./logbook/) | Dated entries, pre-registered expectations → run → comparison (§5a discipline). |
| [`notes/`](./notes/) | See the notes index below. |
| [`refs/`](./refs/) | Per-paper extractions ([`FH20.md`](./refs/extractions/FH20.md), [`Hasse24.md`](./refs/extractions/Hasse24.md), …) + contextual notes + lit-review tracker. **Source of truth for prior-art adjudication.** |
| [`../notebooks/wpw_*.ipynb`](../notebooks/) | Four explanatory synthesis notebooks (chi→wigner, dirichlet targeting, back-action, native bridge). Synthesis artefacts — not a source of truth. |

### `notes/` index

| Note | Role |
|---|---|
| [`wpw_findings.md`](./notes/wpw_findings.md) | **Citable entry point** — program synthesis; every conclusion with gate/commit/logbook. |
| [`analytic_chain.md`](./notes/analytic_chain.md) | D1 standalone derivation: σ_x SDF → direct χ → Dirichlet map → FFT/Wigner → bridge → P0/P1/D4 anchors. Convention source of truth. |
| [`back_action_scope.md`](./notes/back_action_scope.md) | Rank-1 back-action scope (locked + executed; k=0/k=1, full §7#4). |
| [`squeezed_eta2_scope.md`](./notes/squeezed_eta2_scope.md) | The 𝒪(η²)/δt analytic pass (LOCKED): ideal chain η-exact for squeezed vacuum; App.-E timing as the 2ω_m Dirichlet map; pulse-duration order closed. |
| [`squeezed_native_audit_scope.md`](./notes/squeezed_native_audit_scope.md) | The native 𝒪(η²) re-audit scope (LOCKED) + the N-6 capability methodology. |
| [`publication_assessment.md`](./notes/publication_assessment.md) | Novelty-gate verdict (CONDITIONAL GO), prior-art table, referee-risk register, **§8 locked claim contract**, venue/figure map. |
| [`publication_outline.md`](./notes/publication_outline.md) | Paper section/figure outline, built against the §8 contract. |
| [`paper_draft.md`](./notes/paper_draft.md) | **⚠ Internal in-progress paper draft** — §II–V drafted, §I/VI/VII key-paragraphs, no figures, stub refs, provisional authors. **Not a preprint; not for external circulation** (scope: `publication_assessment.md` §7/§8). |

## Quick start (execution)

```bash
# D2–D4 runners — paths relative to the WP-W folder.
cd wp-wigner-tomography
python numerics/run_reach_ladder.py          # D2 reach ladder (analytic)
python numerics/run_p0_preflight.py          # P0 self-consistency gate
python numerics/run_reconstruction_demo.py   # D3 reconstruction (7 states)
python numerics/run_p1_preflight.py          # P1 engine-bridge sentinel
python numerics/run_bridge_native.py         # D4 Layer A — native vs WP-E
python numerics/run_bridge_inversion.py      # D4 Layer B — engine χ FFT (~18 min)
python -m pytest numerics/test_*_helpers.py -q   # all helper smoke locks

# Back-action + squeezed runners — repo-root-relative; explicit --output
# keeps parked artefacts untouched.
cd ..
python wp-wigner-tomography/numerics/run_back_action.py             # k=0 carrier (~2 min)
python wp-wigner-tomography/numerics/run_back_action.py --k-sideband 1 \
  --inputs vacuum coherent1.5 thermal0.5 fock1 fock2 cat1.5 mixed_cat1.5 \
  --output wp-wigner-tomography/numerics/back_action_k1_full.h5
python wp-wigner-tomography/numerics/run_reconstruction_demo.py \
  --states squeezed_0.5 squeezed_0.5_perp \
  --output wp-wigner-tomography/numerics/squeezed_recon.h5         # Rank-2 ideal
python wp-wigner-tomography/numerics/squeezed_native_capability.py # N-6 capability smoke
python wp-wigner-tomography/numerics/run_squeezed_native_audit.py  # native 𝒪(η²) (r,θ) sweep (~3 min)
```

Each runner writes an HDF5 artefact + sidecar `*.manifest.json` per
[`schemas/wp_manifest_v1.schema.json`](../schemas/wp_manifest_v1.schema.json).

## Status of deliverables

| ID | name | status |
|---|---|---|
| D1 | analytical note | ✅ [`notes/analytic_chain.md`](./notes/analytic_chain.md) standalone |
| D2 | reach ladder | ✅ runner + outputs + figure |
| D3 | reconstruction demo | ✅ PASS — all six gated §7#5 states; deciding-state criterion met |
| D4 | engine bridge | ✅ Layer A PASS @ machine precision; Layer B engine-χ ↔ analytic-χ = 3.75×10⁻⁴ (6481 nodes); centroid sub-pixel (Δα-attached, never a bare gate) |
| D5 | logbook | live; pre-reg → run → comparison per entry |
| P0 / P1 | preflight gates | ✅ PASS (P0 analytic-grid; P1 engine-bridge @ 10⁻¹⁴) |
| Rank 1 | back-action | ✅ vacuum gate PASS @ machine precision; quantitative ideal-vs-native map, k=0 + k=1 full §7#4; tooth-robust quantum/classical discriminator; bit-for-bit backward-compat |
| Rank 2 (ideal) | squeezed reconstruction | ✅ clears the §7#5 Gaussian tier; ideal-SDF χ chain η-exact for squeezed vacuum (the P-D bit-for-bit gate) |
| Rank 2 (native) | 𝒪(η²) re-audit | ✅ P-D gate PASS; (r,θ)-robust quantitative boundary — the monochromatic engine does not cleanly engineer the 2ω_m squeezing channel (engine-specific) |
| — | publication-prep | CONDITIONAL GO (methods/characterisation paper); claims locked (`publication_assessment.md` §8); **internal draft in progress — not for external circulation** |

-----

*Conventions: [`notes/analytic_chain.md`](./notes/analytic_chain.md).
Prior-art adjudication: [`refs/extractions/`](./refs/extractions/).
Honest publication framing & the locked claim scope:
[`notes/publication_assessment.md`](./notes/publication_assessment.md)
§8 — no "first/novel/structural-impossibility" framing; subordinate
to [FH20]/[Hasse24]; theory/numerics, not an experimental result.*
