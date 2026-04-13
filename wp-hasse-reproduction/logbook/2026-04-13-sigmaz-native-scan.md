# Logbook — 2026-04-13 — σ_z(|α|, ϑ₀) native readout

**Context.** Question from the user: instead of using the `|C| =
√(σ_x² + σ_y²)` contrast definition, scan the engine's *native* σ_z
output as a function of motional amplitude **and** motional phase, and
look at how the σ_z fringe amplitude varies with |α|.

Driver: [run_sigmaz_alpha_phase.py](../numerics/run_sigmaz_alpha_phase.py).
Output: [sigmaz_alpha_phase.h5](../numerics/sigmaz_alpha_phase.h5),
[sigmaz_alpha_phase_maps.png](../plots/sigmaz_alpha_phase_maps.png),
[sigmaz_amplitude_vs_alpha.png](../plots/sigmaz_amplitude_vs_alpha.png).
Compute: 40.9 s wall (3 configurations × 17 |α| × 32 ϑ₀ = 1632 runs).

Three configurations on the same (|α|, ϑ₀) grid:
- `tsep=1.0,   n_th=0.00`   (default stroboscopic, pure)
- `tsep=1.0,   n_th=0.15`   (default stroboscopic, thermal)
- `tsep=0.999, n_th=0.00`   (Ufree active, pure)

-----

## 1. Headline result

At `t_sep = 1.0` the engine's native σ_z is **identically 0.128** for
every (|α|, ϑ₀) — zero ϑ₀-dependence, zero |α|-dependence:

```
sz_amplitude(|α|) = (max_ϑ₀ σ_z − min_ϑ₀ σ_z) / 2 = 0.000
```

across all 17 |α| values, both with and without thermal smearing
(n_th = 0.00 and n_th = 0.15 give bit-identical maps). Adding thermal
sampling does not break the degeneracy.

At `t_sep = 0.999` (Ufree engaged), σ_z develops a small but
**monotonically growing** ϑ₀-fringe amplitude:

| `|α|` | sz_amplitude | mean σ_z |
|------|--------------|----------|
| 0    | 0.000        | +0.128   |
| 1    | 0.001        | +0.128   |
| 3    | 0.006        | +0.123   |
| 5    | 0.016        | +0.113   |
| 8    | 0.039        | +0.091   |

The mean σ_z drifts downward with |α| as the off-resonant inter-pulse
phase walks the spin away from its synchronous fixed point. The fringe
amplitude reaches ~30% of the mean at |α| = 8.

-----

## 2. What this isolates

Two distinct findings, neither visible in the |C| picture:

### Finding A — At perfect stroboscopy, motional-phase information lives entirely off the σ_z axis

In the engine's frame at `t_sep = 1.0`, σ_z carries no ϑ₀ information at
all. All of the motional-phase signal lives in (σ_x, σ_y), accessible
only through the ϕ-basis-rotation surrogate

```
σ_z(ϕ; ϑ₀) = σ_x(ϑ₀) cos ϕ + σ_y(ϑ₀) sin ϕ
```

i.e., the Hasse "analysis-phase scan" is the *only* channel through
which the engine exposes ϑ₀-dependence under perfectly synchronous
operation. This is consistent with the engine's declared physics (no
ω_m a†a in per-pulse H + Ufree off ⇒ stroboscopic frame is
ϑ₀-blind on σ_z) but worth stating explicitly: a literal lab readout of
σ_z without an analysis-phase pulse will see no ϑ₀-dependence in this
engine, regardless of |α|.

### Finding B — Tiny detuning (`t_sep = 0.999`) generates real σ_z ϑ₀-fringes that grow with |α|

Engaging Ufree at a 0.1% off-resonance produces a σ_z fringe of roughly
sz_amplitude ≈ 0.005 · |α|² (rough fit by eye to the table above —
sub-Lamb–Dicke-Doppler-like growth). This is the channel through which
inter-pulse motional phase reaches σ_z without basis rotation.

Implication: **the t_sep_factor knob is a usable handle for forcing σ_z
to carry direct ϑ₀ information**. If WP-E or a follow-up wants to test
the engine's stroboscopic lock-tolerance against Hasse's experimentally
measured Δω_m/ω_m ≲ 0.7 % bound, this is the relevant axis — and the
σ_z fringe amplitude vs |α| at varying t_sep_factor is a cleaner probe
than |C|, because |C| is dominated by the train-rotation amplitude
(which is large and nearly |α|-independent) while sz_amplitude is zero
in the perfectly synchronous limit and grows monotonically with the
mismatch.

-----

## 3. Reconciliation with previous findings

- WP-V results §1 reported `|C|` flat at 0.917 for all |α| under both
  t_sep = 1.0 and t_sep = 0.999 (the discriminator entry). That remains
  true; the present scan is consistent with it.
- The present scan reveals what `|C|` was hiding: σ_z direct readout has
  *no* ϑ₀-fringe at t_sep = 1.0 and a *growing* one at t_sep = 0.999.
  Both phenomena are invisible to a |C|-only diagnostic because |C| =
  √(σ_x² + σ_y²) is the magnitude of the ϕ-basis-rotation amplitude,
  which is set by the train rotation budget and saturates near the π/2
  nominal regardless of |α| or t_sep at this Ω·dt.
- Thermal smearing (n_th = 0 vs 0.15) makes no difference at t_sep = 1.0.
  This is consistent with Finding A: thermal averages over Fock states,
  which the synchronous frame already projects out of σ_z.

-----

## 4. Recommended diagnostic: σ_z fringe amplitude vs |α| at swept t_sep

A clean follow-up would be a 2D scan `(t_sep_factor, |α|)` recording
sz_amplitude(|α|; t_sep). Expected shape:

- Vertical line at t_sep = 1.0: identically zero.
- Wedge spreading symmetrically about t_sep = 1.0 with sz_amplitude
  growing as (t_sep − 1)·|α|² × (some η-dependent prefactor).
- Hasse Fig 8b's contrast loss should show up *only once* the per-pulse
  motional Hamiltonian is added (the engine extension flagged in the
  t_sep discriminator entry).

Not gating; logged as a candidate next probe. ~40 s × N_tsep would size
this cheaply.

-----

## 5. Status

WP-V remains closed at v0.1; this is a second appendix entry (alongside
the t_sep discriminator). Finding A in particular is a clean physical
statement about the engine that should travel into WP-E's interpretation
of S2/S3 ϑ₀-dependence: any ϑ₀ signal in WP-E's σ_z-derived datasets is
either (i) basis-rotation-derived from (σ_x, σ_y), or (ii) generated by
a deliberate t_sep ≠ 1 setting. Direct σ_z readout will not show it.
