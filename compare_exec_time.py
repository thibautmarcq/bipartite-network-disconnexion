import time
from pathlib import Path
import matplotlib

from analyse_resultats import delete_nodes_result
from strategies import get_strategy_ranking
from tools import read_unoriented_from_csv
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path("data")

STRATEGIES = ("closeness", "eigenvector", "betweenness", "degree",
              "pagerank", "musrank", "musrank_reversed", "neighborhood", "nestedness")

def list_networks():
    """Réseaux X pour lesquels X_nodes.csv et X_edges.csv existent."""
    names = [p.name[:-len("_edges.csv")] for p in DATA_DIR.glob("*_edges.csv")
             if (DATA_DIR / (p.name[:-len("_edges.csv")] + "_nodes.csv")).exists()]
    return sorted(names)



def main():
    networks = list_networks()
    times = {s: [] for s in STRATEGIES}   
    for net in networks:
        try:
            graph, actives, passives = read_unoriented_from_csv(f"{DATA_DIR}/{net}")
            for s in STRATEGIES:
                times[s].append(delete_nodes_result(graph, actives, passives, s, False, net)[1])
        except Exception as e:              # un réseau qui plante est ignoré pour toutes les stratégies
            print(f"ignoré {net} : {e}")
            continue
        finally:
            plt.close("all")
        print(f"{net:20s} traité")
 
    if not times[STRATEGIES[0]]:
        raise SystemExit("Aucun réseau traité.")
 
    means = np.array([np.mean(times[s]) for s in STRATEGIES])
    stds = np.array([np.std(times[s]) for s in STRATEGIES])
    print(f"\nTemps moyen sur {len(times[STRATEGIES[0]])} réseaux :")
    for s, m, sd in zip(STRATEGIES, means, stds):
        print(f"  {s:18s} moyenne = {m:.6f}s | écart-type = {sd:.6f}s | variance = {sd ** 2:.3e}")
 
    # échelle log : les temps vont de ~1e-6 s à plusieurs secondes.
    # la partie basse de la barre d'erreur est limitée à 90 % de la moyenne pour rester positive en échelle log
    lower = np.minimum(stds, 0.9 * means)
    plt.figure(figsize=(9, 5))
    plt.bar(STRATEGIES, means, yerr=[lower, stds], capsize=4, color="tab:blue")
    plt.yscale("log")
    plt.ylabel("Temps de classement moyen (s, échelle log)")
    plt.title(f"Temps d'exécution par stratégie ({len(times[STRATEGIES[0]])} réseaux, barres d'erreur = écart-type)")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    Path("results").mkdir(exist_ok=True)
    plt.savefig("results/execution_times.png", dpi=300)
    print("figure écrite dans results/execution_times.png")
 
 
if __name__ == "__main__":
    main()