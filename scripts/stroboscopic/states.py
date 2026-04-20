"""State preparation: coherent, Fock, squeezed, and spin⊗motion tensor.

Pure-state kets (complex vectors). Thermal sampling and multi-trajectory
handling live in sequences.py, not here.
"""
from __future__ import annotations

import numpy as _np

from .backend import xp, expm
from .operators import annihilation


def coherent_state(alpha_abs: float, alpha_phase_deg: float, nmax: int):
    """|α⟩ = exp(-|α|²/2) Σ αⁿ/√n! |n⟩ — analytical recurrence."""
    theta = _np.radians(float(alpha_phase_deg))
    alpha = float(alpha_abs) * _np.exp(1j * theta)
    # Build on host, transfer once (JAX-safe; avoids in-place assignment).
    psi_host = _np.zeros(nmax, dtype=_np.complex128)
    psi_host[0] = _np.exp(-abs(alpha) ** 2 / 2)
    for n in range(1, nmax):
        psi_host[n] = psi_host[n - 1] * alpha / _np.sqrt(n)
    return xp().asarray(psi_host)


def fock_state(n: int, nmax: int):
    psi_host = _np.zeros(nmax, dtype=_np.complex128)
    if n < nmax:
        psi_host[n] = 1.0
    return xp().asarray(psi_host)


def squeeze_operator(r: float, phi_deg: float, nmax: int):
    """S(r, φ) = exp[(r/2)(e^{-2iφ} a² − e^{2iφ} a†²)]."""
    if r == 0.0:
        return xp().eye(nmax, dtype=xp().complex128)
    phi = _np.radians(float(phi_deg))
    a = annihilation(nmax)
    adag = a.conj().T
    e2phi = _np.exp(2j * phi)
    gen = (r / 2.0) * (_np.conj(e2phi) * (a @ a) - e2phi * (adag @ adag))
    return expm(gen)


def displacement_operator(alpha_abs: float, alpha_phase_deg: float, nmax: int):
    """D(α) = exp(α a† − α* a)."""
    if alpha_abs == 0.0:
        return xp().eye(nmax, dtype=xp().complex128)
    theta = _np.radians(float(alpha_phase_deg))
    alpha = float(alpha_abs) * _np.exp(1j * theta)
    a = annihilation(nmax)
    adag = a.conj().T
    gen = alpha * adag - _np.conj(alpha) * a
    return expm(gen)


def prepare_motional(params: dict):
    """Build motional ket from a params dict (see defaults.DEFAULTS)."""
    nmax = int(params["nmax"])

    if params.get("fock_n") is not None:
        psi = fock_state(int(params["fock_n"]), nmax)
        if params.get("alpha", 0.0) > 0:
            D = displacement_operator(params["alpha"], params["alpha_phase_deg"], nmax)
            psi = D @ psi
    elif params.get("n_thermal", 0.0) > 0:
        nbar = float(params["n_thermal"])
        p = 1.0 / (1.0 + nbar)
        n = min(int(_np.log(_np.random.random()) / _np.log(1 - p)), nmax - 1)
        psi = fock_state(n, nmax)
        if params.get("alpha", 0.0) > 0:
            D = displacement_operator(params["alpha"], params["alpha_phase_deg"], nmax)
            psi = D @ psi
    else:
        if params.get("alpha", 0.0) > 0:
            psi = coherent_state(params["alpha"], params["alpha_phase_deg"], nmax)
        else:
            psi = fock_state(0, nmax)

    if params.get("squeeze_r", 0.0) > 0:
        S = squeeze_operator(params["squeeze_r"], params["squeeze_phi_deg"], nmax)
        psi = S @ psi

    return psi


def tensor_spin_motion(theta_deg: float, phi_deg: float, psi_m, nmax: int):
    """|ψ_spin⟩ ⊗ |ψ_m⟩ in the dim = 2·nmax basis (↓ block first)."""
    theta = _np.radians(float(theta_deg))
    phi = _np.radians(float(phi_deg))
    c_down = _np.cos(theta / 2)
    c_up = _np.sin(theta / 2) * _np.exp(1j * phi)
    return xp().concatenate([c_down * psi_m, c_up * psi_m])
