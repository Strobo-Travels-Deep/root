"""Observables computed from a spin⊗motion state vector (dim = 2·nmax)."""
from __future__ import annotations

import numpy as _np

from .backend import xp


def _as_host(x):
    """Return a numpy view of a JAX or numpy array (cheap)."""
    return _np.asarray(x)


def compute(psi, nmax: int) -> dict:
    """Return dict with sigma_x, sigma_y, sigma_z, coherence, entropy, nbar, mot_purity."""
    xp_ = xp()
    down = psi[:nmax]
    up = psi[nmax:]

    rho_dd = xp_.sum(xp_.abs(down) ** 2)
    rho_uu = xp_.sum(xp_.abs(up) ** 2)
    rho_du = xp_.sum(xp_.conj(down) * up)

    sx = 2 * rho_du.real
    sy = -2 * rho_du.imag
    sz = rho_uu - rho_dd
    coh = xp_.sqrt(sx ** 2 + sy ** 2 + sz ** 2)

    r = xp_.sqrt(4 * xp_.abs(rho_du) ** 2 + (rho_uu - rho_dd) ** 2)
    lp = (1 + r) / 2
    lm = (1 - r) / 2
    # Safe log: branchless, compatible with JAX.
    lp_safe = xp_.where(lp > 1e-15, lp, 1.0)
    lm_safe = xp_.where(lm > 1e-15, lm, 1.0)
    ent = -(lp * xp_.log2(lp_safe) + lm * xp_.log2(lm_safe))

    n_arr = xp_.arange(nmax, dtype=xp_.float64)
    nbar = xp_.sum(n_arr * xp_.abs(down) ** 2) + xp_.sum(n_arr * xp_.abs(up) ** 2)

    rho_m = xp_.outer(xp_.conj(down), down) + xp_.outer(xp_.conj(up), up)
    purity = xp_.real(xp_.trace(rho_m @ rho_m))

    return dict(
        sigma_x=float(_as_host(sx)),
        sigma_y=float(_as_host(sy)),
        sigma_z=float(_as_host(sz)),
        coherence=float(_as_host(coh)),
        entropy=float(_as_host(ent)),
        nbar=float(_as_host(nbar)),
        mot_purity=float(_as_host(purity)),
    )


def motional_fidelity(psi, psi_m_init, nmax: int) -> float:
    xp_ = xp()
    ov_down = xp_.dot(xp_.conj(psi_m_init), psi[:nmax])
    ov_up = xp_.dot(xp_.conj(psi_m_init), psi[nmax:])
    val = xp_.abs(ov_down) ** 2 + xp_.abs(ov_up) ** 2
    return float(_as_host(val))


def fock_leakage(psi, nmax: int, top_k: int = 3) -> float:
    """Population in the top-k Fock levels across both spin blocks."""
    xp_ = xp()
    lo = max(0, nmax - top_k)
    leak = xp_.sum(xp_.abs(psi[lo:nmax]) ** 2) + xp_.sum(xp_.abs(psi[nmax + lo:]) ** 2)
    return float(_as_host(leak))
