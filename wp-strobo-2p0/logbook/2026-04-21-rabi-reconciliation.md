# 2026-04-21 — Rabi-rate reconciliation

**Status:** open, pending a single lab measurement (see §3).
**Upstream:** [2026-04-21-kickoff.md §9 Q1](2026-04-21-kickoff.md).

-----

## 1. The two candidate values on record

Over the strobo 2.0 conversation two distinct Rabi values have appeared:

- **(A) `t_π = 1.122 µs`** (original phrasing), equivalent to
  `Ω/(2π) = π/(2π · 1.122 µs) = 0.4456 MHz`.
- **(B) `Ω/(2π) = 0.178 MHz`** (updated value), equivalent to
  `t_π = π/(2π · 0.178 MHz) = 2.809 µs`.

These differ by a factor of 2.51. Both disagree with the repo's
canonical reference value:

- **(C) `Ω/(2π) = 0.300 MHz`** — Hasse 2024 Table II AC-beam bare
  Rabi rate, as used throughout WP-E, WP-C, and
  [scripts/stroboscopic_sweep.py](../../scripts/stroboscopic_sweep.py).

All three are plausible on their face — none is analytically derivable
from the other two — so the resolution is empirical: one lab carrier
measurement is enough to pick the correct one. See §3.

## 2. What each candidate predicts for |C|_vacuum

In the clean anchor (δ₀ = 0, ϑ₀ = 0, |α| = 0) the coherence contrast
reduces to the closed form

```
|C|_vacuum = |sin(N · Ω_eff · δt)|,   Ω_eff = Ω · exp(-η²/2),
```

with the Debye-Waller factor exp(-η²/2) = 0.9250 at η = 0.395. Values:

| Ω/(2π) [MHz] | |C|_vac  T1 (3 × 100 ns) | |C|_vac  T2 (7 × 50 ns) | source                    |
|-------------:|-------------------------:|------------------------:|---------------------------|
| 0.178        | 0.305                    | 0.354                   | sweep value (strobo 2.0)  |
| 0.300        | 0.500                    | 0.573                   | Hasse 2024 Table II AC    |
| 0.446        | 0.702                    | 0.788                   | from t_π = 1.122 µs       |

The three candidates are well separated — T2 predictions span 0.35 /
0.57 / 0.79, easily distinguishable in a standard lab run. The tool
[numerics/rabi_calibration.py](../numerics/rabi_calibration.py) plots
the full curve on [0, 1] MHz and cross-checks the closed form against
the full engine (the engine underestimates the closed form by ≲ 2 %
at candidate C due to finite-pulse Magnus corrections; the closed
form is adequate for read-off to ~1 %).

Figure: [plots/00_rabi_calibration.png](../plots/00_rabi_calibration.png).

## 3. Proposed resolution protocol

One lab measurement is sufficient:

1. Prepare the ground motional state (|α| = 0, or Doppler-cooled
   + resolved-sideband-cooled as close to it as achievable) and the
   spin in the synchronised |+x⟩-equivalent state.
2. Apply the T2 pulse train (7 × 50 ns, Δt = 0.77 µs, δ₀ = 0).
3. Run the standard analysis-phase scan and fit the σ_z fringe to
   `|C|_obs · sin(φ − φ*)`.
4. Compare `|C|_obs` to the table in §2:
   - |C|_obs ≈ 0.35 → Ω/(2π) ≈ 0.178 MHz (current sweep value
     was correct; no re-run needed).
   - |C|_obs ≈ 0.57 → Ω/(2π) ≈ 0.300 MHz (repo canonical; re-run
     the sweep at this value).
   - |C|_obs ≈ 0.79 → Ω/(2π) ≈ 0.446 MHz (original t_π = 1.122 µs
     interpretation; re-run the sweep at this value).
5. For a 1 % Ω read-off, a 10-point φ scan with 500 shots per
   point is adequate.

T1 (3 × 100 ns) can be used as an independent cross-check at the
same Ω.

## 4. What changes in the sweep output if Ω changes

The sweep code is parametric in `OMEGA_R_MHZ`
([run_sweep.py line 17](../numerics/run_sweep.py)); the full sweep
re-runs in ~100 s on a laptop. So if the lab measurement implies a
different Ω, the cost of updating is one script edit + one re-run.

Qualitatively, raising Ω from 0.178 to 0.300 MHz would:

- Raise |C|_peak on carrier from ~0.35 to ~0.55.
- Broaden all features in δ₀ by ~70 % (linewidths scale with Ω_eff).
- Shift the carrier closer to saturation (|C| ≈ 1 at Ω ≈ 0.9 MHz
  for T1, Ω ≈ 0.77 MHz for T2 — see figure).
- ϑ₀-modulation amplitude would scale up proportionally.

The qualitative findings of
[2026-04-21-sweep-complete.md](2026-04-21-sweep-complete.md) §3 (carrier
dominance, δ⟨n⟩ π-periodicity, T1-vs-T2 linewidth ratio) are
Ω-independent within the weak-probe regime and do not change.

## 5. Open speculation (not load-bearing)

One hypothesis for the `0.446 / 0.178 ≈ 2.51` factor: the √(2π) ≈ 2.507
ratio is suggestive of a cyclic-vs-angular conversion error somewhere
upstream. Neither value lines up cleanly with a known Debye-Waller,
Lamb-Dicke, or sideband-reduction factor of the Hasse 0.300 MHz
reference. This is flagged for the lab-side review rather than resolved
numerically.

-----

*v0.1 2026-04-21 — initial memo. Awaits a single lab measurement to close.*
