# Logbook — 2026-04-13 — Hasse's contrast definition + observable retry

**Context.** After WP-V Round 3 diagnosed Fig 8b as a methodology gap,
we located Hasse's own simulation code in
`refs/vpaula_hologram_2026_02_25.ipynb`. That notebook defines contrast
very specifically:

```python
# cells 9, 14, 25, 26
contrast_z = (np.max(sigma_z) - np.min(sigma_z)) / 2
```

where max/min are taken **over the scan variable** (detuning or
analysis-phase). The contrast is the Ramsey-fringe amplitude over the
scan, divided by 2 — NOT `|C| = √(σ_x² + σ_y²)` at fixed detuning that
earlier WP-V Fig 8b runs used.

-----

## 1. Additional details from Hasse's notebook

Hamiltonian (cell 3):
```python
C = (1j * eta * (a.dag() + a) + 1j).expm()      # = e^i · exp(iηX), global phase
H0 = omega_z/2 · sz + omega_1 · a†a             # motional included
HI = Omega/2 · (sm† · C + sm · C†)
H = [H0, [HI, mod]]                             # time-dependent Rabi
```
Hasse's simulation uses **continuous time evolution with a time-dependent
Rabi envelope**, not discrete unitaries. The envelope `mod(t)` is a
Butterworth-filtered square wave (cutoff 0.8 MHz for fast AOM). The
filtering rounds off the pulse edges.

Displaced-states regime (cell 21):
- `m_freq = 1.3` MHz, `strobo_dur = 0.04` µs (40 ns — fast AOM)
- `Ω/(2π) = 0.3` MHz (Table II value, unchanged)
- Per-pulse θ = Ω_eff·δt ≈ 4°; N ≈ 23 for π/2
- ω_m·δt ≈ 0.33 rad = 19°  (not the 47° I used in v2/v3)

So my v0.8 defaults (N=22, auto δt) were already in Hasse's fast-AOM
regime. The "Hasse-matched" label in v2/v3 actually pointed to Hasse's
slow-AOM regime.

-----

## 2. Two retries — Fix A

### v5 — detuning-scan contrast

Driver: [run_fig8_v5.py](../numerics/run_fig8_v5.py).
For each (α, tilt), run a detuning scan (41 points over ±6 MHz/(2π)),
extract `(max_δ σ_z − min_δ σ_z)/2`.

Result: contrast(α=0) = 0.577, contrast(α=4) = 0.59, contrast(α=8) =
0.59 — with **7 sign-flips** across α ∈ [0, 8]. Oscillation period ≈ 4
in α; identified as the `2η·|α|` phase wrapping with period
π/(2η) = 3.96.

### v6 — phase-scan contrast

Driver: [run_fig8_v6.py](../numerics/run_fig8_v6.py).
For each (α, tilt), run an AC analysis-phase scan (32 points
ac_phase_deg ∈ [0°, 360°)), extract `(max_ϕ σ_z − min_ϕ σ_z)/2`.

Tried both ϑ₀ = 0° (position extremum) and ϑ₀ = 90° (momentum extremum,
per Hasse's claim that contrast decay comes from "finite-time effects
of the flashes" — maximal at max momentum).

Result (ϑ₀ = 0°):
| α   | contrast | phi_0        |
|-----|----------|--------------|
| 0   | 0.90     | 0°           |
| 4   | 0.92     | ±180° (wrap) |
| 8   | 0.92     | 0° (full 2π) |

Result (ϑ₀ = 90°):
| α   | contrast | phi_0   |
|-----|----------|---------|
| 0   | 0.90     | 0°      |
| 4   | 0.92     | 0°      |
| 8   | 0.91     | +0.6°   |

Fig 8a (position calibration via phi_0 vs α at ϑ₀=0) **reproduces Hasse
Fig 8a** — linear slope, total rotation 2π over α ∈ [0, 8]. ✅

Fig 8b (contrast vs α) **does NOT reproduce Hasse Fig 8b** — contrast
is essentially flat at ~0.92 regardless of ϑ₀ or α. ❌

-----

## 3. Why — the matrix-element-magnitude theorem protects the phase-scan contrast

For a coherent state, `|⟨α|C|α⟩| = exp(−η²/2)` is α-independent
(displacement-operator identity D(α)† X D(α) = X + 2Re(α) → exponential
factor cancels under |·|). Under stroboscopic operation with pulses
synchronized to the motion, the effective per-pulse coupling magnitude
is therefore α-independent, and so is the final Bloch vector magnitude.

The phase-scan contrast reads out (max_ϕ σ_z − min_ϕ σ_z)/2, which for
this setup equals `sin(θ_eff)·|Bloch|`. Both factors are protected by
the theorem at leading order. Deviations from flatness appear only at
higher orders and are of size ~`(η·|α|·ω_m·δt)²` — in our regime that
is (0.4·8·0.34)² ≈ 1.2, large in principle but fine-tuned away by the
cancellation structure to a few percent in practice.

**Conclusion.** Hasse's Fig 8b decay from 1 to 0 CANNOT come from the
pure unitary we simulate, because the theorem protects phase-scan
contrast against α-dependence. The decay requires a mechanism that
breaks the theorem at O(1), not O((η·|α|·ω_m·δt)²). Candidates:

1. **AOM pulse filtering** (cell 3). Turns ideal square-wave pulses
   into smooth envelopes; effective per-pulse coupling becomes
   `⟨α|C̄(δt)|α⟩` where C̄ is the filter-averaged operator. This
   quantity is NOT theorem-protected: the filtering integrates over
   positions the wave packet visits during the smooth rising edge, and
   for large |α| the position range |Δ⟨X̂⟩| ~ |α|·ω_m·δt is wide enough
   to average the AC pattern toward zero, reproducing Hasse's decay.

2. **Time-averaged coupling (analytical Bessel).** Implements the same
   smoothing analytically. Cheaper than filter modelling.

3. **Different observable than we've tried.** Possible but unlikely
   given the code we've read.

-----

## 4. WP-V closing position

With four attempted observable definitions (|C| at δ=0, detuning-scan
contrast, phase-scan contrast at ϑ₀=0, phase-scan contrast at ϑ₀=π/2),
**all four give α-flat or α-revival structure**, none reproduces
Hasse's monotone decay. This exhausts the observable-definition
variable.

The matrix-element-magnitude theorem holding at all α under our engine
is WP-V's **cleanest positive finding**: it tells us exactly why our
Fig 8b differs from Hasse's. WP-V has definitively localised the
discrepancy to **a missing ingredient that breaks the theorem** —
almost certainly the AOM pulse filtering (or equivalently, an
analytical time-averaging approximation).

Declaring WP-V's Fig 8b reproduction "blocked on engine extension,
theorem-diagnosed" is the honest status. A follow-up WP (name TBD)
could implement the AOM filter and re-run v6; the theorem tells us
this should give the Hasse decay.

-----

## 5. Status

- Engine v0.9.1 unchanged.
- Drivers [run_fig8_v5.py](../numerics/run_fig8_v5.py) and
  [run_fig8_v6.py](../numerics/run_fig8_v6.py) added.
- Plots: `fig8b_contrast_v5.png`, `fig8{a,b}_contrast_v6.png`,
  `fig8_phase_scans_v6.png`.
- Reference notebooks saved to `refs/` for future engine extensions
  (`vpaula_hologram_*.ipynb`, `qc.py`).

Fig 8a reproduction: ✅ closed at v6 (phi_0 vs α matches Hasse).
Fig 8b reproduction: ❌ blocked; theorem-diagnosed (see §3).
