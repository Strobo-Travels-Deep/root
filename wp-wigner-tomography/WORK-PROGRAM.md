# WP-W — Wigner-Like Reconstruction in the Lamb–Dicke / Idealised-Train Limit

**Work Program · v0.2 · 2026-05-13 · tightening pass**
**Status:** *scaffolding — not yet execution-ready. §2 and §7#1–2 are
settled for the first numerical pass; remaining [TBD] markers are live
edit-surface for the next iterations.*
**Numbering:** WP-W (provisional; to reconcile with the existing
WP-V / WP-E letters in §6).

This document is the full WP that grew out of
[wp-analysis-train-tomography](../wp-analysis-train-tomography/)
— the quick-and-dirty kick-off ("WP-TOM v0.x") that established the
protocol carries tomographic information but mis-identified the
inversion regime (see the kick-off
[logbook §6](../wp-analysis-train-tomography/logbook/2026-05-13-kickoff-expectations-and-run.md)).
WP-W picks up where that logbook ends: in the **Lamb–Dicke regime
with an idealised pulse train**, there should exist a clean
analytic mapping from the measured $(\delta, \varphi_\text{train})$
data to the motional Wigner function $W(\alpha)$ — and the mapping
should remain valid for **non-Gaussian** inputs (Fock states, cat
states, squeezed states).

-----

## Experiment

The apparatus context. We start in an *idealised* limit; deviations
from idealisation become diagnostics in their own right.

- **Idealised analysis train:** $N$ instantaneous SDF pulses at
  period $T_m$, single-tooth (i.e. drive only resolves the chosen
  sideband; carrier and higher sidebands suppressed), spin-dependent
  displacement $D(\sigma_z\,\beta_n)$ per pulse with
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
  idealised SDF (instantaneous, $\sigma_z$-coupled, perturbative),
  the post-train complex contrast is
  $C(\delta, \varphi_\text{train}) = \langle\sigma_x\rangle + i\langle\sigma_y\rangle \;=\; e^{-|\beta_\text{tot}|^2/2}\,\chi_{\rho_m}(\beta_\text{tot})$
  with $\chi_{\rho_m}(\beta) = \mathrm{Tr}[\rho_m\,D(\beta)]$ the
  symmetric characteristic function. **The map is observable-equals-$\chi$
  point-by-point.**
- **Wigner inversion.** $W(\alpha) = \pi^{-2}\int e^{\alpha\beta^* - \alpha^*\beta}\,\chi(\beta)\,d^2\beta$.
  The 2D FFT of $\chi(\beta)$ over the $\beta$-grid returns the
  Wigner function on the corresponding $\alpha$-grid. With this Fourier
  convention, finite $\beta$ support $B$ sets the raw $\alpha$ resolution
  $\Delta\alpha \simeq \pi/(2B)$, while $\Delta\beta$ sets the alias-free
  half-width $\alpha_\text{Nyq} \simeq \pi/(2\Delta\beta)$.
- **Non-Gaussian validity.** The chain holds for *any* $\rho_m$ —
  Gaussian or not, mixed or pure — because $\chi$ is a complete state
  representation. Specific predictions: Fock $|n\rangle$ has
  $\chi(\beta) = e^{-|\beta|^2/2}\,L_n(|\beta|^2)$ (Laguerre);
  even/odd cats have characteristic Gaussian humps at $\pm 2\alpha$
  with interference fringes through the origin.
- **Approximation hierarchy.** [TBD] Document the LD expansion order,
  the role of pulse duration ($\delta t/T_m$), the role of finite
  $N$ tooth width ($1/N$ in $\delta/\omega_m$), and the role of
  non-σ_z SDF coupling (the engine uses $C\sigma_- + h.c.$). Each is
  a separate departure from the ideal limit and should be diagnosed
  as such.
- **Background.** Hofheinz et al. (cQED), Flühmann et al. (trapped
  ions, sympathetic), Lutterbach–Davidovich for the inversion. [TBD]
  add citations.

## Numerical

The dataset, validation, and reconstruction pipeline.

- **Engine.** The same `scripts/stroboscopic` package used by WP-V,
  WP-E, and WP-TOM. The forward maps are exact (full Hilbert-space
  propagation, no approximation in $\eta$ or pulse duration), so the
  numerical–analytical comparison directly quantifies the LD /
  idealised-train errors.
- **Forward-map regime sweep.** Drive strength
  $\Omega_r \cdot N\delta t \in \{0.01\pi, 0.05\pi, 0.1\pi, 0.25\pi, 0.5\pi, \pi\}$
  at fixed input state ($|\alpha|=1$); compare to the analytic
  $\chi$ prediction. The perturbative regime boundary is wherever the
  residual exceeds ~5 %.
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

The kick-off WP-TOM demonstrated that the $(\delta, \varphi_\text{train})$
heatmap visually carries motional-state information and that
template matching against an engine-precomputed grid recovers
$(|\alpha|, \theta_\alpha)$ for coherent inputs. But template
matching is opaque: it works for the eight states in the table and
generalises only by enlarging the table. It does not tell us *why*
the protocol works, where its regime of validity is, or whether it
extends to non-Gaussian inputs.

WP-W reframes the same protocol as **characteristic-function
tomography** in the spirit of Lutterbach–Davidovich, Hofheinz et al.,
and Flühmann et al., specialised to the stroboscopic-comb forward
map. The hypothesis is:

> *In the Lamb–Dicke perturbative regime with an idealised pulse
> train, the complex contrast $C(\delta, \varphi_\text{train})$ is
> a point-wise measurement of the symmetric characteristic function
> $\chi_{\rho_m}(\beta(\delta, \varphi_\text{train}))$, and a 2D FFT
> reconstructs $W(\alpha)$ for arbitrary input motional states.*

The WP tests this analytically (closed-form $\beta$-map and
$\chi$-equivalence), numerically (engine vs. analytic agreement
under controlled drive strength), and operationally (Wigner
reconstruction on the five-class test set, including non-Gaussian
inputs).

The connection to the kick-off is then clean: WP-W is the
**perturbative** version of the same protocol; WP-TOM kick-off is
the **saturated** version. They sample overlapping physics from
opposite sides; the comparison is one of the WP's deliverables.

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

Three motivations, ranked by priority:

1. **Establish the protocol's regime of validity** quantitatively.
   The kick-off told us "saturated → template matching"; WP-W tells
   us "where exactly does the perturbative picture take over, and
   how does the error scale".
2. **Demonstrate Wigner reconstruction on a non-Gaussian state**
   numerically — Fock $|1\rangle$ and the small cat are the
   headline demos. This is the WP's "deliverable plot".
3. **Bridge to WP-E.** WP-E maps the forward observable
   $(\vartheta_0, \delta) \to (\sigma_z, |C|)$ at saturated drive;
   WP-W maps the inverse $(\delta, \varphi_\text{train}) \to W(\alpha)$
   at perturbative drive. Cross-checking on a shared anchor state
   ($|\alpha|=3, \vartheta_0 = 0$) confirms both engines agree on the
   common physics.

Out of scope for the v0.2 execution candidate:

- Lab implementation (this is a numerical WP).
- Thermal-state and decoherence sensitivity beyond a single sanity
  check.
- Squeezed-state reconstruction (a follow-up — needs the LD
  perturbation extended past the linear order).

## 4. Deliverables

[TBD] Tighten this list once §5 and §7#3 are settled.

Provisional deliverables:

1. **Analytical note** (≤ 5 pages) deriving the $(\delta, \varphi_\text{train}, N) \to \beta$
   map, the $C = e^{-|\beta|^2/2}\chi$ equivalence, and the order in
   $\eta$ at which each holds.
2. **Forward-map regime sweep** (.h5 + `wp_manifest_v1`): six drive
   strengths × $|\alpha|=1$ × the v0.2 $\beta$ grid. Plot:
   analytic-vs-engine residual heatmap. Identifies the
   perturbative-regime boundary.
3. **Wigner reconstruction demo** on five input classes: vacuum,
   coherent $|\alpha|=1.5$, thermal $\bar n = 0.5$, Fock $|1\rangle$,
   cat at $|\alpha|=1.5$. Output: $W_\text{rec}$ vs $W_\text{true}$
   side-by-side, fidelity numbers, L¹ error map.
4. **WP-TOM bridge plot.** Same input state reconstructed by
   template matching (saturated drive) and FFT inversion
   (perturbative drive); residual map.
5. **Logbook** with pre-registered expectations per WP-TOM
   convention.

## 4a. Preflight gate (gates the main sweep)

Before the six-drive regime sweep or five-state reconstruction demo, run
a single targeted preflight. Gate condition: the preflight must either
pass, or fail with an identified departure from the idealised chain.

As of v0.2, only the analytic-grid self-consistency half of this gate is
fully specified. The engine comparator depends on the §7#3 conversion
between the engine's $C\sigma_-+\mathrm{h.c.}$ coupling and the idealised
$\sigma_z$ displacement scale $|\beta_0|$; it must not be treated as
runnable until that conversion is fixed.

**Protocol.** At the v0.2 nominal $|\beta_0|=0.05$, run one
central-lobe target point,
$\beta_\star = 0.5\,e^{i\pi/4}$, for two input states: vacuum and
coherent $|\alpha=1\rangle$. Use the inverse-Dirichlet rule of §2 to
choose $(\delta,\varphi_\text{train})$ for $N=20$ and $N=80$.

**Comparators.**

1. Analytic prediction:
   $C_\text{ideal}(\beta_\star) =
   e^{-|\beta_\star|^2/2}\chi_{\rho_m}(\beta_\star)$.
2. Engine prediction from `scripts/stroboscopic`, using the weakest
   available drive setting that realises the same effective per-pulse
   displacement convention.
3. Reconstruction sanity check: insert the analytic $\chi$ values on the
   v0.2 grid for a coherent state and verify the FFT peak lands at the
   prepared $\alpha$ within one raw $\Delta\alpha$ cell.

**Pass criteria.**

- Analytic-grid self-consistency: coherent-state peak position within
  one raw $\Delta\alpha$ cell and no sign flip in the phase convention.
- Engine-vs-analytic single point: complex residual
  $|C_\text{engine}-C_\text{ideal}|/|C_\text{ideal}| < 5\%$ at $N=20$.
  The $N=80$ comparison is diagnostic, not gating, because finite tooth
  width and non-ideal coupling can accumulate visibly over the longer
  train.

**Failure classification.** If the gate fails, classify the cause before
launching the sweep: (i) $\sigma_z$ ideal SDF vs. engine
$C\sigma_-+\mathrm{h.c.}$ coupling; (ii) finite pulse duration /
intra-pulse motion; (iii) leakage to carrier or neighbouring sidebands;
(iv) phase-convention or Dirichlet-branch mismatch. A failure in class
(i) is expected to reopen §7#3 rather than invalidate the grid decision.

## 5. Folder layout

[TBD] At initiation. Provisional:

```
wp-wigner-tomography/
  WORK-PROGRAM.md      # this document
  README.md            # short pointer (added at initiation)
  numerics/            # scan drivers + .h5 outputs
  plots/               # publication-quality figures
  logbook/             # dated entries with pre-registered expectations
  notes/               # analytical derivations (markdown / LaTeX)
```

## 6. Connection to other WPs

| WP | Relation |
|---|---|
| [WP-V (Hasse reproduction)](../wp-hasse-reproduction/) | uses the same engine; WP-V validates the engine itself, WP-W validates a protocol *built on* the engine. |
| [WP-E (Phase-contrast maps)](../wp-phase-contrast-maps/) | mirror image: WP-E is the forward observable at saturation; WP-W is the inverse at perturbation. §3 bullet 3 articulates the bridge. |
| [WP-TOM kickoff](../wp-analysis-train-tomography/) | direct predecessor; supplies the saturated-regime baseline that WP-W is the perturbative counterpart to. |

[TBD] Reconcile the WP-V / WP-E / WP-T / WP-W lettering once the
naming policy is fixed (see WP-E §8).

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
3. **SDF coupling — $\sigma_z$ vs. $\sigma_x$.** The idealised
   analytic chain assumes $\sigma_z$-coupled displacement; the
   engine implements $C\sigma_- + h.c.$, which is $\sigma_x$-like
   on the carrier. How does the analytic chain change, and how
   does it manifest as an engine residual?
4. **Test states.** The five-class list is provisional. Should we
   add: squeezed vacuum (needs higher-order LD)?
   GKP-lattice probe state (ambitious)? Mixed cat (decoherence
   stress test)?
5. **Reconstruction fidelity targets.** What counts as success for
   §4 deliverable 3 — fidelity ≥ 95 %? 99 %? Different for Gaussian
   vs. non-Gaussian? The v0.2 grid makes the cat reconstruction the
   deciding non-Gaussian benchmark; Fock $|2\rangle$ is near the raw
   $\Delta\alpha$ resolution and should carry a looser, explicitly
   resolution-limited target.
6. **Naming.** Provisional WP-W; the existing letters are V, E, and
   the kick-off's WP-TOM. Reconcile.
7. **Cross-check with WP-E.** Pick the shared anchor state and the
   shared observable. Document the anchor in §3 bullet 3 once
   settled.

## 8. Status

**v0.1 scaffold (2026-05-13):** structure in place, regime defined,
hypothesis stated, deliverables sketched.

**v0.2 tightening pass (2026-05-13):** §2 drive scale and grid settled
for the first numerical pass: $|\beta_0|=0.05$, $N_\text{rec}=80$,
$B=4.0$, $\Delta\beta=0.10$, inverse-Dirichlet Cartesian targeting, and a
single-point preflight gate added in §4a. The WP is still not
execution-ready because §7#3–7 remain open.

Next tightening pass anticipated:

- **v0.3:** settle the SDF-coupling chain (§7#3), then tighten §4
  deliverables with concrete engine commands, fidelity targets, naming,
  and the WP-E bridge anchor. Become execution-ready.

## References

[TBD] — add Hofheinz, Flühmann, Lutterbach–Davidovich,
Cahill–Glauber, plus the existing
[Hasse 2024 PRA reference](../refs/Hasse2024_PRA_109_053105.pdf).
