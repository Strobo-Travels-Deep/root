"""Backend abstraction: numpy or JAX.

The public `xp` submodule-like object and `expm` function dispatch to the
active backend. All physics modules import from here and should avoid
element-wise assignment so JAX (immutable arrays) works without branches.
"""
from __future__ import annotations

import numpy as _np
import scipy.linalg as _sla

_ACTIVE = "numpy"


class _NumpyBackend:
    name = "numpy"
    xp = _np
    expm = staticmethod(_sla.expm)
    complex_dtype = _np.complex128
    float_dtype = _np.float64

    @staticmethod
    def asarray(x, dtype=None):
        return _np.asarray(x, dtype=dtype)


class _JaxBackend:
    name = "jax"

    def __init__(self):
        import jax
        import jax.numpy as jnp
        import jax.scipy.linalg as jsla
        self.xp = jnp
        self.expm = jsla.expm
        self.complex_dtype = jnp.complex128
        self.float_dtype = jnp.float64
        jax.config.update("jax_enable_x64", True)
        self._jax = jax

    def asarray(self, x, dtype=None):
        return self.xp.asarray(x, dtype=dtype)


_BACKENDS: dict[str, object] = {"numpy": _NumpyBackend()}


def set_backend(name: str) -> None:
    """Select 'numpy' or 'jax' for all subsequent module calls."""
    global _ACTIVE
    if name not in ("numpy", "jax"):
        raise ValueError(f"unknown backend: {name!r}")
    if name == "jax" and "jax" not in _BACKENDS:
        _BACKENDS["jax"] = _JaxBackend()
    _ACTIVE = name


def get_backend():
    return _BACKENDS[_ACTIVE]


def xp():
    return get_backend().xp


def expm(A):
    return get_backend().expm(A)


def is_jax() -> bool:
    return _ACTIVE == "jax"
