# WP-W — Wigner-Like Reconstruction in the Lamb–Dicke / Idealised-Train Limit

**Work Program · v0.4 · 2026-05-13**
**Status:** *design closed.* §2, §7#1–7, §4 deliverable commands,
and §5 folder layout are all settled. P0 (analytic-grid gate) and
D1–D3 (ideal-SDF layer) are ready for initiation once the runner
scripts of §4 / §5 are written. P1 + D4 (native-engine bridge)
require the bridge-convention implementation flagged in §7#3 —
candidate path is adding an `ideal_sdf` primitive to
`scripts/stroboscopic`. Background citations and references remain
as polish, not blockers.
**Numbering:** WP-W (formal, per §7#6).

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
- **Approximation hierarchy.** v0.3 separates the hierarchy into two
  layers. The ideal-SDF inversion assumes instantaneous
  $D(\sigma_z\beta_n)$ pulses, a single selected comb tooth, and fixed
  per-pulse $\beta_0$. Finite $N$ enters through the Dirichlet tooth width
  $1/N$ in $\delta/\omega_m$. The native engine bridge is a different
  approximation question: its $C\sigma_-+\mathrm{h.c.}$ coupling expands
  into a carrier rotation plus transverse position-dependent spin
  rotation, not directly into $D(\sigma_z\beta)$; see §7#3. [TBD]
  still to document the pulse-duration order ($\delta t/T_m$) and the
  exact bridge residual metric.
- **Background.** Hofheinz et al. (cQED), Flühmann et al. (trapped
  ions, sympathetic), Lutterbach–Davidovich for the inversion. [TBD]
  add citations.

## Numerical

The dataset, validation, and reconstruction pipeline.

- **Engine.** The same `scripts/stroboscopic` package used by WP-V,
  WP-E, and WP-TOM remains the full-physics bridge engine. Its native
  pulse is not the ideal $\sigma_z$ SDF assumed by the analytic
  inversion; see the §7#3 resolution. Therefore the first numerical
  layer is an ideal-SDF / analytic-$\chi$ validation, and the engine
  comparison is a separate bridge test of how far the Raman train
  departs from that ideal limit.
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
   at perturbative drive. The shared bridge anchor is the coherent state
   $|\alpha=3\rangle$ with motional phase zero, prepared on the +X
   quadrature in both conventions. The cross-check validates state/phase
   conventions and the native Raman bridge; it does not assert that the
   WP-E native pulse is the ideal $D(\sigma_z\beta)$ SDF of the WP-W
   inversion layer.

Out of scope for the v0.4 execution candidate:

- Lab implementation (this is a numerical WP).
- Thermal-state and decoherence sensitivity beyond a single sanity
  check.
- Squeezed-state reconstruction (a follow-up — needs the LD
  perturbation extended past the linear order).

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
- $C = e^{-|\beta|^2/2}\chi$ equivalence under the idealised
  $\sigma_z$ SDF.
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
the analytic characteristic function $\chi(\beta)$ and observable
$C(\beta)=e^{-|\beta|^2/2}\chi(\beta)$ for vacuum and coherent
$|\alpha|=1$, and stores the grid coordinates, $\chi$, and $C$.

**Output schema (`reach_ladder_ideal.h5`):**
- `/N_{n}/beta_x` (81,) — Cartesian $\beta$ coordinates
- `/N_{n}/beta_y` (81,)
- `/N_{n}/chi_real`, `/N_{n}/chi_imag` (81, 81) — analytic
  characteristic function
- `/N_{n}/C_real`, `/N_{n}/C_imag` (81, 81) — analytic contrast
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

**Native-engine extension (P1, optional):** If an `ideal_sdf` primitive
is added to `scripts/stroboscopic`, pass `--engine ideal_sdf` and the
script populates a `/N_{n}/C_engine` dataset. The residual heatmap then
becomes $|C_\text{engine} - C_\text{analytic}|/|C_\text{analytic}|$.

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
    --n-pulses 22 --delta-t 40e-9 \
    --eta 0.397 --omega-m 1.3 --omega-r 0.300 \
    --output numerics/bridge_native.json
```

**What it does:** Runs the native `scripts/stroboscopic` engine at the
Hasse nominal parameters, $N=22$, $\delta t=40$ ns, for coherent
$|\alpha=3,\theta_\alpha=0\rangle$, and extracts
$(\sigma_z, \mathrm{Re}\,C, \mathrm{Im}\,C)$ at the three tooth
centres $\delta/\omega_m\in\{-1,0,+1\}$. Compares against the WP-E
`scan_2d_alpha3_v2.h5` values at the same points.

**Output:** `numerics/bridge_native.json` — JSON with fields
`wp_e_reference`, `wp_w_native`, `residuals`.

**Pass criterion (Layer A):** Residuals $< 10^{-3}$ (numerical
tolerance) for all three observables at all three teeth.

**Panel B — Inversion bridge**

**Script:** `wp-wigner-tomography/numerics/run_bridge_inversion.py`

**Command:**
```bash
python numerics/run_bridge_inversion.py \
    --alpha 3.0 --alpha-phase-deg 0.0 \
    --template-grid ../wp-analysis-train-tomography/data/templates_sz_v1.npz \
    --beta0 0.05 --n-pulses 80 \
    --output numerics/bridge_inversion.json
```

**What it does:**
- WP-TOM side: loads the saturated-template grid, finds the nearest
  template for $|\alpha|=3$, reports refined
  $(|\alpha|_\text{tm}, \theta_\text{tm})$.
- WP-W side: runs the ideal-SDF FFT reconstruction on the same state,
  reports the centroid $(|\alpha|_\text{fft}, \theta_\text{fft})$.

**Output:** `numerics/bridge_inversion.json` — JSON with both
recoveries and their difference.

**Plot script:** `wp-wigner-tomography/plots/plot_bridge.py`
```bash
python plots/plot_bridge.py \
    --native numerics/bridge_native.json \
    --inversion numerics/bridge_inversion.json \
    --output plots/bridge_wpe_tom.png
```

**Plot output:** `plots/bridge_wpe_tom.png` — two-panel figure:
- Left: bar chart of Layer A residuals
  $(\sigma_z, \mathrm{Re}\,C, \mathrm{Im}\,C)$.
- Right: phase-space scatter showing the WP-TOM template recovery
  (saturated, orange) and WP-W FFT centroid (perturbative, blue)
  relative to the true state (black cross).

**Pass criterion (Layer B):**
$|\Delta\alpha_\text{centroid}|\leq 0.2$,
$|\Delta\theta_\alpha|\leq 0.05\pi$, no quadrant flip.

### D5 — Logbook

**Command:** None — process deliverable.

**Format:** One dated markdown file per substantive run or decision,
stored in `wp-wigner-tomography/logbook/YYYY-MM-DD-{topic}.md`.

**Required sections:**
1. Pre-registered expectations (before running any D2–D4 script).
2. Actual observations (copy of script stdout and metric values).
3. Comparison table (expectation vs. observation vs. flag).
4. Next-step decision.

**First entry template:** `logbook/2026-05-13-v0.4-preflight.md` —
records the P0 preflight outcome and the decision to proceed to D2–D3
or to debug.

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

1. Analytic prediction:
   $C_\text{ideal}(\beta_\star) =
   e^{-|\beta_\star|^2/2}\chi_{\rho_m}(\beta_\star)$.
2. P1 only: engine prediction from `scripts/stroboscopic`, after either
   implementing an ideal-SDF sequence or fitting an effective
   $\beta_\text{eff}$ bridge for the native Raman train.
3. Reconstruction sanity check: insert the analytic $\chi$ values on the
   v0.2 grid for a coherent state and verify the FFT peak lands at the
   prepared $\alpha$ within one raw $\Delta\alpha$ cell.

**Pass criteria.**

- P0 analytic-grid self-consistency: coherent-state peak position within
  one raw $\Delta\alpha$ cell and no sign flip in the phase convention.
- P1 engine-vs-analytic single point: complex residual
  $|C_\text{engine}-C_\text{ideal}|/|C_\text{ideal}| < 5\%$ at $N=20$.
  The $N=80$ comparison is diagnostic, not gating, because finite tooth
  width and non-ideal coupling can accumulate visibly over the longer
  train.

**Failure classification.** If the gate fails, classify the cause before
launching the sweep: (i) $\sigma_z$ ideal SDF vs. engine
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
    run_reach_ladder.py
    run_reconstruction_demo.py
    run_bridge_native.py
    run_bridge_inversion.py
    reach_ladder_ideal.h5
    reach_ladder_ideal.manifest.json
    reconstruction_demo.h5
    reconstruction_demo.manifest.json
    bridge_native.json
    bridge_inversion.json
  plots/                       # publication-quality figures
    plot_reach_ladder.py
    plot_reconstruction_demo.py
    plot_bridge.py
    reach_ladder_residuals.png
    reconstruction_demo.png
    bridge_wpe_tom.png
  logbook/                     # dated entries with pre-registered expectations
    2026-05-13-v0.4-preflight.md
    ...
  notes/                       # analytical derivations
    analytic_chain.md
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
3. **SDF coupling — $\sigma_z$ vs. $\sigma_x$.** *Direction resolved
   for v0.3; bridge convention pending.* The current engine does **not**
   natively realise the ideal WP-W measurement operator. The ideal chain
   assumes
   $U_\text{SDF}(\beta)=D(\sigma_z\beta)$, so spin coherence directly
   reads a displacement characteristic function. The engine implements

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
   longitudinal $\sigma_z$-conditioned displacement of the motion.

   **No limit recovers the ideal SDF.** At sideband resonance
   $\delta = +\omega_m$ — the WP-W operating point — the leading
   non-trivial term $\eta X\,\sigma_{\varphi+\pi/2}$ becomes, under the
   rotating-wave approximation, a Jaynes–Cummings coupling
   $(\eta\Omega_r/2)\!\left(a\,\sigma_{\varphi+\pi/2}^- + a^\dagger\,\sigma_{\varphi+\pi/2}^+\right)$.
   That is still **transverse** (spin-flip plus phonon-flip), not a
   longitudinal $\sigma_z$-conditioned displacement. N-pulse comb
   sharpening selects this term but does not transform it into the
   ideal SDF; the bridge between the engine and $D(\sigma_z\beta)$
   is *structural*, not a regime limit.

   Consequence: there is no standalone §2 conversion
   $\Omega_r\delta t \mapsto |\beta_0|$ for the native engine until a
   bridge convention is chosen. The v0.3 policy is to keep two numerical
   layers distinct:

   - **Ideal-SDF layer:** validate the inversion with analytic or newly
     implemented $D(\sigma_z\beta)$ pulses. This is the clean WP-W
     tomography claim.
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
   ideal-SDF bridge. Concrete v0.5 scope item, not a v0.4 blocker.

   **Deferred to a follow-up WP: GKP-lattice probe.** GKP states have
   structured phase-space negativity on the lattice scale $\sqrt{\pi/2}$,
   with sub-feature width well below the v0.2 raw
   $\Delta\alpha = 0.39$. A faithful GKP reconstruction needs
   $\Delta\alpha$ down by an order of magnitude, which means
   $\Delta\beta$ down by 10×, $N$ up by 10×, and the perturbativity
   audit $|\beta_0||\alpha|$ revisited at the larger $|\alpha|$ that
   GKP support demands. Out of WP-W's scaffold; flagged for a future
   "WP-W-GKP" if the motivation crystallises.
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
   pulse train, not the ideal-SDF surrogate: Hasse nominal parameters,
   $N=22$, $\delta t=40$ ns, $\eta=0.397$,
   $\omega_m/(2\pi)=1.300$ MHz, $\varphi_\text{train}=0$, pure coherent
   input. Compare raw $(\sigma_z,\mathrm{Re}\,C,\mathrm{Im}\,C)$ at the
   tooth centres $\delta/\omega_m\in\{-1,0,+1\}$ against the same values
   produced by the WP-E forward-map driver. This is a convention /
   provenance check and should agree to numerical tolerance if both
   wrappers call the same engine.

   **Layer B — inversion bridge.** For the same coherent state, compare
   the saturated WP-TOM template-match recovery of
   $(|\alpha|,\theta_\alpha)$ with the perturbative ideal-SDF FFT
   reconstruction centroid. Success target:
   $|\Delta\alpha_\text{centroid}| \leq 0.2$ and
   $|\Delta\theta_\alpha| \leq 0.05\pi$, with no quadrant flip. Because
   $|\alpha|=3$ sits on the edge of the v0.2 demo display window, this
   bridge plot uses $|\mathrm{Re}\,\alpha|,|\mathrm{Im}\,\alpha|\leq4$;
   the v0.2 $B=4$ / $\Delta\beta=0.10$ sampling remains unchanged.

   **Interpretation.** Passing Layer A says WP-E, WP-TOM, and WP-W are
   using the same coherent-state phase convention and native Raman
   observable. Passing Layer B says the saturated-template and
   perturbative-FFT inversions identify the same state on their
   overlapping coherent-state domain. Neither layer claims that the
   native Raman pulse has become the ideal $D(\sigma_z\beta)$ SDF; that
   separation remains the §7#3 bridge policy.

## 8. Status

**v0.1 scaffold (2026-05-13):** structure in place, regime defined,
hypothesis stated, deliverables sketched.

**v0.2 tightening pass (2026-05-13):** §2 drive scale and grid settled
for the first numerical pass: $|\beta_0|=0.05$, $N_\text{rec}=80$,
$B=4.0$, $\Delta\beta=0.10$, inverse-Dirichlet Cartesian targeting, and a
single-point preflight gate added in §4a.

**v0.3 SDF-chain pass (2026-05-13):** §7#3 direction resolved: the
native `scripts/stroboscopic` Raman pulse is not an ideal
$D(\sigma_z\beta)$ SDF, and no regime limit recovers it — the bridge is
structural. Even the sideband-resonant LD term reduces to a
Jaynes–Cummings coupling, which remains transverse. WP-W therefore
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

**Initiation handoff.** P0 + D1–D3 are ready for execution as soon as
the runner scripts of §4 / §5 are written. P1 + D4 require the
bridge-convention implementation flagged in §7#3 (leading candidate:
`ideal_sdf` primitive in `scripts/stroboscopic`). At initiation, add
the WP-W cross-reference line to [ARCHITECTURE.md](../ARCHITECTURE.md)
per §7#6, and open the first logbook entry per D5.

Outstanding non-blocking polish:

- Background citations in §Analytical (Hofheinz, Flühmann,
  Lutterbach–Davidovich, Cahill–Glauber).
- Pulse-duration $(\delta t/T_m)$ order in the approximation hierarchy
  (§Analytical bullet 5).

## References

[TBD] — add Hofheinz, Flühmann, Lutterbach–Davidovich,
Cahill–Glauber, plus the existing
[Hasse 2024 PRA reference](../refs/Hasse2024_PRA_109_053105.pdf).
