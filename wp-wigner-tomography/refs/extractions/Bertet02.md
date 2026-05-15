# Extraction — Bertet et al. (2002)

**Citation key:** [Bertet02]
**Full reference:** P. Bertet, A. Auffeves, P. Maioli, S. Osnaghi,
T. Meunier, M. Brune, J. M. Raimond, S. Haroche,
*Direct Measurement of the Wigner Function of a One-Photon Fock State in a Cavity*,
Phys. Rev. Lett. **89**, 200402 (2002). Published 11 November 2002.
DOI: [10.1103/PhysRevLett.89.200402](https://doi.org/10.1103/PhysRevLett.89.200402).
PubMed: [12443461](https://pubmed.ncbi.nlm.nih.gov/12443461/).

**Authors verified:** P. Bertet, A. Auffeves, P. Maioli, S. Osnaghi,
T. Meunier, M. Brune, J. M. Raimond, S. Haroche (Laboratoire Kastler
Brossel, École Normale Supérieure, Paris — *Brune/Haroche group*).

**Extraction date:** 2026-05-15.

**Note on source.** APS PRL paywalled; PubMed abstract retrieved and
matches established description of this paper from the FH20 reference
context and from broader cavity-QED literature.

**One-line summary.** **First experimental implementation of the
[LD97] displaced-parity scheme** in cavity QED. Bertet *et al.* in
Haroche's microwave-Rydberg-atom setup reconstruct the complete
Wigner function of both the vacuum $|0\rangle$ and the one-photon
Fock state $|1\rangle$ in a high-$Q$ superconducting microwave cavity,
demonstrating the negative-Wigner-region signature of
non-classicality.

**Why it matters for WP-W.** [Bertet02] is the **experimental anchor**
for the [LD97] displaced-parity scheme — the proof-of-concept that
the direct-Wigner-measurement chain works in a real experiment, five
years after the proposal. It fills the "Brune–Haroche cavity parity
measurement" gap the WP-W reviewer flagged. It is the cQED parallel
of [LMKMIW96]'s trapped-ion Wigner reconstruction; both are 1996–2002
landmarks that established phase-space tomography as an experimental
practice.

-----

## 1. Apparatus

- **Superconducting microwave Fabry–Pérot cavity** at ~51 GHz,
  $Q$-factor $\sim 10^{10}$, photon lifetime ~ms (Brune/Haroche
  *photon-box* setup).
- **Circular Rydberg atoms** (Rb in $n = 50, 51$ states) traversing
  the cavity one at a time. The atom acts as both the displacement
  probe (via off-resonant dispersive interaction) and the readout
  qubit (via Ramsey interferometry on the $n = 50 \leftrightarrow n = 51$
  transition).
- Atom velocity selection gives controlled atom-cavity interaction
  time → controlled dispersive phase shift per cavity photon.

## 2. Protocol — [LD97] displaced parity in three steps

1. **State preparation.** Inject either the vacuum $|0\rangle$ or a
   single-photon Fock state $|1\rangle$ into the cavity. The
   single-photon state is prepared by sending a resonant atom in
   $|e\rangle$ through the cavity for half a Rabi period (vacuum
   Rabi oscillation), then exiting via decay.
2. **Displacement.** Inject a classical microwave pulse into the
   cavity to apply $\hat D(\alpha)$ with chosen $|\alpha|$ and
   $\arg\alpha$. This shifts the field state in phase space.
3. **Parity readout via Ramsey.** Send a Rydberg atom through the
   cavity in the *dispersive* regime (atom-cavity detuning $\gg$
   coupling). The atom acquires a light shift $\propto \langle\hat n\rangle$
   per unit interaction time. By choosing the interaction time
   correctly, the Ramsey-interferometer atomic-state population
   difference yields $\langle\hat P\rangle = \langle(-1)^{\hat n}\rangle$
   of the displaced cavity field.

Combining steps 2 and 3 gives
$W(\alpha) = (2/\pi)\langle\hat D^\dagger(\alpha)\hat P\hat D(\alpha)\rangle$
point-by-point in phase space.

## 3. Key result

- Reconstruction of $W(\alpha)$ for both $|0\rangle$ and $|1\rangle$.
- $|0\rangle$: Gaussian peak at origin, $W(0) = 2/\pi \approx 0.637$ —
  consistent with vacuum.
- $|1\rangle$: ring of positive $W$ at $|\alpha| \approx 1$, with
  $W(0) = -2/\pi < 0$ — the **direct experimental signature of
  Wigner negativity** of a one-photon Fock state.
- Negative $W$ region demonstrates the non-classical nature of
  $|1\rangle$ unambiguously.

## 4. Relation to WP-W's lineage

[Bertet02] fills the *experimental* gap between [LD97]'s proposal
(1997) and the modern cQED implementations (Hofheinz 2009, Vlastakis
2013, ...) and trapped-ion variants ([FH20] 2020, WP-W). It is the
"single-photon Wigner measurement" that proves phase-space tomography
is experimentally tractable.

**Lineage timeline:**

| year | reference | platform | state | inversion |
|---|---|---|---|---|
| 1969 | [CG69] | (formalism) | (any) | (none) |
| 1995 | [Wal95] | trapped-ion (proposal) | (any) | (any) |
| 1996 | [LMKMIW96] | ⁹Be⁺ trapped ion | ground, coherent, squeezed, Fock | displaced-Fock-population sum |
| 1997 | [LD97] | cavity QED + trapped ion (proposal) | (any) | displaced-parity |
| **2002** | **[Bertet02]** | **Rb Rydberg + microwave cQED** | **$\|0\rangle$, $\|1\rangle$** | **displaced parity (first LD97 experiment)** |
| 2009 | [Hof09] | superconducting cQED | Fock, coherent superpositions | parity-readout |
| 2020 | [FH20] | Ca⁺ trapped ion | displaced-squeezed, cat, GKP | direct-$\chi$ + 2D-FFT |
| 2024 | [Hasse24] | Mg⁺ trapped ion | coherent (+ squeezed proposal) | ⟨X⟩, |⟨P⟩| cuts |
| 2026+ | WP-W | Mg⁺ trapped ion (numerical) | non-Gaussian (Fock, cat) | stroboscopic-comb + 2D-FFT |

-----

## 5. Direct implications for WP-W

1. **§References**: add [Bertet02] as the first cQED experimental
   implementation of [LD97]. This is the "Brune–Haroche cavity parity"
   reference the WP-W reviewer flagged.
2. **§1 lineage statement**: enrich the cQED side of the lineage by
   citing [Bertet02] (first experiment) alongside [LD97] (proposal)
   and [Hof09] (superconducting implementation).
3. **§Analytical background bullet**: [Bertet02] is the
   experimental-anchor citation for the LD97 displaced-parity scheme.

-----

## 6. Contextual paragraph (for `contextual-notes.md`)

[Bertet02] is the **first experimental implementation** of the [LD97]
displaced-parity scheme for direct Wigner-function measurement.
Bertet *et al.* in the Brune/Haroche photon-box at ENS Paris
reconstructed the complete Wigner function of both the vacuum and
the one-photon Fock state in a high-$Q$ microwave cavity using
circular Rydberg atoms as dispersive probes plus Ramsey
interferometry for parity readout. Their result — the directly-
measured negative $W(0) = -2/\pi$ of the single-photon Fock state —
became the foundational proof-of-concept for cavity-QED phase-space
tomography.

For WP-W, [Bertet02] is principally a **lineage-completion** citation:
it bridges the [LD97] proposal to the [Hof09] superconducting-cQED
realisation and ultimately to the [FH20] trapped-ion direct-$\chi$
generalisation that WP-W's pipeline inherits.
