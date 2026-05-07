# WP-Coastline — Strong / Weak-Binding Boundary Map

**Work Program · v0.1 · 2026-04-21**
**Status:** execution-ready under co-lock resolution of
[council-memo-2026-04-21-strong-weak-coastline.md](../council-memo-2026-04-21-strong-weak-coastline.md)
§9 — §5.1 lemma inlined below as first content item; §4.2 grid geometry,
§4.3 two-map observables, and §4.4 three-point |α| baseline locked.

*Local candidate framework (no parity implied with externally validated
laws).*

*Epistemic category: T2 parametric enumeration around the T1b
calibration point established by [WP-V](../wp-hasse-reproduction/).*

-----

## Experiment

The apparatus anchor this map sweeps around. WP-Coastline does not
introduce new lab calibrations; it parametrises the (N, δt/T_m) plane
around the WP-V Hasse point.

- **Anchor point**: η = 0.397, ω_m/(2π) = 1.300 MHz (Hasse 2024 LF
  axial mode); the (N, δt/T_m, Ω, |α|) calibration of
  [WP-V](../wp-hasse-reproduction/README.md) is the point this WP
  varies *around*.
- **Initial state**: pure coherent (no thermal seeding) — see [§3
  Parameters and grid](#3-parameters-and-grid). The mismatch with
  Hasse's experimental ⟨n⟩_thermal = 0.15 is intentional (this is a
  numerical phase diagram, not a lab reproduction).
- **No new procedural choices** — every per-cell Ω calibration is
  derived (option (a)) or held at the WP-V Hasse value (option (b)
  control slice). See [§3.1](#31-ω-calibration--option-a-primary-b-control-slice).

## Analytical

Lemmas, conventions, and the testable hypothesis the χ-collapse
plot is designed to falsify.

- **Lamb–Dicke validity lemma** — splits the engine-validity
  constraint (drive-strength LD) from the physical-picture validity
  constraint (motional-amplitude LD); both are recorded as per-cell
  flags rather than masking data: [§2 Lamb–Dicke validity lemma](#2-lambdicke-validity-lemma-51-resolution-inlined-per-co-lock).
- **Failure-mode rubric** — three regimes (strong-binding,
  pulse-broadening, Doppler merging) discriminated by the (V, P)
  pair: [§4.2 Failure-mode rubric](#42-failure-mode-rubric-plot-caption-interpretive-key).
- **χ-collapse hypothesis** (testable, falsifiable):
  χ² = (1/N)² + (1/(ω_m·δt))² + (η|α|)² with V ∼ exp[−χ²]. v0.1
  reports whether all cells collapse onto a single curve;
  **falsification is a positive result**. See [§4.5](#45-χ-collapse-candidate-34-of-the-memo-testable-hypothesis).
- **Mechanism discriminant** (V/P ratio): distinguishes
  pulse-bandwidth merging from train-shortness merging when both
  primaries collapse — see [§4.4](#44-tertiary-mechanism-discriminant-scout).

## Numerical

The 6×6 (N, δt/T_m) grid plus control slice and Fock-leakage audit.
*Note:* this WP predates `wp_manifest_v1`; its `.h5` artifacts do
not yet carry sidecar manifests.

- **Driver**: [numerics/run_coastline_v1.py](numerics/run_coastline_v1.py)
  — 36-cell grid × 3 detunings × 64 ϑ₀ × 4 |α| ≈ 29 200 evolutions,
  ≤ 2 min on a laptop.
- **Pre-audit**: [numerics/check_fock_leakage_extremes_v1.py](numerics/check_fock_leakage_extremes_v1.py)
  — confirms NMAX policy (60 for |α|≤3, 80 for |α|=5 stretch).
- **Datasets**:
  [numerics/coastline_v1.h5](numerics/coastline_v1.h5) (V, P,
  diamond amplitude, |δ⟨n⟩|_peak per (N, δt/T_m, |α|, δ) cell with
  per-cell validity flags), and
  [numerics/fock_leakage_extremes_v1.h5](numerics/fock_leakage_extremes_v1.h5)
  (extremes audit).
- **α-recovery probe**: [numerics/alpha_recovery_v2.h5](numerics/alpha_recovery_v2.h5),
  [numerics/run_alpha_recovery_v2.py](numerics/run_alpha_recovery_v2.py)
  — finalisation probe per [§9.4 of the council memo](../council-memo-2026-04-21-strong-weak-coastline.md).
- **Plots**: [plots/](plots/) — V/P heatmaps with double LD-hatching,
  χ-collapse falsification panel, secondary observables and option-(b)
  control slice.
- **Schema policy**: [§5 Deliverables](#5-deliverables) lists the
  per-cell datasets and the root-level scalar attributes (ceilings,
  thresholds) explicitly, so consumers know what is per-cell vs.
  per-WP.

-----

## 1. Purpose

Map the crossover between the **strong-binding / resolved-sideband**
regime — in which the stroboscopic protocol resolves a discrete comb at
δ = k·ω_m — and the **weak-binding** regime — in which pulse bandwidth
and/or train shortness merges adjacent teeth into a Doppler-like
continuum. The map is cut along the (N, δt/T_m) axis pair, with Ω
recalibrated per-cell per §3.1 option (a), at three |α| values.

Prior WPs sample exactly one point of this plane:
[WP-V](../wp-hasse-reproduction/README.md) at (N=30, δt/T_m=0.13,
η=0.397, |α|=3) reproduced Hasse Fig 6a/6b within 5%, and the
[2026-04-21 Rabi scan](../wp-hasse-reproduction/logbook/2026-04-21-coh-theta0-det-rabi5x.md)
mapped the orthogonal Ω axis at that same point. The two missing axes
are N (train length) and δt/T_m (pulse bandwidth).

-----

## 2. Lamb–Dicke validity lemma (§5.1 resolution, inlined per co-lock)

Two LD-related scales appear in the stroboscopic engine. They have
different physical origins and differently constrain validity.

**2.1 Drive-strength LD — governs RWA on the carrier.** The effective
pulse Hamiltonian
$$H = (\delta/2)\,\sigma_z + \omega_m\, a^\dagger a + (\Omega/2)\,[\,e^{i\varphi} C \sigma_- + \mathrm{h.c.}\,]$$
(see [scripts/stroboscopic/hamiltonian.py:42](../scripts/stroboscopic/hamiltonian.py#L42))
relies on the rotating-wave approximation on the internal transition.
That approximation requires Ω ≪ ω₀ (laser frequency scale, always
satisfied here) *and*, in the sideband-resolved picture, Ω_eff ≪ ω_m.
We enforce the operational form
$$\Omega_\text{eff}/\omega_m \leq 0.3$$
as the pre-declared hard ceiling (§3.1), where
$\Omega_\text{eff}=\Omega\,e^{-\eta^2/2}$ is the Debye–Waller-suppressed
carrier Rabi frequency. Breaching cells are rendered as hatched
overlays on primary heatmaps — **not excluded, not cropped**.

**2.2 Motional-amplitude LD — does *not* bound engine validity.** The
Doppler-broadened-sideband picture uses the expansion
$e^{i\eta(a+a^\dagger)} \approx 1 + i\eta(a+a^\dagger) + \mathcal O(\eta^2)$,
which requires
$\eta\sqrt{\langle n\rangle + 1} \lesssim 1$ (linear form) or equivalently
$\eta^2(2\bar n+1) \lesssim 1$ (squared form). These thresholds bound
the *physical picture* (discrete-sideband spectroscopy interpretation),
not the engine: the coupling operator is stored as the exact matrix
exponential
$C = \exp[\,i\eta(a+a^\dagger)\,]$
at the full Fock-basis cutoff
([scripts/stroboscopic/operators.py:23](../scripts/stroboscopic/operators.py#L23)),
with no truncation in η. The engine therefore remains numerically valid
for $\eta\sqrt{\langle n\rangle + 1} \gtrsim 1$, provided the Fock
cutoff NMAX contains the spread. We audit NMAX per-cell through the
top-5 Fock leakage and store the result as a per-cell dataset
(`fock_leakage_top5`) inside each alpha group (schema in §5).

**2.3 Binding inequalities per axis of the scan.** At η = 0.397:

| |α| | ⟨n⟩ ≈ |α|² | $\eta\sqrt{\langle n\rangle+1}$ | $\eta^2(2\bar n+1)$ |
|---|---|---|---|
| 0 | 0.00 | 0.397 ✓ | 0.158 ✓ |
| 1 | 1.00 | 0.561 ✓ | 0.473 ✓ |
| 3 | 9.00 | 1.256 ✗ | 3.00 ✗ |
| 5 | 25.00 | 2.026 ✗ | 8.04 ✗ |

✗ flags cells that fall outside the linear motional-LD picture but
**not** outside engine validity. Both diagnostics (drive-LD breach,
motional-LD breach) are written as per-cell (N, δt) boolean datasets
(`ld_flag_drive`, `ld_flag_motional`) inside each alpha group and
rendered with **distinguishable hatching conventions** on all plots
(§5). Cells that breach both are rendered with both hatches layered.

**2.4 |α| = 5 admission.** Because engine validity is governed by (2.1)
alone — and the §3 grid enforces Ω_eff/ω_m ≤ 0.3 — the aspirational
|α| = 5 row of the memo is admissible as a **contingent stress-test of
the ηα scaling in the Doppler-dominated regime**, with the motional-LD
breach recorded inline. v0.1 completeness does *not* require |α| = 5;
it is run as a stretch target after the three-point baseline completes.

-----

## 3. Parameters and grid

Anchors: η = 0.397, pure coherent state (no thermal seeding). Frequency
convention follows the engine (see
[scripts/stroboscopic_sweep.py:51](../scripts/stroboscopic_sweep.py#L51)):
`OMEGA_M = 1.3` is the **angular** mode frequency in rad per engine
time unit. Hasse's physical anchor ω_m/(2π) = 1.3 MHz is recovered by
choosing the engine time unit equal to 2π μs; all dimensionless
observables depend only on η, Ω/ω_m, N, and t_sep_factor and are
unaffected by absolute time scale. Per-cell reporting below uses
Ω_eff/ω_m (dimensionless) throughout, so the coastline results are
independent of the time-unit choice.

All runs use the restructured engine
[scripts/stroboscopic/](../scripts/stroboscopic/) (CODE_VERSION ≥
v1.0.0, bit-for-bit validated against WP-V v4 data per
[2026-04-20 logbook §3](../wp-hasse-reproduction/logbook/2026-04-20-coh-theta0-det.md)).

### 3.1 Ω calibration — option (a) primary, (b) control slice

**Option (a) — recalibrated Ω (primary):** at each (N, δt) set Ω so
that $N\cdot\Omega_\text{eff}\cdot\delta t = \pi/2$, i.e.
$$\Omega = \frac{\pi/2}{N\,\delta t} \cdot e^{+\eta^2/2}.$$

**Hard ceiling:** Ω_eff/ω_m ≤ 0.3. Breaches logged as the per-cell
`ld_flag_drive` dataset (bool, shape (nN, ndt)) and rendered hatched.
Under (a), roughly 10 of 36 cells
breach the ceiling, concentrated in the small-N / small-δt corner —
diagnostic data, not a defect.

**Option (b) — fixed Ω = Ω_Hasse (control slice):** a supplementary row
at δt/T_m = 0.13 with Ω held at the WP-V Hasse value. The control-slice
caption cross-references
[rabi_scan_v5.h5](../wp-hasse-reproduction/numerics/rabi_scan_v5.h5):
features at values of N where $N\cdot\Omega_\text{Hasse}\cdot\delta t$
crosses a Rabi-envelope node are power-broadening artefacts, not
coastline features.

### 3.2 Geometric grid (6 × 6)

- N ∈ {3, 6, 12, 24, 48, 96}     (geometric factor 2)
- δt/T_m ∈ {0.02, 0.05, 0.10, 0.20, 0.40, 0.80}   (geometric factor ≈ 2)
- δ/ω_m ∈ {0, 0.25, 0.5}          (three detunings; 0.25 guards
  against tooth-position drift under recalibrated-Ω scaling)
- ϑ₀ grid: 64 points, endpoint-excluded, phase-shifted by
  $\omega_m\,\delta t/2$ to match WP-V convention
- |α| ∈ {0, 1, 3}                 (scientific baseline)
- |α| = 5                         (contingent stretch; admissible per §2.4)
- NMAX policy                     (driven by pre-audit; see logbook §2):
  NMAX = 60 for |α| ∈ {0, 1, 3} — confirmed safe at the WP-V baseline
  and under 5× Rabi overdrive
  ([fock_leakage_rabi5x_v5.h5](../wp-hasse-reproduction/numerics/fock_leakage_rabi5x_v5.h5));
  NMAX = 80 for the |α| = 5 stretch row — pre-audit top-5 leakage
  4 × 10⁻⁶ at NMAX 60 → 3 × 10⁻¹³ at NMAX 80. The per-cell NMAX used
  is recorded as the `nmax_used` (nN, ndt) dataset inside each alpha
  group, and the group scalar `attrs['nmax']` summarises the policy for
  that |α|.

**Control slice:** additional six points at δt/T_m = 0.13, N sweeping
{3, 6, 12, 24, 48, 96}, Ω fixed at the WP-V Hasse calibration.

### 3.3 Evolution count and compute budget

36 cells × 3 detunings × 64 ϑ₀ ≈ **6,912 evolutions per |α|**, plus
the 6 × 64 = 384 control-slice evolutions per |α|. Four |α| values:
≈ 29 200 evolutions. Budget: ≤ 30 s for |α| = 3; ≤ 2 min for the full
four-value set on a laptop.

-----

## 4. Observables (§4.3 of the memo)

### 4.1 Primary (two-map, no scalar aggregation)

- **Tooth visibility** $V = 1 - \min_{\vartheta_0} |C|(\vartheta_0, \delta=0)$
- **Off-tooth coherence** $P = \langle |C|(\vartheta_0, \delta=0.5\,\omega_m)\rangle_{\vartheta_0}$

### 4.2 Failure-mode rubric (plot-caption interpretive key)

| Regime           | V    | P    |
|------------------|------|------|
| strong-binding   | high | high |
| pulse-broadening | low  | high |
| Doppler merging  | low  | low  |

### 4.3 Secondary (h5 + plotted if discriminatory)

- Diamond amplitude $\tfrac12(\max-\min)\langle\sigma_z\rangle$ at δ=0
- Back-action peak $|\delta\langle n\rangle|_\text{peak}$ at δ=0

### 4.4 Tertiary (mechanism discriminant, Scout)

- Ratio $V/P$ or $(V, P)$ covariance — distinguishes pulse-bandwidth
  merging from train-shortness merging when both primaries collapse.

### 4.5 χ-collapse candidate (§3.4 of the memo, *testable hypothesis*)

$$\chi^2 = (1/N)^2 + \bigl(1/(\omega_m\,\delta t)\bigr)^2 + (\eta|\alpha|)^2$$

with $V \sim \exp[-\chi^2]$ or similar. v0.1 plots all cells against χ
and reports whether they collapse. **Falsification is a positive
result.** The root-sum-square form presumes incoherent-Gaussian
composition of three physically distinct spectral widths; residual
structure is the physics to be learned.

-----

## 5. Deliverables

1. **This README.** Endorsement Marker as line 1 of the file header.
2. [numerics/run_coastline_v1.py](numerics/run_coastline_v1.py) — driver.
3. [numerics/check_fock_leakage_extremes_v1.py](numerics/check_fock_leakage_extremes_v1.py)
   — pre-audit at |α| × δt/T_m extremes (per §2.3 of the memo).
4. [numerics/coastline_v1.h5](numerics/coastline_v1.h5) — V, P, diamond
   amplitude, |δ⟨n⟩|_peak per (N, δt/T_m, |α|, δ) cell, under
   `/alpha_{X}pY/` groups (one per |α|). On-disk schema (reflecting
   what [run_coastline_v1.py](numerics/run_coastline_v1.py) actually
   writes):
   - Observable fields are (nN, ndt) datasets inside each alpha group.
   - Validity flags are sibling (nN, ndt) datasets — `ld_flag_drive`,
     `ld_flag_motional`, `omega_eff_over_omega_m`, `ld_motional_param`,
     `fock_leakage_top5`, `nmax_used` — **not** scalar attributes,
     because they vary per cell. They are kept separate from the
     observables so downstream rendering consumes them as a mask
     channel without mutating raw data.
   - Ceiling values (`omega_eff_ceiling`, `motional_ld_threshold`) are
     root-level scalar attributes.
   - The option-(b) control slice is nested under each alpha group at
     `/alpha_{X}pY/control_fixed_omega_hasse/` as (nN,) datasets. It
     is per-|α| because the slice observables depend on |α|; there is
     no top-level control group.
5. [numerics/fock_leakage_extremes_v1.h5](numerics/fock_leakage_extremes_v1.h5)
   — extremes audit output.
6. [plots/coastline_vp_maps.png](plots/coastline_vp_maps.png) — primary
   V/P heatmaps per |α|, with drive-LD-ceiling breaches hatched
   (convention A, white ///) and motional-LD breaches hatched
   (convention B, red ···; distinguishable, layered independently).
   V maps additionally carry the **impulsive-limit overlay** at the
   δt/T_m → 0 edge (memo §4.5; one V value per N from
   `build_impulsive_train`).
7. [plots/coastline_chi_collapse.png](plots/coastline_chi_collapse.png)
   — all cells against χ of §4.5 with $V$ as y-axis; caption reports
   whether the collapse survives.
8. [plots/coastline_secondary.png](plots/coastline_secondary.png) —
   diamond amplitude and |δ⟨n⟩|_peak panels, plus the option-(b)
   fixed-Ω control slice at δt/T_m = 0.13. Both LD hatching conventions
   are rendered on the heatmap panels.
9. [logbook/2026-04-21-kickoff.md](logbook/2026-04-21-kickoff.md) and
   [logbook/2026-04-21-results.md](logbook/2026-04-21-results.md).

-----

## 6. Relation to other WPs

- [WP-V](../wp-hasse-reproduction/) — fixes (N, δt/T_m, Ω, α). We sweep
  the (N, δt/T_m) plane around that point.
- [WP-E](../wp-phase-contrast-maps/) — fixes (N, δt/T_m, Ω), varies
  (δ₀, |α|, φ_α). Complementary axis set.
- Rabi follow-up
  ([2026-04-21 §6](../wp-hasse-reproduction/logbook/2026-04-21-coh-theta0-det-rabi5x.md))
  — fixes (N, δt/T_m, α), varies Ω. De-conflicted by §3.1 option (a).

The coastline WP closes the (N, δt/T_m) axis pair; other axes (envelope
shape, ω_m, η, Fock truncation) remain untouched. Within that scope it
gives [ideal-limit-principles.md](../ideal-limit-principles.md) a
numerical phase diagram against which to anchor its Lamb–Dicke /
impulsive / resolved-sideband discussion.

-----

## 7. References

- Council memo v0.3: [council-memo-2026-04-21-strong-weak-coastline.md](../council-memo-2026-04-21-strong-weak-coastline.md).
- Tutorial §3.3: [notebooks/00_tutorial_pulse_train.ipynb](../notebooks/00_tutorial_pulse_train.ipynb).
- Hasse 2024 anchor: [refs/Hasse2024_PRA_109_053105.pdf](../refs/Hasse2024_PRA_109_053105.pdf).

-----

*v0.1 (2026-04-21): scaffolded under co-lock resolution of council memo
v0.3 §9.4. §5.1 lemma inlined as §2; §4.2 grid geometry (6×6
geometric), §4.3 two-map observables, §4.4 three-point |α| baseline
with |α|=5 as stretch target all locked. Execution-ready.*
