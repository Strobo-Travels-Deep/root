"""Smoke tests for the WP-W v0.6 back-action helpers in `_common`.

Five convention/correctness locks (scope §7 step 1):

  1. **partial_trace_spin** — physical orientation. Tr ρ_m = 1; for a
     product spin⊗motion state ρ_m = |ψ_m⟩⟨ψ_m| (purity 1) and equals
     the *physical* convention, not the transposed `observables.compute`
     internal form.

  2. **wigner_from_rho vs analytic, pure states.** Vacuum / coherent /
     Fock |2⟩ reproduce `_common.W_{vacuum,coherent,fock}` (the 2/π
     references) — locks the 2/π parity prefactor and the displacement
     order.

  3. **W_mixed_cat 2/π guardrail (review-pass).** The canonical 2/π
     parity form applied to the *mixed* ρ = ½|α⟩⟨α| + ½|−α⟩⟨−α|
     reproduces `_common.W_mixed_cat` (the ½-folded 1/π closed form).
     Confirms neither is a prefactor bug: `wigner_from_rho` stays 2/π
     for every ρ; the closed form's 1/π is a normalisation artefact.

  4. **conditional_motional_ket — σ_x branch lock.** σ_x post-select of
     the ideal-SDF output on |+y⟩|0⟩ equals D(±β_tot/2)|0⟩, numerically
     locking the σ_x branch convention.

  5. **cat_ket** vs `_common.chi_cat` (⟨ψ|D(β)|ψ⟩) and `_common.W_cat`
     (via wigner_from_rho).

Run: ``python wp-wigner-tomography/numerics/test_back_action_helpers.py``
or via pytest.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(Path(__file__).parent))

from stroboscopic import states
from stroboscopic.ideal_sdf import U_ideal_sdf, displacement as eng_displacement

from _common import (
    W_cat,
    W_coherent,
    W_fock,
    W_vacuum,
    cat_ket,
    chi_cat,
    conditional_motional_ket,
    partial_trace_spin,
    wigner_from_rho,
    _displacement,
)


NMAX = 60  # Fock-truncation floor of D(α) at the |α|≈4.24 box
# corner is ≲4e-8 here; a real convention/orientation bug is O(0.05–0.3),
# so the 1e-6 test tolerance cleanly discriminates the two.


def _alpha_grid(half_width: float = 3.0, n: int = 21) -> np.ndarray:
    """Shared Re/Im axis; n=21 → centre index 10 is α=0."""
    return np.linspace(-half_width, half_width, n)


# ---------------------------------------------------------------------------
# Lock 1 — partial_trace_spin physical orientation
# ---------------------------------------------------------------------------

def test_partial_trace_product_state_is_pure_input():
    psi_m = states.coherent_state(1.0, 37.0, NMAX)
    # |+y⟩ ⊗ ψ_m via apply_mw_pi2 on |↓⟩ψ_m
    psi = states.apply_mw_pi2(
        np.concatenate([psi_m, np.zeros(NMAX, dtype=np.complex128)]),
        mw_phase_deg=0.0, nmax=NMAX,
    )
    rho_m = partial_trace_spin(psi, NMAX)
    assert abs(np.trace(rho_m) - 1.0) < 1e-12
    # product state → reduced motional state is pure = |ψ_m⟩⟨ψ_m|
    purity = float(np.real(np.trace(rho_m @ rho_m)))
    assert abs(purity - 1.0) < 1e-12
    expected = np.outer(psi_m, np.conj(psi_m))
    assert np.max(np.abs(rho_m - expected)) < 1e-12
    # physical (not transposed): off-diagonal sign must match |ψ_m⟩⟨ψ_m|
    assert np.max(np.abs(rho_m - rho_m.conj().T)) < 1e-12  # Hermitian


# ---------------------------------------------------------------------------
# Lock 2 — wigner_from_rho vs analytic 2/π references (pure states)
# ---------------------------------------------------------------------------

def _rho_from_ket(psi_m: np.ndarray) -> np.ndarray:
    return np.outer(psi_m, np.conj(psi_m))


def test_wigner_from_rho_vacuum():
    ax = _alpha_grid()
    rho = _rho_from_ket(states.fock_state(0, NMAX))
    W, err = wigner_from_rho(rho, ax)
    assert err < 1e-12
    AX, AY = np.meshgrid(ax, ax)  # cols = Re, rows = Im
    W_an = W_vacuum(AX + 1j * AY)
    assert abs(W[10, 10] - 2.0 / np.pi) < 1e-6   # W_vac(0) = 2/π
    assert np.max(np.abs(W - W_an)) < 1e-6


def test_wigner_from_rho_coherent():
    ax = _alpha_grid()
    psi_m = states.coherent_state(1.0, 0.0, NMAX)
    W, err = wigner_from_rho(_rho_from_ket(psi_m), ax)
    assert err < 1e-12
    AX, AY = np.meshgrid(ax, ax)
    assert np.max(np.abs(W - W_coherent(AX + 1j * AY, 1.0 + 0j))) < 1e-6


def test_wigner_from_rho_fock2():
    ax = _alpha_grid()
    W, err = wigner_from_rho(_rho_from_ket(states.fock_state(2, NMAX)), ax)
    assert err < 1e-12
    AX, AY = np.meshgrid(ax, ax)
    W_an = W_fock(AX + 1j * AY, 2)
    assert np.max(np.abs(W - W_an)) < 1e-6
    # Fock|2⟩: W(0) = (2/π)(−1)² L₂(0) = +2/π; the ring dips negative.
    assert abs(W[10, 10] - 2.0 / np.pi) < 1e-6
    assert np.min(W) < -0.1


# ---------------------------------------------------------------------------
# Lock 3 — W_mixed_cat 2/π guardrail (the review-pass invariant)
# ---------------------------------------------------------------------------

def test_wigner_from_rho_mixed_cat_matches_half_folded_closed_form():
    """Canonical 2/π parity form on the mixed ρ reproduces the closed
    form `_common.W_mixed_cat` (½-folded 1/π). Neither is a bug."""
    ax = _alpha_grid()
    a0 = 1.5 + 0j
    cp = states.coherent_state(1.5, 0.0, NMAX)
    cm = states.coherent_state(1.5, 180.0, NMAX)
    rho_mixed = 0.5 * np.outer(cp, np.conj(cp)) + 0.5 * np.outer(cm, np.conj(cm))
    W, err = wigner_from_rho(rho_mixed, ax)
    assert err < 1e-12
    AX, AY = np.meshgrid(ax, ax)
    from _common import W_mixed_cat
    assert np.max(np.abs(W - W_mixed_cat(AX + 1j * AY, a0))) < 1e-6


# ---------------------------------------------------------------------------
# Lock 4 — conditional_motional_ket: σ_x branch of ideal SDF
# ---------------------------------------------------------------------------

def test_conditional_sigma_x_selects_displaced_branch():
    beta = 0.9 + 0.3j  # branch separation
    psi_m0 = states.fock_state(0, NMAX)
    psi_plus_y = states.apply_mw_pi2(
        np.concatenate([psi_m0, np.zeros(NMAX, dtype=np.complex128)]),
        mw_phase_deg=0.0, nmax=NMAX,
    )
    psi_out = U_ideal_sdf(beta, NMAX) @ psi_plus_y
    for s, sign in ((+1, +1.0), (-1, -1.0)):
        ket, prob = conditional_motional_ket(psi_out, NMAX, "x", s)
        assert abs(prob - 0.5) < 1e-9          # 50/50 on the equator
        target = eng_displacement(sign * beta / 2.0, NMAX) @ psi_m0
        fidelity = abs(np.vdot(target, ket)) ** 2  # global phase ignored
        assert abs(fidelity - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Lock 5 — cat_ket vs chi_cat / W_cat
# ---------------------------------------------------------------------------

def test_cat_ket_chi_and_wigner():
    a0 = 1.5
    psi = cat_ket(a0 + 0j, NMAX, parity=+1)
    assert abs(np.real(np.vdot(psi, psi)) - 1.0) < 1e-12
    # χ_ψ(β) = ⟨ψ|D(β)|ψ⟩ vs analytic chi_cat
    betas = np.array([0.0, 0.4 + 0j, 0.3 + 0.7j, -1.1j, 1.0 + 0.2j])
    for b in betas:
        chi_eng = np.vdot(psi, _displacement(b, NMAX) @ psi)
        chi_an = chi_cat(np.array([b]), a0 + 0j)[0]
        assert abs(chi_eng - chi_an) < 1e-6
    # Wigner vs analytic W_cat
    ax = _alpha_grid()
    W, err = wigner_from_rho(np.outer(psi, np.conj(psi)), ax)
    assert err < 1e-12
    AX, AY = np.meshgrid(ax, ax)
    assert np.max(np.abs(W - W_cat(AX + 1j * AY, a0 + 0j))) < 1e-6


# ---------------------------------------------------------------------------
# Lock 6 — conditional_motional_ket σ_y matches the engine convention
# ---------------------------------------------------------------------------

def test_conditional_sigma_y_matches_engine_convention():
    """`apply_mw_pi2(|↓⟩|0⟩, 0)` is the engine σ_y=+1 eigenstate
    (σ_y = −2 Im⟨d|u⟩ = +1; cf. test_ideal_sdf). Post-selecting
    σ_y=+1 must return prob 1 with ket ∝ |0⟩, and σ_y=−1 prob 0 —
    the post-run review-pass sign fix."""
    psi_m0 = states.fock_state(0, NMAX)
    psi_py = states.apply_mw_pi2(
        np.concatenate([psi_m0, np.zeros(NMAX, dtype=np.complex128)]),
        mw_phase_deg=0.0, nmax=NMAX,
    )
    d, u = psi_py[:NMAX], psi_py[NMAX:]
    assert abs(-2.0 * np.imag(np.vdot(d, u)) - 1.0) < 1e-12  # engine σ_y=+1
    ket_p, p_p = conditional_motional_ket(psi_py, NMAX, "y", +1)
    _, p_m = conditional_motional_ket(psi_py, NMAX, "y", -1)
    assert abs(p_p - 1.0) < 1e-12
    assert p_m < 1e-12
    assert abs(abs(np.vdot(psi_m0, ket_p)) ** 2 - 1.0) < 1e-12  # ket_p ∝ |0⟩
    # σ_x, σ_z are orthogonal to σ_y ⇒ 50/50
    for b in ("x", "z"):
        _, q = conditional_motional_ket(psi_py, NMAX, b, +1)
        assert abs(q - 0.5) < 1e-12


# ---------------------------------------------------------------------------

def _main() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
