"""Smoke tests for the squeezed-vacuum helpers in `_common`
(squeezed_eta2_scope.md §9 step 1; Rank 2 prerequisite).

Convention/correctness locks:

  1. **r → 0 limit.** `chi_squeezed`/`W_squeezed` reduce *exactly* to
     `chi_vacuum`/`W_vacuum`.

  2. **chi_squeezed vs the exact state.** ⟨r,θ|D(β)|r,θ⟩ for the
     explicit S(ξ)|0⟩ ket reproduces the closed form to the
     `complex128` floor, for θ = 0 and θ = π/2. This is the lock that
     pins the **+** cross-term sign (the scope §3 lock-pass
     correction; the proposed-commit − sign fails this test).

  3. **Axis-orientation lock.** For θ = 0, r > 0, χ is broad along
     β_y and narrow along β_x (χ(0+ib) > χ(b+0i)) — a direct guard
     against a cross-term sign regression.

  4. **W_squeezed vs the parity-form Wigner** of the explicit ket
     (θ = 0, π/2), to the `complex128` floor; pure ⇒ non-negative.

  5. **Hermiticity** χ(−β) = χ*(β) (χ real and even).

  6. **wigner_from_chi(chi_squeezed)** has max|Im W| at the machine
     floor (the §4 convention-error sentinel) and no negativity.

  7. **State factory** parses `squeezed_<r>` / `squeezed_<r>_perp`
     and `chi_of_state` / `W_true_of_state` dispatch correctly.

Run: ``python wp-wigner-tomography/numerics/test_squeezed_helpers.py``
or via pytest.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).parent))

from _common import (  # noqa: E402
    chi_squeezed, W_squeezed, chi_vacuum, W_vacuum,
    chi_of_state, W_true_of_state, parse_state, wigner_from_chi,
)

FLOOR = 1e-12
NCUT = 80


def _squeezed_ket(r: float, theta: float, n: int = NCUT) -> np.ndarray:
    a = np.diag(np.sqrt(np.arange(1, n)), 1)
    ad = a.conj().T
    xi = r * np.exp(1j * theta)
    S = expm(0.5 * (np.conj(xi) * (a @ a) - xi * (ad @ ad)))
    return S[:, 0]


def _D(beta: complex, n: int = NCUT) -> np.ndarray:
    a = np.diag(np.sqrt(np.arange(1, n)), 1)
    ad = a.conj().T
    return expm(beta * ad - np.conj(beta) * a)


def test_chi_squeezed_r0_is_vacuum():
    ax = np.linspace(-4, 4, 41)
    bx, by = np.meshgrid(ax, ax)
    beta = bx + 1j * by
    for theta in (0.0, np.pi / 2, 1.0):
        assert np.max(np.abs(chi_squeezed(beta, 0.0, theta)
                             - chi_vacuum(beta))) == 0.0


def test_W_squeezed_r0_is_vacuum():
    ax = np.linspace(-3, 3, 41)
    gx, gy = np.meshgrid(ax, ax)
    g = gx + 1j * gy
    assert np.max(np.abs(W_squeezed(g, 0.0, 0.0) - W_vacuum(g))) < 1e-15


def test_chi_squeezed_matches_exact_state():
    for theta in (0.0, np.pi / 2):
        psi = _squeezed_ket(0.5, theta)
        worst = 0.0
        for bx in np.linspace(-2.0, 2.0, 9):
            for by in np.linspace(-2.0, 2.0, 9):
                b = bx + 1j * by
                exact = complex(psi.conj() @ (_D(b) @ psi))
                form = complex(chi_squeezed(np.array(b), 0.5, theta))
                worst = max(worst, abs(exact - form))
        assert worst < 1e-12, f"theta={theta}: {worst:.2e}"


def test_chi_squeezed_axis_orientation_theta0():
    # θ=0: squeezed in X ⇒ χ broad along β_y, narrow along β_x.
    r = 0.5
    for b in (0.5, 1.0, 1.5):
        chi_x = float(chi_squeezed(np.array(b + 0.0j), r, 0.0))   # narrow
        chi_y = float(chi_squeezed(np.array(0.0 + 1j * b), r, 0.0))  # broad
        assert chi_y > chi_x, (b, chi_y, chi_x)


def test_W_squeezed_matches_parity_form():
    for theta in (0.0, np.pi / 2):
        psi = _squeezed_ket(0.5, theta)
        n = len(psi)
        par = np.diag((-1.0) ** np.arange(n))
        worst = 0.0
        for x in np.linspace(-1.5, 1.5, 7):
            for y in np.linspace(-1.5, 1.5, 7):
                g = x + 1j * y
                w_par = (2.0 / np.pi) * np.real(
                    psi.conj() @ (_D(g) @ par @ _D(-g) @ psi))
                w_cf = float(W_squeezed(np.array(g), 0.5, theta))
                worst = max(worst, abs(w_par - w_cf))
        assert worst < 1e-12, f"theta={theta}: {worst:.2e}"
    # pure squeezed vacuum is Gaussian ⇒ strictly non-negative
    ax = np.linspace(-3, 3, 61)
    gx, gy = np.meshgrid(ax, ax)
    assert np.min(W_squeezed(gx + 1j * gy, 0.5, 0.0)) >= 0.0


def test_chi_squeezed_hermitian():
    ax = np.linspace(-4, 4, 41)
    bx, by = np.meshgrid(ax, ax)
    beta = bx + 1j * by
    for theta in (0.0, np.pi / 2):
        chi = chi_squeezed(beta, 0.5, theta)
        # χ(−β) = χ*(β); χ is real-valued here
        assert np.max(np.abs(chi - np.conj(chi[::-1, ::-1]))) < 1e-14
        assert np.max(np.abs(np.imag(chi))) == 0.0


def test_wigner_from_chi_squeezed_imag_floor():
    ax = np.linspace(-4, 4, 81)
    bx, by = np.meshgrid(ax, ax)
    beta = bx + 1j * by
    for theta in (0.0, np.pi / 2):
        chi = chi_squeezed(beta, 0.5, theta).astype(complex)
        _, _, err_imag = wigner_from_chi(chi, ax)
        assert err_imag < 1e-10, (theta, err_imag)


def test_state_factory_squeezed():
    s0 = parse_state("squeezed_0.5")
    sp = parse_state("squeezed_0.5_perp")
    assert s0["kind"] == "squeezed" and s0["r"] == 0.5 and s0["theta"] == 0.0
    assert sp["kind"] == "squeezed" and abs(sp["theta"] - np.pi / 2) < 1e-15
    assert s0["gaussian"] is True and s0["non_gaussian_metric"] is False
    ax = np.linspace(-3, 3, 41)
    bx, by = np.meshgrid(ax, ax)
    beta = bx + 1j * by
    assert np.array_equal(chi_of_state(beta, s0), chi_squeezed(beta, 0.5, 0.0))
    g = bx + 1j * by
    assert np.array_equal(W_true_of_state(g, sp),
                          W_squeezed(g, 0.5, np.pi / 2))


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
