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

# ── Harbour colour definitions ───────────────────────────────────
COLOURS = dict(
    bg_figure  = "#f2dcd6",   # page backdrop
    bg_axes    = "#faf3f0",   # card / plot area
    grid       = "#d4a99e",   # border tone
    text       = "#3a2520",   # primary text
    text_sec   = "#6b4a40",   # secondary text
    text_muted = "#8c6e63",   # muted / tick labels
    accent     = "#a0453a",   # terracotta accent
    border     = "#d4a99e",
    # ── trace colours (distinguishable on warm ground) ──
    sigma_x    = "#a0453a",   # terracotta   (was: red)
    sigma_y    = "#3a5a8a",   # slate blue   (was: navy)
    sigma_z    = "#c08a20",   # warm amber   (was: orange)
    coherence  = "#3a2520",   # near-black   (was: black)
    entropy    = "#3a2520",
)

# ── Global rcParams ──────────────────────────────────────────────
def _apply_rcparams():
    """Set matplotlib defaults to match the Harbour page."""
    mpl.rcParams.update({
        # — typography —
        "font.family":        "serif",
        "font.serif":         ["Source Serif 4", "Georgia", "DejaVu Serif"],
        "mathtext.fontset":   "cm",
        "font.size":          11,
        "axes.titlesize":     12,
        "axes.labelsize":     11,
        "legend.fontsize":    9,
        "xtick.labelsize":    9.5,
        "ytick.labelsize":    9.5,
        # — colours —
        "figure.facecolor":   COLOURS["bg_figure"],
        "axes.facecolor":     COLOURS["bg_axes"],
        "axes.edgecolor":     COLOURS["border"],
        "axes.labelcolor":    COLOURS["text"],
        "text.color":         COLOURS["text"],
        "xtick.color":        COLOURS["text_muted"],
        "ytick.color":        COLOURS["text_muted"],
        "grid.color":         COLOURS["grid"],
        "grid.alpha":         0.35,
        "grid.linewidth":     0.6,
        "legend.framealpha":  0.85,
        "legend.edgecolor":   COLOURS["border"],
        "legend.facecolor":   COLOURS["bg_axes"],
        # — layout —
        "axes.linewidth":     0.7,
        "xtick.major.width":  0.6,
        "ytick.major.width":  0.6,
        "xtick.direction":    "in",
        "ytick.direction":    "in",
        "figure.dpi":         150,
        "savefig.dpi":        150,       # irrelevant for SVG, keeps PNG preview crisp
        "savefig.bbox":       "tight",
        "savefig.pad_inches": 0.12,
    })

_apply_rcparams()


# ── Plotting function ────────────────────────────────────────────
def plot_detuning_spectrum(learner, dis_amp, m_freq, aomsel,
                           savepath=None, show=True):
    """
    Plot σ_x, σ_y, σ_z, coherence and entropy vs. detuning.

    Parameters
    ----------
    learner   : adaptive learner with .data  {detuning: [σx, σy, σz, S]}
    dis_amp   : displacement amplitude α  (float or int)
    m_freq    : mode frequency in 2π MHz  (float)
    aomsel    : AOM selection label        (str)
    savepath  : if given, write SVG to this path
    show      : call plt.show()
    """
    # ── extract & sort ───────────────────────────────────────────
    data = learner.data
    xs = np.array(list(data.keys()))
    ys = np.array(list(data.values()))
    order = np.argsort(xs)
    xs, ys = xs[order], ys[order]

    sigma_x, sigma_y, sigma_z = ys[:, 0], ys[:, 1], ys[:, 2]
    entropy = ys[:, 3]
    coherence = np.sqrt(sigma_x**2 + sigma_y**2 + sigma_z**2)

    contrast_x = (sigma_x.max() - sigma_x.min()) / 2
    contrast_y = (sigma_y.max() - sigma_y.min()) / 2
    contrast_z = (sigma_z.max() - sigma_z.min()) / 2

    # ── figure ───────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(8.5, 3.6), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08},
    )

    # ── title ────────────────────────────────────────────────────
    title = (rf"$\alpha = {dis_amp}$"
             rf"$\quad \omega_m / 2\pi = {m_freq}$ MHz"
             rf"$\quad$ AOM: {aomsel}")
    ax1.set_title(title, color=COLOURS["text"], pad=8)

    # ── shared trace style ───────────────────────────────────────
    kw = dict(markersize=2.8, linewidth=0.8, markeredgewidth=0)

    ax1.plot(xs, sigma_x,   color=COLOURS["sigma_x"],  marker="o",
             label=rf"$\sigma_x$  – C = {contrast_x:.2f}", **kw)
    ax1.plot(xs, sigma_y,   color=COLOURS["sigma_y"],  marker="o",
             label=rf"$\sigma_y$  – C = {contrast_y:.2f}", **kw)
    ax1.plot(xs, sigma_z,   color=COLOURS["sigma_z"],  marker="o",
             label=rf"$\sigma_z$  – C = {contrast_z:.2f}", **kw)
    ax1.plot(xs, coherence,  color=COLOURS["coherence"], marker="o",
             label=r"Coherence", **kw)

    ax1.set_ylabel(r"$\langle \sigma_i \rangle$")
    ax1.set_ylim(-1.08, 1.08)
    ax1.yaxis.set_major_locator(MultipleLocator(0.5))
    ax1.legend(loc="upper right", ncol=2, handlelength=1.6,
               columnspacing=1.0, borderpad=0.5)
    ax1.grid(True)

    # ── entropy ──────────────────────────────────────────────────
    ax2.plot(xs, entropy, color=COLOURS["entropy"], marker="o", **kw)
    ax2.set_xlabel(r"Detuning  $(2\pi\,\omega_{\rm LF})$")
    ax2.set_ylabel("Entropy")
    ax2.set_ylim(bottom=-0.01)
    ax2.grid(True)

    # ── spines ───────────────────────────────────────────────────
    for ax in (ax1, ax2):
        ax.tick_params(which="both", length=3)
        for spine in ax.spines.values():
            spine.set_color(COLOURS["border"])

    # ── save / show ──────────────────────────────────────────────
    if savepath:
        fig.savefig(savepath, format="svg", transparent=False)
        print(f"  ✓  saved  {savepath}")
    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig


# ── Convenience: batch all four α values ─────────────────────────
def plot_all(learners, dis_amps, m_freq, aomsel, prefix="R"):
    """
    learners  : dict  {alpha: learner}  or list aligned with dis_amps
    dis_amps  : [0, 1, 3, 5]
    """
    if isinstance(learners, dict):
        learners = [learners[a] for a in dis_amps]
    for amp, lrn in zip(dis_amps, learners):
        path = f"{prefix}_{amp}_alpha.svg"
        plot_detuning_spectrum(lrn, amp, m_freq, aomsel,
                               savepath=path, show=False)
