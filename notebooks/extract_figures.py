#!/usr/bin/env python3
"""
extract_figures.py — pull PNG outputs from the executed notebook.

Reads multi_fock_interference.executed.ipynb, finds every cell with an
image/png output, and saves each as a numbered PNG under outputs/.
"""

import base64
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EXEC_NB = SCRIPT_DIR / 'multi_fock_interference.executed.ipynb'
OUT_DIR = SCRIPT_DIR / 'outputs'
OUT_DIR.mkdir(exist_ok=True)

LABELS = {
    # Map (figure index across all code cells in order) → short name for file
    1: 'step1_omega_heatmap',
    2: 'step2_glauber_overlay',
    3: 'step3_incoherent_carpet',
    4: 'step3_coherent_envelope',
    5: 'step4_pulse_train_spectrum',
    6: 'step5_open_channels',
    7: 'step6_multi_channel_total',
}


def main():
    nb = json.loads(EXEC_NB.read_text())
    code_idx = 0
    figure_idx = 0
    for c in nb['cells']:
        if c.get('cell_type') != 'code':
            continue
        code_idx += 1
        for out in c.get('outputs', []):
            data = out.get('data', {})
            if 'image/png' in data:
                figure_idx += 1
                label = LABELS.get(figure_idx, f'figure_{figure_idx}')
                fname = OUT_DIR / f'{label}.png'
                fname.write_bytes(base64.b64decode(data['image/png']))
                print(f'  wrote {fname.relative_to(SCRIPT_DIR.parent)}  '
                      f'(code cell #{code_idx}, figure #{figure_idx})')
    if figure_idx == 0:
        print('  no image/png outputs found — did the notebook execute cleanly?')


if __name__ == '__main__':
    main()
