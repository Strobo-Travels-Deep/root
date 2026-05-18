"""Smoke tests for the native-audit helpers (squeezed_native_audit_scope.md
§4 step 1): the angle-general squeezed factory, `gaussian_moments`, and
the App. E ξ_tot inverse-Dirichlet target.

Locks:

  1. **parse_state angle-general.** `squeezed_<r>` → θ=0;
     `squeezed_<r>_perp` → π/2 (cd22ef6 back-compat);
     `squeezed_<r>_th<deg>` → deg·π/180 (the N-1 grid needs θ=π).

  2. **gaussian_moments on known Gaussians.** vacuum → means 0,
     cov = I, ratio 1, purity 1; coherent |α⟩ → ⟨X⟩=2α, cov = I,
     purity 1; squeezed vacuum S(r) θ=0 → cov = diag(e^{−2r}, e^{+2r})
     to the complex128 floor, purity 1; an incoherent mixture →
     purity < 1.

  3. **xi_tot_target_appE.** peak (ratio=N) → x̃=0, φ_train=θ,
     δ-offset=0; the detuning conversion uses T_m/2 (App. E), i.e.
     exactly 2× the carrier `inverse_dirichlet_target` offset for the
     same x — the doubled-fundamental signature.

Run: ``python wp-wigner-tomography/numerics/test_squeezed_native_helpers.py``
or via pytest.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).parent))

from _common import (  # noqa: E402
    parse_state, gaussian_moments, xi_tot_target_appE,
)

NCUT = 80


def _ann(n):
    return np.diag(np.sqrt(np.arange(1, n)), 1)


def test_parse_state_angle_general():
    assert parse_state("squeezed_0.5")["theta"] == 0.0
    assert abs(parse_state("squeezed_0.5_perp")["theta"] - np.pi / 2) < 1e-15
    assert abs(parse_state("squeezed_0.5_th90")["theta"] - np.pi / 2) < 1e-15
    assert abs(parse_state("squeezed_0.5_th180")["theta"] - np.pi) < 1e-15
    assert abs(parse_state("squeezed_0.25_th45")["theta"] - np.pi / 4) < 1e-15
    s = parse_state("squeezed_0.5_th180")
    assert s["kind"] == "squeezed" and s["r"] == 0.5
    assert s["gaussian"] is True and s["non_gaussian_metric"] is False
    try:
        parse_state("squeezed_0.5_bogus")
        raise AssertionError("expected ValueError on unknown qualifier")
    except ValueError:
        pass


def test_gaussian_moments_vacuum():
    n = NCUT
    rho = np.zeros((n, n), complex)
    rho[0, 0] = 1.0
    g = gaussian_moments(rho)
    assert abs(g["mean_X"]) < 1e-12 and abs(g["mean_P"]) < 1e-12
    assert abs(g["lambda_max"] - 1.0) < 1e-10
    assert abs(g["lambda_min"] - 1.0) < 1e-10
    assert abs(g["ratio"] - 1.0) < 1e-10
    assert abs(g["purity"] - 1.0) < 1e-10


def test_gaussian_moments_coherent():
    n = NCUT
    a = _ann(n)
    ad = a.conj().T
    alpha = 0.7
    D = expm(alpha * ad - np.conj(alpha) * a)
    psi = D[:, 0]
    rho = np.outer(psi, psi.conj())
    g = gaussian_moments(rho)
    assert abs(g["mean_X"] - 2.0 * alpha) < 1e-8       # ⟨a+a†⟩ = 2 Re α
    assert abs(g["mean_P"]) < 1e-8
    assert abs(g["ratio"] - 1.0) < 1e-6                # coherent ⇒ isotropic
    assert abs(g["purity"] - 1.0) < 1e-8


def test_gaussian_moments_squeezed():
    n = NCUT
    a = _ann(n)
    ad = a.conj().T
    r = 0.5
    S = expm(0.5 * (r * (a @ a) - r * (ad @ ad)))      # θ=0
    psi = S[:, 0]
    rho = np.outer(psi, psi.conj())
    g = gaussian_moments(rho)
    # θ=0 ⇒ Var X = e^{−2r} (squeezed), Var P = e^{+2r}
    assert abs(g["lambda_min"] - np.exp(-2 * r)) < 1e-9
    assert abs(g["lambda_max"] - np.exp(+2 * r)) < 1e-9
    assert abs(g["ratio"] - np.exp(4 * r)) < 1e-7
    assert abs(g["purity"] - 1.0) < 1e-8
    assert abs(g["mean_X"]) < 1e-9 and abs(g["mean_P"]) < 1e-9


def test_gaussian_moments_mixture_is_impure():
    n = NCUT
    rho = np.zeros((n, n), complex)
    rho[0, 0] = 0.6
    rho[1, 1] = 0.4                                    # incoherent |0⟩/|1⟩
    g = gaussian_moments(rho)
    assert g["purity"] < 1.0 - 1e-6                    # 0.6²+0.4² = 0.52
    assert abs(g["purity"] - 0.52) < 1e-9


def test_xi_tot_target_appE():
    N, omega_m = 30, 1.3
    # peak: ratio = N ⇒ x̃ = 0, φ_train = θ, δ-offset = 0
    xt, phi, doff = xi_tot_target_appE(float(N), N, omega_m, theta=0.3)
    assert abs(xt) < 1e-9 and abs(doff) < 1e-9
    assert abs(phi - 0.3) < 1e-9
    # doubled fundamental: App. E δ-offset uses T_m/2 = π/ω_m, i.e.
    # exactly 2× the carrier T_m = 2π/ω_m conversion for the same x̃
    xt2, _, doff_appE = xi_tot_target_appE(float(N) / 2.0, N, omega_m)
    carrier_offset = xt2 / (2.0 * np.pi / omega_m)        # x̃ / T_m
    assert abs(doff_appE - xt2 / (np.pi / omega_m)) < 1e-12
    assert abs(doff_appE - 2.0 * carrier_offset) < 1e-12
    assert xt2 > 0.0


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
