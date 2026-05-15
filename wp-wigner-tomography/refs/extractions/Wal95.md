# Extraction — Wallentowitz & Vogel (1995)

**Citation key:** [Wal95]
**Full reference:** S. Wallentowitz and W. Vogel,
*Reconstruction of the Quantum Mechanical State of a Trapped Ion*,
Phys. Rev. Lett. **75**, 2932 (1995). Published 16 October 1995.
DOI: [10.1103/PhysRevLett.75.2932](https://doi.org/10.1103/PhysRevLett.75.2932).

**Authors verified:** S. Wallentowitz and W. Vogel (Fachbereich
Physik, Universität Rostock, Germany).

**Extraction date:** 2026-05-15.

**Note on source.** APS PRL paywalled; no arXiv preprint located
(1995 predates AMO arXiv usage). Extraction here is anchored on the
confirmed bibliographic data, abstract summary, and the FH20 citation
context which identifies [Wal95] as "the original direct-$\chi$
proposal" (FH20 ref [30]).

**One-line summary.** Proposes the **first scheme for direct
reconstruction of the motional quantum state of a trapped ion** by
mapping motional information onto the ion's electronic dynamics via
laser-driven coupling and reading it out by resonance-fluorescence
detection on a separate strong transition. Predates [LD97] by ~18
months and [LMKMIW96] by ~10 months.

**Why it matters for WP-W.** [Wal95] is the **historical origin** of
the direct-readout trapped-ion motional-state tomography programme.
WP-W's current §References does not include it; the FH20 read
(extraction §6) flags it as the missing earliest-anchor citation.
Adding [Wal95] to WP-W §References properly pins the historical
order: Wallentowitz–Vogel (1995, proposal) → Leibfried-Meekhof
(1996, first experiment) → Lutterbach–Davidovich (1997, parity-based
variant) → ... → Flühmann–Home (2020, direct-$\chi$ trapped-ion).

-----

## 1. Core proposal

The motional state of a single trapped ion can be reconstructed
*completely* — both the density matrix in the Fock basis and the
Wigner function — by:

1. Driving the ion with a sequence of laser pulses tuned to a
   long-lived electronic transition. The choice of laser frequency
   (carrier or sideband), duration, and phase controls *which* aspect
   of the motional state is mapped onto the electronic populations.
2. Reading out the electronic populations by resonance fluorescence
   on a separate **strong** electronic transition — this gives high
   quantum efficiency (close to unity) for the detection step,
   independent of the much lower fluorescence rate on the
   tomography-coupling transition itself.

The combination is high-efficiency motional-state characterisation
*despite* the low coupling strength of the spectroscopy transition —
the "detection-quantum-efficiency-decoupled" idea that recurs in
[LD97] and [FH20].

-----

## 2. Relation to subsequent work

**Successors / extensions:**
- [LMKMIW96] Leibfried, Meekhof, King, Monroe, Itano, Wineland, *PRL*
  77, 4281 (1996) — *first experimental implementation* of
  motional-state reconstruction in a trapped ion. Uses a Fock-state-
  population approach plus displacement scans → Wigner function.
- [LD97] Lutterbach & Davidovich, *PRL* 78, 2547 (1997) — variant
  using *displaced parity* readout via dispersive coupling +
  Ramsey interferometry. Applies to both cavity QED and trapped ions.
- [FH20] Flühmann & Home, *PRL* 125, 043602 (2020) — modern direct-
  $\chi$ implementation using bichromatic SDF + Z-readout on Ca⁺.
  Cites [Wal95] as ref [30] for the original direct-$\chi$ proposal.

**Lineage of trapped-ion motional-state tomography:**

| year | citation | contribution |
|---|---|---|
| 1969 | [CG69] | $s$-ordered formalism foundation. |
| **1995** | **[Wal95]** | **First proposal: direct motional-state reconstruction in a trapped ion via electronic mapping + fluorescence readout.** |
| 1996 | [LMKMIW96] | First experimental implementation in a trapped ion (Fock-population path). |
| 1997 | [LD97] | Displaced-parity variant; applies to cavity QED + trapped ions. |
| 2002 | [Bertet02] | First cQED experimental implementation of [LD97]. |
| 2009 | [Hof09] | cQED implementation in superconducting circuits. |
| 2020 | [FH20] | Modern trapped-ion direct-$\chi$ tomography on Ca⁺. |
| 2024 | [Hasse24] | Stroboscopic monochromatic AC train on Mg⁺; doesn't invoke $\chi$. |
| 2026+ | WP-W | Stroboscopic-comb adaptation of [FH20]'s $\chi$-tomography to [Hasse24]'s engine. |

-----

## 3. Direct implications for WP-W

1. **§References**: add [Wal95] as the earliest direct-readout
   trapped-ion tomography proposal. Predates [LD97] in the lineage.
2. **§1 lineage statement**: optionally update the lineage to begin
   with [Wal95] rather than [LD97]; the question is whether to
   credit "earliest trapped-ion tomography proposal" or "earliest
   displaced-parity proposal." Both are correct; the cleanest WP-W
   framing credits the trapped-ion lineage starting at [Wal95].
3. **§Analytical background bullet** (current text mentions [LD97]
   first): add [Wal95] as predecessor.

-----

## 4. Contextual paragraph (for `contextual-notes.md`)

[Wal95] is the **historical origin** of the trapped-ion motional-state
tomography programme. Wallentowitz & Vogel proposed in 1995 that the
full motional quantum state of a single trapped ion can be transferred
to the electronic dynamics by appropriately chosen laser pulses, then
read out with near-unity efficiency on a separate strong transition.
This kicked off the entire trapped-ion phase-space tomography
literature: [LMKMIW96] gave the first experimental demonstration
within a year; [LD97] re-cast the readout as displaced parity for both
cavity QED and ion traps; and [FH20] generalised it to direct-$\chi$
reconstruction. WP-W inherits this lineage via its $\chi$-based
inversion chain — [Wal95] should be the earliest citation in the
lineage statement.
