# 2026-04-21 — Rabi-rate reconciliation (v0.2 — resolved)

**Status:** **resolved**. The v0.3 sweep adopts a per-train π/2
calibration (each train given its own Ω); the earlier single-Ω
candidates are archived here for reference.
**Upstream:** [2026-04-21-kickoff.md §9 Q1](2026-04-21-kickoff.md),
now pointing to this memo.

-----

## 1. History — three candidate values

Over the strobo 2.0 conversation three Rabi values were in play:

- **(A) `t_π = 1.122 µs`** (original phrasing), equivalent to
  `Ω/(2π) = π/(2π · 1.122 µs) = 0.4456 MHz`.
- **(B) `Ω/(2π) = 0.178 MHz`** (updated value from the user),
  `t_π = 2.809 µs`.
- **(C) `Ω/(2π) = 0.300 MHz`** (Hasse 2024 Table II AC-beam, repo
  canonical).

None of these is a π/2-calibration for strobo 2.0's short trains:
with B the trains deliver only N·θ_pulse ≈ π/9 (weak probe), with C
about π/5, with A about π/4. Hasse 2024 uses its C value with
N = 30 × 100 ns to deliver a full π/2 analysis rotation; a short
strobo-2.0 train needs a stronger Ω to compensate for the shorter
N·δt.

## 2. Current (v0.3) resolution — per-train π/2 calibration

Each strobo 2.0 train is now assigned the Ω that makes
`N · Ω · e⁻η²⁄² · δt = π/2`:

| Train | N | δt (ns) | **Ω/(2π) (MHz)** | source                   |
|-------|---|---------|------------------:|--------------------------|
| T1    | 3 | 100     | **0.9008**        | π/2 calibration (v0.3)   |
| T2    | 7 | 50      | **0.7722**        | π/2 calibration (v0.3)   |

This matches the Hasse App. D convention (π/2 per train) and makes
the v0.3 amplitudes directly comparable to Hasse Fig. 2(b)'s 0.76(3)
and Fig. 6's ±0.9 range.

## 3. |C|_vacuum predictions at all five values

At the clean anchor (δ₀ = 0, ϑ₀ = 0, |α| = 0) the coherence contrast
reduces to the closed form

```
|C|_vacuum = |sin(N · Ω_eff · δt)|,   Ω_eff = Ω · e⁻η²⁄²,   e⁻η²⁄² = 0.9250.
```

| Ω/(2π) [MHz] | |C|_vac  T1 | |C|_vac  T2 | source                               |
|-------------:|-------------:|------------:|--------------------------------------|
| 0.178        | 0.305        | 0.354       | v0.1 pre-calibration sweep            |
| 0.300        | 0.500        | 0.573       | Hasse 2024 Table II AC (their N=30)   |
| 0.446        | 0.702        | 0.788       | from t_π = 1.122 µs                   |
| **0.9008**   | **1.000**    | **0.966**   | **T1 π/2 calibration (v0.3)**         |
| **0.7722**   | **0.975**    | **1.000**   | **T2 π/2 calibration (v0.3)**         |

The tool
[numerics/rabi_calibration.py](../numerics/rabi_calibration.py)
generates this table and plots the full curve on
[plots/00_rabi_calibration.png](../plots/00_rabi_calibration.png).
Engine cross-check (full Fock-basis) at the π/2 points:

- T1 cal on T2 (Ω=0.901 MHz): closed form 0.966, engine 0.850 — 12 %
  below. The gap is the intra-pulse Magnus correction.
- T2 cal on T2 (Ω=0.772 MHz): closed form 1.000, engine 0.919 — 8 %
  below. Same mechanism.

So **at the π/2 calibration the engine returns |C| ≈ 0.92 on carrier
at α = 0** — the main v0.3 sweep peak values
([2026-04-21-sweep-complete.md §2](2026-04-21-sweep-complete.md))
agree with this to within 3 % across all α.

## 4. Lab-feasibility note

The required Ω/(2π) ≈ 0.77–0.90 MHz is 2.6–3× higher than Hasse's
Table II AC-beam value (0.300 MHz). Achieving it requires either
(i) more AC-beam power on the ion or (ii) a different beam geometry.
If the existing lab apparatus cannot reach these Rabi rates,
strobo 2.0's native regime remains the weak-probe v0.1 setting and
any experimental comparison against the v0.3 dataset would require a
matched re-calibration.

## 5. Alternative read-off protocol (retained from v0.1)

If the lab prefers to re-measure rather than derive Ω from first
principles, the original one-shot read-off still works: prepare a
ground motional state, run T2 on carrier, fit the σ_z fringe to
`|C|_obs · sin(φ − φ*)`, and compare `|C|_obs` to column 3 of §3.
The mapping is monotone and unambiguous on [0, 1] MHz.

-----

*v0.1 2026-04-21 — three-candidate memo, open pending lab input.*
*v0.2 2026-04-21 — resolved via per-train π/2 calibration adopted
for the v0.3 sweep. Candidates retained as reference; lab-feasibility
note added.*
