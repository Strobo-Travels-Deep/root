#!/usr/bin/env python3
"""
plot_coastline.py — Render the three WP-C v0.1 figure deliverables.

Inputs : numerics/coastline_v1.h5
Outputs:
  plots/coastline_vp_maps.png       — V & P heatmaps per |α|, drive-LD +
                                      motional-LD hatching (independent
                                      layers), impulsive-limit overlay on
                                      the δt/T_m → 0 edge per §4.5 of the
                                      council memo.
  plots/coastline_chi_collapse.png  — χ-collapse test (§4.5 of README)
  plots/coastline_secondary.png     — diamond amp, |δ⟨n⟩|, control slice,
                                      with both drive-LD and motional-LD
                                      hatches overlaid.
"""
from __future__ import annotations

import os
import sys

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'plots'))
H5_PATH = os.path.join(SCRIPT_DIR, 'coastline_v1.h5')

sys.path.insert(0, os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'scripts')))
from stroboscopic import HilbertSpace, build_impulsive_train  # noqa: E402
from stroboscopic import operators as ops                     # noqa: E402

ETA = 0.397


def alpha_tag(alpha: float) -> str:
    return f"alpha_{alpha:.1f}".replace('.', 'p')


def nmax_for_alpha(alpha: float) -> int:
    return 80 if alpha >= 4.5 else 60


def overlay_hatch(ax, mask, edgecolor='white', hatch='///',
                  linewidth=0.0):
    """Draw hatched rectangles over mask==True cells (facecolor='none')."""
    nrow, ncol = mask.shape
    for i in range(nrow):
        for j in range(ncol):
            if mask[i, j]:
                rect = Rectangle((j - 0.5, i - 0.5), 1.0, 1.0,
                                 facecolor='none', edgecolor=edgecolor,
                                 hatch=hatch, linewidth=linewidth)
                ax.add_patch(rect)


def compute_impulsive_V(alpha: float, N_list, omega_m: float,
                        n_theta0: int = 64):
    """V = 1 − min_ϑ |C| at δ=0 in the impulsive-kick limit at each N.

    pulse_area = π/(2N) to match the recalibrated-Ω net train rotation.
    Gap between kicks is T_m = 2π/ω_m. Used as an analytic-reference
    overlay on the δt/T_m → 0 edge of the primary heatmaps (memo §4.5).
    """
    nmax = nmax_for_alpha(alpha)
    hs = HilbertSpace(n_spins=1, mode_cutoffs=(nmax,))
    C = ops.coupling(ETA, nmax); Cdag = C.conj().T
    theta0_grid = np.linspace(0.0, 2 * np.pi, n_theta0, endpoint=False)

    V = np.zeros(len(N_list))
    for k, N_p in enumerate(N_list):
        train = build_impulsive_train(
            hs=hs, eta=ETA, pulse_area=np.pi / (2.0 * float(N_p)),
            omega_m=omega_m, delta=0.0, n_pulses=int(N_p),
            gap_include_motion=True, gap_include_spin_detuning=True,
            C=C, Cdag=Cdag,
        )
        coh_min = 1.0
        for th0 in theta0_grid:
            psi0 = hs.prepare_state(
                spin={'theta_deg': 0.0, 'phi_deg': 0.0},
                modes=[{'alpha': alpha,
                        'alpha_phase_deg': float(np.degrees(th0))}],
            )
            psi0 = hs.apply_mw_pi2(psi0, 0.0)
            psi_final = train.evolve(psi0)
            obs = hs.observables(psi_final)
            c = np.sqrt(obs['sigma_x'] ** 2 + obs['sigma_y'] ** 2)
            if c < coh_min: coh_min = c
        V[k] = 1.0 - float(coh_min)
    return V


def plot_vp_maps():
    with h5py.File(H5_PATH, 'r') as f:
        N_list = f['N_list'][:]
        dt_list = f['dt_frac_list'][:]
        alphas = f['alpha_list'][:]
        omega_m = float(f.attrs['omega_m'])
        data = {}
        for a in alphas:
            g = f[alpha_tag(float(a))]
            data[float(a)] = dict(
                V=g['V'][:], P=g['P'][:],
                ld_drive=g['ld_flag_drive'][:],
                ld_mot=g['ld_flag_motional'][:],
                omega_eff=g['omega_eff_over_omega_m'][:],
            )

    print("  computing impulsive-limit reference …")
    V_imp = {float(a): compute_impulsive_V(float(a), N_list, omega_m)
             for a in alphas}

    n_alpha = len(alphas)
    fig, axes = plt.subplots(n_alpha, 2, figsize=(10, 2.7 * n_alpha),
                             squeeze=False,
                             gridspec_kw={'width_ratios': [1, 1]})
    fig.suptitle(r'WP-C v0.1 — Strong/weak-binding coastline: '
                 r'$V=1-\min_{\vartheta}|C|$ (left) and '
                 r'$P=\langle|C|\rangle_\vartheta$ at $\delta=0.5\,\omega_m$ (right)',
                 fontsize=11)

    for ai, alpha in enumerate(alphas):
        d = data[float(alpha)]
        for bi, (name, arr) in enumerate([('V', d['V']), ('P', d['P'])]):
            ax = axes[ai, bi]
            im = ax.imshow(arr, origin='lower', aspect='auto',
                           vmin=0.0, vmax=1.0, cmap='viridis')
            # Independent hatch layers — both render on cells where both
            # flags set (memo §4.1 + README §2.3).
            overlay_hatch(ax, d['ld_drive'], edgecolor='white', hatch='///')
            overlay_hatch(ax, d['ld_mot'], edgecolor='red', hatch='...',
                          linewidth=0.5)
            ax.set_xticks(range(len(dt_list)))
            ax.set_xticklabels([f'{x:.2f}' for x in dt_list], fontsize=8)
            ax.set_yticks(range(len(N_list)))
            ax.set_yticklabels([f'{int(n)}' for n in N_list], fontsize=8)
            ax.set_xlabel(r'$\delta t / T_m$', fontsize=9)
            ax.set_ylabel(r'$N$', fontsize=9)
            ax.set_title(rf'$|\alpha|={alpha:.0f}$   —   {name}'
                         rf'   ($\eta\sqrt{{\bar n+1}}={ETA*np.sqrt(alpha**2+1):.2f}$)',
                         fontsize=9)
            for i in range(arr.shape[0]):
                for j in range(arr.shape[1]):
                    val = arr[i, j]
                    color = 'white' if val < 0.5 else 'black'
                    ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                            fontsize=6.5, color=color)
            # Impulsive-limit overlay on V maps only (memo §4.5).
            if name == 'V':
                v_imp = V_imp[float(alpha)]
                for i, v in enumerate(v_imp):
                    col = 'white' if v < 0.5 else 'black'
                    ax.plot(-0.85, i, marker='>', color='orange',
                            markersize=7, markeredgecolor='k',
                            markeredgewidth=0.5, clip_on=False,
                            zorder=5)
                    ax.text(-1.35, i, f'{v:.2f}', ha='center', va='center',
                            fontsize=6.5, color='k', clip_on=False)
                ax.text(-1.1, arr.shape[0] + 0.1,
                        r'$\delta t \to 0$' '\n(impulsive)',
                        ha='center', va='bottom', fontsize=6.5,
                        color='darkorange', clip_on=False)
            fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

    fig.text(0.01, 0.005,
             "Legend: white /// = drive-LD ceiling breach "
             r"($\Omega_\mathrm{eff}/\omega_m>0.3$, §2.1). "
             r"Red ··· = motional-LD breach ($\eta\sqrt{\langle n\rangle+1}>1$, §2.2), "
             "not engine-invalidating. Cells breaching both carry both hatches. "
             "Orange ▷ at left: V in the exact impulsive-kick limit "
             r"$\delta t/T_m\to 0$ at matched net rotation $N\cdot A=\pi/2$ "
             "(memo §4.5 reference overlay). Rubric: (V high, P high) "
             "strong-binding; (V low, P high) pulse-broadening; (V low, P low) "
             "Doppler merging.",
             fontsize=7, color='dimgray', wrap=True)

    out = os.path.join(PLOTS_DIR, 'coastline_vp_maps.png')
    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")


def plot_chi_collapse():
    with h5py.File(H5_PATH, 'r') as f:
        N_list = f['N_list'][:]
        dt_list = f['dt_frac_list'][:]
        alphas = f['alpha_list'][:]
        records = []
        for a in alphas:
            g = f[alpha_tag(float(a))]
            V = g['V'][:]; P = g['P'][:]
            ld_drive = g['ld_flag_drive'][:]
            for i, N in enumerate(N_list):
                for j, dt in enumerate(dt_list):
                    term_N = 1.0 / float(N)
                    # ω_m · δt = 2π · dt_frac (since δt = dt_frac · 2π/ω_m).
                    term_dt = 1.0 / (2.0 * np.pi * float(dt))
                    term_doppler = ETA * float(a)
                    chi2 = term_N ** 2 + term_dt ** 2 + term_doppler ** 2
                    chi = np.sqrt(chi2)
                    records.append(dict(
                        alpha=float(a), N=int(N), dt=float(dt),
                        V=float(V[i, j]), P=float(P[i, j]),
                        chi=float(chi),
                        ld_breach=bool(ld_drive[i, j])))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    colors = {0.0: 'C0', 1.0: 'C1', 3.0: 'C2', 5.0: 'C3'}

    for a in alphas:
        pts = [r for r in records if r['alpha'] == float(a)]
        x = np.array([r['chi'] for r in pts])
        y = np.array([r['V'] for r in pts])
        breach = np.array([r['ld_breach'] for r in pts])
        ax1.scatter(x[~breach], y[~breach], s=30, c=colors.get(float(a), 'k'),
                    label=rf'$|\alpha|={a:.0f}$ (engine-valid)',
                    edgecolors='k', linewidths=0.3)
        ax1.scatter(x[breach], y[breach], s=30, c=colors.get(float(a), 'k'),
                    marker='x', label=rf'$|\alpha|={a:.0f}$ (drive-LD breach)')
    chi_ref = np.linspace(0.01, max(r['chi'] for r in records) * 1.05, 200)
    ax1.plot(chi_ref, 1 - np.exp(-chi_ref ** 2), '--', color='gray', lw=1,
             label=r'ref $V = 1-e^{-\chi^2}$')
    ax1.set_xscale('log'); ax1.set_xlabel(r'$\chi$', fontsize=10)
    ax1.set_ylabel(r'$V$', fontsize=10)
    ax1.set_title(r'$V$ vs $\chi = [\,(1/N)^2 + (1/\omega_m\delta t)^2 + (\eta|\alpha|)^2\,]^{1/2}$',
                  fontsize=10)
    ax1.legend(fontsize=7, loc='lower left', bbox_to_anchor=(1.02, 0.0))
    ax1.grid(alpha=0.3); ax1.set_ylim(-0.05, 1.05)

    for a in alphas:
        pts = [r for r in records if r['alpha'] == float(a)]
        x = np.array([r['chi'] for r in pts])
        y = np.array([r['P'] for r in pts])
        breach = np.array([r['ld_breach'] for r in pts])
        ax2.scatter(x[~breach], y[~breach], s=30, c=colors.get(float(a), 'k'),
                    edgecolors='k', linewidths=0.3,
                    label=rf'$|\alpha|={a:.0f}$')
        ax2.scatter(x[breach], y[breach], s=30, c=colors.get(float(a), 'k'),
                    marker='x')
    ax2.set_xscale('log'); ax2.set_xlabel(r'$\chi$', fontsize=10)
    ax2.set_ylabel(r'$P$', fontsize=10)
    ax2.set_title(r'$P$ vs $\chi$ (off-tooth coherence at $\delta=0.5\,\omega_m$)',
                  fontsize=10)
    ax2.legend(fontsize=7, loc='lower right'); ax2.grid(alpha=0.3)
    ax2.set_ylim(-0.05, 1.1)

    fig.suptitle(r'WP-C v0.1 — $\chi$-collapse test (§4.5)  '
                 r'— falsification is a positive result', fontsize=10)
    out = os.path.join(PLOTS_DIR, 'coastline_chi_collapse.png')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")


def plot_secondary():
    with h5py.File(H5_PATH, 'r') as f:
        N_list = f['N_list'][:]
        dt_list = f['dt_frac_list'][:]
        alphas = f['alpha_list'][:]
        primary = {}
        control = {}
        for a in alphas:
            g = f[alpha_tag(float(a))]
            primary[float(a)] = dict(
                diamond=g['diamond_amp_sigma_z'][:],
                dn=g['dn_peak'][:],
                ld_drive=g['ld_flag_drive'][:],
                ld_mot=g['ld_flag_motional'][:],
            )
            gc = f[f"{alpha_tag(float(a))}/control_fixed_omega_hasse"]
            control[float(a)] = dict(
                V=gc['V'][:], P=gc['P'][:],
                net_rot=gc['net_rotation_pi2'][:],
            )

    n_alpha = len(alphas)
    fig, axes = plt.subplots(n_alpha, 3, figsize=(14, 2.8 * n_alpha),
                             squeeze=False)
    fig.suptitle('WP-C v0.1 — Secondary observables and fixed-Ω control slice',
                 fontsize=11)

    for ai, alpha in enumerate(alphas):
        d = primary[float(alpha)]
        ax = axes[ai, 0]
        im = ax.imshow(d['diamond'], origin='lower', aspect='auto',
                       vmin=0.0, vmax=1.0, cmap='magma')
        overlay_hatch(ax, d['ld_drive'], edgecolor='white', hatch='///')
        overlay_hatch(ax, d['ld_mot'], edgecolor='red', hatch='...',
                      linewidth=0.5)
        ax.set_xticks(range(len(dt_list)))
        ax.set_xticklabels([f'{x:.2f}' for x in dt_list], fontsize=7)
        ax.set_yticks(range(len(N_list)))
        ax.set_yticklabels([f'{int(n)}' for n in N_list], fontsize=7)
        ax.set_xlabel(r'$\delta t/T_m$'); ax.set_ylabel(r'$N$')
        ax.set_title(rf'$|\alpha|={alpha:.0f}$: diamond $\sigma_z$ amp.', fontsize=9)
        fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

        ax = axes[ai, 1]
        im = ax.imshow(d['dn'], origin='lower', aspect='auto', cmap='magma')
        overlay_hatch(ax, d['ld_drive'], edgecolor='white', hatch='///')
        overlay_hatch(ax, d['ld_mot'], edgecolor='red', hatch='...',
                      linewidth=0.5)
        ax.set_xticks(range(len(dt_list)))
        ax.set_xticklabels([f'{x:.2f}' for x in dt_list], fontsize=7)
        ax.set_yticks(range(len(N_list)))
        ax.set_yticklabels([f'{int(n)}' for n in N_list], fontsize=7)
        ax.set_xlabel(r'$\delta t/T_m$'); ax.set_ylabel(r'$N$')
        ax.set_title(rf'$|\alpha|={alpha:.0f}$: $|\delta\langle n\rangle|_\mathrm{{peak}}$', fontsize=9)
        fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

        ax = axes[ai, 2]
        c = control[float(alpha)]
        ax.plot(N_list, c['V'], 'o-', label='V (fixed Ω)', color='C0')
        ax.plot(N_list, c['P'], 's-', label='P (fixed Ω)', color='C1')
        ax.set_xscale('log')
        ax.set_ylim(-0.05, 1.1); ax.set_xlabel(r'$N$'); ax.set_ylabel('V, P')
        ax.set_title(rf'$|\alpha|={alpha:.0f}$: control slice $\delta t/T_m=0.13$', fontsize=9)
        for i, (N, nr) in enumerate(zip(N_list, c['net_rot'])):
            ax.annotate(f'{nr:.1f}', (N, c['V'][i]),
                        textcoords='offset points', xytext=(0, 6),
                        fontsize=7, ha='center', color='C0')
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc='center right')

    axes[0, 2].text(0.02, -0.25,
                    r'Annotations: $N\cdot\Omega_\mathrm{eff}\cdot\delta t/(\pi/2)$ '
                    '— net carrier rotation. Rabi-envelope nodes at integer '
                    r'multiples of 2 are power-broadening artefacts (Guardian-2 D9). '
                    'Heatmap hatching: white /// = drive-LD breach; red ··· = motional-LD breach.',
                    transform=axes[0, 2].transAxes, fontsize=7, color='dimgray')

    out = os.path.join(PLOTS_DIR, 'coastline_secondary.png')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out, dpi=140, bbox_inches='tight')
    plt.close(fig)
    print(f"  wrote {out}")


def main():
    print("Plotting WP-C v0.1 deliverables (v0.1.1 patch).")
    plot_vp_maps()
    plot_chi_collapse()
    plot_secondary()


if __name__ == '__main__':
    main()
