# WP — Strobo 2.0: Detuning × Motional-Phase Maps for Short Pulse Trains

**Status:** v0.3 executed 2026-04-21 (π/2-calibrated per train).
**Codename:** *strobo 2.0*
**Opened:** 2026-04-21

Two-axis sweep of the Hasse-style coherence contrast, analysis phase,
spin polarisation, and stroboscopic back-action for **short** AC pulse
trains — N = 3 × 100 ns and N = 7 × 50 ns — as a function of train
detuning δ₀ and initial motional-state phase ϑ₀, at three coherent
displacement amplitudes |α| ∈ {1, 3, 4.5}.

Each train is calibrated to deliver a full π/2 analysis rotation on
the ground motional state (Hasse 2024 App. D convention). Because
the two trains have different N·δt, the required Rabi rate is
train-specific: **Ω_T1/(2π) = 0.9008 MHz** and
**Ω_T2/(2π) = 0.7722 MHz**.

Distinct from WP-E (Phase-Contrast Maps, N = 22 weak pulses,
δt = 40 ns). Here we probe a short-train regime with fewer, longer
pulses and near-stroboscopic-resonant inter-pulse spacing
(Δt = 0.77 µs ≈ T_m).

## Folder layout

```
wp-strobo-2p0/
├── README.md      (this file)
├── logbook/
│   ├── 2026-04-21-kickoff.md              (parameters, observables, grid)
│   ├── 2026-04-21-sweep-complete.md       (executed main sweep + findings)
│   ├── 2026-04-21-rabi-reconciliation.md  (three-candidate read-off protocol)
│   ├── 2026-04-21-hasse-fig6-slice.md     ((phi, theta_0) analogue of Hasse Fig. 6)
│   └── 2026-04-22-params-document.md      (JSON parameter-document schema v1.0)
├── params/
│   ├── README.md                          (format + usage)
│   ├── strobo2p0_params.json              (current lab-configuration document)
│   └── load_params.py                     (loader + CLI summariser)
├── numerics/
│   ├── preflight.py                 (four validation tests, ~1 s)
│   ├── run_sweep.py                 (main sweep runner, ~100 s)
│   ├── make_plots.py                (main-sweep figure generator)
│   ├── rabi_calibration.py          (|C|_vacuum vs Omega closed form + check)
│   ├── hasse_fig6_slice.py          ((phi, theta_0) slice at delta_0 = 0, ~17 s)
│   ├── make_fig6_plots.py           (Fig. 6-style figure generator)
│   ├── sweep.log                    (console log of main-sweep run)
│   ├── hasse_fig6.log               (console log of Fig-6-slice run)
│   ├── strobo2p0_data.npz           (main-sweep observables, 1.1 MB)
│   ├── strobo2p0_manifest.json      (main-sweep parameters + schema)
│   └── hasse_fig6_slice.npz         (Fig-6-slice observables, 139 KB)
└── plots/
    ├── 00_rabi_calibration.png      (Omega read-off reference)
    ├── 01_coherence_contrast.png    (|C| heatmap)
    ├── 02_arg_C.png                 (analysis phase phi* heatmap)
    ├── 03_sigma_z.png               (<sigma_z> at phi=0)
    ├── 04_delta_n_phi0.png          (back-action at phi=0)
    ├── 05_delta_n_phi_pi2.png       (back-action at phi=pi/2)
    ├── 06_hasse_fig6_alpha3.png     (Fig-6 analogue, |alpha|=3)
    └── 07_hasse_fig6_alpha4p5.png   (Fig-6 analogue, |alpha|=4.5)
```

## Quick start

Reproduce everything from scratch (≈ 2 minutes total on a laptop):

```sh
# optional: sanity-check the parameter document
python3 params/load_params.py params/strobo2p0_params.json

python3 numerics/preflight.py          # ~1 s
python3 numerics/run_sweep.py --params params/strobo2p0_params.json
                                       # main sweep, ~100 s. Drop --params
                                       # to use the in-file defaults (they
                                       # match strobo2p0_params.json).
python3 numerics/make_plots.py         # plots/01..05_*.png
python3 numerics/rabi_calibration.py   # plots/00_rabi_calibration.png
python3 numerics/hasse_fig6_slice.py   # (phi, theta_0) slice, ~17 s
python3 numerics/make_fig6_plots.py    # plots/06..07_*.png
```

## Entry points

- Parameters, observable definitions, grid, open questions →
  [logbook/2026-04-21-kickoff.md](logbook/2026-04-21-kickoff.md).
- Main-sweep peak values, qualitative findings, next-step list →
  [logbook/2026-04-21-sweep-complete.md](logbook/2026-04-21-sweep-complete.md).
- Rabi-rate candidates + one-measurement read-off protocol →
  [logbook/2026-04-21-rabi-reconciliation.md](logbook/2026-04-21-rabi-reconciliation.md).
- (φ, ϑ₀) analogue of Hasse 2024 Fig. 6 + symmetry checks →
  [logbook/2026-04-21-hasse-fig6-slice.md](logbook/2026-04-21-hasse-fig6-slice.md).
- Calibrated lab-parameter document (JSON schema + loader) →
  [params/README.md](params/README.md) and
  [logbook/2026-04-22-params-document.md](logbook/2026-04-22-params-document.md).
