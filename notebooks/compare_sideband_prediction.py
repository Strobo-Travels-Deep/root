#!/usr/bin/env python3
"""
compare_sideband_prediction.py — qualitative cross-check: notebook vs engine.

The multi_fock_interference notebook predicts three α=4 observables:
  (i)   incoherent BSB carpet  P_↑(δ, t) at fixed η = 2
  (ii)  incoherent Rabi envelope  Σ |c_n|² Ω_{n,n+1}²(η) · f(t)   — sign-blind
  (iii) coherent Ramsey envelope  A(η) = Σ |c_n|² Ω_{n,n+1}(η)   — sign-sensitive

Our engine (v0.9.1, scripts/stroboscopic_sweep.py) uses the same
interaction-picture Hamiltonian H = Ω/2 (C σ₋ + C† σ₊) with C =
exp(iη(a+a†)). So running at δ = +ω_m (blue-sideband-resonant) for a
*single* short pulse should reproduce the notebook's predictions from
a completely independent code path (full-Fock expm vs Laguerre closed
form). Agreement → engine's Laguerre structure verified.

Qualitative comparison deliberately: we look at node positions and
amplitude shape, not numerics-to-numerics.

Output: notebooks/outputs/sideband_cross_check.png
"""

import os, sys
from pathlib import Path
import numpy as np
from scipy.special import eval_genlaguerre, factorial
from scipy.linalg import expm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = SCRIPT_DIR.parent / 'scripts'
sys.path.insert(0, str(ENGINE_DIR))
import stroboscopic_sweep as ss


# ── Notebook's closed-form predictions ──────────────────────────────

def rabi_bsb(n, eta):
    """Ω_{n, n+1}(η) / Ω_0, signs preserved."""
    n, eta = np.asarray(n), np.asarray(eta)
    L = eval_genlaguerre(n, 1, eta**2)
    return np.exp(-eta**2 / 2) * eta * L / np.sqrt(n + 1)


def coherent_weights(alpha, n_max):
    """|c_n|² for |α⟩ Glauber coherent state."""
    n = np.arange(n_max + 1)
    log_cn = -0.5 * abs(alpha)**2 + n * np.log(abs(alpha) + 1e-30) \
             - 0.5 * np.log(factorial(n).astype(float))
    return np.exp(2 * log_cn)


def coherent_envelope(alpha, eta_grid, n_max=50):
    """A(η) = Σ |c_n|² Ω_{n,n+1}(η)   (sign-sensitive)."""
    p = coherent_weights(alpha, n_max)
    A = np.zeros_like(eta_grid)
    for n in range(n_max + 1):
        A += p[n] * rabi_bsb(n, eta_grid)
    return A


def incoherent_abs_envelope(alpha, eta_grid, n_max=50):
    """Σ |c_n|² |Ω_{n,n+1}(η)|   (sign-blind)."""
    p = coherent_weights(alpha, n_max)
    B = np.zeros_like(eta_grid)
    for n in range(n_max + 1):
        B += p[n] * np.abs(rabi_bsb(n, eta_grid))
    return B


# ── Engine's direct simulation on the BSB ──────────────────────────

def engine_bsb_ramsey(alpha, eta, omega_r, omega_m, t, ac_phase_rad, nmax):
    """Ramsey-like BSB amplitude observable.

    Sequence: |↓⟩|α⟩ → MW π/2 about +x̂ → BSB pulse at phase ϕ for time t → measure σ_y.

    At δ = +ω_m and short pulse, the BSB coupling rotates the spin about
    the axis (cos ϕ x̂ + sin ϕ ŷ) by an effective angle θ_eff = 2·A·t where
    A = Σ c_n· c_{n+1}* · Ω_{n,n+1}/√2  (coherent sum with signs). Scanning
    ϕ traces out a Ramsey fringe in σ_y whose amplitude is ∝ θ_eff. So:

        contrast_y(η) = max_ϕ σ_y − min_ϕ σ_y over [0, 2π]
                       ∝ A(η) up to a shared geometric factor.
    """
    _, _, X = ss.build_operators(nmax)
    C = ss.build_coupling(eta, nmax, X)
    Cdag = C.conj().T
    delta = +omega_m
    H = ss.build_hamiltonian(eta, omega_r, delta, nmax, C, Cdag,
                              ac_phase_rad=ac_phase_rad, omega_m=omega_m,
                              intra_pulse_motion=True)
    U = expm(-1j * H * t)
    psi_m = ss.coherent_state(alpha, 0.0, nmax)
    psi0 = ss.tensor_spin_motion(theta_deg=0.0, phi_deg=0.0,
                                  psi_m=psi_m, nmax=nmax)
    psi = ss._mw_pi2_apply(psi0, 0.0, nmax)  # MW π/2 about +x̂
    psi = U @ psi
    obs = ss.compute_observables(psi, nmax)
    return obs['sigma_x'], obs['sigma_y'], obs['sigma_z']


def engine_ramsey_contrast_scan(alpha, eta_grid, omega_r, omega_m, t, nmax,
                                 n_phi=16):
    """For each η, scan ϕ ∈ [0, 2π) and extract fringe contrast in σ_x and σ_y.

    Returns contrast_x(η), contrast_y(η), fringe_phase_y(η) — the phase at
    which σ_y peaks (sign-preserving via complex Fourier component).
    """
    phi_list = np.linspace(0.0, 2*np.pi, n_phi, endpoint=False)
    cx_arr = np.zeros_like(eta_grid); cy_arr = np.zeros_like(eta_grid)
    signed_y = np.zeros_like(eta_grid, dtype=complex)
    for i, eta in enumerate(eta_grid):
        sx_trace = np.zeros(n_phi); sy_trace = np.zeros(n_phi)
        for k, phi in enumerate(phi_list):
            sx_trace[k], sy_trace[k], _ = engine_bsb_ramsey(
                alpha, eta, omega_r, omega_m, t, phi, nmax)
        cx_arr[i] = 0.5 * (sx_trace.max() - sx_trace.min())
        cy_arr[i] = 0.5 * (sy_trace.max() - sy_trace.min())
        # Fourier-1 component of σ_y vs ϕ — sign-preserving amplitude
        F1 = np.sum(sy_trace * np.exp(-1j * phi_list)) / n_phi
        signed_y[i] = F1
    return cx_arr, cy_arr, signed_y


# ── Main cross-check ───────────────────────────────────────────────

def main():
    alpha = 4.0
    eta_grid = np.linspace(0.05, 3.0, 200)   # start from 0.05 to avoid η=0 singularity
    omega_r = 0.3      # engine units (angular)
    omega_m = 1.3      # engine units (angular)
    nmax = 80          # generous Fock cutoff for α = 4, η up to 3

    # Closed-form envelopes
    A_coh  = coherent_envelope(alpha, eta_grid, n_max=60)
    A_abs  = incoherent_abs_envelope(alpha, eta_grid, n_max=60)

    # Engine: Ramsey-type sequence that exposes the sign structure
    t_short = 0.05            # engine time units — small BSB rotation angle
    n_phi = 16
    # Decimate eta_grid for the engine scan (it's 16x more expensive than the 1D sum)
    eta_engine = eta_grid[::4]
    print(f"Running engine Ramsey BSB scan: α={alpha}, η ∈ [{eta_engine[0]:.2f}, "
          f"{eta_engine[-1]:.2f}] ({len(eta_engine)} pts × {n_phi} ϕ pts), "
          f"t_pulse={t_short}, nmax={nmax}")

    cx_engine, cy_engine, signed_y = engine_ramsey_contrast_scan(
        alpha, eta_engine, omega_r, omega_m, t_short, nmax, n_phi=n_phi)

    # The Fourier-1 component of σ_y vs ϕ is proportional to the coherent amplitude A(η).
    # Its real part is sign-preserving (the fringe "amplitude with sign").
    signed_engine = signed_y.real    # signed Ramsey fringe amplitude on σ_y

    # Normalise both predictions and engine output to compare shapes
    A_coh_norm = A_coh / np.max(np.abs(A_coh))
    signed_engine_norm = signed_engine / np.max(np.abs(signed_engine))

    # Find node positions predicted by coherent envelope A(η) = 0
    sign_flips_A = np.where(np.diff(np.sign(A_coh)))[0]
    eta_nodes_A  = eta_grid[sign_flips_A]
    print(f"\nCoherent envelope A(η) predicted zero crossings (nodes):")
    for e in eta_nodes_A:
        print(f"  η ≈ {e:.3f}")

    # Engine-detected zero crossings in signed_engine
    sign_flips_eng = np.where(np.diff(np.sign(signed_engine)))[0]
    eta_nodes_eng  = eta_engine[sign_flips_eng]
    print(f"\nEngine Ramsey-σ_y zero crossings:")
    for e in eta_nodes_eng:
        print(f"  η ≈ {e:.3f}")

    # ── Plot ───────────────────────────────────────────────────────
    fig, axs = plt.subplots(2, 1, figsize=(9, 7), sharex=True, constrained_layout=True)

    # Panel A — closed-form envelopes
    ax = axs[0]
    ax.plot(eta_grid, A_coh, color='#c0392b', lw=2,
            label=r'coherent $A(\eta) = \sum_n |c_n|^2 \Omega_{n,n+1}(\eta)$ (sign-kept)')
    ax.plot(eta_grid, A_abs, color='#2c5f7c', lw=1.3, ls='--',
            label=r'sign-blind $\sum_n |c_n|^2 |\Omega_{n,n+1}(\eta)|$')
    ax.axhline(0, color='k', lw=0.4)
    for e in eta_nodes_A:
        ax.axvline(e, color='#c0392b', lw=0.4, ls=':', alpha=0.4)
    ax.set_ylabel(r'amplitude / $\Omega_0$')
    ax.set_title(rf'Notebook closed-form predictions (α={alpha})', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # Panel B — engine Ramsey sequence (signed Fourier-1 amplitude)
    ax = axs[1]
    # Overlay notebook A(η) normalised, on top of engine signed amplitude
    ax.plot(eta_grid, A_coh_norm, color='#c0392b', lw=1.5, alpha=0.6,
            label='notebook A(η), normalised')
    ax.plot(eta_engine, signed_engine_norm, color='#27ae60', lw=0,
            marker='o', ms=4,
            label=rf'engine Ramsey Re[$\tilde\sigma_y$($\varphi$)], normalised')
    ax.axhline(0, color='k', lw=0.4)
    # overlay predicted + engine node positions
    for e in eta_nodes_A:
        ax.axvline(e, color='#c0392b', lw=0.4, ls=':', alpha=0.3,
                   label='notebook nodes' if e == eta_nodes_A[0] else None)
    for e in eta_nodes_eng:
        ax.axvline(e, color='#27ae60', lw=0.8, ls='-.', alpha=0.5,
                   label='engine nodes' if e == eta_nodes_eng[0] else None)
    ax.set_xlabel(r'Lamb–Dicke parameter $\eta$')
    ax.set_ylabel(r'signed Ramsey fringe amplitude (norm.)')
    ax.set_title(r'Engine Ramsey sequence: MW $\pi/2$ + BSB($\varphi$) pulse, Fourier-1 of $\sigma_y(\varphi)$',
                 fontsize=10)
    ax.legend(fontsize=8, loc='upper right', ncol=2)
    ax.grid(alpha=0.3)

    fig.suptitle(r'Qualitative cross-check: multi-Fock interference — notebook vs engine',
                 fontsize=11)

    out_path = SCRIPT_DIR / 'outputs' / 'sideband_cross_check.png'
    fig.savefig(out_path, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"\n  wrote {out_path}")

    # Report pairwise distance between predicted and measured nodes
    if len(eta_nodes_A) > 0 and len(eta_nodes_eng) > 0:
        print("\nPairwise node alignment (notebook A(η) = 0 vs engine Ramsey nodes):")
        for e_A in eta_nodes_A:
            nearest = eta_nodes_eng[np.argmin(np.abs(eta_nodes_eng - e_A))]
            print(f"  notebook η = {e_A:.3f}  ↔  engine η = {nearest:.3f}  "
                  f"(|Δ| = {abs(nearest - e_A):.3f})")


if __name__ == '__main__':
    main()
