# WP-W Contextual Notes — Lineage Map

**Purpose.** Synthesises the lit-review pass (per §5a discipline)
into the lineage WP-W inherits, the experimental and theoretical
precedents, and the *narrow* set of claims WP-W can actually make as
genuinely new contributions.

**Sources.** Per-paper extractions in [`extractions/`](./extractions/);
audit trail in [`review-tracker.md`](./review-tracker.md).

**Compiled:** 2026-05-15.

-----

## 1. The full lineage, by year

| year | reference | key | platform | contribution |
|---|---|---|---|---|
| 1969 | Cahill & Glauber | [CG69] | (formalism) | $s$-ordered quasiprobability family; symmetric $\chi(\beta) = \langle\hat D(\beta)\rangle$ ↔ Wigner $W(\alpha)$ via 2D Fourier transform. State-general. |
| 1995 | Wallentowitz & Vogel | [Wal95] | trapped ion (proposal) | **First proposal for direct readout of trapped-ion motional state** via electronic mapping + fluorescence on a separate strong transition. |
| 1996 | Leibfried et al. (NIST) | [LMKMIW96] | ⁹Be⁺ (experiment) | **First experimental trapped-ion Wigner reconstruction.** Displaced-Fock-population method: $W(\alpha) = (2/\pi)\sum(-1)^n P_n(\alpha)$. Demonstrated ground / coherent / squeezed / Fock states. |
| 1997 | Lutterbach & Davidovich | [LD97] | cavity QED + trapped ion (proposal) | **Displaced-parity scheme.** Dispersive coupling + Ramsey interferometry → $W(\alpha) = (2/\pi)\langle\hat D^\dagger(\alpha)\hat P\hat D(\alpha)\rangle$. |
| 2002 | Bertet et al. (Brune/Haroche) | [Bertet02] | Rb Rydberg + microwave cavity (experiment) | **First experimental implementation of [LD97]**. Reconstructed $W$ for vacuum and one-photon Fock state in a high-$Q$ microwave cavity. Demonstrated negative $W(0) = -2/\pi$ of $\|1\rangle$. |
| 2003 | Leibfried, Blatt, Monroe, Wineland | [LBMW03] | trapped-ion (review) | Canonical trapped-ion review; engine-context citation. |
| 2009 | Hofheinz et al. | [Hof09] | superconducting cQED (experiment) | Phase-space synthesis and Wigner tomography in cQED using parity-readout variants of [LD97]. *Nature* **459**, 546 (2009), 11 authors. |
| 2012 | Mirkhalaf & Mølmer | [STO12] | trapped-ion (proposal) | Sympathetic-readout tomography for *dark* ions via collective modes. Off WP-W main lineage. |
| 2016 | Clos, Porras, Warring, Schaetz | [Clos16] | trapped ion (experiment) | Hasse-group predecessor; established the $H_\text{TI} = \omega_z\sigma_z/2 + \omega_m a^\dagger a + (\Omega/2)[C\sigma_- + \mathrm{h.c.}]$ Hamiltonian form WP-W and Hasse2024 both inherit. |
| 2020 | Flühmann & Home | [FH20] | ⁴⁰Ca⁺ trapped ion (experiment) | **Direct $\chi$-function tomography in trapped ions.** Bichromatic SDF + carrier rotation → Re/Im of $\langle\hat D\rangle$ per phase-space point. 2D-FFT $\chi \to W$. Demonstrated displaced-squeezed, squeezed-cat, approximate-GKP states. Factor-of-20 measurement-time speedup over [LMKMIW96]-style displaced-Fock-population reconstruction. |
| 2024 | Hasse, Palani, Thomm, Warring, Schaetz | [Hasse24] | ²⁵Mg⁺ trapped ion (experiment) | **Stroboscopic AC pulse-train protocol.** 2D scan over $(\varphi, \vartheta_0)$. Position $\langle X\rangle$ from linear analysis-phase shifts; momentum $\|\langle P\rangle\|$ from nonlinear contrast variation. Back-action map (Appendix D, Fig 6b). Squeezed-state extension (Appendix E). Does **not** invoke $\chi$-function tomography. |
| 2026+ | WP-W | (this WP) | Mg⁺ numerical | **Stroboscopic-comb adaptation of [FH20]'s $\chi$-FFT framework to [Hasse24]'s monochromatic engine.** High-$\eta$ regime; bridge between saturated kick-off (WP-TOM) and perturbative inversion. |

-----

## 2. What each reference contributes to WP-W

**[CG69]** — *foundation*. Legitimises the state-general χ↔W Fourier
duality. Cited for the formal claim that the chain applies to any
$\rho_m$, Gaussian or non-Gaussian, pure or mixed. *(WP-W §Analytical
bullets 2/3/4; §1 hypothesis.)*

**[Wal95]** — *historical origin*. The earliest trapped-ion motional-
state tomography proposal. Should be the *first* citation in WP-W's
lineage statement chronologically. *(WP-W §1, §Analytical
background.)*

**[LMKMIW96]** — *first experimental realisation*. Established that
trapped-ion Wigner tomography is experimentally tractable. Uses
displaced-Fock-population approach; superseded by direct-χ ([FH20])
in measurement efficiency but covers the same state classes. *(WP-W
§Analytical background; §7#4 Fock-state benchmark context.)*

**[LD97]** — *theoretical origin of the parity-readout / direct-
measurement lineage*. Displaced-parity expression
$W(\alpha) = (2/\pi)\langle\hat D^\dagger(\alpha)\hat P\hat D(\alpha)\rangle$.
Applies to both cavity QED and ion traps. *(WP-W §Analytical
bullet 2; §1 lineage.)*

**[Bertet02]** — *first cQED experimental implementation of [LD97]*.
Direct measurement of $W$ for vacuum and Fock $|1\rangle$, including
the negative-$W$ signature. The cQED side of the experimental lineage.
*(WP-W §Analytical background.)*

**[Hof09]** — *cQED in superconducting circuits*. Implementation in
solid-state cavity QED platforms; demonstrates the framework's
generality across bosonic-mode platforms. *(WP-W §1 lineage; §Analytical background.)*

**[STO12]** — *sympathetic-readout extension*. Off WP-W's main
lineage; cited only as broader context for the experimental
sophistication of trapped-ion phase-space tomography by 2012.

**[Clos16]** — *Hasse-group predecessor*. Source of the $H_\text{TI}$
form WP-W's engine implements. Anchors the trapped-ion Hamiltonian
convention WP-W inherits.

**[FH20]** — *direct theoretical and experimental precedent for WP-W's
reconstruction pipeline*. Implements the full χ-FFT chain in
trapped ions. Demonstrates non-Gaussian state reconstruction
(displaced-squeezed, cat, GKP) more aggressively than WP-W plans. **The
χ-FFT framework that WP-W cites is not WP-W's contribution — it is
FH20's, adopted by WP-W and adapted to a different drive protocol.**
*(WP-W §1, §Analytical bullets 2/4.)*

**[Hasse24]** — *direct experimental antecedent*. The stroboscopic AC
pulse-train protocol, the H_TI Hamiltonian, the 2D
$(\varphi, \vartheta_0)$ scan, the back-action concept, and the
squeezed-state extension framework all originate here. **The protocol
WP-W reinterprets is not WP-W's; it is Hasse2024's, adopted by WP-W
and theoretically reinterpreted via [FH20]'s χ-tomography lens.** *(WP-W
Experiment pillar; §1; §3 motivation 3.)*

-----

## 3. What WP-W actually contributes

After the lit-review, WP-W's claims narrow to the following *bona fide*
contributions:

### 3.1 Adaptation of [FH20]'s χ-FFT to [Hasse24]'s engine

[FH20] uses a **CW bichromatic SDF** on Ca⁺ at $\eta = 0.05$. [Hasse24]
uses a **stroboscopic monochromatic AC train** on Mg⁺ at $\eta = 0.40$.
These are *different protocols on different platforms*. WP-W's
analytical contribution is to recognise that **the same χ-FFT
inversion chain applies to [Hasse24]'s protocol**, with the comb
structure entering through the Dirichlet kernel forward map
($\beta_\text{tot} = N|\beta_0|\,\mathcal D_N$). The
*inverse-Dirichlet Cartesian targeting rule* (WP-W §2) is the
stroboscopic-specific piece that [FH20] does not need (continuous
β samples) and that has no precedent in the lineage.

### 3.2 High-$\eta$ regime

[FH20] operates at $\eta \approx 0.05$, deep in the LD-perturbative
limit. [Hasse24] / WP-W operates at $\eta = 0.40$, where LD
corrections become $\mathcal O(\eta^2) \approx 16\%$ and matter. WP-W's
explicit *approximation hierarchy* (§Analytical bullet 5) and the
*ideal-SDF / native-engine bridge* analysis (§7#3) address regime
issues that [FH20]'s small-$\eta$ platform sidesteps.

### 3.3 The "no limit recovers ideal SDF" finding (§7#3)

[FH20]'s bichromatic SDF *natively* implements the ideal
$D(\sigma_x\beta)$ chain in the resolved-sideband / LD-perturbative
limit. [Hasse24]'s monochromatic engine *does not* — even at
sideband resonance the leading non-trivial term is a transverse
Jaynes–Cummings coupling, not a longitudinal $\sigma_z$-conditioned
displacement. WP-W's §7#3 analysis pins this down explicitly. **This
finding is specific to monochromatic engines and is, to our knowledge,
not previously stated in the literature.**

### 3.4 Bridge between WP-TOM saturated regime and perturbative inversion

WP-W complements the kick-off
[wp-analysis-train-tomography](../../wp-analysis-train-tomography/)
template-matching at $\Omega_r N\delta t = \pi/2$ saturation with
perturbative-regime FFT inversion. Cross-comparison of saturated
template recovery and perturbative FFT centroid on the same Mg⁺
engine (WP-W §7#7) is a genuine new diagnostic — not pre-figured by
either [FH20] (perturbative only) or [Hasse24] (no inversion claim
made).

### 3.5 Cartesian Dirichlet-targeting rule (§2)

The inverse-Dirichlet rule that lands the physical $(\delta, \varphi)$
scan on FFT-friendly Cartesian $\beta$ nodes is a small but novel
contribution. [FH20] samples χ on a uniform polar / square grid in
β directly (no Dirichlet kernel in their forward map); [Hasse24]
samples in $(\varphi, \vartheta_0)$ space without inverting.
WP-W's rule turns the polar-vs-Cartesian resampling question into a
controlled edge-windowing problem.

-----

## 4. What WP-W *does not* contribute

To prevent overclaiming, the following lit-review-confirmed prior art
should be explicit in WP-W's narrative:

- The χ-FFT-Wigner framework is **[CG69] formalism** combined with
  **[FH20] experimental implementation in trapped ions**. Not WP-W.
- Non-Gaussian state reconstruction in trapped ions exists since
  **[LMKMIW96]** (Fock); modern non-Gaussian capability is **[FH20]**
  (cat, GKP). WP-W's Fock $|1\rangle$, $|2\rangle$ and cat
  reconstructions are demonstrations of *capability transfer to the
  Hasse engine*, not novelty.
- The stroboscopic protocol itself is **[Hasse24]**. Not WP-W.
- Back-action characterisation in the same protocol exists in
  **[Hasse24] Appendix D / Fig 6b**. WP-W's v0.5 back-action scope is
  *quantitative ideal-SDF-vs-native comparison*, not first
  characterisation.
- Squeezed-state extension framework with $\Delta t = 2\pi/(2\omega_m)$
  timing exists in **[Hasse24] Appendix E**. WP-W's v0.5 squeezed-vacuum
  deferral inherits this framework.
- Sympathetic-readout tomography (**[STO12]**) is not in WP-W's scope.
- GKP-state reconstruction at small $\eta$ is **[FH20]**; WP-W's
  deferral of GKP to a follow-up WP is a *grid-resolution* deferral,
  not a *capability* deferral.

-----

## 5. Updated minimum bibliography for v0.4

Replace the v0.4-polish-era five-pillar bibliography with:

1. **[CG69]** Cahill & Glauber — formalism foundation.
2. **[Wal95]** Wallentowitz & Vogel — earliest trapped-ion tomography proposal.
3. **[LMKMIW96]** Leibfried, Meekhof, King, Monroe, Itano, Wineland — first experimental trapped-ion Wigner reconstruction.
4. **[LD97]** Lutterbach & Davidovich — displaced-parity scheme.
5. **[Bertet02]** Bertet et al. (Brune/Haroche) — first cQED implementation of LD97.
6. **[Hof09]** Hofheinz et al. — superconducting cQED implementation.
7. **[Clos16]** Clos, Porras, Warring, Schaetz — Hasse-group $H_\text{TI}$ predecessor.
8. **[FH20]** Flühmann & Home — direct trapped-ion χ-tomography.
9. **[Hasse24]** Hasse, Palani, Thomm, Warring, Schaetz — direct experimental antecedent.
10. **[LBMW03]** Leibfried, Blatt, Monroe, Wineland (RMP review) — engine-context anchor.
11. **[STO12]** Mirkhalaf & Mølmer — contextual (sympathetic-readout).

This is the verified, narrative-aligned bibliography. The v0.4-polish
references list (with only six entries, two unverified) was incomplete.
