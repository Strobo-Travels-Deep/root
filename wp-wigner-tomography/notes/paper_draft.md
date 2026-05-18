<!--
WP-W PAPER DRAFT — Markdown working copy.
Built strictly against publication_assessment.md §8 (locked claim
contract) and publication_outline.md. Status: §II, §III, §IV, §V
drafted in full (theoretical contribution + validated reconstruction
+ quantitative back-action + the proof-of-structure squeezing
result); §I/VI/VII structured prose with key paragraphs; abstract
from the vetted outline sketch; figures = placeholders → committed
artefacts. A claim-hygiene pass separated the ideal-SDF
direct-χ-readout layer from the native engine throughout (§II.A/§IV),
tightened the Hasse24-experimental attribution (§I.P2), fixed the
Ω_r unit/convention note (§II.A), and bounded the FH20 χ-measurement
phrasing (§V.D/§VI.P3).
Claims = exactly the four of publication_assessment.md §3. Banned in
all prose: "first", "first characterisation", "structural
impossibility", "not previously stated", headline "novel/novelty",
unbounded "structural, not a regime limit". Numbers quoted from the
committed artefacts/logbooks (provenance in the figure map).
-->

# Characteristic-function tomography under a high-Lamb–Dicke monochromatic stroboscopic drive: forward map, validated reconstruction, and the native engine's quantitative departure from the ideal SDF

**U. Warring *et al.* (author list provisional)**

*Theory/numerics manuscript — draft. Target: Phys. Rev. A (regular
article) / New J. Phys.*

-----

## Abstract

Direct characteristic-function (χ) tomography reconstructs a motional
quantum state by sampling $\chi(\beta)=\langle \hat D(\beta)\rangle$
and Fourier-transforming to the Wigner function. Flühmann and Home
[FH20] realised this on a Ca⁺ ion with a *bichromatic*
state-dependent force (SDF) at Lamb–Dicke parameter
$\eta\!\approx\!0.05$, demonstrating displaced, squeezed,
squeezed-cat and approximate-GKP states. The Freiburg ²⁵Mg⁺ programme
[Hasse24] instead drives a *monochromatic* stroboscopic AC pulse
train at $\eta=0.40$, measuring phase-space position and momentum and
outlining back-action and squeezed-state extensions. Here we adapt
the χ-FFT framework to that monochromatic stroboscopic regime. An
inverse-Dirichlet rule maps the physical
$(\delta,\varphi_\text{train})$ scan onto FFT-ready Cartesian $\beta$
nodes; we validate the full chain numerically at $\eta=0.40$ against
analytic truth (machine-precision preflight gates; engine-vs-analytic
χ residual $3.75\times10^{-4}$ over 6481 nodes). We then *quantify*,
where [Hasse24] gave qualitative or conceptual sketches, (i) the
Wigner-resolved ideal-vs-native back-action across seven input states
on the carrier and first sideband, exhibiting a tooth-robust
quantum/classical discriminator, and (ii) the $\mathcal O(\eta^2)$
two-phonon (squeezing) channel: at the [Hasse24] App.-E timing the
monochromatic engine does not cleanly engineer it — a gate-anchored,
$(r,\theta)$-robust null, with the η-exact ideal reconstruction as a
bit-for-bit reference. The study is numerical; the [Hasse24]
experiment is cited as motivation and for parameter provenance, not
as a demonstrated experimental match.

-----

## I. Introduction *(structured prose; key paragraphs)*

**P1 — the χ-tomography lineage.** Cahill–Glauber [CG69] symmetric
characteristic function; the displaced-parity reconstruction proposal
[Wal95]/[LD97] and its cavity-QED implementation [Bertet02];
trapped-ion Wigner reconstruction [LMKMIW96]; and the direct trapped-
ion precedent **[FH20]**: χ → 2D-FFT → W on a single Ca⁺ ion at
$\eta\!\approx\!0.05$ via a bichromatic SDF, with squeezed,
squeezed-cat and approximate-GKP states. *State plainly: the χ-FFT
framework and its non-Gaussian reach are [FH20]'s; this work adopts,
not introduces, that framework.*

**P2 — the Freiburg ²⁵Mg⁺ programme.** [Hasse24] established the
monochromatic stroboscopic AC-train protocol (Hamiltonian Eq. (C1))
and demonstrated phase-space position/momentum readout
*experimentally* on ²⁵Mg⁺ at $\eta=0.40$, via the 2D
$(\varphi,\vartheta_0)$ scan. It additionally gave a *qualitative*
back-action map (App. D / Fig. 6b) and a *numerical/conceptual*
squeezed-state extension with the timing change
$\Delta t = 2\pi/(2\omega_m)$ (App. E / Fig. 9). *This manuscript is a
theory/numerics continuation of that programme.*

**P3 — the gap this paper fills.** One sentence per claim,
subordinated: (1) the stroboscopic-monochromatic-specific
inverse-Dirichlet Cartesian forward map that makes χ-FFT tomography
applicable to the [Hasse24] protocol; (2) numerical validation of the
chain in the non-perturbative $\eta=0.40$ regime that [FH20]'s
platform sidesteps; (3) the *quantitative* Wigner-resolved
ideal-vs-native back-action map (vs [Hasse24]'s qualitative
$\delta\langle n\rangle$); (4) the quantitative native
$\mathcal O(\eta^2)$ two-phonon squeezing-channel result, where
[Hasse24] App. E gave only the ideal-timing concept. Explicitly *not*
claimed: the framework, the protocol, the back-action or
squeezed-state concepts, or GKP.

**P4 — scope and honesty.** This is a numerical study. The "native
engine" is a simulation of the [Hasse24] Hamiltonian; the ideal↔
native bridge is validated against a sibling numerical reference, not
against experimental data. [Hasse24]'s measurements motivate the work
and fix all engine parameters; no experimental match is claimed.

## II. Protocol and the inverse-Dirichlet forward map *(drafted in full — the theoretical contribution, claim 1)*

### II.A The monochromatic stroboscopic engine

The [Hasse24] analysis interaction during one AC flash is, in the
spin-rotating frame,
$$
  H_\text{eng}=\frac{\delta}{2}\,\sigma_z+\omega_m a^\dagger a
  +\frac{\Omega_r}{2}\big(e^{i\varphi}\,C\,\sigma_-+e^{-i\varphi}\,C^\dagger\,\sigma_+\big),
  \qquad C=e^{i\eta(a+a^\dagger)},
$$
with Lamb–Dicke parameter $\eta=0.40$ (engine value $0.397$),
$\omega_m/2\pi=1.3$ MHz, flash duration $\delta t=0.13\,T_m$,
$T_m=2\pi/\omega_m$, and dimensionless engine coupling
$\Omega_r=0.0902$ — the pinned D4-Layer-A simulation value. (The
corresponding *physical* AC Rabi rate in [Hasse24] is
$\Omega_\text{AC}/2\pi\!\approx\!0.3$ MHz; this is a different
unit/convention, not the same number — we work throughout in the
engine's dimensionless units, the pinned WP-E/[Hasse24] D4-Layer-A
set.) This is Eq. (C1) of [Hasse24] in the analysis frame; we take it
as given. The train is $N$ flashes at period $T_m$ with a programmed
per-flash phase $\varphi_\text{train}$.

**The ideal measurement operator is *not* this native drive.** It is
the FH20-style σ_x state-dependent force $U=D(\sigma_x\beta/2)$ —
which [FH20] realises with a *bichromatic* drive and which we supply
numerically as a separate primitive. On the equatorial spin state
$|{+}y\rangle$ (Ramsey-orthogonal to the σ_x SDF axis) a single
resolved comb tooth of *the ideal SDF* reads the symmetric
characteristic function **directly**,
$$
  \chi_{\rho_m}(\beta)=\langle\sigma_y\rangle-i\langle\sigma_z\rangle,
$$
with **no Gaussian prefactor and no overall phase** (the σ_x axis,
not σ_z: a σ_z-conditioned displacement commutes with the σ_z
detuning precession and never builds the comb — a 165 % residual,
versus $10^{-14}$ for σ_x; a v0.5 convention correction, Appendix A).

The native monochromatic engine of the Hamiltonian above does **not**
natively realise this ideal operator: its leading term is
Jaynes–Cummings-type and comb-sharpening selects but does not
transmute it (engine-specific — [FH20]'s bichromatic drive *does*
realise the ideal χ-measurement chain; §VI). The native engine
therefore enters this work only as the **matched-control comparison**
against the ideal-SDF prediction (§IV back-action; §V the
$\mathcal O(\eta^2)$ channel), never as a direct χ reader. Keeping
the ideal-SDF measurement layer and the native engine distinct is the
load-bearing framing of this manuscript.

### II.B The Dirichlet forward map

[FH20] uses a CW bichromatic SDF whose displacement amplitude is a
free continuous knob; [Hasse24] uses a *stroboscopic* train whose
physical knobs are the detuning $\delta$ and the train phase
$\varphi_\text{train}$, scanned on a polar $(\varphi,\vartheta_0)$
grid. Neither yields, directly, the *Cartesian* $\beta$ samples a 2D
FFT needs. The bridge is the central construction of this paper.

Between flashes the rotating-frame SDF axis advances by the per-gap
detuning phase $x=(\delta-k\omega_m)\,T_m$ on comb tooth $k$
($k=0$ = carrier). Flash $n\in[0,N)$ therefore contributes a
displacement $\beta_0\,e^{i(\varphi_\text{train}+nx)}$, and the
accumulated branch separation is the geometric sum
$$
  \beta_\text{tot}(\delta,\varphi_\text{train};N)
  =\beta_0\,e^{i\varphi_\text{train}}\sum_{n=0}^{N-1}e^{inx}
  =\beta_0\,e^{i\varphi_\text{train}}\,\mathcal D_N(x),
  \quad
  \mathcal D_N(x)=e^{i(N-1)x/2}\frac{\sin(Nx/2)}{\sin(x/2)},
$$
the **Dirichlet kernel**, $\mathcal D_N(0)=N$ (on-resonance reach
$|\beta_\text{tot}|_\text{max}=N\beta_0$). This per-flash-phase
implementation is exact at all $\beta_0$ (putting the detuning into
free σ_z gap precession instead contaminates the lab-frame χ readout
by $(N-1)\delta T_m$ — Appendix A).

**Inverse-Dirichlet Cartesian targeting.** Reconstruction needs χ on
a Cartesian $\beta$ grid; the knobs are $(\delta,\varphi_\text{train})$.
For a target node $\beta_\star=r\,e^{i\theta}$, $r\le N\beta_0$:
solve $r/\beta_0=|\mathcal D_N(x)|$ on the monotone central branch
$0\le x\le 2\pi/N$ (a 1-D root find; $|\mathcal D_N|$ decreases
monotonically from $N$ to $0$ there), then set
$\varphi_\text{train}=\theta-\arg\mathcal D_N(x)=\theta-(N-1)x/2$ and
the physical detuning $\delta-k\omega_m=x/T_m$. Nodes with
$r>N\beta_0$ are zero-filled before the FFT. This rule — the
**stroboscopic-monochromatic-specific** map from the [Hasse24]
physical scan to FFT-ready Cartesian χ — is absent from [FH20]
(continuous bichromatic amplitude, no comb) and from [Hasse24] (polar
scan, no χ frame). It is the theoretical contribution of this work.

The conjugate α-grid spacing is $\Delta\alpha=\pi/(N_g\Delta\beta)$ —
*not* the textbook $2\pi/(N_g\Delta\beta)$ — because the
Cahill–Glauber kernel carries a factor $2i$; getting this wrong
displaces every reconstruction (Appendix A; validated by P0 below).

**[Fig. 1]** forward-map schematic + the reach ladder: measured
`n_in_disk` $=\{317,1257,2821,5025\}$ for $N=\{20,40,60,80\}$,
matching $\pi(N\beta_0)^2/\Delta\beta^2$ and the independent grid
count $5025$. *(artefact: `reach_ladder_ideal.h5`, D2.)*

## III. Validated reconstruction at η = 0.40 *(claim 2)*

Before any native comparison the inversion chain itself must be
trustworthy at $\eta=0.40$. Two preflight gates establish this. The
analytic self-consistency gate Fourier-transforms an analytically
evaluated χ and recovers the vacuum centre $W(0)=0.636555$ against
$2/\pi=0.636620$ (a $-6.5\times10^{-5}$ finite-grid-windowing
residual), places the coherent peak on the predicted node to one part
in $10^4$, and holds $\max|\mathrm{Im}\,W|\sim10^{-16}$ — confirming
the FFT convention and in particular the
$\Delta\alpha=\pi/(N_g\Delta\beta)$ relation of §II.B. The
engine-faithfulness gate feeds the *ideal-SDF* primitive's measured χ
— not the native engine — at the sentinel
$\beta_\star=0.5\,e^{i\pi/4}$ for vacuum and a coherent state,
$N\in\{20,80\}$, reproducing the analytic χ to a relative residual
$\sim10^{-14}$: the σ_x-SDF / direct-χ chain of §II.A is exact at a
point.

On the v0.2 Cartesian grid the seven headline §7#4 states reconstruct
through the full inverse-Dirichlet → FFT pipeline; the two deciding
states clear at $F=0.9997$ (Fock $|2\rangle$) and $F=0.9664$ (cat
$|\alpha|=1.5$). The quantum/classical control behaves as required:
the *mixed* cat reconstructs as two incoherent Gaussian humps with no
interference fringes while the *pure* cat's fringes are recovered —
the pipeline does not manufacture coherence (**[Fig. 2]**; artefact
`reconstruction_demo.h5`).

The ideal↔native bridge is then quantified at the shared
$|\alpha=3\rangle$ anchor. At matched physical drive the native
engine reproduces an independent reference scan bit-exactly
($\max|\Delta|=0.00\times10^{0}$ on
$(\sigma_z,\mathrm{Re}\,C,\mathrm{Im}\,C)$ at three δ/ω_m points), and
the engine-measured χ matches the analytic χ to
$\max|\Delta|=3.75\times10^{-4}$ over the 6481-node fine grid — the
load-bearing bridge number. The associated FFT-centroid residual
$1.99\times10^{-2}$ is sub-pixel by construction and is quoted only
with its $\Delta\alpha=0.388$ pixel size attached, never as a bare
gate (**[Fig. 3]**; artefact `bridge_inversion.h5`).

Together these establish the chain in the *non-perturbative*
$\eta=0.40$ regime that [FH20]'s $\eta\!\approx\!0.05$ platform
avoids. The LD expansion's $\mathcal O(\eta^2)\!\approx\!16\%$ term is
non-negligible here — a known deviation of this platform, not a new
observation; the deviation hierarchy is carried explicitly
(Appendix B) rather than asserted as a finding.

## IV. Quantitative ideal-vs-native back-action *(claim 3)*

[Hasse24] App. D / Fig. 6b already maps the back-action
$\delta\langle n\rangle(\varphi,\vartheta_0)$ *qualitatively* for
$|\alpha|=3$; the contribution here is the *quantitative,
Wigner-resolved* ideal-vs-native comparison, not a characterisation
of back-action as such. Both legs run the *same* physical drive
program — the inverse-Dirichlet-assigned
$(\delta,\varphi_\text{train},N)$, with no $\beta_\text{eff}$
calibration — so the η-exact ideal-SDF prediction and the
native-engine result form a matched-control pair (the §II.A
ideal/native separation). The single hard gate is the vacuum analytic
anchor: post-measurement purity $\tfrac12(1+e^{-|\beta|^2})$,
fidelity $e^{-|\beta|^2/4}$, and
$W=W_\text{mixed-cat}(\beta_\text{tot}/2)$, passed at machine
precision and tooth-independent.

Across the seven §7#4 inputs, on the carrier ($k=0$) and the first
sideband ($k=1$), the Wigner-resolved ideal-vs-native residual
exhibits a **tooth-robust quantum/classical discriminator**: the pure
cat's structural $L^1$ ($1.87$) exceeds the mixed cat's ($1.47$) on
*both* teeth, while a broad thermal input is the most robust
($L^1=0.49$) — the same coherence-sensitivity ordering survives the
carrier→sideband change of native dynamics. The mixed-input
propagation reuses the validated pure-state pipeline verbatim,
reproduced bit-for-bit ($0.0\times10^{0}$ across 240 fields at $k=0$,
225 at $k=1$). The sideband signature is concentrated in the
conditional, branch-selected channel, so the $k=1$ data do not
retroactively change the carrier conclusion (**[Fig. 4]**; artefacts
`back_action_full.h5`, `back_action_k1_full.h5`).

## V. The native 𝒪(η²) squeezing-channel result *(DRAFTED IN FULL — proof-of-structure, claim 4)*

### V.A Prior art and the timing, stated up front

[Hasse24] Appendix E extends the stroboscopic protocol to squeezed
states, introducing the squeezing operator
$S(\xi)=\exp[\tfrac12(\xi^* a^2-\xi a^{\dagger2})]$ and the **critical
timing change** $\Delta t=2\pi/(2\omega_m)=T_m/2$ — the train syncs
to the quadrature dynamics, which evolve at $2\omega_m$ — together
with numerical $\langle\sigma_z\rangle$ and $\delta\langle n\rangle$
maps for $\langle n\rangle_\text{sq}=1$. That concept and that timing
are [Hasse24]'s. This section asks a different, quantitative
question: *does the monochromatic engine, at the App.-E timing,
actually realise a clean two-phonon (squeezing) channel — and, when
it does not, by how much does it fall short of the η-exact ideal
prediction across the squeezed-state family?*

We first re-derive the App.-E timing as the §II Dirichlet map at the
doubled fundamental. The $\mathcal O(\eta^2)$ term of the LD
expansion is $-\tfrac{\eta^2}{2}X^2\sigma_\varphi$ with
$X^2=a^2+a^{\dagger2}+2a^\dagger a+1$; the two-phonon part
$a^2,a^{\dagger2}$ evolves at $2\omega_m$, so the coherent
stroboscopic build-up requires the gap to be an integer fraction of
the $2\omega_m$ period — exactly $\Delta t=T_m/2$. The §II
construction then carries over verbatim with a doubled fundamental
and a per-flash scale $\xi_0=\mathcal O(\eta^2\Omega_r\Delta t)$:
$\xi_\text{tot}=\xi_0\,e^{i\varphi_\text{train}}\mathcal D_N(\tilde
x)$, $\tilde x=(\delta-k\omega_m)T_m/2$, the same Dirichlet kernel.
A by-product of this analysis closes the long-open finite-pulse
order: the leading $\mathcal O(\delta t/T_m)$ effect is a pure
displacement phase $\omega_m\delta t/2$ (the bit-exact D4-Layer-A
`shift_deg`), the residual $\mathcal O((\delta t/T_m)^2)\!\approx\!1.7\%$
at $\delta t=0.13\,T_m$ — two-phonon in character, sub-dominant to
the $\eta^2\!\approx\!16\%$ term and carried, never subtracted
(Appendix B).

### V.B The ideal leg is η-exact — the hard gate (P-D)

A central, easily-missed point: the ideal-SDF χ chain is **η-exact
for squeezed vacuum**. The ideal SDF is an exact displacement; the
§II direct-χ readout and the FFT carry no η expansion and no
comb-timing dependence. The $\mathcal O(\eta^2)$ dependence therefore
lives entirely in the *native realisation*, not in the readout — the
App.-E timing is a native-protocol device, not a property the ideal
chain acquires. We make this a hard PASS/FAIL: the analytic
squeezed-vacuum reconstruction must reproduce the independently
committed η-exact baseline **bit-for-bit**. It does, to $\le10^{-12}$:
$F=0.999489$ at $\theta=0$ and $F=0.999992$ at $\theta=\pi/2$
(squeezed vacuum $r=0.5$), $\max|\mathrm{Im}\,W|$ at the `complex128`
floor, **independent of the native App.-E gap**. The ideal reference
is sound; any departure measured below is the native engine's.

### V.C The native engine does not cleanly engineer the channel

*Capability smoke (N-6), pre-registered.* We characterise the native
post-train **vacuum** at the App.-E timing ($\Delta t=T_m/2$, second-
sideband resonance $\delta=2\omega_m$) as a full Gaussian state
versus $N\in\{10,20,30\}$: first moments, covariance eigenvalues and
orientation, purity. A genuine 2ω_m squeeze would show the covariance
eigenvalue ratio departing from 1 and growing with $N$ along the
predicted axis, at fixed first moments and purity. Instead the
anisotropy reaches only $\lambda_+/\lambda_- - 1 = 0.022$ at $N=30$ —
five times below the pre-registered $0.10$ threshold — and is
*coupled to purity loss* ($0.99935\!\to\!0.99314$), i.e. not a clean
unitary squeeze. First moments stay $\approx0$ ($\sim10^{-3}$):
$\delta=2\omega_m$ correctly off-resonates the first-order
single-phonon term (the reference $T_m$-timing run instead grows a
clear displacement $\langle P\rangle\!\to\!-0.32$). The App.-E timing
*suppresses displacement but does not convert it into squeezing.*

*The $(r,\theta)$ sweep.* We then run squeezed-vacuum inputs
$r\in\{0,0.25,0.5\}\times\theta\in\{0,\tfrac\pi2,\pi\}$ (the Wigner
ellipse rotates by $\theta/2$, so $\theta=0$ and $\theta=\pi$ are the
perpendicular squeezed-in-$X$/squeezed-in-$P$ alignments, $\theta=\pi/2$
the 45° intermediate), peak and mid probes, ideal and native legs.
The decisive control is $r=0$: the engine-induced anisotropy
(native ratio minus the input squeezed-vacuum ratio $e^{4r}$) is
$+0.022$ — the vacuum null again — and it does **not** track the
input as $r$ grows; the engine-excess goes *negative*, $-0.371$ at
$r=0.5$. That is, the native post-train covariance ratio tracks the
*input* ratio (pass-through), not engine-generated squeezing: the
monochromatic engine adds no coherent squeezing and, at larger $r$,
mildly *erodes* the input anisotropy through decoherence. Consistent
with this, the native fidelity-to-input degrades systematically with
$r$ (peak: $0.996\!\to\!0.934\!\to\!0.760$); the within-fixed-$r$
$\theta$-modulation of the native ratio is modest (max spread
$0.574$), decoherence-flavoured rather than a clean coherent
modulation; and the ideal-vs-native Wigner $L^1$ grows with $r$. No
$(r,\theta,\text{probe})$ cell recovers the squeezed state.

(*Reporting note.* An earlier internal aggregate that compared the
raw native covariance ratio across $r$ was confounded by the input
$e^{4r}$ pass-through; the corrected engine-excess and within-$r$
$\theta$-spread reported here are persisted with the artefact, and
the per-record data is bit-identical across that correction.)

### V.D Interpretation — engine-specific, bounded

Across the squeezed-state family the [Hasse24] monochromatic engine,
at the App.-E timing, **neither engineers nor faithfully realises**
the $2\omega_m$ squeezing operation, while the η-exact ideal leg
reconstructs every squeezed state (P-D, bit-for-bit). This is a
gate-anchored, $(r,\theta)$-robust *quantitative* boundary on the
native platform — turning [Hasse24] App. E's ideal-timing concept
into a measured characterisation. It is **engine-specific**: [FH20]'s
*bichromatic* SDF natively realises the ideal χ-measurement chain
(including for squeezed inputs — it is the *measurement* operator,
not a squeezed-state engineering mechanism); the result bounds the
*monochromatic* constraint inherited from [Hasse24], not trapped-ion
CF-tomography in general. **[Fig. 5]** — the η-exact P-D
reconstruction beside the native $(r,\theta)$ null *(artefacts:
`squeezed_recon.h5`, `squeezed_native_audit.h5`)*. *(This is the
sharpest, most distinctive figure: ideal-sound / native-fails in one
panel.)*

## VI. Discussion *(structured prose; key paragraphs)*

**P1 — what this gives the [Hasse24] platform.** A precise,
quantified map of where and by how much the monochromatic
stroboscopic drive departs from the ideal FH20 SDF, including the
$\mathcal O(\eta^2)$ squeezing ceiling — directly useful to anyone
planning high-η stroboscopic CF-tomography or stroboscopic squeezing
on this class of apparatus.

**P2 — limits, stated honestly.** Numerical only; engine and bridge
are simulations; [Hasse24]'s experiment is cited as motivation and
parameter provenance, not a demonstrated match. Grid-resolution
caveats are carried explicitly (GKP deferred — [FH20] already
demonstrated it at small η, a resolution not a capability deferral;
D4 centroid sub-pixel with $\Delta\alpha$ attached). The
departure result is engine-specific (P3 below).

**P3 — relation to the broader picture.** [FH20]'s bichromatic SDF
realises the ideal χ-measurement chain natively; the present
quantitative departure is a property of the [Hasse24] monochromatic
constraint. The
perturbative-FFT / saturated-template-matching bridge to the sibling
WP-TOM programme is outlook, not a claim of this paper.

## VII. Conclusion & outlook *(structured prose)*

Recap of claims 1–4 in subordinate language; outlook: a
bichromatic-SDF realisation on the Mg⁺ platform; the WP-TOM bridge;
GKP at finer grid; and an experimental test against [Hasse24]-class
data — the natural way to convert this numerical characterisation
into a measured one.

## Appendices / Supplementary

- **A.** The analytic chain and convention locks (σ_x not σ_z; no
  $e^{-|\beta|^2/2}$; $\Delta\alpha=\pi/(N_g\Delta\beta)$; cat
  $\cosh 2\,\mathrm{Re}(\alpha^*\beta)$; parity prefactor $2/\pi$).
  *Source: `analytic_chain.md`.*
- **B.** The $\mathcal O(\eta^2)$ / $\delta t/T_m$ derivation; the
  App.-E timing as the $2\omega_m$ Dirichlet map; the
  finite-pulse-order closure. *Source: `squeezed_eta2_scope.md`.*
- **C.** Pre-registration logbooks and reproducibility manifests (the
  numerical-WP discipline) — a methods-paper strength.
- **D.** The native-audit scope and the N-6 capability methodology
  (pre-registered null). *Source: `squeezed_native_audit_scope.md`.*

## References *(stub — full list at submission)*

[CG69] Cahill & Glauber, Phys. Rev. 177, 1882 (1969).
[Wal95] Wallentowitz & Vogel, PRL 75, 2932 (1995).
[LD97] Lutterbach & Davidovich, PRL 78, 2547 (1997).
[Bertet02] Bertet *et al.*, PRL 89, 200402 (2002).
[LMKMIW96] Leibfried *et al.*, PRL 77, 4281 (1996).
[FH20] Flühmann & Home, PRL 125, 043602 (2020).
[Hasse24] Hasse, Palani, Thomm, Warring, Schaetz, Phys. Rev. A 109, 053105 (2024).

-----

*Draft built against [`publication_assessment.md`](./publication_assessment.md)
§8 (locked claim contract), §3 (claims), §6 (figure→artefact map),
and [`publication_outline.md`](./publication_outline.md). §II/III/IV/V
drafted in full; §I/VI/VII structured prose + key paragraphs; the
ideal-SDF/native separation is consistent throughout (claim-hygiene
pass); no new claims; every number quoted from a committed
artefact/logbook. Next: flesh §I/VI/VII to full prose, generate
Fig. 1–5 from the artefacts, finalise references — on direction.*
