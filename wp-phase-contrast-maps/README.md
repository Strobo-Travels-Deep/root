# WP-E — Forward Map and Observability: Phase and Contrast Maps of the Stroboscopic Analysis Pulse

**Work Program · v0.3 · 2026-04-13**
**Status:** execution-ready pending preflight gate (§4a).
**Numbering:** **WP-E — Forward Map and Observability** (resolved in v0.3; see §8).

-----

## 1. Introduction

Stroboscopic travelling-wave control of a single trapped ion outside the
Lamb–Dicke regime enables spin-mediated readout of motional-state phase
and amplitude with sub-wavelength spatial sensitivity [Hasse2024]. In the
protocol of interest, a train of N = 22 phase-stable analysis pulses, each
synchronised to one motional period T_m = 2π/ω_m, accumulates coherently
to approximately π/2 (≈ 1.53 rad / 88° at the nominal parameters of §2).
Position and velocity information are encoded, respectively, in the
geometric phase k_eff·x (via the travelling-wave wavevector) and in the
Doppler detuning δ_D = k_eff·v (via the Rabi lineshape). The zero-point
Doppler scale,

```
δ_D^ZPM = k_eff · x_0 · ω_m = η · ω_m ≈ 2π × 0.516 MHz,
```

already exceeds the Rabi linewidth (Ω_eff/(2π) = 0.277 MHz) — the regime
is Doppler-dominated even at α = 0.

The physics identity of the scheme — Floquet-synchronised quadrature
spectroscopy rather than a softened ultrafast kick — is developed in
[ideal-limit-principles.md](../ideal-limit-principles.md). This WP
addresses the *observable forward map*: how the complex spin coherence
after the pulse train depends jointly on the pulse detuning δ₀, the
coherent-state amplitude |α|, and the motional phase φ_α at the first
pulse. Where the ideal-limit picture asserts that `arg C` reports position
and `|C|(δ₀)` reports velocity, this WP tests that assertion quantitatively
in the presence of η ≈ 0.4 nonlinearity and 40 ns finite-time (Magnus)
corrections: `arg C` is expected to be dominantly sensitive to position in
the LD and near-synchronous limit, and deviations quantify the channel
mixing.

Two bodies of prior work frame the question. First, the Monroe ultrafast
programme [Mizrahi2013, Mizrahi2014, Johnson2015, Johnson2017,
Wong-Campos2017] established impulsive spin-dependent kicks as a
temperature-insensitive tool for interferometry and cat-state preparation;
the theoretical basis was laid by García-Ripoll, Zoller and Cirac
[García-Ripoll2003, García-Ripoll2005] and scaled by Duan [Duan2004]. In
that regime pulses are short compared with T_m and the kick factorises
cleanly from free evolution. Second, standard trapped-ion spectroscopy in
the resolved-sideband limit provides the canonical Rabi-lineshape velocity
filter; see the review by Leibfried et al. [Leibfried2003] and the earliest
Schrödinger-cat demonstration by Monroe et al. [Monroe1996]. The question
of back-action structure and quadrature selectivity originates with
Braginsky and Caves [Braginsky1980, Caves1980].

The present protocol operates in *neither* the impulsive limit
(δt/T_m ≈ 0.05) nor the fully resolved-sideband limit (Ω/ω_m ≈ 0.23, with
Doppler widths δ_D ≫ Ω already at zero point). Mapping the forward
response over (δ₀, |α|, φ_α) therefore serves three purposes: it
quantifies the stroboscopic phase-lock tolerance, exposes the position
channel (arg C) absent from existing σ_z-only runs, and characterises a
known mismatch between two simulation methods on the contrast observable
(see §3).

-----

## 2. Notation and nominal parameters

All maps in this WP are computed at the fixed device parameters of the
dossier (matched to the ²⁵Mg⁺ AC-Raman experiment of [Hasse2024]):

| Symbol            | Value                  | Meaning                                   |
|-------------------|------------------------|-------------------------------------------|
| ω_m/(2π)          | 1.300 MHz              | Motional frequency                        |
| T_m               | 769 ns                 | Motional period                           |
| η                 | 0.397                  | Effective Lamb–Dicke parameter            |
| Ω/(2π)            | 0.300 MHz              | Bare carrier Rabi frequency               |
| Ω_eff/(2π)        | 0.277 MHz              | Debye–Waller suppressed, = Ω·exp(−η²/2)   |
| δt                | 40 ns                  | Analysis-pulse duration                   |
| N                 | 22                     | Number of pulses (1 per motional cycle)   |
| θ_pulse           | 0.070 rad (4.0°)       | Per-pulse rotation, = Ω_eff · δt          |
| N · θ_pulse       | 1.53 rad (88°)         | Accumulated rotation on carrier at α = 0  |
| T_total           | 16.9 μs                | = N · T_m                                 |
| δ_D^ZPM/(2π)      | 0.516 MHz              | RMS zero-point Doppler width = η·ω_m/(2π) |
| ⟨n⟩_thermal       | 0.001                  | Residual thermal background               |

Observable: the complex spin coherence after the pulse train,

```
C(δ₀, |α|, φ_α) = ⟨σ_x⟩ + i ⟨σ_y⟩,   |C| = contrast,   arg C = measurement phase.
```

Scan axes: δ₀ = analysis-pulse detuning from carrier; |α| = coherent
amplitude of the initial motional state |α e^{iφ_α}⟩; φ_α = motional phase
at first-pulse preparation time, convention fixed in §2.2.

**Rotating-frame caveat.** C is defined in the rotating frame of the final
analysis pulse; experimental access requires phase-referenced tomography,
not σ_z population readout alone. This distinction matters when mapping
simulation predictions onto lab observables.

**Pure-state baseline.** ⟨n⟩_thermal = 0.001 is treated as effectively pure;
all §4 deliverables are pure-state unitary unless otherwise flagged. Noise
channels are admissible only if introduced deliberately per §4a D2.

Abbreviations: WP — work program; LD — Lamb–Dicke; BAE — back-action
evasion; ZPM — zero-point motion; QND — quantum non-demolition.

### 2.1 Contrast reference

The contrast observable |C| is normalised *relative to the maximum
achievable coherence of the same N = 22 pulse sequence on the reference
state* (|α| = 0, δ₀ = 0, φ_α = 0), not relative to an idealised π/2:

```
|C|_normalised(δ₀, |α|, φ_α) = |C(δ₀, |α|, φ_α)| / |C(0, 0, 0)|.
```

This makes the map's absolute scale insensitive to the 1.53 rad vs. π/2
discrepancy (A2) and places all residuals against a concrete,
reproducible anchor point. Raw (unnormalised) |C| is also stored in the
dataset for completeness.

### 2.2 Motional-phase convention

φ_α is the phase of the complex coherent-state amplitude α = |α| e^{iφ_α}
used in state preparation in [scripts/stroboscopic_sweep.py](../scripts/stroboscopic_sweep.py).
The convention is anchored to the engine's Hamiltonian, not to an abstract
phase-space picture:

- Coherent-state construction (code line 103):
  `alpha = alpha_abs * np.exp(1j * theta)` with `theta = np.radians(alpha_phase_deg)`.
- Displacement generator (code line 138): `gen = alpha * adag - np.conj(alpha) * a`,
  i.e. D(α) = exp(α a† − α* a).
- Position quadrature (code line 88): `X = a + adag`.

Consequence: φ_α = 0 prepares the ion on the +X̂ axis in phase space
(⟨X̂⟩ > 0, ⟨P̂⟩ = 0); φ_α = π/2 prepares it on the +P̂ axis. The sign
convention of all ∂C/∂φ_α residuals follows from this anchor.

-----

## 3. Purpose and scope

### 3.1 Purpose

Map the complex coherence C(δ₀, |α|, φ_α) over a structured grid, compare
against three ideal-limit reference models (R1 Lamb–Dicke linear, R2
instantaneous-pulse, R12 composite — see §4 and §8 Q3), and report the
residuals that isolate η-nonlinearity from finite-time (Magnus) effects
via the clean decomposition

```
Δη   = R2 − R12       (pure η effect, δt held at 0)
Δt   = R1 − R12       (pure finite-time effect, η held at 0)
cross = full − (R1 + R2 − R12)   (η × finite-time interaction)
```

This WP is the observable-side companion to the deviations identified in
[ideal-limit-principles.md](../ideal-limit-principles.md):

- §1.3 of the dossier (position readout via phase shift) ↔ `arg C`.
- §1.4 of the dossier (momentum readout via Doppler detuning) ↔ `|C|(δ₀)`.
- §1.5 of the dossier (stroboscopic sampling) ↔ `C(φ_α)`.

Specifically, three concrete motivations:

- **arg C is dominantly sensitive to position in the LD and near-synchronous
  limit; deviations quantify channel mixing.** Dossier §1.3 asserts the
  clean correspondence; no existing simulation output plots arg C, so the
  assertion is currently untested.
- **The φ_α axis makes the stroboscopic lock measurable.** Dossier §1.5
  claims all 22 pulses sample the "same" motional phase. A sweep over φ_α
  directly tests how steeply the signal depends on strobe alignment and
  quantifies the phase-stability tolerance (Δω_m/ω_m ≲ 0.7 %) in
  measurable units.
- **The (δ₀, |α|) surface characterises a known provenance mismatch.**
  Dossier §1.4 notes that two simulation methods disagree on σ_z contrast:
  HDF5 adaptive-learner values 0.61/0.71/0.84/0.75 (α = 0, 1, 3, 5) vs.
  22-pulse JSON uniform ≈ 0.56. *Discriminant:* at the preflight anchor
  point (δ₀ = 0, |α| = 0, φ_α = 0) the two engines must agree to within
  integrator tolerance if and only if they share identical φ_α sampling,
  no hidden ensemble averaging, identical Ω vs Ω_eff calibration, and
  compatible integrator settings. Persistent disagreement at that point
  isolates which of those four causes is responsible; agreement at the
  anchor combined with divergence on the (δ₀, |α|) surface isolates the
  residual cause to a state-space or observable-definition difference
  (see §4a).

### 3.2 In scope
- Forward simulation of C over the agreed grid for coherent motional states.
- Comparison against the three reference limits R1, R2, R12 (§8 Q3).
- Structured 2D slices of the 3D parameter space (§8 Q2).
- Local Jacobian J = ∂(Re C, Im C) / ∂(δ₀, |α|, φ_α) with condition-number
  heatmap as an injectivity probe (§4 deliverable 5).

### 3.3 Out of scope
- Non-coherent motional states (thermal, squeezed, cat) — deferred to WP-C.
- Projective-measurement backaction — WP-A.3.
- Reconstruction of ρ from C — WP-C.3.
- Variations of device parameters (η, Ω, δt, ω_m) — WP-A.3 (η) and
  WP-A.1 (δt). This WP holds the parameters of §2 fixed.

-----

## 4. Deliverables

1. **Dataset** — HDF5 or JSON manifest with C(δ₀, |α|, φ_α) and ⟨σ_z⟩ on
   the agreed grid; also R1, R2, R12 evaluated on the same grid points.
   Stored in [numerics/](numerics/).
2. **Residual plots** — 2D heatmaps of |C| and arg C for each slice defined
   in §8 Q2, together with residual plots against **all three baselines**:
   Δη (full − R2 + R12), Δt (full − R1 + R12), and cross (full − R1 − R2 +
   R12). Stored in [plots/](plots/).
3. **Logbook** — dated entries for each simulation run, parameter choice,
   and interpretation step, stored in [logbook/](logbook/). One entry per
   substantive decision or dataset.
4. **Short note** — ≤ 2 pages summarising what the maps reveal about
   channel separation, phase-lock sensitivity, and the HDF5-vs-JSON
   provenance gap.
5. **Injectivity probe** — local Jacobian

   ```
   J(δ₀, |α|, φ_α) = ∂(Re C, Im C) / ∂(δ₀, |α|, φ_α)
   ```

   evaluated on the slice grid via finite differences, together with a
   condition-number heatmap cond(J). This converts the ledger principle
   P7 (tomographic injectivity) from an implicit claim into a measurable
   output, and lets us distinguish genuine physical degeneracy of the
   forward map from numerical artefact. Stored in [numerics/](numerics/)
   (data) and [plots/](plots/) (heatmaps).
6. **[Stretch] Floquet lock-tolerance diagnostic** — |C| vs. ε with pulse
   frequency ω_pulse = ω_m(1 + ε), at (δ₀ = 0, |α| ∈ {0, 3}, φ_α = 0).
   Directly quantifies the Δω_m/ω_m ≲ 0.7 % lock tolerance of [Hasse2024]
   as a consistency check. Not gating; cheap if the engine supports
   non-resonant pulse spacing via `t_sep_factor`.

Success criterion: each of the three motivations in §3.1 is either
confirmed, refuted, or sharpened into a more specific follow-up question.

-----

## 4a. Preflight gate (gates the main sweep)

Before any map-grid runs, a single-point cross-engine validation must be
performed. Gate condition: preflight must either pass, or fail with an
identified cause from the four-candidate list below.

**Protocol.** At fixed (δ₀ = 0, |α| = 0, φ_α = 0):

1. Run the HDF5 adaptive-learner engine (legacy, produced the
   0.61/0.71/0.84/0.75 contrast series).
2. Run the JSON-uniform engine (legacy, produced the ≈ 0.56 contrast).
3. Run the candidate engine (extended `stroboscopic_sweep.py` or new
   `phase_contrast_map.py` — to be decided per §8 Q5).

For each engine, record the per-pulse Bloch vector (⟨σ_x⟩, ⟨σ_y⟩, ⟨σ_z⟩)
at every pulse index 1 … 22, plus the accumulated phase arg C(0, 0, 0).

**Report.** Do the three engines agree to within integrator tolerance? If
not, which of the four candidate causes is responsible?

- (i) φ_α sampling (e.g., one engine samples at pulse centres, another at
  pulse starts);
- (ii) hidden ensemble averaging (one engine silently averages over a
  thermal or projection-noise distribution);
- (iii) Ω vs Ω_eff calibration (Debye–Waller factor applied / not applied);
- (iv) integrator tolerance (step size, Fock-basis cutoff n_max).

**D2 — noise-model gate.** If the legacy engines' noise models are not
documented to be identical to the candidate engine's pure-unitary
configuration, pure-unitary simulation cannot disambiguate the mismatch,
and the noise-model decision (§8 Q7) must be revisited and resolved
*before* the main sweep — not deferred. This removes a silent deferral
hazard.

**Outcome branching.**
- If preflight passes (all three engines agree at the anchor point): proceed
  to §4 deliverables at the candidate engine, with legacy engines used for
  spot-check cross-validation at sentinel grid points.
- If preflight fails with identified cause: publish a logbook entry naming
  the cause, decide whether to patch, document, or quarantine the affected
  engine, and re-run preflight.
- If preflight fails with *no* identified cause: main sweep is paused; the
  mismatch itself becomes a WP-E sub-deliverable.

-----

## 5. Folder layout

```
wp-phase-contrast-maps/
├── README.md      (this document)
├── numerics/      (datasets, manifests, Jacobian tensors)
├── plots/         (figures: heatmaps, residuals, cond-J maps)
└── logbook/       (dated entries, one per decision or run)
```

-----

## 6. Connection to existing ledger principles

Principles are those of [ideal-limit-principles.md §4](../ideal-limit-principles.md).

| Principle                    | What this WP contributes                                                                  |
|------------------------------|-------------------------------------------------------------------------------------------|
| P1 — Phase lock              | Direct measurement of ∂C/∂φ_α; quantifies lock tolerance; stretch deliverable 6 tests Δω_m/ω_m |
| P3 — Doppler momentum readout| \|C\|(δ₀) family parameterised by \|α\|                                                   |
| P4 — Channel separation (L2) | Test whether arg C tracks position and \|C\|(δ₀) tracks velocity in the LD/near-synchronous limit; deviations quantify channel mixing |
| P7 — Tomographic injectivity | Condition-number heatmap of the local Jacobian over the slice grid                        |

-----

## 7. Relation to the Monroe ultrafast programme

The Monroe scheme achieves temperature-insensitive kicks through
impulsiveness (δt/T_m ~ 10⁻⁵) [Mizrahi2013, Johnson2015]. The present
protocol trades impulsiveness for stroboscopic synchronisation — 22 weak
phase-locked pulses instead of one ultrafast kick [Hasse2024]. The maps
computed in this WP are the diagnostic by which that trade-off is made
quantitative: the φ_α axis exposes the cost of imperfect synchronisation,
and the (δ₀, |α|) surface exposes the coupling between Doppler spectrum
and motional amplitude that the impulsive limit obscures.

-----

## 8. Committed decisions and residual questions

**Q0 — WP numbering.** *Resolved.* Adopted as **WP-E — Forward Map and
Observability**, a new node in the dossier architecture. Cross-reference
updates in [ARCHITECTURE.md](../ARCHITECTURE.md) and
[ideal-limit-principles.md](../ideal-limit-principles.md) are a separate
task and tracked in the logbook entry dated 2026-04-13.

**Q1 — Observable.** *Resolved:* **C + σ_z** (full complex coherence plus
σ_z for cross-validation with legacy runs). Requires the simulation
backend to expose ⟨σ_x⟩, ⟨σ_y⟩; code-reading pass during preflight (§4a)
will confirm availability in [scripts/stroboscopic_sweep.py](../scripts/stroboscopic_sweep.py).

**Q2 — Grid structure.** *Resolved:* **Option B, structured 2D slices.**
- S1: (δ₀, |α|) at φ_α = 0.
- S2: (δ₀, φ_α) at |α| ∈ {1, 3, 5} — three separate sheets.
- S3: (|α|, φ_α) at δ₀ ∈ {0, ω_m} — two separate sheets.
Promotion to a full 3D cube is reserved for a follow-up if slices reveal
non-separable cross-terms.

**Q3 — Reference models.** *Resolved:* **R1 + R2 + R12 composite
baseline.** Residuals computed per the decomposition in §3.1. *Residual
question:* does the repo contain a closed-form Lamb–Dicke linear
prediction for C(δ₀, |α|, φ_α), or does R1 require numerical evaluation
at small η with extrapolation? Code reading during preflight answers this.

**Q4 — Grid resolution.** *Partially resolved.*
- δ₀: ±6 MHz/(2π), step to be finalised in the preflight logbook entry
  (target 41–121 points).
- |α|: {0, 1, 3, 5} in the first pass, matching legacy runs; finer set
  {0, 0.5, 1, 2, 3, 4, 5} only if residuals demand it.
- **φ_α: minimum 48 points, 64 preferred.** At η ≈ 0.4, harmonics to
  3–4× fundamental are expected; 16 points are a sanity-check resolution
  only and may not resolve the harmonic structure at amplitude.
*Residual question:* is 64 φ_α points × 121 δ₀ points × 5 |α| values =
38,720 runs tractable on the candidate engine? Preflight timing answers
this.

**Q5 — Engine and tooling.** *Conditionally resolved:* **decide after
preflight.** Default = extend
[scripts/stroboscopic_sweep.py](../scripts/stroboscopic_sweep.py) to
expose ⟨σ_x⟩, ⟨σ_y⟩ and to support N-D sweeps. A new `phase_contrast_map.py`
is the fallback if extension is more invasive than writing a thin wrapper.

**Q6 — Motional-phase convention.** *Resolved in §2.2.* Anchored to the
code definition at [scripts/stroboscopic_sweep.py:103](../scripts/stroboscopic_sweep.py#L103)
and the displacement generator at line 138.

**Q7 — Noise model.** *Resolved:* **pure-state unitary**, gated by the §4a
D2 clause — if preflight reveals undocumented noise in the legacy engines,
Q7 reopens immediately.

**Q8 — N_pulses treatment.** *Resolved:* **fix N = 22**, with contrast
defined per §2.1 relative to the reference state (|α| = 0, δ₀ = 0,
φ_α = 0). The fact that N · θ_pulse = 1.53 rad ≠ π/2 is acknowledged
explicitly; the reference state encodes the actual accumulated rotation
and removes the π/2-idealisation ambiguity.

-----

## 9. Proposed next step

1. Execute the §4a preflight protocol.
2. Resolve the residual questions in §8 Q3, Q4, Q5 on the basis of
   preflight results.
3. Produce a short preflight logbook entry naming the candidate engine,
   grid resolutions, and any identified cause if engines disagree.
4. Begin the slice runs (S1, S2, S3) per §4 deliverables 1–5; the
   stretch deliverable 6 runs opportunistically.

**Forward-looking hook.** If the injectivity probe (§4 deliverable 5)
reveals that the forward map is non-injective on regions of the slice grid
relevant to the target state family, the follow-up decision is whether to
treat this as a protocol limitation or to design multi-frequency /
multi-phase pulse trains that restore injectivity. This is flagged as
candidate scope for the next WP in this series and is *not* in WP-E's
remit.

-----

## References

- **[Braginsky1980]** V. B. Braginsky and Yu. I. Vorontsov, "Quantum-Mechanical Limitations in Macroscopic Experiments and Modern Experimental Technique," Sov. Phys. Usp. **23**, 644 (1980).
- **[Caves1980]** C. M. Caves, K. S. Thorne, R. W. P. Drever, V. D. Sandberg, and M. Zimmermann, "On the measurement of a weak classical force coupled to a quantum-mechanical oscillator," Rev. Mod. Phys. **52**, 341 (1980).
- **[Duan2004]** L.-M. Duan, "Scaling Ion Trap Quantum Computation through Fast Quantum Gates," Phys. Rev. Lett. **93**, 100502 (2004).
- **[García-Ripoll2003]** J. J. García-Ripoll, P. Zoller, and J. I. Cirac, "Speed Optimized Two-Qubit Gates with Laser Coherent Control Techniques for Ion Trap Quantum Computing," Phys. Rev. Lett. **91**, 157901 (2003).
- **[García-Ripoll2005]** J. J. García-Ripoll, P. Zoller, and J. I. Cirac, "Coherent control of trapped ions using off-resonant lasers," Phys. Rev. A **71**, 062309 (2005).
- **[Hasse2024]** F. Hasse, D. Palani, R. Thomm, U. Warring, and T. Schaetz, "Phase-stable travelling waves stroboscopically matched for super-resolved observation of trapped-ion dynamics," Phys. Rev. A **109**, 053105 (2024); arXiv: 2309.15580.
- **[Johnson2015]** K. G. Johnson, B. Neyenhuis, J. Mizrahi, J. D. Wong-Campos, and C. Monroe, "Sensing Atomic Motion from the Zero Point to Room Temperature with Ultrafast Atom Interferometry," Phys. Rev. Lett. **115**, 213001 (2015).
- **[Johnson2017]** K. G. Johnson, J. D. Wong-Campos, B. Neyenhuis, J. Mizrahi, and C. Monroe, "Ultrafast creation of large Schrödinger cat states of an atom," Nat. Commun. **8**, 697 (2017).
- **[Leibfried2003]** D. Leibfried, R. Blatt, C. Monroe, and D. Wineland, "Quantum dynamics of single trapped ions," Rev. Mod. Phys. **75**, 281 (2003).
- **[Mizrahi2013]** J. Mizrahi, C. Senko, B. Neyenhuis, K. G. Johnson, W. C. Campbell, C. W. S. Conover, and C. Monroe, "Ultrafast Spin–Motion Entanglement and Interferometry with a Single Atom," Phys. Rev. Lett. **110**, 203001 (2013).
- **[Mizrahi2014]** J. Mizrahi, B. Neyenhuis, K. G. Johnson, W. C. Campbell, C. Senko, D. Hayes, and C. Monroe, "Quantum control of qubits and atomic motion using ultrafast laser pulses," Appl. Phys. B **114**, 45–61 (2014).
- **[Monroe1996]** C. Monroe, D. M. Meekhof, B. E. King, and D. J. Wineland, "A 'Schrödinger Cat' Superposition State of an Atom," Science **272**, 1131 (1996).
- **[Wong-Campos2017]** J. D. Wong-Campos, S. A. Moses, K. G. Johnson, and C. Monroe, "Demonstration of Two-Atom Entanglement with Ultrafast Optical Pulses," Phys. Rev. Lett. **119**, 230501 (2017).

-----

*v0.3 changelog (2026-04-13):*

- **A1** (Guardian + external): softened channel-separation claim in §1, §3.1,
  §6 P4 row. `arg C` is "dominantly sensitive to position in the LD and
  near-synchronous limit; deviations quantify channel mixing."
- **A2**: replaced "π/2 rotation" in §1 with "approximately π/2 (≈ 1.53 rad
  / 88° at the nominal parameters of §2)"; added N · θ_pulse row to the §2
  table; §8 Q8 cross-references.
- **A3**: added provenance discriminant sentence to §3.1 motivation 3;
  downgraded "disambiguates" → "characterises" in §1 and §3.1; four
  candidate causes enumerated in §4a.
- **B1**: added R12 composite baseline and the Δη / Δt / cross
  decomposition in §3.1; §4 deliverable 2 now requires residual plots
  against all three baselines.
- **C1**: new §4 deliverable 5 — local Jacobian J and condition-number
  heatmap as injectivity probe. P7 row of §6 rewritten to reference it.
- **C2**: forward-looking hook appended to §9 on non-injectivity remediation.
- **D1**: new §4a preflight gate with three-engine single-point cross-validation
  and four-candidate-cause report format.
- **D2**: noise-model gate clause in §4a; Q7 reopens if legacy noise models
  are not documented to match candidate engine.
- **E1**: §2.2 anchors φ_α to code lines 103 and 138 of
  [scripts/stroboscopic_sweep.py](../scripts/stroboscopic_sweep.py); Q6
  resolved.
- **E2**: φ_α resolution raised from 16/32 → **48 minimum, 64 preferred**
  in §8 Q4; 16 retained as sanity-check only.
- **E3**: new §2.1 defines |C| normalisation against the reference state,
  not against π/2.
- **E4**: pure-state baseline stated explicitly in §2; ambiguity in Q7
  removed.
- **E5**: δ_D^ZPM = η · ω_m formula and numerical value (0.516 MHz) added
  to §1 and §2 parameter table.
- **F1**: rotating-frame caveat added to §2.
- **G1**: Q0 resolved to **WP-E — Forward Map and Observability**; section
  header and numbering line updated; Q0 removed from §8's open list and
  archived as a resolved decision.
- **H1**: stretch deliverable 6 — Floquet lock-tolerance diagnostic — added
  to §4 and cross-referenced in §6 P1 row.

*Guardian assessment (self-review):* five external-review tightening points
(A1, B1, C1, D1, E2) each addressed with a specific edit to a specific
section. Guardian EC points A2, A3, D2, E1, E3, E4, E5, F1, G1 adopted;
H1 adopted as non-gating stretch. No declinations.

*v0.2: introduction + literature + self-contained notation and references.*

*v0.1: initial draft for discussion.*
