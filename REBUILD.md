# Rebuild Instructions

These files need to be sourced from the v0.7 repository and patched:

## simulate.html

Source: Original repository `simulate.html` (v0.7/v0.8)

Patches to apply:

1. **Nav bar** — replace the existing `<nav>` block with:
```html
  <nav>
    <a href="index.html">Overview</a> <a href="dossier.html">Dossier</a>
    <a href="framework.html">Framework</a> <a href="tutorial.html">Tutorial</a>
    <a href="numerics.html">Numerics</a>
    <a href="simulate.html" aria-current="page">Simulate</a>
    <a href="code.html">Code</a>
    <a href="reference.html">Reference</a>
    <a href="getting-started.html">Start</a>
  </nav>
```

2. **Python download button** — find:
```html
    <button class="db" id="dl-py">↓ Python</button>
```
   Replace with:
```html
    <button class="db" id="dl-py">↓ Python (params)</button>
```

## js/simulate-engine.js

Source: Original repository `js/simulate-engine.js` (v0.7/v0.8)

Patches to apply:

1. **Python download docstring** — in the `dl-py` click handler, find:
```javascript
"""Stroboscopic Detuning Scan — PRA 109, 053105 (2024)
Repo: ${REPO}  v${VER}  Browser hash: ${lastHash}
pip install qutip numpy"""
```
   Replace with:
```javascript
"""Stroboscopic Detuning Scan — Parameter Export Only
PRA 109, 053105 (2024)
Repo: ${REPO}  v${VER}  Browser hash: ${lastHash}

NOTE: This file exports parameters only. For the full Python implementation,
see scripts/stroboscopic_sweep.py. pip install numpy scipy"""
```

## scripts/plot_detuning_harbour.py

Source: Original repository `scripts/plot_detuning_harbour.py`
No patches needed — copy as-is.

## Quick patch script

```bash
# From the v0.7 repo root:
# 1. Copy simulate.html and apply patches
sed -i 's|<a href="code.html">Code</a>|<a href="code.html">Code</a>\n    <a href="reference.html">Reference</a>\n    <a href="getting-started.html">Start</a>|' simulate.html
sed -i 's|↓ Python</button>|↓ Python (params)</button>|' simulate.html

# 2. Copy simulate-engine.js and apply patch
sed -i 's|Stroboscopic Detuning Scan — PRA|Stroboscopic Detuning Scan — Parameter Export Only\nPRA|' js/simulate-engine.js

# 3. Copy plot script
cp scripts/plot_detuning_harbour.py scripts/
```
