# Analytic reference — WP-Coastline

**Status:** v0.1 · 2026-04-21. Two closed-form lemmas that anchor
numerical findings of WP-C v0.1 and the subsequent α-recovery / Doppler
probes. Verified numerically by
[verify_analytic.py](../numerics/verify_analytic.py) against
[coastline_v1.h5](../numerics/coastline_v1.h5) and
[coastline_doppler_v1.h5](../numerics/coastline_doppler_v1.h5).

-----

## 1. Setup and notation

Single mode $a, a^\dagger$, single spin $\sigma_{x,y,z}$. Coupling
operator as stored in
[scripts/stroboscopic/operators.py:23](../../scripts/stroboscopic/operators.py#L23):

$$
C = \exp\!\bigl[i\eta(a + a^\dagger)\bigr] = D(i\eta),
$$

i.e. the displacement operator by a pure-imaginary amount $i\eta$. The
per-pulse Hamiltonian as used in
[scripts/stroboscopic/hamiltonian.py:42](../../scripts/stroboscopic/hamiltonian.py#L42)
(at detuning $\delta = 0$, ac phase $\varphi = 0$):

$$
H_\text{pulse} = \omega_m\, a^\dagger a + \tfrac{\Omega}{2}\,(C\,\sigma_- + C^\dagger\,\sigma_+).
$$

The strobe train consists of $N$ pulses of duration $\delta t$
separated by gaps of length $T_\text{gap} = T_m - \delta t$ where
$T_m = 2\pi/\omega_m$. The coherent-state initial condition with phase
$\vartheta_0$ is

$$
|\psi_0\rangle = |\!\downarrow\rangle\otimes|\alpha e^{i\vartheta_0}\rangle
\quad\xrightarrow{\text{MW }\pi/2\text{ at }\phi=0}\quad
\tfrac{1}{\sqrt 2}\bigl(|\!\downarrow\rangle + i|\!\uparrow\rangle\bigr)\otimes|\alpha e^{i\vartheta_0}\rangle.
$$

The observables are $\sigma_x, \sigma_y$, and from them
$|C|(\vartheta_0) \equiv \sqrt{\langle\sigma_x\rangle^2 + \langle\sigma_y\rangle^2}$,
the spin coherence after the train. The coastline observables are

$$
V = 1 - \min_{\vartheta_0} |C|(\vartheta_0),
\qquad
P(\delta) = \langle|C|(\vartheta_0)\rangle_{\vartheta_0}\big|_\delta.
$$

-----

## 2. Lemma A — Stroboscopic motional heterodyne

**Claim.** For strobe-gap duration $T_\text{gap} = T_m$ (i.e.
$t_\text{sep} = T_m$, exactly one motional period between pulses), the
motional component of the gap propagator is the identity on the Fock
basis. Consequently, at $\delta = 0$, the entire gap is the identity,
and the train propagator reduces to $U_\text{train} = K^N$ where $K$
is the single-pulse propagator. Any Doppler-broadening that a single
pulse experiences within its own $\delta t$ window is therefore
**not** amplified by accumulation over $N$ pulses — it is cancelled
exactly by the motional-period sampling.

**Proof.** The gap propagator at $\delta = 0$ (see
[scripts/stroboscopic/propagators.py:41](../../scripts/stroboscopic/propagators.py#L41))
is diagonal in the Fock basis with entries $e^{-i\omega_m n t}$ for
$n = 0, 1, \ldots, N_\text{max}-1$. At $t = T_\text{gap} = T_m =
2\pi/\omega_m$, every phase equals $-2\pi n$, which is a multiple of
$2\pi$ for all integer $n$. Hence $U_\text{gap}|_{t=T_m} = \mathbb{1}$.
The full train is

$$
U_\text{train} = K \cdot \underbrace{\mathbb{1}}_{U_\text{gap}} \cdot K \cdot \mathbb{1} \cdots K = K^N.
$$

At $\delta \ne 0$, the gap propagator carries an extra spin-frame
phase $e^{\pm i\delta T_m/2}$ on the two spin blocks — this contributes
$(N-1)\cdot\delta T_m$ of spin rotation across the train but does **not**
depend on $\alpha$. ∎

**Consequence for the Doppler probe.** Because $K$ itself depends on
$\alpha$ only through the action of $C$ on the coherent state (which
at $\delta = 0$ gives no Doppler broadening proper — see Lemma B),
the entire $\alpha$-dependence of $V$ lives in $K^N$, and crucially
in the **intra-pulse** structure of $K$. This is why the v0.1.1
Doppler probe found
$P_\text{mid,min} \geq 0.999$ everywhere: there is nothing in the
gap to Doppler-broaden, and the off-tooth coherence at $\delta \ne 0$
simply rotates the spin by an $\alpha$-independent amount.

-----

## 3. Lemma B — Impulsive-limit $V$ floor

**Claim.** In the exact impulsive limit $\delta t \to 0$ at fixed
total rotation $N \cdot A = \pi/2$ (where $A$ is the dimensionless
per-kick area), and with $t_\text{sep} = T_m$, the tooth visibility
for a coherent state $|\alpha e^{i\vartheta_0}\rangle$ is

$$
V_\text{imp} \;=\; \tfrac{1}{2}\bigl(1 + e^{-2\eta^2}\bigr),
$$

**independently of $\alpha$ and $N$**, provided
$\eta|\alpha| \gtrsim \pi/4$ so that the $\vartheta_0$ sweep covers a
full period of the interference factor.

**Derivation.** In the impulsive limit $\delta t \to 0$, $\omega_m
\delta t \to 0$, so intra-pulse motion is frozen and the per-kick
unitary is

$$
K = \exp\!\left[-i\tfrac{A}{2}\begin{pmatrix}0 & C\\ C^\dagger & 0\end{pmatrix}\right].
$$

Since $\bigl(\begin{smallmatrix}0 & C\\ C^\dagger & 0\end{smallmatrix}\bigr)^2 = \mathbb{1}$ (as $CC^\dagger = \mathbb{1}$), the matrix exponential evaluates exactly:

$$
K = \cos(A/2)\,\mathbb{1} - i\sin(A/2)\begin{pmatrix}0 & C\\ C^\dagger & 0\end{pmatrix}.
$$

Under Lemma A, $U_\text{train} = K^N$. At fixed $N \cdot A = \pi/2$,
in the large-$N$ (i.e. $A \to 0$) limit, the per-kick rotation
generator commutes with itself across kicks, so

$$
U_\text{train}\;\xrightarrow{A\to 0}\;\exp\!\left[-i\tfrac{\pi}{4}\begin{pmatrix}0 & C\\ C^\dagger & 0\end{pmatrix}\right] = \tfrac{1}{\sqrt 2}\left(\mathbb{1} - i\begin{pmatrix}0 & C\\ C^\dagger & 0\end{pmatrix}\right).
$$

Applying $U_\text{train}$ to $|\psi_0\rangle$ and projecting onto the
spin-coherence observables yields, after a standard computation using
the displacement-operator identities
$D(i\eta)|\beta\rangle = e^{i\eta\,\mathrm{Re}\,\beta}\,|\beta + i\eta\rangle$
and the coherent-state overlap
$\langle\beta|\beta'\rangle = \exp(-\tfrac{1}{2}(|\beta|^2+|\beta'|^2)+\beta^*\beta')$:

$$
|C|(\vartheta_0) \;=\; \tfrac{1}{2}\sqrt{1 - 2\,e^{-2\eta^2}\cos(4\eta\alpha\cos\vartheta_0) + e^{-4\eta^2}}.
$$

**Range over $\vartheta_0$.** As $\vartheta_0$ sweeps $[0, 2\pi)$, the
argument $4\eta\alpha\cos\vartheta_0$ ranges over
$[-4\eta\alpha, +4\eta\alpha]$. For $4\eta\alpha \geq \pi$ (i.e.
$|\alpha| \geq \pi/(4\eta) \approx 1.98$ at $\eta = 0.397$), the
cosine takes every value in $[-1, +1]$, so

$$
\min_{\vartheta_0}|C| = \tfrac{1}{2}\bigl(1 - e^{-2\eta^2}\bigr),
\qquad
\max_{\vartheta_0}|C| = \tfrac{1}{2}\bigl(1 + e^{-2\eta^2}\bigr),
$$

yielding
$V_\text{imp} = 1 - \min|C| = \tfrac{1}{2}(1 + e^{-2\eta^2})$. For
$|\alpha| < \pi/(4\eta)$, the full cosine range is not swept and
$V_\text{imp}$ is reduced. ∎

**Numerical value at $\eta = 0.397$:** $V_\text{imp} = (1 +
e^{-0.315})/2 = (1 + 0.7296)/2 = 0.8648$. This matches the numerical
impulsive-limit overlay on the v0.1.1 primary heatmaps to the fourth
decimal (confirmed by
[verify_analytic.py](../numerics/verify_analytic.py)).

**Consequence for the α-recovery attribution.** Lemma B establishes
that the impulsive limit has no $\alpha$-structure above $|\alpha| \approx 2$.
The V($|\alpha|$) oscillation observed in the v0.1 full grid and the
dense α-recovery scan at $\delta t/T_m = 0.80$ is therefore a
**finite-$\delta t$ effect**, not a feature of the impulsive reference.
This narrows the §5.3 mechanism attribution: the oscillation is
generated by the non-commutativity of $H_\text{coupling}$ with
$\omega_m a^\dagger a$ inside each pulse's $\delta t$ window, which
produces $\alpha$-dependent corrections to $K$ of order $\omega_m
\delta t$.

-----

## 4. Finite-$\delta t$ expansion (partial)

The next-to-leading-order correction to $K$ in $\omega_m \delta t$ is
obtained from the symmetric Trotter split
$K = e^{-i H_\text{pulse} \delta t}$ with $H_\text{pulse} = \omega_m
a^\dagger a + H_\text{coupling}$:

$$
K \;=\; e^{-i\omega_m a^\dagger a\, \delta t/2}\,
e^{-i H_\text{coupling} \delta t}\,
e^{-i\omega_m a^\dagger a\, \delta t/2}\,
+\, \mathcal{O}((\omega_m \delta t)^3)\cdot[\text{BCH}].
$$

The leading correction to the action on a coherent state at the
motional-mode frequency is a Debye–Waller-like factor $e^{i\omega_m
\delta t\,(a^\dagger a)/2}$ applied before and after the coupling;
this rotates the displacement direction of $C$ by $\omega_m \delta t
/ 2$, which at large $\alpha$ produces the encoder-sensitivity
revival observed numerically. The closed-form evaluation — taking
$N \to \infty$ at fixed $\delta t$ to match the option-(a) calibration
— is more involved and is the *full* WP-C v0.2 analytic deliverable.
This note establishes the leading-order structure and the impulsive
anchor; the finite-$\delta t$ calculation to the first oscillation
maximum is deferred.

-----

## 5. Summary of what is and is not established

| Claim | Proved here? | Numerical anchor |
|---|---|---|
| $V_\text{imp} = \tfrac{1}{2}(1+e^{-2\eta^2})$ independent of $N, \alpha$ for $|\alpha| \geq \pi/(4\eta)$ | **Yes** (Lemma B) | v0.1.1 impulsive overlay, $V \approx 0.865$ uniformly |
| Gap propagator is identity on motion at $t_\text{sep} = T_m$, $\delta = 0$ | **Yes** (Lemma A) | Doppler probe $P_\text{mid,min} \geq 0.999$ everywhere |
| Any α-structure in $V$ at finite $\delta t$ is a finite-$\delta t$ effect, not impulsive | **Yes** (Lemma B corollary) | α-recovery v1, v2 |
| Closed-form $V(\alpha)$ curve at $\delta t/T_m = 0.80$ | Not here | α-recovery v2 numerical curves |
| Debye–Waller vs JC-revival attribution for the finite-$\delta t$ oscillation | Not here | v0.2 scope |

-----

*v0.1 · 2026-04-21 · Written after completion of the α-recovery v1/v2
and Doppler probes. Verified numerically — see companion
[verify_analytic.py](../numerics/verify_analytic.py).*
