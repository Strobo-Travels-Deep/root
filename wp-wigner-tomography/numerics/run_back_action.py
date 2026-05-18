"""WP-W v0.6 — motional back-action diagnostic (Rank-1 follow-up).

Scope: `notes/back_action_scope.md` (LOCKED 2026-05-16). This runner
measures the *post-train motional state* ρ_m^(post) — what the
analysis train costs the oscillator — for the ideal FH20-style σ_x
SDF and the native Raman engine, side by side.

Pre-registered conventions (logged here per the WP-W "state
conventions explicitly before declaring" discipline; cf. D4 Layer A
guardrail):

  * **Ideal SDF** U = D(σ_x β_tot/2); branch separation β_tot, each
    branch displaced ±β_tot/2 (analytic_chain.md §1, scope §2).
  * **Comb tooth k** — default k=0 (carrier) matches the P1 / D3 /
    D4-Layer-B inverse-Dirichlet convention used throughout WP-W.
    The k=1 sideband follow-up uses the same matched-control
    diagnostic at the first red/blue sideband tooth to expose the
    native engine's JC-like motional back-action.
  * **Matched physical control, not β_eff** (scope §4a). The β_tot
    probe points are defined on the *ideal leg* via the
    inverse-Dirichlet rule. The native leg runs the D4-Layer-A pinned
    WP-E v0.9.1 train at the *same* (δ−kω_m, φ_train, N). The
    ideal-vs-native Wigner L¹ is a *structural* residual at matched
    drive — not a β_eff calibration (forbidden by §7#3 /
    analytic_chain.md §5).
  * **Native-leg state prep**: spin |↓⟩ (NO separate MW π/2 — the
    train accumulates π/2 via the Ω_R calibration; D4 Layer A
    Corrections 4–5), motional input prepared directly in the lab
    frame (θ=0). **No input-state phase shift is applied to any
    input, on either leg** (uniform lab frame). The D4-Layer-A
    `shift_deg = ω_m·δt/2` was a *pulse-centering compensation to
    reproduce an external WP-E reference scan at a coherent state*;
    this diagnostic has no external reference and is a *matched-
    control structural comparison*, which requires both legs to see
    the **identical** input in the same frame. shift_deg is
    phase-symmetric for vacuum / Fock |2⟩ anyway (no-op); applying
    it to the native cat *only* would rotate the cat relative to the
    ideal cat and break matched control (conflating an input
    difference with the propagator difference being measured). It is
    therefore deliberately not applied — the cat axis is on the real
    line for both legs.
  * **Probe points** (per state): peak |β_tot| = N·β₀ (x=0,
    on-resonance, max back-action) and mid-branch |β_tot| = N·β₀/2.
  * **Inputs**: default vacuum, Fock |2⟩, cat |α|=1.5 (all pure;
    scope §3 decision 2). Follow-up runs may add coherent states
    (for example `coherent2`) because the native sideband
    collapse–revival effect is most naturally exposed on coherent
    inputs.
  * **Readouts**: unconditional ρ_m^(post) (headline) + all three
    conditional bases σ_{x,y,z} (scope §3 decision 1).

GATE (the *only* hard PASS/FAIL — back-action analogue of P0/P1,
scope §5/§6): vacuum, ideal SDF, |+y⟩ in →
  purity   Tr[(ρ_m^post)²]   = ½(1 + e^{−|β_tot|²})
  fidelity ⟨0|ρ_m^post|0⟩    = e^{−|β_tot|²/4}
  Wigner   W(ρ_m^post)       = W_mixed_cat(α, β_tot/2)
to ≤ 1e-6 (Fock-truncation floor at nmax=60 is ≲4e-8; a convention
or orientation bug is O(0.05–0.3) — the tolerance discriminates).
If the gate fails the diagnostic is not trusted and the runner
aborts non-zero before writing the full sweep.

Usage:
    python wp-wigner-tomography/numerics/run_back_action.py
    python wp-wigner-tomography/numerics/run_back_action.py --k-sideband 1
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import h5py
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(Path(__file__).parent))

from stroboscopic import HilbertSpace, build_strobo_train, states
from stroboscopic import operators as ops
from stroboscopic.ideal_sdf import build_ideal_sdf_train

from _common import (
    RUNNER_VERSION,
    W_mixed_cat,
    canonical_manifest,
    cat_ket,
    conditional_motional_ket,
    inverse_dirichlet,
    partial_trace_spin,
    wigner_from_rho,
    write_manifest,
)

WP_ID = "wigner-tomography"
CODE_VERSION = "0.6.2"
REPOSITORY = "https://github.com/Strobo-Travels-Deep/root"

# D4-Layer-A pinned WP-E v0.9.1 native parameters (run_bridge_native.py).
ETA = 0.397
OMEGA_R = 0.09016606431708851
DELTA_T = 0.6283185307179586  # = 0.13 · T_m at ω_m = 1.3


def tooth_label(k: int) -> str:
    """Human-readable comb-tooth label for reports and manifests."""
    if int(k) == 0:
        return "carrier"
    if int(k) == 1:
        return "first sideband"
    if int(k) == -1:
        return "negative first sideband"
    return f"k={int(k)} comb tooth"


def default_output_for_k(k: int) -> str:
    """Default artifact path that preserves the parked k=0 result."""
    if int(k) == 0:
        return "wp-wigner-tomography/numerics/back_action.h5"
    return f"wp-wigner-tomography/numerics/back_action_k{int(k)}.h5"


def inverse_dirichlet_target(ratio: float, N: int, omega_m: float,
                             theta: float = 0.0) -> tuple[float, float, float]:
    """(x, φ_train, δ−kω_m) so the ideal-SDF train delivers |β_tot| = ratio·β₀.

    ratio = |β_tot|/β₀ ∈ [0, N]; θ = arg β_tot (0 ⇒ β_tot real +).
    arg β₀ = 0, arg 𝒟_N(x) = (N−1)x/2 on the monotone branch ⇒
    φ_train = θ − (N−1)x/2. Returns x in rad and the detuning offset
    (δ − kω_m) in physical units.
    """
    x = inverse_dirichlet(N, ratio)
    phi_train = (theta - (N - 1) * x / 2.0) % (2.0 * np.pi)
    T_m = 2.0 * np.pi / omega_m
    return float(x), float(phi_train), float(x / T_m)


def motional_input(kind: str, nmax: int) -> np.ndarray:
    """Lab-frame motional ket for the v0.6 input subset (all pure)."""
    if kind == "vacuum":
        return states.fock_state(0, nmax)
    if kind == "fock2":
        return states.fock_state(2, nmax)
    if kind == "cat1.5":
        return cat_ket(1.5 + 0j, nmax, parity=+1)
    if kind.startswith("fock"):
        n_s = kind[len("fock"):].lstrip("_")
        if not n_s:
            raise ValueError("fock input must include a level, e.g. fock1")
        return states.fock_state(int(n_s), nmax)
    if kind.startswith("coherent"):
        alpha_s = kind[len("coherent"):].lstrip("_")
        if not alpha_s:
            raise ValueError("coherent input must include an amplitude, e.g. coherent2")
        return states.coherent_state(float(alpha_s), 0.0, nmax)
    raise ValueError(f"unknown input {kind!r}")


def thermal_terms(nbar: float, nmax: int, tol: float = 1e-6):
    """Thermal ρ = Σ pₙ|n⟩⟨n| as a truncated, renormalised ket list.

    pₙ = n̄ⁿ/(1+n̄)^{n+1} = p·rⁿ with p=1/(1+n̄), r=n̄/(1+n̄). The tail
    after keeping n=0..M is exactly r^{M+1}; pick the smallest M with
    r^{M+1} ≤ tol (scope §8 Decision A; n̄=0.5 ⇒ 13 terms). Kept
    weights are renormalised; the discarded tail mass is returned for
    honest reporting.
    """
    p0 = 1.0 / (1.0 + nbar)
    r = nbar / (1.0 + nbar)
    M = 0
    while r ** (M + 1) > tol and M < nmax - 1:
        M += 1
    raw = np.array([p0 * r ** n for n in range(M + 1)], dtype=np.float64)
    tail = float(1.0 - raw.sum())
    w = raw / raw.sum()
    terms = [(float(wi), states.fock_state(n, nmax))
             for n, wi in enumerate(w)]
    return terms, {"pre_kind": "thermal", "nbar": float(nbar),
                   "n_terms": M + 1, "discarded_tail": tail}


def motional_input_terms(kind: str, nmax: int):
    """Input as a weighted ket list [(wᵢ,|φᵢ⟩)], Σwᵢ=1 (scope §8 A).

    Pure inputs → a single (1.0, ket) term so the existing pure
    pipeline is reused verbatim (byte-identical regression). Mixed
    inputs → genuinely multi-term.
    """
    if kind.startswith("thermal"):
        nbar = float(kind[len("thermal"):].lstrip("_"))
        return thermal_terms(nbar, nmax)
    if kind.startswith("mixed_cat"):
        a = float(kind[len("mixed_cat"):].lstrip("_"))
        return ([(0.5, states.coherent_state(a, 0.0, nmax)),
                 (0.5, states.coherent_state(a, 180.0, nmax))],
                {"pre_kind": "mixed_cat", "alpha": a})
    return [(1.0, motional_input(kind, nmax))], {"pre_kind": "pure"}


def rho_pre_of_terms(terms, nmax: int) -> np.ndarray:
    """ρ_m^pre = Σ wᵢ |φᵢ⟩⟨φᵢ| (single-term ⇒ exactly |φ⟩⟨φ|)."""
    rho = np.zeros((nmax, nmax), dtype=np.complex128)
    for w, ket in terms:
        rho += w * np.outer(ket, np.conj(ket))
    return rho


def mixed_conditional_rho(outs, nmax, basis, s):
    """Conditional motional ρ for a mixed input + total outcome prob.

    ρ_cond,s = Σ wᵢ (M_s|φᵢ⟩)(M_s|φᵢ⟩)† / P(s),  P(s)=Σ wᵢ ‖M_s|φᵢ⟩‖².
    `conditional_motional_ket` returns (normalised ket, prob=‖proj‖²),
    so the unnormalised projected vector is √probᵢ · ketᵢ.
    """
    acc = np.zeros((nmax, nmax), dtype=np.complex128)
    P = 0.0
    for w, po in outs:
        ket_i, prob_i = conditional_motional_ket(po, nmax, basis, s)
        comp = np.sqrt(prob_i) * ket_i
        acc += w * np.outer(comp, np.conj(comp))
        P += w * prob_i
    if P < 1e-15:
        return np.zeros((nmax, nmax), dtype=np.complex128), float(P)
    return acc / P, float(P)


def evolve_ideal(psi_m, *, hs, nmax, beta0, N, omega_m, k, x, phi_train):
    """|↓⟩ψ_m → MW π/2 (|+y⟩) → ideal-SDF train; return ψ_out."""
    psi0 = np.concatenate([psi_m, np.zeros(nmax, dtype=np.complex128)])
    psi_eq = states.apply_mw_pi2(psi0, mw_phase_deg=0.0, nmax=nmax)
    delta = k * omega_m + x / (2.0 * np.pi / omega_m)
    train = build_ideal_sdf_train(
        hs=hs, beta0=beta0, ac_phase_rad=phi_train, omega_m=omega_m,
        delta=delta, n_pulses=N, k_sideband=k,
    )
    return train.evolve(psi_eq)


def evolve_native(psi_m, *, hs, nmax, N, omega_m, k, x, phi_train, C, Cdag):
    """|↓⟩ψ_m (NO MW π/2) → D4-Layer-A WP-E native train; return ψ_out."""
    psi0 = np.concatenate([psi_m, np.zeros(nmax, dtype=np.complex128)])
    delta = k * omega_m + x / (2.0 * np.pi / omega_m)
    train = build_strobo_train(
        hs=hs, eta=ETA, omega_r=OMEGA_R, omega_m=omega_m, delta=delta,
        n_pulses=N, delta_t=DELTA_T, t_sep_factor=1.0,
        ac_phase_rad=phi_train, intra_pulse_motion=True,
        gap_includes_spin_detuning=True, C=C, Cdag=Cdag,
    )
    return train.evolve(psi0)


def neg_volume(W: np.ndarray, d_alpha: float) -> float:
    """∫ min(0, W) d²α — Wigner negativity volume (≤ 0)."""
    return float(np.sum(np.minimum(0.0, W)) * d_alpha ** 2)


def state_metrics(psi_out, psi_m_pre, nmax, alpha_axis, d_alpha,
                   want_wigner=True):
    """Unconditional ρ_m^post metrics + (optionally) its Wigner."""
    rho = partial_trace_spin(psi_out, nmax)
    purity = float(np.real(np.trace(rho @ rho)))
    fid_pre = float(np.real(np.vdot(psi_m_pre, rho @ psi_m_pre)))
    out = {"purity": purity, "purity_drop": 1.0 - purity,
           "fidelity_to_pre": fid_pre}
    if want_wigner:
        W, err = wigner_from_rho(rho, alpha_axis)
        out["W"] = W
        out["W_err_imag"] = err
        out["neg_volume"] = neg_volume(W, d_alpha)
    return rho, out


def conditional_metrics(psi_out, nmax, beta_tot, psi_m_pre):
    """All six σ_{x,y,z}=±1 conditional kets: prob + σ_x branch fidelity.

    For the *ideal* leg the σ_x outcomes select single displaced
    branches D(±β_tot/2)|ψ_m_pre⟩ — branch_fid quantifies that.
    """
    from _common import _displacement
    res = {}
    for basis in ("x", "y", "z"):
        for s in (+1, -1):
            ket, prob = conditional_motional_ket(psi_out, nmax, basis, s)
            entry = {"prob": prob}
            if basis == "x" and prob > 1e-12:
                tgt = _displacement(s * beta_tot / 2.0, nmax) @ psi_m_pre
                entry["branch_fidelity"] = float(abs(np.vdot(tgt, ket)) ** 2)
            res[f"{basis}{'+' if s > 0 else '-'}"] = entry
    return res


def run_vacuum_gate(*, hs, nmax, beta0, N, omega_m, k, points,
                    alpha_axis, d_alpha, tol) -> tuple[bool, list[dict]]:
    """The only hard PASS/FAIL (scope §5/§6). Vacuum, ideal SDF, |+y⟩."""
    print("=" * 66)
    print("VACUUM ANALYTIC GATE (ideal SDF) — the only hard PASS/FAIL")
    print("=" * 66)
    psi_m = states.fock_state(0, nmax)
    rows, ok = [], True
    for name, ratio in points:
        x, phi, _ = inverse_dirichlet_target(ratio, N, omega_m)
        beta_tot = ratio * beta0  # real +, θ = 0 by construction
        psi_out = evolve_ideal(psi_m, hs=hs, nmax=nmax, beta0=beta0, N=N,
                               omega_m=omega_m, k=k, x=x, phi_train=phi)
        rho = partial_trace_spin(psi_out, nmax)
        purity = float(np.real(np.trace(rho @ rho)))
        fid = float(np.real(np.vdot(psi_m, rho @ psi_m)))
        W, werr = wigner_from_rho(rho, alpha_axis)
        AX, AY = np.meshgrid(alpha_axis, alpha_axis)
        W_tgt = W_mixed_cat(AX + 1j * AY, (beta_tot / 2.0) + 0j)
        p_tgt = 0.5 * (1.0 + np.exp(-beta_tot ** 2))
        f_tgt = np.exp(-beta_tot ** 2 / 4.0)
        dp, df = abs(purity - p_tgt), abs(fid - f_tgt)
        dW = float(np.max(np.abs(W - W_tgt)))
        passed = (dp <= tol) and (df <= tol) and (dW <= tol)
        ok &= passed
        print(f"  {name:>5}  |β_tot|={beta_tot:.4f}")
        print(f"    purity   {purity:.10f} vs ½(1+e^-|β|²)={p_tgt:.10f}  |Δ|={dp:.2e}")
        print(f"    fidelity {fid:.10f} vs e^-|β|²/4   ={f_tgt:.10f}  |Δ|={df:.2e}")
        print(f"    max|ΔW| vs W_mixed_cat(β_tot/2) = {dW:.2e}  (W_im={werr:.1e})")
        print(f"    -> {'PASS' if passed else 'FAIL'} @ tol {tol:.0e}")
        rows.append({"point": name, "beta_tot": beta_tot,
                     "purity": purity, "purity_target": float(p_tgt),
                     "purity_resid": float(dp),
                     "fidelity": fid, "fidelity_target": float(f_tgt),
                     "fidelity_resid": float(df),
                     "W_max_resid": dW, "W_err_imag": float(werr),
                     "pass": bool(passed)})
    print(f"\nGATE {'PASS' if ok else 'FAIL'}\n")
    return ok, rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--beta0", type=float, default=0.05)
    ap.add_argument("--omega-m", type=float, default=1.3)
    ap.add_argument("--N", type=int, default=30)
    ap.add_argument("--k-sideband", type=int, default=0)
    ap.add_argument("--nmax", type=int, default=60)
    ap.add_argument("--alpha-window", type=float, default=3.0)
    ap.add_argument("--alpha-points", type=int, default=41)
    ap.add_argument("--gate-alpha-window", type=float, default=3.0,
                    help="phase-space half-window used only by the hard "
                         "vacuum Wigner gate; keep at the validated v0.6 "
                         "value when plotting wider reporting windows")
    ap.add_argument("--gate-alpha-points", type=int, default=41,
                    help="number of points on the hard-gate alpha axis")
    ap.add_argument("--gate-tol", type=float, default=1e-6)
    ap.add_argument("--inputs", nargs="+",
                    default=["vacuum", "fock2", "cat1.5"],
                    help="pure motional inputs to run; known names include "
                         "vacuum, fock2, cat1.5, coherent2")
    ap.add_argument("--output", type=str, default=None,
                    help="output HDF5 path; defaults to back_action.h5 for k=0 "
                         "and back_action_k{K}.h5 otherwise")
    args = ap.parse_args()

    t0 = time.time()
    nmax, N, k, b0, wm = args.nmax, args.N, args.k_sideband, args.beta0, args.omega_m
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(nmax,))
    C = ops.coupling(ETA, nmax)
    Cdag = C.conj().T
    alpha_axis = np.linspace(-args.alpha_window, args.alpha_window,
                             args.alpha_points)
    d_alpha = float(alpha_axis[1] - alpha_axis[0])
    gate_alpha_axis = np.linspace(-args.gate_alpha_window,
                                  args.gate_alpha_window,
                                  args.gate_alpha_points)
    gate_d_alpha = float(gate_alpha_axis[1] - gate_alpha_axis[0])

    points = [("peak", float(N)), ("mid", float(N) / 2.0)]
    inputs = list(args.inputs)

    tlabel = tooth_label(k)
    if args.output is None:
        args.output = default_output_for_k(k)

    print(f"WP-W v0.6 back-action — N={N}, β₀={b0}, k={k} ({tlabel}), "
          f"nmax={nmax}, α∈[-{args.alpha_window},{args.alpha_window}]²"
          f" ({args.alpha_points}², Δα={d_alpha:.3f})\n")
    if (args.gate_alpha_window != args.alpha_window
            or args.gate_alpha_points != args.alpha_points):
        print("  hard-gate Wigner axis: "
              f"α∈[-{args.gate_alpha_window},{args.gate_alpha_window}]²"
              f" ({args.gate_alpha_points}², Δα={gate_d_alpha:.3f})\n")

    gate_ok, gate_rows = run_vacuum_gate(
        hs=hs, nmax=nmax, beta0=b0, N=N, omega_m=wm, k=k, points=points,
        alpha_axis=gate_alpha_axis, d_alpha=gate_d_alpha, tol=args.gate_tol)
    if not gate_ok:
        print("ABORT: vacuum gate failed — diagnostic not trusted.")
        return 1

    # Per-input weighted ket lists (scope §8 A). Pure = single (1,ket)
    # term ⇒ the existing pure pipeline is reused verbatim below.
    terms_by, premeta_by, W_pre, pre_purity = {}, {}, {}, {}
    for inp in inputs:
        terms, meta = motional_input_terms(inp, nmax)
        terms_by[inp] = terms
        premeta_by[inp] = meta
        rho_pre = rho_pre_of_terms(terms, nmax)
        pre_purity[inp] = float(np.real(np.trace(rho_pre @ rho_pre)))
        Wp, _ = wigner_from_rho(rho_pre, alpha_axis)
        W_pre[inp] = Wp
        if meta.get("pre_kind") == "thermal":
            print(f"  thermal n̄={meta['nbar']}: {meta['n_terms']} Fock "
                  f"terms, discarded tail = {meta['discarded_tail']:.2e}")

    print("=" * 66)
    print("DIAGNOSTIC SWEEP  (reported, not gated)")
    print("=" * 66)
    records = []
    for inp in inputs:
        terms = terms_by[inp]
        pure = len(terms) == 1
        ppre = pre_purity[inp]
        for pname, ratio in points:
            x, phi, _ = inverse_dirichlet_target(ratio, N, wm)
            beta_tot = ratio * b0
            leg_W = {}
            for leg in ("ideal", "native"):
                def _evolve(ket):
                    if leg == "ideal":
                        return evolve_ideal(ket, hs=hs, nmax=nmax, beta0=b0,
                                            N=N, omega_m=wm, k=k, x=x,
                                            phi_train=phi)
                    return evolve_native(ket, hs=hs, nmax=nmax, N=N,
                                         omega_m=wm, k=k, x=x,
                                         phi_train=phi, C=C, Cdag=Cdag)
                if pure:
                    # ---- pure path: existing primitives, verbatim ----
                    pm = terms[0][1]
                    psi_out = _evolve(pm)
                    rho, m = state_metrics(psi_out, pm, nmax, alpha_axis,
                                           d_alpha, want_wigner=True)
                    cond = conditional_metrics(psi_out, nmax, beta_tot, pm)
                    cond_W = None
                    if pname == "peak":
                        ky, _p = conditional_motional_ket(psi_out, nmax,
                                                          "y", +1)
                        cond_W, _ = wigner_from_rho(
                            np.outer(ky, np.conj(ky)), alpha_axis)
                    purity = m["purity"]
                    rec = {"input": inp, "point": pname, "leg": leg,
                           "beta_tot": beta_tot, "x": x, "phi_train": phi,
                           "purity": purity, "purity_drop": m["purity_drop"],
                           "fidelity_to_pre": m["fidelity_to_pre"],
                           "neg_volume": m["neg_volume"],
                           "pre_purity": ppre,
                           "purity_drop_vs_pre": ppre - purity,
                           "W": m["W"], "W_err_imag": m["W_err_imag"],
                           "cond": cond, "cond_W_sy_plus": cond_W}
                else:
                    # ---- mixed path: weighted-density-matrix sum ----
                    outs = [(w, _evolve(ket)) for w, ket in terms]
                    rho = np.zeros((nmax, nmax), dtype=np.complex128)
                    for w, po in outs:
                        rho += w * partial_trace_spin(po, nmax)
                    purity = float(np.real(np.trace(rho @ rho)))
                    rho_pre = rho_pre_of_terms(terms, nmax)
                    fid = float(np.real(np.trace(rho_pre @ rho)))
                    W, werr = wigner_from_rho(rho, alpha_axis)
                    cond = {}
                    for basis in ("x", "y", "z"):
                        for s in (+1, -1):
                            rc, P = mixed_conditional_rho(outs, nmax,
                                                          basis, s)
                            cond[f"{basis}{'+' if s > 0 else '-'}"] = {
                                "prob": P,
                                "purity": float(np.real(np.trace(rc @ rc)))}
                            # branch_fidelity intentionally omitted (mixed
                            # input has no single ψ_pre; scope §8 C)
                    cond_W = None
                    if pname == "peak":
                        rc_y, _P = mixed_conditional_rho(outs, nmax, "y", +1)
                        cond_W, _ = wigner_from_rho(rc_y, alpha_axis)
                    rec = {"input": inp, "point": pname, "leg": leg,
                           "beta_tot": beta_tot, "x": x, "phi_train": phi,
                           "purity": purity, "purity_drop": 1.0 - purity,
                           "fidelity_to_pre": fid,
                           "neg_volume": neg_volume(W, d_alpha),
                           "pre_purity": ppre,
                           "purity_drop_vs_pre": ppre - purity,
                           "W": W, "W_err_imag": float(werr),
                           "cond": cond, "cond_W_sy_plus": cond_W}
                leg_W[leg] = rec["W"]
                records.append(rec)
                bx = rec["cond"].get("x+", {}).get("branch_fidelity")
                print(f"  {inp:>10} {pname:>4} {leg:>6}: "
                      f"purity={rec['purity']:.4f} "
                      f"drop_vs_pre={rec['purity_drop_vs_pre']:.4f} "
                      f"F_pre={rec['fidelity_to_pre']:.4f} "
                      f"neg={rec['neg_volume']:+.4f}"
                      + (f" σx-branchF={bx:.4f}" if bx is not None
                         else "  (σx-branchF N/A: mixed)" if not pure
                         else ""))
            # Structural ideal-vs-native L¹ on the unconditional W.
            l1 = float(np.sum(np.abs(leg_W["ideal"] - leg_W["native"]))
                       * d_alpha ** 2)
            for rec in records:
                if rec["input"] == inp and rec["point"] == pname:
                    rec["ideal_vs_native_W_L1"] = l1
            print(f"  {inp:>10} {pname:>4}  ideal-vs-native W L¹ = {l1:.4e}"
                  f"  (structural residual, §4a)")

    elapsed = time.time() - t0
    print(f"\nWall: {elapsed:.1f} s")

    # ---- HDF5 ----
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(out_path, "w") as h5:
        h5.attrs["wp_id"] = WP_ID
        h5.attrs["code_version"] = CODE_VERSION
        h5.attrs["runner_version"] = RUNNER_VERSION
        h5.attrs["N"] = N
        h5.attrs["beta0"] = b0
        h5.attrs["k_sideband"] = k
        h5.attrs["omega_m"] = wm
        h5.attrs["nmax"] = nmax
        h5.attrs["alpha_window"] = args.alpha_window
        h5.attrs["alpha_points"] = args.alpha_points
        h5.attrs["gate_pass"] = bool(gate_ok)
        h5.attrs["gate_tol"] = args.gate_tol
        h5.attrs["gate_alpha_window"] = args.gate_alpha_window
        h5.attrs["gate_alpha_points"] = args.gate_alpha_points
        h5.attrs["inputs_json"] = json.dumps(inputs)
        h5.create_dataset("alpha_axis", data=alpha_axis)
        g = h5.create_group("gate")
        for i, r in enumerate(gate_rows):
            gg = g.create_group(f"point_{i}")
            for kk, vv in r.items():
                gg.attrs[kk] = vv
        for inp in inputs:
            h5.create_dataset(f"W_pre/{inp}", data=W_pre[inp])
        pmg = h5.create_group("pre_meta")
        for inp in inputs:
            pg = pmg.create_group(inp)
            pg.attrs["pre_purity"] = pre_purity[inp]
            for mk, mv in premeta_by[inp].items():
                pg.attrs[mk] = mv
        for i, r in enumerate(records):
            grp = h5.create_group(f"rec_{i:02d}")
            for kk, vv in r.items():
                if kk == "W":
                    grp.create_dataset("W", data=vv)
                elif kk == "cond_W_sy_plus":
                    if vv is not None:
                        grp.create_dataset("cond_W_sy_plus", data=vv)
                elif kk == "cond":
                    cg = grp.create_group("cond")
                    for ck, cv in vv.items():
                        cgg = cg.create_group(ck)
                        for cck, ccv in cv.items():
                            cgg.attrs[cck] = ccv
                else:
                    grp.attrs[kk] = vv

    payload = {
        "conventions": {
            "ideal_sdf": "U=D(sigma_x beta_tot/2); branch sep beta_tot",
            "comb_tooth_k": k,
            "k_note": (
                "carrier (k=0) — matches P1/D3/D4-LayerB"
                if k == 0 else
                f"{tooth_label(k)} (k={k}) — sideband follow-up at matched "
                "physical control; native leg exposes JC-like motional "
                "back-action rather than carrier-dominated response"
            ),
            "native_leg": "D4-Layer-A pinned WP-E v0.9.1; matched physical control, not beta_eff (scope §4a, §7#3)",
            "native_eta": ETA, "native_omega_r": OMEGA_R,
            "native_delta_t": DELTA_T,
            "native_state_prep": "spin |down>, no separate MW pi/2; NO input-state phase shift on either leg (uniform lab frame). shift_deg was a D4-Layer-A external-reference device, not applied here: phase-symmetric for vacuum/Fock, and deliberately not applied to the cat (a cat-only shift would break matched control by rotating the native cat vs the ideal cat).",
        },
        "physical_parameters": {"beta0": b0, "omega_m": wm, "N": N,
                                "nmax": nmax,
                                "alpha_window": args.alpha_window,
                                "alpha_points": args.alpha_points,
                                "gate_alpha_window": args.gate_alpha_window,
                                "gate_alpha_points": args.gate_alpha_points},
        "inputs": inputs,
        "pre_meta": {inp: {**premeta_by[inp],
                           "pre_purity": pre_purity[inp]}
                     for inp in inputs},
        "points": {p: r for p, r in points},
        "gate": {"tol": args.gate_tol, "pass": bool(gate_ok),
                 "rows": gate_rows,
                 "criteria": "purity=½(1+e^-|β|²), fidelity=e^-|β|²/4, "
                             "W=W_mixed_cat(β_tot/2); back-action P0/P1 analogue"},
        "summary": [
            {kk: vv for kk, vv in r.items()
             if kk not in ("W", "cond_W_sy_plus", "cond")}
            for r in records
        ],
        "overall_pass": bool(gate_ok),
        "tags": ["WP-W", "v0.6", "back-action", "ideal-SDF", "native-bridge"],
    }
    manifest = canonical_manifest(
        wp_id=WP_ID, code_version=CODE_VERSION,
        runner_version=RUNNER_VERSION, repository=REPOSITORY,
        artifact_path=str(out_path), artifact_format="hdf5",
        elapsed_s=elapsed, payload=payload)
    write_manifest(manifest, out_path.with_suffix(".manifest.json"))
    print(f"Wrote {out_path} + manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
