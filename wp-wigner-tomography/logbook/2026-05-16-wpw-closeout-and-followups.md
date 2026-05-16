# Logbook — 2026-05-16 — WP-W close-out + follow-up options

**Status.** Decision / milestone entry (not a run entry). WP-W's
entire §4 deliverable surface plus both preflight gates are executed,
documented, and pushed to `origin/main`. This entry summarises the
findings across the five execution sessions, records the clean-stop
state, and ranks the optional follow-up scope so a future session can
reopen without re-deriving the landscape.

**One-line outcome.** WP-W is *complete and parked*: P0 + D1–D5 + P1
+ D4 all closed; the only open work is optional follow-up scope, not
execution blockers.

-----

## 1. Execution arc — what was done, in order

Five same-/next-day sessions (2026-05-15 → 2026-05-16), one clean
commit each, engine code touched only to add the `ideal_sdf`
primitive.

| # | session | commit | logbook |
|---|---|---|---|
| 1 | D2 reach ladder + P0 gate | `4e34ef8` | [`2026-05-15-D2-and-P0.md`](./2026-05-15-D2-and-P0.md) |
| 2 | D3 reconstruction demo (7 states) | `1b63cd0` | [`2026-05-15-D3-reconstruction.md`](./2026-05-15-D3-reconstruction.md) |
| 3 | `ideal_sdf` primitive + P1 sentinel | `9d5360a` | [`2026-05-15-ideal-sdf-primitive.md`](./2026-05-15-ideal-sdf-primitive.md) |
| 4 | D4 bridge (Layer A + Layer B) | `71027b6` | [`2026-05-15-D4-bridge.md`](./2026-05-15-D4-bridge.md) |
| 5a | v0.5 doc correction pass (doc-only) | `fe8f8b0` | — (§8 v0.5 in WORK-PROGRAM) |
| 5b | D1 standalone analytic note | `64a2e10` | — ([`notes/analytic_chain.md`](../notes/analytic_chain.md)) |

## 2. Findings by deliverable

### P0 — analytic-grid self-consistency (PASS)

Vacuum $W(0)=0.636555$ vs analytic $2/\pi=0.636620$
($\Delta=-6.5\times10^{-5}$, finite-grid windowing — the Gaussian
$\chi_\text{vac}$ has support just outside $|\beta|=B=4$). Coherent
$|\alpha=1\rangle$ peak landed **exactly** on the predicted closest
grid node, value correct to 1 part in $10^4$;
$\max|\operatorname{Im}W|\sim10^{-16}$. Confirms the FFT
sign/centring and the $\Delta\alpha=\pi/(N_g\Delta\beta)$ relation.
*Surprise (caught at plot stage):* `wigner_from_chi` initially output
transposed axes; fixed, and array↔physical axis tagging now in the
`_common.py` docstring.

### D2 — forward-map reach ladder

`n_in_disk` $=\{317,1257,2821,5025\}$ for $N=\{20,40,60,80\}$,
matching the continuous estimate $\pi B_N^2/\Delta\beta^2$ within
rounding; the $N=80$ count **5025 exactly matches** the value
independently quoted in WORK-PROGRAM §2 — validates the
inverse-Dirichlet implementation against the §2 grid analysis.

### D3 — reconstruction demo (PASS)

All six gated states clear their §7#5 thresholds; the deciding
states (Fock $|2\rangle$, cat $|\alpha|=1.5$) pass, so the inversion
pipeline is validated at the v0.2 Cartesian resolution. The mixed-cat
control reconstructs as a classical two-hump mixture with **no
invented fringes** — the quantum-vs-classical discriminator behaves.
*Two corrections logged:* (i) radial Hanning dropped for analytic χ
(it over-attenuated, dropping vacuum $\mathcal F$ to ~0.86 — Hanning
belongs to measured/truncated data, not exact analytic χ); (ii) the
cat off-diagonal `cosh` argument must be $\operatorname{Re}(\alpha^*\beta)$,
not $\alpha^*\beta$, or χ loses Hermiticity ($\max|\operatorname{Im}W|\sim0.2$
on the cat — a real bug, fixed). *Open observation:* the one-sided
$\rho_\text{neg}\ge0.5$ criterion is too permissive given the cat
negativity overshoot; WP-W should later report both one-sided
preservation and symmetric deviation (noted, not yet actioned —
not a blocker).

### `ideal_sdf` primitive + P1 (PASS at 1e-14)

FH20-style σ_x SDF $U=D(\sigma_x\beta/2)$ added to
`scripts/stroboscopic`; 28 smoke tests pass at $\le10^{-9}$ (four
convention locks: branch separation, branch sign, direct
$\chi=\langle\sigma_y\rangle-i\langle\sigma_z\rangle$ readout, σ_x
carries no χ). P1 sentinel ($\beta_\star=0.5\,e^{i\pi/4}$, vacuum +
coherent $|\alpha=1\rangle$, $N\in\{20,80\}$) passes at
$\sim1\times10^{-14}$ relative residual — the 5 % gate cleared by 13
orders. *Key finding:* the ideal SDF is σ_x, **not** σ_z — σ_z
conditioning does not rotate under the σ_z spin precession that
generates the Dirichlet kernel and gave a **165 %** residual; σ_x
gave $10^{-14}$. Detuning must be encoded as explicit per-pulse SDF
phase, not free σ_z precession in the gap.

### D4 — bridge (Layer A machine-precision; Layer B substantive)

**Layer A** (native engine vs WP-E `scan_2d_alpha3_v2.h5`): max
$|\Delta|=\mathbf{0.00\times10^{0}}$ (bit-exact) on
$(\sigma_z,\operatorname{Re}C,\operatorname{Im}C)$ at the three WP-E
nearest-grid δ/ω_m points. *Surprise → fix:* first attempt gave
≈1.3 residuals; the native engine takes **no separate MW π/2** (the
train accumulates π/2 via the $\Omega_r$ calibration) and needs the
WP-E v0.9.1 motional-phase shift $\texttt{shift\_deg}=\omega_m\delta t/2$.
WP-E uses $N=30$, not the Hasse-paper $N=22$.
**Layer B** (engine-measured χ vs analytic χ over the $81^2$ fine
grid at $|\alpha=3\rangle$): max
$|\chi_\text{engine}-\chi_\text{analytic}|=\mathbf{3.75\times10^{-4}}$
over 6481 nodes — the canonical bridge metric. The FFT centroid
$2.980+0i$ ($1.99\times10^{-2}$) is **sub-pixel** at
$\Delta\alpha=0.39$ and is *not* an engine defect; the pre-set
$10^{-2}$ centroid gate was tighter than grid resolution and was the
wrong metric. The coarse pass ($N=20$) is a saturated-regime
diagnostic that fails by construction (outer β-nodes leave the
inverse-Dirichlet central monotone branch) — future stability checks
should vary β-grid resolution at fixed $N$, not $N$.

### v0.5 doc correction pass (doc-only) + D1

Five conventions surfaced by execution were corrected in
WORK-PROGRAM (σ_z→σ_x; removed spurious $e^{-|\beta|^2/2}$ prefactor;
$N=22\to30$; documented `shift_deg`; removed stale MW π/2 step), and
§5 layout / §4 D4 reconciled to executed artefact names. D1
([`notes/analytic_chain.md`](../notes/analytic_chain.md)) is a
standalone, convention-locked derivation tied to the four executed
residual anchors — a reader can reconstruct every runner without
chasing the WP text.

## 3. Provenance anchors (the load-bearing numbers)

| gate | metric | result |
|---|---|---|
| P0 | vacuum $W(0)$ vs $2/\pi$ | $0.636555$ vs $0.636620$ ($\Delta=-6.5\times10^{-5}$) |
| P1 | engine χ vs analytic χ, sentinel | $\sim1\times10^{-14}$ |
| D4 Layer A | native vs WP-E, 3 nearest-grid pts | $0.00\times10^{0}$ (bit-exact) |
| D4 Layer B | engine χ vs analytic χ, 6481-node grid | $3.75\times10^{-4}$ |

D4 Layer B is the load-bearing bridge number. The Layer B FFT
centroid is reported only with its $\Delta\alpha$ pixel size
attached, never as a bare gate.

## 4. Clean-stop assessment

- All §4 deliverables (D1–D5) and both preflight gates (P0, P1)
  closed; D4 bridge done.
- Doc matches executed artefacts after the v0.5 pass; no known
  doc/code drift.
- No execution blockers remain. The items still noted as "open"
  (D3 negativity-criterion refinement; pulse-duration $\delta t/T_m$
  order in WP §Analytical bullet 5 [TBD]) are *polish*, not blockers,
  and are explicitly non-gating.
- WP-W is parked. Reopen only on a specific follow-up decision.

## 5. Follow-up options (ranked)

Optional scope only — none is an execution blocker. Recommended
ranking, with the reasoning and a concrete first step for each.

### Rank 1 — Motional back-action diagnostic *(highest value)*

**Why first.** Highest conceptual value and it **reuses existing
engine outputs** — the same forward propagator that drives the χ
readout also produces $\rho_m^{(\mathrm{post})}$, so no new physics
machinery is required. It is a third bridge residual orthogonal to
the §7#7 spin-side anchor (the "cost of measurement" per bit of
phase-space information), and it forward-looks to weak-measurement /
sequential-tomography variants. [Hasse24] App. D / Fig. 6b already
maps $\delta\langle n\rangle$ qualitatively — WP-W's contribution is
the *quantitative* ideal-SDF-vs-native Wigner-resolved difference.

**First step.** Decide the three open parameters before coding
(WORK-PROGRAM §8 v0.5 back-action open items):
(i) readout basis — under the corrected σ_x SDF the branch-selecting
axis is σ_x and the cat-/χ-producing readout is σ_y/σ_z;
(ii) input-state subset — start with the §7#4 headline three or the
aggressive cat + Fock $|2\rangle$ stress only;
(iii) back-action metric — purity drop, fidelity to the pre-train
state, Wigner-negativity gain, or branch distance $|\beta_\text{tot}|$.
Provisional deliverable: side-by-side $W(\rho_m^{(\mathrm{post})})$
panels (engine vs ideal-SDF) computed *directly from the simulated
density matrix* via the parity form
$W=\pi^{-1}\operatorname{Tr}[\rho\,D(\alpha)\Pi D^\dagger(\alpha)]$,
sidestepping the v0.4 grid-resolution limits but raising a
partial-trace / mixed-state Wigner-cost implementation question.

### Rank 2 — Squeezed-vacuum reconstruction

**Why second.** Natural FH20/Hasse extension ([Hasse24] App. E gives
the framework with the timing change $\Delta t=2\pi/(2\omega_m)$;
[FH20] demonstrated it at $\eta=0.05$), but it is **gated on an
analytic pass**: the squeezed χ carries phase-dependent quadratic
structure not captured by the first-order LD chain that anchors
§7#3. Requires extending the analytic chain to $\mathcal O(\eta^2)$
and re-auditing the ideal-SDF bridge before any runner work — more
upfront derivation than Rank 1.

**First step.** $\mathcal O(\eta^2)$ extension of the analytic chain
(the squeezing term enters at second order in $\eta$), then re-audit
the σ_x-SDF bridge at that order; test state ideal squeezed vacuum at
$r\sim0.5$. Update D1 §6 (approximation hierarchy) accordingly.

### Rank 3 — GKP-lattice probe *(defer)*

**Why deferred.** [FH20] Fig. 4 already demonstrates approximate-GKP
at $\eta=0.05$, so this is a *grid-resolution* deferral, not a
capability one. GKP sub-features sit well below the v0.2
$\Delta\alpha=0.39$; a faithful reconstruction needs $\Delta\alpha$
down ~10×, cascading to $\Delta\beta$ ÷10, $N$ ×10, and the
perturbativity audit revisited at the larger $|\alpha|$ GKP support
demands. Defer until there is appetite for the finer-grid compute and
a separate "WP-W-GKP" scope.

**First step (when reopened).** Scope as its own WP; not a WP-W
extension.

-----

## 6. Next-step decision

**Park WP-W.** No further action without a specific follow-up
decision from the user. If reopened, take Rank 1 (back-action
diagnostic) first — it has the best value-to-effort ratio because it
reuses the existing engine propagator and needs only the three
parameter decisions above, no new analytic pass. Rank 2 needs the
$\mathcal O(\eta^2)$ analytic extension first; Rank 3 is a separate
future WP.
