#!/usr/bin/env python3
"""Loader for experimental_params_v1 documents.

Usage (as a library):
    from load_params import load_params, engine_kwargs_for_sequence

    doc = load_params("strobo2p0_params.json")
    kwargs = engine_kwargs_for_sequence(doc, "T2_short_pi2")
    # -> dict with omega_m, omega_r, eta, n_pulses, delta_t_us, t_sep_factor,
    #    ac_phase_deg, ready to splat into stroboscopic_sweep.run_single.

Usage (as a CLI):
    python load_params.py strobo2p0_params.json
    # prints a summary of every measured value and the derived engine kwargs
    # for each pulse sequence.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


# -------------------------------------------------------------------
# Unit conversion
# -------------------------------------------------------------------

_FREQ_TO_MHZ = {
    "Hz":  1e-6,
    "kHz": 1e-3,
    "MHz": 1.0,
    "GHz": 1e3,
}
_TIME_TO_US = {
    "ns": 1e-3,
    "us": 1.0,
    "ms": 1e3,
    "s":  1e6,
}


def _to_MHz(v: dict) -> float:
    unit = v["unit"]
    if unit not in _FREQ_TO_MHZ:
        raise ValueError(f"Unsupported frequency unit: {unit}")
    return float(v["value"]) * _FREQ_TO_MHZ[unit]


def _to_us(v: dict) -> float:
    unit = v["unit"]
    if unit not in _TIME_TO_US:
        raise ValueError(f"Unsupported time unit: {unit}")
    return float(v["value"]) * _TIME_TO_US[unit]


def _dimensionless(v: dict) -> float:
    if v["unit"] not in ("1", "dimensionless"):
        raise ValueError(f"Expected dimensionless, got unit: {v['unit']}")
    return float(v["value"])


def _angle_deg(v: dict) -> float:
    unit = v["unit"]
    if unit == "deg":
        return float(v["value"])
    if unit == "rad":
        return math.degrees(float(v["value"]))
    raise ValueError(f"Unsupported angle unit: {unit}")


# -------------------------------------------------------------------
# Document API
# -------------------------------------------------------------------

def load_params(path: str | Path) -> dict[str, Any]:
    """Read a parameter document from JSON and sanity-check schema_version."""
    path = Path(path)
    doc = json.loads(path.read_text())
    if doc.get("schema_version") != "1.0":
        raise ValueError(
            f"Unsupported schema_version: {doc.get('schema_version')!r} "
            f"(expected '1.0'). File: {path}"
        )
    return doc


def _resolve_rabi_MHz(doc: dict, seq: dict) -> float:
    """Return Omega/(2pi) in MHz for a sequence: override if present, else beam default."""
    if "rabi_override" in seq:
        return _to_MHz(seq["rabi_override"])
    beam = doc["beams"][seq["beam"]]
    if "rabi_over_2pi" not in beam:
        raise ValueError(
            f"Sequence '{seq.get('description', '?')}' uses beam "
            f"'{seq['beam']}' which has no rabi_over_2pi; and no rabi_override."
        )
    return _to_MHz(beam["rabi_over_2pi"])


def _resolve_eta(doc: dict, seq: dict) -> float:
    """Return Lamb-Dicke eta for the beam * mode combination.

    Priority: beam.lamb_dicke_eta_per_mode[<mode>] > trap.motional_modes[<mode>].lamb_dicke_eta
    """
    beam_entry = doc["beams"][seq["beam"]]
    per_mode = beam_entry.get("lamb_dicke_eta_per_mode", {})
    if seq["mode"] in per_mode:
        return _dimensionless(per_mode[seq["mode"]])
    mode_entry = doc["trap"]["motional_modes"][seq["mode"]]
    if "lamb_dicke_eta" in mode_entry:
        return _dimensionless(mode_entry["lamb_dicke_eta"])
    raise ValueError(
        f"No Lamb-Dicke eta found for beam={seq['beam']}, mode={seq['mode']}."
    )


def engine_kwargs_for_sequence(doc: dict, sequence_name: str) -> dict[str, Any]:
    """Translate a named pulse sequence into keyword args for
    stroboscopic_sweep.run_single. Returns only the fields that are
    uniquely fixed by the parameter document — the caller still supplies
    run-specific fields (alpha, alpha_phase_deg, nmax, det_min/max/npts,
    theta_deg/phi_deg initial spin, intra_pulse_motion, etc.).
    """
    seq = doc["pulse_sequences"][sequence_name]
    mode = doc["trap"]["motional_modes"][seq["mode"]]

    omega_m_MHz = _to_MHz(mode["omega_m_over_2pi"])
    omega_r_MHz = _resolve_rabi_MHz(doc, seq)
    eta = _resolve_eta(doc, seq)
    n_pulses = int(seq["n_pulses"]["value"])
    dt_us = _to_us(seq["pulse_duration"])
    dt_sep_us = _to_us(seq["inter_pulse_spacing"])
    T_m_us = 1.0 / omega_m_MHz
    t_sep_factor = dt_sep_us / T_m_us

    ac_phase_deg = 0.0
    if "analysis_phase_deg" in seq:
        ac_phase_deg = _angle_deg(seq["analysis_phase_deg"])

    return {
        # Engine's "omega_m", "omega_r" are angular (rad/us when engine
        # time unit is us). 2*pi factors match the convention used
        # throughout wp-strobo-2p0/numerics/run_sweep.py.
        "omega_m": 2.0 * math.pi * omega_m_MHz,
        "omega_r": 2.0 * math.pi * omega_r_MHz,
        "eta": eta,
        "n_pulses": n_pulses,
        "delta_t_us": dt_us,
        "t_sep_factor": t_sep_factor,
        "ac_phase_deg": ac_phase_deg,
        # Metadata for logging / manifest provenance.
        "_provenance": {
            "document_id": doc["document_id"],
            "sequence_name": sequence_name,
            "omega_m_MHz": omega_m_MHz,
            "omega_r_MHz": omega_r_MHz,
            "eta": eta,
            "T_m_us": T_m_us,
            "t_sep_factor": t_sep_factor,
            "pi2_delivered": n_pulses * omega_r_MHz * math.exp(-eta ** 2 / 2) * dt_us * 2 * math.pi,
            # ^ in radians; equals pi/2 iff the sequence is pi/2-calibrated.
        },
    }


def thermal_n_for_sequence(doc: dict, sequence_name: str) -> float:
    """Convenience: thermal occupation of the mode used by a sequence."""
    seq = doc["pulse_sequences"][sequence_name]
    mode = doc["trap"]["motional_modes"][seq["mode"]]
    if "thermal_occupation" in mode:
        return float(mode["thermal_occupation"]["value"])
    return 0.0


# -------------------------------------------------------------------
# CLI summary
# -------------------------------------------------------------------

def _fmt_measured(v: dict, unit_override: str | None = None) -> str:
    val = v["value"]
    unit = unit_override or v.get("unit", "")
    stderr = v.get("stderr")
    src = v.get("source", "")
    err_part = f" +/- {stderr:g}" if stderr is not None else ""
    return f"{val:g}{err_part} {unit}   [{src}]"


def _print_summary(doc: dict) -> None:
    print("=" * 78)
    print(f"Document: {doc.get('document_title', '?')}")
    print(f"  id={doc['document_id']}   date={doc['calibration_date']}   operator={doc.get('operator', '?')}")
    if (ref := doc.get("apparatus_reference")):
        print(f"  apparatus_ref: {ref}")
    print("=" * 78)

    ion = doc.get("ion", {})
    if ion:
        print(f"\nIon: {ion.get('species', '?')}")
        if (tr := ion.get("qubit_transition")):
            om = tr.get("omega_over_2pi")
            if om:
                print(f"  qubit transition '{tr.get('name', '?')}': omega/(2pi) = {_fmt_measured(om)}")

    print("\nMotional modes:")
    for name, mode in doc["trap"]["motional_modes"].items():
        print(f"  [{name}]  {mode.get('description', '')}")
        print(f"    omega_m/(2pi) = {_fmt_measured(mode['omega_m_over_2pi'])}")
        if "lamb_dicke_eta" in mode:
            print(f"    eta           = {_fmt_measured(mode['lamb_dicke_eta'])}")
        if "thermal_occupation" in mode:
            print(f"    <n>_thermal   = {_fmt_measured(mode['thermal_occupation'])}")

    print("\nBeams:")
    for name, beam in doc["beams"].items():
        print(f"  [{name}]  {beam.get('description', '')}")
        if "rabi_over_2pi" in beam:
            print(f"    Omega/(2pi)   = {_fmt_measured(beam['rabi_over_2pi'])}")
        for mk, ev in beam.get("lamb_dicke_eta_per_mode", {}).items():
            print(f"    eta[{mk}]  = {_fmt_measured(ev)}")

    print("\nPulse sequences (derived engine kwargs):")
    for name in doc["pulse_sequences"]:
        kw = engine_kwargs_for_sequence(doc, name)
        pr = kw.pop("_provenance")
        seq = doc["pulse_sequences"][name]
        print(f"  [{name}]  {seq.get('description', '')}")
        print(f"    beam='{seq['beam']}'  mode='{seq['mode']}'")
        print(f"    N = {pr['omega_m_MHz']:.6f} MHz (carrier),  "
              f"Omega/(2pi) = {pr['omega_r_MHz']:.4f} MHz,  "
              f"eta = {pr['eta']:.4f}")
        print(f"    N_pulses = {kw['n_pulses']}  delta_t = {kw['delta_t_us']*1e3:.0f} ns  "
              f"t_sep_factor = {pr['t_sep_factor']:.5f}")
        print(f"    N*Omega*DW*dt = {pr['pi2_delivered']:.6f} rad  "
              f"(target pi/2 = {math.pi/2:.6f})  "
              f"-> {'pi/2-calibrated' if abs(pr['pi2_delivered'] - math.pi/2) < 1e-3 else 'off-calibration'}")

    if "decoherence" in doc:
        print("\nDecoherence (informational):")
        for name, v in doc["decoherence"].items():
            print(f"  {name}: {_fmt_measured(v)}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load and summarise an experimental_params_v1 document."
    )
    parser.add_argument("path", type=str, help="Path to the parameter JSON.")
    args = parser.parse_args()
    doc = load_params(args.path)
    _print_summary(doc)


if __name__ == "__main__":
    main()
