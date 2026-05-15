# Extraction — Leibfried, Meekhof, King, Monroe, Itano & Wineland (1996)

**Citation key:** [LMKMIW96]
**Full reference:** D. Leibfried, D. M. Meekhof, B. E. King, C. Monroe,
W. M. Itano, and D. J. Wineland,
*Experimental Determination of the Motional Quantum State of a Trapped Atom*,
Phys. Rev. Lett. **77**, 4281 (1996). Published 18 November 1996.
DOI: [10.1103/PhysRevLett.77.4281](https://doi.org/10.1103/PhysRevLett.77.4281).

**Authors verified:** D. Leibfried, D. M. Meekhof, B. E. King, C.
Monroe, W. M. Itano, D. J. Wineland (NIST Boulder, Time and Frequency
Division).

**Extraction date:** 2026-05-15.

**Note on source.** APS PRL paywalled; no arXiv preprint (pre-1997
AMO arXiv era). Extraction anchored on confirmed bibliographic data,
the published abstract / summary, and the [FH20] reference [2]
context which identifies [LMKMIW96] as the predecessor trapped-ion
Wigner reconstruction the FH20 protocol supersedes by factor ~20 in
measurement time.

**One-line summary.** First experimental Wigner-function
reconstruction of a trapped-ion motional state. Uses a
**displaced-Fock-population** approach on a single ⁹Be⁺ ion: apply
coherent displacements with varied amplitude and phase, measure the
resulting Fock-state populations via blue-sideband Rabi oscillations,
and linearly combine to obtain the Wigner function.

**Why it matters for WP-W.** [LMKMIW96] is the **first experimental
realisation** of trapped-ion motional-state tomography (one year
after the [Wal95] proposal). It establishes the "displaced
expectation value of a number-counting observable → Wigner function"
chain that [LD97], [Bertet02], and [FH20] later refine into the
displaced-parity / direct-$\chi$ chain that WP-W inherits.

-----

## 1. Core method — displaced-Fock-population Wigner reconstruction

The Wigner function of a motional state $\rho$ admits the
*number-state expansion* (a standard CG69 result):

$$
W(\alpha) = \frac{2}{\pi}\sum_{n=0}^{\infty}(-1)^n\,P_n(\alpha)
\quad\text{where}\quad
P_n(\alpha) = \langle n|\hat D^\dagger(\alpha)\,\rho\,\hat D(\alpha)|n\rangle.
$$

i.e. the Wigner function at phase-space point $\alpha$ is a
*staggered sum* of the displaced Fock-state populations. The factor
$(-1)^n$ is the photon-number parity expectation, recovering the
displaced-parity expression of [LD97]; LMKMIW96 implements this by
measuring the *individual* populations $P_n(\alpha)$ for $n = 0, 1,
\ldots$ and summing.

### 1.1 Experimental sequence

1. Cool the ⁹Be⁺ ion to the motional ground state $|0\rangle$ along
   the chosen axial mode.
2. Prepare the test motional state $\rho$ (coherent, thermal, squeezed,
   or Fock — LMKMIW96 demonstrates all four classes).
3. Apply a coherent displacement $\hat D(-\alpha)$ with chosen amplitude
   $|\alpha|$ and phase $\arg\alpha$ via a classical electric drive at
   the trap frequency.
4. Read out the Fock-state populations $P_n$ by driving the blue
   sideband ($\Delta = +\omega_m$) and observing the resulting Rabi
   oscillation on the spin transition; the multi-frequency oscillation
   resolves each $P_n$ via spectral filtering.
5. Compute $W(\alpha) = (2/\pi)\sum(-1)^n P_n(\alpha)$.

The protocol is **slow**: extracting $P_n$ requires resolving
multiple Rabi frequencies, which means many sequence repetitions per
phase-space point. [FH20] reports a factor-of-20 speedup over this
displaced-Fock approach by going to direct-$\chi$ readout.

### 1.2 States demonstrated

LMKMIW96 reconstructs Wigner functions for four classes:

1. **Ground state** $|0\rangle$ — Gaussian, peaked at origin.
2. **Coherent state** $|\alpha\rangle$ — Gaussian, displaced from origin.
3. **Squeezed state** $|\xi\rangle$ — elliptical Gaussian.
4. **Fock state** $|n\rangle$ for small $n$ — ring of negativity at radius $\sqrt{n+1/2}$.

The reconstructed Wigner functions are sensitive indicators of
**decoherence**: any motional dephasing or heating during the
displacement-and-readout sequence manifests as Wigner-function
broadening / negativity loss. LMKMIW96 uses this sensitivity to
characterise the NIST trap's decoherence properties.

-----

## 2. Relation to WP-W's lineage

| year | reference | method | observable | states |
|---|---|---|---|---|
| 1995 | [Wal95] | proposal: ion → electronic mapping → fluorescence | (any) | (any) |
| **1996** | **[LMKMIW96]** | **first experiment: displaced + Fock populations + Σ(-1)ⁿ Pₙ** | **Fock populations** | **ground, coherent, squeezed, Fock** |
| 1997 | [LD97] | proposal: dispersive coupling + Ramsey + parity readout | displaced parity | (any) |
| 2002 | [Bertet02] | cQED experiment: LD97 protocol | parity | Fock $\|1\rangle$ |
| 2009 | [Hof09] | cQED experiment in superconducting circuits | parity (LD97 variant) | Fock, coherent superpositions |
| 2020 | [FH20] | trapped-ion direct-$\chi$ on Ca⁺ via bichromatic SDF | Re/Im of $\langle\hat D\rangle$ | displaced-squeezed, cat, GKP |

**WP-W's relationship to [LMKMIW96]:**
- Both target trapped-ion motional-state reconstruction.
- LMKMIW96 uses **resonant Be⁺ blue-sideband Rabi oscillation** to extract Fock populations; WP-W uses **stroboscopic monochromatic AC train on Mg⁺** to sample $\chi(\beta)$.
- LMKMIW96 reconstructs $W(\alpha)$ by *summing displaced Fock populations*; WP-W reconstructs $W(\alpha)$ by *Fourier-transforming the directly-measured $\chi(\beta)$* (the [FH20] generalisation).
- Both can in principle reconstruct the same non-Gaussian states (Fock, cat); the difference is in measurement efficiency and phase-space sampling pattern.

-----

## 3. What [LMKMIW96] does NOT do (relative to WP-W / FH20)

- Does **not** measure $\chi(\beta)$ directly — that requires the
  displaced-parity ([LD97]) or direct-$\chi$ ([FH20]) variants.
- Does **not** use a Fourier-transform inversion. Each phase-space
  point is computed by summing the displaced-Fock-population series
  $\sum(-1)^n P_n$, which converges in principle but is slow in practice.
- Does **not** address the *stroboscopic-comb* sampling structure that
  WP-W inherits from [Hasse24]. LMKMIW96 uses single classical
  displacements + Rabi-resolved population measurements; the displacement
  is a one-shot operation, not a stroboscopic train.
- Does **not** treat high-$\eta$ corrections systematically. ⁹Be⁺ axial
  mode at NIST had $\eta \approx 0.2$, comparable to Mg⁺'s $\eta = 0.40$,
  but LMKMIW96's analysis stays largely in the LD-perturbative limit.

-----

## 4. Direct implications for WP-W

1. **§References**: add [LMKMIW96] as the first experimental
   trapped-ion Wigner reconstruction. This is the "Leibfried–Wineland
   tomography" the WP-W reviewer flagged as missing.
2. **§1 lineage statement**: optionally enrich the lineage to mention
   the displaced-Fock-population predecessor (LMKMIW96) alongside the
   displaced-parity (LD97) and direct-$\chi$ (FH20) variants.
3. **§Analytical background**: note that the displaced-Fock-population
   approach is the historical first realisation; the displaced-parity
   and direct-$\chi$ variants are efficiency optimisations.
4. **WP-W's deciding-state criterion** (§7#5) uses Fock $|2\rangle$ and
   cat as the resolution stress test. [LMKMIW96] reconstructed Fock
   states up to $n \approx 2$ on ⁹Be⁺ in 1996. Reconstruction *capability*
   for Fock $|2\rangle$ is not novel; WP-W's contribution is the
   stroboscopic-engine pipeline and the perturbative-regime grid
   resolution analysis.

-----

## 5. Contextual paragraph (for `contextual-notes.md`)

[LMKMIW96] is the **first experimental realisation** of trapped-ion
motional-state tomography. Leibfried *et al.* at NIST Boulder
reconstructed Wigner functions for the ground, coherent, squeezed, and
Fock-state classes on a single ⁹Be⁺ ion in 1996, one year after
[Wal95]'s proposal, by applying coherent displacements and measuring
the resulting Fock-state populations via blue-sideband Rabi
oscillations, then summing $W(\alpha) = (2/\pi)\sum(-1)^n P_n(\alpha)$.
This established the trapped-ion phase-space tomography programme; all
subsequent variants ([LD97] parity readout, [FH20] direct-$\chi$
readout) are efficiency optimisations of the same underlying chain.

WP-W's debt to [LMKMIW96] is principally historical: the *capability*
of reconstructing Fock or coherent states in a trapped ion has been
established for nearly three decades. WP-W's contribution is the
*specific stroboscopic-comb adaptation* of the modern direct-$\chi$
variant ([FH20]) to the [Hasse24] monochromatic engine.
