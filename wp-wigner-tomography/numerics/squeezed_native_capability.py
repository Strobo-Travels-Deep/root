"""WP-W — native-engine 𝒪(η²) capability smoke (N-6).

squeezed_native_audit_scope.md §3 N-6 / §4 step 1. The *critical
first* execution step of the native re-audit: characterise the native
post-train vacuum at the App. E two-phonon timing (Δt=T_m/2,
δ=2ω_m) as a full Gaussian state, vs N ∈ {10,20,30}, to discriminate
a genuine 2ω_m squeezing channel from first-order displacement
leakage or heating/decoherence. A null is itself the headline finding
(parent §2 "structural, not a regime limit") — reported, not worked
around. Ideal leg untouched; no parked artefact written.

Usage:
    python wp-wigner-tomography/numerics/squeezed_native_capability.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import h5py
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(Path(__file__).parent))

from stroboscopic import HilbertSpace, build_strobo_train  # noqa: E402
from stroboscopic import operators as ops                   # noqa: E402

from _common import (  # noqa: E402
    RUNNER_VERSION, canonical_manifest, write_manifest,
    partial_trace_spin, gaussian_moments,
)

# D4-Layer-A pinned WP-E v0.9.1 native parameters (run_back_action.py).
ETA = 0.397
OMEGA_R = 0.09016606431708851
OMEGA_M = 1.3
DELTA_T = 0.6283185307179586  # = 0.13 · T_m at ω_m = 1.3
WP_ID = "wigner-tomography"
CODE_VERSION = "0.7.0-capability"
REPOSITORY = "https://github.com/Strobo-Travels-Deep/root"

NS = [10, 20, 30]
NMAX = 60


def native_vacuum(N: int, t_sep_factor: float, *, hs, C, Cdag):
    """|↓⟩⊗|0⟩ → native train (App. E timing) → reduced ρ_m.

    δ = 2ω_m (second-sideband two-phonon resonance), on-resonance peak
    (x̃=0 ⇒ φ_train=0). Convention matches run_back_action.evolve_native
    (no separate MW π/2; the train delivers the spin rotation), only
    t_sep_factor differs (0.5 = App. E Δt=T_m/2).
    """
    psi0 = np.zeros(2 * NMAX, dtype=np.complex128)
    psi0[0] = 1.0  # |↓⟩ ⊗ |0⟩
    train = build_strobo_train(
        hs=hs, eta=ETA, omega_r=OMEGA_R, omega_m=OMEGA_M,
        delta=2.0 * OMEGA_M, n_pulses=N, delta_t=DELTA_T,
        t_sep_factor=t_sep_factor, ac_phase_rad=0.0,
        intra_pulse_motion=True, gap_includes_spin_detuning=True,
        C=C, Cdag=Cdag,
    )
    psi = train.evolve(psi0)
    return partial_trace_spin(psi, NMAX)


def classify(rows_appE: list[dict]) -> tuple[str, str]:
    """Pre-registered N-6 discriminator on the App. E rows."""
    g30 = next(r for r in rows_appE if r["N"] == 30)
    aniso = g30["ratio"] - 1.0
    mean_mag = float(np.hypot(g30["mean_X"], g30["mean_P"]))
    purity = g30["purity"]
    ratios = [r["ratio"] for r in sorted(rows_appE, key=lambda r: r["N"])]
    growing = ratios[-1] > ratios[0] + 1e-6
    purities = [r["purity"] for r in sorted(rows_appE, key=lambda r: r["N"])]
    purity_falls = purities[-1] < purities[0] - 1e-3
    # squeezing scale ~ sqrt of the larger eigenvalue departure
    squeeze_scale = abs(g30["lambda_max"] - 1.0) + abs(g30["lambda_min"] - 1.0)

    if aniso >= 0.10 and growing and mean_mag < 0.1 and purity > 0.99:
        return ("SQUEEZING-PRESENT",
                f"λ_max/λ_min−1={aniso:.3f}≥0.10 at N=30, growing, "
                f"|⟨q⟩|={mean_mag:.3e}≈0, purity={purity:.4f}≈1")
    if mean_mag >= squeeze_scale and mean_mag > 0.1:
        return ("DISPLACEMENT-DOMINATED",
                f"|⟨q⟩|={mean_mag:.3f} ≳ squeeze scale {squeeze_scale:.3f}; "
                f"first-order single-phonon leakage wins")
    if purity_falls and aniso < 0.10:
        return ("HEATING-DOMINATED",
                f"purity {purities[0]:.4f}→{purities[-1]:.4f} falls, "
                f"anisotropy {aniso:.3f}<0.10 (≈isotropic growth)")
    return ("INCONCLUSIVE / WEAK",
            f"λ_max/λ_min−1={aniso:.3f}<0.10, |⟨q⟩|={mean_mag:.3e}, "
            f"purity={purity:.4f} — no clean 2ω_m squeezing channel")


def main() -> int:
    t0 = time.time()
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX)
    Cdag = C.conj().T

    print(f"WP-W native 𝒪(η²) capability smoke (N-6) — η={ETA}, "
          f"Ω_r={OMEGA_R:.5f}, ω_m/2π={OMEGA_M}, δ=2ω_m, nmax={NMAX}\n")
    hdr = (f"{'timing':>10} {'N':>3} {'⟨X⟩':>9} {'⟨P⟩':>9} "
           f"{'λ_max':>8} {'λ_min':>8} {'ratio':>8} {'orient°':>8} "
           f"{'purity':>8}")
    print(hdr)

    rows = []
    for label, tsf in (("AppE T/2", 0.5), ("ref  T", 1.0)):
        for N in NS:
            g = gaussian_moments(native_vacuum(N, tsf, hs=hs, C=C, Cdag=Cdag))
            row = {"timing": label, "t_sep_factor": tsf, "N": N,
                   "mean_X": g["mean_X"], "mean_P": g["mean_P"],
                   "lambda_max": g["lambda_max"],
                   "lambda_min": g["lambda_min"], "ratio": g["ratio"],
                   "orient_deg": g["orient_deg"], "purity": g["purity"]}
            rows.append(row)
            print(f"{label:>10} {N:>3d} {g['mean_X']:>9.3e} "
                  f"{g['mean_P']:>9.3e} {g['lambda_max']:>8.4f} "
                  f"{g['lambda_min']:>8.4f} {g['ratio']:>8.4f} "
                  f"{g['orient_deg']:>8.2f} {g['purity']:>8.5f}")

    appE = [r for r in rows if r["t_sep_factor"] == 0.5]
    verdict, reason = classify(appE)
    print(f"\n>>> N-6 VERDICT: {verdict}\n    {reason}")

    out = Path("wp-wigner-tomography/numerics/squeezed_native_capability.h5")
    with h5py.File(out, "w") as h5:
        h5.attrs["wp_id"] = WP_ID
        h5.attrs["code_version"] = CODE_VERSION
        h5.attrs["runner_version"] = RUNNER_VERSION
        h5.attrs["eta"] = ETA
        h5.attrs["omega_r"] = OMEGA_R
        h5.attrs["omega_m"] = OMEGA_M
        h5.attrs["delta_over_omega_m"] = 2.0
        h5.attrs["nmax"] = NMAX
        h5.attrs["verdict"] = verdict
        h5.attrs["verdict_reason"] = reason
        for i, r in enumerate(rows):
            g = h5.create_group(f"rec_{i:02d}")
            for k, v in r.items():
                g.attrs[k] = v
    elapsed = time.time() - t0
    payload = {
        "physical_parameters": {"eta": ETA, "omega_r": OMEGA_R,
                                "omega_m": OMEGA_M,
                                "delta_over_omega_m": 2.0,
                                "delta_t": DELTA_T, "nmax": NMAX},
        "timings": {"appE_t_sep_factor": 0.5, "ref_t_sep_factor": 1.0},
        "N_values": NS,
        "rows": rows,
        "verdict": verdict,
        "verdict_reason": reason,
        "tags": ["WP-W", "Rank2", "native-eta2", "capability-smoke", "N-6"],
    }
    manifest = canonical_manifest(
        wp_id=WP_ID, code_version=CODE_VERSION,
        runner_version=RUNNER_VERSION, repository=REPOSITORY,
        artifact_path=str(out), artifact_format="hdf5",
        elapsed_s=elapsed, payload=payload,
    )
    write_manifest(manifest, out.with_suffix(".manifest.json"))
    print(f"\nWrote {out} + manifest  ({elapsed:.1f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
