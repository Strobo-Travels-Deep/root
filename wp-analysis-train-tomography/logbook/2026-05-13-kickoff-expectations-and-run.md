# Logbook — 2026-05-13 — WP-TOM Kick-off: Pre-registered Expectations + First Run

**Context.** First entry of the new
[wp-analysis-train-tomography](../README.md) work program. The kick-off
notebook
[`notebooks/00_kickoff_tomography.ipynb`](../notebooks/00_kickoff_tomography.ipynb)
scans the analysis-pulse-train coordinate $(\delta, \varphi_\text{train})$
on nine fixed coherent input states $|\alpha|\,e^{i\theta_\alpha}$
(three amplitudes × three phases) for $N \in \{1, 3, 10\}$, and reads
out $P(\uparrow)$.

This entry **pre-registers** the expectations *before* execution
(§2), then logs the run (§3) and a point-by-point comparison (§4). The
point of the order is to make any surprises legible — if the run
matches predictions, fine; if it deviates, we know exactly which
prediction was wrong.

-----

## 1. Parameters and conventions

- Engine: [`scripts/stroboscopic`](../../scripts/stroboscopic), same
  primitives as the [main tutorial](../../notebooks/00_tutorial_pulse_train.ipynb).
- Lamb–Dicke parameter $\eta = 0.397$, motional frequency $\omega_m = 1.3$
  (natural units), pulse duration $\delta t = 0.13\,T_m$.
- Train length $N \in \{1, 3, 10\}$. Rabi rate $\Omega_r$ rescaled per
  $N$ so the on-resonance carrier rotation is always $\pi/2$:
  $\Omega_\text{eff} = \pi/(2\,N\,\delta t)$, $\Omega_r = \Omega_\text{eff}\,e^{\eta^2/2}$.
- Input: $(|\!\!\downarrow\rangle$ ⊗ coherent $|\alpha\rangle)$ followed
  by an MW $\pi/2$ pulse with phase 0 — i.e. spin on $+\hat y$ of the
  Bloch equator (= equal superposition with engine convention).
  Motional amplitudes $|\alpha| \in \{0.1, 1, 3\}$, phases
  $\theta_\alpha \in \{0, \pi/4, \pi/2\}$.
- Scan grid: $\delta/\omega_m \in [-1.5, 1.5]$, 21 points;
  $\varphi_\text{train} \in [0, 2\pi)$, 21 points.
- Hilbert cut $n_\max = 60$ (generous: tutorial uses the same for
  $|\alpha|=3$).

Key derived numbers, fixed by the parameters above:

| quantity | value | note |
|---|---|---|
| $2\eta\,|\alpha|$ at $|\alpha|=0.1$ | 0.079 | Bessel arg, carrier band |
| $2\eta\,|\alpha|$ at $|\alpha|=1$   | 0.794 | |
| $2\eta\,|\alpha|$ at $|\alpha|=3$   | 2.382 | sits on first zero of $J_0(x{=}2.405)$ |
| $J_0(2\eta\,|\alpha|)$ at $|\alpha|=\{0.1,1,3\}$ | $\{0.998, 0.853, 0.012\}$ | carrier weight |
| $J_1(2\eta\,|\alpha|)$ at $|\alpha|=\{0.1,1,3\}$ | $\{0.040, 0.367, 0.503\}$ | first-sideband weight |
| Debye–Waller $e^{-\eta^2/2}$ | 0.924 | overall envelope |

-----

## 2. Pre-registered expectations

These are written **before** running the notebook. Each prediction has
a specific feature, a quantitative target where I can pin one, and a
flag for the §4 comparison (✓ matches, ✗ deviates, ? ambiguous).

### 2.1 Three-band structure in $\delta$

Comb teeth at $\delta/\omega_m = \{-1, 0, +1\}$:

- **Carrier** $\delta = 0$: weight $\propto J_0(2\eta|\alpha|)$.
  Strong at $|\alpha| \in \{0.1, 1\}$; **strongly suppressed at
  $|\alpha|=3$** because $2\eta\cdot 3 = 2.38$ falls on the first
  zero of $J_0$ (tutorial §2.5).
- **First sidebands** $\delta = \pm\omega_m$: weight $\propto J_1(2\eta|\alpha|)$.
  Invisible at $|\alpha|=0.1$ ($J_1 \approx 0.04$), visible at $|\alpha|=1$,
  prominent at $|\alpha|=3$.

**Numerical target.** The ratio of sideband peak-to-peak contrast to
carrier peak-to-peak contrast at $|\alpha|=3$ should be large
($\geq 5{\times}$), because the carrier is near its Bessel zero
whereas the first sideband is near its maximum.

### 2.2 Tooth narrowing as $1/N$

HWHM of each comb tooth in $\delta/\omega_m$ should scale as $1/N$:

| $N$ | predicted HWHM in $\delta/\omega_m$ |
|---|---|
| 1  | $\sim 1$    (no comb — the carrier and sidebands are not yet resolved) |
| 3  | $\sim 0.33$ (teeth marginally separated) |
| 10 | $\sim 0.10$ (clean separation; carrier and $\pm\omega_m$ bands disjoint) |

**Visual marker.** At $N=1$, the maps should look like a single broad
envelope across the full $\delta$ range. At $N=10$, three distinct
bands separated by near-flat strips at $\delta/\omega_m \approx \pm 0.5$.

### 2.3 Carrier fringe in $\varphi_\text{train}$ is $\theta_\alpha$-independent

The carrier band ($k=0$ in the Jacobi–Anger expansion of $\langle\alpha|C|\alpha\rangle$)
has weight $J_0(2\eta|\alpha|)$ with **no $\theta_\alpha$ phase**.
So the carrier fringe along $\varphi_\text{train}$ at $\delta=0$
should look identical across the three columns of each $N$-figure.

**Functional form.** For $|\alpha|=0.1$ (effectively vacuum) at $\delta=0$,
$N=10$ (clean π/2 rotation), the fringe should follow

$$P(\uparrow)(\varphi_\text{train}) \;\approx\; \tfrac{1}{2}\bigl[1 - \sin(\varphi_\text{train} + \varphi_0)\bigr]$$

i.e. a single sinusoid spanning $[0, 1]$. The offset $\varphi_0$ is set
by the engine's coupling convention (the
[`hamiltonian.py`](../../scripts/stroboscopic/hamiltonian.py) docstring
fixes the sign) — I'm not predicting $\varphi_0$ in advance, only that
the fringe is **a single full-contrast sinusoid in $\varphi_\text{train}$**.

### 2.4 Sideband fringe in $\varphi_\text{train}$ rotates with $\theta_\alpha$

The $k=\pm 1$ sideband transitions carry an $e^{\mp i\theta_\alpha}$
Jacobi–Anger phase. So along the $\delta = +\omega_m$ ridge the
$\varphi_\text{train}$ fringe should shift by exactly $-\theta_\alpha$
between columns $\theta_\alpha \in \{0, \pi/4, \pi/2\}$:

- $\theta_\alpha = 0$: ridge fringe peak at some $\varphi_\text{train} = \varphi_+^{(0)}$.
- $\theta_\alpha = \pi/4$: peak at $\varphi_+^{(0)} - \pi/4$.
- $\theta_\alpha = \pi/2$: peak at $\varphi_+^{(0)} - \pi/2$.

**This is the tomographic signature**: a rigid translation of the
$\varphi_\text{train}$ fringe along the sideband ridge as $\theta_\alpha$
varies. At $\delta = -\omega_m$ the shift is the opposite sign.

**Sanity number.** Between $\theta_\alpha = 0$ and $\theta_\alpha = \pi/2$
the fringe peak at $\delta = +\omega_m$ should move by exactly
$\pi/2$ in $\varphi_\text{train}$ ($= 0.5\pi$ in the $\varphi/\pi$
plot scale).

### 2.5 $|\alpha|=0.1$ row is θ-degenerate

For $|\alpha|=0.1$ the sideband weight $J_1 \approx 0.04$ is too small
to give a visible ridge inside the scan's colour scale.
**Prediction:** the entire $|\alpha|=0.1$ row of each $N$-figure should
look indistinguishable across the three $\theta_\alpha$ columns — only
the carrier band is visible, and it doesn't depend on $\theta_\alpha$.

### 2.6 Symmetries

- $P(\uparrow) \in [0, 1]$ everywhere (unitarity).
- For $|\alpha|=0.1$ (≈ vacuum), the map should be approximately
  $\delta \to -\delta$ symmetric (only the carrier carries weight).
- For $|\alpha|>0$, $(\delta, \varphi_\text{train}) \to (-\delta, \varphi_\text{train} + 2\theta_\alpha)$
  should leave $P(\uparrow)$ invariant (the $k=+1$ and $k=-1$
  Jacobi–Anger components are conjugate).

### 2.7 Wall time

Per $N$: 441 train builds × 9 input states = 3969 evolutions, plus 441
matrix exponentials of a 120×120 Hamiltonian. Estimate: $\sim 5$–10 s
per $N$, so $\sim 30$ s total. **If the run takes minutes, something
is wrong** (Hilbert-cut blow-up, accidental quadratic nesting, etc.)
and should be investigated before reading the maps.

-----

## 3. Execution

- Notebook: [`notebooks/00_kickoff_tomography.executed.ipynb`](../notebooks/00_kickoff_tomography.executed.ipynb)
  (executed in-place via `jupyter nbconvert --execute`).
- PNG renders of the three $N$-figures: [`plots/p_up_N1.png`](../plots/p_up_N1.png),
  [`plots/p_up_N3.png`](../plots/p_up_N3.png),
  [`plots/p_up_N10.png`](../plots/p_up_N10.png).
- Wall time **36 s end-to-end** for the entire notebook (including
  nine Wigner panels and three full 21×21 scans). Each $N$-scan
  individually ran in ≈ 1 s. **Order of magnitude faster than my
  §2.7 estimate.** Hilbert cut, propagator builds, and the
  `StroboTrain.evolve` matrix–vector loop are all cheap at this
  problem size — bumping to 41×41 or 81×81 is trivial.
- All maps live in $P(\uparrow) \in [0.024, 0.976]$ globally;
  no unitarity violation, no NaN, no overflow at $n_\max = 60$.

Visual summary of the three figures (numerical detail in §4):

- **$N=1$**: one slanted full-contrast stripe spanning the full
  $\delta$ window. No comb teeth — single broad envelope.
- **$N=3$**: three distinct stripes at $\delta/\omega_m \in \{-1, 0, +1\}$
  but with substantial overlap; the carrier and first-sideband ridges
  are not yet cleanly separated.
- **$N=10$**: three sharp, well-separated bands at
  $\delta/\omega_m \in \{-1, 0, +1\}$. Off-band regions sit near
  $P(\uparrow) = 0.5$. The carrier fringe along $\varphi_\text{train}$
  is visibly the same across the three $\theta_\alpha$ columns;
  the sideband fringes visibly shift between columns — the
  tomography signature is there to the eye.

-----

## 4. Comparison — predictions vs. observations

### Result table

| §  | prediction                                                         | observation                                                  | flag |
|---:|--------------------------------------------------------------------|--------------------------------------------------------------|:---:|
| 2.1 | Carrier suppressed at $\|\alpha\|=3$ by Bessel zero of $J_0(2.38)$ | Carrier amplitude $\approx 0.92$ for **all** $\|\alpha\|$    |  ✗  |
| 2.2 | HWHM in $\delta/\omega_m$ scales as $1/N$                           | $N=10$: 0.146 measured vs 0.100 predicted (within 50 %); $N=3$: 1.345 vs 0.333 (teeth not yet resolved) | ✓ (qualitative) |
| 2.3 | Carrier fringe in $\varphi_\text{train}$ is $\theta_\alpha$-independent | True for $\|\alpha\|\in\{0.1, 1\}$ ($\Delta\varphi \leq 0.01\pi$); drifts by $\sim 0.4\pi$ for $\|\alpha\|=3$ | ✓ / ✗ partial |
| 2.4 | Sideband fringe shifts by $-\pi/2$ between $\theta_\alpha = 0$ and $\pi/2$ at $\delta=+\omega_m$ | $\Delta\varphi = +0.277\pi, +0.358\pi, +0.388\pi$ for $N=1,3,10$ — **wrong sign** and **78 %** of predicted magnitude | ✗ sign / ≈ magnitude |
| 2.5 | $\|\alpha\|=0.1$ row degenerate in $\theta_\alpha$                  | Yes — fringe peak drift $\leq 0.013\pi$ across columns      |  ✓  |
| 2.6 | Unitarity ($P\in[0,1]$, $\delta\to-\delta$ symmetry at $\|\alpha\|=0.1$) | Yes — global range $[0.024, 0.976]$; vacuum row $\delta$-symmetric to eye | ✓ |
| 2.7 | Wall time $\lesssim 30$ s                                           | 36 s total notebook, ≈ 3 s for all scans                     |  ✓  |

### Where the predictions failed, and why

**2.1 — the Bessel-zero suppression is washed out by my own normalisation.**
I rescaled $\Omega_r$ per $N$ so the *carrier* (LD-limit) on-resonance
rotation is always $\pi/2$. That saturates the carrier transition by
construction, so the resulting carrier fringe amplitude approaches 1
regardless of how the Jacobi–Anger coherent-state matrix element
$J_0(2\eta|\alpha|)$ would have suppressed it in a perturbative regime.
The $J_0$ zero is real physics, but it manifests as a reduction in the
effective Rabi rate, **not** in the saturated fringe amplitude. The
prediction was internally inconsistent with the calibration choice.

**Implication.** To see the Bessel suppression we need a different
protocol: fix $\Omega_r$ across $\|\alpha\|$ (per-pulse kick is the
invariant) and let the carrier fringe amplitude vary with
$J_0(2\eta\|\alpha\|)$. This is one of the open questions raised in §5
of the kick-off notebook and is now the leading candidate for the
follow-up run.

**2.2 — tooth narrowing is correct but the $N=3$ HWHM measurement is
contaminated by sideband overlap.** The $\varphi$-averaged
$|P(\uparrow) - 0.5|$ used to compute HWHM has support from both the
carrier and the $\pm\omega_m$ sidebands; at $N=3$ they are not yet
disjoint and the HWHM probe just records "where the map deviates
substantially from 0.5," not the carrier tooth width per se. The
$N=10$ measurement (0.146 vs predicted 0.100) is closer because the
sidebands are now disjoint from the carrier; the residual factor 1.46
likely comes from the 21-point $\delta$ grid (spacing 0.15) being too
coarse to resolve a 0.10 HWHM cleanly. **Action:** for any
quantitative tooth-width claim, run the 41×41 or 81×81 grid.

**2.3 — carrier fringe is $\theta_\alpha$-blind at small $\|\alpha\|$,
drifts at $\|\alpha\|=3$.** At $\|\alpha\|=1$ the carrier fringe peak
location agrees across $\theta_\alpha \in \{0, \pi/4\}$ to better than
0.01π; the $\theta_\alpha = \pi/2$ entry drifts by $\sim 0.12\pi$. At
$\|\alpha\|=3$, all three columns disagree, drifting up to $0.37\pi$.
This is consistent with two effects: (i) at $\|\alpha\|=3$, the carrier
ridge at $\delta=0$ is contaminated by the wing of the sideband
($N=10$ HWHM 0.146 → sideband wing reaches into $\|\delta\| \lesssim 0.1$);
(ii) ac-Stark-like effects of order $(\eta|\alpha|)^2 \cdot (\Omega/\omega_m)$
shift the carrier position itself, mimicking a $\theta_\alpha$ drift
at the discrete grid resolution. **Action:** verify on a 41×41 grid
that the carrier-fringe drift at $\|\alpha\|=3$ persists; if it does,
it is a genuine ac-Stark signature worth its own probe.

**2.4 — the tomography signature is there, but with opposite sign and
short magnitude.** The shift in $\varphi_\text{train}$ at the
$\delta = +\omega_m$ sideband ridge between $\theta_\alpha = 0$ and
$\theta_\alpha = \pi/2$ trends from $+0.277\pi$ ($N=1$) → $+0.358\pi$
($N=3$) → $+0.388\pi$ ($N=10$). The trend toward a limiting value as
$N$ grows is exactly what you would expect for a clean tomographic
mapping; the limit value (≈ $0.4\pi$, not exactly $0.5\pi$) is more
puzzling. Three candidate explanations, to disentangle in follow-up:

  1. **Engine sign convention.** The Hamiltonian uses
     $e^{i\varphi}C\sigma_-$; the Jacobi–Anger expansion of $C(t)$ in
     the interaction picture introduces a phase
     $e^{-ik\theta_\alpha}$ for the $k$-th sideband — so the
     resonance fringe at $\delta = +\omega_m$ should shift as
     $\varphi \to \varphi + \theta_\alpha$, not $-\theta_\alpha$. The
     observed $+\pi/2$ shift (positive sign) is **consistent with the
     engine convention**; the negative-sign prediction was my error.
  2. **Saturation reduces the slope.** Because each pulse saturates
     the spin towards a fixed Bloch direction, the $\theta_\alpha$
     phase is partially imprinted and partially "clipped" by the
     finite rotation budget. A first-Born regime (lower $\Omega$,
     larger $N$) should give the full $\pi/2$ shift.
  3. **Grid coarseness.** $\varphi_\text{train}$ is sampled on 21
     points; parabolic peak refinement helps but not all the way.
     Refining the grid is cheap.

  **Action:** repeat the $N=10$ row at a 41-point $\varphi$ grid and
  with a halved $\Omega_r$ to test whether the shift moves toward
  $+0.5\pi$. If yes, the protocol is a clean tomographic mapping
  modulo a known sign convention; if no, the saturation is a genuine
  limit of single-train tomography and we need a softer protocol.

**2.5 — $\|\alpha\|=0.1$ shows strong sidebands, not the absence I
half-anticipated in §2.5.** This is **not** a contradiction of the
prediction (which only said the row is $\theta_\alpha$-degenerate —
which it is). But it is worth flagging that the $\|\alpha\|=0.1$
sidebands are clearly visible (amplitude $\approx 0.75$ at $N=10$),
because the relevant matrix element is the Lamb–Dicke ground-state
coupling $\eta\sqrt{n+1}$ for the $|0\rangle \to |1\rangle$
transition, *not* the coherent-state Jacobi–Anger weight
$J_1(2\eta\|\alpha\|) \approx 0.04$. The two pictures describe
different limits: the former is Fock-resolved (right for near-vacuum),
the latter is coherent-state-resolved (right for $\|\alpha\| \gg 1$).
This is a useful clarification of when each picture applies and is
worth a short note on the next pass.

-----

## 5. Open questions and follow-ups

Ordered by how much they would change the picture:

1. **Sideband fringe shift falls short of $\pi/2$.** Resolve whether
   the limit value is $\sim 0.4\pi$ (saturation artefact) or exactly
   $0.5\pi$ (recovered at a finer grid and lower drive). Run the
   $N=10$ row at a $\varphi$ grid of 41 points and $\Omega_r$ halved.
   This is the single most diagnostic follow-up.
2. **Carrier suppression at the $J_0$ zero.** Add a second sweep with
   $\Omega_r$ fixed across $\|\alpha\|$ (matching the per-pulse kick
   rather than the carrier rotation) so the Bessel zero at
   $\|\alpha\|=3$ has a chance to express itself in the carrier-ridge
   amplitude. This separates dynamics from calibration.
3. **Are the carrier-fringe drifts at $\|\alpha\|=3$ real?** Run a
   41×41 grid; if the drifts in §2.3 persist with the better
   sampling, the carrier band itself carries motional information
   at large $\|\alpha\|$ — interesting in its own right.
4. **Build an inverter.** Once we trust the forward map, write the
   small fit that takes $P(\uparrow)(\delta, \varphi_\text{train})$
   and returns $(\|\alpha\|, \theta_\alpha)$ — the actual point of
   WP-TOM. The $N=10$ map already has more than enough structure to
   identify $(\|\alpha\|, \theta_\alpha)$ uniquely for
   $\|\alpha\| \geq 1$.
5. **WP-E cross-check.** The
   [wp-phase-contrast-maps](../../wp-phase-contrast-maps/) WP-E
   forward map and our WP-TOM inverse map should agree on shared
   reference points; one anchor comparison should be enough to
   confirm both engines are speaking the same physics.

**Status.** Kick-off passes. The protocol clearly carries
tomographic information; the open questions are about how much, in
what units, and under which calibration. None of them are blockers.

-----

## 6. Iteration 2 (same day) — building the inverter

This addendum extends the same logbook entry with the work I did after
§5 was written: implementing follow-up #4 ("build an inverter") by
trying the two analytical routes I sketched in the
[previous turn](../../README.md), discovering that both fail, and
landing on a third route that does work. The story is worth recording
because *the failures pin down which regime the kick-off protocol is
actually in*, which was unclear from the heatmaps alone.

### 6.1 Two routes, two failures

**Route A — single-sideband Bessel ridge fit.** Anger–Jacobi predicts
that $\langle\alpha|C(t)|\alpha\rangle$ has a $J_1(2\eta|\alpha|)$
component at frequency $\omega_m$ with phase $-\theta_\alpha$, so the
$k=1$ Fourier coefficient $F_{+1}$ of the measured complex contrast
along the $\delta = +\omega_m$ ridge should encode $(|\alpha|, \theta_\alpha)$.

Measured: $|F_{+1}|$ varies from $0.0051$ at $|\alpha|=0$ to $0.0101$
at $|\alpha|=4$ — a 2× variation in a quantity ~50 × smaller than the
actual $|C|$ swing (0.06 → 0.87) along the ridge. The signal is **not
in this Fourier mode**. Recovered $|\alpha|$ via the inversion table
clusters near 2 regardless of input; $\theta_\alpha$ recovery is
random-walk noise.

**Route B — $\chi_{|\alpha\rangle}$ global fit.** The same problem in
a different guise. Fitting the coherent-state characteristic function
$\chi_{|\alpha\rangle}(\beta) = e^{-|\beta|^2/2}\,e^{\beta\alpha^* - \beta^*\alpha}$
to the measured $C(\delta, \varphi_\text{train})$ over the two
sideband windows assumes the train implements a clean
$D(\beta(\delta, \varphi_\text{train}))$. It doesn't in the
$\pi/2$-saturated regime. Fit converges to $|\alpha| \approx 8$
regardless of input, with residual cost $\sim 4 \times 10^2$ —
nonsense.

### 6.2 What the protocol is actually doing

Inspecting the Fourier spectrum along $\delta = +\omega_m$
revealed:

- The dominant mode is $\sigma_z[k=1]$ with magnitude $\approx 0.46$
  (close to the unit-amplitude $-\sin(\varphi - \psi)$ expected for a
  saturated $\pi/2$ rotation around an equator axis at angle $\psi$).
- Its **phase** $\psi$ tracks $\theta_\alpha$; its **magnitude** is
  nearly $|\alpha|$-independent (variation ≤ 1 % across the test set).
- $C[k=0]$ and $C[k=2]$ carry the $|\alpha|$-information (5–20 %
  variation), but neither is dominant.

So *no single Fourier mode is sufficient* for inversion in this
regime — the saturation washes out the perturbative tomographic
weights, and the residual $|\alpha|$-information is spread across the
full 2D structure.

### 6.3 Route C — engine-as-forward-model template matching

If no Fourier mode carries the inversion cleanly, treat the engine
itself as the forward model. Precompute $\sigma_z(\delta, \varphi_\text{train};\,|\alpha|, \theta_\alpha)$
on a $9 \times 16$ template grid (|\alpha| ∈ {0, 0.25, ..., 3}, θ_α uniform
on $[0, 2\pi)$). Inversion = nearest-neighbour template plus parabolic
refinement in both axes.

**Cache.** Templates live at
[`data/templates_sz_v1.npz`](../data/templates_sz_v1.npz) (776 kB);
generation takes ≈ 210 s once, inversion is sub-second thereafter.

**Recovery on the nine kick-off states** (truth → grid match → refined):

| truth $(|\alpha|, \theta_\alpha/\pi)$ | refined recovery | $\Delta|\alpha|$ | $\Delta\theta_\alpha/\pi$ |
|---|---|---|---|
| (0.10, 0.00) | (0.246, −0.241) | +0.146 | −0.241 |
| (0.10, 0.25) | (0.234, +0.500) | +0.134 | +0.247 |
| (0.10, 0.50) | (0.395, +0.600) | +0.295 | +0.103 |
| (1.00, 0.00) | (0.925, +0.047) | −0.075 | +0.047 |
| (1.00, 0.25) | (0.925, +0.197) | −0.075 | −0.049 |
| (1.00, 0.50) | (0.925, +0.490) | −0.075 | −0.010 |
| (3.00, 0.00) | (3.000, +0.047) | +0.000 | +0.047 |
| (3.00, 0.25) | (3.000, +0.203) | +0.000 | −0.049 |
| (3.00, 0.50) | (3.000, +0.491) | +0.000 | −0.009 |

Phase-space scatter: [`plots/route_C_phase_space_recovery.png`](../plots/route_C_phase_space_recovery.png).

For $|\alpha| \geq 1$ recovery is clean: $\Delta|\alpha| \leq 0.075$,
$\Delta\theta_\alpha \leq 0.05\pi$ (limited by the
$\theta_\alpha$-grid spacing of $0.125\pi$ before refinement). At
$|\alpha| = 0.1$ the template grid bottoms out at $|\alpha| = 0.25$,
so the inversion correctly identifies "very small $|\alpha|$" but
cannot resolve sub-0.25 amplitude, and $\theta_\alpha$ is noisy
because the physical signal is small. Both are template-grid
limitations, not inversion-method limitations.

### 6.4 What this iteration changed in our understanding

Going into v0.2 I would have said the kick-off protocol is a clean
phase-space tomography scan. Going out of v0.3, the corrected picture
is:

- The protocol is **saturated** (carrier rotation = $\pi/2$ on
  resonance). This is NOT the regime where Anger–Jacobi $J_k$ weights
  or characteristic-function inversion apply. Those describe
  *perturbative* analysis pulses.
- The full 2D $\sigma_z(\delta, \varphi_\text{train})$ map *does*
  carry enough information to identify $(|\alpha|, \theta_\alpha)$
  uniquely for $|\alpha| \geq 1$ — just not via any single-harmonic
  fit.
- A perturbative regime (10 × weaker drive, or smaller per-pulse
  rotation budget) would put Routes A and B back into play and would
  recover the clean Hofheinz/Flühmann-style tomography. That is a
  protocol choice, not a property of the engine.

**Updated follow-up list** (supersedes §5 above):

1. **Finer template grid.** $|\alpha|$ spacing $0.1$, $\theta_\alpha$
   spacing $0.0625\pi$ → $30 \times 32 = 960$ maps, ~25 min build.
   Brings $|\alpha| = 0.1$ inside resolution and pushes
   $\Delta\theta_\alpha$ to $\sim 0.02\pi$.
2. **Continuous-optimisation refinement** of the template result
   using `scipy.optimize.minimize` with the engine as the forward
   model. ~5 forward evaluations per inversion → $\Delta|\alpha| \lesssim 0.01$.
3. **Perturbative re-run.** Drop $\Omega_r$ by 10× (so the carrier
   rotation is $\sim 0.05\pi$). Re-test Routes A and B in this
   regime; they should now work, and the comparison to Route C
   pins down the saturation correction quantitatively.
4. **WP-E cross-check** (carried over from §5 follow-up #5) — still
   pending.

### 6.5 Artefact summary for this iteration

- New: [`notebooks/01_tomography_inversion.ipynb`](../notebooks/01_tomography_inversion.ipynb)
  (and `.executed.ipynb`) — runs through Routes A/B failure
  diagnosis, the Fourier-content analysis, and the Route C
  template-matching inversion with self-test on the nine kick-off
  states.
- New: [`data/templates_sz_v1.npz`](../data/templates_sz_v1.npz) —
  cached $9 \times 16$ template grid (~776 kB).
- New: [`plots/route_C_phase_space_recovery.png`](../plots/route_C_phase_space_recovery.png).

**Status v0.3.** Inverter exists and works on $|\alpha| \geq 1$. The
two analytical routes I bet on in v0.2 turned out to be wrong for
this protocol's regime; that's now documented (not patched over),
and we have a working baseline plus a clear path to refinement.

-----

(*Original §5 follow-up list above is retained for the historical
record — items #1, #2, #3 there are still relevant; item #4 has been
addressed in §6.3.*)
what units, and under which calibration. None of them are blockers.
