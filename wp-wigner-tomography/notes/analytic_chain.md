# WP-W D1 — Analytic chain (standalone derivation)

**WP-W · D1 · 2026-05-16**

This note derives, from first principles, exactly what the WP-W
runner scripts compute. It is **self-contained**: a reader can
re-derive the β-grid, the χ readout, and the FFT inversion without
opening `WORK-PROGRAM.md` or the source. Where the WP doc and the
code agree, this note is the bridge; where a convention was corrected
in the v0.5 doc pass, the corrected form is the one derived here.

Symbols: motional mode $a,a^\dagger$, quadrature $X=a+a^\dagger$;
displacement $D(\beta)=\exp(\beta a^\dagger-\beta^* a)$; Pauli spin
$\sigma_{x,y,z}$; Lamb–Dicke parameter $\eta$; motional frequency
$\omega_m$, period $T_m=2\pi/\omega_m$; train length $N$; per-pulse
displacement scale $\beta_0$ (taken real positive, $\arg\beta_0=0$).

-----

## 1. The ideal measurement operator: FH20-style σ_x SDF

The ideal analysis pulse is the Flühmann–Home bichromatic
state-dependent force (SDF)

$$
  U_\text{SDF}(\beta) \;=\; D\!\left(\sigma_x\,\tfrac{\beta}{2}\right)
  \;=\;\tfrac12\!\begin{bmatrix} D_{+}+D_{-} & D_{+}-D_{-}\\[2pt]
                                 D_{+}-D_{-} & D_{+}+D_{-}\end{bmatrix},
  \qquad D_{\pm}=D(\pm\beta/2),
$$

written in the engine's $[\,\text{down},\text{up}\,]$ spin blocks
using $|{\pm}x\rangle\langle{\pm}x|=(\mathbb 1\pm\sigma_x)/2$. In the
σ_x eigenbasis it is diagonal-in-spin:
$U_\text{SDF}\,|{\pm}x\rangle|\psi_m\rangle
 = |{\pm}x\rangle\,D(\pm\beta/2)\,|\psi_m\rangle$.

**Convention lock — `β` is the branch *separation*.** The
$|{+}x\rangle$ branch is displaced by $+\beta/2$ and $|{-}x\rangle$
by $-\beta/2$, so the phase-space separation of the two branches is
exactly $\beta$. This is the WP-W §2 $\beta_\text{tot}$. (The smoke
tests in `scripts/stroboscopic/tests/test_ideal_sdf.py` verify the
factor-of-two explicitly: overlap with $|{+}\beta\rangle$ must be
$<0.95$ for $|\beta|>0.6$, ruling out the $D(\sigma_x\beta)$ branch
convention.)

### 1.1 Why σ_x and not σ_z

The §3 forward map below requires the SDF axis to rotate under the
detuning-induced spin precession (which is about $\sigma_z$). A
$\sigma_z$-conditioned displacement *commutes* with that precession
and would accumulate a flat $N\beta_0$ regardless of detuning — no
Dirichlet kernel. A $\sigma_x$ (equatorial) SDF axis *does* rotate
under $\sigma_z$ precession, picking up the per-pulse phase that
builds the kernel. This is not a stylistic choice: the P1 sentinel
gives $10^{-14}$ agreement with σ_x and a **165 %** residual with σ_z
(logbook `2026-05-15-ideal-sdf-primitive.md` §3.2). The v0.4 doc
wording "$\sigma_z$-coupled" was a convention error, corrected in
v0.5.

## 2. The direct χ readout

Prepare the spin on the equator orthogonal to the SDF axis. In the
σ_x eigenbasis any such state is
$|{+}y\rangle=\tfrac1{\sqrt2}\bigl(|{+}x\rangle+e^{i\phi_0}|{-}x\rangle\bigr)$
for a fixed equatorial phase $\phi_0$ (the exact value is an
implementation convention, locked numerically below — it does not
affect the structure). With arbitrary motional input $|\psi_m\rangle$
(or mixed $\rho_m$), after one ideal SDF,

$$
  U_\text{SDF}(\beta)\,|{+}y\rangle|\psi_m\rangle
  =\tfrac1{\sqrt2}\Bigl(|{+}x\rangle\,D(\tfrac{\beta}{2})|\psi_m\rangle
        + e^{i\phi_0}\,|{-}x\rangle\,D(-\tfrac{\beta}{2})|\psi_m\rangle\Bigr).
$$

Trace out the motion. The spin coherence in the σ_x basis is

$$
  \langle{+}x|\rho_\text{spin}|{-}x\rangle
  \;\propto\; \big\langle\psi_m\big|\,
      D(-\tfrac{\beta}{2})^\dagger D(+\tfrac{\beta}{2})\,
      \big|\psi_m\big\rangle
  = \big\langle\psi_m\big|\,D(\beta)\,\big|\psi_m\big\rangle
  = \chi_{\rho_m}(\beta),
$$

using $D(-\tfrac\beta2)^\dagger=D(\tfrac\beta2)$ and
$D(\tfrac\beta2)D(\tfrac\beta2)=D(\beta)$ (the BCH cross-phase
$\exp\!\big[\tfrac12(\tfrac\beta2\tfrac{\beta^*}2-\tfrac{\beta^*}2\tfrac\beta2)\big]=1$
vanishes for collinear arguments). Here

$$
  \boxed{\;\chi_{\rho_m}(\beta)\;=\;\operatorname{Tr}\!\big[\rho_m\,D(\beta)\big]\;}
$$

is the **symmetric characteristic function** (Cahill–Glauber). Reading
out the two equatorial spin observables orthogonal to σ_x gives χ
directly,

$$
  \boxed{\;\chi_{\rho_m}(\beta)\;=\;\langle\sigma_y\rangle\;-\;i\,\langle\sigma_z\rangle\;}
$$

with **no Gaussian prefactor, no overall phase, no conjugation**.
($\langle\sigma_x\rangle$ carries no χ information — it is the SDF
axis itself.) The exact sign/phase normalisation is locked by smoke
test "lock 3" at $\le 10^{-9}$ residual on vacuum and coherent
inputs.

**Correction note (v0.5).** The earlier WP-W form
$C=\langle\sigma_x\rangle+i\langle\sigma_y\rangle=e^{-|\beta|^2/2}\chi$
is wrong on two counts: the spin pair and the $e^{-|\beta|^2/2}$
factor. The prefactor was an artefact conflated with the WP-E
Doppler-broadening contrast; the σ_x-SDF/|+y⟩ chain has no such
factor. (The runner-side function `_common.contrast_from_chi`
returning $e^{-|\beta|^2/2}\chi$ survives only as a *legacy radial-
envelope diagnostic* for the D2 reach-ladder figure, never as the
measured observable.)

## 3. The Dirichlet β-map

The train delivers $N$ ideal SDF kicks of size $\beta_0$ at period
$T_m$. Between pulses the rotating-frame SDF axis advances by the
per-gap detuning phase $x=(\delta-k\omega_m)\,T_m$ on the chosen comb
tooth $k$ ($k=0$ = carrier). Pulse $n\in[0,N)$ therefore contributes
$\beta_0\,e^{i(\varphi_\text{train}+n x)}$, and the accumulated branch
separation is the geometric sum

$$
  \beta_\text{tot}(\delta,\varphi_\text{train};N)
  =\beta_0\,e^{i\varphi_\text{train}}\sum_{n=0}^{N-1}e^{inx}
  =\beta_0\,e^{i\varphi_\text{train}}\,\mathcal D_N(x),
$$

$$
  \mathcal D_N(x)=\sum_{n=0}^{N-1}e^{inx}
   =e^{i(N-1)x/2}\,\frac{\sin(Nx/2)}{\sin(x/2)},
$$

the **Dirichlet kernel**, with $\mathcal D_N(0)=N$ (on-resonance
peak reach $|\beta_\text{tot}|_\text{max}=N\beta_0$). In the
`ideal_sdf` primitive this is implemented *exactly* as an explicit
per-pulse phase $\varphi_n=\varphi_\text{train}+n x$, with the
inter-pulse gap carrying motion only (full motional period,
identity for $t_\text{sep}=T_m$) and **no** spin detuning. Putting
the detuning into free σ_z precession in the gap instead would
contaminate the lab-frame χ readout by $(N-1)\delta T_m$; the
explicit per-pulse phase is exact at all $\beta_0$ and is the
implementation that passes P1 (logbook `…ideal-sdf-primitive` §3.2).

### 3.1 Inverse-Dirichlet Cartesian targeting

Reconstruction needs χ on a *Cartesian* β grid for the FFT, but the
physical knobs are $(\delta,\varphi_\text{train})$. Invert the map.
For a target node $\beta_\star=r\,e^{i\theta}$ with $r\le B=N\beta_0$:

1. Solve $r/\beta_0=|\mathcal D_N(x)|$ for $x$ on the **monotone
   central branch** $0\le x\le 2\pi/N$ (a 1-D root find;
   $|\mathcal D_N|$ decreases monotonically from $N$ at $x=0$ to $0$
   at $x=2\pi/N$).
2. Set the train phase, using $\arg\mathcal D_N(x)=(N-1)x/2$ on that
   branch and $\arg\beta_0=0$:

$$
  \varphi_\text{train}=\theta-\arg\beta_0-\arg\mathcal D_N(x)
                      =\theta-\tfrac{(N-1)x}{2}.
$$

3. Physical detuning offset: $\delta-k\omega_m=x/T_m$.

The central branch spans only $|\delta-k\omega_m|/\omega_m\le 1/N$ of
the chosen tooth ($\pm16.25$ kHz at $N=80$, $\omega_m/2\pi=1.3$ MHz),
which sets the scan resolution and lock-stability requirement.
Nodes with $r>B$ are unreachable on the central lobe and are
zero-filled before the FFT.

## 4. The Wigner / FFT inversion

The symmetric characteristic function and the Wigner function are a
2-D Fourier pair (Cahill–Glauber):

$$
  W(\alpha)=\frac1{\pi^2}\int e^{\alpha\beta^*-\alpha^*\beta}\,
            \chi(\beta)\,d^2\beta
          =\frac1{\pi^2}\int e^{2i(\alpha_y\beta_x-\alpha_x\beta_y)}\,
            \chi(\beta)\,d^2\beta,
$$

writing $\alpha=\alpha_x+i\alpha_y$, $\beta=\beta_x+i\beta_y$. The
**factor of 2** in the exponent is the crux of the grid relation: on
an $N_g$-point β-axis of spacing $\Delta\beta$, the conjugate α-axis
has spacing

$$
  \boxed{\;\Delta\alpha=\frac{\pi}{N_g\,\Delta\beta}\;}
$$

— *not* the textbook $2\pi/(N_g\Delta\beta)$, precisely because of
the $2i$ in the kernel. The alias-free half-width is
$\alpha_\text{Nyq}=\pi/(2\Delta\beta)$.

The discrete implementation (in `_common.wigner_from_chi`), with
$\chi$ indexed `chi[j,k]` $=\chi(\beta_x[k]+i\beta_y[j])$ (rows
= $\operatorname{Im}\beta$, cols = $\operatorname{Re}\beta$):

```
ifftshift(chi)  →  ifft(axis=1)  →  fft(axis=0)  →  fftshift
   ×  (N_g · Δβ² / π²)   →   transpose
```

- `ifft` on axis 1 ($\beta_x\!\to\!\alpha_y$, **positive** sign,
  carries the $1/N_g$);
- `fft` on axis 0 ($\beta_y\!\to\!\alpha_x$, **negative** sign);
- the $N_g\Delta\beta^2/\pi^2$ prefactor restores the continuous
  measure ($N_g$ cancels the ifft's $1/N_g$, $\Delta\beta^2$ is
  $d^2\beta$, $1/\pi^2$ is the inversion constant);
- the final transpose maps the natural FFT layout
  (rows $\alpha_x$, cols $\alpha_y$) back to the input convention
  (rows $\operatorname{Im}\alpha$, cols $\operatorname{Re}\alpha$),
  so `imshow` shows $\operatorname{Re}\alpha$ on the x-axis.

For analytically pure χ, $\max|\operatorname{Im}W|$ sits at the
`complex128` floor; a value $>10^{-10}$ flags a convention error.

### 4.1 χ for the WP-W test states

Closed forms a reader can regenerate the D3 inputs from
(`_common.chi_*`):

| state | $\chi(\beta)$ |
|---|---|
| vacuum | $e^{-|\beta|^2/2}$ |
| coherent $|\alpha\rangle$ | $e^{-|\beta|^2/2}\,e^{2i\,\operatorname{Im}(\alpha^*\beta)}$ |
| thermal $\bar n$ | $e^{-(2\bar n+1)|\beta|^2/2}$ |
| Fock $|n\rangle$ | $e^{-|\beta|^2/2}\,L_n(|\beta|^2)$ |
| even cat | $\chi_\text{diag}+\chi_\text{off}$, $\;\chi_\text{diag}=\tfrac{2}{\mathcal N^2}e^{-|\beta|^2/2}\cos\!\big(2\operatorname{Im}(\alpha^*\beta)\big)$, $\;\chi_\text{off}=\tfrac{2}{\mathcal N^2}e^{-2|\alpha|^2-|\beta|^2/2}\cosh\!\big(2\operatorname{Re}(\alpha^*\beta)\big)$ |

The cat off-diagonal `cosh` argument is **$\operatorname{Re}(\alpha^*\beta)$
(real)**, not $\alpha^*\beta$: the BCH phase $e^{-i\operatorname{Im}(\alpha^*\beta)}$
on $\langle\alpha|D(\beta)|{-}\alpha\rangle$ exactly cancels the
imaginary part, leaving χ Hermitian, $\chi(-\beta)=\chi^*(\beta)$.
Getting this wrong manifests as $\max|\operatorname{Im}W|\sim0.2$ on
the cat (it was a real bug in D3, fixed; see
`2026-05-15-D3-reconstruction.md`).

Reconstruction quality (overlap fidelity $\mathcal F=\pi\!\int
W_\text{rec}W_\text{true}\,d^2\alpha$, $L^1$, one-sided negativity
ratio) and the per-state §7#5 thresholds are deliverable D3, not part
of this derivation.

## 5. Ideal ↔ native bridge (structural, not a regime limit)

The `scripts/stroboscopic` engine does **not** natively realise
$U_\text{SDF}$. Its monochromatic Raman Hamiltonian is

$$
  H_\text{eng}=\frac{\delta}{2}\sigma_z
   +\frac{\Omega_r}{2}\big(e^{i\varphi}C\sigma_-+e^{-i\varphi}C^\dagger\sigma_+\big),
  \qquad C=e^{i\eta X},\;X=a+a^\dagger.
$$

Since $C$ commutes with the spin, the coupling is
$\tfrac{\Omega_r}{2}\big[\cos(\varphi+\eta X)\sigma_x
+\sin(\varphi+\eta X)\sigma_y\big]$, with LD expansion

$$
  \frac{\Omega_r}{2}\Big[\sigma_\varphi+\eta X\,\sigma_{\varphi+\pi/2}
   -\tfrac{\eta^2X^2}{2}\sigma_\varphi+\mathcal O(\eta^3)\Big],
  \quad \sigma_\varphi=\cos\varphi\,\sigma_x+\sin\varphi\,\sigma_y.
$$

The leading term is a carrier rotation about an equatorial axis; the
leading motional term is a *transverse* position-dependent spin
rotation. At sideband resonance $\delta=+\omega_m$ the term
$\eta X\,\sigma_{\varphi+\pi/2}$ becomes, under RWA, a Jaynes–Cummings
coupling $(\eta\Omega_r/2)(a\,\sigma^-_{\varphi+\pi/2}+a^\dagger\sigma^+_{\varphi+\pi/2})$
— still spin-flip ⊗ phonon-flip, **not** a spin-eigenstate-conditioned
displacement. N-pulse comb sharpening selects this term but never
turns it into $U_\text{SDF}$. **No limit of the monochromatic engine
recovers the ideal SDF**; the bridge is *structural*. Only a
*bichromatic* (simultaneous red+blue) drive yields the
Mølmer–Sørensen-type spin-eigenstate-conditioned displacement that
FH20 realises natively — which is exactly why WP-W supplies the ideal
chain through the `ideal_sdf` primitive rather than a regime limit of
`build_strobo_train`.

Consequence: there is no native $\Omega_r\delta t\mapsto\beta_0$
conversion. The two layers stay distinct — the **ideal-SDF layer**
(clean tomography claim, validated below) and the **native-engine
bridge** (a measured diagnostic, not a fidelity gate).

## 6. Approximation hierarchy

1. **Ideal-SDF inversion** assumes instantaneous
   $D(\sigma_x\beta/2)$ pulses, a single resolved comb tooth, fixed
   $\beta_0$. Finite $N$ enters only through the Dirichlet tooth
   width $\sim1/N$ in $\delta/\omega_m$.
2. **Perturbativity** is audited *per pulse*: $|\beta_0||\alpha|$
   ($=0.075$ at the $|\alpha|=1.5$ headline, $0.15$ at the
   $|\alpha|=3$ bridge anchor) — not $N|\beta_0||\alpha|$.
3. **Grid resolution.** At the v0.2 grid ($N_g=81$, $B=4$,
   $\Delta\beta=0.10$) the raw $\Delta\alpha=\pi/(N_g\Delta\beta)
   \approx0.39$. Fock $|2\rangle$ structure (~2 $\Delta\alpha$) is a
   resolution stress test, not a clean benchmark; a centroid
   residual below $\Delta\alpha$ is sub-pixel and *not* an engine
   defect.
4. **Native-engine departure** (LD order, pulse duration
   $\delta t/T_m$, carrier/sideband leakage) is the §5 bridge
   residual — quantified, never assumed. Pulse-duration order is
   still open ([TBD] in WP §Analytical bullet 5).

## 7. Executed residual anchors (provenance)

These four numbers pin the chain to executed artefacts. Quoted
exactly; see the dated logbooks for full tables.

| gate | what it checks | result | source |
|---|---|---|---|
| **P0** | analytic χ → FFT self-consistency (vacuum + coherent $|\alpha=1\rangle$) | vacuum $W(0)=0.636555$ vs analytic $2/\pi=0.636620$ ($\Delta=-6.5\times10^{-5}$, finite-grid windowing); coherent peak exactly on the closest grid node, value to $1$ part in $10^4$; $\max|\operatorname{Im}W|\sim10^{-16}$ | `2026-05-15-D2-and-P0.md` §3.2 |
| **P1** | engine χ readout vs analytic χ, single sentinel $\beta_\star=0.5\,e^{i\pi/4}$, vacuum + coherent $|\alpha=1\rangle$, $N\in\{20,80\}$ | relative residual $\sim1\times10^{-14}$ (machine precision; 5 % gate cleared by 13 orders) | `2026-05-15-ideal-sdf-primitive.md` §3.1 |
| **D4 Layer A** | native engine vs WP-E reference `scan_2d_alpha3_v2.h5` ($\sigma_z,\operatorname{Re}C,\operatorname{Im}C$) at three WP-E nearest-grid δ/ω_m points | max $|\Delta|=\mathbf{0.00\times10^{0}}$ (bit-exact) under the WP-E v0.9.1 convention (no separate MW π/2; $\texttt{shift\_deg}=\omega_m\delta t/2$; $N=30$) | `2026-05-15-D4-bridge.md` §3.1 |
| **D4 Layer B** | engine-measured χ (ideal-SDF) vs analytic χ over the $81^2$ fine grid at $|\alpha=3,\theta_\alpha=0\rangle$ | max $|\chi_\text{engine}-\chi_\text{analytic}|=\mathbf{3.75\times10^{-4}}$ over 6481 nodes (canonical bridge metric; the $1.99\times10^{-2}$ FFT-centroid residual is sub-pixel at $\Delta\alpha=0.39$) | `2026-05-15-D4-bridge.md` §3.2 |

P0 validates §4 (FFT/Wigner convention). P1 validates §1–§2 (σ_x
SDF + direct χ readout, single point). D4 Layer A validates the
native-engine provenance (§5). D4 Layer B validates §1–§3 over the
*full* reconstruction grid — it is the load-bearing bridge number.
The centroid residual is reported only with its $\Delta\alpha$ pixel
size attached, never as a bare gate (§6 point 3).

-----

*Source of truth for conventions: `WORK-PROGRAM.md` §Analytical /
§2 / §7#3 as corrected in the v0.5 doc pass. This note derives the
runner behaviour; it does not introduce new design decisions.*
