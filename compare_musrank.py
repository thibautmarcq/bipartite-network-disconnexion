"""Compare la moyenne des aires d'extinction : musrank, musrank adaptatif, musrank inversé.

Usage : python compare_musrank.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from analyse_resultats import delete_nodes_result
from adaptive_musrank import adaptive_musrank_result
from tools import read_unoriented_from_csv

DATA_DIR = Path("data/fichiers_csv/du papier")
NETWORKS = None            # None = tous les réseaux du dossier, ou par exemple ["alpine", "dupint"]


def list_networks():
    """Réseaux X pour lesquels X_nodes.csv et X_edges.csv existent."""
    names = [p.name[:-len("_edges.csv")] for p in DATA_DIR.glob("*_edges.csv")
             if (DATA_DIR / (p.name[:-len("_edges.csv")] + "_nodes.csv")).exists()]
    return sorted(names)


def main():
    networks = NETWORKS or list_networks()
    variants = ["musrank", "musrank_adaptive", "musrank_reversed"]
    areas = {v: [] for v in variants}
    kept = []

    for name in networks:
        try:
            graph, actives, passives = read_unoriented_from_csv(f"{DATA_DIR}/{name}")
            a = {
                "musrank": delete_nodes_result(graph, actives, passives, "musrank", False, name)[0],
                "musrank_adaptive": adaptive_musrank_result(graph, actives, passives, False, name)[0],
                "musrank_reversed": delete_nodes_result(graph, actives, passives, "musrank_reversed", False, name)[0],
            }
        except Exception as e:                       # un réseau qui plante est ignoré pour les 3 variantes
            print(f"ignoré {name} : {e}")
            continue
        finally:
            plt.close("all")                         # évite l'accumulation de figures ouvertes
        for v in variants:
            areas[v].append(a[v])
        kept.append(name)
        print(f"{name:20s} " + " | ".join(f"{v} = {a[v]:.4f}" for v in variants))

    if not kept:
        raise SystemExit("Aucun réseau traité.")

    means = [np.mean(areas[v]) for v in variants]
    stds = [np.std(areas[v]) for v in variants]
    print(f"\nMoyenne sur {len(kept)} réseaux :")
    for v, m, s in zip(variants, means, stds):
        print(f"  {v:18s} {m:.4f} (± {s:.4f})")

    plt.figure(figsize=(6, 4.5))
    plt.bar(variants, means, yerr=stds, capsize=5, color=["tab:blue", "tab:orange", "tab:green"])
    plt.ylabel("Aire sous la courbe d'extinction (moyenne)")
    plt.title(f"MusRank : moyenne sur {len(kept)} réseaux (barres d'erreur = écart-type)")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    Path("results").mkdir(exist_ok=True)
    plt.savefig("results/musrank_comparison.png", dpi=300)
    print("figure écrite dans results/musrank_comparison.png")


if __name__ == "__main__":
    main()