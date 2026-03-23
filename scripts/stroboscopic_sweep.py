#!/usr/bin/env python3
"""
stroboscopic_sweep.py — Systematic simulation engine for the Breakwater Dossier.

Stroboscopic detuning-scan simulation for Hasse et al., PRA 109, 053105 (2024).
Ion species: ²⁵Mg⁺. Full Fock-basis exact evolution (no Lamb-Dicke truncation).

Modes:
    single_run          — one parameter set, one detuning scan
    sweep_1d            — sweep one parameter across a grid
    state_comparison    — compare multiple initial states at fixed parameters

All output follows manifest schema v2.0.
Status: systematic (Float64 throughout).

Requirements:
    pip install numpy scipy qutip

Usage:
    python stroboscopic_sweep.py                    # run default examples
    python stroboscopic_sweep.py --mode single_run  # single run with defaults
    python stroboscopic_sweep.py --mode sweep_1d --sweep-param n_pulses --sweep-values 5,10,22,50
    python stroboscopic_sweep.py --mode state_comparison

Repository: https://github.com/threehouse-plus-ec/open-research-platform
"""

import argparse
import hashlib
import json
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.linalg import expm

CODE_VERSION = "0.8.0"
REPO = "https://github.com/threehouse-plus-ec/open-research-platform"
SOURCE_PAPER = {
    "journal": "Phys. Rev. A 109, 053105 (2024)",
    "doi": "10.1103/PhysRevA.109.053105",
    "arxiv": "2309.15580",
}

# ═══════════════════════════════════════════════════════════════
# Default parameters
# ═══════════════════════════════════════════════════════════════

DEFAULTS = dict(
    alpha=3.0,
    alpha_phase_deg=0.0,
    eta=0.397,
    omega_m=1.3,        # MHz (cyclic, i.e. /(2π))
    omega_r=0.300,       # MHz
    n_thermal=0.0,
    n_thermal_traj=1,
    nmax=50,
    squeeze_r=0.0,
    squeeze_phi_deg=0.0,
    theta_deg=0.0,       # spin polar angle (0 = |↓⟩)
    phi_deg=0.0,         # spin azimuthal
    det_min=-6.0,
    det_max=6.0,
    npts=201,
    n_pulses=22,
    t_sep_factor=1.0,    # 1.0 = stroboscopic
    T1=0.0,              # μs, 0 = off
    T2=0.0,
    heating=0.0,         # quanta/ms
    n_traj=1,
    n_rep=0,             # 0 = ideal (no projection noise)
    fock_n=None,         # if set, use Fock |n⟩ instead of coherent state
)


# ═══════════════════════════════════════════════════════════════
# Physics engine
# ═══════════════════════════════════════════════════════════════

def build_operators(nmax):
    """Build motional annihilation and position operators."""
    a = np.zeros((nmax, nmax), dtype=complex)
    for n in range(nmax - 1):
        a[n, n + 1] = np.sqrt(n + 1)
    adag = a.conj().T
    X = a + adag  # position quadrature (a + a†)
    return a, adag, X


def build_coupling(eta, nmax, X=None):
    """Build C = exp(iη(a + a†)) exactly in Fock basis."""
    if X is None:
        _, _, X = build_operators(nmax)
    C = expm(1j * eta * X)
    return C


def coherent_state(alpha_abs, alpha_phase_deg, nmax):
    """Coherent state D(α)|0⟩ in Fock basis."""
    theta = np.radians(alpha_phase_deg)
    alpha = alpha_abs * np.exp(1j * theta)
    psi = np.zeros(nmax, dtype=complex)
    psi[0] = np.exp(-abs(alpha) ** 2 / 2)
    for n in range(1, nmax):
        psi[n] = psi[n - 1] * alpha / np.sqrt(n)
    return psi


def fock_state(n, nmax):
    """Fock state |n⟩."""
    psi = np.zeros(nmax, dtype=complex)
    if n < nmax:
        psi[n] = 1.0
    return psi


def squeeze_operator(r, phi_deg, nmax):
    """Squeeze operator S(r,φ) as matrix."""
    if r == 0:
        return np.eye(nmax, dtype=complex)
    phi = np.radians(phi_deg)
    a, adag, _ = build_operators(nmax)
    # S = exp[(r/2)(e^{-2iφ} a² − e^{2iφ} (a†)²)]
    e2phi = np.exp(2j * phi)
    gen = (r / 2) * (np.conj(e2phi) * a @ a - e2phi * adag @ adag)
    return expm(gen)


def displacement_operator(alpha_abs, alpha_phase_deg, nmax):
    """Displacement operator D(α) as matrix."""
    if alpha_abs == 0:
        return np.eye(nmax, dtype=complex)
    theta = np.radians(alpha_phase_deg)
    alpha = alpha_abs * np.exp(1j * theta)
    a, adag, _ = build_operators(nmax)
    gen = alpha * adag - np.conj(alpha) * a
    return expm(gen)


def prepare_motional(params):
    """Prepare motional state: S(r,φ) D(α) |n⟩."""
    nmax = params["nmax"]

    # Base state
    if params.get("fock_n") is not None:
        psi = fock_state(params["fock_n"], nmax)
    elif params["n_thermal"] > 0:
        # Sample from Bose-Einstein distribution
        nbar = params["n_thermal"]
        p = 1.0 / (1.0 + nbar)
        n = min(int(np.log(np.random.random()) / np.log(1 - p)), nmax - 1)
        psi = fock_state(n, nmax)
    else:
        psi = fock_state(0, nmax)

    # Displacement
    if params["alpha"] > 0 or params.get("fock_n") is not None:
        if params.get("fock_n") is not None and params["alpha"] > 0:
            D = displacement_operator(params["alpha"], params["alpha_phase_deg"], nmax)
            psi = D @ psi
        elif params.get("fock_n") is None:
            psi = coherent_state(params["alpha"], params["alpha_phase_deg"], nmax)

    # Squeeze
    if params["squeeze_r"] > 0:
        S = squeeze_operator(params["squeeze_r"], params["squeeze_phi_deg"], nmax)
        psi = S @ psi

    return psi


def tensor_spin_motion(theta_deg, phi_deg, psi_m, nmax):
    """Full state |ψ_spin⟩ ⊗ |ψ_mot⟩ in the 2*nmax basis."""
    theta = np.radians(theta_deg)
    phi = np.radians(phi_deg)
    c_down = np.cos(theta / 2)
    c_up = np.sin(theta / 2) * np.exp(1j * phi)

    dim = 2 * nmax
    psi = np.zeros(dim, dtype=complex)
    psi[:nmax] = c_down * psi_m          # |↓⟩ block
    psi[nmax:] = c_up * psi_m            # |↑⟩ block
    return psi


def build_hamiltonian(eta, omega_r, delta, nmax, C, Cdag):
    """Build H_eff in the 2*nmax spin⊗motion basis."""
    dim = 2 * nmax
    H = np.zeros((dim, dim), dtype=complex)

    # Detuning: -δ/2 on ↓↓, +δ/2 on ↑↑
    for n in range(nmax):
        H[n, n] = -delta / 2
        H[nmax + n, nmax + n] = delta / 2

    # Coupling: (Ω/2)(C ⊗ σ₋ + C† ⊗ σ₊)
    H[:nmax, nmax:] = (omega_r / 2) * C        # ↓↑ block (σ₋)
    H[nmax:, :nmax] = (omega_r / 2) * Cdag     # ↑↓ block (σ₊)

    return H


def compute_observables(psi, nmax):
    """Compute spin and motional observables from the full state vector."""
    # Reduced spin density matrix
    rho_dd = np.sum(np.abs(psi[:nmax]) ** 2)
    rho_uu = np.sum(np.abs(psi[nmax:]) ** 2)
    rho_du = np.sum(np.conj(psi[:nmax]) * psi[nmax:])

    sx = 2 * rho_du.real
    sy = -2 * rho_du.imag
    sz = rho_uu - rho_dd
    coh = np.sqrt(sx**2 + sy**2 + sz**2)

    # Entropy
    r = np.sqrt(4 * np.abs(rho_du) ** 2 + (rho_uu - rho_dd) ** 2)
    lp, lm = (1 + r) / 2, (1 - r) / 2
    ent = 0.0
    if lp > 1e-15:
        ent -= lp * np.log2(lp)
    if lm > 1e-15:
        ent -= lm * np.log2(lm)

    # Motional <n>
    ns = np.arange(nmax)
    nbar = np.sum(ns * np.abs(psi[:nmax]) ** 2) + np.sum(ns * np.abs(psi[nmax:]) ** 2)

    # Motional purity Tr(ρ_m²)
    # ρ_m(i,j) = ψ*(↓,i)ψ(↓,j) + ψ*(↑,i)ψ(↑,j)
    rho_m = np.outer(np.conj(psi[:nmax]), psi[:nmax]) + \
            np.outer(np.conj(psi[nmax:]), psi[nmax:])
    purity = np.real(np.trace(rho_m @ rho_m))

    return dict(
        sigma_x=sx, sigma_y=sy, sigma_z=sz,
        coherence=coh, entropy=ent,
        nbar=nbar, mot_purity=purity,
    )


def motional_fidelity(psi, psi_m_init, nmax):
    """Fidelity of final motional state with initial: F = ⟨ψ_init|ρ_m|ψ_init⟩."""
    ov_down = np.dot(np.conj(psi_m_init), psi[:nmax])
    ov_up = np.dot(np.conj(psi_m_init), psi[nmax:])
    return float(np.abs(ov_down) ** 2 + np.abs(ov_up) ** 2)


def fock_leakage(psi, nmax):
    """Population in top 3 Fock states (both spin components)."""
    leak = 0.0
    for n in range(max(0, nmax - 3), nmax):
        leak += np.abs(psi[n]) ** 2 + np.abs(psi[nmax + n]) ** 2
    return leak


def collapse_step(psi, nmax, Tm, gamma1, gamma_phi, gamma_h):
    """One quantum trajectory collapse step during inter-pulse free evolution."""
    dim = 2 * nmax

    # Jump probabilities
    p_up = np.sum(np.abs(psi[nmax:]) ** 2)
    dp1 = gamma1 * Tm * p_up

    dp2 = (gamma_phi / 2) * Tm

    ns = np.arange(nmax, dtype=float)
    expect_np1 = np.sum((ns + 1) * np.abs(psi[:nmax]) ** 2) + \
                 np.sum((ns + 1) * np.abs(psi[nmax:]) ** 2)
    dp3 = gamma_h * Tm * expect_np1

    # Clamp total probability
    total = dp1 + dp2 + dp3
    if total > 0.95:
        scale = 0.95 / total
        dp1 *= scale
        dp2 *= scale
        dp3 *= scale

    r = np.random.random()

    if r < dp1 and dp1 > 0:
        # Spin decay: σ₋ ⊗ I
        out = np.zeros(dim, dtype=complex)
        out[:nmax] = psi[nmax:]  # |↑⟩ → |↓⟩
        return out / np.linalg.norm(out)

    if r < dp1 + dp2 and dp2 > 0:
        # Pure dephasing: σ_z ⊗ I
        out = psi.copy()
        out[:nmax] = -psi[:nmax]  # flip sign on |↓⟩
        return out / np.linalg.norm(out)

    if r < dp1 + dp2 + dp3 and dp3 > 0:
        # Motional heating: I ⊗ a†
        out = np.zeros(dim, dtype=complex)
        for n in range(nmax - 1):
            sq = np.sqrt(n + 1)
            out[n + 1] += sq * psi[n]
            out[nmax + n + 1] += sq * psi[nmax + n]
        return out / np.linalg.norm(out)

    # No jump: apply non-Hermitian correction
    out = psi.copy()
    for n in range(nmax):
        s1 = gamma1 * Tm / 2
        out[nmax + n] -= s1 * psi[nmax + n]

        s2 = (gamma_phi / 2) * Tm / 2
        out[n] -= s2 * psi[n]
        out[nmax + n] -= s2 * psi[nmax + n]

        s3 = gamma_h * (n + 1) * Tm / 2
        out[n] -= s3 * psi[n]
        out[nmax + n] -= s3 * psi[nmax + n]

    return out / np.linalg.norm(out)


def projection_noise(ideal_value, n_rep):
    """Binomial projection noise sampling."""
    if n_rep <= 0:
        return ideal_value, 0.0
    p = np.clip((1 + ideal_value) / 2, 1e-10, 1 - 1e-10)
    successes = np.random.binomial(n_rep, p)
    noisy = 2 * (successes / n_rep) - 1
    err = 2 * np.sqrt(p * (1 - p) / n_rep)
    return noisy, err


# ═══════════════════════════════════════════════════════════════
# Parameter type enforcement
# ═══════════════════════════════════════════════════════════════

# Parameters that must be integers (used in range(), array indexing, etc.)
_INT_PARAMS = {"nmax", "n_pulses", "npts", "n_traj", "n_rep", "n_thermal_traj", "fock_n"}


def _enforce_types(params):
    """Cast integer-valued parameters from float to int. Returns a new dict."""
    out = dict(params)
    for k in _INT_PARAMS:
        if k in out and out[k] is not None:
            out[k] = int(out[k])
    return out


# ═══════════════════════════════════════════════════════════════
# Single-run engine
# ═══════════════════════════════════════════════════════════════

def run_single(params, verbose=True):
    """Execute one detuning scan. Returns (data_dict, convergence_dict)."""
    p = _enforce_types({**DEFAULTS, **params})
    nmax = p["nmax"]
    dim = 2 * nmax

    omega_eff = p["omega_r"] * np.exp(-p["eta"] ** 2 / 2)
    dt = np.pi / (2 * p["n_pulses"] * omega_eff)
    Tm = 2 * np.pi / p["omega_m"]
    Tsep = Tm * p["t_sep_factor"]

    # Decoherence rates
    gamma1 = 1.0 / p["T1"] if p["T1"] > 0 else 0.0
    gamma_phi_raw = 1.0 / p["T2"] if p["T2"] > 0 else 0.0
    gamma_phi = max(0.0, gamma_phi_raw - gamma1 / 2)
    gamma_h = p["heating"] / 1000 if p["heating"] > 0 else 0.0
    use_deco = gamma1 > 0 or gamma_phi > 0 or gamma_h > 0

    use_thermal = p["n_thermal"] > 0
    n_th_traj = p["n_thermal_traj"] if use_thermal else 1
    n_deco_traj = p["n_traj"] if use_deco else 1
    total_traj = n_th_traj * n_deco_traj

    # Build operators
    _, _, X = build_operators(nmax)
    C = build_coupling(p["eta"], nmax, X)
    Cdag = C.conj().T

    # Free evolution operator (non-stroboscopic case)
    need_free = abs(p["t_sep_factor"] - 1.0) > 1e-6
    if need_free:
        phase_per_n = 2 * np.pi * p["t_sep_factor"]
        Ufree = np.zeros((dim, dim), dtype=complex)
        for n in range(nmax):
            ph = np.exp(-1j * n * phase_per_n)
            Ufree[n, n] = ph
            Ufree[nmax + n, nmax + n] = ph
    else:
        Ufree = None

    # Detuning grid
    dets = np.linspace(p["det_min"], p["det_max"], p["npts"])

    # Output arrays
    keys = ["sigma_x", "sigma_y", "sigma_z", "coherence", "entropy",
            "nbar", "mot_purity", "mot_fidelity"]
    data = {"detuning": dets.tolist()}
    arrays = {k: np.zeros(p["npts"]) for k in keys}
    noisy_arrays = {}
    if p["n_rep"] > 0:
        for k in ["sigma_x", "sigma_y", "sigma_z"]:
            noisy_arrays[f"noisy_{k}"] = np.zeros(p["npts"])
            noisy_arrays[f"err_{k}"] = np.zeros(p["npts"])

    max_leak = 0.0

    for i, det_rel in enumerate(dets):
        delta = det_rel * p["omega_m"]
        H = build_hamiltonian(p["eta"], p["omega_r"], delta, nmax, C, Cdag)
        U = expm(-1j * H * dt)

        accum = {k: 0.0 for k in keys}

        for _ in range(n_th_traj):
            psi_m = prepare_motional(p)
            psi0 = tensor_spin_motion(p["theta_deg"], p["phi_deg"], psi_m, nmax)

            for _ in range(n_deco_traj):
                psi = psi0.copy()
                for pulse in range(p["n_pulses"]):
                    psi = U @ psi
                    if pulse < p["n_pulses"] - 1:
                        if need_free:
                            psi = Ufree @ psi
                        if use_deco:
                            psi = collapse_step(psi, nmax, Tsep,
                                                gamma1, gamma_phi, gamma_h)

                obs = compute_observables(psi, nmax)
                fid = motional_fidelity(psi, psi_m, nmax)
                obs["mot_fidelity"] = fid

                for k in keys:
                    accum[k] += obs[k]

                leak = fock_leakage(psi, nmax)
                if leak > max_leak:
                    max_leak = leak

        for k in keys:
            arrays[k][i] = accum[k] / total_traj

        if p["n_rep"] > 0:
            for k in ["sigma_x", "sigma_y", "sigma_z"]:
                n_val, n_err = projection_noise(arrays[k][i], p["n_rep"])
                noisy_arrays[f"noisy_{k}"][i] = n_val
                noisy_arrays[f"err_{k}"][i] = n_err

        if verbose and (i + 1) % max(1, p["npts"] // 10) == 0:
            print(f"  point {i + 1}/{p['npts']}", flush=True)

    for k in keys:
        data[k] = arrays[k].tolist()
    for k, v in noisy_arrays.items():
        data[k] = v.tolist()

    convergence = {
        "max_fock_leakage": float(max_leak),
        "converged": max_leak < 0.01,
    }

    return data, convergence


# ═══════════════════════════════════════════════════════════════
# Manifest and provenance
# ═══════════════════════════════════════════════════════════════

def compute_derived(params):
    """Compute derived quantities from parameters."""
    p = {**DEFAULTS, **params}
    omega_eff = p["omega_r"] * np.exp(-p["eta"] ** 2 / 2)
    return {
        "omega_eff": omega_eff,
        "debye_waller": np.exp(-p["eta"] ** 2 / 2),
        "n_mean": p["alpha"] ** 2,
        "hilbert_dim": 2 * p["nmax"],
    }


def _json_default(o):
    """JSON serialiser for numpy types."""
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"Object of type {type(o).__name__} not serialisable")


def compute_hash(obj):
    """SHA-256 of JSON-serialised object."""
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=_json_default)
    return hashlib.sha256(raw.encode()).hexdigest()


def build_manifest(mode, status, payload, elapsed_s):
    """Build a v2.0 manifest envelope."""
    manifest = {
        "schema_version": "2.0",
        "mode": mode,
        "status": status,
        "code_version": CODE_VERSION,
        "repository": REPO,
        "source_paper": SOURCE_PAPER,
        "endorsement_marker": "Local candidate framework",
        "execution": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engine": "python-scipy",
            "precision": "float64",
            "elapsed_s": round(elapsed_s, 2),
        },
        "provenance_hash": "",
        "payload": payload,
    }
    manifest["provenance_hash"] = compute_hash({
        "code_version": CODE_VERSION,
        "mode": mode,
        "payload": payload,
    })
    return manifest


# ═══════════════════════════════════════════════════════════════
# Mode: single_run
# ═══════════════════════════════════════════════════════════════

def mode_single_run(params=None, output_path=None):
    """Run a single detuning scan and save."""
    p = {**DEFAULTS, **(params or {})}
    print(f"[single_run] α={p['alpha']}, η={p['eta']}, N_p={p['n_pulses']}, "
          f"N_max={p['nmax']}, {p['npts']} pts")

    t0 = time.time()
    data, conv = run_single(p)
    elapsed = time.time() - t0

    payload = {
        "parameters": {k: v for k, v in p.items() if v is not None},
        "derived": compute_derived(p),
        "convergence": conv,
        "data": data,
    }

    manifest = build_manifest("single_run", "systematic", payload, elapsed)

    if output_path is None:
        output_path = f"single_alpha{p['alpha']:.0f}.json"
    Path(output_path).write_text(json.dumps(manifest, indent=2, default=_json_default))
    print(f"  ✓ {output_path} ({elapsed:.1f}s, hash={manifest['provenance_hash'][:12]}…)")
    return manifest


# ═══════════════════════════════════════════════════════════════
# Mode: sweep_1d
# ═══════════════════════════════════════════════════════════════

def mode_sweep_1d(sweep_param, sweep_values, fixed_params=None, output_path=None):
    """Sweep one parameter across a grid of values."""
    fp = {**DEFAULTS, **(fixed_params or {})}
    n_vals = len(sweep_values)

    print(f"[sweep_1d] {sweep_param} = {sweep_values}")
    print(f"  fixed: α={fp['alpha']}, η={fp['eta']}, N_p={fp['n_pulses']}, "
          f"N_max={fp['nmax']}, {fp['npts']} pts")

    t0 = time.time()
    runs = []
    convergences = []
    summaries = {"contrast_z": [], "peak_purity": [], "peak_fidelity": []}

    for vi, val in enumerate(sweep_values):
        p = deepcopy(fp)
        p[sweep_param] = val
        print(f"  [{vi + 1}/{n_vals}] {sweep_param}={val}")

        data, conv = run_single(p, verbose=False)
        convergences.append(conv)

        run_entry = {"sweep_value": val}
        for k in ["sigma_x", "sigma_y", "sigma_z", "coherence", "entropy",
                   "nbar", "mot_purity", "mot_fidelity"]:
            if k in data:
                run_entry[k] = data[k]
        runs.append(run_entry)

        sz = np.array(data["sigma_z"])
        summaries["contrast_z"].append(float((sz.max() - sz.min()) / 2))
        if "mot_purity" in data:
            summaries["peak_purity"].append(float(max(data["mot_purity"])))
        if "mot_fidelity" in data:
            summaries["peak_fidelity"].append(float(max(data["mot_fidelity"])))

    elapsed = time.time() - t0

    payload = {
        "fixed_parameters": {k: v for k, v in fp.items() if v is not None},
        "sweep": {
            "parameter": sweep_param,
            "values": [float(v) for v in sweep_values],
            "n_values": n_vals,
        },
        "convergence_per_value": convergences,
        "data": {
            "detuning": np.linspace(fp["det_min"], fp["det_max"], fp["npts"]).tolist(),
            "runs": runs,
        },
        "summary": summaries,
    }

    manifest = build_manifest("sweep_1d", "systematic", payload, elapsed)

    if output_path is None:
        output_path = f"sweep_{sweep_param}.json"
    Path(output_path).write_text(json.dumps(manifest, indent=2, default=_json_default))
    print(f"  ✓ {output_path} ({elapsed:.1f}s, {n_vals} runs, "
          f"hash={manifest['provenance_hash'][:12]}…)")
    return manifest


# ═══════════════════════════════════════════════════════════════
# Mode: state_comparison
# ═══════════════════════════════════════════════════════════════

# Gallery of standard states
# Only include optional fields when they carry a value (schema compliance).
STATE_GALLERY = [
    {"id": "ground", "label": "Ground |0⟩",
     "alpha": 0},
    {"id": "coherent_1", "label": "Coherent α=1",
     "alpha": 1},
    {"id": "coherent_3", "label": "Coherent α=3",
     "alpha": 3},
    {"id": "coherent_5", "label": "Coherent α=5",
     "alpha": 5},
    {"id": "fock_1", "label": "Fock |1⟩",
     "alpha": 0, "fock_n": 1},
    {"id": "fock_3", "label": "Fock |3⟩",
     "alpha": 0, "fock_n": 3},
    {"id": "squeezed_05", "label": "Squeezed r=0.5",
     "alpha": 0, "squeeze_r": 0.5},
    {"id": "squeezed_10", "label": "Squeezed r=1.0",
     "alpha": 0, "squeeze_r": 1.0},
    {"id": "thermal_3", "label": "Thermal n̄=3",
     "alpha": 0, "n_thermal": 3.0, "n_thermal_traj": 20},
    {"id": "thermal_9", "label": "Thermal n̄=9",
     "alpha": 0, "n_thermal": 9.0, "n_thermal_traj": 20},
]


def spectral_distance(spec_a, spec_b, detunings):
    """Integrated spectral distance between two spectra.

    D = √( (1/N) Σ_i Σ_obs (a_obs(i) - b_obs(i))² )

    where obs ∈ {σ_x, σ_y, σ_z}.
    """
    dist_sq = 0.0
    n_pts = len(detunings)
    for obs in ["sigma_x", "sigma_y", "sigma_z"]:
        if obs in spec_a and obs in spec_b:
            a = np.array(spec_a[obs])
            b = np.array(spec_b[obs])
            dist_sq += np.sum((a - b) ** 2) / n_pts
    return float(np.sqrt(dist_sq))


def mode_state_comparison(states=None, fixed_params=None, output_path=None):
    """Compare multiple initial states at fixed parameters."""
    if states is None:
        # Default: ground, coherent α=3, Fock |3⟩, squeezed r=1.0, thermal n̄=9
        states = [STATE_GALLERY[i] for i in [0, 2, 5, 7, 9]]

    fp = {**DEFAULTS, **(fixed_params or {})}
    n_states = len(states)

    print(f"[state_comparison] {n_states} states")
    for s in states:
        print(f"  · {s['label']}")

    t0 = time.time()
    spectra = []
    convergences = []

    for si, state_def in enumerate(states):
        p = deepcopy(fp)
        # Override motional state parameters from state definition
        for k in ["alpha", "alpha_phase_deg", "squeeze_r", "squeeze_phi_deg",
                   "n_thermal", "n_thermal_traj", "fock_n"]:
            if k in state_def:
                p[k] = state_def[k]

        print(f"  [{si + 1}/{n_states}] {state_def['label']}")
        data, conv = run_single(p, verbose=False)
        convergences.append(conv)

        spectrum = {"state_id": state_def["id"]}
        for k in ["sigma_x", "sigma_y", "sigma_z", "coherence", "entropy",
                   "nbar", "mot_purity", "mot_fidelity"]:
            if k in data:
                spectrum[k] = data[k]
        spectra.append(spectrum)

    # Pairwise distinguishability
    state_ids = [s["id"] for s in states]
    dets = np.linspace(fp["det_min"], fp["det_max"], fp["npts"])
    dist_matrix = np.zeros((n_states, n_states))
    for i in range(n_states):
        for j in range(i + 1, n_states):
            d = spectral_distance(spectra[i], spectra[j], dets)
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d

    elapsed = time.time() - t0

    payload = {
        "parameters": {k: v for k, v in fp.items() if v is not None},
        "states": [{k: v for k, v in s.items() if v is not None} for s in states],
        "convergence_per_state": convergences,
        "data": {
            "detuning": dets.tolist(),
            "spectra": spectra,
        },
        "distinguishability": {
            "metric": "integrated_spectral_distance",
            "matrix": dist_matrix.tolist(),
            "state_ids": state_ids,
        },
    }

    manifest = build_manifest("state_comparison", "systematic", payload, elapsed)

    if output_path is None:
        output_path = "state_comparison.json"
    Path(output_path).write_text(json.dumps(manifest, indent=2, default=_json_default))

    # Print distance matrix
    print(f"\n  Distinguishability matrix (integrated spectral distance):")
    header = "         " + "  ".join(f"{s[:8]:>8}" for s in state_ids)
    print(f"  {header}")
    for i, sid in enumerate(state_ids):
        row = "  ".join(f"{dist_matrix[i, j]:8.4f}" for j in range(n_states))
        print(f"  {sid[:8]:>8}  {row}")

    print(f"\n  ✓ {output_path} ({elapsed:.1f}s, {n_states} states, "
          f"hash={manifest['provenance_hash'][:12]}…)")
    return manifest


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Stroboscopic sweep engine — Breakwater Dossier v0.8")
    parser.add_argument("--mode", default="single_run",
                        choices=["single_run", "sweep_1d", "state_comparison"])
    parser.add_argument("--alpha", type=float, default=None)
    parser.add_argument("--eta", type=float, default=None)
    parser.add_argument("--n-pulses", type=int, default=None)
    parser.add_argument("--nmax", type=int, default=None)
    parser.add_argument("--npts", type=int, default=None)
    parser.add_argument("--sweep-param", type=str, default="n_pulses")
    parser.add_argument("--sweep-values", type=str, default="5,10,22,50",
                        help="Comma-separated values for sweep_1d")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    # Build parameter overrides from CLI
    overrides = {}
    if args.alpha is not None:
        overrides["alpha"] = args.alpha
    if args.eta is not None:
        overrides["eta"] = args.eta
    if args.n_pulses is not None:
        overrides["n_pulses"] = args.n_pulses
    if args.nmax is not None:
        overrides["nmax"] = args.nmax
    if args.npts is not None:
        overrides["npts"] = args.npts

    if args.mode == "single_run":
        mode_single_run(overrides, args.output)

    elif args.mode == "sweep_1d":
        values = [float(v.strip()) for v in args.sweep_values.split(",")]
        mode_sweep_1d(args.sweep_param, values, overrides, args.output)

    elif args.mode == "state_comparison":
        mode_state_comparison(fixed_params=overrides, output_path=args.output)


if __name__ == "__main__":
    main()
