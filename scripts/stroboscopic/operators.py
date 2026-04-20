"""Motional operators for a single Fock-truncated mode.

All constructors are vectorized (no per-index assignment) so they
work under both numpy and JAX backends.
"""
from __future__ import annotations

from .backend import xp, expm


def annihilation(nmax: int):
    """a with a[n, n+1] = sqrt(n+1)."""
    sqrt_n = xp().sqrt(xp().arange(1, nmax, dtype=xp().float64))
    return xp().diag(sqrt_n.astype(xp().complex128), k=1)


def position(nmax: int):
    """X = a + a†."""
    a = annihilation(nmax)
    return a + a.conj().T


def coupling(eta: float, nmax: int):
    """C = exp(i·η·(a + a†)) in Fock basis."""
    X = position(nmax)
    return expm(1j * eta * X)
