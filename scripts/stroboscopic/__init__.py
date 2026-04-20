"""Stroboscopic sequences package (clean restructure, 1 spin × 1 mode).

Public API:
    backend.set_backend('numpy'|'jax')
    HilbertSpace(n_spins=1, mode_cutoffs=[nmax])
    build_strobo_train(hs=..., eta=..., omega_r=..., ...)
    run_sequence(name, hs=..., psi0=..., **params)

Physics convention: coupling C with σ₋, C† with σ₊, dressed by the AC
analysis phase. Gap propagator includes spin detuning by default (v0.9.1).
"""
from __future__ import annotations

from .defaults import DEFAULTS, CODE_VERSION, enforce_types, merged
from .hilbert import HilbertSpace
from .sequences import (
    StroboTrain, build_strobo_train, build_impulsive_train, run_sequence,
)
from . import backend
from . import operators
from . import states
from . import hamiltonian
from . import propagators
from . import observables

__all__ = [
    "DEFAULTS", "CODE_VERSION", "enforce_types", "merged",
    "HilbertSpace", "StroboTrain", "build_strobo_train",
    "build_impulsive_train", "run_sequence",
    "backend", "operators", "states", "hamiltonian", "propagators", "observables",
]
