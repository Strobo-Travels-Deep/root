"""Per-pulse effective Hamiltonian in the 2·nmax spin⊗motion basis.

Coupling convention matches legacy engine v0.9.1: C with σ₋, C† with σ₊,
dressed by the AC analysis phase.
"""
from __future__ import annotations

import numpy as _np

from .backend import xp


def build_pulse_hamiltonian(eta: float, omega_r: float, delta: float,
                            nmax: int, C, Cdag,
                            ac_phase_rad: float = 0.0,
                            omega_m: float = 0.0,
                            intra_pulse_motion: bool = False):
    """H_eng = δ/2·σ_z + [ω_m·a†a if intra_pulse_motion] + (Ω/2)[e^{iϕ}C σ₋ + e^{-iϕ}C† σ₊].

    Returns a (2·nmax, 2·nmax) complex matrix.
    """
    xp_ = xp()
    n_arr = xp_.arange(nmax, dtype=xp_.float64)

    diag_down = xp_.full((nmax,), -delta / 2.0, dtype=xp_.complex128)
    diag_up = xp_.full((nmax,), +delta / 2.0, dtype=xp_.complex128)
    if intra_pulse_motion and omega_m != 0.0:
        diag_down = diag_down + omega_m * n_arr
        diag_up = diag_up + omega_m * n_arr

    D_down = xp_.diag(diag_down)
    D_up = xp_.diag(diag_up)

    if ac_phase_rad == 0.0:
        UR = (omega_r / 2.0) * C
        LL = (omega_r / 2.0) * Cdag
    else:
        ph = _np.exp(1j * float(ac_phase_rad))
        UR = (omega_r / 2.0) * ph * C
        LL = (omega_r / 2.0) * _np.conj(ph) * Cdag

    return xp_.block([[D_down, UR], [LL, D_up]])
