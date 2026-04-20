"""Sequence builders: high-level wrappers that assemble propagators and evolve.

Registry:
    strobo_train     — N identical pulses with fixed gap between.
    rabi_flop        — single continuous pulse of variable duration.
    ramsey           — π/2, free evolution, π/2 with analysis phase.
    spin_motion      — alias of strobo_train with t_sep_factor tuned for SDF.

Only strobo_train is fleshed out in this first restructure pass, matching
legacy run_2d_alpha3.py bit-for-bit. Others raise NotImplementedError.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as _np

from .backend import xp
from . import hamiltonian as _ham
from . import propagators as _prop
from . import operators as _ops


@dataclass
class StroboTrain:
    """Bundle of (U_pulse, U_gap_diag, n_pulses) ready to evolve a state."""
    U_pulse: object
    U_gap_diag: object
    n_pulses: int

    def evolve(self, psi, record_steps: bool = False):
        if record_steps:
            history = [psi]
            for k in range(self.n_pulses):
                psi = self.U_pulse @ psi
                if k < self.n_pulses - 1:
                    psi = _prop.apply_gap(self.U_gap_diag, psi)
                history.append(psi)
            return psi, history
        for k in range(self.n_pulses):
            psi = self.U_pulse @ psi
            if k < self.n_pulses - 1:
                psi = _prop.apply_gap(self.U_gap_diag, psi)
        return psi


def build_strobo_train(*, hs,
                       eta: float, omega_r: float, omega_m: float,
                       delta: float, n_pulses: int, delta_t: float,
                       t_sep_factor: float = 1.0,
                       ac_phase_rad: float = 0.0,
                       intra_pulse_motion: bool = True,
                       gap_includes_spin_detuning: bool = True,
                       C=None, Cdag=None) -> StroboTrain:
    """Construct U_pulse and U_gap for an N-pulse stroboscopic train."""
    nmax = hs.nmax
    if C is None:
        C = _ops.coupling(eta, nmax)
    if Cdag is None:
        Cdag = C.conj().T

    H_pulse = _ham.build_pulse_hamiltonian(
        eta, omega_r, delta, nmax, C, Cdag,
        ac_phase_rad=ac_phase_rad, omega_m=omega_m,
        intra_pulse_motion=intra_pulse_motion,
    )
    U_pulse = _prop.build_U_pulse(H_pulse, delta_t)

    T_m = 2.0 * _np.pi / omega_m
    Tsep = T_m * t_sep_factor
    t_gap = (Tsep - delta_t) if intra_pulse_motion else Tsep

    U_gap_diag = _prop.build_U_gap(
        nmax, omega_m, t_gap,
        delta=delta if gap_includes_spin_detuning else 0.0,
        include_spin_detuning=gap_includes_spin_detuning,
    )
    return StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag, n_pulses=int(n_pulses))


def build_impulsive_train(*, hs,
                          eta: float, pulse_area: float,
                          omega_m: float, delta: float, n_pulses: int,
                          t_sep: float | None = None,
                          ac_phase_rad: float = 0.0,
                          gap_include_motion: bool = False,
                          gap_include_spin_detuning: bool = True,
                          C=None, Cdag=None) -> StroboTrain:
    """Impulsive-kick stroboscopic train (R2 physics).

    Pulse: K = exp(-i·(A/2)·[[0,C],[C†,0]]).  A = pulse_area (dimensionless).
    Gap: spin-detuning phase over t_sep (default T_m = 2π/ω_m).
    """
    nmax = hs.nmax
    if C is None:
        C = _ops.coupling(eta, nmax)
    if Cdag is None:
        Cdag = C.conj().T

    U_pulse = _prop.build_impulsive_pulse(pulse_area, nmax, C, Cdag,
                                          ac_phase_rad=ac_phase_rad)
    t_sep = (2.0 * _np.pi / omega_m) if t_sep is None else float(t_sep)
    U_gap_diag = _prop.build_U_gap(
        nmax, omega_m, t_sep,
        delta=delta if gap_include_spin_detuning else 0.0,
        include_motion=gap_include_motion,
        include_spin_detuning=gap_include_spin_detuning,
    )
    return StroboTrain(U_pulse=U_pulse, U_gap_diag=U_gap_diag, n_pulses=int(n_pulses))


# ── Registry dispatcher ────────────────────────────────────────

def run_sequence(name: str, *, hs, psi0, record_steps: bool = False, **params):
    if name == "strobo_train":
        train = build_strobo_train(hs=hs, **params)
        return train.evolve(psi0, record_steps=record_steps)
    if name == "impulsive_train":
        train = build_impulsive_train(hs=hs, **params)
        return train.evolve(psi0, record_steps=record_steps)
    if name in ("rabi_flop", "ramsey", "spin_motion"):
        raise NotImplementedError(f"{name!r} not yet implemented in restructure pass")
    raise KeyError(f"unknown sequence: {name!r}")
