#!/usr/bin/env python3
"""
append_pulse_train_extension.py — inject Steps 4–6 (pulse-train multi-channel
analysis) into multi_fock_interference.ipynb.

Idempotent: checks for the sentinel marker in existing cells and skips if
the extension is already present. Appends new cells at the end of the
notebook, preserving the original three Steps and the final "What to
compare" summary.
"""

import json
from pathlib import Path

NB_PATH = Path(__file__).resolve().parent / 'multi_fock_interference.ipynb'
SENTINEL = 'Step 4 — Pulse-train Fourier spectrum'


def md_cell(text):
    return {
        'cell_type': 'markdown',
        'metadata': {},
        'source': text.split('\n') if isinstance(text, str) else text,
    }


def code_cell(text):
    return {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': text.split('\n') if isinstance(text, str) else text,
    }


def newline_preserving(text):
    """Split a string on newlines but keep each trailing \\n for ipynb format."""
    lines = text.split('\n')
    return [l + '\n' for l in lines[:-1]] + ([lines[-1]] if lines[-1] else [])


NEW_CELLS = [
    md_cell(newline_preserving("""## Step 4 — Pulse-train Fourier spectrum

Steps 1–3 used the single-sideband matrix element $\\Omega_{n,n+1}(\\eta)$. But a *stroboscopic pulse train* at period $T_m = 2\\pi/\\omega_m$ is a multi-frequency drive: its Fourier series is

$$\\text{mod}(t) = d + \\sum_{k\\neq 0} F_k \\, e^{i k \\omega_m t}, \\qquad F_k = \\frac{\\sin(\\pi k d)}{\\pi k},$$

with $d = \\delta t / T_m$ the duty cycle. Each harmonic $k \\in \\mathbb{Z}$ is resonant with a different sideband: $k=0$ carrier, $k=\\pm 1$ first sideband, $k=\\pm 2$ second, etc. In the non-LD regime each sideband has its *own* Laguerre structure; the pulse train opens *all* these channels simultaneously with weights $F_k$."""
    )),
    code_cell(newline_preserving("""def pulse_train_fourier(k, d):
    \"\"\"Fourier coefficient F_k of a unit-amplitude stroboscopic square wave.

    mod(t) = d  +  Σ_{k ≠ 0}  F_k · exp(i k ω_m t),   F_k = sin(π k d)/(π k).
    \"\"\"
    k = np.asarray(k)
    return np.where(k == 0, d, np.sin(np.pi * k * d) / (np.pi * k + (k == 0)))

k_range = np.arange(-6, 7)
duty_cycles = [0.05, 0.13, 0.30, 0.50]   # fast-AOM, slow-AOM, wide, half

fig, ax = plt.subplots(figsize=(8, 4))
for d in duty_cycles:
    F = pulse_train_fourier(k_range, d)
    ax.stem(k_range + 0.08*duty_cycles.index(d), np.abs(F),
            basefmt=' ',
            label=fr'$d = {d:.2f}$', linefmt=f'C{duty_cycles.index(d)}-',
            markerfmt=f'C{duty_cycles.index(d)}o')
ax.set_xlabel(r'harmonic $k$   (resonant detuning $\\delta = k\\,\\omega_m$)')
ax.set_ylabel(r'$|F_k|$')
ax.set_title('Stroboscopic pulse-train Fourier amplitudes')
ax.set_xticks(k_range)
ax.axhline(0, color='k', lw=0.4)
ax.legend(ncol=4, fontsize=9, loc='upper right')
ax.grid(alpha=0.3)
plt.tight_layout(); plt.show()

print(f'fast-AOM duty (δt=40 ns, T_m=770 ns): d ≈ 0.052 → |F_1|/|F_0| ≈',
      f'{np.abs(pulse_train_fourier(1, 0.052))/0.052:.3f}')
print(f'slow-AOM duty (δt=100 ns):           d ≈ 0.130 → |F_1|/|F_0| ≈',
      f'{np.abs(pulse_train_fourier(1, 0.130))/0.130:.3f}')"""
    )),
    md_cell(newline_preserving("""**Reading the spectrum.** At d = 0.05 (fast AOM, ~40 ns pulses) the sideband harmonics $|F_{\\pm 1}|, |F_{\\pm 2}|$ are nearly equal and within a factor ~3 of the carrier coefficient $d$. So the pulse train is *far from* a clean carrier drive: the first few sidebands all receive comparable Fourier amplitude. At larger duty cycle $d = 0.5$ the spectrum collapses toward a pure carrier. The ion sees all these channels simultaneously."""
    )),
    md_cell(newline_preserving("""## Step 5 — Open channels per sideband: $A_k(\\eta)$

For each harmonic $k$, the Ramsey-contrast amplitude on that sideband for a coherent state $|\\alpha\\rangle$ is

$$A_k(\\eta) = \\sum_n c_n^* \\, c_{n+|k|} \\, \\Omega_{n, n+|k|}(\\eta),$$

with the generalised sideband matrix element (Wineland et al. 1998, Leibfried 2003):

$$\\Omega_{n, n+|k|}(\\eta) = \\Omega_0 \\, e^{-\\eta^2/2} \\, \\eta^{|k|} \\sqrt{\\frac{n!}{(n+|k|)!}} \\, L_n^{(|k|)}(\\eta^2).$$

For $k=0$ this reduces to the carrier matrix element; for $k=1$ it reproduces the rabi_bsb function of Step 1. The *sign* of $L_n^{(|k|)}$ is kept. Below we plot $A_k(\\eta)$ for $k \\in \\{-3, ..., +3\\}$ at fixed $\\alpha = 4$."""
    )),
    code_cell(newline_preserving("""def rabi_sideband(n, eta, k):
    \"\"\"Ω_{n, n+|k|}(η) / Ω_0, Laguerre-signed. k=0 → carrier; k≠0 → |k|-th sideband.\"\"\"
    n = np.asarray(n); eta = np.asarray(eta)
    k_abs = abs(int(k))
    L = eval_genlaguerre(n, k_abs, eta**2)
    if k_abs == 0:
        return np.exp(-eta**2 / 2) * L
    from scipy.special import gammaln
    log_ratio = 0.5 * (gammaln(n + 1) - gammaln(n + k_abs + 1))
    return np.exp(-eta**2 / 2 + log_ratio) * eta**k_abs * L


def channel_amplitude(alpha, eta, k, n_max=60):
    \"\"\"A_k(η) = Σ_n c_n^* c_{n+|k|} · Ω_{n, n+|k|}(η),   signed.\"\"\"
    c = coherent_amplitudes(alpha, n_max)
    eta = np.asarray(eta)
    k_abs = abs(int(k))
    if k_abs == 0:
        # Carrier: Σ_n |c_n|² · Ω_{n,n}(η)
        n_arr = np.arange(n_max + 1)
        scalar = (eta.ndim == 0)
        eta_b = eta.reshape(-1) if not scalar else eta[None]
        out = np.array([np.sum(np.abs(c)**2 * rabi_sideband(n_arr, e, 0)) for e in eta_b])
        return out.item() if scalar else out.reshape(eta.shape)
    # Sideband: coherent sum over shifted pair
    n_arr = np.arange(n_max + 1 - k_abs)
    scalar = (eta.ndim == 0)
    eta_b = eta.reshape(-1) if not scalar else eta[None]
    out = np.zeros(eta_b.shape, dtype=complex)
    for j, e in enumerate(eta_b):
        Om = rabi_sideband(n_arr, e, k_abs)
        out[j] = np.sum(np.conj(c[:n_max+1-k_abs]) * c[k_abs:n_max+1] * Om)
    if k < 0:
        out = np.conj(out)
    return out.item() if scalar else out.reshape(eta.shape)


alpha_fixed = 4.0
eta_scan = np.linspace(0.05, 3.0, 400)
k_list = [-3, -2, -1, 0, 1, 2, 3]

A_k = {k: channel_amplitude(alpha_fixed, eta_scan, k, n_max=60) for k in k_list}

fig, ax = plt.subplots(figsize=(10, 5))
colors = plt.cm.coolwarm(np.linspace(0, 1, len(k_list)))
for k, col in zip(k_list, colors):
    y = A_k[k].real if np.iscomplexobj(A_k[k]) else A_k[k]
    ax.plot(eta_scan, y, lw=1.5, color=col, label=fr'$k = {k:+d}$')
ax.axhline(0, color='k', lw=0.4)
ax.set_xlabel(r'$\\eta$')
ax.set_ylabel(r'$\\mathrm{Re}\\,A_k(\\eta) / \\Omega_0$')
ax.set_title(rf'Open channel amplitudes per sideband ($\\alpha = {alpha_fixed}$)')
ax.legend(ncol=7, fontsize=9)
ax.grid(alpha=0.3)
plt.tight_layout(); plt.show()

print('Sign-change counts (nodes of each channel over η ∈ [0.05, 3.0]):')
for k in k_list:
    y = A_k[k].real if np.iscomplexobj(A_k[k]) else A_k[k]
    nodes = int(np.sum(np.diff(np.sign(y)) != 0))
    print(f'  k = {k:+d}:  {nodes} sign changes')"""
    )),
    md_cell(newline_preserving("""**Reading Step 5.** $k = 0$ and $k = \\pm 1$ each have their own Laguerre-sign structure — the $k=+1$ curve reproduces the notebook's original $A(\\eta)$ from Step 3 (the single-channel envelope). $k = \\pm 2, \\pm 3$ are suppressed by $\\eta^2, \\eta^3$ at small $\\eta$ but catch up in the non-LD regime ($\\eta \\gtrsim 1$), and their node positions are *different* from the $k=1$ nodes. A physical measurement probes the Fourier-amplitude-weighted sum of all these — which is what Step 6 computes."""
    )),
    md_cell(newline_preserving("""## Step 6 — Weighted multi-channel total

The full stroboscopic pulse train couples to the spin through *every* open channel with weight $F_k$ from Step 4. To leading order in pulse area, the multi-channel Ramsey envelope is

$$A_\\text{train}(\\eta) = \\sum_{k} F_k(d) \\, A_k(\\eta),$$

with signs kept throughout. Below we overlay $A_\\text{train}(\\eta)$ against Step 3's single-channel $A(\\eta) = A_{k=+1}(\\eta)$. The difference exposes the contribution of the carrier and higher sidebands that the single-sideband picture misses."""
    )),
    code_cell(newline_preserving("""# compute A_train(η) at three representative duty cycles
duty_picks = [0.05, 0.13, 0.30]
k_range_full = np.arange(-4, 5)   # carrier ± 4 sidebands — enough for η ≤ 3 at α=4

# reuse A_k computed above for k in [-3, 3]; compute ±4 on the fly
A_k_full = dict(A_k)
for k in (-4, 4):
    A_k_full[k] = channel_amplitude(alpha_fixed, eta_scan, k, n_max=60)

fig, axs = plt.subplots(2, 1, figsize=(10, 7), sharex=True, constrained_layout=True)

ax = axs[0]
# Step-3 single-channel reference
A_single = A_k_full[+1].real
ax.plot(eta_scan, A_single, color='black', lw=1.8, ls='--',
        label=r'Step 3 single channel: $A_{+1}(\\eta)$')
# Multi-channel at three duty cycles
for d in duty_picks:
    A_train = np.zeros_like(eta_scan)
    for k in k_range_full:
        F = pulse_train_fourier(k, d)
        y = A_k_full[k].real if np.iscomplexobj(A_k_full[k]) else A_k_full[k]
        A_train += F * y
    ax.plot(eta_scan, A_train, lw=1.5, label=fr'multi-channel, $d = {d}$')
ax.axhline(0, color='k', lw=0.4)
ax.set_ylabel(r'amplitude / $\\Omega_0$')
ax.set_title(rf'Multi-channel Ramsey envelope $A_\\mathrm{{train}}(\\eta)$ vs single channel ($\\alpha = {alpha_fixed}$)')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Bottom panel: residual (multi - single) at the fast-AOM duty
d_fast = 0.05
A_train_fast = np.zeros_like(eta_scan)
for k in k_range_full:
    F = pulse_train_fourier(k, d_fast)
    y = A_k_full[k].real if np.iscomplexobj(A_k_full[k]) else A_k_full[k]
    A_train_fast += F * y
residual = A_train_fast - A_single
ax = axs[1]
ax.plot(eta_scan, residual, color='#c0392b', lw=1.5,
        label=fr'residual at $d = {d_fast}$')
ax.axhline(0, color='k', lw=0.4)
# Mark original Step-3 nodes
from numpy import diff, sign
step3_nodes = eta_scan[np.where(diff(sign(A_single)))[0]]
for e in step3_nodes:
    ax.axvline(e, color='grey', lw=0.4, ls=':', alpha=0.7)
ax.set_xlabel(r'$\\eta$')
ax.set_ylabel(r'$A_\\mathrm{train} - A_{+1}$')
ax.set_title('Residual — extra structure added by carrier + higher sidebands')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
plt.show()

# Node positions at d = 0.05
train_nodes = eta_scan[np.where(diff(sign(A_train_fast)))[0]]
print(f'Step-3 single-channel nodes:    {[f\"{e:.3f}\" for e in step3_nodes]}')
print(f'Multi-channel nodes (d=0.05):   {[f\"{e:.3f}\" for e in train_nodes]}')"""
    )),
    md_cell(newline_preserving("""## What this extension adds

1. **Step 4** makes explicit that a stroboscopic pulse train is a multi-tone drive: with 5% duty cycle (fast-AOM regime) the $k = \\pm 1, \\pm 2$ Fourier coefficients are all within a factor ~3 of the carrier. So single-sideband analysis is already a strong assumption even for a "BSB π/2" pulse.

2. **Step 5** extends the Laguerre/Glauber machinery of Steps 1–3 to *every* open channel. Each channel has its own sign structure, its own node locations, and its own small-η scaling ($\\propto \\eta^{|k|}$).

3. **Step 6** predicts the *actual* measurable envelope: a $F_k$-weighted coherent sum over channels. Node positions shift relative to the single-channel prediction, and the residual (bottom panel of Step 6) is exactly the signature of "other channels are active too". A falsification test: if Freddy's contrast nodes line up with Step-3 nodes → single-channel picture survives; if they line up with Step-6 multi-channel nodes → evidence for coherent multi-channel physics.

**Connection to the engine (WP-V Round 2+):** our `stroboscopic_sweep.py` engine's full unitary $\\exp(-i H \\delta t)$ with $H = \\omega_m a^\\dagger a + (\\Omega/2)(C \\sigma_- + C^\\dagger \\sigma_+)$ automatically includes every $A_k$. A direct cross-check against this notebook at selected $(\\alpha, \\eta, d)$ verifies the engine's multi-sideband content against the Laguerre closed form."""
    )),
]


def main():
    nb = json.loads(NB_PATH.read_text())

    # Idempotency check
    existing = ''.join(''.join(c.get('source', [])) for c in nb['cells'])
    if SENTINEL in existing:
        print(f'  sentinel found — extension already present; skipping.')
        return

    nb['cells'].extend(NEW_CELLS)

    # Write back preserving JSON formatting
    NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    print(f'  appended {len(NEW_CELLS)} cells to {NB_PATH.name}')
    print(f'  new total: {len(nb["cells"])} cells')


if __name__ == '__main__':
    main()
