# WP-TOM — Phase-Space Tomography via Detuning–Phase Scans of the Analysis Train

**Status:** kick-off · v0.1 · 2026-05-13
**Numbering:** WP-TOM (provisional — to be reconciled with existing WP letters).

## Question

Can a stroboscopic analysis train, scanned over its detuning δ and AC
drive phase φ_train, **reconstruct** a coherent displaced motional
state $|\alpha\rangle$ from the resulting $P(\uparrow)(\delta, \varphi_\text{train})$
map?

Adjacent to but distinct from [WP-E (phase-contrast-maps)](../wp-phase-contrast-maps/):
WP-E fixes the train and scans the *state* coordinate $(\vartheta_0, \delta)$;
WP-TOM fixes the *state* and scans the *train* coordinate
$(\delta, \varphi_\text{train})$ — i.e. the analysis pulse drive phase.
The two together form the forward map and its conjugate.

## Scope of the kick-off

Quick-and-dirty intuition check, not yet production-grade:

- Nine input states: $|\alpha| \in \{0.1, 1, 3\}$ × $\theta_\alpha \in \{0, \pi/4, \pi/2\}$,
  tensored with $(|\uparrow\rangle + |\downarrow\rangle)/\sqrt{2}$.
- Three train lengths: $N \in \{1, 3, 10\}$.
- $(\delta, \varphi_\text{train})$ heatmap of $P(\uparrow)$ for each
  $(\alpha, N)$ combination.
- Total Rabi budget rescaled so each $N$ delivers a π/2 carrier rotation
  on resonance — this isolates comb-narrowing from raw drive strength.

## Files

- [`notebooks/00_kickoff_tomography.ipynb`](./notebooks/00_kickoff_tomography.ipynb) —
  the kick-off notebook (this folder's only artefact for now).

## What to look for

- **Ridge orientation in (δ, φ)** should rotate with $\theta_\alpha$ —
  this is the tomographic signature.
- **Tooth structure** along the δ axis should sharpen as $1/N$ —
  consistent with §1 of the [tutorial notebook](../notebooks/00_tutorial_pulse_train.ipynb).
- **Small-α contrast** should vanish as $|\alpha| \to 0$: the
  $(\delta, \varphi)$ map carries no motional information when there is
  no motion to interrogate. Recovery of any phase information at
  $|\alpha|=0.1$ is the signal-to-noise floor of this protocol.

## Follow-ups (after the kick-off)

- Promote the heatmap to a fit-based inversion: given $P(\uparrow)(\delta, \varphi)$,
  recover $(|\alpha|, \theta_\alpha)$.
- Add a finite-temperature thermal envelope and probe robustness.
- Compare to the WP-E forward map: do the two scans share a common
  invariant manifold?
