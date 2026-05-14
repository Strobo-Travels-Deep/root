# WP-W Lit-Review Tracker

**Purpose.** Persistent log of references encountered during the WP-W
lit-review pass (per §5a discipline). Tracks primary papers (extracted
to `refs/extractions/*.md`), secondary references encountered, and
relevance assessment.

**Started:** 2026-05-13 (WP-W v0.4 → execution-ready transition).

-----

## A. Primary papers — extraction status

| key | status | extraction | notes |
|---|---|---|---|
| [Hasse24] | ✅ extracted | [Hasse24.md](./extractions/Hasse24.md) | Direct experimental antecedent; protocol foundation. |
| [FH20] | ✅ extracted | [FH20.md](./extractions/FH20.md) | **Direct theoretical+experimental precedent for χ-FFT tomography in trapped ions.** Reframes WP-W's contributions significantly. |
| [LD97] | ⏳ pending | — | Displaced-parity Wigner measurement origin. |
| [CG69] | ⏳ pending | — | Phase-space formalism foundation. |
| [STO12] | ⏳ pending | — | Sympathetic Wigner tomography precedent; author list unverified. |
| [Hof09] | ✅ verified inline | (via FH20 ref [13]) | **VERIFIED**: M. Hofheinz, H. Wang, M. Ansmann, R. C. Bialczak, E. Lucero, M. Neeley, A. D. O'Connell, D. Sank, J. Wenner, J. M. Martinis, A. N. Cleland, *Nature* **459**, 546 (2009). Title: *Synthesizing the quantum states of a superconducting resonator*. |

-----

## B. Secondary references — discovered, awaiting assessment

Each entry should record: (i) where encountered, (ii) what it claims,
(iii) WP-W relevance hypothesis, (iv) read decision.

### B.1 From [Hasse24] reference list (47 entries; relevant subset)

| ref | citation | encountered as | relevance hypothesis | decision |
|---|---|---|---|---|
| Hasse [11] | Leibfried, Blatt, Monroe, Wineland, *Rev. Mod. Phys.* **75**, 281 (2003) | canonical trapped-ion review | Engine context; σ_z vs. σ_x SDF distinction; foundational notation conventions. | **READ** — likely add to §References as [LBMW03]. |
| Hasse [21] | Leibfried, DeMarco et al., *Nature* **422**, 412 (2003) | geometric phase gate demonstration | State-dependent forces in trapped ions; possibly relevant to WP-W §7#3 σ_z-SDF lineage. | **READ** — assess against WP-W §7#3 claims. |
| Hasse [27] | Affolter, Gilmore, Jordan, Bollinger, *Phys. Rev. A* **102**, 052609 (2020) | phase-stable pulse trains | Recent precedent for phase-coherent pulse trains in ion sensing. | **MAYBE** — check whether their stroboscopic technique overlaps WP-W. |
| Hasse [28] | Vasquez et al., *Phys. Rev. Lett.* **130**, 133201 (2023) | recent trapped-ion phase-space work | Modern context for WP-W's claim. | **MAYBE** — check for prior-art overlap. |
| Hasse [38] | A. A. Pushkina, G. Maltese, J. I. Costa-Filho, P. Patel, A. I. Lvovsky, *Phys. Rev. Lett.* **127**, 253602 (2021) | state-dependent optical dipole forces | Possibly the closest non-trapped-ion analog of WP-W's protocol. | **READ** — adjacent platform, similar physics. |
| Hasse [43] | C. Glos, D. Porras, U. Warring, T. Schaetz, *Phys. Rev. Lett.* **117**, 174001 (2016) | earlier paper from Hasse group; cited as H_TI source | Predecessor protocol from the same group; engine Hamiltonian origin. | **READ** — direct lineage to Hasse 2024 and the engine. |
| Hasse [40] | Wittemer et al., *Phys. Rev. Lett.* **123**, 180502 (2019) | Hasse-group; trapped-ion analog of relativistic effects | Less relevant to WP-W's tomography focus. | SKIP unless context demands. |
| Hasse [41] | Wittemer et al., *Philos. Trans. R. Soc.* **378**, 20190230 (2019) | follow-up to [40] | Less relevant. | SKIP. |
| Hasse [4,5] | LIGO / Virgo collaborations | gravitational-wave context | Not directly relevant. | SKIP. |
| Hasse [10] | Gilmore, Affolter et al., *Science* **373**, 673 (2021) | trapped-ion sensing of feeble forces | Possibly relevant context. | MAYBE. |
| Hasse [29] | Saner et al., *Phys. Rev. Lett.* **131**, 220601 (2023) | recent trapped-ion (Oxford) | Modern context. | MAYBE. |
| Hasse [42] | Friedenauer et al., *Appl. Phys. B* **84**, 371 (2006) | apparatus details (Mg+ trap) | Engineering background; skip. | SKIP. |

### B.2 From reviewer feedback (earlier in session)

| ref | citation | encountered as | relevance hypothesis | decision |
|---|---|---|---|---|
| Leibfried–Wineland tomography | various PRLs late 1990s | reviewer flagged as missing from §References | Original trapped-ion motional-state tomography; pre-Flühmann phase-space measurement. | **READ — high priority gap.** |
| Brune–Haroche parity measurement | Brune, Haroche group, late 1990s cQED | reviewer flagged | Experimental implementation of LD97 in cavity QED; lineage anchor. | MAYBE — would strengthen LD97 → FH20 narrative. |
| Lougovski Fresnel-representation tomography | unspecified | reviewer flagged | Methodologically adjacent phase-space tomography. | MAYBE — assess if cited by FH20. |
| Mizrahi–Monroe stroboscopic kicks | Mizrahi et al. 2013–2017 | reviewer flagged; cited in `ideal-limit-principles.md` | Ultrafast kick predecessor; contrasting regime to WP-W's resolved-sideband. | **READ** if `ideal-limit-principles.md` doesn't already cover it for WP-W's purposes. |

### B.3 From [FH20] reference list (53 entries; relevant subset)

| ref | citation | encountered as | relevance hypothesis | decision |
|---|---|---|---|---|
| FH20 [30] | **S. Wallentowitz, W. Vogel, *Phys. Rev. Lett.* **75**, 2932 (1995)** | direct-χ reconstruction *original proposal* | **PREDATES LD97 by two years.** WP-W should add as the earliest theoretical anchor. | **MUST READ — promote to primary.** |
| FH20 [2] | **D. Leibfried, D. M. Meekhof, B. E. King, C. Monroe, W. M. Itano, D. J. Wineland, *Phys. Rev. Lett.* **77**, 4281 (1996)** | first trapped-ion Wigner reconstruction via Fock-state populations | Pre-FH20 trapped-ion tomography baseline; the "Leibfried-Wineland tomography" gap reviewer flagged. | **MUST READ — promote to primary as [LMKMIW96].** |
| FH20 [20] | **P. Bertet, A. Auffeves, P. Maioli, S. Osnaghi, T. Meunier, M. Brune, J. M. Raimond, S. Haroche, *Phys. Rev. Lett.* **89**, 200402 (2002)** | *first cQED implementation of LD97* (Brune-Haroche group) | Direct experimental implementation of [LD97] in cavity QED. | **MUST READ — promote to primary as [Bertet02].** |
| FH20 [4] | C. Flühmann, V. Negnevitsky, M. Marinelli, J. P. Home, *Phys. Rev. X* **8**, 021001 (2018) | FH20 predecessor — Wigner reconstruction via Fock populations in trapped ions | Useful context; less critical than FH20. | MAYBE — read abstract only. |
| FH20 [22] | B. Vlastakis et al., *Science* **342**, 607 (2013) | large-amplitude cat-state Wigner tomography in cQED | Lineage anchor (between Hof09 and FH20). | MAYBE — abstract-level read sufficient. |
| FH20 [39] | D. J. Wineland, C. Monroe, W. M. Itano, D. Leibfried, B. E. King, D. M. Meekhof, *J. Res. NIST* **103**, 259 (1998) | canonical trapped-ion review (pre-LBMW03) | Predates LBMW03 from Hasse [11]; same group, expanded version becomes LBMW03. | SKIP — LBMW03 supersedes for our purposes. |
| FH20 [33] | J. Casanova, C. E. López, J. J. García-Ripoll, C. F. Roos, E. Solano, *Eur. Phys. J. D* **66**, 222 (2012) | trapped-ion phase-space tomography | **Note:** different journal from [STO12] (which is PRA 85, 042109, 2012). Still need to verify [STO12] separately. | MAYBE. |
| FH20 [11] | D. M. Meekhof, C. Monroe, B. E. King, W. M. Itano, D. J. Wineland, *Phys. Rev. Lett.* **76**, 1796 (1996) | generation of nonclassical motional states | Foundational; same group / time as [LMKMIW96]. | MAYBE. |
| FH20 [36] | K. G. Johnson, B. Neyenhuis, J. Mizrahi, J. D. Wong-Campos, C. Monroe, *Phys. Rev. Lett.* **115**, 213001 (2015) | the Monroe ultrafast / stroboscopic-kick line | Cited in `ideal-limit-principles.md` for the Hasse comparison; if not already covered there, read. | DEFER — likely already covered in the ledger. |

### B.4 To be discovered

This section grows as later extractions surface new references.

-----

## C. Read order rationale

1. **[FH20]** first — modern trapped-ion characteristic-function tomography. Highest risk of "this has already been done"; need to know the gap WP-W actually fills.
2. **[LD97]** second — original displaced-parity scheme; cavity-QED context. Anchors WP-W's lineage statement.
3. **[CG69]** third — phase-space formalism. Foundational but rarely surprising for someone who has read FH20 / LD97.
4. **[STO12], [Hof09]** for author/bibliographic verification only — abstract-level read sufficient.
5. **Secondary references** as triaged in §B above, after primaries.

-----

## D. Output goals

After this lit-review pass:

1. Five to seven extraction files in `extractions/`.
2. One `contextual-notes.md` lineage map (one paragraph per primary
   paper, plus the "what WP-W actually contributes" summary).
3. Updated WP-W §1 / §3 / §7#4 / §8 / §References with correct
   credit attribution.
4. This tracker doc archived as the audit trail; future v0.5 work
   can extend it.
