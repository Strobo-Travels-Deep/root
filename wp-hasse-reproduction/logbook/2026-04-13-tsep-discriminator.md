# Logbook — 2026-04-13 — t_sep_factor discriminator (WP-V follow-up)

**Context.** Closes the open question in
[2026-04-13-results.md §2](2026-04-13-results.md): is the missing Fig 8b
contrast decay caused by the `Ufree = None` shortcut at
`t_sep_factor = 1.0`, or by the *absence of* `ω_m a†a` in the per-pulse
Hamiltonian regardless of `Ufree`?

Driver: [run_fig8b_tsep_probe.py](../numerics/run_fig8b_tsep_probe.py).
Output: [fig8b_tsep_probe.h5](../numerics/fig8b_tsep_probe.h5),
[fig8b_tsep_probe.png](../plots/fig8b_tsep_probe.png).
Compute: 3.3 s wall (3 × 17 = 51 runs).

-----

## 1. Result

| t_sep_factor | C(α=0) | C(α=8) | C(α=8)/C(α=0) |
|--------------|--------|--------|---------------|
| 1.000        | 0.903  | 0.917  | 1.015         |
| 0.999        | 0.863  | 0.917  | 1.062         |
| 1.001        | 0.881  | 0.917  | 1.041         |

All three are flat-to-rising contrast curves. The engaged `Ufree`
propagator (active at 0.999/1.001) does not produce the Hasse contrast
decay; it only perturbs the α = 0 reference point by ≲ 5%.

## 2. Verdict

**Reading (a) confirmed; reading (b) ruled out.** The
`t_sep_factor = 1.0 ⇒ Ufree = None` branch is **not** a silent shortcut.
Engaging `Ufree` adds inter-pulse free evolution at near-resonant offsets
but does not inject the per-pulse `ω_m a†a` term that would let the
motional wave packet rotate *during* the analysis flash. The contrast
loss that Hasse Fig 8b attributes to the time-averaged variance
⟨Var(X_i)⟩_δt is therefore structurally absent from the engine in either
configuration.

To reproduce Hasse Fig 8b in this engine, one of the following is
required:

1. **Lab-frame mode.** Add an `intra_pulse_motion=True` switch that
   builds H = (Ω/2)(C ⊗ σ₋ + h.c.) + ω_m a†a ⊗ I and propagates each
   pulse with that combined Hamiltonian for δt. (`δt` becomes a
   first-class parameter; current engine derives it from the π/2 budget.)
2. **Effective time-averaging post-processor.** Average the AC coupling
   operator C = exp(iη(a + a†)) over a δt window of motional rotation
   analytically before each pulse, recovering the smearing in the
   rotating frame. Cheaper but less general.

Neither is in WP-V's remit. Both are clean engineering tasks; option 1 is
preferred because it keeps the physics in the Hamiltonian rather than in
a calibration step.

## 3. Implication for WP-E

WP-E S1 contrast variations along (δ₀, |α|) at fixed φ_α therefore
originate **purely from the Doppler axis** in the engine — confirmed by
this discriminator, not just inferred from the original WP-V Fig 8b run.
A footnote to that effect should land in WP-E v0.4 or the next
preflight-results revision; it changes the interpretation of the S1
plots without changing the numbers.

## 4. Status

- WP-V remains **closed at v0.1**; this entry is appendix-grade.
- The "intra-pulse motional H" feature is logged here as a candidate
  engine extension; assignment to a WP belongs to the user.
