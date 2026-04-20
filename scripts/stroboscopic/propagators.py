"""Propagators for pulses and inter-pulse gaps.

- U_pulse = expm(-i H_pulse · dt_pulse), from Hamiltonian.
- U_gap   = diagonal analytical propagator for free evolution.

The gap is diagonal in the Fock×spin-z basis: motional phases exp(-i·ω_m·n·T_gap)
optionally combined with spin detuning phases exp(∓i·δ/2·T_gap) on the two
spin blocks (matches v0.9.1 convention used by run_2d_alpha3.py).
"""
from __future__ import annotations

import numpy as _np

from .backend import xp, expm


def build_U_pulse(H_pulse, dt_pulse: float):
    return expm(-1j * H_pulse * float(dt_pulse))


def build_impulsive_pulse(pulse_area: float, nmax: int, C, Cdag,
                          ac_phase_rad: float = 0.0):
    """K = exp(-i·(A/2)·[[0, e^{iϕ}C], [e^{-iϕ}C†, 0]]) — impulsive spin-motion kick.

    Used by the R2 path where the pulse carries no detuning or free
    motional evolution and only the coupling acts on the state.
    """
    xp_ = xp()
    zero = xp_.zeros((nmax, nmax), dtype=xp_.complex128)
    if ac_phase_rad == 0.0:
        UR = C
        LL = Cdag
    else:
        ph = _np.exp(1j * float(ac_phase_rad))
        UR = ph * C
        LL = _np.conj(ph) * Cdag
    K_gen = xp_.block([[zero, UR], [LL, zero]])
    return expm(-1j * (float(pulse_area) / 2.0) * K_gen)


def build_U_gap(nmax: int, omega_m: float, t_gap: float,
                delta: float = 0.0,
                include_motion: bool = True,
                include_spin_detuning: bool = True):
    """Diagonal gap propagator on the (↓ block, ↑ block) state.

    Motional phases (if enabled): exp(-i·ω_m·n·t_gap) on both spin blocks.
    Spin-detuning phases (if enabled): exp(+i·δ/2·t_gap) on ↓, exp(-i·δ/2·t_gap) on ↑.
    If both flags are False, returns the identity diagonal.
    """
    xp_ = xp()
    n_arr = xp_.arange(nmax, dtype=xp_.float64)
    if include_motion:
        mot = xp_.exp(-1j * omega_m * n_arr * float(t_gap)).astype(xp_.complex128)
    else:
        mot = xp_.ones(nmax, dtype=xp_.complex128)
    if include_spin_detuning and delta != 0.0:
        ph_d = _np.exp(+1j * delta / 2.0 * float(t_gap))
        ph_u = _np.exp(-1j * delta / 2.0 * float(t_gap))
        diag = xp_.concatenate([mot * ph_d, mot * ph_u])
    else:
        diag = xp_.concatenate([mot, mot])
    return diag  # apply as U_gap · ψ  ≡  diag * ψ   (element-wise)


def apply_gap(U_gap_diag, psi):
    """Left-apply the diagonal gap propagator: element-wise multiply."""
    return U_gap_diag * psi
