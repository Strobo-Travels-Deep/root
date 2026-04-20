"""Shared fixtures for stroboscopic package regression tests.

These tests reproduce the physics from the legacy scripts/stroboscopic_sweep.py
engine on small grids and assert that the new package matches bit-for-bit
(or to floating-point reassociation noise where the orderings differ).

All tests use numpy backend. JAX backend is covered when the environment
supports it (native ARM Python on Apple Silicon, or any non-Rosetta
x86_64 machine).
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pytest

# Make scripts/ importable so legacy stroboscopic_sweep loads alongside the
# new package.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.dirname(os.path.dirname(_HERE))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)


@pytest.fixture(scope="session")
def physics_params():
    """Small-grid reference parameters, Hasse-matched."""
    OMEGA_M = 1.3
    T_M = 2 * np.pi / OMEGA_M
    DELTA_T = 0.13 * T_M
    N_PULSES = 30
    ETA = 0.397
    NMAX = 30
    OMEGA_EFF = np.pi / (2 * N_PULSES * DELTA_T)
    OMEGA_R = OMEGA_EFF / np.exp(-ETA ** 2 / 2)
    return dict(
        OMEGA_M=OMEGA_M, T_M=T_M, DELTA_T=DELTA_T, N_PULSES=N_PULSES,
        ETA=ETA, NMAX=NMAX, OMEGA_R=OMEGA_R, ALPHA=3.0,
    )


@pytest.fixture(scope="session")
def small_grid(physics_params):
    p = physics_params
    det_rel = np.linspace(-15.0 / p['OMEGA_M'], +15.0 / p['OMEGA_M'], 13)
    phi_deg = np.linspace(0.0, 360.0, 4, endpoint=False)
    return dict(det_rel=det_rel, phi_deg=phi_deg)
