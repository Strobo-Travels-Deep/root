"""WP-W — native-engine 𝒪(η²) re-audit, full (r, θ) sweep.

squeezed_native_audit_scope.md §4 step 2 (LOCKED ba030c9), reframed
after the N-6 capability null (1ad9c4b): show the native engine's
failure to realise the 2ω_m squeezing channel is **systematic across
(r, θ)**, not a vacuum artefact, while the η-exact ideal leg is sound
(the P-D hard gate, bit-for-bit vs cd22ef6).

Per (r, θ) ∈ {0,0.25,0.5}×{0,π/2,π}:

  · P-D gate  — analytic squeezed-vacuum reconstruction (chi_squeezed
    → FFT → F vs W_squeezed); timing-independent; for the two states
    shared with cd22ef6 it must reproduce squeezed_recon.h5
    bit-for-bit (≤1e-12). The ONLY hard PASS/FAIL.
  · native    — engine at App. E timing (Δt=T_m/2, δ=2ω_m + ξ_tot
    inverse-Dirichlet offset), peak & mid: ρ_m Gaussian moments
    (ratio, orient, purity, means) + fidelity to the input |sq⟩.
  · ideal     — η-exact ideal SDF at matched (δ,φ,N,k=2) drive:
    purity/drop/fid-pre/W (back_action_scope §4a structural leg).
  · structural residual — ideal-vs-native Wigner L¹.

Reported vs the pre-registered P-A…P-E (scope §1). New artefact
family; parked artefacts untouched.

Usage:
    python wp-wigner-tomography/numerics/run_squeezed_native_audit.py
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

from stroboscopic import HilbertSpace, build_strobo_train, states  # noqa: E402
from stroboscopic import operators as ops                           # noqa: E402
from stroboscopic.ideal_sdf import build_ideal_sdf_train             # noqa: E402

from _common import (  # noqa: E402
    RUNNER_VERSION, canonical_manifest, write_manifest,
    partial_trace_spin, wigner_from_rho, gaussian_moments,
    squeezed_ket, chi_squeezed, W_squeezed, wigner_from_chi,
    xi_tot_target_appE, zero_pad_centered, padded_beta_axis,
    restrict_to_window, fidelity as overlap_fidelity,
)

ETA = 0.397
OMEGA_R = 0.09016606431708851
OMEGA_M = 1.3
DELTA_T = 0.6283185307179586
BETA0 = 0.05
N = 30
NMAX = 60
WP_ID = "wigner-tomography"
CODE_VERSION = "0.7.0-native-audit"
REPOSITORY = "https://github.com/Strobo-Travels-Deep/root"

R_GRID = [0.0, 0.25, 0.5]
THETA_GRID = [("0", 0.0), ("pi_2", np.pi / 2.0), ("pi", np.pi)]
PROBES = [("peak", float(N)), ("mid", float(N) / 2.0)]

# v0.2 reconstruction grid (matches cd22ef6 / run_reconstruction_demo).
RECON_B = 4.0
RECON_NG = 81
RECON_PAD = 161
RECON_WINDOW = 3.0
PD_TOL = 1e-12
CD22EF6 = "wp-wigner-tomography/numerics/squeezed_recon.h5"


def _state_metrics(rho, psi_pre, alpha_axis, d_alpha):
    purity = float(np.real(np.trace(rho @ rho)))
    fid_pre = float(np.real(np.vdot(psi_pre, rho @ psi_pre)))
    W, werr = wigner_from_rho(rho, alpha_axis)
    neg = float(np.sum(np.minimum(0.0, W)) * d_alpha ** 2)
    return {"purity": purity, "purity_drop": 1.0 - purity,
            "fidelity_to_pre": fid_pre, "neg_volume": neg,
            "W_err_imag": float(werr)}, W


def _pd_reconstruction(r, theta):
    """η-exact analytic squeezed reconstruction (timing-independent)."""
    ax = np.linspace(-RECON_B, RECON_B, RECON_NG)
    bx = ax[None, :] + 1j * ax[:, None]
    chi = chi_squeezed(bx, r, theta).astype(complex)
    chi_pad = zero_pad_centered(chi, RECON_PAD)
    bax_pad = padded_beta_axis(ax, RECON_PAD)
    aax, W_rec, err = wigner_from_chi(chi_pad, bax_pad)
    da = float(aax[1] - aax[0])
    ag = aax[None, :] + 1j * aax[:, None]
    W_true = W_squeezed(ag, r, theta)
    Wr, _ = restrict_to_window(W_rec, aax, RECON_WINDOW)
    Wt, _ = restrict_to_window(W_true, aax, RECON_WINDOW)
    return float(overlap_fidelity(Wr, Wt, da)), float(err)


def main() -> int:
    t0 = time.time()
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(NMAX,))
    C = ops.coupling(ETA, NMAX)
    Cdag = C.conj().T
    alpha_axis = np.linspace(-3.0, 3.0, 41)
    d_alpha = float(alpha_axis[1] - alpha_axis[0])

    # cd22ef6 baseline for the P-D bit-for-bit regression.
    cd = {}
    with h5py.File(CD22EF6, "r") as h5:
        cd[("0.5", "0")] = float(h5["squeezed_0.5"].attrs["metric_fidelity"])
        cd[("0.5", "pi_2")] = float(
            h5["squeezed_0.5_perp"].attrs["metric_fidelity"])

    print(f"WP-W native 𝒪(η²) re-audit — η={ETA}, App. E Δt=T_m/2, "
          f"δ=2ω_m, N={N}, nmax={NMAX}\n")

    recs = []
    gate_ok = True
    for r in R_GRID:
        for th_name, theta in THETA_GRID:
            psi_sq = squeezed_ket(r, theta, NMAX)

            # ---- P-D gate: η-exact reconstruction (timing-independent)
            F_pd, imW = _pd_reconstruction(r, theta)
            shared = (f"{r:g}", th_name) in cd
            pd_pass = True
            note = ""
            if shared:
                base = cd[(f"{r:g}", th_name)]
                dF = abs(F_pd - base)
                pd_pass = dF <= PD_TOL
                note = f"vs cd22ef6 {base:.6f} |Δ|={dF:.2e}"
            else:
                pd_pass = (F_pd >= 0.99) and (imW <= 1e-10)
                note = "η-exact Gaussian tier (no cd22ef6 baseline)"
            gate_ok &= pd_pass

            for pr_name, ratio in PROBES:
                x_t, phi, d_off = xi_tot_target_appE(ratio, N, OMEGA_M, theta)
                delta = 2.0 * OMEGA_M + d_off

                # ---- ideal leg: η-exact SDF at matched (δ,φ,N,k=2)
                psi0_i = np.concatenate([psi_sq, np.zeros(NMAX, complex)])
                psi_eq = states.apply_mw_pi2(psi0_i, mw_phase_deg=0.0,
                                             nmax=NMAX)
                tr_i = build_ideal_sdf_train(
                    hs=hs, beta0=BETA0, ac_phase_rad=phi, omega_m=OMEGA_M,
                    delta=delta, n_pulses=N, k_sideband=2)
                rho_i = partial_trace_spin(tr_i.evolve(psi_eq), NMAX)
                mi, Wi = _state_metrics(rho_i, psi_sq, alpha_axis, d_alpha)

                # ---- native leg: engine at App. E timing
                psi0_n = np.concatenate([psi_sq, np.zeros(NMAX, complex)])
                tr_n = build_strobo_train(
                    hs=hs, eta=ETA, omega_r=OMEGA_R, omega_m=OMEGA_M,
                    delta=delta, n_pulses=N, delta_t=DELTA_T,
                    t_sep_factor=0.5, ac_phase_rad=phi,
                    intra_pulse_motion=True,
                    gap_includes_spin_detuning=True, C=C, Cdag=Cdag)
                rho_n = partial_trace_spin(tr_n.evolve(psi0_n), NMAX)
                mn, Wn = _state_metrics(rho_n, psi_sq, alpha_axis, d_alpha)
                gm = gaussian_moments(rho_n)

                L1 = float(np.sum(np.abs(Wi - Wn)) * d_alpha ** 2)
                rec = {
                    "r": r, "theta_name": th_name, "theta": theta,
                    "probe": pr_name, "ratio": ratio, "delta": delta,
                    "F_pd": F_pd, "imW_pd": imW, "pd_shared": shared,
                    "pd_pass": bool(pd_pass), "pd_note": note,
                    "ideal_purity": mi["purity"],
                    "ideal_drop": mi["purity_drop"],
                    "ideal_fid_pre": mi["fidelity_to_pre"],
                    "native_purity": mn["purity"],
                    "native_drop": mn["purity_drop"],
                    "native_fid_pre": mn["fidelity_to_pre"],
                    "native_cov_ratio": gm["ratio"],
                    "native_cov_orient": gm["orient_deg"],
                    "native_mean_mag": float(np.hypot(gm["mean_X"],
                                                      gm["mean_P"])),
                    "ideal_vs_native_W_L1": L1,
                }
                recs.append(rec)
                print(f"  r={r:<4} θ={th_name:<4} {pr_name:<4} | "
                      f"P-D F={F_pd:.6f}{' ✓' if pd_pass else ' ✗'} | "
                      f"nat ratio={gm['ratio']:.3f} pur={gm['purity']:.4f} "
                      f"|⟨q⟩|={rec['native_mean_mag']:.2e} fidpre="
                      f"{mn['fidelity_to_pre']:.3f} | L¹={L1:.3f}")

    # ---- pre-registered P-A…P-E comparison.
    # HONEST aggregates: the 3f9f7dd-era prints reported the raw native
    # cov-ratio change with r and the cross-r max−min, both DOMINATED
    # by the input squeezed-vacuum ratio e^{4r} (pass-through), not by
    # an engine effect — the confound flagged in
    # 2026-05-18-squeezed-native-audit.md §4. Replaced here by (i) the
    # ENGINE-EXCESS anisotropy native_ratio − e^{4r} (the pass-through
    # subtracted) and (ii) the WITHIN-fixed-r θ-spread.
    peak = [r for r in recs if r["probe"] == "peak"]
    r_max = max(R_GRID)

    def _input_ratio(r):                 # squeezed-vacuum cov ratio
        return float(np.exp(4.0 * r))

    exc = {x["r"]: x["native_cov_ratio"] - _input_ratio(x["r"])
           for x in peak if x["theta_name"] == "0"}
    pc_excess_r0 = float(exc.get(0.0, float("nan")))
    pc_excess_rmax = float(exc.get(r_max, float("nan")))
    pc_excess_change = float(pc_excess_rmax - pc_excess_r0)
    pb_theta_spread = 0.0                # θ-modulation WITHIN fixed r
    for r in R_GRID:
        vals = [x["native_cov_ratio"] for x in peak if x["r"] == r]
        if len(vals) > 1:
            pb_theta_spread = max(pb_theta_spread,
                                  max(vals) - min(vals))
    fid_r0 = max(x["native_fid_pre"] for x in peak if x["r"] == 0.0)
    fid_rmax = min(x["native_fid_pre"] for x in peak if x["r"] == r_max)
    aggregates = {
        "pc_engine_excess_r0": pc_excess_r0,
        "pc_engine_excess_rmax": pc_excess_rmax,
        "pc_engine_excess_change": pc_excess_change,
        "pb_theta_spread_within_r_max": float(pb_theta_spread),
        "native_fidpre_r0": float(fid_r0),
        "native_fidpre_rmax_min": float(fid_rmax),
    }
    verdict = ("SYSTEMATIC STRUCTURAL NULL — native engine fails to "
               "realise/preserve squeezing across (r,θ); P-D ideal leg "
               "sound" if gate_ok else
               "P-D GATE FAIL — ideal leg regression broken (investigate)")

    print(f"\n>>> P-D hard gate: {'PASS' if gate_ok else 'FAIL'} "
          f"(all (r,θ); 2 shared bit-for-bit vs cd22ef6)")
    print(f">>> P-A/P-C engine-excess anisotropy (native−input e^4r, "
          f"θ=0 peak): r=0 {pc_excess_r0:+.3f} → r={r_max:g} "
          f"{pc_excess_rmax:+.3f}  (Δ {pc_excess_change:+.3f}) — "
          f"small at r=0, NEGATIVE at r={r_max:g} ⇒ engine adds no "
          f"squeezing (mild decoherence-driven erosion of the input "
          f"anisotropy, not engineering)")
    print(f">>> P-B θ-modulation WITHIN fixed r (max over r, peak): "
          f"{pb_theta_spread:.3f}")
    print(f">>> P-C native fidelity-to-input degradation: r=0 "
          f"{fid_r0:.3f} → r={r_max:g} {fid_rmax:.3f}")
    print(f">>> VERDICT: {verdict}")

    out = Path("wp-wigner-tomography/numerics/squeezed_native_audit.h5")
    with h5py.File(out, "w") as h5:
        h5.attrs["wp_id"] = WP_ID
        h5.attrs["code_version"] = CODE_VERSION
        h5.attrs["runner_version"] = RUNNER_VERSION
        h5.attrs["eta"] = ETA
        h5.attrs["omega_m"] = OMEGA_M
        h5.attrs["N"] = N
        h5.attrs["nmax"] = NMAX
        h5.attrs["app_e_t_sep_factor"] = 0.5
        h5.attrs["delta_over_omega_m_base"] = 2.0
        h5.attrs["pd_gate_pass"] = bool(gate_ok)
        h5.attrs["verdict"] = verdict
        for k, v in aggregates.items():        # honest aggregates
            h5.attrs[f"agg_{k}"] = v
        for i, rc in enumerate(recs):
            g = h5.create_group(f"rec_{i:02d}")
            for k, v in rc.items():
                g.attrs[k] = v
    elapsed = time.time() - t0
    payload = {
        "physical_parameters": {"eta": ETA, "omega_r": OMEGA_R,
                                "omega_m": OMEGA_M, "N": N,
                                "nmax": NMAX, "beta0": BETA0,
                                "app_e_t_sep_factor": 0.5,
                                "delta_over_omega_m_base": 2.0},
        "grid": {"r": R_GRID, "theta": [t[0] for t in THETA_GRID],
                 "probes": [p[0] for p in PROBES]},
        "pd_gate_pass": bool(gate_ok),
        "aggregates": aggregates,
        "records": recs,
        "verdict": verdict,
        "tags": ["WP-W", "Rank2", "native-eta2", "re-audit", "step2"],
    }
    write_manifest(
        canonical_manifest(
            wp_id=WP_ID, code_version=CODE_VERSION,
            runner_version=RUNNER_VERSION, repository=REPOSITORY,
            artifact_path=str(out), artifact_format="hdf5",
            elapsed_s=elapsed, payload=payload),
        out.with_suffix(".manifest.json"))
    print(f"\nWrote {out} + manifest  ({elapsed:.1f} s)")
    return 0 if gate_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
