"""WP-W P1 sentinel — engine-side single-point validation of the ideal SDF.

Per the §4a P1 spec, this runs ONE central-lobe target point
$\\beta_\\star = 0.5 e^{i\\pi/4}$, for two input states (vacuum and
coherent $|\\alpha=1\\rangle$), at two train lengths ($N=20$ and
$N=80$), using the inverse-Dirichlet rule of §2 to choose the
$(\\delta, \\varphi_\\text{train})$ scan parameters. The post-train
spin contrast $C_\\text{engine}$ is compared to the analytic
prediction.

**Comparison target** (per the P1 guardrail): the **spin observables
combined to read out χ directly** — for the σ_x SDF on the |+y⟩
equator state, the smoke tests (`test_ideal_sdf.py` lock 3) lock the
convention

    χ(β) = ⟨σ_y⟩ − i⟨σ_z⟩

— no Gaussian prefactor, no overall phase, no conjugation. Comparison
is then $\\chi_\\text{engine}(\\beta_\\star)$ vs analytic
$\\chi_\\text{ρ_m}(\\beta_\\star)$. *Not* $\\langle\\psi_\\text{post}|\\hat D(\\beta_\\star)|\\psi_\\text{post}\\rangle$ —
that would be a back-action diagnostic, not the measurement signal.

Pass criterion (per §4a): $|C_\\text{engine} - C_\\text{analytic}| / |C_\\text{analytic}| < 5\\%$
at $N=20$. The $N=80$ comparison is diagnostic, not gating.

Usage:
    python numerics/run_p1_preflight.py
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import h5py
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(Path(__file__).parent))

from stroboscopic import HilbertSpace, states
from stroboscopic.ideal_sdf import build_ideal_sdf_train

from _common import (
    RUNNER_VERSION,
    canonical_manifest,
    chi_coherent,
    chi_vacuum,
    inverse_dirichlet,
    write_manifest,
)


WP_ID = "wigner-tomography"
CODE_VERSION = "0.4.0"
REPOSITORY = "https://github.com/Strobo-Travels-Deep/root"


def measure_chi_readout(psi: np.ndarray, nmax: int) -> complex:
    """χ_engine(β) ≡ ⟨σ_y⟩ − i⟨σ_z⟩  (FH20-style σ_x SDF + |+y⟩ equator).

    For σ_x SDF on |+y⟩|ψ_m⟩, ⟨σ_x⟩ carries no χ info (it's the SDF
    axis); the χ-readout combination of the orthogonal spin
    observables ⟨σ_y⟩ and ⟨σ_z⟩ returns χ_ψ_m(β) directly (see
    `scripts/stroboscopic/tests/test_ideal_sdf.py` lock 3).
    """
    down = psi[:nmax]
    up = psi[nmax:]
    inner = np.vdot(down, up)
    sy = -2.0 * float(np.imag(inner))
    sz = float(np.vdot(up, up).real - np.vdot(down, down).real)
    return complex(sy, -sz)


def inverse_dirichlet_target(beta_star: complex, beta0: float, N: int,
                              omega_m: float) -> tuple[float, float]:
    """Find (δ - kω_m, φ_train) such that the ideal-SDF train delivers β★ at N pulses.

    Returns (delta_offset_in_units_of_omega_m, phi_train_rad).
    The detuning offset is x = (δ − kω_m)·T_m / (2π); convert outside.
    """
    r = abs(beta_star)
    theta = float(np.angle(beta_star))
    ratio = r / beta0  # ∈ [0, N]
    x = inverse_dirichlet(N, ratio)  # x = (δ - kω_m) T_m on monotone branch
    # arg β₀ = 0 (real positive), arg D_N(x) = (N-1) x / 2 on monotone branch.
    phi_train = (theta - (N - 1) * x / 2.0) % (2.0 * np.pi)
    # Convert x → physical detuning offset in units of ω_m
    T_m = 2.0 * np.pi / omega_m
    delta_offset = x / T_m  # in physical units (s⁻¹ if ω_m is s⁻¹)
    return float(delta_offset), float(phi_train), float(x)


def analytic_chi(beta: complex, alpha: float | None) -> complex:
    """Analytic χ_ρ_m(β) — the target the σ_x-SDF readout should reproduce.

    For σ_x SDF on |+y⟩|ψ_m⟩, χ_engine = ⟨σ_y⟩ − i⟨σ_z⟩ equals
    χ_ψ_m(β) directly (no prefactor, no phase).
    """
    if alpha is None or alpha == 0.0:
        return complex(chi_vacuum(beta))
    return complex(chi_coherent(beta, complex(alpha)))


def run_one_point(*, hs, nmax, beta_star, beta0, N, omega_m, k_sideband: int,
                  state_name: str, alpha: float | None) -> dict:
    """Execute one P1 (β★, state, N) sentinel point."""
    # Inverse-Dirichlet inversion of (β★) → (δ - kω_m, φ_train)
    delta_offset, phi_train, x_branch = inverse_dirichlet_target(
        beta_star, beta0, N, omega_m
    )
    delta = k_sideband * omega_m + delta_offset

    # Prepare initial state: |↓⟩|ψ_m⟩ then MW π/2 → equator
    if alpha is None or alpha == 0.0:
        psi_m = states.fock_state(0, nmax)
    else:
        psi_m = states.coherent_state(float(alpha), 0.0, nmax)
    psi_start = np.concatenate([psi_m, np.zeros(nmax, dtype=np.complex128)])
    psi_equator = states.apply_mw_pi2(psi_start, mw_phase_deg=0.0, nmax=nmax)

    # Build and run the ideal-SDF train
    train = build_ideal_sdf_train(
        hs=hs,
        beta0=beta0,
        ac_phase_rad=phi_train,
        omega_m=omega_m,
        delta=delta,
        n_pulses=N,
    )
    psi_out = train.evolve(psi_equator)

    # Engine-measured χ readout via ⟨σ_y⟩ − i⟨σ_z⟩
    chi_engine = measure_chi_readout(psi_out, nmax)

    # Analytic prediction
    chi_an = analytic_chi(beta_star, alpha)

    rel_residual = abs(chi_engine - chi_an) / max(abs(chi_an), 1e-12)
    abs_residual = abs(chi_engine - chi_an)

    return {
        "state": state_name,
        "alpha": alpha,
        "N": N,
        "k_sideband": k_sideband,
        "beta_star": beta_star,
        "delta_offset_in_omega_m": delta_offset / omega_m,
        "delta_physical": delta,
        "phi_train_rad": phi_train,
        "x_branch_rad": x_branch,
        "chi_engine": chi_engine,
        "chi_analytic": chi_an,
        "rel_residual": rel_residual,
        "abs_residual": abs_residual,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--beta0", type=float, default=0.05)
    parser.add_argument("--omega-m", type=float, default=1.3,
                        help="motional frequency (natural units)")
    parser.add_argument("--nmax", type=int, default=30)
    parser.add_argument("--k-sideband", type=int, default=0,
                        help="comb tooth (k=0 = on-resonance; ±1 for sidebands)")
    parser.add_argument("--N-values", type=int, nargs="+", default=[20, 80])
    parser.add_argument("--output", type=str,
                        default="numerics/p1_preflight.h5")
    args = parser.parse_args()

    t0 = time.time()
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(args.nmax,))

    # Sentinel point: β★ = 0.5 · e^{iπ/4} per §4a
    beta_star = 0.5 * np.exp(1j * np.pi / 4.0)
    print(f"P1 sentinel target: β★ = 0.5 · e^{{iπ/4}} = {beta_star}")
    print(f"  |β★| = {abs(beta_star):.4f}, arg β★ = π/4")
    print(f"Engine: nmax = {args.nmax}, β₀ = {args.beta0}, ω_m = {args.omega_m}")
    print(f"Train lengths: {args.N_values}    Sideband: k = {args.k_sideband}\n")

    # Pass criterion: |C_engine - C_analytic| / |C_analytic| < 5% at N=20.
    PASS_REL_TOL_AT_N20 = 0.05

    results = []
    states_to_test = [
        ("vacuum", None),
        ("coherent_1.0", 1.0),
    ]

    overall_pass = True
    for state_name, alpha in states_to_test:
        for N in args.N_values:
            r = run_one_point(
                hs=hs, nmax=args.nmax, beta_star=beta_star,
                beta0=args.beta0, N=N, omega_m=args.omega_m,
                k_sideband=args.k_sideband,
                state_name=state_name, alpha=alpha,
            )
            results.append(r)

            print(f"--- {state_name}  N={N}  ---")
            print(f"  inverse-Dirichlet: x = {r['x_branch_rad']:.4f} rad, "
                  f"(δ − kω_m)/ω_m = {r['delta_offset_in_omega_m']:.4f}, "
                  f"φ_train = {r['phi_train_rad']:.4f} rad")
            print(f"  χ_engine   = {r['chi_engine']:.6f}")
            print(f"  χ_analytic = {r['chi_analytic']:.6f}")
            print(f"  |residual| = {r['abs_residual']:.2e}    "
                  f"rel = {r['rel_residual']:.2%}")
            gate = r['rel_residual'] < PASS_REL_TOL_AT_N20
            print(f"  PASS @ 5% (gating at N=20 only): "
                  f"{gate if N == 20 else 'diagnostic'}")
            if N == 20 and not gate:
                overall_pass = False
            print()

    elapsed = time.time() - t0
    print("=" * 60)
    print(f"P1 overall (N=20 gating, ≤ 5% rel residual): "
          f"{'PASS' if overall_pass else 'FAIL'}")
    print(f"Total wall: {elapsed:.2f} s")

    # Save HDF5 + manifest
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(output_path, "w") as h5:
        h5.attrs["wp_id"] = WP_ID
        h5.attrs["code_version"] = CODE_VERSION
        h5.attrs["runner_version"] = RUNNER_VERSION
        h5.attrs["beta_star_real"] = float(beta_star.real)
        h5.attrs["beta_star_imag"] = float(beta_star.imag)
        h5.attrs["beta0"] = args.beta0
        h5.attrs["nmax"] = args.nmax
        h5.attrs["k_sideband"] = args.k_sideband
        h5.attrs["pass"] = bool(overall_pass)
        for i, r in enumerate(results):
            grp = h5.create_group(f"point_{i:02d}")
            for k, v in r.items():
                if isinstance(v, complex):
                    grp.attrs[f"{k}_real"] = float(v.real)
                    grp.attrs[f"{k}_imag"] = float(v.imag)
                elif isinstance(v, (int, float, str, bool)) or v is None:
                    if v is not None:
                        grp.attrs[k] = v

    payload = {
        "physical_parameters": {
            "beta0": args.beta0,
            "omega_m": args.omega_m,
            "nmax": args.nmax,
            "k_sideband": args.k_sideband,
        },
        "sentinel": {
            "beta_star_real": float(beta_star.real),
            "beta_star_imag": float(beta_star.imag),
            "states": [s[0] for s in states_to_test],
            "N_values": args.N_values,
        },
        "pass_criterion": {
            "rel_tol_at_N20": PASS_REL_TOL_AT_N20,
            "N80_is_gating": False,
        },
        "results": [
            {k: (str(v) if isinstance(v, complex) else v) for k, v in r.items()}
            for r in results
        ],
        "overall_pass": bool(overall_pass),
        "tags": ["WP-W", "P1", "sentinel", "ideal-SDF"],
    }
    manifest = canonical_manifest(
        wp_id=WP_ID, code_version=CODE_VERSION, runner_version=RUNNER_VERSION,
        repository=REPOSITORY, artifact_path=str(output_path),
        artifact_format="hdf5", elapsed_s=elapsed, payload=payload,
    )
    write_manifest(manifest, output_path.with_suffix(".manifest.json"))
    print(f"Wrote {output_path} + manifest")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
