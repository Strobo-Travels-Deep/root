# v0.7 Changelog — Council-3 Guardian Audit Fixes

## High Severity (Fixed)

### H1: numerics.html — Pulse count corrected
- **Before:** "Pulses in train: 326" 
- **After:** "Stroboscopic pulses: 22" with "Pulses per motional cycle: 1"
- Settings panel restructured to distinguish physical parameters from simulation method
- Added cross-validation caveat note

### H2: manifest.json — Contrast values corrected
- **Before:** contrast_z = 0.29, 0.35, 0.41, 0.37 (stale, from unknown source)
- **After:** contrast_z = 0.56 for all α (computed from JSON run data)
- Added note field explaining HDF5 vs JSON provenance distinction

### H3: README.md — Cross-validation caveat added
- **Before:** "Default runs use the same physics parameters as the HDF5 data for cross-validation."
- **After:** Explicit caveat explaining HDF5 (adaptive-learner) vs JSON (22-pulse stroboscopic) difference
- v0.7 changelog section added

### H4: Tutorial contrast values — Deferred
- The tutorial.html and Sail essay reference σ_z contrast values 0.61→0.71→0.84→0.75
- These derive from the HDF5 adaptive-learner data, not the 22-pulse JSON runs
- Full tutorial rewrite deferred; noted in README cross-validation section

## Medium Severity (Fixed)

### M1: simulate.html — Decoherence collapse probability saturation
- Added `decoSaturationCount` tracking
- `collapseStep()` now checks `dp1+dp2+dp3 < 1`; if exceeded, rescales to 0.95 total
- Status bar reports saturation count after run
- Downloaded manifest includes `deco_saturations` field

### M2: simulate.html — Fock convergence across all trajectories
- **Before:** `fockLeak()` called only on last trajectory (`t === ntraj - 1`)
- **After:** Checked on every trajectory; `maxLk` updated throughout
- Convergence banner now reflects worst-case across all trajectories

### M3: export_hdf5.py — n_pulses default corrected
- **Before:** `n_pulses=326`
- **After:** `n_pulses=22`
- `export_version` bumped to `'0.7'`

### M4: numerics.html — Parameter panel clarified
- Separated "Physical parameters" from "Stroboscopic protocol"
- Added explanatory note about simulation method (interaction picture, identity free evolution)
- Removed ambiguous "Duty cycle" and "Modulation" rows

## Code version bumped
- `CODE_VERSION` in simulate.html: `'0.6.0'` → `'0.7.0'`
- Footer version: v0.6 → v0.7 across simulate.html, numerics.html

## Physics engine: No changes needed
- Hamiltonian construction: correct ✓
- Coupling operator: correct ✓
- Stroboscopic evolution: correct ✓
- Observable computation: correct ✓
- Unit convention: internally consistent ✓
- σ_z(δ=0) α-independence: physically correct ✓
