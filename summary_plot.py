import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize


def _ensure_dir(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


# --------------------------------------------------------------------------
# 1. Courbes superposées : une sous-figure par réseau
# --------------------------------------------------------------------------
def plot_curve_grid(curves, networks, path, baseline="random", ncols=2,
                    xlabel="Proportion de noeuds passifs supprimés",
                    ylabel="Proportion de noeuds actifs éteints"):
    """Une grille de sous-figures ; chaque sous-figure superpose toutes les stratégies.

    La stratégie `baseline` est tracée en pointillés noirs, avec une bande ± std
    si une valeur std est fournie (courbe = (x, mean, std)).
    """
    strategies = list(curves)
    n = len(networks)
    ncols = min(ncols, n)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.5 * ncols, 4 * nrows),
                             sharex=True, sharey=True, squeeze=False)
    cmap = plt.get_cmap("tab10")
    colors = {s: cmap(i % 10) for i, s in enumerate(s for s in strategies if s != baseline)}

    for ax, net in zip(axes.flat, networks):
        for s in strategies:
            if net not in curves[s]:
                continue
            c = curves[s][net]
            x, y = np.asarray(c[0]), np.asarray(c[1])
            if s == baseline:
                ax.plot(x, y, "k--", lw=1.5, label=f"{s} (réf.)", zorder=1)
                if len(c) > 2 and c[2] is not None:
                    std = np.asarray(c[2])
                    ax.fill_between(x, y - std, y + std, color="k", alpha=0.15, zorder=0)
            else:
                ax.plot(x, y, lw=1.6, color=colors[s], label=s)
        ax.set_title(net, fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)

    for ax in axes.flat[n:]:          # cache les cases vides
        ax.set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel(xlabel)
    for ax in axes[:, 0]:
        ax.set_ylabel(ylabel)

    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=min(len(labels), 5),
               fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    _ensure_dir(path)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# 2. Heatmap stratégie x réseau, colorée par le gain relatif vs aléatoire
# --------------------------------------------------------------------------
def compute_gain(results, baseline="random", larger_is_better=True):
    """Retourne (strategies, networks, gain) ; gain[i, j] est le gain relatif de la
    stratégie i sur le réseau j par rapport à `baseline`. Valeur manquante = NaN.

    larger_is_better=True  : gain = (AUC - AUC_ref) / AUC_ref
    larger_is_better=False : gain = (AUC_ref - AUC) / AUC_ref
    Dans les deux cas, gain > 0 signifie "plus efficace que l'aléatoire".
    """
    strategies = [s for s in results if s != baseline]
    networks = list(results[baseline])
    gain = np.full((len(strategies), len(networks)), np.nan)
    for j, net in enumerate(networks):
        ref = results[baseline][net][0]
        if ref == 0:
            continue
        for i, s in enumerate(strategies):
            if net in results[s]:
                auc = results[s][net][0]
                d = (auc - ref) if larger_is_better else (ref - auc)
                gain[i, j] = d / ref
    return strategies, networks, gain


def plot_heatmap(results, path, baseline="random", larger_is_better=True,
                 annotate=True, sort_rows=True):
    """Heatmap des gains relatifs. Lignes triées par gain moyen (meilleure en haut)."""
    strategies, networks, gain = compute_gain(results, baseline, larger_is_better)

    if sort_rows:
        order = np.argsort(-np.nanmean(gain, axis=1))
        strategies = [strategies[i] for i in order]
        gain = gain[order]

    m = np.nanmax(np.abs(gain))
    m = m if m > 0 else 1.0
    fig, ax = plt.subplots(figsize=(1.8 + 0.65 * len(networks),
                                    1.5 + 0.55 * len(strategies)))
    im = ax.imshow(gain, cmap="RdYlGn", norm=Normalize(-m, m), aspect="auto")
    ax.set_xticks(range(len(networks)), networks, rotation=60, ha="right", fontsize=8)
    ax.set_yticks(range(len(strategies)), strategies)

    if annotate:
        for i in range(gain.shape[0]):
            for j in range(gain.shape[1]):
                v = gain[i, j]
                if np.isnan(v):
                    ax.text(j, i, "–", ha="center", va="center", fontsize=7, color="gray")
                else:
                    ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7)

    ax.set_title(f"Gain relatif de l'AUC par rapport à « {baseline} »")
    fig.colorbar(im, ax=ax, label="gain relatif (> 0 : plus efficace que l'aléatoire)")
    fig.tight_layout()
    _ensure_dir(path)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)



if __name__ == "__main__":
    import sys