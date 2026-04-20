"""HilbertSpace — composite Hilbert space registry.

Scope of this restructure: 1 spin × 1 motional mode. The constructor
accepts `n_spins` and `mode_cutoffs` and validates them against scope
so that future generalization is a drop-in.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import operators as _ops
from . import states as _states
from . import observables as _obs


@dataclass(frozen=True)
class HilbertSpace:
    n_spins: int
    mode_cutoffs: tuple[int, ...]

    def __post_init__(self):
        if self.n_spins != 1 or len(self.mode_cutoffs) != 1:
            raise NotImplementedError(
                "current scope: 1 spin × 1 mode. Got "
                f"n_spins={self.n_spins}, mode_cutoffs={self.mode_cutoffs}"
            )

    @property
    def nmax(self) -> int:
        return int(self.mode_cutoffs[0])

    @property
    def dim(self) -> int:
        return 2 * self.nmax

    def annihilation(self, mode_idx: int = 0):
        assert mode_idx == 0
        return _ops.annihilation(self.nmax)

    def coupling(self, eta: float, mode_idx: int = 0):
        assert mode_idx == 0
        return _ops.coupling(eta, self.nmax)

    def prepare_state(self, spin: dict, modes: list[dict]):
        if len(modes) != 1:
            raise ValueError("exactly one mode required in current scope")
        psi_m = _states.prepare_motional({"nmax": self.nmax, **modes[0]})
        return _states.tensor_spin_motion(
            spin.get("theta_deg", 0.0), spin.get("phi_deg", 0.0),
            psi_m, self.nmax,
        )

    def apply_mw_pi2(self, psi, mw_phase_deg: float):
        """MW π/2 pulse about (cos φ x̂ + sin φ ŷ) on spin only."""
        return _states.apply_mw_pi2(psi, mw_phase_deg, self.nmax)

    def observables(self, psi) -> dict:
        return _obs.compute(psi, self.nmax)

    def motional_fidelity(self, psi, psi_m_ref) -> float:
        return _obs.motional_fidelity(psi, psi_m_ref, self.nmax)

    def fock_leakage(self, psi, top_k: int = 3) -> float:
        return _obs.fock_leakage(psi, self.nmax, top_k)
