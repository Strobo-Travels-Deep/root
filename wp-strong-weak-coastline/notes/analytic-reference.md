# Analytic reference — WP-Coastline

**Status:** v0.2 · 2026-04-21. Two closed-form lemmas (one reformulated
from the v0.1 draft after a reviewer found that the original Lemma A
was stated for an idealization — $t_\text{gap} = T_m$ — that does not
match the executed train, which uses $t_\text{gap} = T_m - \delta t$).
Numerically verified by
[verify_analytic.py](../numerics/verify_analytic.py), which in v0.2
also opens [coastline_v1.h5](../numerics/coastline_v1.h5) and
[coastline_doppler_v1.h5](../numerics/coastline_doppler_v1.h5) to
spot-check the lemmas' downstream numerical claims.

*Read as: idealised-asymptotic analytic model. The finite-$\delta t$
train used by the WP numerics differs from the idealisation in ways
that this note makes explicit; the v0.1 draft slipped on that point
and over-reached in the downstream framing.*

-----

## 1. Setup and notation

Single mode $a, a^\dagger$, single spin $\sigma_{x,y,z}$. Coupling
operator as stored in
[scripts/stroboscopic/operators.py:23](../../scripts/stroboscopic/operators.py#L23):

$$
C = \exp\!\bigl[i\eta(a + a^\dagger)\bigr] = D(i\eta),
$$

i.e. the displacement operator by a pure-imaginary amount $i\eta$.
Per-pulse Hamiltonian as used in
[scripts/stroboscopic/hamiltonian.py:42](../../scripts/stroboscopic/hamiltonian.py#L42)
(at ac phase $\varphi = 0$, with $\text{intra\_pulse\_motion}=\text{True}$):

$$
H_\text{pulse} = H_0 + V,
\quad
H_0 \equiv \omega_m\, a^\dagger a + \tfrac{\delta}{2}\sigma_z,
\quad
V \equiv \tfrac{\Omega}{2}\,(C\sigma_- + C^\dagger\sigma_+).
$$

The strobe train consists of $N$ pulses of duration $\delta t$
separated by gaps of length $T_\text{gap} = T_m - \delta t$ (with
$T_m = 2\pi/\omega_m$), so that the pulse-to-pulse period is exactly
$T_m$. During gaps the Hamiltonian is $H_0$ only (the coupling $V$
vanishes).

-----

## 2. Lemma A — Stroboscopic motional heterodyne (interaction-picture
formulation)

**Statement.** In the interaction picture with respect to $H_0$ —
i.e. in the frame rotating at $\omega_m a^\dagger a + (\delta/2)\sigma_z$:

1. **(Exact, for any $t_\text{gap}$.)** The gap Hamiltonian in the
   interaction picture is identically zero: $\widetilde H_\text{gap}(t) = 0$.
   Gaps contribute the identity to $U_\text{train}^\text{IP}$.

2. **(Stroboscopic-condition-dependent.)** For $t_\text{sep} = T_m =
   2\pi/\omega_m$, the coupling operator's motional part at any
   pulse-start time $t_j = j\,T_m$ equals its lab-frame value at
   $t = 0$:
   $$
   e^{i\omega_m a^\dagger a\, t_j}\,C\,e^{-i\omega_m a^\dagger a\, t_j}
   = \exp\!\bigl[i\eta(a\,e^{-i\omega_m t_j} + a^\dagger e^{i\omega_m t_j})\bigr]
   = \exp\!\bigl[i\eta(a + a^\dagger)\bigr] = C,
   $$
   because $\omega_m t_j = 2\pi j$ is an integer multiple of $2\pi$. The motional coupling operator is therefore **stroboscopically stationary at pulse-start times** — the heterodyne.

3. **(Intra-pulse rotation, $\alpha$-dependent.)** Within a single
   pulse window $[t_j, t_j + \delta t]$, the interaction-picture coupling
   operator rotates:
   $$
   \widetilde C(t_j + \tau) = \exp\!\bigl[i\eta(a\,e^{-i\omega_m \tau} + a^\dagger e^{i\omega_m \tau})\bigr]
   = D\!\bigl(i\eta\, e^{i\omega_m \tau}\bigr),
   \quad \tau\in[0, \delta t].
   $$
   The direction of the displacement rotates through angle $\omega_m\,\delta t$
   during the pulse. This is the *only* $\alpha$-sensitive structure
   in the interaction-picture train.

**Proof.** (1) During a gap, $H_\text{lab} = H_0$ exactly (the coupling
$V$ vanishes). In the IP at $H_0$, the Hamiltonian is
$\widetilde H = U_{H_0}^\dagger(t)[H_\text{lab} - H_0]U_{H_0}(t) = 0$.
True for any $t_\text{gap}$. (2) Direct substitution of
$\omega_m t_j = 2\pi j$ into the transformed operator. (3) Direct
expansion of $e^{i\omega_m a^\dagger a \tau}C\,e^{-i\omega_m a^\dagger a \tau}$. ∎

**What the lemma does not say.** It does **not** say the lab-frame
gap propagator is the identity — it is not, for the executed code.
The lab-frame gap propagator carries $\exp(-i\omega_m n\,T_\text{gap})$
on the motional block and $\exp(\pm i\delta T_\text{gap}/2)$ on the
spin block, with $T_\text{gap} = T_m - \delta t$; neither factor is
unity at finite $\delta t$. The v0.1 draft of this note stated Lemma A
for the idealised $T_\text{gap} = T_m$ case and then applied it to the
executed train; that conflation has been corrected.

**Consequence for the Doppler probe.** The IP formulation converts
the train to a time-ordered pulse sequence with no gap-mediated
accumulation of motional phase. The spin-detuning phase at $\delta
\neq 0$ accumulates linearly as $(N-1)\delta T_\text{gap}/2$ on
each spin block — $\alpha$-independent by construction. Off-tooth
coherence $P$ at $\delta \neq 0$ can therefore only be reduced by the
**intra-pulse** finite-$\delta t$ action of $V$ combined with the
intra-pulse rotation of $\widetilde C(\tau)$. This reduces the
Doppler-accumulation budget from $\mathcal O(N)$ (naive expectation)
to $\mathcal O(1)$ per single pulse. The numerical observation
$P_\text{mid,min} \geq 0.999$ in the Doppler probe is consistent with
this: at the calibration-scheme-stable option-(a) point, a single
pulse's finite bandwidth does not appreciably broaden the line, and
the $\mathcal O(N)$ accumulation that would normally reach the
(V low, P low) regime is absent.

**What this still does not settle.** It does not prove
$P_\text{mid,min} = 1$ identically. A finite-$\delta t$ intra-pulse
analysis could still leave residual $\mathcal O(\delta t/T_m)$ Doppler
signatures in $P$ at large $\alpha$; those would not show up in the
three-decimal readouts of the v0.1.1 probes but would exist in
principle. "Doppler-merging quadrant empty in principle" is therefore
too strong: what is proved is **Doppler-accumulation suppression from
$\mathcal O(N)$ to $\mathcal O(1)$** by the stroboscopic heterodyne, not
identical vanishing of $P$-deviations.

-----

## 3. Lemma B — Impulsive-limit $V$ floor

**Statement.** In the **exact impulsive limit** $\delta t \to 0$ at
fixed total rotation $N \cdot A = \pi/2$ and $t_\text{sep} = T_m$, the
tooth visibility for a coherent state $|\alpha e^{i\vartheta_0}\rangle$
under option-(a) calibration is

$$
V_\text{imp} \;=\; \tfrac{1}{2}\bigl(1 + e^{-2\eta^2}\bigr),
$$

**independently of $\alpha$ and $N$**, provided
$|\alpha| \geq \pi/(4\eta)$ so that the $\vartheta_0$ sweep covers a
full period of the interference factor.

**Derivation.** In the impulsive limit $\delta t \to 0$, intra-pulse
motion is frozen (Lemma A point 3 with $\omega_m \delta t \to 0$, so
$\widetilde C(\tau) \to C$). The per-kick unitary is then

$$
K = \exp\!\left[-i\tfrac{A}{2}\Sigma\right],
\quad
\Sigma = \begin{pmatrix}0 & C\\ C^\dagger & 0\end{pmatrix},\quad \Sigma^2 = \mathbb{1}.
$$

Because the gaps are identity in the IP (Lemma A point 1) and the
coupling is stroboscopically stationary (Lemma A point 2), the train
propagator in the IP is $U_\text{train}^\text{IP} = K^N$. At fixed
$NA = \pi/2$ and $A\to 0$, the per-kick generator commutes with
itself across kicks, so

$$
U_\text{train}^\text{IP}\;\xrightarrow{A\to 0}\;
\exp\!\left[-i\tfrac{\pi}{4}\Sigma\right]
= \tfrac{1}{\sqrt 2}\bigl(\mathbb{1} - i\Sigma\bigr).
$$

Applying to the initial state
$\tfrac{1}{\sqrt 2}(|\!\downarrow\rangle + i|\!\uparrow\rangle)
\otimes |\alpha e^{i\vartheta_0}\rangle$ and computing $\sigma_x, \sigma_y$
via the coherent-state displacement identity
$D(i\eta)|\beta\rangle = e^{i\eta\,\mathrm{Re}\,\beta}\,|\beta + i\eta\rangle$
and the overlap
$\langle\beta|\beta'\rangle = \exp(-\tfrac{1}{2}(|\beta|^2+|\beta'|^2)+\beta^*\beta')$
yields

$$
|C|(\vartheta_0) \;=\; \tfrac{1}{2}\sqrt{1 - 2\,e^{-2\eta^2}\cos(4\eta\alpha\cos\vartheta_0) + e^{-4\eta^2}}.
$$

For $4\eta\alpha \geq \pi$ (i.e. $|\alpha| \geq \pi/(4\eta)$), the
cosine argument sweeps a full period and

$$
\min_{\vartheta_0}|C| = \tfrac{1}{2}\bigl(1 - e^{-2\eta^2}\bigr),
\qquad
V_\text{imp} = 1 - \min|C| = \tfrac{1}{2}\bigl(1 + e^{-2\eta^2}\bigr). \qed
$$

**Numerical value at $\eta = 0.397$:** $V_\text{imp} = 0.86482$.

**What the lemma says, strictly.** Only that the impulsive limit has
no $\alpha$-structure and saturates at a Debye–Waller-determined floor
above $|\alpha| \approx 1.98$. The impulsive limit is an *asymptotic
reference*, not the finite-$\delta t$ train the WP numerics actually
execute.

**What the lemma does not say.** It does **not** attribute the
mechanism of the finite-$\delta t$ $V(|\alpha|)$ oscillation. The v0.1
draft of this note claimed that because the impulsive limit has no
$\alpha$-structure, any observed $\alpha$-structure must be a
Debye–Waller-class finite-$\delta t$ correction, with JC-revival
therefore ruled out. That is **too strong**:

- What is rigorous: the observed $\alpha$-structure is a
  finite-$\delta t$ effect (correct — the impulsive limit cannot
  source it).
- What is not rigorous: *which* finite-$\delta t$ mechanism generates
  it. JC-style interference acts within single pulses as readily as
  DW-class corrections do; both enter at order $\omega_m \delta t$
  and higher. The α-recovery v2 Test B (fixed-Ω option) shows that
  JC-style N-phase interference is a real phenomenon in this system
  under variable rotation. Ruling it out under option-(a) specifically
  requires the finite-$\delta t$ closed-form — not yet derived.

The conservative summary is: **the observed $V(|\alpha|)$ oscillation
is a finite-$\delta t$ correction to the Debye–Waller floor.** Whether
the correction is best named "Debye–Waller-class" or has a JC-like
component is unresolved. Lemma B narrows but does not close §5.3.

-----

## 4. Finite-$\delta t$ expansion (partial, conjectural)

The next-to-leading-order correction to $K$ in $\omega_m \delta t$ can
be organised by the symmetric Trotter split and by the exact IP
expression

$$
K_\text{IP} \;=\; \mathcal T \exp\!\left[-i \int_0^{\delta t}\!\! V_\text{IP}(\tau)\,d\tau\right],
\quad
V_\text{IP}(\tau) = \tfrac{\Omega}{2}\bigl[e^{-i\delta\tau}\widetilde C(\tau)\sigma_- + \text{h.c.}\bigr].
$$

At $\delta = 0$, expanding $\widetilde C(\tau) \approx C\bigl(\mathbb{1}
+ i\omega_m\tau\,[\widetilde C(0)]^{-1}\partial_\tau\widetilde C(0) + \dots\bigr)$
and time-ordering yields a correction to $K$ proportional to
$\omega_m\,\delta t\,[a^\dagger a, C] / 2$. On a coherent state with
amplitude $\alpha$, this commutator has expectation
$\sim \eta|\alpha|$, producing an $\alpha$-scaled contribution to $V$
at order $\omega_m\delta t \cdot \eta|\alpha|$. The sign and
oscillatory structure of this contribution determine the shape of the
$V(|\alpha|)$ curve but cannot be extracted without the higher-order
time-ordered integral. The full closed-form at order
$(\omega_m\delta t)^2$ remains a WP-C v0.2 scope item.

-----

## 5. Summary of what is and is not established

| Claim | Proved here? | Precision |
|---|---|---|
| $U_\text{gap}^\text{IP} = \mathbb{1}$ for any $t_\text{gap}$ (Lemma A.1) | Yes | exact |
| Coupling stroboscopically stationary at $t_j = j T_m$ (Lemma A.2) | Yes | exact |
| Intra-pulse $\widetilde C(\tau)$ rotates through $\omega_m \delta t$ (Lemma A.3) | Yes | exact |
| $V_\text{imp} = \tfrac{1}{2}(1+e^{-2\eta^2})$ α-independent for $\|\alpha\| \geq \pi/(4\eta)$ (Lemma B) | Yes | exact |
| Doppler accumulation suppressed from $\mathcal O(N)$ to $\mathcal O(1)$ | Yes (corollary of Lemma A) | structural |
| (V low, P low) quadrant empty in principle | **No — too strong** | — |
| Observed $V(\|\alpha\|)$ oscillation is a finite-$\delta t$ correction to the DW floor | Yes (corollary of Lemma B) | structural |
| JC-revival ruled out for option-(a) | **No — too strong** | — |
| Closed-form $V(\|\alpha\|)$ at $\delta t/T_m = 0.80$ | Not here | — |

-----

*v0.2 · 2026-04-21 · Reviewer-prompted rewrite of Lemma A into the
interaction-picture formulation that matches the executed code, with
downstream claims tightened accordingly. v0.1 superseded.*

*v0.1 · 2026-04-21 · Initial draft. Lemma A stated for the idealisation
$t_\text{gap} = T_m$, which does not match the code
($t_\text{gap} = T_m - \delta t$); downstream claims over-reached as a
result. Superseded by v0.2.*
