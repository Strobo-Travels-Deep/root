"""Smoke tests for the ideal-SDF primitive (FH20-style σ_x SDF).

Four convention locks per the WP-W P1 session plan:

  1. **Branch separation, +x branch.** $U_\\text{ideal-sdf}(\\beta)\\,|{+}x\\rangle|0\\rangle$
     displaces the |+x⟩ branch by +β/2 (not β); locks the WP-W §2
     branch-separation convention.

  2. **Branch sign, −x branch.** $U\\,|{-}x\\rangle|0\\rangle$ displaces
     the |−x⟩ branch by −β/2.

  3. **σ_x SDF on |+y⟩|0⟩ → χ readout.** Starting from the equator
     state $|{+}y\\rangle\\otimes|0\\rangle$ (orthogonal to σ_x), the
     post-SDF observables give
     $\\langle\\sigma_y\\rangle = \\mathrm{Re}\\,\\chi(\\beta)$,
     $\\langle\\sigma_z\\rangle = -\\mathrm{Im}\\,\\chi(\\beta)$,
     and the *χ-readout combination*
     $C_\\text{yz} \\equiv \\langle\\sigma_y\\rangle - i\\langle\\sigma_z\\rangle = \\chi(\\beta)$
     — no Gaussian prefactor, no overall phase, no conjugation.

  4. **No σ_x dependence on χ.** $\\langle\\sigma_x\\rangle$ carries
     no χ-dependent signal (σ_x is the SDF axis itself).

Each test verifies against a closed-form analytic prediction with
tolerance ≤ 1e-9 (machine precision on `complex128`).
"""
from __future__ import annotations

import numpy as np
import pytest

from scripts.stroboscopic import ideal_sdf as _isdf
from scripts.stroboscopic.states import coherent_state, fock_state, apply_mw_pi2


NMAX = 30


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_coherent(alpha_complex: complex, nmax: int = NMAX):
    mag = float(abs(alpha_complex))
    if mag == 0.0:
        return fock_state(0, nmax)
    return coherent_state(mag, float(np.degrees(np.angle(alpha_complex))), nmax)


def _coherent_overlap_sq(psi: np.ndarray, alpha: complex, nmax: int = NMAX) -> float:
    target = _make_coherent(alpha, nmax)
    return float(abs(np.vdot(target, psi)) ** 2)


def _make_plus_x(motion: np.ndarray, nmax: int) -> np.ndarray:
    """|+x⟩⊗|ψ_m⟩ = (1/√2)(|↓⟩+|↑⟩)⊗|ψ_m⟩ in [down, up] ordering."""
    return np.concatenate([motion, motion]) / np.sqrt(2.0)


def _make_minus_x(motion: np.ndarray, nmax: int) -> np.ndarray:
    """|-x⟩⊗|ψ_m⟩ = (1/√2)(|↓⟩-|↑⟩)⊗|ψ_m⟩."""
    return np.concatenate([motion, -motion]) / np.sqrt(2.0)


def _make_plus_y(motion: np.ndarray, nmax: int) -> np.ndarray:
    """|+y⟩⊗|ψ_m⟩ via apply_mw_pi2 on |↓⟩⊗|ψ_m⟩ with phase 0."""
    psi_start = np.concatenate([motion, np.zeros(nmax, dtype=np.complex128)])
    return apply_mw_pi2(psi_start, mw_phase_deg=0.0, nmax=nmax)


def _spin_expectations(psi: np.ndarray, nmax: int) -> tuple[float, float, float]:
    """Return ⟨σ_x⟩, ⟨σ_y⟩, ⟨σ_z⟩ on the [down, up] state vector."""
    down = psi[:nmax]
    up = psi[nmax:]
    inner = np.vdot(down, up)
    # σ_x = [[0, 1], [1, 0]] (in [down, up]) → 2 Re⟨d|u⟩
    sx = 2.0 * float(np.real(inner))
    # σ_y = [[0, i], [-i, 0]] → -2 Im⟨d|u⟩ (derived in the convention notes)
    sy = -2.0 * float(np.imag(inner))
    # σ_z = [[-1, 0], [0, 1]] (with [down, up] = [−, +] eigenvalues)
    sz = float(np.vdot(up, up).real - np.vdot(down, down).real)
    return sx, sy, sz


# ---------------------------------------------------------------------------
# Lock 1 — branch separation: |+x⟩|0⟩ → |+x⟩|+β/2⟩
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("beta_complex", [0.5 + 0j, 1.0 + 0j, 0.3 + 0.4j, -0.8j])
def test_lock1_plus_x_branch_displaced_by_half_beta(beta_complex):
    """|+x⟩|0⟩ → |+x⟩|+β/2⟩  (branch displacement = β/2, NOT β)."""
    nmax = NMAX
    psi = _make_plus_x(fock_state(0, nmax), nmax)
    U = _isdf.U_ideal_sdf(beta_complex, nmax)
    psi_out = U @ psi

    # Spin should remain |+x⟩ (D(σ_x β/2)|+x⟩ = |+x⟩ · D(β/2)|0⟩)
    down = psi_out[:nmax]
    up = psi_out[nmax:]
    assert np.allclose(down, up, atol=1e-10), \
        f"down ≠ up: |+x⟩ branch broke for β={beta_complex}"

    # Motional state (either block, divided by 1/√2) should be |+β/2⟩
    motion_out = down * np.sqrt(2.0)
    overlap_sq = _coherent_overlap_sq(motion_out, beta_complex / 2.0, nmax)
    assert overlap_sq > 0.999999, (
        f"|+x⟩-branch motion did NOT match |+β/2⟩ for β={beta_complex}: "
        f"|⟨β/2|m⟩|² = {overlap_sq:.10f}"
    )
    # Factor-of-2 trap: should NOT match |+β⟩
    if abs(beta_complex) > 0.6:
        overlap_wrong = _coherent_overlap_sq(motion_out, beta_complex, nmax)
        assert overlap_wrong < 0.95, (
            f"factor-of-2 violated: |+x⟩-branch motion matches |+β⟩ "
            f"with overlap² {overlap_wrong:.4f} for β={beta_complex}"
        )


# ---------------------------------------------------------------------------
# Lock 2 — branch sign: |−x⟩|0⟩ → |−x⟩|−β/2⟩
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("beta_complex", [0.5 + 0j, 1.0 + 0j, 0.3 + 0.4j, -0.8j])
def test_lock2_minus_x_branch_displaced_by_neg_half_beta(beta_complex):
    """|−x⟩|0⟩ → |−x⟩|−β/2⟩."""
    nmax = NMAX
    psi = _make_minus_x(fock_state(0, nmax), nmax)
    U = _isdf.U_ideal_sdf(beta_complex, nmax)
    psi_out = U @ psi

    down = psi_out[:nmax]
    up = psi_out[nmax:]
    assert np.allclose(down, -up, atol=1e-10), \
        f"down ≠ -up: |−x⟩ branch broke for β={beta_complex}"

    motion_out = down * np.sqrt(2.0)
    overlap_sq = _coherent_overlap_sq(motion_out, -beta_complex / 2.0, nmax)
    assert overlap_sq > 0.999999, (
        f"|−x⟩-branch motion did NOT match |−β/2⟩ for β={beta_complex}: "
        f"|⟨-β/2|m⟩|² = {overlap_sq:.10f}"
    )


# ---------------------------------------------------------------------------
# Lock 3 — σ_x SDF on |+y⟩|0⟩: spin observables give χ
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("beta_complex", [0.3 + 0j, 0.5 + 0j, 0.7 + 0.7j, -0.4 - 0.3j])
def test_lock3_chi_readout_on_vacuum(beta_complex):
    """On |+y⟩|0⟩:
       ⟨σ_y⟩ = Re χ_vac(β),  ⟨σ_z⟩ = −Im χ_vac(β),
       C_yz = ⟨σ_y⟩ − i⟨σ_z⟩ = χ_vac(β).
    For real-valued χ_vac the Im part is zero so this only locks ⟨σ_y⟩.
    """
    nmax = NMAX
    psi_in = _make_plus_y(fock_state(0, nmax), nmax)
    U = _isdf.U_ideal_sdf(beta_complex, nmax)
    psi_out = U @ psi_in

    sx, sy, sz = _spin_expectations(psi_out, nmax)
    chi_vac = float(np.exp(-abs(beta_complex) ** 2 / 2.0))  # real

    C_yz = complex(sy, -sz)  # = ⟨σ_y⟩ − i⟨σ_z⟩
    residual = abs(C_yz - chi_vac)
    assert residual < 1e-9, (
        f"C_yz vs χ_vac mismatch at β={beta_complex}: "
        f"C_yz={C_yz}, χ_vac={chi_vac}, residual={residual:.2e}"
    )
    # Lock 4 cross-check: σ_x should be ~0 (no χ dependence on σ_x axis)
    assert abs(sx) < 1e-9, f"⟨σ_x⟩ ≠ 0 at β={beta_complex}: got {sx:.2e}"


@pytest.mark.parametrize("alpha", [0.5, 1.0])
@pytest.mark.parametrize("beta_complex", [0.4 + 0j, 0.5 + 0.5j, -0.3 - 0.4j])
def test_lock3b_chi_readout_on_coherent(alpha, beta_complex):
    """On |+y⟩|α⟩ (real α):
       C_yz = χ_coh(β; α) = e^{-|β|²/2} e^{2i Im(α* β)}.
    """
    nmax = NMAX
    motion = coherent_state(float(alpha), 0.0, nmax)
    psi_in = _make_plus_y(motion, nmax)
    U = _isdf.U_ideal_sdf(beta_complex, nmax)
    psi_out = U @ psi_in

    sx, sy, sz = _spin_expectations(psi_out, nmax)
    chi_coh = (np.exp(-abs(beta_complex) ** 2 / 2.0)
               * np.exp(2j * np.imag(np.conj(alpha) * beta_complex)))
    C_yz = complex(sy, -sz)
    residual = abs(C_yz - chi_coh)
    assert residual < 1e-9, (
        f"C_yz vs χ_coh mismatch: α={alpha}, β={beta_complex}, "
        f"C_yz={C_yz}, χ_coh={chi_coh}, residual={residual:.2e}"
    )
    # σ_x carries no χ info
    assert abs(sx) < 1e-9, f"⟨σ_x⟩ ≠ 0: α={alpha}, β={beta_complex}, sx={sx:.2e}"


# ---------------------------------------------------------------------------
# Inversion direction χ(β) = C_yz on equator-state readout
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("alpha", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("beta_complex", [0.4 + 0.3j, -0.6 + 0.2j])
def test_inversion_direction_chi_from_Cyz(alpha, beta_complex):
    """χ(β) = ⟨σ_y⟩ − i⟨σ_z⟩ — the WP-W reconstruction-pipeline target."""
    nmax = NMAX
    if alpha == 0.0:
        motion = fock_state(0, nmax)
    else:
        motion = coherent_state(float(alpha), 0.0, nmax)
    psi_in = _make_plus_y(motion, nmax)
    U = _isdf.U_ideal_sdf(beta_complex, nmax)
    psi_out = U @ psi_in

    sx, sy, sz = _spin_expectations(psi_out, nmax)
    chi_inverted = complex(sy, -sz)

    chi_analytic = (np.exp(-abs(beta_complex) ** 2 / 2.0)
                    * np.exp(2j * np.imag(np.conj(alpha) * beta_complex)))

    assert abs(chi_inverted - chi_analytic) < 1e-9, (
        f"χ_inv ≠ χ_an: α={alpha}, β={beta_complex}, "
        f"χ_inv={chi_inverted}, χ_an={chi_analytic}"
    )


# ---------------------------------------------------------------------------
# Unitarity & identity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("beta_complex", [0.5 + 0j, 1.2 + 0.7j, -0.6 + 0.3j])
def test_unitarity(beta_complex):
    U = _isdf.U_ideal_sdf(beta_complex, NMAX)
    UUd = U.conj().T @ U
    I = np.eye(2 * NMAX, dtype=np.complex128)
    assert np.allclose(UUd, I, atol=1e-9), \
        f"U not unitary at β={beta_complex}: max|U†U−I| = {np.max(np.abs(UUd - I)):.2e}"


def test_beta_zero_is_identity():
    U = _isdf.U_ideal_sdf(0.0 + 0.0j, NMAX)
    I = np.eye(2 * NMAX, dtype=np.complex128)
    assert np.allclose(U, I, atol=1e-15)
