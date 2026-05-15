"""Ideal σ_x-coupled state-dependent displacement (SDF) primitive — FH20 style.

This is the FH20 (Flühmann & Home 2020) bichromatic SDF operator
$U = D(\\sigma_x\\,\\beta/2)$, exposed as a single Fock-basis unitary
on the 2·nmax spin⊗motion Hilbert space. It is the *ideal* SDF that
WP-W's reconstruction pipeline assumes — clean, instantaneous,
spin-eigenstate-conditioned displacement — and is *not* what the
native Raman engine (`build_strobo_train`) realises (§7#3).

**Why σ_x and not σ_z.** The WP-W §2 inverse-Dirichlet rule
$\\beta_\\text{tot} = \\beta_0\\,e^{i\\varphi_\\text{train}}\\,\\mathcal{D}_N((\\delta-k\\omega_m)T_m)$
requires the SDF axis to rotate by $\\delta T_m$ per gap so that the
per-pulse displacement picks up a $e^{i n \\delta T_m}$ phase
factor — the source of the Dirichlet kernel. The detuning-induced
spin precession is around $\\sigma_z$, so the SDF axis must lie on
the equator (σ_x or any σ_φ); σ_z conditioning does *not* rotate
under $\\sigma_z$ precession and would deliver a flat $N\\beta_0$
accumulated displacement regardless of $\\delta$. The earlier
WP-W §Analytical bullet 2 wording "$\\sigma_z$-coupled" is
inconsistent with §2 and is corrected to "$\\sigma_x$-coupled (FH20)"
in the v0.5 logbook queued for that pass.

**Convention lock (WP-W §2):** `beta` is the **branch separation**
matching $\\beta_\\text{tot}$ in the σ_x eigenbasis. Internally the
operator is $U = D(\\sigma_x\\,\\beta/2)$:

- $|{+}x\\rangle$ branch is displaced by $+\\beta/2$.
- $|{-}x\\rangle$ branch is displaced by $-\\beta/2$.
- The branch *separation* in phase space is therefore $\\beta$.

After an $N$-pulse train with per-pulse separation kick $\\beta_0$,
the accumulated separation on resonance is $N\\beta_0 = \\beta_\\text{tot}$;
under off-resonant detuning, the spin precession between pulses
rotates the lab-frame SDF axis by $\\delta T_m$ per gap, picking up
the Dirichlet kernel factor in the rotating frame.

**Spin-contrast prediction.** Starting from
$|{+}y\\rangle\\otimes|\\psi_m\\rangle$ (after `apply_mw_pi2`, spin on
the equator orthogonal to $\\sigma_x$), the post-train complex
contrast is

  $$C_\\text{yz}(\\beta) = \\langle\\sigma_y\\rangle - i\\langle\\sigma_z\\rangle = \\chi_{\\rho_m}(\\beta).$$

Direct readout of χ — no Gaussian prefactor, no overall $i$ phase,
no conjugation. The $\\langle\\sigma_x\\rangle$ observable carries
no χ-dependent information (σ_x is the SDF axis itself).

**Block-matrix structure.** Using the σ_x projectors
$|{\\pm x}\\rangle\\langle{\\pm x}|=(I\\pm\\sigma_x)/2$:

  $$U = \\tfrac{1}{2}\\begin{bmatrix} D_+ + D_- & D_+ - D_- \\\\ D_+ - D_- & D_+ + D_- \\end{bmatrix}$$

with $D_\\pm = D(\\pm\\beta/2)$, in the engine's [down, up] block
ordering. The off-diagonal blocks couple the spin branches — this
is what makes σ_x SDF rotate under σ_z spin precession.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as _np

from .backend import xp, expm
from .operators import annihilation
from . import propagators as _prop
from .sequences import StroboTrain


def displacement(beta: complex, nmax: int):
    """Motional displacement operator $D(\\beta) = \\exp(\\beta a^\\dagger - \\beta^* a)$.

    Returns an (nmax, nmax) complex matrix in the Fock basis.

    For β = 0 returns the identity (avoids `expm(0)` overhead).
    """
    b = complex(beta)
    if b == 0:
        return xp().eye(nmax, dtype=xp().complex128)
    a = annihilation(nmax)
    adag = a.conj().T
    gen = b * adag - _np.conj(b) * a
    return expm(gen)


def U_ideal_sdf(beta: complex, nmax: int):
    """Ideal σ_x-conditioned displacement $U = D(\\sigma_x\\,\\beta/2)$ (FH20 style).

    `beta` is the branch *separation* (WP-W §2 convention) along the σ_x
    eigenbasis: $|{+}x\\rangle$ branch displaced by $+\\beta/2$,
    $|{-}x\\rangle$ branch by $-\\beta/2$.

    Returns a (2·nmax, 2·nmax) complex matrix in the engine's
    [down, up] block ordering:

        U = (1/2) · [[ D_+ + D_-, D_+ - D_- ],
                     [ D_+ - D_-, D_+ + D_- ]]

    where $D_\\pm = D(\\pm\\beta/2)$. The off-diagonal blocks couple
    the [down, up] spin branches — this is what makes σ_x SDF rotate
    under the σ_z spin precession applied by `build_U_gap` between
    pulses, yielding the WP-W §2 Dirichlet-kernel forward map.
    """
    half_b = complex(beta) / 2.0
    D_plus = displacement(+half_b, nmax)
    D_minus = displacement(-half_b, nmax)
    sum_block = 0.5 * (D_plus + D_minus)
    diff_block = 0.5 * (D_plus - D_minus)
    return xp().block([[sum_block, diff_block],
                       [diff_block, sum_block]])


@dataclass
class IdealSDFTrain:
    """N-pulse ideal-SDF train with explicit per-pulse phase rotation.

    Implements the WP-W §2 forward map directly: each pulse $n \\in [0, N)$
    delivers a σ_x SDF kick of magnitude $\\beta_0$ along the *rotating-
    frame* direction $\\varphi_n = \\varphi_\\text{train} + n \\cdot x$
    where $x = (\\delta - k\\omega_m)T_m$ is the per-gap detuning phase
    on the chosen comb tooth. The pulse list is therefore

        U_pulse_n = U_ideal_sdf(beta_0 · exp(i·(phi_train + n·x)), nmax)

    Between pulses the gap is *motion only* (no spin detuning), since
    the per-pulse phase rotation already encodes the WP-W §2
    detuning-induced rotation analytically. The motional gap evolves
    at $\\omega_m$ over $T_m \\cdot t_\\text{sep factor}$ and, for
    $t_\\text{sep factor}=1$, is the identity ($\\omega_m T_m = 2\\pi$).

    This convention keeps the χ readout
    $C_\\text{yz}=\\langle\\sigma_y\\rangle - i\\langle\\sigma_z\\rangle = \\chi(\\beta_\\text{tot})$
    in the lab frame valid: the spin doesn't precess during gaps, so
    the post-train readout is in the same frame as the initial $|+y\\rangle$
    preparation and there is no closing-rotation correction to apply.

    The accumulated displacement on resonance ($x=0$) is the on-axis
    peak $N\\beta_0$; off-resonance it is
    $\\beta_\\text{tot} = \\beta_0 e^{i\\varphi_\\text{train}}\\,\\mathcal{D}_N(x)$
    point-by-point per the WP-W §2 rule.
    """
    U_pulses: list  # length n_pulses
    U_gap_diag: object
    n_pulses: int

    def evolve(self, psi, record_steps: bool = False):
        if record_steps:
            history = [psi]
            for k in range(self.n_pulses):
                psi = self.U_pulses[k] @ psi
                if k < self.n_pulses - 1:
                    psi = _prop.apply_gap(self.U_gap_diag, psi)
                history.append(psi)
            return psi, history
        for k in range(self.n_pulses):
            psi = self.U_pulses[k] @ psi
            if k < self.n_pulses - 1:
                psi = _prop.apply_gap(self.U_gap_diag, psi)
        return psi


def build_ideal_sdf_train(*, hs,
                          beta0: float,
                          ac_phase_rad: float,
                          omega_m: float,
                          delta: float,
                          n_pulses: int,
                          k_sideband: int = 0,
                          t_sep_factor: float = 1.0) -> IdealSDFTrain:
    """Construct the per-pulse list and gap for an N-pulse ideal-SDF train.

    Per-pulse: ``U_ideal_sdf(beta_0 · exp(i·(ac_phase_rad + n·x)), nmax)``
    with $x = (\\delta - k_\\text{sideband}\\,\\omega_m) \\cdot T_m$ — the
    WP-W §2 per-gap rotating-frame phase.

    Gap: motion-only at $\\omega_m$ for $T_m \\cdot t_\\text{sep factor}$.
    With $t_\\text{sep factor}=1$ this is identity (full motional period).
    """
    nmax = hs.nmax
    T_m = 2.0 * _np.pi / omega_m
    x = (float(delta) - float(k_sideband) * float(omega_m)) * T_m

    U_pulses = []
    for n in range(int(n_pulses)):
        phase_n = float(ac_phase_rad) + n * x
        beta_n = complex(beta0) * _np.exp(1j * phase_n)
        U_pulses.append(U_ideal_sdf(beta_n, nmax))

    t_gap = T_m * t_sep_factor
    U_gap_diag = _prop.build_U_gap(
        nmax, omega_m, t_gap,
        delta=0.0,
        include_motion=True,
        include_spin_detuning=False,
    )
    return IdealSDFTrain(U_pulses=U_pulses, U_gap_diag=U_gap_diag, n_pulses=int(n_pulses))
