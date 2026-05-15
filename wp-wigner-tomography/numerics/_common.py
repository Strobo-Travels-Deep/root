"""WP-W shared numerics helpers.

Functions:
    dirichlet_magnitude(N, x)        — |D_N(x)| at angular argument x
    inverse_dirichlet(N, ratio)      — solve |D_N(x)| = ratio on the central lobe
    chi_vacuum(beta)                 — χ for the motional ground state
    chi_coherent(beta, alpha)        — χ for a coherent state |α⟩
    contrast_from_chi(beta, chi)     — C(β) = e^{-|β|²/2} χ(β) (ideal-SDF prefactor)
    wigner_from_chi(chi, beta_axis)  — 2D-FFT inversion χ → W on the α grid
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
from scipy.optimize import brentq


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
