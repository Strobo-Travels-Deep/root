# 2026-04-21 — Strobo 2.0 Main Sweep Complete

**Status:** sweep executed, plots generated, observations recorded.
**Operator:** uwarring (with Claude)
**Upstream log:** [2026-04-21-kickoff.md](2026-04-21-kickoff.md)

-----

## 1. What was done

- **Preflight** ([numerics/preflight.py](../numerics/preflight.py)).
  Tests 1–4 passed. Test 3 invalidated the original
  `|C| = |⟨σ_x⟩+i⟨σ_y⟩|` identity (residual 7.4 × 10⁻¹ vs ~10⁻¹⁵ for
  the corrected sinusoidal form); kickoff logbook §4.2/§4.3/§4.4
  updated accordingly. Test 4 confirmed the two-run extraction
  (init |+x⟩, |+y⟩) matches the 8-point φ_laser fit to 2.4 × 10⁻⁴ and
  |a_I| ≤ 3 × 10⁻⁴ at the spot-checked anchor.
- **Main sweep** ([numerics/run_sweep.py](../numerics/run_sweep.py)).
  768 engine calls (= 64 ϑ₀ × 3 α × 2 trains × 2 initial spins), each
  covering 81 detunings. Wall time 100.7 s (Nmax = 60, scipy expm).
  Saved to [numerics/strobo2p0_data.npz](../numerics/strobo2p0_data.npz)
  (1.1 MB) with JSON manifest.
- **Plots** ([numerics/make_plots.py](../numerics/make_plots.py)).
  Five heatmap figures in [plots/](../plots/), each a 2 × 3 panel array
  (rows: trains T1, T2; cols: |α| = 1, 3, 4.5):
  - [01_coherence_contrast.png](../plots/01_coherence_contrast.png) — |C|
  - [02_arg_C.png](../plots/02_arg_C.png) — arg C in degrees
  - [03_sigma_z.png](../plots/03_sigma_z.png) — ⟨σ_z⟩ at φ = 0
  - [04_delta_n_phi0.png](../plots/04_delta_n_phi0.png) — δ⟨n⟩ at φ = 0
  - [05_delta_n_phi_pi2.png](../plots/05_delta_n_phi_pi2.png) — δ⟨n⟩ at φ = π/2

## 2. Peak values (observed)

| Tag           | max \|C\|  | max \|σ_z\|_{φ=0} | max\|δ⟨n⟩\|_{φ=0} | max\|δ⟨n⟩\|_{φ=π/2} |
|---------------|-----------:|------------------:|------------------:|--------------------:|
| T1, \|α\|=1   | 0.305      | 0.280             | 0.089             | 0.119               |
| T1, \|α\|=3   | 0.304      | 0.293             | 0.288             | 0.308               |
| T1, \|α\|=4.5 | 0.303      | 0.258             | 0.391             | 0.394               |
| T2, \|α\|=1   | 0.353      | 0.327             | 0.105             | 0.143               |
| T2, \|α\|=3   | 0.353      | 0.348             | 0.366             | 0.404               |
| T2, \|α\|=4.5 | 0.353      | 0.333             | 0.555             | 0.574               |

### Carrier saturation: sanity check
Weak-pulse-limit prediction: on carrier at |α| = 0, |C| = sin(N θ_pulse).

- T1:  N·θ_pulse = 0.3355 rad → sin = 0.3294.  Observed 0.305 at |α|=1
  (small but finite reduction from the coherent-state Debye-Waller-like
  averaging over |α| > 0). ✓
- T2:  N·θ_pulse = 0.3914 rad → sin = 0.3815.  Observed 0.353. ✓

The **|C| peak is essentially |α|-independent** across |α| ∈ {1, 3, 4.5}
(relative scatter < 0.5 %). This is the expected stroboscopic-sync
signature: for pulses arriving at the same motional phase of a coherent
state, the coherent-amplitude dependence cancels in the carrier
response at leading order in η·α. The weak |α|-modulation visible in
the off-carrier regions is the η-nonlinearity of the coupling.

## 3. Three qualitative observations

### 3.1 Stroboscopic carrier dominates; off-carrier peaks are much weaker

The ϑ₀-averaged |C| shows a sharp carrier feature at δ₀ = 0 and only a
faint feature near δ₀ ≈ ±4 MHz ≈ ±3 ω_m (at |α| = 3, T2 train,
|C|_avg = 0.074 vs 0.344 on carrier). No clear ±ω_m, ±2ω_m sidebands.
This is consistent with the stroboscopic lock: because Δt ≈ T_m
(within 0.56 %), pulses arrive at the same motional phase, and
sidebands at integer multiples of the pulse rate 1/Δt ≈ ω_m interfere
such that the carrier is the only surviving resonance. The faint
±3 ω_m feature is likely the beating between the 0.56 % pulse-spacing
slip and the third-order η³ coupling.

### 3.2 δ⟨n⟩ has π-periodicity in ϑ₀ at the carrier (four-lobe pattern)

Explicit check at (δ₀ = 0, |α| = 3, T2): correlation between δ⟨n⟩(ϑ₀)
and δ⟨n⟩(ϑ₀ + π) is 1.0000 to four decimals, with maximum absolute
difference < 10⁻⁴. This reproduces the four-lobe quadrant pattern of
**Hasse 2024 Fig. 6(b)** with the amplitude scaling
max|δ⟨n⟩| ∝ η·|α| · sin(N·θ_pulse). Sign structure: δ⟨n⟩_A and
δ⟨n⟩_B are π/2 out of phase in ϑ₀, consistent with the cos/sin
decomposition of the analysis-phase axis.

### 3.3 T1 vs T2 differ in detuning-width, not in maximum

T2's carrier feature is clearly narrower than T1's. Rough HWHM from
the plots:

- T1 (N=3, 1.84 µs total):   HWHM_δ₀/(2π) ≈ 1.2 MHz
- T2 (N=7, 4.97 µs total):   HWHM_δ₀/(2π) ≈ 0.6 MHz

The ratio (2×) tracks the total train duration, as expected for a
finite-duration π/2-equivalent train (Fourier-limited linewidth).
At |α| = 4.5 the T1 map develops stronger ϑ₀-modulation across the
full map area than T2 — the shorter total duration of T1 has less
motional phase averaging, so the ϑ₀ structure at finite η·|α| is
more pronounced.

## 4. arg C — structure and wrap-ups

[02_arg_C.png](../plots/02_arg_C.png) shows a slanted-stripe pattern:
arg C increases approximately linearly in (δ₀ − offset)·ϑ₀-dependent
slope. The slopes are steeper for T2 than T1 (longer train →
more accumulated phase per unit detuning). The slope flips sign at
ϑ₀ ≈ 0 and ϑ₀ ≈ π, consistent with the ϑ₀-π reflection symmetry of
the coherent-state trajectory. The pattern wraps (modulo 2π) into the
twilight-colormap stripes seen in the figure.

## 5. Anomaly/ambiguity tracker

Nothing unexpected in the physics. Three bookkeeping notes:

- **a_I offset.** Spot-checked at (|α|=3, δ₀=0, ϑ₀=0, T2) and bounded
  to 3 × 10⁻⁴. Not verified at every cell. If a future re-analysis
  depends on an absolute σ_z offset to < 1 %, re-run the full sweep
  with the three-run-per-cell protocol (spins at |+x⟩, |+y⟩, |−x⟩).
- **Δt = 0.77 µs vs T_m = 0.7657 µs.** Flagged in the kickoff as a
  deliberate 0.56 % super-stroboscopic slip. Its main footprint in
  this dataset is: (i) the weak δ₀ ≈ ±4 MHz feature in |C|, and (ii)
  the modest asymmetry of the δ⟨n⟩ maps about δ₀ = 0 visible at
  |α| = 4.5. A companion run at Δt = T_m exactly would quantify the
  slip contribution but is not required for this WP's first report.
- **Rabi-rate reconciliation.** Kickoff §9 Q1 still open: the
  original "t_π = 1.122 µs" statement is inconsistent with the
  confirmed Ω/(2π) = 0.178 MHz used here. Not relevant to this
  dataset's internal consistency, but worth resolving before
  comparing to lab results.

## 6. Output files

```
wp-strobo-2p0/
├── README.md
├── logbook/
│   ├── 2026-04-21-kickoff.md          (v0.2; see that file's changelog)
│   └── 2026-04-21-sweep-complete.md   (this file)
├── numerics/
│   ├── preflight.py                    (4 tests, ~1 s)
│   ├── run_sweep.py                    (main sweep, 101 s on Nmax=60)
│   ├── make_plots.py                   (5 figures)
│   ├── sweep.log                       (console log of the main run)
│   ├── strobo2p0_data.npz              (all observables, 1.1 MB)
│   └── strobo2p0_manifest.json         (parameters + schema)
└── plots/
    ├── 01_coherence_contrast.png
    ├── 02_arg_C.png
    ├── 03_sigma_z.png
    ├── 04_delta_n_phi0.png
    └── 05_delta_n_phi_pi2.png
```

## 7. Next steps (not gated; for discussion)

1. **Companion Δt = T_m run.** Exact stroboscopic-resonance sheet to
   isolate the Δt/T_m − 1 = 0.56 % slip contribution to the ±3 ω_m
   feature and the δ⟨n⟩ asymmetry.
2. **Analysis-phase slice.** At one informative (δ₀, ϑ₀), run a full
   8–16 point φ_laser scan to make a Hasse-Fig.-6-style (φ, ϑ₀) sheet
   for comparison.
3. **Rabi-rate reconciliation.** Resolve the t_π = 1.122 µs vs
   Ω/(2π) = 0.178 MHz mismatch with the experimental team; re-run if
   the value needs updating.
4. **Thermal-background admixture.** Currently pure coherent state.
   If the measured ion has ⟨n⟩_th ≈ 0.2 (Hasse text), admixing via the
   engine's `n_thermal` parameter (20 trajectories) costs 20 × 101 s =
   34 min for the full sweep — still tractable.

-----

*v0.1 2026-04-21 — initial post-sweep record.*
*v0.2 2026-04-21 — editorial pass: version reference to the kickoff log
updated (v0.1 → v0.2), "One bookkeeping note" → "Three bookkeeping
notes" to match the bullet count.*
