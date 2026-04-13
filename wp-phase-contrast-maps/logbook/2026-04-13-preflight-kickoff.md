# Logbook — 2026-04-13 — Preflight kickoff

**Context.** Guardian cleared [v0.3](../README.md) for execution. This entry
opens §4a preflight and codifies five residual Guardian flags as operational
requirements *before* any numerics runs. Sequel entry:
`2026-04-13-preflight-results.md` will record outcomes.

-----

## 1. Guardian flags → operational settings

### Flag 3 — Integrator-tolerance threshold (must fix before any comparison)

**Decision.** Three engines "agree to within integrator tolerance" at the
anchor point (δ₀ = 0, |α| = 0, φ_α = 0) iff

```
‖ΔC‖ = |C_A − C_B| < 10⁻⁴                  (complex coherence)
|Δ⟨σ_z⟩|           < 10⁻⁴                  (σ_z population)
max_n ‖ΔBloch_n‖   < 10⁻³                  (per-pulse, n = 1…22)
```

The per-pulse threshold is relaxed 10× because intermediate Bloch values
accumulate floating-point error across 22 matrix exponentials whereas the
final C is a single-point readout. These thresholds are defaults; if
preflight discovers legitimate engine differences dominated by a specific
cause (i.e. one of the four candidates in §4a), the cause is reported
regardless of whether thresholds are met.

### Flag 4 — Injectivity probe on raw C, not normalised

**Decision.** cond(J) is always computed on raw C = ⟨σ_x⟩ + i⟨σ_y⟩, not on
|C|_normalised. The normalisation factor 1/|C(0, 0, 0)| is a constant over
the entire map and therefore rescales cond(J) by that constant — harmless —
but *if* |C(0, 0, 0)| turns out to be small in the Doppler-dominated regime,
the normalisation amplifies numerical noise and corrupts the conditioning
analysis. Normalised |C| is a visualisation device only, per §2.1 of v0.3.

### Flag 2 — Finite-difference step per axis

**Decision.** For the Jacobian J = ∂(Re C, Im C)/∂(δ₀, |α|, φ_α):

- **δ₀:** central differences on the native grid (Δδ₀ = 0.05–0.1 MHz/(2π)
  depending on final resolution per Q4).
- **φ_α:** central differences on the native grid (Δφ_α ≈ 0.098 rad at 64
  points).
- **|α|:** the Q4-sanctioned sparse grid {0, 1, 3, 5} gives finite
  differences of spacing {1, 2, 2} — non-uniform and coarse. cond(J)
  along the |α| row will therefore reflect sampling artefact, not
  physics. **Mitigation:** a dense sub-grid |α| ∈ {0, 0.25, 0.5, …, 2}
  at 0.25 spacing is run *only* where S1 shows cond(J) flagged as ill-
  conditioned; elsewhere the coarse grid stands with an explicit caveat
  annotated on the plot.

### Flag 1 — Per-run cost quote for S2 budget

**Decision.** During preflight, measure wall time for a single anchor-point
run in the candidate engine. Multiply by slice sizes:
- S1 = 121 × 5 = 605 runs
- S2 = 121 × 64 × 3 = 23,232 runs    (expensive sheet)
- S3 = 5 × 64 × 2 = 640 runs

If S2 × (per-run cost) > 24 h wall, triage options: drop to 48 φ_α points
(Δφ_α ≈ 0.131 rad, still above 16-point sanity level); or reduce δ₀
resolution from 121 → 81 points; or run only the |α| = 3 sheet of S2 as
the diagnostic slice and defer |α| ∈ {1, 5} to a follow-up. Decision
deferred to the results entry; options stated here so they're not
invented mid-sweep.

### Flag 5 — Q3 and Q5 must both be resolved before S1

**Decision.** The preflight-results entry must explicitly state:

- **Q3:** whether a closed-form Lamb–Dicke linear prediction exists in the
  repo for C(δ₀, |α|, φ_α), or whether R1 will be evaluated numerically at
  η → 0 (e.g. η = 0.04 with linear extrapolation). Until this is stated,
  R1 residual plots cannot be generated.
- **Q5:** engine commitment — extend
  [../../scripts/stroboscopic_sweep.py](../../scripts/stroboscopic_sweep.py)
  or fork to a new `phase_contrast_map.py`. The decision depends on
  whether ⟨σ_x⟩, ⟨σ_y⟩ are already exposed or require a backend patch; see
  §2.

-----

## 2. Immediate inspection targets

Before any engine runs, answer three questions by reading files:

**Q5a — Does `stroboscopic_sweep.py` already return ⟨σ_x⟩, ⟨σ_y⟩?**
Expected finding: σ_z / P_↑ only, requiring a patch. To confirm, read
the remainder of the script beyond line 200 (Hamiltonian block seen in
the v0.3 code-reading pass).

**Q3a — Is there a closed-form LD linear prediction anywhere in the
repo?** Grep for "Lamb" / "LD" / `eta = 0` / small-η expansion in
`scripts/` and the HTML sources.

**Anchor data — Where is the (α=0, δ₀=0) legacy data point?** The
`data/alpha_0/` directory holds the HDF5 adaptive-learner outputs. The
JSON uniform engine data is under `data/runs/` (inferred from directory
name). Read both and extract the contrast value + any phase info at the
anchor point.

-----

## 3. Plan of execution

1. Inspect `scripts/stroboscopic_sweep.py` completely (lines 200 onward)
   — answer Q5a.
2. Inspect `data/alpha_0/` and `data/runs/` — locate anchor-point legacy
   values.
3. Grep for LD closed form — answer Q3.
4. If Q5a = no, decide: minimal patch vs. new script. Document either way.
5. Run candidate at anchor point; record wall time and Bloch trajectory.
6. Three-way comparison; if disagreement, assign one of four candidate
   causes.
7. Write `2026-04-13-preflight-results.md` with pass/fail determination,
   Q3 and Q5 resolutions, S2 budget calculation, and next-step call on
   main-sweep execution.

-----

## 4. Non-goals for preflight

- No map-grid runs.
- No Jacobian computation.
- No modifications to v0.3 README (per Guardian's cadence recommendation:
  next README touch is v0.4 *after* preflight data exists).
- No modifications to legacy data.

*Guardian cadence respected: single pass on §4a, then results entry, then
— and only then — main sweep or README v0.4.*
