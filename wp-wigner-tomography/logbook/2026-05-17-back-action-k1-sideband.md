# Logbook — 2026-05-17 — back-action k=1 sideband follow-up

**Status.** Follow-up execution after the v0.6 back-action diagnostic.
The parked v0.6 run deliberately used the carrier tooth (`k=0`) to
match the P1/D3/D4-Layer-B convention. This run exercises the first
sideband tooth (`k=1`) with the same matched-control policy, so the
native Raman leg is probed in the sideband/Jaynes-Cummings-like
regime flagged as the natural next extension in the 2026-05-16 run
logbook.

**Headline outcome.**

- **Vacuum analytic gate still PASSes at machine precision.** The
  ideal leg is tooth-independent after the inverse-Dirichlet
  subtraction of `k·omega_m`; the hard P0/P1-style anchor therefore
  remains the same: purity/fidelity residuals ≤ `2e-14`, Wigner
  residual ≤ `1.3e-10`.
- **The original v0.6 states are not the most sensitive sideband
  witnesses.** Vacuum, Fock `|2>`, and the `|alpha|=1.5` cat are
  numerically close to their carrier-tooth native results at the two
  locked probe points. That is a useful negative result: the k=1
  follow-up needs a coherent input to show the expected native
  sideband response cleanly.
- **Coherent `|alpha|=2` is the useful anchor.** At the peak probe,
  the native leg stays nearly pure (`purity_drop = 0.050`) but no
  longer resembles either the input (`F_pre = 0.049`) or an ideal
  `sigma_x` SDF branch (`sigma_x` branch `F = 0.037`). The ideal leg
  remains branch-exact (`F = 1.000`) by construction. This is the
  sideband version of the structural finding: the native sideband
  drive moves the oscillator in a way the ideal branch-split model
  does not describe.

-----

## 1. Pre-registered expectations

- **Comb tooth:** `k=1` first sideband. Matched control remains
  identical to v0.6: the ideal leg defines `beta_tot`; the native leg
  receives the same inverse-Dirichlet-assigned
  `(delta - k omega_m, phi_train, N)`. No `beta_eff` calibration.
- **Hard gate:** unchanged from v0.6. Vacuum, ideal SDF, `|+y>` in:
  purity `= 1/2(1 + exp(-|beta_tot|^2))`, fidelity
  `= exp(-|beta_tot|^2/4)`, and
  `W = W_mixed_cat(beta_tot/2)`, all within `1e-6`.
- **Inputs:** keep the v0.6 headline set and add coherent `|alpha|=2`.
  The earlier scratch choice `|alpha|=3` was rejected because it sits
  on the edge of the validated `[-3,3]` Wigner window; widening the
  window exposed high-alpha Fock-truncation artefacts in the parity
  Wigner diagnostic. `|alpha|=2` stays inside the validated window
  while retaining the coherent-state sideband witness.
- **Metrics:** state-space purity, fidelity-to-pre, and conditional
  `sigma_x` branch fidelity are the primary sideband readouts. Wigner
  `L^1` remains a reported structural diagnostic, not a gate.

## 2. Execution

Runner and plot code were made tooth-aware before the run:

- `run_back_action.py --k-sideband K` now writes `back_action_kK.h5`
  by default for non-carrier teeth, leaving the parked
  `back_action.h5` carrier artefact untouched.
- `--inputs` accepts pure-state labels such as `coherent2`, and the
  HDF5 carries `inputs_json` so the plotter is data-driven.
- `plot_back_action.py` reads the input list from HDF5 and writes
  `back_action_k1.png` automatically for the sideband artefact.

Commands run from the repository root:

```bash
python wp-wigner-tomography/numerics/run_back_action.py \
  --k-sideband 1 --inputs vacuum coherent2 fock2 cat1.5
python wp-wigner-tomography/plots/plot_back_action.py \
  --h5 wp-wigner-tomography/numerics/back_action_k1.h5
python -m pytest \
  wp-wigner-tomography/numerics/test_back_action_helpers.py \
  scripts/stroboscopic/tests/test_ideal_sdf.py -q
```

| artefact | path |
|---|---|
| runner | [`numerics/run_back_action.py`](../numerics/run_back_action.py) |
| HDF5 | [`numerics/back_action_k1.h5`](../numerics/back_action_k1.h5) |
| manifest | [`numerics/back_action_k1.manifest.json`](../numerics/back_action_k1.manifest.json) |
| figure | [`plots/back_action_k1.png`](../plots/back_action_k1.png) |
| plotter | [`plots/plot_back_action.py`](../plots/plot_back_action.py) |

Runtime: 140.5 s. Tests: **36 passed**.

## 3. Vacuum gate

| point | `|beta_tot|` | purity residual | fidelity residual | Wigner residual |
|---|---:|---:|---:|---:|
| peak | 1.50 | `6.66e-16` | `3.33e-16` | `1.28e-10` |
| mid | 0.75 | `1.83e-14` | `1.34e-14` | `2.36e-12` |

The gate uses the validated `[-3,3]`, `41^2` parity-Wigner axis.
Runner support for a separate gate axis was added after a scratch
wide-window test showed that evaluating displaced parity at
`|alpha|=5` hits the nmax=60 truncation edge. The production k=1
artefact uses the original validated Wigner window, so this issue is
not present in the committed data.

## 4. Diagnostic results

Native-leg state-space and structural metrics:

| input | point | native drop | native `F_pre` | native `sigma_x` branch F | ideal-vs-native W `L1` |
|---|---|---:|---:|---:|---:|
| vacuum | peak | 0.0560 | 0.9326 | 0.3023 | 0.8103 |
| vacuum | mid | 0.0266 | 0.9846 | 0.7741 | 0.2508 |
| coherent `|alpha|=2` | peak | 0.0504 | 0.0486 | 0.0372 | 1.6930 |
| coherent `|alpha|=2` | mid | 0.0235 | 0.0730 | 0.0598 | 1.7357 |
| Fock `|2>` | peak | 0.2766 | 0.7092 | 0.0530 | 1.8075 |
| Fock `|2>` | mid | 0.1161 | 0.9337 | 0.4479 | 0.9167 |
| cat `|alpha|=1.5` | peak | 0.3923 | 0.1465 | 0.1937 | 1.8656 |
| cat `|alpha|=1.5` | mid | 0.1636 | 0.1996 | 0.2261 | 1.9987 |

The ideal leg remains the reference branch split at every row:
`sigma_x` branch fidelity = `1.0000`. The coherent input is the
cleanest qualitative sideband witness: native evolution remains
nearly pure but lands far from the input and far from either ideal
SDF branch. That is a motional-side signature of the operator
mismatch, not an inversion or plotting issue.

Comparison to the parked carrier artefact for the three shared
states is intentionally modest: peak native metrics shift only at
roughly the `1e-3`–`1e-2` level for vacuum/Fock/cat. The sideband
follow-up therefore does **not** retroactively change the v0.6
carrier conclusion; it adds a coherent-state witness that the
minimal v0.6 input subset did not contain.

## 5. Interpretation and next decision

This run closes the specific k=1 follow-up promised by the v0.6
logbook. It confirms that the hard ideal-SDF machinery is tooth-safe
and that coherent inputs make the native sideband mismatch visible
in state space. It does **not** attempt a full collapse-revival map:
there is still only one matched-control train, two beta probe
points, and no scan over coherent phase, detuning, or train length.

Natural next scope, if needed: a small sideband map on coherent
inputs, varying one of `(N, delta offset, coherent phase)`, with
state-space fidelity as the primary observable and Wigner panels only
for representative points.
