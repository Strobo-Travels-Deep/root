# Stroboscopic Spin–Motion Coupling: Ideal-Limit Principles and Deviations

**Breakwater Dossier — Sail (Essay)**
**Hasse et al., Phys. Rev. A 109, 053105 (2024)**
**v0.2.4 · 2026-02-26**

-----

## Purpose

This document derives the physics of the stroboscopic travelling-wave measurement scheme
from the *ideal limit* — low Lamb–Dicke parameter η, pulses much shorter than both motional
and spin dynamics — where the principles are cleanest and best understood. Each principle
is then annotated with an explicit **⚠ Deviation** block stating *where and how* the actual
experimental parameters (η ≈ 0.4, δt ≈ 40 ns, ~22 pulses at 1 per motional cycle,
Ω/(2π) = 0.3 MHz, ω_m/(2π) = 1.3 MHz) depart from the ideal, and what consequences follow.

The Monroe group’s programme of ultrafast pulsed-laser control of trapped ions
[Mizrahi2013, Johnson2015, Johnson2017, Wong-Campos2017] provides the clearest
experimental and theoretical baseline for impulsive spin-dependent kicks outside
the Lamb–Dicke regime. The comparison is instructive — but the present protocol is
*not* a slow approximation to an ultrafast kick. Its physics identity is different
(§3).

-----

## 1. The Ideal Limit

### 1.1 Impulsive spin-dependent kick

In the ideal limit, a travelling-wave laser pulse acts on a trapped ion for a duration
δt satisfying two conditions:

**Condition I — frozen motion:** δt ≪ T_m = 2π/ω_m.
The ion’s position and velocity are effectively constant during the pulse.

**Condition II — impulsive spin flip:** The pulse area is a well-defined fraction of π.
The Rabi frequency Ω is large enough that Ω·δt = θ (target rotation angle) while
δt still satisfies Condition I.

Under these conditions, the pulse imparts a *state-dependent momentum kick*:
the coupling operator C = exp(iη(a + a†)) acts as a displacement in momentum
space conditioned on the spin state [García-Ripoll2003, Duan2004].

The key insight from Monroe’s ultrafast programme: if δt is short enough,
the kick is independent of the ion’s motional state — it works from the ground state
to room temperature [Johnson2015]. This is because the ion is “frozen” during the
pulse; neither its position nor its velocity changes appreciably. The displacement
operator factorises cleanly from free evolution.

> **⚠ Deviation (Condition I — finite-time Magnus correction)**
> 
> Our pulse duration δt ≈ 40 ns. The motional period T_m ≈ 769 ns.
> Ratio: δt/T_m = 0.052.
> 
> The motional phase accumulated during one pulse is
> 
> ```
> δφ = ω_m · δt ≈ 0.33 rad ≈ 19°
> ```
> 
> This is not small compared to unity. The pulse does not act at a single
> motional phase; it integrates over a 19° arc of the oscillation.
> 
> Structurally, the deviation is a finite-time Magnus correction. The
> time-evolution operator during one pulse is not the product of
> a pure displacement and a pure free rotation:
> 
> ```
> U_pulse ≠ U_free(δt) · D(η)
> ```
> 
> Formally, the deviation arises because [H_m, H_int(t)] ≠ 0 during the
> finite pulse — where H_m is the harmonic motional Hamiltonian and
> H_int(t) the laser interaction — so the evolution cannot be factorised
> into a pure displacement and free rotation.
> 
> The leading correction is O(ω_m δt): the pulse generates a displacement
> *composed with* free evolution during the pulse. To first order in ω_m δt,
> this acts similarly to replacing the instantaneous position x(t₀) with a
> pulse-envelope-weighted average
> 
> ```
> x̄ = (1/δt) ∫₀^δt x(t₀ + t') dt'
> ```
> 
> and similarly for velocity (to leading order, for a smooth pulse envelope).
> The phase blur accumulated during the pulse is
> 
> ```
> Δφ ~ k_eff · v · δt = δ_D · δt
> ```
> 
> Here Δφ is a heuristic scale for intra-pulse phase evolution; in a full
> model, finite-δt effects split into geometric phase averaging (set by how
> much k_eff·x(t) changes over the pulse, scaling with both ω_m δt and
> k_eff v δt depending on the motional state) and Doppler-detuning
> distortions of the Rabi response (controlled by δ_D/Ω_eff, i.e. the
> Doppler shift relative to the Rabi linewidth).
> 
> Careful with units: if δ_D/(2π) is quoted in MHz, then
> Δφ_rad = 2π · [δ_D/(2π)] · δt. It is useful to separate coherent
> peak motion (nonzero |α|) from the zero-point RMS Doppler width (σ).
> 
> **(A) Coherent oscillation — peak blur (radians)**
> (with |α| the coherent-state amplitude, v_peak = ω_m x₀ √2 |α|,
> hence δ_D^peak = k_eff v_peak):
> 
> |α|δ_D^peak/(2π) (MHz)|Δφ_peak = 2π·[δ_D^peak/(2π)]·δt (rad)|Significance                                   |
> |-|-------------------|-------------------------------------|-----------------------------------------------|
> |1|1.04               |0.26                                 |Small–moderate                                 |
> |3|3.12               |0.78                                 |Moderate                                       |
> |5|5.16               |1.30                                 |Order-unity blur (~1 rad, i.e. tens of degrees)|
> 
> **(B) Zero-point motion — RMS blur (radians):**
> With RMS Doppler width σ/(2π) = 0.52 MHz:
> Δφ_rms ≈ 2π · [σ/(2π)] · δt ≈ 0.13 rad.
> This is not “zero,” but it is still ≪ 1 rad. Note ω_m δt ≈ 0.33 rad
> is the baseline finite-time parameter even at α = 0; the ZPM Doppler
> contribution adds an additional ~0.13 rad RMS scale.
> 
> The stroboscopic synchronisation compensates for the secular accumulation
> of motional phase across pulses, but it cannot eliminate the intra-pulse
> Magnus correction. This correction must be included in any quantitative
> signal model (WP-A.1).

> **⚠ Deviation (Condition II — weak pulses, coherent accumulation)**
> 
> Our effective carrier Rabi rate Ω_eff/(2π) = 0.277 MHz (Debye–Waller
> suppressed). Rotation per pulse:
> 
> ```
> θ_pulse = Ω_eff · δt ≈ 0.070 rad ≈ 4.0°
> ```
> 
> This is a *weak* rotation — far from a single impulsive π/2 kick.
> Approximately 22 pulses accumulate to π/2:
> 
> ```
> N_π/2 = (π/2) / θ_pulse ≈ 22.5
> ```
> 
> Total accumulation time: 22 × T_m ≈ 16.9 μs (consistent with the
> measured 17.0 μs stroboscopic π/2 length).
> 
> Contrast with Monroe: ultrafast pulses (10 ps) achieve θ ~ π in a single
> shot [Mizrahi2013, Johnson2017]. Our scheme compensates with coherent
> accumulation over 22 phase-locked pulses — one flash per motional cycle,
> true stroboscopic illumination. The trade: Monroe’s single kicks are
> temperature-independent by construction; our accumulated signal requires
> stable phase lock over ~22 motional cycles (L1, L8).

### 1.2 Lamb–Dicke regime (η ≪ 1)

In the Lamb–Dicke regime, the coupling operator can be expanded:

```
C = exp(iη(a + a†)) ≈ 1 + iη(a + a†)
```

This linearisation has three consequences:

**(a)** The interaction couples only neighbouring Fock states (Δn = ±1).
Sidebands are cleanly resolved: carrier at δ = 0, first red/blue at δ = ∓ω_m.

**(b)** The coupling strength is *linear* in position x̂ = x₀(a + a†).
The measurement is a linear probe of the position quadrature.

**(c)** Backaction is *single-quadrature*: the measurement disturbs only the
conjugate quadrature (momentum), not the measured one.
This is the structural prerequisite for back-action evasion (BAE)
[Braginsky1980, Caves1980].

These three properties are not independent. Property (c) follows from (b):
a coupling linear in x̂ generates a force conjugate to x̂, i.e. in p̂, leaving
x̂ undisturbed. The structural linkage is: linearity → quadrature selectivity → BAE.

> **⚠ Deviation (η ≈ 0.4 — loss of quadrature selectivity)**
> 
> The small-η expansion at η = 0.397:
> 
> |Order|Term|Value|Relative to linear|
> |-----|----|-----|------------------|
> |1    |η   |0.400|reference         |
> |2    |η²/2|0.080|20%               |
> |3    |η³/6|0.011|2.7%              |
> 
> The quadratic correction is 20% of the linear term.
> 
> The breakdown is not merely amplitude distortion. What fails at η ≈ 0.4
> is **quadrature selectivity**: the exponential operator samples all powers
> of x̂, including x̂², x̂³, etc. These higher harmonics couple both
> quadratures. Specifically:
> 
> - x̂² = x₀²(a + a†)² mixes position and momentum (contains a†a and aa, a†a†
>   terms that act on both quadratures).
> - The measurement ceases to be a linear probe of one quadrature.
>   It becomes a nonlinear functional of the full motional state.
> 
> Consequences:
> 
> - **Multi-sideband coupling:** Δn = 0, ±1, ±2, ±3 all contribute.
>   Amplitudes from |0⟩: carrier 0.923, 1st 0.369, 2nd 0.074, 3rd 0.010.
>   The 2nd sideband is 8% of the carrier — not negligible.
> - **BAE structurally compromised:** Backaction spreads across both
>   quadratures. Whether a perturbative linear regime exists in some
>   accessible parameter window is open (L6), but the *structural* basis
>   for BAE — single-quadrature coupling — is absent at this η.
> - **Debye–Waller suppression:** Carrier Rabi rate reduced by
>   exp(−η²/2) = 0.924. Confirmed: Ω_eff = 0.277 vs. Ω = 0.300 MHz.
> - **Asset for tomography:** The nonlinear coupling accesses higher
>   harmonics of the characteristic function χ(ξ) = Tr[ρ exp(iξx̂/x₀)],
>   providing richer phase-space information than a linear probe.
>   This is why the primary framing is tomography, not BAE.
> 
> Note: even at η ≪ 1, the exponential structure matters when acting on
> large coherent states (|α| ≫ 1/η), because the exponent η·2|α| can
> be large even if η is small. The Lamb–Dicke condition is properly
> η√(2⟨n⟩ + 1) ≪ 1, not just η ≪ 1. At α = 5 (⟨n⟩ = 25):
> η√(51) ≈ 2.8, deeply outside Lamb–Dicke by any measure.

### 1.3 Position readout via phase shift

For an ion at position x in a travelling wave with wavevector k_eff,
the spin acquires a phase:

```
φ = k_eff · x = (2π/λ_eff) · x
```

In the ideal limit (instantaneous pulse, linear coupling), this phase
shift is a clean measurement of position. Scanning the motional phase
(by varying the stroboscopic timing relative to the oscillation) maps
out ⟨cos(k_eff · x(t))⟩ and ⟨sin(k_eff · x(t))⟩.

With super-resolution from the AC lattice: λ_eff ≈ 140 nm, giving
position sensitivity far below the optical wavelength. This is *geometric*
super-resolution — engineered k_eff, not dynamical or QND.

> **⚠ Deviation (intra-pulse phase blur)**
> 
> During the 40 ns pulse, the ion traverses a finite arc. The measured
> phase is not the instantaneous value k_eff·x(t₀) but a convolution:
> 
> ```
> φ_measured = ∫ g(t) · k_eff · x(t₀ + t) dt
> ```
> 
> where g(t) is the normalised pulse envelope. The leading correction is
> the Magnus term from §1.1. The phase blur Δφ ~ k_eff · v · δt is
> bounded by the values in the table in §1.1.
> 
> For coherent motion, Δφ_peak ≈ 0.26 rad at |α| = 1 and reaches
> ~1.3 rad at |α| = 5 (Table §1.1). For zero-point motion the RMS blur
> is Δφ_rms ≈ 0.13 rad. Thus, position-phase readout is progressively
> smeared for large |α|, precisely where the Doppler channel becomes
> the dominant information carrier.

### 1.4 Momentum readout via Doppler detuning

A moving ion sees the analysis pulse Doppler-shifted:

```
δ_D = k_eff · v
```

In the ideal limit (narrow Rabi linewidth Ω ≪ ω_m, resolved sidebands),
scanning the detuning δ₀ of the analysis pulse maps out the velocity
distribution: each δ₀ selects the velocity class v = −δ₀/k_eff.

The transition probability at detuning δ is:

```
P_↑(δ) = (Ω²/Ω_eff²) · sin²(Ω_eff τ/2),    Ω_eff = √(Ω² + δ²)
```

This Rabi lineshape acts as a velocity filter with spectral resolution ~Ω.

> **⚠ Deviation (spectroscopic, not dynamical regime)**
> 
> |α|δ_D^peak/(2π)   |δ_D/Ω     |Regime                    |
> |-|----------------|----------|--------------------------|
> |0|0 (σ = 0.52 MHz)|1.73 (RMS)|ZPM already exceeds Ω     |
> |1|1.04 MHz        |3.5       |Strongly Doppler-dominated|
> |3|3.12 MHz        |10.4      |Deep Doppler regime       |
> |5|5.16 MHz        |17.2      |Very deep                 |
> 
> Even zero-point motion (α = 0) produces Doppler shifts comparable to Ω.
> This is not the resolved-sideband regime of standard ion-trap spectroscopy.
> 
> **The regime is spectroscopic rather than dynamical.** The analysis
> pulse does not coherently rotate the spin through a well-defined angle
> (because the Doppler shift moves the ion far off resonance for most
> velocity classes). Instead, it functions as a **narrowband frequency
> discriminator**: at each detuning δ₀, the Rabi lineshape selects the
> velocity class with k_eff·v ≈ −δ₀ and reports its population weight
> via P_↑.
> 
> The “π/2 pulse” picture is misleading for the detuning scan. The
> accumulated rotation reaches π/2 only *on resonance* (δ = 0); at the
> typical Doppler shifts encountered (δ/Ω ≫ 1), the effective rotation
> is suppressed as ~(Ω/δ)². The system is performing frequency-domain
> tomography of the velocity distribution, not coherent gate dynamics.
> 
> The simulation confirms: the coherence envelope (Bloch vector length
> vs. detuning) directly maps the velocity distribution convolved with
> the Rabi instrument function. Its progressive broadening from α = 0 → 5
> is the Doppler mechanism made visible.
> 
> Contrast loss (σ_z at δ = 0) is the frequency-integrated version,
> discarding spectral information. The non-monotonic trend
> 0.61 → 0.71 → 0.84 → 0.75 encodes velocity-distribution shape.

### 1.5 Stroboscopic sampling

In the ideal limit, each pulse is instantaneous and acts at a precise
motional phase φ_m = ω_m · t_n. If pulses are synchronised to the
motional frequency (stroboscopic condition), all pulses sample the
*same* phase of oscillation. The accumulated signal is
N_pulses × (single-pulse signal), with coherent enhancement.

This is literal stroboscopic illumination: a vibrating object appears
frozen when the flash rate matches the oscillation.

> **⚠ Deviation (22 pulses, 1 per cycle, 17 μs total)**
> 
> The scheme uses approximately **22 laser pulses, one per motional
> cycle**, accumulating to a stroboscopic π/2 in ~17 μs over ~22
> oscillation periods. (The “326” in the simulation settings is the
> number of numerical time steps, not laser flashes; 326 pulses ×
> 0.070 rad/pulse ≈ 23 rad ≈ 7π — inconsistent with π/2.)
> 
> With 1 flash per cycle, the sampling is *sparse and synchronous* —
> true stroboscopic illumination. Each flash catches the ion at the
> same motional phase. There is no averaging over different phases
> within one measurement; each pulse redundantly samples the same
> phase-space point.
> 
> **Structural trade-off:** The stroboscopic scheme shifts the
> impulsiveness requirement from “δt ≪ T_m” (Monroe) to “phase
> stability over N ≈ 22 pulses.” The required phase coherence is:
> 
> ```
> Δω_m/ω_m ≪ 1/(ω_m · T_total) ≈ 0.007
> ```
> 
> This is a fractional frequency stability of ~0.7%, which is not extreme.
> But any jitter between the RF drive and the Raman modulation appears
> directly as phase washout across the 22-pulse accumulation.
> 
> Motional heating over T_total ≈ 17 μs: at a typical rate ṅ ~ 1 phonon/ms,
> the accumulated heating is Δn ≈ 0.017 — negligible. This becomes
> relevant only for longer sequences or higher heating rates.

### 1.6 Spin–motion factorisation and backaction

In the ideal limit (linear coupling, instantaneous pulses, low η), the
spin and motional states remain approximately factorisable after the
interaction. The measurement extracts information about motion with
minimal backaction on the motional state.

This is the structural basis for repeated measurements, QND protocols,
and back-action evasion.

> **⚠ Deviation (two types of backaction)**
> 
> At η ≈ 0.4, the exponential coupling creates spin–motion entanglement
> during each pulse. The simulation entropy panels confirm this: entropy
> peaks where the analysis pulse partially drives transitions, creating
> entangled spin–motion states.
> 
> Two distinct mechanisms of backaction must be separated:
> 
> **(i) Unitary backaction (reversible entanglement).** During the
> pulse train, spin and motion become entangled. If the spin is not
> measured, this entanglement is in principle reversible — a spin-echo
> or refocusing sequence could disentangle them. The unitary backaction
> is characterised by the purity Tr(ρ_motion²) of the reduced motional
> state, and by the quadrature moments ⟨X⟩, ⟨P⟩, ⟨X²⟩, ⟨P²⟩ before
> and after the interaction.
> 
> **(ii) Measurement-induced backaction (irreversible collapse).** When
> the spin is projectively measured (fluorescence detection), the motional
> state undergoes non-Gaussian collapse conditioned on the measurement
> outcome. The disturbance depends on the spin–motion entanglement at
> the moment of projection, which scales with η and N_pulses.
> 
> In the present protocol, the final readout is projective (spin-state
> detection). Therefore both mechanisms contribute:
> 
> - The accumulated unitary entanglement sets the *size* of the collapse.
> - The projection makes the disturbance irreversible and state-dependent.
> 
> For a weak-measurement interpretation (signal averaged over many
> experimental repetitions), the per-run backaction may be small in
> the ensemble average. But for single-shot state reconstruction,
> the measurement-induced collapse is the dominant effect.
> 
> Quantifying both contributions — unitary (purity, quadrature disturbance)
> and projective (conditional state, coherent-state overlap) — is the
> deliverable of WP-A.3 and the prerequisite for all downstream claims.

-----

## 2. Comparison with Monroe’s Ultrafast Programme

|Parameter           |Monroe (Yb⁺)         |Hasse (Ba⁺ AC)          |Ratio / contrast     |
|--------------------|---------------------|------------------------|---------------------|
|Pulse duration      |~10 ps               |~40 ns                  |×4000 longer         |
|δt / T_m            |~10⁻⁵                |~0.05                   |×5000 less impulsive |
|Pulses per operation|1–4 kicks            |~22 (stroboscopic)      |Coherent accumulation|
|η                   |0.1–0.3 (optical)    |0.40 (AC Raman)         |Comparable but higher|
|θ per pulse         |~π (single kick)     |~0.07 rad (4°)          |×45 smaller          |
|Temperature range   |ZPM to ~10⁴ phonons  |ZPM to ~25 phonons      |Monroe wider         |
|Primary application |Interferometry, gates|Phase-space spectroscopy|Different goals      |

Monroe’s temperature independence arises from three properties: δt ≪ T_m,
displacement operator factorisation, and cancellation sequences in fast gates.
The present protocol does not inherit this full temperature insensitivity.
Instead it maintains **phase selectivity under moderate motional occupation**:
the stroboscopic lock ensures all 22 pulses sample the same oscillation phase,
but the velocity distribution still broadens the Doppler lineshape and limits
the effective measurement bandwidth.

The theoretical framework for fast gates outside the Lamb–Dicke regime
originates with García-Ripoll, Zoller, and Cirac [García-Ripoll2003],
who showed that gates operating much faster than the trap period become
insensitive to temperature. Duan [Duan2004] extended this to scalable
architectures. Mizrahi et al. [Mizrahi2013, Mizrahi2014] provided the
experimental methodology for ultrafast spin–motion entanglement with
single trapped ions, achieving entanglement in < 50 ps. Johnson et al.
[Johnson2015] demonstrated sensing from ZPM to n̄ ~ 10⁴, and [Johnson2017]
created Schrödinger cat states with separations up to Δx ≈ 0.5 μm using
sequences of impulsive kicks.

-----

## 3. Physics Identity: Floquet-Synchronised Quadrature Spectroscopy

The preceding comparison might suggest that the present scheme is a
“softened Monroe kick” — an impulsive protocol degraded by finite pulse
duration. This framing is misleading.

**The protocol is a Floquet-synchronised quadrature probe, not a slow
approximation to an ultrafast kick.**

The distinction matters:

**(a) Impulsiveness is not required.** The Monroe scheme needs δt ≪ T_m
because each kick must act at a well-defined motional phase. The present
scheme achieves the same phase selectivity through synchronisation: the
pulse train is locked to the motional frequency, so each of the ~22 pulses
arrives at the same oscillation phase. The information comes from coherent
accumulation over the Floquet period, not from single-pulse impulsiveness.

**(b) The nonlinear η is both asset and liability.** In the Monroe scheme,
large η is tolerated because the kick factorises (impulsive limit). Here,
large η is *exploited*: the exponential coupling C = exp(iη(a + a†)) at
η ≈ 0.4 accesses higher harmonics of the characteristic function, providing
richer phase-space information than a linear probe could. The same
nonlinearity that compromises BAE enables tomography.

**(c) The measurement is spectroscopic.** The detuning scan sweeps a
narrowband frequency discriminator (Rabi linewidth ~Ω) across the
velocity distribution (Doppler width ≫ Ω). This is frequency-domain
tomography: each detuning point reports the weight of one velocity class.
The coherence envelope vs. detuning is a convolved image of the
velocity distribution. This is closer to absorption spectroscopy
than to coherent gate dynamics.

**(d) Tomography is plausible even without BAE.** The two measurement
channels — phase shift (position) and Doppler spectrum (momentum) —
together access the full phase space. The characteristic function
χ(ξ) = Tr[ρ exp(iξ x̂/x₀)] can in principle be reconstructed from the
combined data. This does not require single-quadrature coupling or
BAE; it requires only injectivity and stability of the map ρ → data,
which is the question addressed by WP-C.

-----

## 4. What the Deviations Mean for the Dossier

### Principles that survive

**P1 — Phase lock.** The four-oscillator phase lock (L1, COMPATIBLE) is
the operational substitute for single-pulse impulsiveness. 22 phase-locked
flashes, one per cycle, is a clean stroboscope.

**P2 — Super-resolution.** Geometric: λ_eff ≈ 140 nm. Holds regardless
of η or pulse duration (L3, COMPATIBLE).

**P3 — Doppler momentum readout.** The detuning scan encodes the velocity
distribution. This mechanism is *enhanced* by large η (bigger Doppler shifts).
The deviation from the ideal limit is quantitative (intra-pulse Magnus
correction), not qualitative.

### Principles that require verification

**P4 — Channel separation (L2).** Clean position and momentum channels
exist only in the ideal limit. At η ≈ 0.4 with 40 ns pulses, crosstalk
between channels must be bounded. The Magnus correction (§1.1) sets
the scale (WP-A.1).

**P5 — Backaction (L5).** Small backaction requires either low η (Lamb–Dicke)
or impulsive pulses (Monroe regime). We have neither. Both unitary and
measurement-induced contributions must be quantified separately (WP-A.3).

**P6 — BAE compatibility (L6).** Requires linear single-quadrature coupling.
At η ≈ 0.4 the exponential operator couples both quadratures — quadrature
selectivity is lost (§1.2). Whether a perturbative linear regime exists
in some accessible parameter window is open (WP-D).

**P7 — Tomographic injectivity (L7).** The nonlinear coupling at η ≈ 0.4
accesses higher harmonics — an asset for χ(ξ) sampling — but only if
the map ρ → (phase, Doppler spectrum) is injective and stable under
noise. This must be demonstrated (WP-C).

-----

## 5. Summary Table

|Ideal-limit principle        |Status at our parameters                     |Ledger|Action   |
|-----------------------------|---------------------------------------------|------|---------|
|Impulsive kick (δt ≪ T_m)    |δt/T_m ≈ 0.05; Magnus correction O(ω_m δt)   |L1 (✓)|WP-A.1   |
|Lamb–Dicke (η ≪ 1)           |η ≈ 0.4; quadrature selectivity lost         |L5, L6|WP-A.3   |
|Linear position coupling     |Exponential; nonlinear (20% at 2nd order)    |L6    |WP-D     |
|Single-quadrature backaction |Both quadratures coupled                     |L5    |WP-A.3   |
|Clean channel separation     |Crosstalk bounded by Magnus + η² terms       |L2    |WP-A.1   |
|Temperature-independent kicks|Phase-selective, not temperature-independent |L1, L8|—        |
|Resolved sidebands           |Doppler-dominated; spectroscopic regime      |—     |WP-B     |
|Spin–motion factorisation    |Entanglement; unitary + projective backaction|L5, L7|WP-A.3, C|

-----

## 6. Corrected Experimental Parameters

|Parameter                   |Value           |Note                    |
|----------------------------|----------------|------------------------|
|Mode frequency ω_m/(2π)     |1.3 MHz         |                        |
|Motional period T_m         |769 ns          |                        |
|Effective η                 |0.397           |AC Raman, LF mode       |
|Bare Rabi rate Ω/(2π)       |0.300 MHz       |                        |
|Eff. carrier Rabi Ω_eff/(2π)|0.277 MHz       |= Ω · exp(−η²/2)        |
|Pulse duration δt           |40 ns           |                        |
|δt/T_m                      |0.052           |                        |
|Rotation per pulse θ        |0.070 rad (4.0°)|= Ω_eff · δt            |
|**Pulses for π/2**          |**~22**         |**1 per motional cycle**|
|Total π/2 time              |17.0 μs         |= 22 × T_m ≈ 16.9 μs    |
|Duty cycle                  |5.2%            |= δt/T_m                |
|Thermal background ⟨n⟩      |0.001           |                        |
|AOM setup                   |fast            |                        |

-----

## References

- **[Braginsky1980]** V. B. Braginsky and Yu. I. Vorontsov, “Quantum-Mechanical Limitations in Macroscopic Experiments and Modern Experimental Technique,” Sov. Phys. Usp. **23**, 644 (1980).
- **[Caves1980]** C. M. Caves, K. S. Thorne, R. W. P. Drever, V. D. Sandberg, and M. Zimmermann, “On the measurement of a weak classical force coupled to a quantum-mechanical oscillator,” Rev. Mod. Phys. **52**, 341 (1980).
- **[Duan2004]** L.-M. Duan, “Scaling Ion Trap Quantum Computation through Fast Quantum Gates,” Phys. Rev. Lett. **93**, 100502 (2004).
- **[García-Ripoll2003]** J. J. García-Ripoll, P. Zoller, and J. I. Cirac, “Speed Optimized Two-Qubit Gates with Laser Coherent Control Techniques for Ion Trap Quantum Computing,” Phys. Rev. Lett. **91**, 157901 (2003).
- **[García-Ripoll2005]** J. J. García-Ripoll, P. Zoller, and J. I. Cirac, “Coherent control of trapped ions using off-resonant lasers,” Phys. Rev. A **71**, 062309 (2005).
- **[Hasse2024]** F. Hasse, D. Palani, R. Thomm, U. Warring, and T. Schaetz, “Phase-stable travelling waves stroboscopically matched for super-resolved observation of trapped-ion dynamics,” Phys. Rev. A **109**, 053105 (2024); arXiv: 2309.15580.
- **[Johnson2015]** K. G. Johnson, B. Neyenhuis, J. Mizrahi, J. D. Wong-Campos, and C. Monroe, “Sensing Atomic Motion from the Zero Point to Room Temperature with Ultrafast Atom Interferometry,” Phys. Rev. Lett. **115**, 213001 (2015).
- **[Johnson2017]** K. G. Johnson, J. D. Wong-Campos, B. Neyenhuis, J. Mizrahi, and C. Monroe, “Ultrafast creation of large Schrödinger cat states of an atom,” Nat. Commun. **8**, 697 (2017).
- **[Leibfried2003]** D. Leibfried, R. Blatt, C. Monroe, and D. Wineland, “Quantum dynamics of single trapped ions,” Rev. Mod. Phys. **75**, 281 (2003).
- **[Mizrahi2013]** J. Mizrahi, C. Senko, B. Neyenhuis, K. G. Johnson, W. C. Campbell, C. W. S. Conover, and C. Monroe, “Ultrafast Spin–Motion Entanglement and Interferometry with a Single Atom,” Phys. Rev. Lett. **110**, 203001 (2013).
- **[Mizrahi2014]** J. Mizrahi, B. Neyenhuis, K. G. Johnson, W. C. Campbell, C. Senko, D. Hayes, and C. Monroe, “Quantum control of qubits and atomic motion using ultrafast laser pulses,” Appl. Phys. B **114**, 45–61 (2014).
- **[Monroe1996]** C. Monroe, D. M. Meekhof, B. E. King, and D. J. Wineland, “A ‘Schrödinger Cat’ Superposition State of an Atom,” Science **272**, 1131 (1996).
- **[Wong-Campos2017]** J. D. Wong-Campos, S. A. Moses, K. G. Johnson, and C. Monroe, “Demonstration of Two-Atom Entanglement with Ultrafast Optical Pulses,” Phys. Rev. Lett. **119**, 230501 (2017).

-----

*Changelog is cumulative.*

*v0.2 changelog: Corrected pulse count from 326 → ~22 (1 per motional cycle).
Incorporated Guardian tightening: Magnus correction explicit in §1.1,
quadrature selectivity loss in §1.2, spectroscopic regime in §1.4,
unitary vs. projective backaction in §1.6, Floquet identity in §3,
temperature-independence caveat in §2. Added §6 corrected parameter table.*

*v0.2.1 changelog: Fixed missing 2π factor in phase-blur table (§1.1).
Old values (0.04, 0.12, 0.21 rad) were δ_D/(2π)·δt, not δ_D·δt —
off by factor 2π ≈ 6.28. Corrected: 0.26, 0.78, 1.30 rad. Separated
coherent peak blur from ZPM RMS blur (0.13 rad). Updated §1.3 cross-
reference. Added commutator non-commutativity statement after Magnus
introduction.*

*v0.2.2 changelog: Notational tightening. Table header formula now reads
Δφ_peak = 2π·[δ_D^peak/(2π)]·δt to prevent misreading with the cyclic-
frequency column. Same for RMS line. “Order-unity blur” anchored as
“~1 rad, i.e. tens of degrees.” Commutator line names H_m (harmonic
motional) and H_int(t) (laser interaction) for readability.*

*v0.2.3 changelog: Physics-precision tightening of §1.1 blur block.
(A) Δφ identified as heuristic; finite-δt effects split into geometric
phase averaging (ω_m δt) and Doppler-detuning Rabi distortion (δ_D/Ω).
(B) Velocity convention pinned: v_peak = ω_m x₀ √2 |α|. (C) ZPM RMS
blur (0.13 rad) placed against ω_m δt ≈ 0.33 rad baseline. (D) Magnus
averaging statement softened: “replaces” → “acts similarly to replacing
… pulse-envelope-weighted average.”*

*v0.2.4 changelog: Final precision pass on §1.1. (1) Geometric averaging
now correctly attributed to k_eff·x(t) variation (both ω_m δt and k_eff v δt,
state-dependent), not ω_m δt alone. (2) Doppler distortion control parameter
specified as δ_D/Ω_eff (not bare Ω). (3) σ labelled “RMS Doppler width.”
(4) Envelope-averaging qualifier: “to leading order, for a smooth pulse
envelope.”*
