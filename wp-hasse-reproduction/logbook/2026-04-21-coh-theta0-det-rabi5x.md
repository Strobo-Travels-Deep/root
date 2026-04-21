# Logbook — 2026-04-21 — (ϑ₀, δ) scan at 5× Rabi + back-action

**Context.** Follow-up to
[2026-04-20-coh-theta0-det.md](2026-04-20-coh-theta0-det.md). Same
Hasse-matched parameters on the restructured stroboscopic package
([v1.0.0-restructure](../../scripts/stroboscopic/)), except Ω is
multiplied by RABI_SCALE = 5 relative to the π/2-calibrated baseline.
Also finally rendering the back-action δ⟨n⟩ = ⟨n⟩_final − |α|²,
which was being stored in the v5 h5 but never plotted.

Driver: [run_coh_theta0_det_v5_rabi5x.py](../numerics/run_coh_theta0_det_v5_rabi5x.py).
Output: [coh_theta0_det_v5_rabi5x.h5](../numerics/coh_theta0_det_v5_rabi5x.h5).
Compute: 16.9 s wall for 64 × 201 = 12 864 evolutions.

Drive budget:

| quantity | baseline (v5) | 5× run |
|---|---|---|
| Ω | 0.0902 | 0.4508 |
| Ω·δt per pulse | π/(2N) = 0.017 rad | 5π/(2N) = 0.087 rad |
| train total N·Ω_eff·δt | **π/2** (calibrated) | **5π/2 = 2.5 π** (overdriven) |

Everything else is identical: α = 3, η = 0.397, ω_m = 1.3,
N = 30, δt = 0.13·T_m, MW π/2 at phase 0°, AC phase 0°,
intra_pulse_motion on, center_pulses_at_phase on, n_max = 60.

-----

## 1. Headline — comb teeth fatten, off-tooth coherence partly breaks

| field | 1× baseline | 5× this run |
|---|---|---|
| `⟨σ_x⟩` range | [−1.00, +1.00] | [−1.00, +1.00] |
| `⟨σ_y⟩` range | [−0.999, +1.00] | [−0.999, +0.998] |
| `⟨σ_z⟩` range | [−0.949, +0.948] | **[−0.993, +0.974]** |
| `|C|` range | [0.075, 1.00] | [0.055, 1.00] |
| `δ⟨n⟩` range | (not plotted) | **[−1.15, +1.31]** |

Three qualitative changes vs the baseline:

1. **Comb teeth visibly widen.** In the baseline, tooth HWHM in δ/ω_m is
   ≈ 1/N = 0.033 (pulse-train finite-length limited). At 5× the tooth
   width is dominated by the single-pulse Rabi broadening
   Ω_eff = Ω · e^{−η²/2} ≈ 5× baseline. The `|C|` map
   ([coh_theta0_det_rabi5x_coh_abs_v5.png](../plots/coh_theta0_det_rabi5x_coh_abs_v5.png))
   makes this obvious.

2. **σ_z is no longer ≈ 0 off-tooth.** At 2.5 π train rotation, the spin
   completes multiple Rabi cycles even well off resonance, so
   `⟨σ_z⟩(ϑ₀, δ)` carries finite ϑ₀-modulated structure everywhere in
   the δ window, not just at integer δ/ω_m. Compare the broad blue/red
   striping across the entire 5× σ_z map with the near-zero off-tooth
   regions in the baseline σ_z map.

3. **Internal ϑ₀-substructure inside each tooth.** Both σ_z and δ⟨n⟩
   show secondary extrema within a single comb tooth, not present in
   the baseline. This is overdrive ringing: multiple Rabi cycles
   elapse during the pulse-train window at each tooth, giving extra
   nodes in the on-resonance response.

-----

## 2. Back-action δ⟨n⟩

[coh_theta0_det_rabi5x_delta_n_v5.png](../plots/coh_theta0_det_rabi5x_delta_n_v5.png).
Peak deviation ±1.31 phonons, comparable to the Fig 6b baseline's
±1.11 despite a 5× stronger drive. Two observations:

### 2.1 Back-action is tooth-localized
Away from comb resonances, δ⟨n⟩ ≈ 0: the pulse train neither cools nor
heats the coherent state that it is off-resonance with. All phonon
exchange happens at δ = k·ω_m. This was implicit in Fig 6b (which is
the δ = 0 slice) but becomes a real statement once we see the full δ
range.

### 2.2 Back-action saturates in drive strength
That peak δ⟨n⟩ values stay near unity across a 5× Ω change is
consistent with each comb tooth saturating at a similar motional
displacement: a strong resonant drive quickly achieves the full
coherent-state population transfer implied by the Lamb-Dicke parameter
and the available spin-motion coupling, so there is no further
increase as Ω grows. This is an interesting separate statement from
the Fig 6b headline about the ϑ₀-structure and warrants a clean 1D
scan (δ⟨n⟩_peak vs Ω·RABI_SCALE) to quantify the saturation.

-----

## 3. What this says about the Hasse regime

Hasse operates at the calibrated π/2 budget (RABI_SCALE = 1). The
Fig 6 narrative — narrow comb teeth, off-resonance coherence
preserved, saturated on-resonance back-action — is a property of that
calibration. Going to 5× puts the system into a genuinely different
regime where:

- the "flat coherence background + narrow collapses" picture breaks,
- the Fig 6a diamond grows secondary nodes,
- but the δ⟨n⟩ magnitude on-tooth does not scale with Ω.

The qualitative robustness of the Fig 6a/6b structure at Ω×5 (comb
positions unchanged, ϑ₀-symmetry of the diamond preserved under
symmetry transformations of the substructure) suggests the underlying
Hasse theorems about ϑ₀-dependence survive outside the calibrated
regime. A quantitative comparison of diamond amplitudes vs RABI_SCALE
would close this out.

-----

## 4. Loose ends

1. **Overdrive vs Hasse** — run a 1D scan of RABI_SCALE ∈ [0.2, 5]
   at fixed (ϑ₀, δ), e.g. on the (ϑ₀=π/2, δ=0) tooth, and record the
   diamond amplitude and δ⟨n⟩-peak vs Ω. Expected: saturation of
   δ⟨n⟩, monotonic broadening of the tooth HWHM, eventual loss of
   the clean diamond at very high Ω.
2. **Single-tooth zoom at 5×** — δ/ω_m ∈ [−0.3, +0.3] at 201 points
   would resolve the internal ϑ₀-substructure inside one tooth and
   make the secondary nodes legible. Cheap; few seconds.
3. **Fix arg C alpha mask** — baseline logbook note still applies;
   should alpha-mask by (1 − |C|) so that on-tooth collapse regions
   are visible and off-tooth winding is suppressed.
4. **Fock cutoff check** — at 5× overdrive with `|α| = 3`, verify
   `fock_leakage` stays below a safe threshold; NMAX = 60 was ample
   at 1× but deserves a re-check under stronger driving. (Quick;
   `hs.fock_leakage(psi, top_k=5)` on a handful of worst-case points.)

-----

## 5. Status

WP-V and WP-E remain closed at their respective versions. This run is
logged as an exploratory companion to the 2026-04-20 baseline entry.
The back-action panel and RABI_SCALE attribute are now first-class in
the `(ϑ₀, δ)` scan pipeline; any follow-up over the same grid can
toggle `RABI_SCALE` at the top of the driver to sweep drive strength
without further code changes.

Code path: `HilbertSpace` + `build_pulse_hamiltonian` + `build_U_pulse`
+ `build_U_gap` + `StroboTrain`, identical to the baseline. Only the
`OMEGA_R` constant changed.

-----

## 6. Follow-up 1 — Rabi-amplitude scan at δ = 0

Driver: [run_rabi_scan_v5.py](../numerics/run_rabi_scan_v5.py).
Output: [rabi_scan_v5.h5](../numerics/rabi_scan_v5.h5),
[rabi_scan_v5.png](../plots/rabi_scan_v5.png).
Grid: RABI_SCALE ∈ [0.2, 5.0] at 25 linear points × 64 ϑ₀. Compute
1.9 s wall for 1600 evolutions.

**Headline — the "saturation" claim in §2.2 above is wrong.** All
three figures of merit *oscillate* with drive in a clean sinc-envelope
pattern, not saturate:

| RABI_SCALE | diamond amp \|⟨σ_z⟩\| | \|δ⟨n⟩\|_peak | ⟨\|C\|⟩ | min \|C\| |
|---|---|---|---|---|
| 0.2 | 0.238 | 0.309 | 0.964 | 0.981 |
| 0.6 | 0.628 | 0.836 | 0.851 | 0.686 |
| **1.0 (baseline)** | **0.786** | **1.111** | **0.685** | **0.214** |
| 1.2 | 0.756 | 1.126 | 0.642 | 0.029 |
| 2.0 | 0.134 | 0.453 | 0.735 | 0.594 |
| 3.0 | 0.758 | 1.130 | 0.696 | 0.066 |
| 4.0 | 0.244 | 0.593 | 0.957 | 0.835 |
| 5.0 | 0.678 | 0.923 | 0.742 | 0.541 |

The diamond amplitude and δ⟨n⟩ peak both peak near RABI_SCALE ≈ 1
(first envelope peak), collapse near RABI_SCALE ≈ 2 (train rotation =
π), revive at RABI_SCALE ≈ 3, and dip again at RABI_SCALE ≈ 4. This
is the ordinary N-pulse Rabi envelope over the (δ = 0) tooth, shifted
and stretched by the intra-pulse-motion term.

### 6.1 Three structural findings

1. **Calibration is a local optimum, not an arbitrary choice.** The
   π/2-budget calibration `N·Ω_eff·δt = π/2` sits at the first peak
   of the Rabi-amplitude envelope. Hasse's parameter regime is not a
   compromise — it is the unique point where the diamond is largest
   for the smallest drive. Any overdrive moves down the envelope
   before reaching the next peak at RABI_SCALE ≈ 3.

2. **5× sits between peaks 3 and 4.** The value we ran in §1-2 is not
   at an envelope extremum — it's ~20% below peak 3 on the decline.
   This explains the intermediate diamond amplitude 0.678 we saw and
   also why internal ϑ₀-substructure appeared (multi-node Rabi
   dynamics per tooth, not a saturated response).

3. **\|C\| and diamond amplitude are anticorrelated, not linked.**
   Minimum \|C\| across ϑ₀ touches zero at RABI_SCALE ≈ 1.2 and again
   at ≈ 3.2, and recovers between (where the diamond is small).
   Interpretation: the coherence-collapse regions at the centre of
   the tooth are exactly where the train has rotated enough to drive
   a full ϑ₀-locked π-flip; between Rabi peaks the ϑ₀ averaging does
   not collapse the Bloch vector.

### 6.2 What this corrects in §2

§2.2 claimed δ⟨n⟩ "saturates in drive strength." It does not. The
peak-to-peak variation in δ⟨n⟩_peak across [0.2, 5] is 1.13 − 0.31
= 0.82 phonons, i.e. a factor 3.6×. The near-equality of the
baseline (1.11) and 5× (0.92) peaks was coincidence, not a plateau.

-----

## 7. Follow-up 2 — Single-tooth zoom at 5×

Driver:
[run_single_tooth_rabi5x_v5.py](../numerics/run_single_tooth_rabi5x_v5.py).
Output: [single_tooth_rabi5x_v5.h5](../numerics/single_tooth_rabi5x_v5.h5),
three plots `single_tooth_rabi5x_{sigma_z, coh_abs, delta_n}_v5.png` in
[plots](../plots/). Grid: 64 ϑ₀ × 201 δ points in δ/ω_m ∈ [−0.3, +0.3].
Compute 16.2 s.

Ranges on the zoomed grid:

| field | range |
|---|---|
| `⟨σ_z⟩` | [−0.929, +0.986] |
| `|C|` | [0.041, 1.000] |
| `δ⟨n⟩` | [−1.183, +1.270] |

The zoomed `|C|` map
([single_tooth_rabi5x_coh_abs_v5.png](../plots/single_tooth_rabi5x_coh_abs_v5.png))
now resolves the tooth structure visually:

- **Tooth HWHM** ≈ 0.05 in δ/ω_m (widened from baseline 1/N = 0.033).
- **Three distinct dark lobes** inside the main tooth, centred near
  δ/ω_m ∈ {−0.035, 0, +0.035}, arranged as ϑ₀-dependent "eye"
  structures. These are the overdrive Rabi-cycle nodes that were
  unresolved at the ±3 zoom.
- **ϑ₀-antisymmetry survives** — the σ_z substructure under
  ϑ₀ → 2π − ϑ₀ still flips sign, confirming that overdrive does not
  break the symmetry argument behind Fig 6a.

-----

## 8. Follow-up 3 — arg C with `(1 − |C|)` alpha mask

Driver: [plot_arg_c_masked_v5.py](../numerics/plot_arg_c_masked_v5.py),
re-reads both existing h5 outputs from §1 and §6 (baseline + 5×) and
re-renders arg C with the alpha inverted. Outputs:
[coh_theta0_det_coh_arg_masked_v5.png](../plots/coh_theta0_det_coh_arg_masked_v5.png),
[coh_theta0_det_rabi5x_coh_arg_masked_v5.png](../plots/coh_theta0_det_rabi5x_coh_arg_masked_v5.png).

With `alpha = 1 − |C|`, the phase map cleanly isolates the comb teeth:
off-tooth the plot is nearly transparent, and the ϑ₀-dependent phase
structure at each resonance is now legible instead of being drowned by
the rapid global winding. This is the right convention for reading
arg C maps in stroboscopic scans and should replace the baseline
alpha-by-\|C\| rendering in any follow-up figures.

-----

## 9. Follow-up 4 — Fock-cutoff leakage check

Driver:
[check_fock_leakage_rabi5x_v5.py](../numerics/check_fock_leakage_rabi5x_v5.py).
Output: [fock_leakage_rabi5x_v5.h5](../numerics/fock_leakage_rabi5x_v5.h5).
Scans 64 × 81 worst-case grid (δ-zoomed at 5× Rabi) at three NMAX
truncations, reporting top-3 and top-5 Fock-level population:

| NMAX | ⟨n⟩ range | worst top-3 leak | worst top-5 leak |
|---|---|---|---|
| 40 | [7.82, 10.27] | 1.3e-9 | 1.2e-8 |
| **60** (used in scans) | [7.82, 10.27] | **2.4e-21** | **4.9e-20** |
| 80 | [7.82, 10.27] | 3.6e-35 | 9.8e-34 |

**Verdict — NMAX = 60 is safe at 5× Rabi, by a large margin.** Worst
top-5 leakage is 4.9 × 10⁻²⁰, 12 orders of magnitude below the 1e-8
safety threshold. Even NMAX = 40 would have held (1.2e-8 top-5, at
the safety boundary). The exponential convergence from 40 → 60 → 80
(decades per 20 levels) is consistent with a coherent-state tail whose
Poisson cutoff at n ≈ |α|² + 6√(|α|²) = 9 + 18 = 27 is well below the
NMAX = 60 basis. No re-runs needed; §1–2 and §6–7 data are trustworthy.

-----

## 10. Updated status

All four loose ends from §4 are closed. The main correction to the
earlier narrative: §2.2 stated back-action saturates with Ω, but §6
shows it oscillates with N·Ω_eff·δt in the expected Rabi-envelope
pattern, with the Hasse calibration at the first peak. Follow-up
artifacts added to the pipeline:

- `rabi_scan_v5.{h5,png}` — drive-strength sweep at δ = 0
- `single_tooth_rabi5x_v5.*` — zoomed tooth structure at 5×
- `coh_theta0_det_coh_arg_masked_v5.png` + `..._rabi5x_...` — corrected
  arg C alpha convention
- `fock_leakage_rabi5x_v5.h5` — NMAX provisioning record

Each follow-up driver is self-contained and parametrised at the top
of the file; further sweeps (e.g., over `RABI_SCALE` at a different
δ, or over a different ϑ₀ density) are one-line edits.

-----

## 11. Patch note (2026-04-21, consistency pass)

Cross-checked the text against the committed h5/driver artifacts. All
tabulated ranges (§1, §6, §7, §9), file paths, grid shapes, and
compute-time comments reproduce from the on-disk data. Two corrections
to the narrative above — originals kept in place for traceability:

### 11.1 Drive-budget table (§1) — units mislabelled

The middle row of the §1 table reads

> | Ω·δt per pulse | π/(2N) = 0.017 rad | 5π/(2N) = 0.087 rad |

The values 0.017 and 0.087 are **coefficients of π**, not radians:
π/(2·30) = 0.0524 rad and 5π/(2·30) = 0.262 rad. Separately, the row
label "Ω·δt" names Ω, but the formula π/(2N) is Ω_eff·δt (differs by
the Debye–Waller factor e^{−η²/2} = 0.924); the true Ω·δt at baseline
is 0.0902 × 0.628 = 0.0567 rad. The third row `N·Ω_eff·δt = π/2 vs
5π/2` is the physically load-bearing one and is correct as stated.

### 11.2 Single-tooth symmetry claim (§7) — softer than written

§7 bullet 3 asserts "ϑ₀-antisymmetry survives — the σ_z substructure
under ϑ₀ → 2π − ϑ₀ still flips sign." Pointwise this is not what the
h5 data shows: σ_z(ϑ₀, δ) + σ_z(2π − ϑ₀, δ) has max deviation ≈ 1.63
on the single-tooth grid (σ_z range ≈ ±1), and the baseline
coh_theta0_det_v5 data is similarly non-antisymmetric under this map
(max ≈ 1.83). Rough ϑ₀ → 2π − ϑ₀ *symmetry* (not antisymmetry) holds
on the baseline and single-tooth data with residual ≈ 0.33/0.36, and
is partially broken at 5× across the wide ±3 δ window (residual ≈ 1.97).

The qualitative point — overdrive does not obviously destroy the
ϑ₀-structure inherited from Fig 6a — still stands visually, but the
specific statement about antisymmetry should be read as a
visual-pattern description of the substructure, not a pointwise
symmetry of the full map. A proper symmetry audit against the Hasse
argument (which invariance the theorem actually predicts, and under
what joint ϑ₀/δ/φ_AC transformation) is a separate loose end worth
opening before this claim is repeated.

Neither correction changes the numerics or the §6/§6.2 correction of
the "saturation" narrative.
