"""Smoke tests for the public API surface: import, construction, and shape."""
from __future__ import annotations

import numpy as np
import pytest

from stroboscopic import (
    HilbertSpace, StroboTrain, build_strobo_train, build_impulsive_train,
    run_sequence, backend,
)
from stroboscopic import operators as ops
from stroboscopic import propagators as prop


def test_hilbert_scope_enforced():
    HilbertSpace(n_spins=1, mode_cutoffs=(10,))
    with pytest.raises(NotImplementedError):
        HilbertSpace(n_spins=2, mode_cutoffs=(10,))
    with pytest.raises(NotImplementedError):
        HilbertSpace(n_spins=1, mode_cutoffs=(10, 10))


def test_prepare_state_shape():
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(16,))
    psi = hs.prepare_state(
        spin={'theta_deg': 30.0, 'phi_deg': 60.0},
        modes=[{'alpha': 1.5, 'alpha_phase_deg': 45.0}],
    )
    assert psi.shape == (2 * 16,)
    assert np.isclose(float(np.sum(np.abs(np.asarray(psi)) ** 2)), 1.0, atol=1e-12)


def test_strobo_train_builds_and_evolves():
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(20,))
    psi0 = hs.prepare_state(
        spin={'theta_deg': 0.0, 'phi_deg': 0.0},
        modes=[{'alpha': 2.0, 'alpha_phase_deg': 0.0}],
    )
    train = build_strobo_train(
        hs=hs, eta=0.2, omega_r=0.1, omega_m=1.0,
        delta=0.05, n_pulses=5, delta_t=0.1,
        intra_pulse_motion=True, gap_includes_spin_detuning=True,
    )
    psi = train.evolve(psi0)
    assert psi.shape == psi0.shape
    assert np.isclose(float(np.sum(np.abs(np.asarray(psi)) ** 2)), 1.0, atol=1e-10)


def test_impulsive_train_builds_and_evolves():
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(20,))
    psi0 = hs.prepare_state(
        spin={'theta_deg': 0.0, 'phi_deg': 0.0},
        modes=[{'alpha': 2.0, 'alpha_phase_deg': 0.0}],
    )
    train = build_impulsive_train(
        hs=hs, eta=0.2, pulse_area=0.3, omega_m=1.0, delta=0.05, n_pulses=5,
        gap_include_motion=False, gap_include_spin_detuning=True,
    )
    psi = train.evolve(psi0)
    assert psi.shape == psi0.shape


def test_run_sequence_dispatch():
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(16,))
    psi0 = hs.prepare_state(
        spin={'theta_deg': 0.0, 'phi_deg': 0.0},
        modes=[{'alpha': 1.0, 'alpha_phase_deg': 0.0}],
    )
    psi_a = run_sequence(
        'strobo_train', hs=hs, psi0=psi0,
        eta=0.2, omega_r=0.1, omega_m=1.0, delta=0.0,
        n_pulses=3, delta_t=0.1,
        intra_pulse_motion=True, gap_includes_spin_detuning=True,
    )
    assert psi_a.shape == psi0.shape

    with pytest.raises(NotImplementedError):
        run_sequence('ramsey', hs=hs, psi0=psi0)
    with pytest.raises(KeyError):
        run_sequence('nonsense', hs=hs, psi0=psi0)


def test_evolution_preserves_norm():
    # NMAX must accommodate the Fock tail of |α| = 3, which needs ≥ ~35 levels
    # to keep truncation leakage below machine precision.
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(50,))
    psi0 = hs.prepare_state(
        spin={'theta_deg': 45.0, 'phi_deg': 90.0},
        modes=[{'alpha': 3.0, 'alpha_phase_deg': 30.0}],
    )
    train = build_strobo_train(
        hs=hs, eta=0.397, omega_r=0.3, omega_m=1.3,
        delta=0.5, n_pulses=30, delta_t=0.13 * 2 * np.pi / 1.3,
        intra_pulse_motion=True, gap_includes_spin_detuning=True,
    )
    psi = train.evolve(psi0)
    norm = float(np.sum(np.abs(np.asarray(psi)) ** 2))
    assert abs(norm - 1.0) < 1e-10, f'norm drift = {abs(norm - 1.0):.3e}'


def test_backend_defaults_to_numpy():
    assert backend.get_backend().name == 'numpy'
