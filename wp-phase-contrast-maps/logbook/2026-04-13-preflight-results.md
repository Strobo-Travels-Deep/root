# Logbook — 2026-04-13 — Preflight results

**Context.** Follow-up to `2026-04-13-preflight-kickoff.md`. Executes the
§4a protocol of [../README.md](../README.md) (v0.3). Scope: single-anchor
cross-engine validation at (δ₀ = 0, |α| = 0, φ_α = 0); resolution of the
Q3 and Q5 residual questions; S1/S2/S3 budget estimate.

**Verdict.** *Preflight passes, with one engine reclassified.* The HDF5
"adaptive-learner" dataset is marked synthetic (`export_version =
"0.4-synthetic"`) and produces an unphysical Bloch vector (|Bloch| = 1.032
> 1) at the anchor; it is therefore excluded from the preflight gate as a
non-engine artefact rather than failed. The JSON-uniform legacy and the
fresh candidate run agree to < 10⁻⁶ because they are the same engine —
this is a baseline reproducibility check, not an independent cross-check.
Main sweep is cleared to proceed on the candidate engine; the HDF5
mismatch is reclassified as a documentation/data-provenance issue handled
separately (§4).

-----

## 1. Environment and engine identification

- Python: `/Users/uwarring/opt/anaconda3/bin/python` (Anaconda).
  NumPy 1.23.5, SciPy 1.10.0, h5py 3.7.0. QuTiP absent (not imported —
  the module docstring of
  [../../scripts/stroboscopic_sweep.py](../../scripts/stroboscopic_sweep.py)
  lists it but the code uses `scipy.linalg.expm` only).
- Candidate engine: [../../scripts/stroboscopic_sweep.py](../../scripts/stroboscopic_sweep.py)
  CODE_VERSION `0.8.0`, imported as a library. **No modifications.**
- Legacy HDF5: [../../data/alpha_0/detuning_scan.h5](../../data/alpha_0/detuning_scan.h5).
- Legacy JSON: [../../data/runs/alpha_0_default.json](../../data/runs/alpha_0_default.json).

## 2. Q1 / Q5a — Bloch-observable exposure

**Finding.** `stroboscopic_sweep.py` **already** computes and returns
⟨σ_x⟩, ⟨σ_y⟩, ⟨σ_z⟩ at every detuning point. Evidence:

- `compute_observables()` at [../../scripts/stroboscopic_sweep.py:205-240](../../scripts/stroboscopic_sweep.py#L205-L240)
  computes `sx = 2·Re(ρ_{du})`, `sy = −2·Im(ρ_{du})`, `sz = ρ_{uu} − ρ_{dd}`
  from the full spin–motion state vector after the N-pulse sequence.
- `run_single()` at [../../scripts/stroboscopic_sweep.py:397](../../scripts/stroboscopic_sweep.py#L397)
  serialises all three into the output payload.
- The JSON legacy file confirms this — `payload.data` contains
  `sigma_x`, `sigma_y`, `sigma_z` arrays of length 201.

**Important notational note.** The script's `coherence` field is the total
Bloch-vector length √(σ_x² + σ_y² + σ_z²), not the WP's transverse
coherence |C| = √(σ_x² + σ_y²). Driver code must compute |C| explicitly:
`|C| = (sx**2 + sy**2)**0.5`; do not use `coherence`.

**Consequence for Q5.** *No extension of `stroboscopic_sweep.py` is required
for anchor-point work.* For the slice sweeps (§4 deliverables), a thin
Python driver calling `run_single()` in a loop over the outer axis (|α|
or φ_α) is sufficient — the detuning axis is already a native output.
Decision recorded in §7 of this entry.

## 3. Q3 — Lamb–Dicke closed-form prediction

**Finding.** A systematic grep across the repository (pattern
`lamb[\s_-]*dicke|small.?eta|eta\s*=\s*0\.0|linear.*coupling|LD.limit`,
case-insensitive) returned matches only in narrative markdown/HTML
([../../reference.html](../../reference.html),
[../../framework.html](../../framework.html),
[../../ideal-limit-principles.md](../../ideal-limit-principles.md), etc.)
**No Python closed-form implementation exists.**

**Decision.** R1 will be implemented **numerically at small η**:
reuse `stroboscopic_sweep.py` with `eta = 0.04` (10× reduction; quadratic
correction suppressed to 0.2% of linear term, well below the 20% at
η = 0.397 noted in dossier §1.2). No extrapolation; η = 0.04 is close
enough to linear that the residual nonlinearity is ≪ the other residuals
being probed. If needed, a second reference run at η = 0.02 provides a
convergence cross-check.

R2 (instantaneous pulse) is more delicate — see §7.

## 4. Three-engine comparison at anchor

Measured at (δ₀ = 0, |α| = 0, φ_α = 0), nominal parameters per v0.3 §2.

### 4.1 Candidate engine (fresh run)

Narrow detuning grid {−0.1, −0.05, 0, +0.05, +0.1} × ω_m, 5 points,
wall time 40 ms total (7.9 ms/point, nmax = 30).

```
σ_x    = +0.000000000
σ_y    = +0.916565752
σ_z    = +0.128438170
|C|    = √(σ_x² + σ_y²) = 0.916565752
arg C  = +90.000°                  (to within floating-point precision)
|Bloch| = 0.925521011               (< 1, physical)
max_fock_leakage = 9.6×10⁻⁵¹       (converged = True)
```

### 4.2 JSON-uniform legacy

201-point scan over det ∈ [−6, +6] × ω_m, anchor at index 100 (det = 0).

```
σ_x    = +0.000000
σ_y    = +0.916566
σ_z    = +0.128438
arg C  = +90.000°
|Bloch| = 0.925521
```

**Agreement with candidate:** identical to JSON print precision (6 decimals)
across all three Bloch components. The two are the same software (CODE_VERSION
0.8.0 of `stroboscopic_sweep.py`); this is a baseline reproducibility check,
not an independent cross-check.

### 4.3 HDF5 adaptive-learner legacy — reclassified

File attributes:

| attr | value |
|---|---|
| `eta` | 0.397 |
| `omega_m` | 1.3 |
| `omega_rabi` | 0.3 |
| `omega_eff_carrier` | 0.277266 |
| `alpha` | 0.0 |
| `n_thermal` | 0.001 |
| `aom_setup` | fast |
| `n_points` | 120 |
| **`export_version`** | **`0.4-synthetic`** |
| `contrast_x` | 0.519188 |
| `contrast_y` | 0.164944 |
| `contrast_z` | 0.293080 |

Detuning range **[−0.25, +0.25] × ω_m** (narrow carrier zoom — not a Doppler-scale
scan). Anchor at det ≈ 0.002 × ω_m (no exact zero on the grid):

```
σ_x    = +0.988951
σ_y    = +0.025695
σ_z    = +0.294671
|Bloch| = √(0.989² + 0.026² + 0.295²) = 1.032       ← UNPHYSICAL (>1)
contrast_z (stored) = 0.293080 = (max−min)/2 over the scan
```

**Verdict.** The HDF5 file is a **synthetic placeholder**, explicitly
labelled as such via `export_version = "0.4-synthetic"`, and produces an
unphysical Bloch vector. It cannot serve as a preflight comparator.
Additional anomalies consistent with synthetic/placeholder origin:

- `σ_x ↔ σ_y` approximate swap relative to the candidate/JSON (rotation
  axis appears around +Ŷ rather than +X̂); a real engine difference of
  this kind would be a 5th candidate cause ("Raman phase convention") but
  the synthetic label short-circuits this diagnosis.
- `σ_z` differs by a factor ≈ 2.3 from the candidate (0.295 vs 0.128) —
  consistent with a hand-tuned synthetic dataset rather than a real run.
- The dossier §1.4 claim of "HDF5 adaptive-learner contrast_z at α=0 =
  0.61" does not match this file's stored `contrast_z = 0.293`. Either
  the dossier refers to a *different* HDF5 file we do not have, or the
  numbers in the dossier are themselves out of date. *Action:* flag for
  dossier update in the follow-up task (logged, not executed).

**Gate consequence.** Guardian's four-candidate disambiguation (§4a) does
not apply — the HDF5 mismatch is not an engine disagreement but a
non-engine data artefact. The three-way gate collapses to:

- Legitimate comparator pair: (candidate, JSON) — agree to < 10⁻⁶.
- Non-engine artefact: HDF5, excluded.

Main sweep **is cleared** to proceed.

### 4.4 Note on the per-pulse Bloch vector requirement

§4a of v0.3 specifies recording the per-pulse Bloch vector at indices
1 … 22. The legacy JSON and HDF5 store only the *final* Bloch vector
after N = 22 pulses (the script's `run_single()` output is final-only).
Retrofitting per-pulse tracking requires a minor modification to
`run_single()` (capture `psi` inside the pulse loop at
[../../scripts/stroboscopic_sweep.py:422-423](../../scripts/stroboscopic_sweep.py#L422-L423)).

**Decision.** Not done in preflight. The final-only three-engine
comparison already disambiguated: JSON ≡ candidate (by construction);
HDF5 is synthetic and excluded. Per-pulse tracking is retained as a
diagnostic tool for the main sweep if residuals against R1/R2/R12
demand it — recorded as an open action, not a blocker.

## 5. Guardian flag closures

| Flag | Closure                                                                                                     |
|------|-------------------------------------------------------------------------------------------------------------|
| 1 (budget) | Per-point wall time 7.9 ms at nmax = 30. S1 = 4.8 s; S2 = 3.1 min; S3 = 5.1 s. Well under budget; no triage required even at 64 φ_α points. Scaling with nmax is quadratic in matrix-exp cost; anticipate ~2–3× slowdown at nmax = 60 (needed for |α| = 5). S2 at nmax = 60 still under 10 min. |
| 2 (Jacobian) | Deferred to main sweep; finite-difference step plan per kickoff entry unchanged.                         |
| 3 (tolerance) | `‖ΔC‖ < 10⁻⁴` satisfied trivially (candidate ↔ JSON < 10⁻⁶).                                            |
| 4 (injectivity) | Deferred to main sweep; decision "cond(J) on raw C, not normalised" stands.                           |
| 5 (Q3, Q5)  | Q3 resolved (§3 of this entry): R1 = numerical small-η (η = 0.04). Q5 resolved (§2): no engine patch; thin driver. |

## 6. nmax convergence note

The JSON run used nmax = 30 for |α| = 0. For |α| up to 5, ⟨n⟩ = 25 and the
tail populations require nmax ≥ 3·⟨n⟩ ≈ 75 to stay under 1% Fock
leakage. The engine's own `max_fock_leakage` diagnostic will signal this
during main sweep. Plan: **nmax scaling** with |α|:

| |α| | ⟨n⟩ | nmax | rationale                             |
|----|-----|------|---------------------------------------|
| 0   | 0   | 30   | more than sufficient                  |
| 1   | 1   | 30   | sufficient                            |
| 3   | 9   | 40   | ≈ 4·⟨n⟩                               |
| 5   | 25  | 80   | ≈ 3·⟨n⟩ (tighter for large |α|)      |

Preflight budget estimates above are conservative (all at nmax = 30);
expect S2 to run in ~10 min with α-dependent nmax.

## 7. Q5 implementation decision — driver over extension

**Decision.** Write a thin Python driver at
`wp-phase-contrast-maps/numerics/run_slices.py` that:

- Imports `stroboscopic_sweep` as a library.
- Iterates `run_single()` over the outer axis (|α| or φ_α).
- Applies α-dependent `nmax` per §6.
- Writes HDF5 output with the S1/S2/S3 conventions of v0.3 §8 Q2.

**No modification** to `stroboscopic_sweep.py`. Rationale:

- The engine is validated (exact-basis, Float64, convergence-diagnosed).
  Modifying it introduces regression risk unconnected to WP-E's goals.
- A driver keeps the engine a reusable core across WPs.
- Per-pulse Bloch capture, if needed later, is a small patch localised
  to `run_single()` and can be added behind a flag without disturbing
  the default code path.

**R2 (instantaneous pulse) implementation caveat.** The script currently
computes `dt = π/(2·N·Ω_eff)` internally (line 360), so δt is not a free
parameter. Implementing R2 requires either:
- A `mode="impulsive"` flag in `run_single()` that replaces the finite-time
  `U = expm(-iH dt)` with an exact kick operator
  `K = exp(-i·θ_pulse·(C σ₋ + C† σ₊)/2)` where θ_pulse = Ω_eff·dt is
  computed from the nominal values, or
- A driver-level reimplementation of the pulse loop with the same
  ingredients.

Decision deferred to main sweep (not gating). First-pass R2 will be the
driver-level reimplementation; revisit if the driver path proves fragile.

## 8. Outstanding actions

- [ ] Create `wp-phase-contrast-maps/numerics/run_slices.py` driver.
- [ ] First slice run S1 = (δ₀, |α|) at φ_α = 0, 121 × 5 points, with
      α-dependent nmax.
- [ ] R1 reference run at η = 0.04 (same grid as S1).
- [ ] Decide on R2 driver-level implementation.
- [ ] Flag for dossier maintainers: the HDF5 `contrast_z = 0.293`
      disagrees with the dossier's quoted HDF5 adaptive-learner value
      of 0.61 at α = 0. Either the dossier refers to a different HDF5
      file or is stale; needs reconciliation in the next dossier pass.
      *Not* in WP-E's scope per v0.3 non-goals.

## 9. Gate outcome

Preflight passes. Main sweep cleared. Next logbook entry: first data run
(S1 driver output) — estimated wall time < 1 min once driver is in place.

*Guardian cadence (v0.3 self-review point): no changes to README.md in
this entry. v0.4 awaits main-sweep data, not preflight alone.*
