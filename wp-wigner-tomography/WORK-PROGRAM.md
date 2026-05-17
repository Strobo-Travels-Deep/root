# WP-W — Wigner-Like Reconstruction in the Lamb–Dicke / Idealised-Train Limit

**Work Program · v0.5 · 2026-05-15 (doc correction pass; lit-review pass: 2026-05-15)**
**Status:** *design closed; lit-review completed; v0.4 execution
complete; v0.5 doc-correction pass applied.* P0 + D2 + D3 + P1 + D4
all cleared on 2026-05-15 (see §8 v0.4-execution and the four
[logbook](./logbook/) entries). The v0.5 doc pass (§8) corrected
five conventions surfaced by execution — the ideal SDF is the
FH20-style $\sigma_x$ $D(\sigma_x\beta/2)$ (not $\sigma_z$); the χ
readout is direct $\langle\sigma_y\rangle-i\langle\sigma_z\rangle$
with no Gaussian prefactor; §4 D4 native-engine convention (N=30,
$\texttt{shift\_deg}=\omega_m\delta t/2$, no separate MW π/2)
documented. §2, §7#1–7, §4 deliverable commands, and §5 folder
layout are settled and reconciled to the executed artefacts. §5a
conduct conventions are codified. §References has 11 verified
entries with per-paper extractions in
[`refs/extractions/`](./refs/extractions/) and a lineage synthesis
in [`refs/contextual-notes.md`](./refs/contextual-notes.md).
Remaining: D1 analytical note (to inherit the corrected §Analytical
material). **Numbering:** WP-W (formal, per §7#6).

This document is the full WP that grew out of
[wp-analysis-train-tomography](../wp-analysis-train-tomography/)
— the quick-and-dirty kick-off ("WP-TOM v0.x") that established the
protocol encodes motional-state information amenable to phase-space
inversion, but mis-identified the inversion regime (see the kick-off
[logbook §6](../wp-analysis-train-tomography/logbook/2026-05-13-kickoff-expectations-and-run.md)).
WP-W picks up where that logbook ends: in the **Lamb–Dicke regime
with an idealised pulse train**, there should exist a clean
analytic mapping from the measured $(\delta, \varphi_\text{train})$
data to the motional Wigner function $W(\alpha)$. The inversion is
formally state-general — the symmetric characteristic function
$\chi$ is a complete state representation [CG69] — so the chain
applies to non-Gaussian inputs (Fock states, cat states) within the
LD / idealised-train approximations. Squeezed states likely require
terms beyond the linear Lamb–Dicke chain and are deferred to v0.5
per §7#4. Experimental validity, separately, depends on how closely the
native engine realises the ideal FH20-style $\sigma_x$ SDF — quantified
numerically as the §7#3 bridge residual rather than assumed.

-----

## Experiment

The apparatus context. We start in an *idealised* limit; deviations
from idealisation become diagnostics in their own right.

- **Idealised analysis train:** $N$ instantaneous SDF pulses at
  period $T_m$, single-tooth (i.e. drive only resolves the chosen
  sideband; carrier and higher sidebands suppressed), spin-dependent
  displacement $D(\sigma_x\,\beta_n)$ per pulse (FH20-style $\sigma_x$
  SDF, see §Analytical bullet 2 and §7#3) with
  $\beta_n = \beta_0\,e^{i\varphi_\text{train}}\,e^{i(\delta - k\omega_m)\,n\,T_m}$.
- **Drive regime:** *perturbative* — $|\beta_0|\,|\alpha| \ll 1$ per
  pulse, with fixed $|\beta_0| = 0.05$ in the first reconstruction pass.
  The nominal reconstruction train uses $N = 80$, giving central-tooth
  reach $|\beta_\text{tot}|_\text{max} = N|\beta_0| = 4.0$. Shorter
  $N \in \{20,40,60\}$ scans are retained as reach / tooth-width
  diagnostics.
- **Reference platform:** ²⁵Mg⁺ AC-Raman setup of
  [Hasse 2024](../refs/Hasse2024_PRA_109_053105.pdf),
  $\omega_m/(2\pi) = 1.300$ MHz, $\eta = 0.397$. The kick-off
  protocol's saturated regime ($\Omega_r N\delta t = \pi/2$) is the
  *opposite* limit and serves as a regime-boundary marker.
- **Input states under test:** five classes, in order of increasing
  Wigner-negativity stress: vacuum, coherent $|\alpha\rangle$, thermal
  $\rho_\text{th}(\bar n)$, Fock $|n\rangle$ (n = 0, 1, 2), cat
  $(|\alpha\rangle + |{-}\alpha\rangle)/\mathcal N$ at modest
  $|\alpha|$ (≈ 1.5).

## Analytical

The model layer — what the inversion machinery should reduce to in
the ideal limit, and where the LD / idealised-train approximation is
expected to break.

- **Phase-space mapping $(\delta, \varphi_\text{train}, N) \to \beta$.**
  Derive in closed form for the idealised train. The accumulated
  displacement is $\beta_\text{tot}(\delta, \varphi_\text{train}; N) = \beta_0\,e^{i\varphi_\text{train}}\,\mathcal{D}_N\!\bigl((\delta - k\omega_m)\,T_m\bigr)$
  with $\mathcal{D}_N(x) = \sum_{n=0}^{N-1} e^{inx}
  = e^{i(N-1)x/2}\sin(Nx/2)/\sin(x/2)$ the Dirichlet kernel. Each
  $(\delta, \varphi_\text{train})$ identifies one point in phase space.
- **Spin contrast $\to$ characteristic function.** Under the
  idealised FH20-style SDF (instantaneous, $\sigma_x$-coupled,
  $U=D(\sigma_x\,\beta_\text{tot}/2)$ with branch separation
  $\beta_\text{tot}$, perturbative), with the spin prepared on the
  $|{+}y\rangle$ equator state orthogonal to the SDF axis, the
  post-train χ readout is **direct**:
  $\chi_\text{engine}(\beta_\text{tot}) = \langle\sigma_y\rangle - i\langle\sigma_z\rangle = \chi_{\rho_m}(\beta_\text{tot})$
  with $\chi_{\rho_m}(\beta) = \mathrm{Tr}[\rho_m\,D(\beta)]$ the
  symmetric characteristic function [CG69]. **No Gaussian prefactor,
  no overall phase, no conjugation** — the σ_x-SDF / |+y⟩-equator
  combination reads χ point-by-point. ($\langle\sigma_x\rangle$
  carries no χ information: σ_x is the SDF axis itself.) The earlier
  v0.4 wording "$\sigma_z$-coupled" with a
  $C=\langle\sigma_x\rangle+i\langle\sigma_y\rangle=e^{-|\beta|^2/2}\chi$
  prefactor was inconsistent with the §2 inverse-Dirichlet forward
  map and with FH20, and is corrected here per the
  [2026-05-15 ideal-SDF logbook](./logbook/2026-05-15-ideal-sdf-primitive.md)
  §3.3 (the prefactor was an artefact conflated with the WP-E
  Doppler-broadening case; σ_z conditioning does not rotate under
  the σ_z spin precession that generates the Dirichlet kernel,
  whereas σ_x does — verified at $10^{-14}$ by the P1 sentinel).
  The displaced-parity origin of this measurement scheme traces to
  Lutterbach & Davidovich [LD97]; the modern trapped-ion
  implementation that motivates WP-W's protocol is the direct
  characteristic-function tomography of Flühmann & Home [FH20],
  whose bichromatic σ_x SDF on the |+y⟩ equator is exactly this
  ideal chain.
- **Wigner inversion.** $W(\alpha) = \pi^{-2}\int e^{\alpha\beta^* - \alpha^*\beta}\,\chi(\beta)\,d^2\beta$
  is the Fourier dual of the symmetric characteristic function [CG69].
  The 2D FFT of $\chi(\beta)$ over the $\beta$-grid therefore returns
  the Wigner function on the corresponding $\alpha$-grid. With this
  Fourier convention, finite $\beta$ support $B$ sets the raw $\alpha$
  resolution $\Delta\alpha \simeq \pi/(2B)$, while $\Delta\beta$ sets
  the alias-free half-width $\alpha_\text{Nyq} \simeq \pi/(2\Delta\beta)$.
- **Non-Gaussian validity.** The chain is *formally* state-general:
  $\chi_{\rho_m}$ is a complete representation of any density operator
  $\rho_m$, Gaussian or not, pure or mixed [CG69]. Specific
  predictions: Fock $|n\rangle$ has
  $\chi(\beta) = e^{-|\beta|^2/2}\,L_n(|\beta|^2)$ (Laguerre);
  even/odd cats have characteristic Gaussian humps at $\pm 2\alpha$
  with interference fringes through the origin. The trapped-ion
  demonstration of non-Gaussian state tomography by these means is
  [FH20]. *Two distinct caveats.* (i) **Formal reconstructibility**
  (the chain provides a unique $\chi \to W$ map for any state) is not
  the same as **numerical resolvability** on a given grid; on the v0.2
  $\Delta\alpha = 0.39$ mesh, Fock $|2\rangle$ sits at the resolution
  stress-test edge (§2) and is therefore a grid probe rather than a
  clean reconstruction benchmark. (ii) State-general analytic validity
  does not imply state-general *experimental* validity — the latter
  requires the ideal-SDF assumptions of this chain, and any departure
  (LD order, pulse duration, native vs. ideal coupling) is a separate
  numerical question (§7#3).
- **Approximation hierarchy.** v0.3 separates the hierarchy into two
  layers. The ideal-SDF inversion assumes instantaneous FH20-style
  $D(\sigma_x\beta_n)$ pulses, a single selected comb tooth, and fixed
  per-pulse $\beta_0$. Finite $N$ enters through the Dirichlet tooth width
  $1/N$ in $\delta/\omega_m$. The native engine bridge is a different
  approximation question: its $C\sigma_-+\mathrm{h.c.}$ coupling expands
  into a carrier rotation plus transverse position-dependent spin
  rotation, not directly into a spin-eigenstate-conditioned
  $D(\sigma_x\beta)$ displacement; see §7#3. [TBD]
  still to document the pulse-duration order ($\delta t/T_m$) and the
  exact bridge residual metric.
- **Measurement back-action (ideal SDF).** The same ideal-SDF chain
  gives the unconditional post-train motional state
  $\rho_m^{(\mathrm{post})} = \tfrac{1}{2}\bigl(D(\beta_\text{tot}/2)\,\rho_m\,D^\dagger(\beta_\text{tot}/2) + D(-\beta_\text{tot}/2)\,\rho_m\,D^\dagger(-\beta_\text{tot}/2)\bigr)$
  — measurement-induced decoherence between two displaced branches.
  ($\beta_\text{tot}$ is the branch *separation*; each branch is
  displaced by $\pm\beta_\text{tot}/2$ — the v0.5-corrected σ_x SDF
  convention, `analytic_chain.md` §1. Earlier v0.4 wording used the
  stale full-$\beta_\text{tot}$ form; corrected here in the
  back-action scoping pass for consistency with §8.) Conditioning on
  the SDF-axis spin readout selects one branch
  ($D(\pm\beta_\text{tot}/2)\,|\psi\rangle$); conditioning on an
  orthogonal-equator readout instead produces cat-like superpositions
  via the Kraus operator
  $M_s \propto D(\beta_\text{tot}/2) + s\,e^{i\phi}D(-\beta_\text{tot}/2)$.
  (Under the corrected FH20-style σ_x SDF the branch-selecting axis is
  σ_x and the cat-/χ-producing readout is σ_y/σ_z; the full
  readout-basis treatment is the back-action diagnostic, §8.)
  The native-engine departure from this prediction is the v0.6
  back-action diagnostic (§8;
  [`notes/back_action_scope.md`](./notes/back_action_scope.md)).
- **Background.** Phase-space formalism: Cahill & Glauber [CG69].
  Displaced-parity scheme for direct Wigner measurement (originally
  cavity QED): Lutterbach & Davidovich [LD97]. Trapped-ion
  characteristic-function tomography: Flühmann & Home [FH20].
  Sympathetic-readout phase-space tomography of trapped ions:
  Casanova et al. (PRA 85, 042109, 2012; authors to be verified at
  initiation) [STO12]. Phase-space synthesis and tomography in cQED:
  Hofheinz et al. (Nature 2009) [Hof09]. See §References for
  bibliographic details.

## Numerical

The dataset, validation, and reconstruction pipeline.

- **Engine.** The same `scripts/stroboscopic` package used by WP-V,
  WP-E, and WP-TOM remains the full-physics bridge engine. Its native
  monochromatic pulse is not the ideal FH20-style $\sigma_x$ SDF
  assumed by the analytic inversion; see the §7#3 resolution. The
  ideal σ_x SDF is supplied numerically by the `ideal_sdf` primitive
  (FH20-style bichromatic $U=D(\sigma_x\beta/2)$ added to
  `scripts/stroboscopic`). Therefore the first numerical layer is an
  ideal-SDF / analytic-$\chi$ validation, and the engine comparison
  is a separate bridge test of how far the native Raman train departs
  from that ideal limit.
- **Forward-map regime sweep.** Drive strength
  $\Omega_r \cdot N\delta t \in \{0.01\pi, 0.05\pi, 0.1\pi, 0.25\pi, 0.5\pi, \pi\}$
  at fixed input state ($|\alpha|=1$); compare to the analytic
  $\chi$ prediction. The perturbative regime boundary is wherever the
  residual exceeds ~5 %. v0.3 caveat: the ideal-SDF layer should be
  parameterised directly by $\beta_0$ / $\beta_\text{tot}$; the
  $\Omega_r N\delta t$ sweep belongs to the native-engine bridge after
  $\beta_\text{eff}$ is defined.
- **Reconstruction pipeline.** Three algorithms with shared
  pre-processing:
  1. **Direct FFT** of measured $\chi(\beta)$ → $W(\alpha)$. The scan
     targets Cartesian $\beta$ nodes directly by inverting the central
     Dirichlet lobe, then applies radial windowing and zero-padding
     before the FFT.
  2. **Parametric fit** (for coherent / cat inputs) of a model
     $\chi$-family; recovers $(\alpha, \text{phase}, ...)$ via least
     squares.
  3. **Template-match** (the kick-off Route C), as a regime-overlap
     check — should agree with FFT in the LD regime and degrade
     gracefully as we approach saturation.
- **Test set.** Reconstruct each of the five input classes from
  numerically-generated $(\delta, \varphi_\text{train})$ scans at the
  perturbative-regime drive; quantify reconstruction fidelity
  $\mathcal F(W_\text{rec}, W_\text{true}) = \int W_\text{rec} W_\text{true}\,d^2\alpha$
  and the L¹ error.
- **Manifest.** Output `.h5` files carry a `wp_manifest_v1` envelope
  per [WP-E precedent](../wp-phase-contrast-maps/) and the
  [FAIR Tier 3](../schemas/) schemas.

-----

## 1. Introduction

### 1.1 What WP-W inherits, and from whom

WP-W sits at the intersection of two well-established lineages.

**Trapped-ion phase-space tomography lineage.** Initiated by
Wallentowitz & Vogel [Wal95] (proposal) and first realised
experimentally by Leibfried *et al.* at NIST [LMKMIW96] on ⁹Be⁺ using
displaced-Fock-population reconstruction. Flühmann & Home [FH20]
modernised the trapped-ion implementation with a **direct
characteristic-function readout** via bichromatic SDF + spin-rotation
+ Z-readout, achieving full Wigner-FFT reconstruction of displaced,
squeezed, squeezed-cat, and approximate-GKP states on a single ⁴⁰Ca⁺
ion at $\eta \approx 0.05$. **The χ-FFT chain that WP-W uses is FH20's,
not WP-W's.**

**Hasse-group stroboscopic protocol lineage.** Clos *et al.* [Clos16]
established the $H_\text{TI}$ Hamiltonian form on a trapped-ion engine;
Hasse *et al.* [Hasse24] developed the stroboscopic AC-pulse-train
protocol, demonstrated coherent-displaced-state probing with
$\sim 100$ ns time resolution and $1.8$ nm / $8$ zN·μs position /
momentum noise floors, mapped the back-action $\delta\langle n\rangle$
qualitatively (App. D, Fig. 6b), and outlined a squeezed-state
extension with $\Delta t = 2\pi/(2\omega_m)$ (App. E). **The protocol
WP-W reinterprets is Hasse 2024's, not WP-W's.**

The parallel **cavity-QED** lineage — Lutterbach & Davidovich
[LD97] (displaced-parity proposal), Bertet *et al.* [Bertet02] (first
cQED implementation in the Brune/Haroche photon-box), Hofheinz *et
al.* [Hof09] (superconducting cQED implementation) — informs the
spiritual lineage of "qubit-observable measures phase-space function"
but is not WP-W's direct technical precedent.

### 1.2 The kick-off finding

The kick-off
[wp-analysis-train-tomography](../wp-analysis-train-tomography/)
("WP-TOM v0.x") demonstrated that the $(\delta, \varphi_\text{train})$
heatmap encodes motional-state information amenable to phase-space
inversion (kick-off [logbook §6](../wp-analysis-train-tomography/logbook/2026-05-13-kickoff-expectations-and-run.md)),
and that **template matching** against an engine-precomputed grid
recovers $(|\alpha|, \theta_\alpha)$ for coherent inputs. But template
matching is opaque: it works for the eight states in the table and
generalises only by enlarging the table. It does not tell us *why*
the protocol works, where its regime of validity is, or whether it
extends to non-Gaussian inputs.

### 1.3 What WP-W contributes

Given the prior art, WP-W's contributions narrow to five concrete
points:

1. **Stroboscopic-comb adaptation of [FH20]'s χ-FFT.** [FH20] uses a
   CW bichromatic SDF; [Hasse24] uses a stroboscopic monochromatic
   AC train. The connection between the two — the inverse-Dirichlet
   forward map (§2) that lands the physical $(\delta, \varphi_\text{train})$
   scan on FFT-friendly Cartesian $\beta$ nodes — is WP-W's
   theoretical contribution.
2. **High-$\eta$ regime.** [FH20] operates at $\eta \approx 0.05$;
   [Hasse24] / WP-W at $\eta = 0.40$. LD corrections at
   $\mathcal O(\eta^2) \approx 16\%$ matter; WP-W's
   approximation-hierarchy analysis (§Analytical bullet 5) and the
   ideal-SDF / native-engine bridge (§7#3) address regime issues that
   [FH20]'s perturbative platform sidesteps.
3. **The structural-bridge finding** (§7#3 "no limit recovers the
   ideal SDF"). Specific to monochromatic engines: [FH20]'s
   bichromatic SDF *does* natively realise the ideal chain, but
   [Hasse24]'s monochromatic engine cannot, even at sideband
   resonance under RWA. *To our knowledge this finding has not been
   stated previously in the literature.*
4. **Bridge between WP-TOM saturated template-matching and WP-W
   perturbative FFT** on the same Mg⁺ engine (§7#7).
5. **Numerical-WP discipline**: pre-registered expectations,
   reproducibility manifests, and the conduct conventions of §5a
   applied to a tomography pipeline that has only been published in
   *experimental* form previously.

### 1.4 Hypothesis

In compact form:

> *In the Lamb–Dicke perturbative regime with an idealised
> FH20-style $D(\sigma_x\beta)$ SDF and the spin on the |+y⟩ equator,
> the χ readout $\langle\sigma_y\rangle - i\langle\sigma_z\rangle$
> is — with no prefactor — a direct point-wise measurement of the
> symmetric characteristic function
> $\chi_{\rho_m}(\beta(\delta, \varphi_\text{train}))$
> with $\beta$ given by the Dirichlet kernel of the N-pulse train;
> a 2D FFT then reconstructs $W(\alpha)$ for any input motional
> state.*

The first half (direct χ readout, FFT$\to W$) is **[FH20]'s** result
adapted to our protocol. The Dirichlet-kernel forward map is **WP-W's**
adaptation. The validity of both *under* the [Hasse24] native engine
(not the idealised one) is **the open numerical question**, addressed
by the §4a P0/P1 preflight gates.

### 1.5 Connection to the kick-off

WP-W is the **perturbative** counterpart to the kick-off's
**saturated** template-matching, on the same engine. The cross-
comparison of inversion strategies (§7#7 Layer B) at the shared
anchor $|\alpha=3\rangle$ is one of WP-W's deliverables.

## 2. Notation and nominal parameters

Adopt the
[WP-E §2 conventions](../wp-phase-contrast-maps/README.md) for
$\eta$, $\omega_m$, $\delta t$, $T_m$, ac-phase reference, and
motional-phase $\vartheta_0$. WP-W adds the following idealised-SDF
tomography conventions.

| Symbol | v0.2 value | Meaning |
|---|---:|---|
| $|\beta_0|$ | 0.05 | idealised per-pulse displacement scale |
| $N_\text{rec}$ | 80 | nominal reconstruction train length |
| $B = N_\text{rec}|\beta_0|$ | 4.0 | maximum sampled radius in $\beta$ on the central tooth |
| $\Delta\beta$ | 0.10 | target Cartesian $\beta$-grid spacing |
| $\beta$ grid | $81 \times 81$ over $[-4,4]^2$ | FFT working grid; samples with $|\beta|>B$ are taper / zero-fill |
| $\alpha_\text{plot}$ | $|\mathrm{Re}\,\alpha|,|\mathrm{Im}\,\alpha|\leq 3$ | display and fidelity window for the v0.2 demo |
| raw $\Delta\alpha$ | $\simeq \pi/(2B)=0.39$ | true resolution before zero-padding interpolation |
| $\alpha_\text{Nyq}$ | $\simeq \pi/(2\Delta\beta)=15.7$ | alias-free half-width from the $\beta$ spacing |

The numerical reason for $B=4$ is the cat-state stress test. For
$|\alpha_\text{cat}| = 1.5$, the characteristic-function side humps sit
near $|\beta| \simeq 2|\alpha_\text{cat}| = 3$; $B=4$ leaves a modest
margin instead of truncating the humps at their centres. The same grid is
overkill for vacuum, coherent, thermal, and Fock $n \leq 2$ tests, which is
acceptable because a shared grid makes reconstruction errors comparable
across the state set.

The raw $\Delta\alpha \simeq 0.39$ is adequate for the v0.2 headline
features but not generous. Fock $|1\rangle$ and the $|\alpha|=1.5$ cat
fringes are resolved at this scale; Fock $|2\rangle$ has structure close
to the grid resolution and should be treated as a resolution stress test,
not the primary fidelity benchmark.

**Drive scaling rule.** Fixed $\beta_0$ across $|\alpha|$ and $N$ — no
per-$N$ rescaling. This is the change that makes Routes A/B work where the
kick-off failed. Perturbativity is audited per pulse:
$|\beta_0||\alpha| = 0.075$ for the headline
$|\alpha|=1.5$ reconstructions and $0.15$ for the WP-E bridge anchor
$|\alpha|=3$. The latter is a bridge diagnostic, not the default
tomography stress test.

**Dirichlet-to-grid rule.** Reconstruction scans should not begin from a
uniform polar $(\delta,\varphi_\text{train})$ mesh and interpolate
afterwards. Instead, define the desired Cartesian $\beta$ nodes first. For
each node $\beta_\star = r e^{i\theta}$ with $r \leq B$, solve

$$
  r/|\beta_0| = |\mathcal D_{N_\text{rec}}(x)|,\qquad
  x = (\delta-k\omega_m)T_m,
$$

on the monotone branch of the central lobe $0 \leq x \leq 2\pi/N_\text{rec}$,
then set

$$
  \varphi_\text{train}
  = \theta - \arg\beta_0 - \arg\mathcal D_{N_\text{rec}}(x).
$$

This lands the physical scan directly on FFT-friendly Cartesian
$\beta$ nodes and turns polar-vs-Cartesian resampling into a controlled
edge-windowing problem. For $N_\text{rec}=80$, the branch spans only
$|\delta-k\omega_m|/\omega_m \leq 1/80 = 0.0125$ from the selected tooth,
or $\pm 16.25$ kHz around the selected tooth for the Hasse
$\omega_m/(2\pi)=1.300$ MHz reference. Detuning resolution and lock
stability must fit inside that window; the scan step is therefore set by
the inverse map rather than by a coarse uniform detuning grid.

## 3. Purpose and scope

Three motivations, ranked by priority. Each is framed against the
prior art identified in [§1.1](#11-what-wp-w-inherits-and-from-whom)
and elaborated in [`refs/contextual-notes.md`](./refs/contextual-notes.md).

1. **Validate the stroboscopic-comb adaptation of [FH20]'s χ-FFT
   chain on [Hasse24]'s engine** quantitatively. [FH20] demonstrated
   χ-tomography with a CW bichromatic SDF at $\eta \approx 0.05$;
   [Hasse24] demonstrated phase-space probing with stroboscopic
   monochromatic AC pulses at $\eta = 0.40$. Neither work tests the
   bridge between them. WP-W's first task is to establish that the
   FH20 χ-FFT chain, parameterised via the Dirichlet-kernel forward
   map (§2), gives faithful reconstruction in the Hasse engine's
   high-$\eta$ regime — and to pin down the perturbative-regime
   boundary beyond which the chain breaks down.
2. **Demonstrate phase-space reconstruction across a transferable
   state set on the high-$\eta$ Mg⁺ platform.** Reconstruction of
   non-Gaussian states (Fock $|1\rangle$, $|2\rangle$, cat, mixed
   cat) is *capability transfer*, not novelty — [LMKMIW96] showed
   Fock-state reconstruction in 1996 (⁹Be⁺, η ≈ 0.2);
   [FH20] showed cat and approximate-GKP at η = 0.05.
   WP-W's contribution is the *same capability under the [Hasse24]
   engine constraint*, with explicit grid-resolution analysis
   (§7#5) accounting for the larger $\eta$ and the stroboscopic-
   comb structure.
3. **Bridge WP-TOM saturated template-matching to WP-W perturbative
   FFT** on the same Mg⁺ engine, and **bridge to WP-E** at the
   shared anchor $|\alpha=3, \theta_\alpha=0\rangle$. WP-E maps the
   forward observable $(\vartheta_0, \delta) \to (\sigma_z, |C|)$ at
   saturated drive; WP-W maps the inverse $(\delta, \varphi_\text{train})
   \to W(\alpha)$ at perturbative drive. The cross-check validates
   state/phase conventions and the native Raman bridge; it does not
   assert that the WP-E native pulse is the ideal FH20-style
   $D(\sigma_x\beta)$ SDF of the WP-W inversion layer (cf. §7#3).

Out of scope for the v0.4 execution candidate:

- **Lab implementation** (this is a numerical WP).
- **Thermal-state and decoherence sensitivity beyond a single sanity
  check.**
- **Squeezed-state reconstruction.** A follow-up; needs the LD chain
  extended to $\mathcal O(\eta^2)$ and the timing change
  $\Delta t = 2\pi/(2\omega_m)$ already outlined in
  [Hasse24] Appendix E (see §7#4 and §8 v0.5 outlook).
- **GKP-state reconstruction.** Already demonstrated by [FH20] at
  $\eta = 0.05$ in their Fig 4. WP-W's deferral is grid-resolution
  (§7#4), not capability.
- **First characterisation of back-action.** [Hasse24] App. D /
  Fig. 6b qualitatively maps $\delta\langle n\rangle(\varphi, \vartheta_0)$
  for $|\alpha|=3$. WP-W's v0.5 back-action scope (§8) is the
  *quantitative ideal-SDF-vs-native-engine comparison*, not first
  characterisation.

## 4. Deliverables

Each deliverable is a concrete artefact with a generation command, an
output path, and a pass criterion. The P0/P1 layering of §4a is
respected: D1–D3 are ideal-SDF layer (runnable once the runner scripts
are written); D4 is the native-engine bridge (runnable only after the
bridge convention of §7#3 is implemented).

### D1 — Analytical note

**Command:** None — manual composition.

**Output:** `wp-wigner-tomography/notes/analytic_chain.md` (or `.tex`
if equation density exceeds markdown comfort).

**Contents checklist:**
- Closed-form $(\delta, \varphi_\text{train}, N) \to \beta$ map via the
  Dirichlet kernel.
- Direct χ readout $\chi = \langle\sigma_y\rangle - i\langle\sigma_z\rangle$
  (no prefactor, no phase, no conjugation) under the idealised
  FH20-style $\sigma_x$ SDF with |+y⟩-equator preparation.
- LD expansion order at which each step holds: $\mathcal O(\eta)$ for
  the displacement, $\mathcal O(\eta^2)$ for neglected squeezing.
- Finite-$N$ tooth-width correction: $1/N$ scaling in
  $\delta/\omega_m$.
- The *No limit recovers the ideal SDF* result of §7#3: why the native
  Raman engine is structurally different.

**Pass criterion:** The note is self-contained enough that a reader can
re-derive the $\beta$-grid and the inversion formula without opening the
code.

### D2 — Forward-map regime sweep (ideal-SDF reach ladder)

**Script:** `wp-wigner-tomography/numerics/run_reach_ladder.py`

**Command:**
```bash
cd wp-wigner-tomography
python numerics/run_reach_ladder.py \
    --beta0 0.05 \
    --n-values 20 40 60 80 \
    --states vacuum coherent \
    --alpha 1.0 \
    --grid-size 81 \
    --output numerics/reach_ladder_ideal.h5
```

**What it does:** For each $N \in \{20,40,60,80\}$, builds the
Cartesian $\beta$ grid via the inverse-Dirichlet rule of §2, computes
the analytic characteristic function $\chi(\beta)$ for vacuum and
coherent $|\alpha|=1$, and stores the grid coordinates and $\chi$.
The corrected measurement observable is $\chi$ **directly** (per the
§Analytical bullet 2 σ_x-SDF / |+y⟩ readout, no Gaussian prefactor);
the $e^{-|\beta|^2/2}$-weighted quantity
$C(\beta)=e^{-|\beta|^2/2}\chi(\beta)$ is retained in the output only
as a legacy analytic radial-envelope diagnostic for the reach /
tooth-width sub-panel, *not* as the protocol observable.

**Output schema (`reach_ladder_ideal.h5`):**
- `/N_{n}/beta_x` (81,) — Cartesian $\beta$ coordinates
- `/N_{n}/beta_y` (81,)
- `/N_{n}/chi_real`, `/N_{n}/chi_imag` (81, 81) — analytic
  characteristic function
- `/N_{n}/C_real`, `/N_{n}/C_imag` (81, 81) — legacy analytic
  radial-envelope diagnostic ($e^{-|\beta|^2/2}\chi$); not the
  protocol observable (see "What it does")
- Attributes: `beta0`, `n_pulses`, `grid_size`, `state`, `alpha`,
  `code_version`

**Sidecar manifest:** `numerics/reach_ladder_ideal.manifest.json` per
`schemas/wp_manifest_v1.schema.json`.

**Plot script:** `wp-wigner-tomography/plots/plot_reach_ladder.py`
```bash
python plots/plot_reach_ladder.py \
    --input numerics/reach_ladder_ideal.h5 \
    --output plots/reach_ladder_residuals.png
```

**Plot output:** `plots/reach_ladder_residuals.png` — four-panel figure
showing $|C(\beta)|$ on the $\beta$ grid for $N=20,40,60,80$, with a
sub-panel of tooth-width HWHM vs. $1/N$.

**Pass criterion:** The $N=80$ grid covers the disk $|\beta|\leq 4$ with
no branch-wrap artefacts, and the HWHM scales as $1/N$ to within 10%.

**Native-engine extension (P1, optional):** The `ideal_sdf` primitive
(FH20-style σ_x SDF) is now in `scripts/stroboscopic`; the engine-side
χ is read out directly as $\langle\sigma_y\rangle - i\langle\sigma_z\rangle$.
The residual heatmap is the canonical bridge metric
$|\chi_\text{engine} - \chi_\text{analytic}|/|\chi_\text{analytic}|$
(engine χ vs analytic χ on the β grid — *not* a centroid or
prefactored-contrast residual; see the
[2026-05-15 D4-bridge logbook](./logbook/2026-05-15-D4-bridge.md) §3.3).

### D3 — Wigner reconstruction demo

**Script:** `wp-wigner-tomography/numerics/run_reconstruction_demo.py`

**Command:**
```bash
cd wp-wigner-tomography
python numerics/run_reconstruction_demo.py \
    --beta0 0.05 \
    --n-pulses 80 \
    --grid-size 81 \
    --states vacuum coherent_1.5 thermal_0.5 fock_1 fock_2 cat_1.5 mixed_cat_1.5 \
    --output numerics/reconstruction_demo.h5
```

**What it does:** For each state in the test set:
1. Populates the v0.2 Cartesian $\beta$ grid ($81\times81$, $B=4$).
2. Computes analytic $\chi(\beta)$.
3. Applies radial Hanning window and zero-pads to $161\times161$.
4. 2D FFT $\to W_\text{rec}(\alpha)$.
5. Computes analytic $W_\text{true}(\alpha)$ on the same $\alpha$ grid.
6. Computes overlap fidelity $\mathcal F$, $L^1$ error, and negativity
   ratio $\rho_\text{neg}$ per §7#5.

**Output schema (`reconstruction_demo.h5`):**
- `/{state}/W_rec` (161, 161) float64 — reconstructed Wigner
- `/{state}/W_true` (161, 161) float64 — analytic Wigner
- `/{state}/chi_real`, `/{state}/chi_imag` (81, 81) — characteristic
  function on $\beta$ grid
- `/{state}/metrics` — structured array with fields `fidelity`,
  `L1_error`, `neg_ratio`
- `/alpha_x`, `/alpha_y` (161,) — reconstructed $\alpha$ coordinates
- `/beta_x`, `/beta_y` (81,) — $\beta$ coordinates

**Sidecar manifest:** `numerics/reconstruction_demo.manifest.json`.

**Plot script:** `wp-wigner-tomography/plots/plot_reconstruction_demo.py`
```bash
python plots/plot_reconstruction_demo.py \
    --input numerics/reconstruction_demo.h5 \
    --output plots/reconstruction_demo.png
```

**Plot output:** `plots/reconstruction_demo.png` — multi-panel figure:
- Top row: $W_\text{true}$ for each state.
- Middle row: $W_\text{rec}$ for each state.
- Bottom row: $L^1$ error map
  $\Delta(\alpha)=|W_\text{rec}-W_\text{true}|$.
- Right margin: summary table with $\mathcal F$, $L^1$,
  $\rho_\text{neg}$.

**Pass criterion:** All headline states meet their §7#5 thresholds;
deciding states (Fock $|2\rangle$, cat) trigger the diagnostic flow if
they miss.

### D4 — WP-E / WP-TOM bridge plot

**Panel A — Native Raman convention check**

**Script:** `wp-wigner-tomography/numerics/run_bridge_native.py`

**Command:**
```bash
cd wp-wigner-tomography
python numerics/run_bridge_native.py \
    --alpha 3.0 --alpha-phase-deg 0.0 \
    --output numerics/bridge_native.json
```

The engine parameters are pinned inside the runner to the WP-E
reference scan `wp-phase-contrast-maps/numerics/scan_2d_alpha3_v2.h5`
($\omega_m/2\pi=1.3$ MHz, $\eta=0.397$, $\Omega_r=0.0902$,
$\delta t = 0.13\,T_m$, $N=30$, $n_\text{max}=60$) and are not CLI
arguments — the bridge is a provenance check against that specific
artefact, so the runner does not expose them as knobs.

**Spec-deviation note (Correction 3, v0.5).** The v0.4 §4 D4 wording
read $N=22$, $\delta t = 40$ ns (the Hasse-paper numbers). The WP-E
reference scan at the shared $|\alpha=3,\theta_\alpha=0\rangle$ anchor
is at $N=30$, $\delta t = 0.13\,T_m \approx 100$ ns. Layer A runs at
$N=30$ to match WP-E directly; the bridge is meaningful at any $N$ as
long as both legs agree (resolution chosen per the
[2026-05-15 D4-bridge logbook](./logbook/2026-05-15-D4-bridge.md) §4
Correction 3). $N=22$ remains the Hasse-paper number, quoted for
context only.

**Native-engine convention (Corrections 4 & 5, v0.5).** The runner
reproduces WP-E `run_2d_alpha3_v2.py` exactly:

- **No separate MW π/2 pulse.** The initial spin is $|{\downarrow}\rangle$
  via `prepare_state(theta_deg=0, phi_deg=0)`; the train itself
  accumulates the π/2 spin rotation through the $\Omega_r$
  calibration ($\Omega_\text{eff} = \pi/(2N\delta t)$). The v0.4
  description implying a $|{\downarrow}\rangle \to \text{MW }\pi/2 \to \text{train}$
  preparation is **incorrect** and is removed: it is
  $|{\downarrow}\rangle \to \text{train}$. (The first Layer A attempt
  applied `apply_mw_pi2` and produced ≈ 1.3 residuals; removing it
  was the fix.)
- **Pulse-centering motional-phase shift.** The prepared motional
  phase is $\varphi_\alpha + \texttt{shift\_deg}$ with
  $\texttt{shift\_deg} = \omega_m\,\delta t/2$ (WP-E v0.9.1
  pulse-centering convention, so pulse #1 is centered on $\varphi_\alpha$).
  Omitting this shift was the other half of the ≈ 1.3-residual
  failure.
- Train flags `intra_pulse_motion=True`,
  `gap_includes_spin_detuning=True`, `t_sep_factor=1.0`,
  `ac_phase_rad=0.0` — matched to WP-E.

The `convention_alignment` block in `bridge_native.json` records all
of the above explicitly, per the session guardrail "log any
MW-π/2 / contrast-convention alignment before declaring Layer A pass."

**What it does:** Runs the native `scripts/stroboscopic` engine at the
WP-E-matched parameters for coherent $|\alpha=3,\theta_\alpha=0\rangle$
and extracts $(\sigma_z, \mathrm{Re}\,C, \mathrm{Im}\,C)$ — where
$\mathrm{Re}\,C \equiv \langle\sigma_x\rangle$,
$\mathrm{Im}\,C \equiv \langle\sigma_y\rangle$ for the *native*-engine
readout (this is the native-engine spin-contrast convention, distinct
from the ideal-SDF χ readout of §Analytical bullet 2) — at two sets of
detunings: (i) the three WP-E nearest-grid points
$\delta/\omega_m \in \{-0.9923, 0, +0.9923\}$ (**gated**, since the WP-E
grid step 0.023 has no exact-tooth points — labelled "nearest-grid"
per the guardrail against silent interpolation), and (ii) the exact
tooth centres $\delta/\omega_m\in\{-1,0,+1\}$ (diagnostic, no
reference). Compares (i) against the WP-E `scan_2d_alpha3_v2.h5`
values at the same grid points.

**Output:** `numerics/bridge_native.json` — JSON with
`comparison_1_nearest_grid`, `comparison_2_exact_tooth_centres`,
`convention_alignment`, and per-point `residuals`.

**Pass criterion (Layer A):** max residual $< 10^{-3}$ on
$(\sigma_z, \mathrm{Re}\,C, \mathrm{Im}\,C)$ across the three
nearest-grid points (engine-consistency / provenance check).
*Executed 2026-05-15: PASS at 0.00e+00 (bit-exact).*

**Panel B — Inversion bridge**

**Script:** `wp-wigner-tomography/numerics/run_bridge_inversion.py`

**Command:**
```bash
python numerics/run_bridge_inversion.py \
    --alpha 3.0 --alpha-phase-deg 0.0 \
    --beta0 0.05 --N-coarse 20 --N-fine 80 \
    --grid-coarse 41 --grid-fine 81 \
    --output numerics/bridge_inversion.h5
```

**What it does:** Re-runs the WP-W reconstruction pipeline with
*engine-measured* χ (the FH20-style `ideal_sdf` primitive) instead of
analytic χ, at the shared $|\alpha=3,\theta_\alpha=0\rangle$ anchor.
For each β-node the §2 inverse-Dirichlet rule sets
$(\delta, \varphi_\text{train})$, the ideal-SDF train evolves
$|{+}y\rangle|\alpha=3\rangle$, and the **direct χ readout**
$\langle\sigma_y\rangle - i\langle\sigma_z\rangle$ is recorded (no
prefactor, per the corrected §Analytical bullet 2). Two passes:
coarse ($41^2 \times N=20$) and fine ($81^2 \times N=80$, the §2
reconstruction configuration). 2D-FFT → $W_\text{rec}$, centroid
$\hat\alpha$ extracted.
- WP-W side: engine χ vs analytic χ residual on the β grid, plus the
  FFT centroid $\hat\alpha^W$.
- WP-TOM side: saturated template-match self-recovery of
  $(|\alpha|,\theta_\alpha)$ — trivially exact because the template
  bank in `wp-analysis-train-tomography/data/templates_sz_v1.npz`
  covers $(\alpha{=}3,\theta{=}0)$ on its native grid; reported as
  $\hat\alpha^\text{TOM}=3{+}0i$ for the figure annotation.

**Output:** `numerics/bridge_inversion.h5` (HDF5 with `coarse`,
`fine`, `wp_tom` groups + `wp_manifest_v1` sidecar) — engine χ,
analytic χ, $W_\text{rec}$, centroids, and residuals per pass.

**Plot script:** `wp-wigner-tomography/plots/plot_bridge.py`
```bash
python plots/plot_bridge.py \
    --layer-a numerics/bridge_native.json \
    --layer-b numerics/bridge_inversion.h5 \
    --output plots/bridge.png
```

**Plot output:** `plots/bridge.png` — two-panel figure:
- Left: Layer A bar pairs (engine vs WP-E reference) for
  $\sigma_z$, $\mathrm{Re}\,C$, $\mathrm{Im}\,C$ at the three
  nearest-grid $\delta/\omega_m$ points, with residual annotations.
- Right: Layer B $W_\text{rec}(\alpha)$ heatmap with ground-truth
  $\alpha=3$ (★), $\hat\alpha^{W,\text{fine}}$ (✕),
  $\hat\alpha^{W,\text{coarse}}$ (○), and $\hat\alpha^\text{TOM}$ (+).

**Pass criterion (Layer B).** The **canonical bridge metric is the
engine-χ vs analytic-χ residual on the β grid**, not the FFT centroid
error (the centroid is grid-resolution-limited: at the $81^2$ fine
grid $\Delta\alpha = 0.39$, so a $\sim 10^{-2}$ centroid residual is
sub-pixel and not engine-relevant — see the
[2026-05-15 D4-bridge logbook](./logbook/2026-05-15-D4-bridge.md)
§3.3):

1. $\max|\chi_\text{engine}-\chi_\text{analytic}| \leq 10^{-3}$ on the
   fine ($81^2 \times N=80$) grid.
2. FFT centroid $\hat\alpha^W$ within one $\Delta\alpha$ pixel of
   $\alpha_\text{truth}$ (reported with $\Delta\alpha$ annotated;
   sub-pixel = pass).

The coarse pass is a saturated-regime stress diagnostic (at $N=20$ the
inverse-Dirichlet central monotone branch covers only
$|\beta|\leq N\beta_0=1$, so outer nodes leave the branch); it is not
gated. A future centroid-stability check should vary only the β-grid
resolution at fixed $N$, not $N$. *Executed 2026-05-15: criterion 1
PASS at $3.75\times10^{-4}$ (6481 fine-grid nodes); criterion 2 PASS,
$\hat\alpha^W = 2.980+0i$ (1.99×10⁻², 5% of one Δα pixel).*

### D5 — Logbook

**Command:** None — process deliverable.

**Format:** One dated markdown file per substantive run or decision,
stored in `wp-wigner-tomography/logbook/YYYY-MM-DD-{topic}.md`.

**Required sections:**
1. Pre-registered expectations (before running any D2–D4 script).
2. Actual observations (copy of script stdout and metric values).
3. Comparison table (expectation vs. observation vs. flag).
4. Next-step decision.

**First entry (executed):** `logbook/2026-05-15-D2-and-P0.md` —
records the P0 preflight outcome and the decision to proceed to D2–D3.
Subsequent entries: `2026-05-15-D3-reconstruction.md`,
`2026-05-15-ideal-sdf-primitive.md`, `2026-05-15-D4-bridge.md`.

## 4a. Preflight gate (gates the main sweep)

Before the D2 reach ladder or D3 reconstruction demo, run a single
targeted preflight. Gate condition: the preflight must either
pass, or fail with an identified departure from the idealised chain.

The v0.3 SDF-chain resolution makes this a two-layer gate: P0 validates
the ideal inversion grid, while P1 validates any chosen native-engine
bridge. P0 is required before the reconstruction demo; P1 is required
only before claims about the current Raman engine.

**Protocol.** At the v0.2 nominal $|\beta_0|=0.05$, run one
central-lobe target point,
$\beta_\star = 0.5\,e^{i\pi/4}$, for two input states: vacuum and
coherent $|\alpha=1\rangle$. Use the inverse-Dirichlet rule of §2 to
choose $(\delta,\varphi_\text{train})$ for $N=20$ and $N=80$.

**Comparators.**

1. Analytic prediction: $\chi_{\rho_m}(\beta_\star)$ **directly** —
   the FH20-style σ_x SDF on the |+y⟩ equator reads χ with no
   Gaussian prefactor (corrected §Analytical bullet 2; the v0.4
   $C_\text{ideal}=e^{-|\beta_\star|^2/2}\chi$ form was the spurious
   prefactor and is removed).
2. P1 only: engine prediction from `scripts/stroboscopic` via the
   FH20-style `ideal_sdf` primitive, χ read out as
   $\langle\sigma_y\rangle - i\langle\sigma_z\rangle$.
3. Reconstruction sanity check: insert the analytic $\chi$ values on the
   v0.2 grid for a coherent state and verify the FFT peak lands at the
   prepared $\alpha$ within one raw $\Delta\alpha$ cell.

**Pass criteria.**

- P0 analytic-grid self-consistency: coherent-state peak position within
  one raw $\Delta\alpha$ cell and no sign flip in the phase convention.
- P1 engine-vs-analytic single point: complex residual
  $|\chi_\text{engine}-\chi_\text{analytic}|/|\chi_\text{analytic}| < 5\%$
  at $N=20$. The $N=80$ comparison is diagnostic, not gating, because
  finite tooth width and non-ideal coupling can accumulate visibly over
  the longer train. *Executed 2026-05-15: PASS at $10^{-14}$ (vacuum
  and coherent $|\alpha=1\rangle$, both $N\in\{20,80\}$).*

**Failure classification.** If the gate fails, classify the cause before
launching the sweep: (i) FH20-style $\sigma_x$ ideal SDF vs. engine
$C\sigma_-+\mathrm{h.c.}$ coupling; (ii) finite pulse duration /
intra-pulse motion; (iii) leakage to carrier or neighbouring sidebands;
(iv) phase-convention or Dirichlet-branch mismatch. A class-(i) residual
belongs to the native-engine bridge layer and does not invalidate the P0
inversion grid.

**v0.3 split.** Operationally:

1. **P0 analytic-grid gate** — runnable immediately. Populate the v0.2
   Cartesian $\beta$ grid from known analytic $\chi(\beta)$ for vacuum
   and a coherent state, then verify FFT phase, centring, and scaling.
2. **P1 engine-bridge gate** — runnable only after the bridge convention
   below is implemented. Either add an ideal-SDF sequence to the
   numerical package, or fit an effective $\beta_\text{eff}$ for the
   native Raman train from sentinel vacuum / coherent points and compare
   that fitted bridge against the analytic prediction.

## 5. Folder layout

Final layout, aligned with WP-E precedent and the deliverable commands
of §4.

```
wp-wigner-tomography/
  WORK-PROGRAM.md              # this document
  README.md                    # short pointer (added at initiation)
  numerics/                    # scan drivers, .h5 outputs, sidecar manifests
    _common.py
    run_reach_ladder.py
    run_p0_preflight.py
    run_reconstruction_demo.py
    run_p1_preflight.py
    run_bridge_native.py
    run_bridge_inversion.py
    reach_ladder_ideal.h5 / .manifest.json
    p0_preflight.h5 / .manifest.json
    reconstruction_demo.h5 / .manifest.json
    p1_preflight.h5 / .manifest.json
    bridge_native.json
    bridge_inversion.h5 / .manifest.json
  plots/                       # publication-quality figures
    plot_reach_ladder.py
    plot_p0_preflight.py
    plot_reconstruction_demo.py
    plot_bridge.py
    reach_ladder_residuals.png
    p0_preflight.png
    reconstruction_demo.png
    bridge.png
  logbook/                     # dated entries with pre-registered expectations
    2026-05-15-D2-and-P0.md
    2026-05-15-D3-reconstruction.md
    2026-05-15-ideal-sdf-primitive.md
    2026-05-15-D4-bridge.md
  notes/                       # analytical derivations
    analytic_chain.md
  refs/                        # primary literature + extractions (see §5a)
    extractions/
    contextual-notes.md
```

## 5a. Conduct and FAIR conventions

WP-W execution follows the project's existing conventions; this
section codifies them so initiation does not have to re-derive
practice from precedent.

**FAIR-aligned data and provenance.**

- Every numerical artefact (`.h5`, `.json`) carries a sidecar manifest
  per [`schemas/wp_manifest_v1.schema.json`](../schemas/) — FAIR Tier 3.
  Manifest fields: code version (git SHA), command line, input
  parameters, output dataset names, dependencies, timestamps.
- Reproducibility test: any §4 deliverable must be re-runnable from
  its manifest plus the repo at the recorded SHA, with byte-for-byte
  identical primary outputs.
- Filenames carry the WP, version, and content (e.g.
  `reach_ladder_ideal.h5` / `.manifest.json`) — no implicit shared
  state between scripts.

**Three-lens framing.**

- Every WP iteration is structured around the Experiment / Analytical
  / Numerical lenses (matching the WP-E precedent and this document's
  own three-pillar lead). Each lens names its own assumptions and
  diagnostics so the reader can read any one in isolation.

**Logbook discipline (anchors §4 D5).**

- One dated markdown file per substantive run or decision, in
  `logbook/YYYY-MM-DD-{topic}.md`.
- **Pre-register expectations *before* running.** State each
  prediction with a quantitative target (a number, a sign, a feature
  scale) and a flag column for the comparison pass. Anchor pattern is
  the WP-TOM kick-off [logbook §2](../wp-analysis-train-tomography/logbook/2026-05-13-kickoff-expectations-and-run.md#2-pre-registered-expectations).
- **Compare against expectations with explicit flags** (✓ matches,
  ✗ deviates, ? ambiguous) and concrete numerical values. Phrases
  like "agrees within reason" are not acceptable; quote the residual.
- **Name surprises.** Any deviation from the pre-registered prediction
  is the most valuable signal — flag it prominently, classify it
  (engine bug, convention error, real physics), and propose the
  diagnostic next step.

**Tutorial notebooks (visitor onboarding).**

- Each substantive numerical capability — new engine primitive, new
  inversion algorithm, new diagnostic — pairs with a tutorial
  notebook in the WP's `notebooks/` directory.
- Tutorial pattern: §0 Setup; §1 Concept; §2 Code; §3 Results;
  §4 Tie-back to the WP claim. Matches the
  [`notebooks/00_tutorial_pulse_train.ipynb`](../notebooks/00_tutorial_pulse_train.ipynb)
  precedent.
- Commit both source and executed copies (`.ipynb` and
  `.executed.ipynb`) so reviewers can see outputs without running.

**Reference discipline (the §References habit).**

The §References list at the end of this document is the minimum
*citation* layer. The deeper layer — primary text, extraction,
contextual note — is captured in `refs/`:

- **Primary texts** as PDFs in `refs/` (per
  [`refs/Hasse2024_PRA_109_053105.pdf`](../refs/Hasse2024_PRA_109_053105.pdf)),
  one per cited work.
- **Extractions** in `refs/extractions/` — per-paper markdown notes
  capturing key equations, definitions, and sign conventions in
  derived form, so the WP doesn't have to re-derive them at use
  sites. Goal: a reader can re-derive the analytic chain from the
  extraction without opening the PDF.
- **Contextual notes** in `refs/contextual-notes.md` (or per-topic
  files): the lineage — what each cited work contributes, how it
  relates to the protocol, what's adopted vs. what's a contrast. This
  is the layer that turns a flat bibliography into a foundation.

  For WP-W's v0.4 citations: each of [CG69], [LD97], [FH20], [STO12],
  [Hof09] should accrue an extraction + a contextual paragraph during
  D1 (analytical note) drafting. The bibliography in §References
  remains the index; the extractions are the working knowledge.

**[TBD] Pointers needed from user.** Two named conventions were
referenced in the v0.4-polish review but I could not locate them in
the repository:

- "*Harbor principles*" — please link the document, or indicate the
  scope (overarching project ethic? new convention to introduce
  alongside the Breakwater Dossier metaphor?).
- "*DG reports*" — please link the template or define the acronym
  (Design-Gate? Diagnostic-Group? Dispatch?) and whether DG reports
  are part of WP-W's deliverable surface or a separate channel.

These are flagged here so WP-W's conduct conventions are explicit
about what is *not yet* anchored; the section is otherwise a
self-contained codification of the repo's existing practice.

## 6. Connection to other WPs

| WP | Relation |
|---|---|
| [WP-V (Hasse reproduction)](../wp-hasse-reproduction/) | uses the same engine; WP-V validates the engine itself, WP-W validates a protocol *built on* the engine. |
| [WP-E (Phase-contrast maps)](../wp-phase-contrast-maps/) | mirror image: WP-E is the forward observable at saturation; WP-W is the inverse at perturbation. §3 bullet 3 articulates the bridge. |
| [WP-TOM kickoff](../wp-analysis-train-tomography/) | direct predecessor; supplies the saturated-regime baseline that WP-W is the perturbative counterpart to. |

Naming policy resolved in §7#6 — WP-W is formal; single-letter and
codename designators coexist in the repo with no letter-sequence
reconciliation required.

## 7. Tightening roadmap — what to settle before initiation

Open questions, in the order I'd attack them. Each is a clarifying
decision the user (or a council) needs to weigh in on before this
WP becomes execution-ready.

1. **Drive scale (§2 / §3).** *Resolved for v0.2:* use
   $|\beta_0|=0.05$ and $N_\text{rec}=80$ for the reconstruction grid,
   giving $B=4.0$. Retain $N\in\{20,40,60,80\}$ as a reach / tooth-width
   ladder: $B=\{1,2,3,4\}$. Perturbativity is per-pulse, so the relevant
   audit number is $|\beta_0||\alpha|$ rather than $N|\beta_0||\alpha|$.
2. **Phase-space grid (§Numerical).** *Resolved for v0.2:* target a
   Cartesian $\beta$ grid directly by inverse Dirichlet mapping. Use an
   $81\times81$ working grid over $[-4,4]^2$ with $\Delta\beta=0.10$,
   sample the disk $|\beta|\leq4$, radially taper the edge, zero-fill
   outside the accessible disk, and FFT the windowed grid.
3. **SDF coupling — $\sigma_z$ vs. $\sigma_x$.** *Resolved: the ideal
   is FH20-style $\sigma_x$ (v0.5 Correction 1); structural-bridge
   finding stands.* The current monochromatic engine does **not**
   natively realise the ideal WP-W measurement operator. The ideal
   chain assumes the FH20-style bichromatic σ_x SDF
   $U_\text{SDF}(\beta)=D(\sigma_x\beta/2)$ (branch separation
   $\beta$); on the $|{+}y\rangle$ equator the orthogonal spin
   observables read χ directly,
   $\chi=\langle\sigma_y\rangle-i\langle\sigma_z\rangle$ (corrected
   §Analytical bullet 2). The earlier v0.3/v0.4 wording took the ideal
   as $D(\sigma_z\beta)$; that is corrected to $\sigma_x$ here — σ_z
   conditioning does not rotate under the σ_z spin precession that
   generates the §2 Dirichlet kernel, whereas σ_x does (P1 sentinel:
   σ_x gives $10^{-14}$ agreement, σ_z gives 165% residual; see the
   [2026-05-15 ideal-SDF logbook](./logbook/2026-05-15-ideal-sdf-primitive.md)
   §3.2–3.3). The engine implements

   $$
   H_\text{eng}
   = \frac{\delta}{2}\sigma_z
     + \frac{\Omega_r}{2}
       \left(e^{i\varphi}C\sigma_-+
             e^{-i\varphi}C^\dagger\sigma_+\right),
   \qquad
   C=e^{i\eta X},\quad X=a+a^\dagger .
   $$

   Since $C$ commutes with spin, the coupling term is equivalently

   $$
   \frac{\Omega_r}{2}\left[
     \cos(\varphi+\eta X)\,\sigma_x
     + \sin(\varphi+\eta X)\,\sigma_y
   \right].
   $$

   Its LD expansion is

   $$
   \frac{\Omega_r}{2}\left[
     \sigma_\varphi
     + \eta X\,\sigma_{\varphi+\pi/2}
     - \frac{\eta^2X^2}{2}\sigma_\varphi
     + \mathcal O(\eta^3)
   \right],
   $$

   where $\sigma_\varphi=\cos\varphi\,\sigma_x+\sin\varphi\,\sigma_y$.
   Thus the leading engine term is a carrier rotation about an equatorial
   spin axis, and the leading motional term is a transverse
   position-dependent spin rotation. That is not the same operator as a
   spin-eigenstate-conditioned displacement of the motion (neither the
   FH20-style σ_x-conditioned $D(\sigma_x\beta/2)$ nor a σ_z-conditioned
   one).

   **No limit of the monochromatic engine recovers the ideal SDF.**
   At sideband resonance $\delta = +\omega_m$ — the WP-W operating
   point — the leading non-trivial term $\eta X\,\sigma_{\varphi+\pi/2}$
   becomes, under the rotating-wave approximation, a Jaynes–Cummings
   coupling $(\eta\Omega_r/2)\!\left(a\,\sigma_{\varphi+\pi/2}^- + a^\dagger\,\sigma_{\varphi+\pi/2}^+\right)$.
   That is still **transverse** (spin-flip plus phonon-flip), not a
   spin-eigenstate-conditioned displacement. N-pulse comb
   sharpening selects this term but does not transform it into the
   ideal SDF; the bridge between the monochromatic Hasse engine and
   the FH20-style $D(\sigma_x\beta/2)$ SDF is *structural*, not a
   regime limit.

   *Scope of this finding.* A **bichromatic** SDF (simultaneous red
   and blue sideband drive) gives a *different* leading operator —
   the standard Mølmer–Sørensen-style spin-eigenstate-conditioned
   displacement — which [FH20] demonstrates *natively realises* the
   ideal-SDF chain on Ca⁺ at $\eta = 0.05$. The structural-bridge
   issue is therefore specific to the **monochromatic-engine**
   constraint inherited from [Hasse24], not a universal trapped-ion
   tomography limitation. The `ideal_sdf` primitive (FH20-style
   bichromatic $U=D(\sigma_x\beta/2)$) is now implemented in
   `scripts/stroboscopic` and sidesteps this issue numerically for
   the ideal-SDF layer of §4a (P1 sentinel passes at $10^{-14}$;
   D4 engine-χ bridge at $3.75\times10^{-4}$).

   Consequence: there is no standalone §2 conversion
   $\Omega_r\delta t \mapsto |\beta_0|$ for the native engine until a
   bridge convention is chosen. The v0.3 policy is to keep two numerical
   layers distinct:

   - **Ideal-SDF layer:** validate the inversion with analytic χ or the
     FH20-style $D(\sigma_x\beta/2)$ `ideal_sdf` primitive. This is the
     clean WP-W tomography claim.
   - **Native-engine bridge:** treat `scripts/stroboscopic` as a
     full-Raman departure from the ideal SDF. Compare it only after
     fitting or deriving an effective $\beta_\text{eff}$ on sentinel
     states; the residual is then a diagnostic, not a failure of the
     inversion grid.
4. **Test states.** *Resolved for v0.4-accum:* keep the five-class
   headline set as the §7#5 gating bench, add **mixed cat** as a
   sixth diagnostic state, and explicitly defer the other two
   candidates with reasons.

   **Headline set** (gating per §7#5 thresholds):
   vacuum / Fock $|0\rangle$; coherent $|\alpha|=1.5$;
   thermal $\bar n=0.5$; Fock $|1\rangle$; Fock $|2\rangle$;
   pure cat $(|\alpha\rangle + |\!{-}\alpha\rangle)/\mathcal N$ at $|\alpha|=1.5$.

   **Diagnostic addition — mixed cat.**
   $\rho_\text{mc} = \tfrac{1}{2}\bigl(|\alpha\rangle\langle\alpha| + |\!{-}\alpha\rangle\langle{-}\alpha|\bigr)$
   at $|\alpha|=1.5$: an *incoherent* two-hump Gaussian mixture with
   no fringes and no Wigner negativity. Reconstructing the pure cat
   *and* the mixed cat together is the protocol's quantum-vs-classical
   discriminator — invented fringes on the mixed cat would expose an
   inversion artefact masquerading as quantum coherence. Reported
   alongside the pure cat in §4 deliverable 3; not gating per §7#5,
   but a published diagnostic. Cost is essentially zero given the
   pure-cat infrastructure.

   **Deferred to v0.5+: squeezed vacuum.** A squeezed state's
   characteristic function $\chi_{|r\rangle}(\beta)$ carries
   phase-dependent quadratic structure that is not captured by the
   first-order LD chain anchoring §7#3. Adding it requires extending
   the analytic chain to $\mathcal O(\eta^2)$ and re-auditing the
   ideal-SDF bridge. **Framework precedent**: [Hasse24] Appendix E
   outlines the squeezed-state extension of the monochromatic
   stroboscopic protocol with the critical timing change
   $\Delta t = 2\pi/(2\omega_m)$ (half the displaced-state cycle period —
   the train syncs to the quadrature dynamics, which evolve at
   $2\omega_m$). [FH20] demonstrates experimental squeezed-state
   reconstruction at $\eta = 0.05$. The v0.5 WP-W scope adapts these
   to the high-$\eta$ stroboscopic regime. Concrete v0.5 scope item,
   not a v0.4 blocker.

   **Deferred to a follow-up WP: GKP-lattice probe.** [FH20] Fig 4
   *already demonstrates* approximate-GKP reconstruction at $\eta = 0.05$
   on Ca⁺ — so this is a *grid-resolution* deferral, not a *capability*
   deferral. GKP states have structured phase-space negativity on the
   lattice scale $\sqrt{\pi/2}$, with sub-feature width well below the
   v0.2 raw $\Delta\alpha = 0.39$. A faithful GKP reconstruction in the
   [Hasse24] high-$\eta$ regime needs $\Delta\alpha$ down by an order
   of magnitude, which cascades into $\Delta\beta$ down by 10×, $N$ up
   by 10×, and the perturbativity audit $|\beta_0||\alpha|$ revisited
   at the larger $|\alpha|$ that GKP support demands. Out of WP-W's
   v0.4 scaffold; flagged for a future "WP-W-GKP" if the motivation
   crystallises.
5. **Reconstruction fidelity targets.** *Resolved for v0.4-draft:*
   adopt a three-metric bundle and per-state thresholds matched to the
   v0.2 Cartesian grid resolution. Targets apply to the ideal-SDF
   inversion layer (§7#3); the native-engine bridge residual is
   reported as a separate diagnostic per §4a, not a fidelity criterion.

   **Metric bundle** (every reconstruction reports all three):

   - **Overlap fidelity**
     $\mathcal{F} = \pi\!\int W_\text{rec}(\alpha)\,W_\text{true}(\alpha)\,d^2\alpha$.
     For pure $\psi_\text{true}$ this equals
     $\langle\psi_\text{true}|\rho_\text{rec}|\psi_\text{true}\rangle \in [0,1]$.
     For the thermal target this is bounded above by
     $\mathrm{Tr}(\rho_\text{th}^2)=1/(2\bar n+1)$; report both raw
     $\mathcal{F}$ and $\mathcal{F}/\mathrm{Tr}(\rho_\text{th}^2)$.
   - **$L^1$ error map** $\Delta(\alpha)=|W_\text{rec}(\alpha)-W_\text{true}(\alpha)|$
     and its integral $\|\Delta\|_1$. Diagnoses where the error lives
     in phase space (centre, ring, fringes).
   - **Negativity ratio** (non-Gaussian targets only)
     $\rho_\text{neg}=\int\min(0,W_\text{rec})\,d^2\alpha\,/\int\min(0,W_\text{true})\,d^2\alpha$.
     Tests whether the reconstruction preserves the quantum signature.
     Grid-limited reconstructions systematically *under-estimate*
     $|\rho_\text{neg}|$ (Gibbs / edge-windowing overshoot kills the
     dip); they almost never over-estimate it. So the quality marker
     is the lower bound, not a symmetric window.

   **Per-state thresholds** (v0.4 demo, v0.2 grid):

   | state | threshold | rationale |
   |---|---:|---|
   | vacuum                 | $\mathcal F \geq 0.999$ | Gaussian, no structure |
   | coherent $\|\alpha\|=1.5$ | $\mathcal F \geq 0.99$  | off-centre Gaussian |
   | thermal $\bar n=0.5$     | $\mathcal F/\mathrm{Tr}(\rho_\text{th}^2)\geq 0.98$ | broader Gaussian; absolute $\mathcal F\geq 0.49$ |
   | Fock $\|1\rangle$        | $\mathcal F \geq 0.95$  | ring at $\|\alpha\|\!\approx\!1.22$, ~3 $\Delta\alpha$ feature width |
   | Fock $\|2\rangle$        | $\mathcal F \geq 0.90$  | tightest features (~2 $\Delta\alpha$); grid-edge case |
   | cat $\|\alpha\|=1.5$     | $\mathcal F \geq 0.90$  | fringe period $\pi/(2\|\alpha\|)\!\approx\!1.05$, barely resolved |
   | $\rho_\text{neg}$ (Fock, cat) | $\geq 0.5$ | sign preserved; magnitude $\geq 50\%$ of true value (one-sided — see metric bundle) |

   **Aggregate.** Geometric mean of (normalised) $\mathcal F$ across the
   five-state set $\geq 0.95$ for the headline reconstruction claim.
   The geometric mean is a headline convenience; the deciding-state
   criterion is the binding validation.

   **Deciding states.** Fock $|2\rangle$ and the cat. If both pass, the
   inversion pipeline is validated at the chosen Cartesian resolution.
   If either fails, the diagnostic flow is: (i) re-run with
   $\Delta\beta=0.05$ (doubled resolution); (ii) localise whether the
   failure is in analytic $\chi\to$ FFT vs. sampling / windowing;
   (iii) tighten the grid only if (i) recovers threshold, else identify
   the residual physics.

   **Negativity preservation** is reported but not gating in v0.4 —
   it's a quality marker, not a primary success criterion. Promoted to
   gating if a later protocol iteration explicitly targets
   negativity-preserving reconstruction.
6. **Naming.** *Resolved for v0.4:* adopt **WP-W** as the formal
   designator for this work program. The repository's existing WP-naming
   policy is permissive — single-letter designators
   ([WP-V](../wp-hasse-reproduction/), [WP-E](../wp-phase-contrast-maps/),
   WP-W) and codename designators
   ([WP-TOM](../wp-analysis-train-tomography/),
   [WP-Coastline](../wp-strong-weak-coastline/)) coexist — so WP-W
   requires no reconciliation with the letter sequence. The
   [WP-TOM kick-off](../wp-analysis-train-tomography/) retains its
   informal label as a labelled predecessor; it is not promoted to a
   peer WP letter because its scope was explicitly a quick-and-dirty
   intuition check rather than an execution-ready work program.

   Cross-reference update expected during initiation: add a one-line
   pointer to WP-W in [ARCHITECTURE.md](../ARCHITECTURE.md) alongside
   the existing WP-A / WP-B context, mirroring the WP-E pattern from
   its v0.3 §8 logbook entry.
7. **Cross-check with WP-E.** *Resolved for v0.4-accum:* use a
   two-layer bridge contract, with one shared state and two observables.

   **Shared state.** Coherent $|\alpha=3\rangle$ with motional phase
   zero: $\theta_\alpha=0$ in the WP-TOM notation and
   $\varphi_\alpha=0$ / $\vartheta_0=0$ in WP-E notation. This is the
   Hasse / WP-E baseline amplitude, is present in the kick-off template
   grid, and fixes the sign convention: the packet starts on the +X
   quadrature.

   **Layer A — native Raman convention check.** Use the WP-E native
   pulse train, not the ideal-SDF surrogate. Parameters are pinned to
   the WP-E reference scan `scan_2d_alpha3_v2.h5`: $N=30$,
   $\delta t = 0.13\,T_m$, $\eta=0.397$, $\omega_m/(2\pi)=1.300$ MHz,
   $\Omega_r = 0.0902$, pure coherent input, **no separate MW π/2**
   (the train accumulates the π/2 via the $\Omega_r$ calibration; the
   spin starts $|{\downarrow}\rangle$), and the WP-E v0.9.1
   pulse-centering motional-phase shift
   $\texttt{shift\_deg}=\omega_m\,\delta t/2$ (Corrections 3–5, v0.5;
   $N=22$ / $\delta t=40$ ns were the stale Hasse-paper numbers).
   Compare raw $(\sigma_z,\mathrm{Re}\,C,\mathrm{Im}\,C)$ at the three
   WP-E nearest-grid points $\delta/\omega_m\in\{-0.9923,0,+0.9923\}$
   (the WP-E grid has no exact-tooth points; the exact teeth
   $\{-1,0,+1\}$ are reported as an unreferenced diagnostic) against
   the WP-E driver's values at the same grid points. Convention /
   provenance check; should agree to numerical tolerance if both
   wrappers call the same engine.

   **Layer B — inversion bridge.** For the same coherent state, compare
   the saturated WP-TOM template-match recovery of
   $(|\alpha|,\theta_\alpha)$ with the perturbative ideal-SDF FFT
   reconstruction, using *engine-measured* χ from the FH20-style
   `ideal_sdf` primitive. The **canonical bridge metric is the
   engine-χ vs analytic-χ residual** ($\leq 10^{-3}$ on the $81^2$
   fine grid); the FFT centroid is reported with its $\Delta\alpha$
   pixel size annotated (sub-pixel = pass) rather than gated at a
   raw $|\Delta\alpha_\text{centroid}|$ threshold, since the centroid
   is grid-resolution-limited (§4 D4 Layer B; D4-bridge logbook §3.3).
   Because $|\alpha|=3$ sits on the edge of the v0.2 demo display
   window, this bridge plot uses
   $|\mathrm{Re}\,\alpha|,|\mathrm{Im}\,\alpha|\leq4$; the v0.2 $B=4$
   / $\Delta\beta=0.10$ sampling remains unchanged.

   **Interpretation.** Passing Layer A says WP-E, WP-TOM, and WP-W are
   using the same coherent-state phase convention and native Raman
   observable. Passing Layer B says the saturated-template and
   perturbative-FFT inversions identify the same state on their
   overlapping coherent-state domain. Neither layer claims that the
   native Raman pulse has become the ideal FH20-style $D(\sigma_x\beta)$
   SDF; that separation remains the §7#3 bridge policy.

## 8. Status

**v0.1 scaffold (2026-05-13):** structure in place, regime defined,
hypothesis stated, deliverables sketched.

**v0.2 tightening pass (2026-05-13):** §2 drive scale and grid settled
for the first numerical pass: $|\beta_0|=0.05$, $N_\text{rec}=80$,
$B=4.0$, $\Delta\beta=0.10$, inverse-Dirichlet Cartesian targeting, and a
single-point preflight gate added in §4a.

**v0.3 SDF-chain pass (2026-05-13):** §7#3 direction resolved: the
native `scripts/stroboscopic` Raman pulse is not an ideal
spin-eigenstate-conditioned SDF, and no regime limit recovers it — the
bridge is structural. (v0.3/v0.4 took the ideal as $D(\sigma_z\beta)$;
the v0.5 doc pass corrects this to the FH20-style $D(\sigma_x\beta/2)$
— see the v0.5 entry below. The structural finding is unchanged: the
monochromatic engine realises neither.) Even the sideband-resonant LD
term reduces to a Jaynes–Cummings coupling, which remains transverse. WP-W therefore
separates ideal-SDF inversion (clean WP-W tomography claim) from the
native-engine bridge (diagnostic, not gating). At v0.3 close the WP was
not yet execution-ready because the bridge convention itself, §7#4–7,
and concrete §4 deliverable commands remained open.

**v0.4 accumulation (2026-05-13):** §7#5 fidelity targets resolved with
a three-metric bundle and state-specific thresholds. §7#7 bridge anchor
resolved as the shared coherent state $|\alpha=3,\theta_\alpha=0\rangle$,
with a native Raman convention check against WP-E and a separate
saturated-template vs. ideal-SDF FFT inversion comparison. §7#4
test-state scope resolved: five-class headline set kept, mixed cat
added as a quantum-vs-classical diagnostic, squeezed vacuum deferred
to v0.5 (needs $\mathcal O(\eta^2)$ extension), and GKP deferred to a
separate follow-up WP (needs ~10× finer grid). §4 deliverable commands
resolved: D1–D5 each have a concrete script name, CLI invocation,
output path, and pass criterion; §5 folder layout is final.

**v0.4 close (2026-05-13):** §7#6 naming resolved — WP-W adopted as the
formal designator under the repository's permissive WP-naming policy,
which already mixes single-letter (V, E) and codename (TOM, Coastline)
forms. All §7 items now resolved; design surface is closed.

**v0.4 lit-review pass (2026-05-14 / 15):** Path-A literature review
completed per §5a discipline. Eight primary papers extracted to
[`refs/extractions/`](./refs/extractions/) ([Hasse24], [FH20], [LD97],
[CG69], [Wal95], [LMKMIW96], [Bertet02], [STO12]); [Hof09] verified
inline; secondary survey triaged in
[`refs/review-tracker.md`](./refs/review-tracker.md). The
[`refs/contextual-notes.md`](./refs/contextual-notes.md) synthesises
the lineage map and the narrowed contribution scope.

**Major findings from the lit-review:**

1. [Hasse24] is the **direct experimental antecedent** — the
   stroboscopic AC-train protocol, $H_\text{TI}$ Hamiltonian, 2D
   $(\varphi, \vartheta_0)$ scan, back-action concept (App. D, Fig.
   6b), and squeezed-state extension framework (App. E) all originate
   there.
2. [FH20] is the **direct theoretical-and-experimental precedent** for
   χ-FFT tomography in trapped ions — bichromatic SDF on Ca⁺ at
   $\eta \approx 0.05$, full 2D-FFT $\chi \to W$, non-Gaussian states
   including approximate-GKP code state.
3. WP-W's contribution narrows to: stroboscopic-comb adaptation of
   [FH20]'s χ-FFT to [Hasse24]'s monochromatic engine; high-$\eta$
   regime ($0.40$ vs. $0.05$); the §7#3 "no limit recovers ideal SDF"
   finding (specific to monochromatic engines); the WP-TOM bridge;
   the inverse-Dirichlet Cartesian targeting rule (§2).

§References expanded from 6 to 11 entries with verified bibliographic
detail; §1 introduction restructured into 1.1–1.5 (inheritance,
kick-off finding, contributions, hypothesis, kick-off connection);
§3 motivations reframed against the prior art; §7#3 softened to
"no limit *of the monochromatic engine* recovers the ideal SDF"
([FH20]'s bichromatic protocol does); §7#4 deferrals updated to
reference [Hasse24] App. E and [FH20] Fig. 4 GKP precedent; §8
v0.5 back-action reframed as quantitative ideal-vs-native diagnostic
(not first characterisation, which [Hasse24] App. D has done
qualitatively).

**v0.4 execution (2026-05-15).** Runner scripts written and the
preflight + deliverable chain executed in four same-day sessions
(logbook entries [D2/P0](./logbook/2026-05-15-D2-and-P0.md),
[D3](./logbook/2026-05-15-D3-reconstruction.md),
[ideal-SDF + P1](./logbook/2026-05-15-ideal-sdf-primitive.md),
[D4 bridge](./logbook/2026-05-15-D4-bridge.md)). Outcomes: **P0**
PASS (analytic-grid self-consistency); **D2** reach ladder + figure;
**D3** reconstruction PASS on all six gated states (deciding states
Fock $|2\rangle$ and cat clear §7#5); the FH20-style `ideal_sdf`
primitive added to `scripts/stroboscopic` (28 smoke tests, 4
convention locks); **P1** sentinel PASS at $10^{-14}$; **D4**
Layer A PASS at machine precision and Layer B substantive PASS
(engine-χ vs analytic-χ at $3.75\times10^{-4}$ over the $81^2$ fine
grid; FFT centroid sub-pixel).

**v0.5 doc correction pass (2026-05-15).** Five convention
corrections, surfaced by the ideal-SDF + D4 execution, applied to
make this document match the executed artefacts:

1. **σ_z → σ_x (FH20-style ideal SDF).** §Analytical bullet 2,
   §1.4 hypothesis, §Experiment, §Numerical, §3 bullet 3, §D1,
   §4a, §7#3, §8 now state the ideal SDF as the FH20-style
   bichromatic $U=D(\sigma_x\beta/2)$. σ_z conditioning does not
   rotate under the σ_z spin precession that generates the §2
   Dirichlet kernel; σ_x does (P1: σ_x → $10^{-14}$, σ_z → 165%).
2. **Removed spurious $e^{-|\beta|^2/2}$ prefactor.** The ideal-SDF
   χ readout on the |+y⟩ equator is **direct**:
   $\chi=\langle\sigma_y\rangle-i\langle\sigma_z\rangle$, no
   prefactor, phase, or conjugation. The earlier
   $C=\langle\sigma_x\rangle+i\langle\sigma_y\rangle=e^{-|\beta|^2/2}\chi$
   was an artefact conflated with the WP-E Doppler case. §Analytical
   bullet 2, §1.4, §D1, §D2, §4a updated; D2's $e^{-|\beta|^2/2}\chi$
   is relabelled a legacy radial-envelope diagnostic, not the
   observable.
3. **N=22 ↔ 30 stale wording.** §4 D4 Layer A and §7#7 now read
   $N=30$ (matching the WP-E `scan_2d_alpha3_v2.h5` reference);
   $N=22$ noted as the Hasse-paper number for context only.
4. **shift_deg = $\omega_m\delta t/2$ documented.** §4 D4 Layer A
   and §7#7 record the WP-E v0.9.1 pulse-centering motional-phase
   shift explicitly.
5. **Stale MW π/2 step removed.** §4 D4 Layer A now states the
   native engine takes **no separate MW π/2**: spin starts
   $|{\downarrow}\rangle$ and the train accumulates the π/2 via
   the $\Omega_r$ calibration.

Folder layout (§5) and the §4 D4 commands/outputs reconciled to the
executed artefact names (`bridge_inversion.h5`, `bridge.png`,
preflight scripts). This pass is **doc-only**; no code or artefact
changed. D1 (analytical note) remains to be drafted and should
inherit the corrected §Analytical material directly.

**Initiation handoff.** P0 + D1–D3 are ready for execution as soon as
the runner scripts of §4 / §5 are written. P1 + D4 require the
bridge-convention implementation flagged in §7#3 (leading candidate:
`ideal_sdf` primitive in `scripts/stroboscopic`, implementing an
[FH20]-style bichromatic SDF sequence). At initiation, add the WP-W
cross-reference line to [ARCHITECTURE.md](../ARCHITECTURE.md) per §7#6,
and open the first logbook entry per D5.

Outstanding non-blocking polish:

- ~~Background citations in §Analytical~~ — *done in the v0.4-polish
  pass and verified in the v0.4 lit-review pass.* §References has 11
  verified entries; only the [Hof09] / [LBMW03] / [Clos16] DOI
  resolutions to verify at first runner-script commit.
- ~~Conduct and FAIR conventions section~~ — *done in the v0.4-polish
  pass.* §5a codifies the practice. The "harbor principles" / "DG
  reports" placeholders remain pending user pointers.
- Pulse-duration $(\delta t/T_m)$ order in the approximation hierarchy
  (§Analytical bullet 5) — still outstanding.

**Anticipated v0.5 scope** (deferred, not blockers for v0.4 execution):

- **Squeezed-vacuum reconstruction.** Carried over from §7#4. Requires
  extending the analytic chain to $\mathcal O(\eta^2)$ so the
  quadrature-dependent second-order term contributes alongside the
  first-order displacement, and re-auditing the ideal-SDF bridge.
  Test state: ideal squeezed vacuum at moderate squeezing $r \sim 0.5$.

- **Motional back-action of the analysis train.** The WP-W v0.4 design
  characterises the *forward* map $\rho_m \to C(\delta,\varphi_\text{train})$
  and its *inversion* to $W(\alpha)$ — but not the *post-train
  motional state* $\rho_m^{(\mathrm{post})}$. **Framework precedent**:
  [Hasse24] Appendix D / Fig 6b qualitatively maps
  $\delta\langle n\rangle(\varphi, \vartheta_0)$ for $|\alpha|=3$ —
  this *is* a back-action map and demonstrates that back-action
  structure exists in the protocol. **WP-W's v0.5 contribution would
  be the *quantitative* ideal-SDF-vs-native-engine comparison** of
  $\rho_m^{(\mathrm{post})}$ — not first characterisation, which
  [Hasse24] has done qualitatively, but a Wigner-resolved difference
  diagnostic that ties to §7#7's bridge framework.

  - **Ideal-SDF prediction.** Under the FH20-style
    $U_\text{ideal} = D(\sigma_x\beta_\text{tot}/2)$ with initial
    $|+y\rangle$ spin (equator, orthogonal to the σ_x SDF axis), the
    unconditional reduced motional state is the 50/50 mixture
    $$\rho_m^{(\mathrm{post})} = \tfrac{1}{2}\bigl(D(\beta_\text{tot}/2)\,\rho_m\,D^\dagger(\beta_\text{tot}/2) + D(-\beta_\text{tot}/2)\,\rho_m\,D^\dagger(-\beta_\text{tot}/2)\bigr),$$
    a measurement-induced decoherence between the two σ_x-branch
    displacements. The conditional Kraus map *depends on the readout
    basis*: σ_x-axis (SDF-axis) readout selects one displaced branch
    $D(\pm\beta_\text{tot}/2)\,|\psi\rangle$; an orthogonal-equator
    (σ_y/σ_z) readout produces a coherent sum
    $M_s \propto D(\beta_\text{tot}/2) + s\,e^{i\phi}D(-\beta_\text{tot}/2)$
    — the conditioned state is cat-like, not single-branch. The
    readout-basis choice is therefore a v0.5 protocol decision (open
    item below).

  - **Native-engine prediction.** The Raman engine's JC-like coupling
    (§7#3) produces a different back-action structure including
    collapse–revival contributions on coherent inputs. Quantitative
    form follows from the same forward propagator that drives $C$.

  - **Why it matters.** (i) Back-action sets the *cost of measurement*
    — how much motional disturbance per bit of phase-space
    information. (ii) Comparing engine vs. ideal-SDF back-action is a
    third bridge residual, orthogonal to the spin-side §7#7 anchor.
    (iii) Forward-looks to weak-measurement and sequential-tomography
    protocol variants.

  - **Provisional deliverable sketch.** $W$-of-back-action panels:
    side-by-side $W(\rho_m^{(\mathrm{post})})$ for engine vs. ideal-SDF
    prediction on each headline state from §7#4. Single figure per
    state. The Wigner function is computed *directly from the
    simulated density matrix* via
    $W(\alpha) = \tfrac{2}{\pi}\mathrm{Tr}\!\bigl[\rho\,D(\alpha)\Pi D^\dagger(\alpha)\bigr]$
    (parity operator $\Pi$; prefactor $2/\pi$ — corrected from a
    stale $\pi^{-1}$ in the back-action scoping pass, to anchor
    $W_\text{vac}(0)=2/\pi$ consistent with P0 / `analytic_chain.md`
    §4), not via $\chi\to$FFT inversion — so the
    pipeline sidesteps v0.4's grid-resolution limits but raises its
    own implementation question on partial-trace and mixed-state
    Wigner cost. *Resolved and executed in v0.6* (`run_back_action.py`
    via the `_common.wigner_from_rho` / `partial_trace_spin` helpers;
    see the v0.6 entry below and the run logbook).

  - **v0.6 back-action scope (LOCKED 2026-05-16; executed).** The
    open items below are settled in
    [`notes/back_action_scope.md`](./notes/back_action_scope.md)
    (2026-05-16 scoping pass + user review/lock; logbook
    [`2026-05-16-back-action-scope.md`](./logbook/2026-05-16-back-action-scope.md),
    run [`2026-05-16-back-action-run.md`](./logbook/2026-05-16-back-action-run.md)).
    Locked decisions: (1) **readout basis** — compute all three
    (unconditional, σ_x branch-select, σ_y/σ_z equator); (2)
    **input subset** — minimal {vacuum, Fock $|2\rangle$, cat
    $|\alpha|=1.5$}, full §7#4 set a no-new-physics extension; (3)
    **metrics** — grid-free state-space primary (purity drop,
    fidelity to pre-train state, analytic $|\beta_\text{tot}|$) +
    parity-form Wigner ($2/\pi$ prefactor) / negativity-change /
    ideal-vs-native $L^1$ as reported diagnostic (not gated, per the
    χ-bridge-metric caveat). The native leg is **matched physical
    control** (D4 Layer A pinned WP-E v0.9.1 train at the
    inverse-Dirichlet-assigned $(\delta,\varphi_\text{train})$), a
    *structural* residual — not a $\beta_\text{eff}$ calibration
    (§7#3; scope note §4a). (4) **artefacts** — `run_back_action.py` →
    `back_action.h5`, `plot_back_action.py`; (5) **gating** —
    exploratory diagnostic, the *only* hard PASS/FAIL is the vacuum
    analytic self-consistency anchor (back-action analogue of
    P0/P1). Executed 2026-05-16 (`run_back_action.py`,
    `plot_back_action.py`, vacuum gate PASS); native leg pinned at
    the carrier tooth $k=0$ matching the P1/D3/D4-Layer-B
    inverse-Dirichlet convention (logged in the run logbook
    pre-registration).

  - **k=1 sideband follow-up (executed 2026-05-17).** The first
    sideband variant promised in the v0.6 run logbook is executed in
    [`2026-05-17-back-action-k1-sideband.md`](./logbook/2026-05-17-back-action-k1-sideband.md).
    The runner is now tooth-aware (`--k-sideband 1`) and writes
    `back_action_k1.h5` / `back_action_k1.png` without touching the
    parked carrier artefact. The hard ideal-vacuum gate remains
    PASS at machine precision. Vacuum, Fock $|2\rangle$, and the
    small cat are close to their carrier-tooth native results at the
    locked probe points; the useful sideband witness is coherent
    $|\alpha|=2$, where the native leg stays nearly pure but lands
    far from the input and far from either ideal σ_x branch
    (peak native $F_\mathrm{pre}=0.0486$, σ_x branch
    $F=0.0372$). This closes the single-point k=1 follow-up; a full
    collapse-revival map would require a separate scan over coherent
    phase, detuning, or train length.

## References

Verified bibliography after the v0.4 lit-review pass (per [§5a
discipline](#5a-conduct-and-fair-conventions)). Eleven entries
spanning formalism foundation, trapped-ion lineage, cavity-QED
parallel lineage, and the direct experimental antecedent. Each entry
has a per-paper extraction in [`refs/extractions/`](./refs/extractions/);
the lineage synthesis is in [`refs/contextual-notes.md`](./refs/contextual-notes.md).

### Foundation

- **[CG69]** K. E. Cahill and R. J. Glauber,
  *Density Operators and Quasiprobability Distributions*,
  Phys. Rev. **177**, 1882 (1969).
  DOI: [10.1103/PhysRev.177.1882](https://doi.org/10.1103/PhysRev.177.1882).
  Extraction: [`refs/extractions/CG69.md`](./refs/extractions/CG69.md).
  *Anchors:* §Analytical (bullets 2, 3, 4); §1 hypothesis.

### Trapped-ion phase-space tomography lineage

- **[Wal95]** S. Wallentowitz and W. Vogel,
  *Reconstruction of the Quantum Mechanical State of a Trapped Ion*,
  Phys. Rev. Lett. **75**, 2932 (1995).
  DOI: [10.1103/PhysRevLett.75.2932](https://doi.org/10.1103/PhysRevLett.75.2932).
  Extraction: [`refs/extractions/Wal95.md`](./refs/extractions/Wal95.md).
  *Anchors:* §1 (lineage start — earliest trapped-ion tomography proposal).

- **[LMKMIW96]** D. Leibfried, D. M. Meekhof, B. E. King, C. Monroe,
  W. M. Itano, D. J. Wineland,
  *Experimental Determination of the Motional Quantum State of a Trapped Atom*,
  Phys. Rev. Lett. **77**, 4281 (1996).
  DOI: [10.1103/PhysRevLett.77.4281](https://doi.org/10.1103/PhysRevLett.77.4281).
  Extraction: [`refs/extractions/LMKMIW96.md`](./refs/extractions/LMKMIW96.md).
  *Anchors:* §1 (first experimental trapped-ion Wigner reconstruction);
  §7#4 (Fock-state benchmark precedent on Be⁺).

- **[FH20]** C. Flühmann and J. P. Home,
  *Direct Characteristic-Function Tomography of Quantum States of the
  Trapped-Ion Motional Oscillator*,
  Phys. Rev. Lett. **125**, 043602 (2020).
  DOI: [10.1103/PhysRevLett.125.043602](https://doi.org/10.1103/PhysRevLett.125.043602).
  Extraction: [`refs/extractions/FH20.md`](./refs/extractions/FH20.md).
  *Anchors:* §Analytical (bullets 2, 4 — direct trapped-ion implementation
  with non-Gaussian demonstrations: displaced-squeezed, cat, GKP); §1
  (direct precedent for WP-W's reconstruction pipeline). **WP-W
  inherits the χ-FFT chain from FH20; the stroboscopic-comb adaptation
  is WP-W's distinct contribution.**

### Cavity-QED parallel lineage

- **[LD97]** L. G. Lutterbach and L. Davidovich,
  *Method for Direct Measurement of the Wigner Function in Cavity QED and Ion Traps*,
  Phys. Rev. Lett. **78**, 2547 (1997).
  DOI: [10.1103/PhysRevLett.78.2547](https://doi.org/10.1103/PhysRevLett.78.2547).
  Extraction: [`refs/extractions/LD97.md`](./refs/extractions/LD97.md).
  *Anchors:* §Analytical (bullet 2 — displaced-parity origin); §1
  (lineage statement). Applies to both cavity QED and ion traps.

- **[Bertet02]** P. Bertet, A. Auffeves, P. Maioli, S. Osnaghi,
  T. Meunier, M. Brune, J. M. Raimond, S. Haroche,
  *Direct Measurement of the Wigner Function of a One-Photon Fock State in a Cavity*,
  Phys. Rev. Lett. **89**, 200402 (2002).
  DOI: [10.1103/PhysRevLett.89.200402](https://doi.org/10.1103/PhysRevLett.89.200402).
  Extraction: [`refs/extractions/Bertet02.md`](./refs/extractions/Bertet02.md).
  *Anchors:* §Analytical background — first cQED implementation of LD97.

- **[Hof09]** M. Hofheinz, H. Wang, M. Ansmann, R. C. Bialczak,
  E. Lucero, M. Neeley, A. D. O'Connell, D. Sank, J. Wenner,
  J. M. Martinis, A. N. Cleland,
  *Synthesizing the quantum states of a superconducting resonator*,
  Nature **459**, 546 (2009).
  *Anchors:* §1 (lineage — superconducting-cQED implementation);
  §Analytical background. Author list verified via FH20 ref [13].

### Hasse-group lineage (experimental antecedents)

- **[Hasse24]** F. Hasse, D. Palani, R. Thomm, U. Warring, T. Schaetz,
  *Phase-stable traveling waves stroboscopically matched for superresolved
  observation of trapped-ion dynamics*,
  Phys. Rev. A **109**, 053105 (2024).
  DOI: [10.1103/PhysRevA.109.053105](https://doi.org/10.1103/PhysRevA.109.053105).
  ArXiv: [2309.15580](https://arxiv.org/abs/2309.15580).
  Local PDF: [`../refs/Hasse2024_PRA_109_053105.pdf`](../refs/Hasse2024_PRA_109_053105.pdf).
  Extraction: [`refs/extractions/Hasse24.md`](./refs/extractions/Hasse24.md).
  *Anchors:* §Experiment (reference platform); §1 (direct experimental
  antecedent); §7#7 (bridge anchor); §8 v0.5 back-action and
  squeezed-state scope (Hasse App D, App E). **WP-W reinterprets
  Hasse24's protocol; it does not invent it.**

- **[Clos16]** G. Clos, D. Porras, U. Warring, T. Schaetz,
  *Time-Resolved Observation of Thermalization in an Isolated Quantum System*,
  Phys. Rev. Lett. **117**, 170401 (2016).
  DOI: [10.1103/PhysRevLett.117.170401](https://doi.org/10.1103/PhysRevLett.117.170401).
  *Anchors:* §Analytical bullet 5 — Hasse-group predecessor establishing
  the $H_\text{TI}$ form. (Hasse 2024 cites this as ref [43].)

### Engine context and supplementary

- **[LBMW03]** D. Leibfried, R. Blatt, C. Monroe, D. J. Wineland,
  *Quantum dynamics of single trapped ions*,
  Rev. Mod. Phys. **75**, 281 (2003).
  DOI: [10.1103/RevModPhys.75.281](https://doi.org/10.1103/RevModPhys.75.281).
  *Anchors:* §Analytical background — canonical trapped-ion review,
  spin–motion Hamiltonian conventions.

- **[STO12]** S. S. Mirkhalaf and K. Mølmer,
  *Sympathetic Wigner-function tomography of a dark trapped ion*,
  Phys. Rev. A **85**, 042109 (2012).
  DOI: [10.1103/PhysRevA.85.042109](https://doi.org/10.1103/PhysRevA.85.042109).
  ArXiv: [1110.4804](https://arxiv.org/abs/1110.4804).
  Extraction: [`refs/extractions/STO12.md`](./refs/extractions/STO12.md).
  *Anchors:* §Analytical background — sympathetic-readout extension
  (off WP-W main lineage; cited as broader trapped-ion tomography
  context).

-----

**Lineage map and what-WP-W-actually-contributes synthesis:** see
[`refs/contextual-notes.md`](./refs/contextual-notes.md).
