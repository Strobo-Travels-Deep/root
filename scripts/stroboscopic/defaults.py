"""Default parameters for stroboscopic sequences.

Kept compatible with legacy scripts/stroboscopic_sweep.py DEFAULTS where
relevant, but trimmed to the 1-spin/1-mode clean-restructure scope.
"""
from __future__ import annotations

CODE_VERSION = "1.0.0-restructure"

DEFAULTS = dict(
    # Motional prep
    alpha=3.0,
    alpha_phase_deg=0.0,
    squeeze_r=0.0,
    squeeze_phi_deg=0.0,
    fock_n=None,
    n_thermal=0.0,
    # Spin prep
    theta_deg=0.0,
    phi_deg=0.0,
    # Physics
    eta=0.397,
    omega_m=1.3,
    omega_r=0.300,
    # Drive
    ac_phase_deg=0.0,
    n_pulses=22,
    t_sep_factor=1.0,
    delta_t_us=None,
    intra_pulse_motion=False,
    center_pulses_at_phase=False,
    gap_includes_spin_detuning=True,
    # Truncation
    nmax=50,
)

_INT_PARAMS = {"nmax", "n_pulses", "fock_n"}


def enforce_types(params: dict) -> dict:
    out = dict(params)
    for k in _INT_PARAMS:
        if k in out and out[k] is not None:
            out[k] = int(out[k])
    return out


def merged(params: dict | None = None) -> dict:
    return enforce_types({**DEFAULTS, **(params or {})})
