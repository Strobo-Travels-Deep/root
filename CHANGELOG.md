# Changelog — Breakwater Dossier

## v0.8 (2026-03-19) — Guardian Audit II Fixes

### Provenance & documentation

- **P1: `export_hdf5.py` — `n_pulses` corrected (recurrence fix)**
  - `n_pulses=326` → `n_pulses=22` in DEFAULTS dict
  - `export_version` bumped `'0.4'` → `'0.8'`
  - This was flagged as fixed in v0.7 (M3) but the fix had not been applied to the file

- **P2: Tutorial contrast provenance caveat added**
  - σ_z contrast values 0.61→0.71→0.84→0.75 now explicitly attributed to HDF5 adaptive-learner data
  - 22-pulse stroboscopic JSON runs (uniform ≈ 0.56) identified as separate dataset
  - WP-B deliverable updated to require cross-method reconciliation
  - Practical Starting Points §2 rewritten for dual-target formulation

- **P3: Sail essay (ideal-limit-principles.md) §1.4 contrast provenance + §2 species**
  - Added provenance note distinguishing HDF5 and JSON contrast sources
  - Removed bare claim that contrast encodes velocity-distribution shape without method context
  - Corrected ion species in §2 Monroe comparison table: Ba⁺ → ²⁵Mg⁺

- **P4: Version labelling unified**
  - Changelog renamed from `CHANGELOG-v07.md` to `CHANGELOG.md`
  - All footers read "Dossier v0.8"
  - `code_version` in all run manifests: `0.8.0`
  - README header: "Dossier v0.8"

- **P5: `numerics.html` settings panel corrected**
  - N_max: `40` → `50` (matching actual default run data)
  - Leakage note for α=5 corrected: "0.005% at N_max=50" (not "1.1% at N_max=40")

- **P6: Legacy `data/manifest.json` labelled**
  - Added `"_legacy_note"` field explaining HDF5 provenance
  - Points readers to `data/runs/manifest.json` for current JSON data

- **P7: Python download script labelled as parameter-export stub**
  - Download button label changed from "↓ Python" to "↓ Python (params)"
  - Script header clarified: "Parameter export only — see code.html for full QuTiP implementation"

- **P8: `index.html` version tag clarified**
  - Removed ambiguous `v0.4` tag from meta-block
  - Replaced with `v0.8` consistent with footer

### Simulation engine

- No changes to physics engine, Hamiltonian, coupling, or observables
- `CODE_VERSION` remains `'0.8.0'` (set in prior update)

### Run data

- All default JSON runs regenerated at v0.8.0 with N_max=50
- No changes to run data files

---

## v0.7 — Council-3 Guardian Audit Fixes

### High Severity (Fixed)

#### H1: numerics.html — Pulse count corrected
- **Before:** "Pulses in train: 326" 
- **After:** "Stroboscopic pulses: 22" with "Pulses per motional cycle: 1"
- Settings panel restructured to distinguish physical parameters from simulation method
- Added cross-validation caveat note

#### H2: manifest.json — Contrast values corrected
- **Before:** contrast_z = 0.29, 0.35, 0.41, 0.37 (stale, from unknown source)
- **After:** contrast_z = 0.56 for all α (computed from JSON run data)
- Added note field explaining HDF5 vs JSON provenance distinction

#### H3: README.md — Cross-validation caveat added
- **Before:** "Default runs use the same physics parameters as the HDF5 data for cross-validation."
- **After:** Explicit caveat explaining HDF5 (adaptive-learner) vs JSON (22-pulse stroboscopic) difference
- v0.7 changelog section added

#### H4: Tutorial contrast values — Deferred → Resolved in v0.8 (P2)
- The tutorial.html and Sail essay reference σ_z contrast values 0.61→0.71→0.84→0.75
- These derive from the HDF5 adaptive-learner data, not the 22-pulse JSON runs
- **v0.8 resolution:** Provenance caveat added to both tutorial and Sail essay

### Medium Severity (Fixed)

#### M1: simulate.html — Decoherence collapse probability saturation
- Added `decoSaturationCount` tracking
- `collapseStep()` now checks `dp1+dp2+dp3 < 1`; if exceeded, rescales to 0.95 total
- Status bar reports saturation count after run
- Downloaded manifest includes `deco_saturations` field

#### M2: simulate.html — Fock convergence across all trajectories
- **Before:** `fockLeak()` called only on last trajectory (`t === ntraj - 1`)
- **After:** Checked on every trajectory; `maxLk` updated throughout
- Convergence banner now reflects worst-case across all trajectories

#### M3: export_hdf5.py — n_pulses default corrected
- **Before:** `n_pulses=326`
- **After:** `n_pulses=22`
- `export_version` bumped to `'0.7'`
- **Note:** This fix was not applied in v0.7; corrected in v0.8 (P1)

#### M4: numerics.html — Parameter panel clarified
- Separated "Physical parameters" from "Stroboscopic protocol"
- Added explanatory note about simulation method (interaction picture, identity free evolution)
- Removed ambiguous "Duty cycle" and "Modulation" rows

### Code version bumped
- `CODE_VERSION` in simulate.html: `'0.6.0'` → `'0.7.0'` → `'0.8.0'`
- Footer version: v0.6 → v0.7 → v0.8 across all pages

### Physics engine: No changes needed
- Hamiltonian construction: correct ✓
- Coupling operator: correct ✓
- Stroboscopic evolution: correct ✓
- Observable computation: correct ✓
- Unit convention: internally consistent ✓
- σ_z(δ=0) α-independence: physically correct ✓

### v0.8.1 — 2026-03-23 (audit response)

**Fixes (all 6 audit findings):**

1. **[H] sweep_1d integer typing** — Added `_INT_PARAMS` set and `_enforce_types()`
   in `stroboscopic_sweep.py`. Integer-valued sweep parameters (`n_pulses`, `nmax`,
   `npts`, `n_traj`, `n_rep`, `fock_n`) are now cast from float to int before dispatch.
   CLI `--sweep-values 5,10,22,50` now works for all integer parameters.

2. **[H] state_comparison schema compliance** — Removed `fock_n: None` from all
   STATE_GALLERY entries that don't use Fock initial states. Added None-stripping
   to state definitions in the payload. Output now validates against
   `schemas/manifest_v2.schema.json`.

3. **[H] Browser simulator status** — All pages now clearly state that the browser
   engine (`simulate.html` + `js/simulate-engine.js`) is not included in this
   packaged snapshot. Updated: README.md, index.html, getting-started.html,
   code.html. REBUILD.md provides patching instructions for the original files.

4. **[M] N_max provenance** — Corrected all claims of N_max = 50 to the actual
   values used in the default runs: N_max = 30 (α = 0, 1, 3) and N_max = 40
   (α = 5). Updated: numerics.html, reference.html, getting-started.html.

5. **[M] Run index naming** — Renamed `data/runs/manifest.json` →
   `data/runs/run_index.json` to avoid confusion with the v2 manifest schema.
   Updated: `js/numerics-viewer.js`, `README.md`.

6. **[L] Legacy HDF5 quarantine** — Rewrote `data/manifest.json` with explicit
   `_status: "ARCHIVAL — NON-SHIPPING"` header and note that .h5 files are not
   included and not required for any current functionality.
