# WP — Strobo 2.0: Detuning × Motional-Phase Maps for Short Pulse Trains

**Status:** first sweep executed 2026-04-21.
**Codename:** *strobo 2.0*
**Opened:** 2026-04-21

Two-axis sweep of the Hasse-style coherence contrast, analysis phase,
spin polarisation, and stroboscopic back-action for **short** AC pulse
trains — N = 3 × 100 ns and N = 7 × 50 ns — as a function of train
detuning δ₀ and initial motional-state phase ϑ₀, at three coherent
displacement amplitudes |α| ∈ {1, 3, 4.5}.

Distinct from WP-E (Phase-Contrast Maps, N = 22 weak pulses,
δt = 40 ns). Here we probe a short-train regime with fewer, longer
pulses and near-stroboscopic-resonant inter-pulse spacing
(Δt = 0.77 µs ≈ T_m).

## Folder layout

```
wp-strobo-2p0/
├── README.md      (this file)
├── logbook/
│   ├── 2026-04-21-kickoff.md         (parameters, observables, grid)
│   └── 2026-04-21-sweep-complete.md  (executed sweep + findings)
├── numerics/
│   ├── preflight.py                   (four validation tests, ~1 s)
│   ├── run_sweep.py                   (main sweep runner)
│   ├── make_plots.py                  (figure generator)
│   ├── sweep.log                      (console log from the executed run)
│   ├── strobo2p0_data.npz             (all observables, 1.1 MB)
│   └── strobo2p0_manifest.json        (parameters + schema)
└── plots/
    ├── 01_coherence_contrast.png
    ├── 02_arg_C.png
    ├── 03_sigma_z.png
    ├── 04_delta_n_phi0.png
    └── 05_delta_n_phi_pi2.png
```

## Quick start

Reproduce the sweep from scratch (≈ 100 s on a laptop):

```sh
python3 numerics/preflight.py          # optional sanity checks
python3 numerics/run_sweep.py          # produces strobo2p0_data.npz
python3 numerics/make_plots.py         # produces plots/*.png
```

## Entry points

- Parameters, observable definitions, grid, and open questions →
  [logbook/2026-04-21-kickoff.md](logbook/2026-04-21-kickoff.md).
- Peak values, qualitative findings, next-step candidates →
  [logbook/2026-04-21-sweep-complete.md](logbook/2026-04-21-sweep-complete.md).
