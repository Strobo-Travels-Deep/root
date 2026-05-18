"""WP-W shared numerics helpers.

Functions:
    dirichlet_magnitude(N, x)        — |D_N(x)| at angular argument x
    inverse_dirichlet(N, ratio)      — solve |D_N(x)| = ratio on the central lobe
    chi_vacuum(beta)                 — χ for the motional ground state
    chi_coherent(beta, alpha)        — χ for a coherent state |α⟩
    contrast_from_chi(beta, chi)     — C(β) = e^{-|β|²/2} χ(β) (ideal-SDF prefactor)
    wigner_from_chi(chi, beta_axis)  — 2D-FFT inversion χ → W on the α grid
    partial_trace_spin(psi, nmax)    — physical reduced motional ρ_m (back-action)
    conditional_motional_ket(...)    — σ_{x,y,z} post-selected motional ket + prob
    wigner_from_rho(rho, alpha_axis) — parity-form W = (2/π)Tr[ρ D Π D†]
    cat_ket(alpha, nmax, parity)     — normalised (|α⟩ ± |-α⟩) cat ket
    sha256_of_file(path)             — file digest for manifest binding
    canonical_manifest(...)          — assemble the wp_manifest_v1 envelope
    write_manifest(...)              — write the sidecar JSON

Conventions follow WORK-PROGRAM.md §2 / §Analytical:
    - β₀ taken real positive (arg β₀ = 0). The phase convention φ_train =
      θ − arg β₀ − arg 𝒟_N(x) then collapses to φ_train = θ − (N−1)x/2 on
      the monotone branch.
    - χ(β) = ⟨α|D̂(β)|α⟩ = e^{-|β|²/2} · e^{2i Im(α* β)} for coherent input.
    - W(α) = π⁻² ∫ e^{αβ* − α*β} χ(β) d²β.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.linalg import expm
from scipy.optimize import brentq
from scipy.special import eval_laguerre


RUNNER_VERSION = "0.1.0"


# ---------------------------------------------------------------------------
# Dirichlet kernel and its inverse on the central monotone branch
# ---------------------------------------------------------------------------

def dirichlet_magnitude(N: int, x: float) -> float:
    """|𝒟_N(x)| = |sin(N x / 2) / sin(x / 2)|, with 𝒟_N(0) = N."""
    if abs(x) < 1e-12:
        return float(N)
    return abs(np.sin(N * x / 2.0) / np.sin(x / 2.0))


def inverse_dirichlet(N: int, ratio: float) -> float:
    """Solve |𝒟_N(x)| = ratio on the monotone branch 0 ≤ x ≤ 2π/N.

    Parameters
    ----------
    N : int
        Number of pulses.
    ratio : float
        Desired |𝒟_N(x)|, in [0, N]. The function clamps small numerical
        excess at the peak (ratio ≥ N) to x = 0.

    Returns
    -------
    x : float
        Solution in [0, 2π/N]. Raises ValueError if ratio < 0.
    """
    if ratio < 0:
        raise ValueError(f"ratio must be non-negative, got {ratio}")
    if ratio >= N - 1e-9:
        return 0.0
    if ratio < 1e-12:
        return 2.0 * np.pi / N
    # f(x) = |𝒟_N(x)| − ratio; monotonically decreasing on (0, 2π/N).
    def f(x):
        return dirichlet_magnitude(N, x) - ratio
    return brentq(f, 1e-9, 2.0 * np.pi / N - 1e-9, xtol=1e-12)


# ---------------------------------------------------------------------------
# Characteristic functions on the β grid
# ---------------------------------------------------------------------------

def chi_vacuum(beta: np.ndarray) -> np.ndarray:
    """χ_vac(β) = e^{-|β|²/2}."""
    return np.exp(-np.abs(beta) ** 2 / 2.0)


def chi_coherent(beta: np.ndarray, alpha: complex) -> np.ndarray:
    """χ_{|α⟩}(β) = e^{-|β|²/2} · e^{2i Im(α* β)}."""
    phase = 2.0 * np.imag(np.conj(alpha) * beta)
    return np.exp(-np.abs(beta) ** 2 / 2.0) * np.exp(1j * phase)


def contrast_from_chi(beta: np.ndarray, chi: np.ndarray) -> np.ndarray:
    """C(β) = e^{-|β|²/2} · χ(β) — the ideal-SDF spin-contrast observable."""
    return np.exp(-np.abs(beta) ** 2 / 2.0) * chi


# ---------------------------------------------------------------------------
# χ for the full WP-W test-state set (D3)
# ---------------------------------------------------------------------------

def chi_thermal(beta: np.ndarray, n_bar: float) -> np.ndarray:
    """χ_th(β) = exp(-(2·n̄+1)|β|²/2)."""
    return np.exp(-(2.0 * n_bar + 1.0) * np.abs(beta) ** 2 / 2.0)


def chi_fock(beta: np.ndarray, n: int) -> np.ndarray:
    """χ_n(β) = exp(-|β|²/2) · L_n(|β|²)."""
    r2 = np.abs(beta) ** 2
    return np.exp(-r2 / 2.0) * eval_laguerre(n, r2)


def chi_cat(beta: np.ndarray, alpha: complex) -> np.ndarray:
    """χ for the even pure cat (|α⟩ + |-α⟩)/N with N² = 2(1 + e^{-2|α|²}).

    Decomposed into diagonal and off-diagonal contributions:
        χ_diag = (2/N²) e^{-|β|²/2} cos(2 Im(α* β))
        χ_off  = (2/N²) e^{-2|α|² - |β|²/2} cosh(2 Re(α* β))

    The off-diagonal cosh argument is real (Re(α*β), *not* α*β) — the
    BCH phase factor e^{-i Im(α*β)} on ⟨α|D(β)|-α⟩ exactly cancels the
    imaginary part of ⟨α|β-α⟩, leaving the entire χ Hermitian:
    χ(-β) = χ*(β) = χ(β) (real for real α; real-valued more generally
    because both diag and off are real).
    """
    a = complex(alpha)
    a2 = np.abs(a) ** 2
    norm_sq = 2.0 * (1.0 + np.exp(-2.0 * a2))
    diag = 2.0 * np.exp(-np.abs(beta) ** 2 / 2.0) * np.cos(2.0 * np.imag(np.conj(a) * beta))
    off = 2.0 * np.exp(-2.0 * a2 - np.abs(beta) ** 2 / 2.0) * np.cosh(2.0 * np.real(np.conj(a) * beta))
    return (diag + off) / norm_sq


def chi_mixed_cat(beta: np.ndarray, alpha: complex) -> np.ndarray:
    """χ for the incoherent mixture ρ_mc = (|α⟩⟨α| + |-α⟩⟨-α|)/2.

    Equivalent to the diagonal half of `chi_cat` without the off-diagonal
    coherence term, and is the quantum-vs-classical control state per §7#4:
        χ_mc(β) = e^{-|β|²/2} cos(2 Im(α* β))
    """
    a = complex(alpha)
    return np.exp(-np.abs(beta) ** 2 / 2.0) * np.cos(2.0 * np.imag(np.conj(a) * beta))


def chi_squeezed(beta: np.ndarray, r: float, theta: float = 0.0) -> np.ndarray:
    """χ for squeezed vacuum S(ξ)|0⟩, ξ = r e^{iθ}, S = exp[½(ξ*a² − ξ a†²)].

        χ_{|r,θ⟩}(β) = exp[ −½ ( |β|² cosh 2r + Re(β² e^{−iθ}) sinh 2r ) ]

    Derivation: S†aS = a cosh r − a† e^{iθ} sinh r ⇒ S†D(β)S = D(γ) with
    γ = β cosh r + β* e^{iθ} sinh r, so χ = ⟨0|D(γ)|0⟩ = e^{−|γ|²/2} and
    |γ|² = |β|² cosh 2r + Re(β² e^{−iθ}) sinh 2r. Reduces to χ_vacuum at
    r = 0. For θ = 0 this is exp[−½(β_x² e^{+2r} + β_y² e^{−2r})] —
    narrow along β_x, broad (∝ e^{+r}) along β_y, consistent with the
    state being squeezed in X (Var X = e^{−2r}). χ is real and even, so
    χ(−β) = χ*(β) = χ(β) (Hermiticity). The cross-term sign is **+**:
    this matches the exact ⟨r,θ|D(β)|r,θ⟩ to machine precision (see
    notes/squeezed_eta2_scope.md §3, incl. the lock-pass sign correction).
    """
    b2 = np.abs(beta) ** 2
    cross = np.real(beta ** 2 * np.exp(-1j * theta))
    return np.exp(-0.5 * (b2 * np.cosh(2.0 * r) + cross * np.sinh(2.0 * r)))


# ---------------------------------------------------------------------------
# Analytic Wigner functions on the α grid (ground truth for D3 metrics)
# ---------------------------------------------------------------------------

def W_vacuum(alpha: np.ndarray) -> np.ndarray:
    """W_vac(γ) = (2/π) e^{-2|γ|²}."""
    return (2.0 / np.pi) * np.exp(-2.0 * np.abs(alpha) ** 2)


def W_coherent(alpha: np.ndarray, alpha0: complex) -> np.ndarray:
    """W_{|α₀⟩}(γ) = (2/π) e^{-2|γ-α₀|²}."""
    return (2.0 / np.pi) * np.exp(-2.0 * np.abs(alpha - complex(alpha0)) ** 2)


def W_thermal(alpha: np.ndarray, n_bar: float) -> np.ndarray:
    """W_th(γ) = (2 / (π (2n̄+1))) e^{-2|γ|² / (2n̄+1)}."""
    s = 2.0 * n_bar + 1.0
    return (2.0 / (np.pi * s)) * np.exp(-2.0 * np.abs(alpha) ** 2 / s)


def W_fock(alpha: np.ndarray, n: int) -> np.ndarray:
    """W_n(γ) = (2/π)(-1)^n L_n(4|γ|²) e^{-2|γ|²}."""
    r2 = np.abs(alpha) ** 2
    return (2.0 / np.pi) * (-1) ** n * eval_laguerre(n, 4.0 * r2) * np.exp(-2.0 * r2)


def W_cat(alpha: np.ndarray, alpha0: complex) -> np.ndarray:
    """W for the even pure cat (|α₀⟩ + |-α₀⟩)/N.

    W(γ) = (2/π) · (e^{-2|γ-α₀|²} + e^{-2|γ+α₀|²} + 2 e^{-2|γ|²} cos(4 Im(α₀* γ))) / N²
    with N² = 2(1 + e^{-2|α₀|²}).
    """
    a = complex(alpha0)
    a2 = np.abs(a) ** 2
    norm_sq = 2.0 * (1.0 + np.exp(-2.0 * a2))
    W_pos = np.exp(-2.0 * np.abs(alpha - a) ** 2)
    W_neg = np.exp(-2.0 * np.abs(alpha + a) ** 2)
    W_int = 2.0 * np.exp(-2.0 * np.abs(alpha) ** 2) * np.cos(4.0 * np.imag(np.conj(a) * alpha))
    return (2.0 / np.pi) * (W_pos + W_neg + W_int) / norm_sq


def W_mixed_cat(alpha: np.ndarray, alpha0: complex) -> np.ndarray:
    """W_mc(γ) = (1/π) (e^{-2|γ-α₀|²} + e^{-2|γ+α₀|²}).  Half-and-half incoherent mixture."""
    a = complex(alpha0)
    return (1.0 / np.pi) * (
        np.exp(-2.0 * np.abs(alpha - a) ** 2) + np.exp(-2.0 * np.abs(alpha + a) ** 2)
    )


def W_squeezed(alpha: np.ndarray, r: float, theta: float = 0.0) -> np.ndarray:
    """W for squeezed vacuum S(ξ)|0⟩, ξ = r e^{iθ} (pure ⇒ Gaussian, no
    negativity).

        W(γ) = (2/π) exp[ −2 ( e^{+2r} ζ_x² + e^{−2r} ζ_y² ) ],
        ζ = γ e^{−iθ/2},  ζ_x = Re ζ,  ζ_y = Im ζ.

    The squeeze angle θ rotates the phase-space ellipse by θ/2. For
    θ = 0 the state is squeezed in X (narrow along Re γ, Var X = e^{−2r})
    and anti-squeezed in P (broad along Im γ); θ = π/2 swaps the axes.
    Reduces to W_vacuum at r = 0. Verified to machine precision against
    the parity-form Wigner of the explicit S(ξ)|0⟩ ket and against
    `wigner_from_chi(chi_squeezed)` (notes/squeezed_eta2_scope.md §3).
    """
    zeta = np.asarray(alpha) * np.exp(-1j * theta / 2.0)
    zx, zy = np.real(zeta), np.imag(zeta)
    return (2.0 / np.pi) * np.exp(
        -2.0 * (np.exp(2.0 * r) * zx ** 2 + np.exp(-2.0 * r) * zy ** 2)
    )


# ---------------------------------------------------------------------------
# State factory
# ---------------------------------------------------------------------------

def parse_state(name: str) -> dict:
    """Parse a state name into a spec dict.

    Recognised forms:
        vacuum
        coherent_<alpha>
        thermal_<n_bar>
        fock_<n>
        cat_<alpha>
        mixed_cat_<alpha>
        squeezed_<r>            (θ = 0, squeezed in X)
        squeezed_<r>_perp       (θ = π/2 anisotropy-orientation control)
    """
    parts = name.split("_")
    if parts[0] == "vacuum":
        return {"name": name, "kind": "vacuum", "gaussian": True, "non_gaussian_metric": False}
    if parts[0] == "coherent":
        return {"name": name, "kind": "coherent", "alpha": float(parts[1]),
                "gaussian": True, "non_gaussian_metric": False}
    if parts[0] == "thermal":
        return {"name": name, "kind": "thermal", "n_bar": float(parts[1]),
                "gaussian": True, "non_gaussian_metric": False,
                "purity": 1.0 / (2.0 * float(parts[1]) + 1.0)}
    if parts[0] == "fock":
        n = int(parts[1])
        return {"name": name, "kind": "fock", "n": n,
                "gaussian": False, "non_gaussian_metric": True}
    if parts[0] == "cat":
        return {"name": name, "kind": "cat", "alpha": float(parts[1]),
                "gaussian": False, "non_gaussian_metric": True}
    if parts[0] == "mixed" and len(parts) >= 3 and parts[1] == "cat":
        return {"name": name, "kind": "mixed_cat", "alpha": float(parts[2]),
                "gaussian": True, "non_gaussian_metric": False}
    if parts[0] == "squeezed":
        r = float(parts[1])
        theta = np.pi / 2.0 if (len(parts) >= 3 and parts[2] == "perp") else 0.0
        return {"name": name, "kind": "squeezed", "r": r, "theta": theta,
                "gaussian": True, "non_gaussian_metric": False, "purity": 1.0}
    raise ValueError(f"Unknown state name: {name!r}")


def chi_of_state(beta: np.ndarray, spec: dict) -> np.ndarray:
    """Return χ(β) for the spec returned by `parse_state`."""
    kind = spec["kind"]
    if kind == "vacuum":
        return chi_vacuum(beta)
    if kind == "coherent":
        return chi_coherent(beta, spec["alpha"] + 0.0j)
    if kind == "thermal":
        return chi_thermal(beta, spec["n_bar"])
    if kind == "fock":
        return chi_fock(beta, spec["n"])
    if kind == "cat":
        return chi_cat(beta, spec["alpha"] + 0.0j)
    if kind == "mixed_cat":
        return chi_mixed_cat(beta, spec["alpha"] + 0.0j)
    if kind == "squeezed":
        return chi_squeezed(beta, spec["r"], spec.get("theta", 0.0))
    raise ValueError(f"Unknown kind: {kind!r}")


def W_true_of_state(alpha: np.ndarray, spec: dict) -> np.ndarray:
    """Return analytic W(α) for the spec returned by `parse_state`."""
    kind = spec["kind"]
    if kind == "vacuum":
        return W_vacuum(alpha)
    if kind == "coherent":
        return W_coherent(alpha, spec["alpha"] + 0.0j)
    if kind == "thermal":
        return W_thermal(alpha, spec["n_bar"])
    if kind == "fock":
        return W_fock(alpha, spec["n"])
    if kind == "cat":
        return W_cat(alpha, spec["alpha"] + 0.0j)
    if kind == "mixed_cat":
        return W_mixed_cat(alpha, spec["alpha"] + 0.0j)
    if kind == "squeezed":
        return W_squeezed(alpha, spec["r"], spec.get("theta", 0.0))
    raise ValueError(f"Unknown kind: {kind!r}")


# ---------------------------------------------------------------------------
# Window + zero-pad for the D3 reconstruction pipeline
# ---------------------------------------------------------------------------

def radial_hanning(beta_grid: np.ndarray, B: float) -> np.ndarray:
    """Radial Hanning window on |β| ∈ [0, B]; zero outside.

        w(β) = 0.5 (1 + cos(π |β| / B))   for |β| ≤ B
             = 0                           otherwise
    """
    r = np.abs(beta_grid)
    w = np.where(r <= B, 0.5 * (1.0 + np.cos(np.pi * r / B)), 0.0)
    return w


def zero_pad_centered(arr: np.ndarray, target_size: int) -> np.ndarray:
    """Symmetric zero-pad an N×N array to target_size × target_size."""
    N = arr.shape[0]
    if arr.shape[1] != N:
        raise ValueError("array must be square")
    if target_size < N:
        raise ValueError(f"target_size {target_size} < N {N}")
    if target_size == N:
        return arr.copy()
    pad_total = target_size - N
    pad_lo = pad_total // 2
    pad_hi = pad_total - pad_lo
    return np.pad(arr, ((pad_lo, pad_hi), (pad_lo, pad_hi)), mode="constant")


def padded_beta_axis(beta_axis: np.ndarray, target_size: int) -> np.ndarray:
    """Extend a centred β axis to the target size keeping Δβ unchanged."""
    N = len(beta_axis)
    d_beta = float(beta_axis[1] - beta_axis[0])
    extent = (target_size - 1) / 2.0 * d_beta
    return np.linspace(-extent, +extent, target_size)


# ---------------------------------------------------------------------------
# Metrics — §7#5 reconstruction quality
# ---------------------------------------------------------------------------

def fidelity(W_rec: np.ndarray, W_true: np.ndarray, d_alpha: float) -> float:
    """F = π ∫ W_rec W_true d²α.  For pure ψ_true this equals ⟨ψ|ρ_rec|ψ⟩."""
    return float(np.pi * np.sum(W_rec * W_true) * d_alpha ** 2)


def l1_error_map(W_rec: np.ndarray, W_true: np.ndarray) -> np.ndarray:
    """Pointwise |W_rec − W_true|."""
    return np.abs(W_rec - W_true)


def l1_error_total(W_rec: np.ndarray, W_true: np.ndarray, d_alpha: float) -> float:
    """∫ |W_rec − W_true| d²α."""
    return float(np.sum(l1_error_map(W_rec, W_true)) * d_alpha ** 2)


def negativity_ratio(W_rec: np.ndarray, W_true: np.ndarray, d_alpha: float) -> float | None:
    """ρ_neg = ∫ min(0, W_rec) d²α / ∫ min(0, W_true) d²α.

    Returns None if the target has no negativity (denominator zero or tiny).
    Per §7#5, the criterion is one-sided ρ_neg ≥ 0.5.
    """
    num = float(np.sum(np.minimum(0.0, W_rec)) * d_alpha ** 2)
    den = float(np.sum(np.minimum(0.0, W_true)) * d_alpha ** 2)
    if abs(den) < 1e-12:
        return None
    return num / den


def restrict_to_window(W: np.ndarray, alpha_axis: np.ndarray, window: float) -> tuple[np.ndarray, np.ndarray]:
    """Restrict a 2D W array and its α axis to |α| ≤ window."""
    mask = np.abs(alpha_axis) <= window
    idx = np.where(mask)[0]
    if len(idx) == 0:
        return W, alpha_axis
    i_lo, i_hi = idx[0], idx[-1] + 1
    return W[i_lo:i_hi, i_lo:i_hi], alpha_axis[i_lo:i_hi]


# ---------------------------------------------------------------------------
# Wigner inversion via 2D FFT
# ---------------------------------------------------------------------------

def wigner_from_chi(chi: np.ndarray, beta_axis: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Invert χ(β) on a Cartesian grid to W(α) via 2D FFT.

    The β grid is indexed as chi[j, k] = χ(beta_axis[k] + 1j * beta_axis[j])
    (rows j = Im β, cols k = Re β). The conjugate α grid has spacing
    Δα = π/(N · Δβ) — this is the Nyquist relation for the exponent
    factor 2i in §Analytical bullet 3, *not* the usual 2π/(N Δβ).

    The integral is

        W(α) = (1/π²) ∫ e^{α β* − α* β} χ(β) d²β
             = (1/π²) ∫ e^{2i (α_y β_x − α_x β_y)} χ(β) d²β

    with positive sign on the (α_y, β_x) pairing and negative on the
    (α_x, β_y) pairing. The two-step FFT below implements this with
    np.fft.ifft on axis=1 (cols, β_x → α_y, positive sign) followed by
    np.fft.fft on axis=0 (rows, β_y → α_x, negative sign).

    Verified on vacuum: W(α=0) = 2/π = 0.6366 to within FFT precision.

    Returns
    -------
    alpha_axis : (N,) ndarray
        α coordinate axis (same for x and y).
    W : (N, N) ndarray, real
        Reconstructed Wigner function, indexed W[i, j] with i = Im α
        index (row) and j = Re α index (col) — matching the input
        χ array convention. This is the standard imshow-friendly
        layout (x-axis = Re α, y-axis = Im α).
    err_imag : float
        Max absolute value of Im[W] before discarding (≲ 1e-15 for
        analytically pure χ; > 1e-10 indicates a convention error).
    """
    N = len(beta_axis)
    if chi.shape != (N, N):
        raise ValueError(f"chi shape {chi.shape} != ({N}, {N})")
    d_beta = float(beta_axis[1] - beta_axis[0])

    d_alpha = np.pi / (N * d_beta)
    alpha_axis = (np.arange(N) - (N - 1) / 2.0) * d_alpha

    # Centered β grid → ifftshift to move β=0 to index 0 for the FFT.
    chi_shifted = np.fft.ifftshift(chi)
    # ifft on axis=1 (β_x → α_y, positive sign, prefactor 1/N).
    inter = np.fft.ifft(chi_shifted, axis=1)
    # fft on axis=0 (β_y → α_x, negative sign).
    out = np.fft.fft(inter, axis=0)
    # Re-centre α=0 to the array centre, then apply the (1/π²) · N · Δβ²
    # prefactor (the N cancels ifft's 1/N; Δβ² is the continuous-integral
    # measure; 1/π² is the Wigner-inversion prefactor).
    W_complex = np.fft.fftshift(out) * (N * d_beta**2 / np.pi**2)
    # The natural FFT output has rows = α_x, cols = α_y (rows conjugate
    # to β_y via the negative-sign FFT, cols conjugate to β_x via the
    # positive-sign IFFT). Transpose to match the input χ convention
    # (rows = Im, cols = Re), so imshow displays Re α on the x-axis.
    W_complex = W_complex.T

    err_imag = float(np.max(np.abs(W_complex.imag)))
    return alpha_axis, W_complex.real, err_imag


# ---------------------------------------------------------------------------
# Back-action diagnostic helpers (v0.6 — see notes/back_action_scope.md)
# ---------------------------------------------------------------------------

def _annihilation(nmax: int) -> np.ndarray:
    """a = √n on the first super-diagonal, (nmax, nmax) complex."""
    return np.diag(np.sqrt(np.arange(1, nmax, dtype=np.float64)), 1).astype(np.complex128)


def _displacement(beta: complex, nmax: int) -> np.ndarray:
    """D(β) = exp(β a† − β* a), Fock basis (nmax, nmax).

    Mirrors `scripts.stroboscopic.ideal_sdf.displacement` but kept local
    so `_common` stays a pure numpy/scipy module with no engine import.
    """
    b = complex(beta)
    if b == 0.0:
        return np.eye(nmax, dtype=np.complex128)
    a = _annihilation(nmax)
    adag = a.conj().T
    return expm(b * adag - np.conj(b) * a)


def partial_trace_spin(psi: np.ndarray, nmax: int) -> np.ndarray:
    """Reduced motional ρ_m = Tr_spin |ψ⟩⟨ψ| for ψ = [down; up] (2·nmax,).

    **Physical index convention** (the back-action load-bearing point,
    scope §5): ρ_m[i, j] = ⟨i|ρ_m|j⟩
        = down[i] conj(down[j]) + up[i] conj(up[j]).

    This is *not* `scripts.stroboscopic.observables.compute`'s internal
    `rho_m = outer(conj(down), down) + outer(conj(up), up)`, which is the
    conjugate-transpose ρ_m* — harmless for its only consumer (the
    transpose-invariant purity) but wrong for Wigner / fidelity. Use
    this helper for every back-action consumer.

    For a normalised ψ, Tr ρ_m = ‖down‖² + ‖up‖² = 1.
    """
    if psi.shape[0] != 2 * nmax:
        raise ValueError(f"psi length {psi.shape[0]} != 2·nmax = {2 * nmax}")
    down = psi[:nmax]
    up = psi[nmax:]
    return np.outer(down, np.conj(down)) + np.outer(up, np.conj(up))


def conditional_motional_ket(psi: np.ndarray, nmax: int, basis: str,
                             outcome: int) -> tuple[np.ndarray, float]:
    """Post-selected motional ket ⟨s|ψ⟩ (renormalised) and its probability.

    ψ = [down; up] = |↓⟩⊗down + |↑⟩⊗up, engine [down, up] ordering with
    σ_z = +1 on |↑⟩ (up block), −1 on |↓⟩ (down block) — matching
    `observables.compute` and `test_ideal_sdf._spin_expectations`.

    Spin eigenvectors / projected (unnormalised) motional components:
        z, +1 → up                z, −1 → down
        x, +1 → (down+up)/√2      x, −1 → (down−up)/√2
        y, +1 → (down+i·up)/√2    y, −1 → (down−i·up)/√2
    using |±x⟩=(|↓⟩±|↑⟩)/√2 and the **engine σ_y convention**
    |±y⟩=(|↓⟩∓i|↑⟩)/√2 — i.e. |+y⟩=(|↓⟩−i|↑⟩)/√2 is the σ_y=+1
    eigenstate, identical to `states.apply_mw_pi2(|↓⟩,phase=0)` and
    locked by `observables.compute` (σ_y = −2 Im⟨d|u⟩) and
    `test_ideal_sdf._spin_expectations`. (The earlier draft used the
    opposite σ_y sign, mislabelling the conditional outcome; fixed in
    the post-run review pass and locked by smoke test 6.)

    Returns (ket, prob) with ‖ket‖ = 1 and prob = ‖projected‖². The
    σ_x / σ_y conventions are locked numerically by the back-action
    smoke tests (σ_x post-select of ideal-SDF |+y⟩|0⟩ → D(±β_tot/2)|0⟩;
    σ_y=+1 post-select of the |+y⟩ equator state → prob 1).
    """
    down = psi[:nmax]
    up = psi[nmax:]
    s = int(outcome)
    if s not in (+1, -1):
        raise ValueError(f"outcome must be ±1, got {outcome}")
    if basis == "z":
        comp = up if s == +1 else down
    elif basis == "x":
        comp = (down + s * up) / np.sqrt(2.0)
    elif basis == "y":
        comp = (down + 1j * s * up) / np.sqrt(2.0)
    else:
        raise ValueError(f"basis must be 'x'|'y'|'z', got {basis!r}")
    prob = float(np.real(np.vdot(comp, comp)))
    if prob < 1e-15:
        return np.zeros(nmax, dtype=np.complex128), prob
    return comp / np.sqrt(prob), prob


def wigner_from_rho(rho: np.ndarray,
                    alpha_axis: np.ndarray) -> tuple[np.ndarray, float]:
    """Wigner via displaced parity: W(α) = (2/π) Tr[ρ D(α) Π D†(α)].

    Π = diag((−1)^n). **Prefactor is 2/π, not π⁻¹** — anchors
    W_vac(0) = 2/π consistent with P0 / `analytic_chain.md` §4 and the
    `_common.W_*` analytic references. This canonical form is applied
    *unchanged to every ρ, pure or mixed*; any per-state prefactor in
    the closed-form `W_*` helpers (e.g. `W_mixed_cat`'s ½-folded 1/π)
    is a normalisation artefact of those formulae and is **never** a
    target for this general helper (scope §4, review-pass guardrail).

    `rho` is (nmax, nmax) in the physical convention of
    `partial_trace_spin`. `alpha_axis` is the shared 1-D Re/Im axis;
    the returned grid is W[i, j] = W(alpha_axis[j] + 1j·alpha_axis[i])
    (rows = Im α, cols = Re α), matching `wigner_from_chi`.

    Returns (W_real, err_imag). err_imag ≲ 1e-13 for a valid ρ; a
    value > 1e-10 flags a convention/orientation error.
    """
    nmax = rho.shape[0]
    if rho.shape != (nmax, nmax):
        raise ValueError(f"rho must be square, got {rho.shape}")
    n = len(alpha_axis)
    pm = ((-1.0) ** np.arange(nmax)).astype(np.complex128)  # parity diagonal
    W = np.empty((n, n), dtype=np.complex128)
    for ii, ay in enumerate(alpha_axis):       # row = Im α
        for jj, ax in enumerate(alpha_axis):   # col = Re α
            D = _displacement(ax + 1j * ay, nmax)
            # Tr[ρ D Π D†] with Π = diag(pm); (D * pm) scales D's columns
            # by Π, so M = (D·Π)·D† and W = (2/π) Tr[ρ M].
            M = (D * pm) @ D.conj().T
            W[ii, jj] = np.trace(rho @ M)
    W *= 2.0 / np.pi
    err_imag = float(np.max(np.abs(W.imag)))
    return W.real, err_imag


def cat_ket(alpha: complex, nmax: int, parity: int = +1) -> np.ndarray:
    """Normalised cat (|α⟩ + parity·|−α⟩)/𝒩, Fock basis (nmax,).

    parity = +1 → even cat, −1 → odd cat. Coherent amplitudes built
    analytically (|α⟩_n = e^{−|α|²/2} αⁿ/√n!) so `_common` needs no
    engine import; verified against `chi_cat` / `W_cat` in the
    back-action smoke tests.
    """
    a = complex(alpha)
    n = np.arange(nmax)
    log_coef = -0.5 * np.abs(a) ** 2 + n * np.log(a if a != 0 else 1.0) \
        - 0.5 * _log_factorial(nmax)
    coh_plus = np.exp(log_coef).astype(np.complex128)
    coh_minus = np.exp(-0.5 * np.abs(a) ** 2 + n * np.log(-a if a != 0 else 1.0)
                       - 0.5 * _log_factorial(nmax)).astype(np.complex128)
    psi = coh_plus + int(parity) * coh_minus
    nrm = np.sqrt(np.real(np.vdot(psi, psi)))
    if nrm < 1e-300:
        raise ValueError("cat ket has zero norm (degenerate α / parity)")
    return psi / nrm


def _log_factorial(nmax: int) -> np.ndarray:
    """[log(0!), …, log((nmax−1)!)] via cumulative log — Fock-amp stability."""
    lf = np.zeros(nmax, dtype=np.float64)
    if nmax > 1:
        lf[1:] = np.cumsum(np.log(np.arange(1, nmax, dtype=np.float64)))
    return lf


# ---------------------------------------------------------------------------
# Manifest helpers (wp_manifest_v1 schema)
# ---------------------------------------------------------------------------

def sha256_of_file(path: str | Path) -> str:
    """Return the SHA-256 of the file at *path*."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_manifest(
    *,
    wp_id: str,
    code_version: str,
    runner_version: str,
    repository: str,
    artifact_path: str,
    artifact_format: str,
    elapsed_s: float,
    payload: dict,
) -> dict:
    """Assemble a wp_manifest_v1 envelope and compute its provenance hash."""
    p = Path(artifact_path)
    bytes_ = p.stat().st_size
    sha = sha256_of_file(p)
    artifact = {
        "path": artifact_path,
        "format": artifact_format,
        "bytes": bytes_,
        "sha256": sha,
    }
    # Provenance hash binds the manifest to its input description + artifact.
    canon = {
        "wp_id": wp_id,
        "code_version": code_version,
        "runner_version": runner_version,
        "payload": payload,
        "artifact_sha256": sha,
    }
    canon_bytes = json.dumps(canon, sort_keys=True, separators=(",", ":")).encode("utf-8")
    provenance_hash = hashlib.sha256(canon_bytes).hexdigest()
    return {
        "schema_version": "1.0",
        "wp_id": wp_id,
        "code_version": code_version,
        "runner_version": runner_version,
        "repository": repository,
        "artifact": artifact,
        "execution": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engine": "python-scipy",
            "precision": "complex128",
            "elapsed_s": float(elapsed_s),
        },
        "provenance_hash": provenance_hash,
        "payload": payload,
    }


def write_manifest(manifest: dict, manifest_path: str | Path) -> None:
    """Write the manifest JSON to disk."""
    Path(manifest_path).write_text(json.dumps(manifest, indent=2) + "\n")
