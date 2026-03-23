"""
Detuning-spectrum plotter — Harbour palette (pastel-red)
Produces SVG figures for the Breakwater dossier.

Usage:
    plot_detuning_spectrum(learner, dis_amp, m_freq, aomsel,
                           savepath="R_{}_alpha.svg".format(dis_amp))
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

COLOURS = dict(
    bg_figure="#f2dcd6", bg_axes="#faf3f0", grid="#d4a99e",
    text="#3a2520", text_sec="#6b4a40", text_muted="#8c6e63",
    accent="#a0453a", border="#d4a99e",
    sigma_x="#a0453a", sigma_y="#3a5a8a", sigma_z="#c08a20",
    coherence="#3a2520", entropy="#3a2520",
)

def _apply_rcparams():
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Source Serif 4", "Georgia", "DejaVu Serif"],
        "mathtext.fontset": "cm", "font.size": 11,
        "figure.facecolor": COLOURS["bg_figure"],
        "axes.facecolor": COLOURS["bg_axes"],
        "axes.edgecolor": COLOURS["border"],
        "axes.labelcolor": COLOURS["text"],
        "text.color": COLOURS["text"],
        "xtick.color": COLOURS["text_muted"],
        "ytick.color": COLOURS["text_muted"],
        "grid.color": COLOURS["grid"], "grid.alpha": 0.35,
        "legend.framealpha": 0.85,
        "legend.edgecolor": COLOURS["border"],
        "legend.facecolor": COLOURS["bg_axes"],
        "axes.linewidth": 0.7, "figure.dpi": 150,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.12,
    })

_apply_rcparams()

def plot_detuning_spectrum(learner, dis_amp, m_freq, aomsel,
                           savepath=None, show=True):
    data = learner.data
    xs = np.array(list(data.keys()))
    ys = np.array(list(data.values()))
    order = np.argsort(xs)
    xs, ys = xs[order], ys[order]

    sigma_x, sigma_y, sigma_z = ys[:, 0], ys[:, 1], ys[:, 2]
    entropy = ys[:, 3]
    coherence = np.sqrt(sigma_x**2 + sigma_y**2 + sigma_z**2)

    cx = float((sigma_x.max() - sigma_x.min()) / 2)
    cy = float((sigma_y.max() - sigma_y.min()) / 2)
    cz = float((sigma_z.max() - sigma_z.min()) / 2)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(8.5, 3.6), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08},
    )

    title = (rf"$\alpha = {dis_amp}$"
             rf"$\quad \omega_m / 2\pi = {m_freq}$ MHz"
             rf"$\quad$ AOM: {aomsel}")
    ax1.set_title(title, color=COLOURS["text"], pad=8)

    kw = dict(markersize=2.8, linewidth=0.8, markeredgewidth=0)
    ax1.plot(xs, sigma_x, color=COLOURS["sigma_x"], marker="o",
             label=rf"$\sigma_x$  – C = {cx:.2f}", **kw)
    ax1.plot(xs, sigma_y, color=COLOURS["sigma_y"], marker="o",
             label=rf"$\sigma_y$  – C = {cy:.2f}", **kw)
    ax1.plot(xs, sigma_z, color=COLOURS["sigma_z"], marker="o",
             label=rf"$\sigma_z$  – C = {cz:.2f}", **kw)
    ax1.plot(xs, coherence, color=COLOURS["coherence"], marker="o",
             label=r"Coherence", **kw)

    ax1.set_ylabel(r"$\langle \sigma_i \rangle$")
    ax1.set_ylim(-1.08, 1.08)
    ax1.yaxis.set_major_locator(MultipleLocator(0.5))
    ax1.legend(loc="upper right", ncol=2)
    ax1.grid(True)

    ax2.plot(xs, entropy, color=COLOURS["entropy"], marker="o", **kw)
    ax2.set_xlabel(r"Detuning  $(2\pi\,\omega_{\rm LF})$")
    ax2.set_ylabel("Entropy")
    ax2.set_ylim(bottom=-0.01)
    ax2.grid(True)

    if savepath:
        fig.savefig(savepath, format="svg", transparent=False)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig

def plot_all(learners, dis_amps, m_freq, aomsel, prefix="R"):
    if isinstance(learners, dict):
        learners = [learners[a] for a in dis_amps]
    for amp, lrn in zip(dis_amps, learners):
        plot_detuning_spectrum(lrn, amp, m_freq, aomsel,
                               savepath=f"{prefix}_{amp}_alpha.svg", show=False)
