# Council Memo — Proposed WP: Strong/Weak-Binding Coastline Map

**Council Memo · post-execution fold-in · v0.4 · 2026-04-21**
**Status:** v0.1.1 of the scoped WP is executed, plotted, and committed at [wp-strong-weak-coastline/](wp-strong-weak-coastline/) (commit `528267b`). The memo's locked decisions survived execution; §5.1 was resolved by co-lock (lemma inlined in the WP README §2). This v0.4 folds the v0.1 outcomes back into the memo and retargets §9 as a forward-looking ask for WP-C v0.2. Planning text from v0.2/v0.3 preserved verbatim below for provenance; post-execution material lives in new §2.6, §5.3, and §9 rewrite.
**Status (pre-execution legacy):** Findings + locked-decisions package for final Integrator pass, pending one open item (§5.1). Guardian-synthesised, Architect- and Scout-reviewed; Integrator stance not yet registered.
**Origin:** Follow-up to the §3.3 tutorial section of
[notebooks/00_tutorial_pulse_train.ipynb](notebooks/00_tutorial_pulse_train.ipynb)
and the drive-strength scan of
[2026-04-21-coh-theta0-det-rabi5x.md](wp-hasse-reproduction/logbook/2026-04-21-coh-theta0-det-rabi5x.md).

*Local candidate framework (no parity implied with externally validated laws).*

*Epistemic category: T2 parametric enumeration around the T1b calibration point established by WP-V.*

-----

## 1. Subject

Map the boundary (the "coastline") between the **strong-binding / resolved-sideband** regime, in which the stroboscopic protocol resolves a discrete comb at $\delta = k\omega_m$, and the **weak-binding** regime, in which pulse bandwidth and/or train shortness merges adjacent teeth into a continuous Doppler-like response. The question is when — along the $(N,\ \delta t/T_m)$ axis pair, with the $\Omega$-calibration scheme specified in §4.1 — the Fig 6a/6b phenomenology survives.

This is a distinct axis from WP-E (which fixes the train shape and varies the coherent-state parameters) and from the 2026-04-21 Rabi-amplitude follow-up (which fixes the train shape and varies $\Omega$). The missing axes are $N$ (train length) and $\delta t/T_m$ (pulse duration relative to mode period).

-----

## 2. Findings summary — what the council already has on the table

### 2.1 The strong-binding picture is the regime WP-V/WP-E validated

- **WP-V** ([2026-04-13 kickoff/results](wp-hasse-reproduction/logbook/2026-04-13-results.md)) reproduced Hasse Fig 6a/6b at $N=30$, $\delta t/T_m = 0.13$, $\eta = 0.397$, $\omega_m/(2\pi)=1.3$ MHz, $|\alpha|=3$, within the 5% anchor tolerance.
- **WP-E** ([README](wp-phase-contrast-maps/README.md)) noted in its §1 motivation that the regime is "*neither* impulsive ($\delta t/T_m \approx 0.05$) nor fully resolved-sideband ($\Omega/\omega_m \approx 0.23$, with Doppler widths $\delta_D \gg \Omega$ at zero point)." The stroboscopic protocol therefore sits **already near the coastline**, not deep in the resolved limit, which is why a coastline map is worth producing rather than assuming.
- **Engine-level bit-for-bit validation** of the restructured v1.0.0 package against WP-V v4 data: max $|\Delta|$ per field $\leq 3.4 \cdot 10^{-14}$ ([2026-04-20 logbook §3](wp-hasse-reproduction/logbook/2026-04-20-coh-theta0-det.md)). The engine can be trusted to extrapolate away from the calibration point.

### 2.2 The drive-strength axis is already mapped

The 2026-04-21 follow-up ([§6](wp-hasse-reproduction/logbook/2026-04-21-coh-theta0-det-rabi5x.md), [rabi_scan_v5.h5](wp-hasse-reproduction/numerics/rabi_scan_v5.h5)) scanned `RABI_SCALE` $\in [0.2, 5.0]$ at $\delta=0$. Headline numbers:

| quantity | behaviour vs $\Omega/\Omega_\text{cal}$ |
|---|---|
| diamond amplitude $\frac12(\max-\min)\langle\sigma_z\rangle$ | oscillates with N-pulse Rabi envelope, first peak at RABI_SCALE $\approx 1$ (0.787), first null at $\approx 2$ (0.134), revival at $\approx 3.2$ (0.740) |
| $|\delta\langle n\rangle|_\text{peak}$ | tracks the diamond envelope; peak value $\approx 1.20$ across the scan |
| $\min_\vartheta |C|$ | touches zero at RABI_SCALE $\approx 1.2$ and $\approx 3.2$ |

**Key takeaway for the proposed WP:** the $\Omega$-axis is analytically distinct from the $(N, \delta t)$ resolvedness axis, though operational coupling reappears whenever the calibration scheme changes the total train rotation. The Rabi-scan result is also the reason the §2.2 "saturation" claim was retracted in the §11 consistency patch — a reminder that envelope-oscillation effects will recur whenever we vary any axis that changes total train rotation. §4.1 locks a calibration that isolates $N$ and $\delta t$ from $\Omega$.

### 2.3 Fock-basis truncation tolerance is known

[§9 of the rabi5x logbook](wp-hasse-reproduction/logbook/2026-04-21-coh-theta0-det-rabi5x.md) and [fock_leakage_rabi5x_v5.h5](wp-hasse-reproduction/numerics/fock_leakage_rabi5x_v5.h5) audited the NMAX=60 truncation at 5× overdrive over a 64×81 grid in the worst-case tooth region. Top-5 leakage $\leq 4.9\cdot 10^{-20}$. NMAX=40 is marginal ($1.2 \cdot 10^{-8}$). The proposed WP retains NMAX $\geq 60$ at $|\alpha|=3$ and extends the audit to the $|\alpha|\times\delta t/T_m$ extremes before the full grid sweep (§6).

### 2.4 Conceptual distinction is already on paper

[Tutorial notebook §3.3](notebooks/00_tutorial_pulse_train.ipynb) introduces the strong/weak distinction qualitatively, via two dimensionless ratios:

- Tooth width in units of $\omega_m$: $1/N$, need $\ll 1$.
- Pulse bandwidth in units of $\omega_m$: $\delta t/T_m$, need $\ll 1$.

and names the Doppler halfwidth $\eta|\alpha|\,\omega_m$ as the broad-line scale in the weak limit. This memo turns §3.3 from an illustrated concept into a quantitative phase diagram.

### 2.5 Lamb–Dicke-validity status of prior WPs

A Guardian-stance audit flagged that the **motional-amplitude LD parameter** $\eta\sqrt{\langle n\rangle + 1}$ is already $\approx 1.26$ at the WP-V baseline ($\eta=0.397$, $|\alpha|=3$), exceeding 1. Neither WP-V nor WP-E explicitly audited this. Both WPs rely on an engine that retains the full coupling operator $C = e^{i\eta(a+a^\dagger)}$ rather than a low-order expansion in $\eta$. The engine may therefore remain valid beyond the naive motional-LD bound, but that validity must now be specified explicitly. The *drive-strength LD* parameter $\Omega_\text{eff}/\omega_m \approx 0.21$ is comfortably $< 1$ at the baseline. A formal specification of which LD inequality the engine's approximations actually require is the single open item in §5.1; it conditions the $|\alpha|=5$ row of §4.4.

### 2.6 Post-execution fold-in (v0.4, 2026-04-21)

WP-C v0.1.1 is executed: [wp-strong-weak-coastline/](wp-strong-weak-coastline/), results at [logbook/2026-04-21-results.md](wp-strong-weak-coastline/logbook/2026-04-21-results.md). Total wall time 15.5 s — well under the ≤ 2 min memo budget. Headline findings reshape what the memo had anticipated:

- **N-degeneracy under option (a) recalibration.** $V$ varies by $\leq 0.005$ across $N \in \{3,6,12,24,48,96\}$ at every $(|\alpha|, \delta t/T_m)$ slice. The coastline collapses to a **1D curve in $\delta t/T_m$ alone** once $\Omega$ is recalibrated per cell. The memo's §2 premise that $(N, \delta t/T_m)$ were two *independent* missing axes is thereby refuted for this calibration scheme. N only re-emerges as load-bearing in the option-(b) control slice, where it parameterises the Rabi envelope (memo §4.1 Guardian-2 D9 caveat: *power-broadening artefacts*).
- **$\chi$-collapse falsified — positive result per §3.4 / §4.5.** Cells at matched $\chi \approx 1.2$ carry $V$ spanning $0.10$ ($|\alpha|=3$) to $0.85$ ($|\alpha|=1$); the root-sum-square composition of train-length, pulse-bandwidth, and Doppler widths does not reproduce the scan data. Each individual width acts monotonically within its row, but the three widths do *not* combine in quadrature.
- **Doppler-merging regime not reached** at $\delta = 0.5\,\omega_m$. $P \approx 1.00$ across the grid except in drive-LD-breach cells. The two-map rubric therefore discriminates *pulse-broadening* (low $V$, high $P$) from *strong-binding* (high both) cleanly but never observes *Doppler merging* (low both). This is a v0.2 scope item: probe $P$ at a detuning $\delta \sim \eta|\alpha|\,\omega_m$ that lands inside the Doppler-broadened sideband.
- **Non-monotonic $\alpha$ at $\delta t/T_m = 0.80$.** $V$ is $\{0.998, 0.760, 0.101, 0.377\}$ for $|\alpha| \in \{0,1,3,5\}$. The $\alpha=5$ *recovery* from the $\alpha=3$ trough is genuinely finite-$\delta t$ physics: the impulsive-limit reference $V_\text{imp} \approx 0.865$ is **uniform** across all $N$ and all $|\alpha|$ (limited by the Debye–Waller factor alone), so all finite-$\delta t$ curves head to the same limit. A probe at $|\alpha| \in \{3.5, 4.0, 4.5, 5.5\}$ at $\delta t/T_m = 0.80$ is flagged in the results logbook §4.1.
- **§5.1 lemma resolution.** Engine retains the full coupling $C = \exp[i\eta(a+a^\dagger)]$ as a matrix exponential ([scripts/stroboscopic/operators.py:23](scripts/stroboscopic/operators.py#L23)); motional-LD inequality $\eta\sqrt{\langle n\rangle + 1} \lesssim 1$ bounds the physical-picture interpretability, **not** engine validity. Engine validity is governed by drive-LD $\Omega_\text{eff}/\omega_m \leq 0.3$ alone (§4.1 ceiling). $|\alpha|=5$ therefore admitted; motional-LD breaches rendered as a distinguishable hatching layer rather than exclusion. v0.1.1 pre-audit confirmed NMAX 60 safe for $|\alpha| \in \{0,1,3\}$, NMAX 80 required for $|\alpha|=5$.
- **§4.2 grid geometry validated.** The 6×6 geometric grid executes in 15.5 s for four $|\alpha|$ values; no re-deliberation required. The option-(b) control slice at $\delta t/T_m = 0.13$ recovers the expected Rabi-envelope structure, confirming Guardian-2 D9 inline.
- **Floquet-synchronisation promotion criterion (§8) — not met.** Memo §8 required observable structure tracking $N$-phase rather than $N$-bandwidth. Under recalibrated $\Omega$, $V(N) \approx$ const, so no such structure exists in the v0.1 data. Floquet framing remains commentary-level; revisit only if a v0.2 finds $N$-phase-tracking structure.

Two findings are new information the memo could not have anticipated: the $N$-degeneracy (it weakens the scope that the memo argued for) and the uniform impulsive floor (it provides a cleaner analytic anchor than memo §4.5 proposed). Neither invalidates the WP; both reshape what v0.2 should ask.

-----

## 3. What is *not* yet mapped

**Post-execution (v0.4):** Items (1)–(4) below are now *mapped* in WP-C v0.1.1 as scoped. See §2.6 for the re-framing of what remains unmapped after that execution — chiefly the Doppler-merging quadrant and the $|\alpha|$-recovery mechanism. The enumeration below is preserved verbatim as the v0.3 pre-execution snapshot.

1. **The 2D plane $(N,\ \delta t/T_m)$** with other parameters held at Hasse values. Prior work samples exactly one point of this plane: $(30,\ 0.13)$.
2. **Coastline metrics** — the relation between observables we already compute ($|C|$, $\langle\sigma_z\rangle$, $\delta\langle n\rangle$) and a one-scalar "resolvedness" quantifier that flags the crossover.
3. **The interplay with $\eta|\alpha|$** — in the weak limit the classical Doppler halfwidth $\eta|\alpha|\,\omega_m$ sets the line shape, so the coastline's position depends on $|\alpha|$. A low-$|\alpha|$ slice, a vacuum control, and a high-$|\alpha|$ slice frame this dependence (§4.4).
4. **Candidate collapse form** — a tested conjecture, not a derivation. Hypothesis: tooth visibility $V$ collapses onto a single curve in a dimensionless root-sum-square parameter combining train-length, pulse-bandwidth, and Doppler-broadening widths. A natural form is
   $$\chi^2 \;=\; \bigl(1/N\bigr)^2 \;+\; \bigl(1/(\omega_m\,\delta t)\bigr)^2 \;+\; \bigl(\eta|\alpha|\bigr)^2\,,$$
   with $V \sim \exp[-\chi^2]$ or similar. The sign convention for the pulse-bandwidth term is load-bearing: narrow bandwidth (large $\delta t$) *helps* resolvedness, so the term enters as $1/(\omega_m\,\delta t)$, not as $\delta t/T_m$. At the WP-V calibration point the three terms are comparable in order of magnitude ($1/N \approx 0.03$, $1/(\omega_m\,\delta t) \approx 1.22$, $\eta|\alpha| \approx 1.19$), which is why that point sits near the coastline. The root-sum-square combination *presumes* incoherent-Gaussian composition of three physically distinct spectral widths; this is an empirical hypothesis the coastline is *meant to test*, not a derivation. **Falsification of the collapse is a positive result of the WP.** v0.1 plots all $(N, \delta t/T_m, |\alpha|)$ cells against $\chi$ and reports whether they collapse onto a single curve; residual structure is the physics we have learned.

-----

## 4. Locked decisions (with one open item parked in §5)

§4 is now *decisions*, not questions. Each subsection names the locked choice, the stance(s) endorsing it, and any caveats that must appear inline in downstream artifacts.

**Post-execution annotations (v0.4):** All §4 decisions survived execution. §4.1 (Ω ceiling) held — 10 of 36 cells breached as predicted and were hatched rather than excluded. §4.2 (6×6 geometric grid) executed in 15.5 s and produced the N-degeneracy finding (§2.6). §4.3 (two-map V/P rubric) discriminated pulse-broadening from strong-binding cleanly; Doppler merging was not reached at $\delta=0.5\,\omega_m$ and is deferred to v0.2. §4.4 (|α| baseline + stretch) ran all four values; §5.1 lemma resolution admitted $|\alpha|=5$ without downgrade. §4.5 impulsive overlay rendered on the primary V maps per §4.5 intent (not secondary, as a typo in the README §5 bullet 8 briefly suggested).

### 4.1 Calibration of $\Omega$ across the grid — LOCKED

**Decision:** Option (a) **recalibrated $\Omega$** as primary — at each $(N, \delta t)$, set $\Omega$ so that $N\cdot\Omega_\text{eff}\cdot\delta t = \pi/2$. Option (b) **fixed $\Omega = \Omega_\text{Hasse}$** retained as a single-row control slice at $\delta t/T_m = 0.13$. Three-stance convergent (Guardian-1, Guardian-2, Architect).

**Hard ceiling:** $\Omega_\text{eff}/\omega_m \leq 0.3$, pre-declared and engine-enforced. Cells breaching the ceiling are **logged and rendered as hatched overlays** on all primary heatmaps — *not* excluded, *not* cropped, *not* silently filtered. This is the single most important Clarity commitment in the WP; §6 enforces its propagation into h5 attributes and plot legends.

**Memo-level footnote:** Under option (a) with the §4.2 geometric grid, approximately **10 of 36 cells** breach the ceiling, concentrated in the small-$N$ / small-$\delta t$ corner. This is diagnostic data, not a defect.

**Control-slice caveat:** The (b) slice at $\delta t/T_m = 0.13$ carries a caption cross-referencing [rabi_scan_v5.h5](wp-hasse-reproduction/numerics/rabi_scan_v5.h5). Features at values of $N$ where $N\cdot\Omega_\text{Hasse}\cdot\delta t$ crosses a Rabi-envelope node are power-broadening artefacts, not coastline features (Guardian-2 D9).

### 4.2 Grid extent and density — PROVISIONALLY LOCKED

**Decision:** 6×6 geometric grid, chosen because the coastline is a crossover phenomenon for which log-spaced axes track the dimensionless $\chi$ of §3.4:

- $N \in \{3,\ 6,\ 12,\ 24,\ 48,\ 96\}$ (six points, geometric factor 2).
- $\delta t/T_m \in \{0.02,\ 0.05,\ 0.10,\ 0.20,\ 0.40,\ 0.80\}$ (six points, geometric factor $\approx 2$).

Three detuning values: $\delta/\omega_m \in \{0,\ 0.25,\ 0.5\}$. The intermediate $\delta=0.25\,\omega_m$ point (Architect recommendation) guards against systematic tooth-position drift under recalibrated-$\Omega$ scaling.

At each $(N, \delta t/T_m, \delta)$: 64 $\vartheta_0$ points → 36 × 3 × 64 ≈ **6900 evolutions** per $|\alpha|$ value. Compute budget as declared in §6 (≤ 30 s per $|\alpha|$; ≤ 2 min for the full set).

In addition to the 6×6 grid, a single supplementary row at $\delta t/T_m = 0.13$ is run under option (b) fixed-$\Omega$ for the control slice defined in §4.1.

Architect's original endorsement of the v0.1 7×6 grid is read as approving *scale* rather than *spacing*; if Architect objects to the geometric reparameterisation, the spacing returns to §5 as a divergence to resolve in re-deliberation.

### 4.3 Observables for the coastline — LOCKED

**Decision:** Two-map primary presentation. No single-scalar aggregation in v0.1.

**Primary metrics:**
- **Tooth visibility** $V = 1 - \min_\vartheta |C|(\vartheta_0, \delta=0)$.
- **Off-tooth coherence** $P = \langle|C|(\vartheta_0, \delta=0.5\,\omega_m)\rangle_\vartheta$.

**Failure-mode rubric** (inserted verbatim from the second-perspective review; forms the plot-caption interpretive key):

| Regime | $V$ | $P$ |
|---|---|---|
| strong-binding | high | high |
| pulse-broadening | low | high |
| Doppler merging | low | low |

The two-map choice is deliberate: it preserves failure-mode discrimination that a single scalar would erase.

**Secondary panels** (archived to h5, plotted if discriminatory):
- Diamond amplitude $\frac12(\max-\min)\langle\sigma_z\rangle$ at $\delta=0$.
- Back-action peak $|\delta\langle n\rangle|_\text{peak}$ at $\delta=0$.

**Tertiary mechanism-discriminant panel** (Scout): the ratio $V/P$ (or the $(V, P)$ covariance across the grid) supplements the two-map primary by distinguishing *pulse-bandwidth merging* from *train-shortness merging* when both $V$ and $P$ collapse. Not a replacement; a targeted diagnostic for the weak-regime corner where the two primary maps become co-monotonic.

### 4.4 $|\alpha|$ dependence — PROVISIONALLY LOCKED pending §5.1

**Decision:** Scientific baseline is the three-point set $|\alpha| \in \{0,\ 1,\ 3\}$, each with its own 2D map. An aspirational fourth point $|\alpha|=5$ is included as a contingent stress-test of the $\eta|\alpha|$ scaling in the Doppler-dominated regime; $|\alpha|=5$ runs only if the §5.1 lemma establishes engine validity for $\eta\sqrt{\langle n\rangle+1} \gtrsim 2$. v0.1 completeness does not require $|\alpha|=5$.

Justification: $|\alpha|=0$ (vacuum) isolates comb-vs-pulse structure from Doppler broadening and acts as a strong-binding control; $|\alpha|=1$ is the LD-safe tuning; $|\alpha|=3$ matches the WP-V/WP-E baseline. $|\alpha|=5$, when admitted, stress-tests the $\eta|\alpha|$ scaling where Doppler width dominates the weak-binding response.

### 4.5 Impulsive-limit overlay — LOCKED, in scope as analytic reference

**Decision:** In scope as an **analytic reference line** overlaid on the $\delta t/T_m \to 0$ edge of the primary heatmaps. *Not* a numerical grid cell (the §4.1 $\Omega$-ceiling forbids the engine from reaching that edge under option (a); the impulsive curve is an asymptotic anchor, clearly labelled as such).

Scout rationale adopted: without this overlay the weak-$\delta t$ boundary is *underdetermined* — there is no Discriminant Condition separating "engine converging to the impulsive limit" from "engine breaking down under extreme $\Omega$". The overlay provides that condition. The package already supplies `build_impulsive_train` (`scripts/stroboscopic/sequences.py:80`); no new engine development required.

### 4.6 Provenance and location — LOCKED

**Decision:** New WP directory `wp-strong-weak-coastline/`, mirroring the WP-V/WP-E structure (README / numerics / plots / logbook). Unanimous across Guardian, Architect, Scout; preserves WP-V's Hasse-reproduction mandate and aligns with the prior council precedent enforcing scope boundaries ("not a pulse-detuning analysis, that is WP-E's job", `wp-hasse-reproduction/README.md:20-22`).

-----

## 5. Open questions (load-bearing before scope-lock)

### 5.0 Resolution status (v0.4)

- **§5.1 — RESOLVED by co-lock.** Lemma inlined in [wp-strong-weak-coastline/README.md §2](wp-strong-weak-coastline/README.md). Drive-LD ceiling $\Omega_\text{eff}/\omega_m \leq 0.3$ is the single engine-validity inequality (§2.1). Motional-LD ($\eta\sqrt{\langle n\rangle+1} > 1$) is a physical-picture-interpretability flag, rendered as a distinct per-cell hatching layer but not engine-invalidating because the coupling $C = \exp[i\eta(a+a^\dagger)]$ is stored as the exact matrix exponential without $\eta$-truncation.
- **§5.2 — RESOLVED.** $|\alpha|=5$ admissible under §5.1's resolution; pre-audit confirmed NMAX 80 safe (top-5 leakage 3 × 10⁻¹³). Executed.
- **§5.3 — NEW OPEN ITEM (post-execution).** *Why does $V(|\alpha|)$ turn non-monotone at $\delta t/T_m = 0.80$?* Observed: $V$ = 0.998 → 0.760 → 0.101 → 0.377 for $|\alpha| \in \{0,1,3,5\}$, with the same impulsive-limit floor $V_\text{imp} \approx 0.865$ for all four. Hypotheses to discriminate: (i) a Jaynes–Cummings-like revival at large $\eta\sqrt{\langle n\rangle+1}$, (ii) Debye–Waller higher-order structure in the finite-$\delta t$ propagator, (iii) genuine physics of the motional-LD-breaching regime. Minimal probe: $|\alpha| \in \{3.25, 3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.25, 5.5\}$ at $\delta t/T_m = 0.80$, $N = 48$ — twenty-ish evolutions, ≲ 1 s compute. **Recommended as the first WP-C v0.2 task.**

### 5.1 Lamb–Dicke threshold specification (Architect-originated)

Architect asks: *What specific mathematical threshold should we encode into the engine to define "out of bounds" LD validity?*

**Guardian-stance flag (not resolution):** The answer is not single-parameter. At least two LD-related scales are in play:

- **Drive-strength LD:** $\Omega_\text{eff}/\omega_m \leq 0.3$ (three-stance endorsed in §4.1). Governs sideband-resolution validity of the effective Hamiltonian.
- **Motional-amplitude LD:** $\eta\sqrt{\langle n\rangle + 1} < 1$, where $\langle n\rangle \approx |\alpha|^2$ for a coherent state. At $\eta = 0.397$: $|\alpha|=1 \Rightarrow 0.56$ ✓;  $|\alpha|=3 \Rightarrow 1.26$ ✗;  $|\alpha|=5 \Rightarrow 2.03$ ✗.

The motional-LD parameter is already $\gtrsim 1$ at the WP-V baseline ($|\alpha|=3$). This does not *automatically* invalidate the engine — the engine retains the full Debye–Waller factor $e^{-\eta^2/2}$ in a non-truncated coupling $C = e^{i\eta(a+a^\dagger)}$, which survives beyond naive LD — but it means the $|\alpha|=5$ addition to §4.4 carries a separate LD-validity burden from the $\Omega$-ceiling.

**Guardian recommendation to the council:** Before scope-lock, a short lemma-style note (one to two paragraphs) in the forthcoming WP README specifying exactly (i) which LD expansion the engine uses, (ii) which order in $\eta$ is retained in `build_pulse_hamiltonian`, and (iii) which of (drive-strength LD / motional-amplitude LD / both) actually constrain the engine's validity. Without this, the $|\alpha|=5$ row and the small-$N$ / small-$\delta t$ corner of the grid carry *two different* validity concerns that may be conflated — a Clarity issue in its own right. The lemma must also specify whether the binding inequality takes the linear-amplitude form $\eta\sqrt{\langle n\rangle+1} \lesssim 1$ or the squared form $\eta^2(2\bar n+1) \lesssim 1$; these have different numerical thresholds and imply different $|\alpha|=5$ decisions.

**Provisional answer, pending that lemma:** Enforce both inequalities as **per-cell diagnostics**. Cells breaching either are hatched with a legend that distinguishes *drive-LD breach* from *motional-LD breach*. §6 carries the implementation commitment.

### 5.2 $|\alpha|=5$ inclusion — conditional on §5.1

If the §5.1 lemma establishes that the engine is valid only under motional-LD ≲ 1, $|\alpha|=5$ (and possibly $|\alpha|=3$) must be pruned or rendered under a prominent validity warning. If the lemma establishes that the engine remains valid for $\eta\sqrt{\langle n\rangle+1} \gtrsim 2$ provided the coupling $C$ is not truncated, $|\alpha|=5$ proceeds as scoped in §4.4.

-----

## 6. Deliverables shape (v0.1)

Conditional on §5.1 resolution and Integrator non-objection. Lean v0.1 comprises:

- **Endorsement Marker** as the first line of the WP README: *Local candidate framework (no parity implied with externally validated laws).*
- `wp-strong-weak-coastline/README.md` — council-cleared scope with §5.1 lemma inlined, hatching/LD-legend conventions declared, rubric table from §4.3 included, $\chi$-collapse conjecture from §3.4 declared as *testable hypothesis, not backbone*.
- `wp-strong-weak-coastline/numerics/run_coastline_v1.py` — driver over the 6×6 $(N, \delta t/T_m)$ grid × 3 $\delta$ × 4 $|\alpha|$ values (or 3 pending §5.2), at the §4.1 calibration, with:
  - Per-cell worst-case Fock-leakage audit at NMAX $\geq 60$, run first at the $|\alpha|\times\delta t/T_m$ extremes before the full grid sweep (§2.3).
  - Per-cell drive-LD and motional-LD diagnostics, stored as h5 dataset attributes.
- `wp-strong-weak-coastline/numerics/coastline_v1.h5` — $V$, $P$, diamond-amplitude, $|\delta\langle n\rangle|_\text{peak}$ per $(N, \delta t/T_m, |\alpha|, \delta)$ cell. **Data-ledger protocol:** constraint-selection rules declared as dataset attributes (`omega_eff_ceiling`, `ld_flag_drive`, `ld_flag_motional`, `fock_leakage_top5`), *not* bled into the observable fields themselves. Observables remain the raw engine output; hatching/exclusion logic is a downstream rendering concern that consumes the flags.
- **Primary heatmaps** — two maps ($V$, $P$) per $|\alpha|$, with drive-LD-ceiling breaches (§4.1) hatched in one convention. Optional diamond-amplitude panel where discriminatory; 1D cut along $\delta t/T_m = 0.13$ showing $N$-dependence; tertiary $V/P$ covariance panel (§4.3); analytic impulsive overlay on the $\delta t/T_m \to 0$ edge (§4.5).
- **Motional-LD diagnostic overlays** — per-cell motional-LD-breach indicator from §5.1, hatched in a *distinguishable* convention from the drive-LD hatching. Legend must make provenance unambiguous: drive-LD is §4.1's ceiling; motional-LD is §5.1's per-cell diagnostic pending the lemma.
- `wp-strong-weak-coastline/logbook/2026-04-XX-kickoff.md` + results entry tracking the §3.4 conjecture's fate.

Estimated compute: ≤ 30 s wall for $|\alpha|=3$ alone; ≤ 2 min for the full four-value set.

-----

## 7. Relation to existing WPs

- **WP-V (Hasse reproduction)** — fixes $(N, \delta t/T_m, \Omega, \alpha)$ at the Hasse values. Coastline WP samples the $(N, \delta t/T_m)$ plane around that point.
- **WP-E (Forward Map)** — fixes $(N, \delta t/T_m, \Omega)$, varies $(\delta_0, |\alpha|, \varphi_\alpha)$. Complementary axis set.
- **Rabi follow-up (2026-04-21 §6)** — fixes $(N, \delta t/T_m, \alpha)$, varies $\Omega$. Explicitly de-conflicted from the proposed WP by §4.1 option (a).

The coastline WP closes the $(N, \delta t/T_m)$ axis pair; other axes (envelope shape, $\omega_m$, $\eta$, Fock truncation) remain untouched. Within that scope it gives [ideal-limit-principles.md](ideal-limit-principles.md) a numerical phase diagram against which to anchor its Lamb–Dicke / impulsive / resolved-sideband discussion (Guardian-1 D5: prior overclaim — "closes the one remaining axis pair" — narrowed accordingly).

-----

## 8. Future work (parked, not in v0.1 scope)

- **Universal-collapse forward question (candidate WP-N).** Conditional on the §3.4 $\chi$-collapse conjecture surviving v0.1: generalise the coastline by including $\eta$- and $\omega_m$-variation, Wigner-function thermal seeds, and envelope-shape deformations to test whether the single-parameter collapse extends beyond the axes mapped here. Framing matches the `iontrap-dynamics` v0.3 exit-criterion discipline: freeze first (v0.1 WP), universalise later (WP-N).
- **Floquet-synchronisation reframing** (second-perspective §9). Promoted from organising frame to *Discussion* subsection of the v0.1 WP results document, flagged as interpretive. Pre-declared promotion criterion: observable structure in the $(V, P)$ maps that tracks $N$-phase rather than $N$-bandwidth. If v0.1 data satisfy that criterion, promote in v0.2 of the WP README; otherwise retain as commentary (Guardian-2 D10).

-----

## 9. Ask of the council (retargeted for WP-C v0.2)

v0.3 asks are closed: §5.1 resolved by co-lock (item 2, 4), §4.2 grid geometry and §4.4 |α| set confirmed by execution without objection (item 3), and the Integrator review of item 1 is effectively granted by the clean run and the intact locked decisions — but is formally noted here for the record. What remains for the council is a **v0.2 scope decision**:

1. **WP-C v0.2 — Doppler-merging probe.** Re-run the (N, δt/T_m) grid with $\delta$ scaled per cell to land inside the Doppler-broadened sideband, e.g. $\delta = \eta|\alpha|\,\omega_m$ for the P observable. This is the only way to exercise the (V low, P low) quadrant of the §4.3 rubric. Compute cost: one additional pass of the driver at ≈ 30 s per |α|. Not scope-creep — it is the gap-closing follow-up to the rubric that v0.1 under-discriminated.
2. **§5.3 — α-recovery probe.** Run the dense |α| scan at $\delta t/T_m = 0.80$, $N = 48$ specified in §5.3. ≲ 1 s compute. This decides between physics and engine artefact; if physics, the observed $V(|\alpha|)$ shape is itself a result worth naming.
3. **Memo disposition.** Two options:
   - **(A) Close this memo at v0.4** and start a new pre-WP memo for WP-C v0.2 covering items (1) and (2) as a coherent scope. Cleaner provenance, matches the memo-per-WP pattern established by `council-memo-2026-04-21-strong-weak-coastline.md` itself.
   - **(B) Iterate this memo to v0.5** with items (1) and (2) folded in. Preserves all prior deliberation in one file; risks bloat.
   Guardian recommendation: **(A)** — this memo has served its pre-WP function and is now a results-archival artefact. The v0.2 scope is narrow enough that it does not need the full pre-deliberation cycle of a new memo; a short "WP-C v0.2 plan" note would suffice.
4. **Integrator pronouncement.** Item 3 disposition, and whether items (1) and (2) should be sequenced (α-recovery first to resolve §5.3 before committing to the larger Doppler probe) or parallelised.

Items 1 and 2 are numerical follow-ups any stance can authorise; item 3 is the only council-level decision remaining.

-----

*v0.4 (2026-04-21, post-execution): header status rewritten to reflect that WP-C v0.1.1 is executed (commit `528267b`); §2.6 added summarising the six principal findings of the run ($N$-degeneracy, $\chi$-collapse falsified, Doppler-merging regime not reached, non-monotone $\alpha$, uniform impulsive floor, §5.1 lemma resolution, Floquet §8 promotion criterion unmet); §3 prefaced with a post-execution note pointing to §2.6; §4 preamble annotated with per-subsection execution outcomes; §5 prefixed with a §5.0 resolution-status block that closes §5.1 and §5.2 and opens §5.3 (α-recovery mechanism); §9 rewritten from pre-execution ask to forward-looking WP-C v0.2 ask with memo-disposition choice. v0.3 body preserved verbatim below §2.6 for provenance. v0.3 superseded.*

*v0.3 (2026-04-21): $\chi$-collapse ansatz corrected for pulse-bandwidth sign/monotonicity; §4.2 relabelled provisionally locked and augmented with 0.13 control-slice row; §4.4 scientific baseline demoted to $\{0,1,3\}$ with $|\alpha|=5$ contingent on §5.1; §2.2 softened; §2.5 split for readability; §4.3 rubric-defending sentence added; §5.1 motional-LD-form specification burden noted; §6 plots bullet split to distinguish drive-LD from motional-LD hatching; §9 re-opening threshold and lemma-timing ask added; compute estimate reconciled. v0.2 superseded.*

*v0.2 (2026-04-21): demoted §4 from questions to locked decisions; added §2.5 LD-audit, §3.4 $\chi$-collapse conjecture, §5 open questions, §8 future-work parking; integrated data-ledger protocol, hatched-overlay convention, drive-LD/motional-LD per-cell diagnostics, rubric table, analytic-impulsive overlay, and Endorsement Marker. v0.1 superseded.*
