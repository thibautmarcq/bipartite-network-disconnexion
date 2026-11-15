import time
from pathlib import Path
import matplotlib

from adaptive_musrank import adaptive_musrank_result
from analyse_resultats import delete_nodes_result
from strategies import get_strategy_ranking
from tools import read_unoriented_from_csv
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path("data/fichiers_csv/du papier")

def list_networks():
    """Réseaux X pour lesquels X_nodes.csv et X_edges.csv existent."""
    names = [p.name[:-len("_edges.csv")] for p in DATA_DIR.glob("*_edges.csv")
             if (DATA_DIR / (p.name[:-len("_edges.csv")] + "_nodes.csv")).exists()]
    return sorted(names)



def main():
    networks = list_networks()
    t_static =[]
    t_adaptive = []  
    for net in networks:
        try:
            graph, actives, passives = read_unoriented_from_csv(f"{DATA_DIR}/{net}")
            
            t_static.append(delete_nodes_result(graph, actives, passives, "musrank", False, net)[1])

            t_adaptive.append(adaptive_musrank_result(graph, actives, passives, False, net)[1])
        except Exception as e:              # un réseau qui plante est ignoré pour toutes les stratégies
            print(f"ignoré {net} : {e}")
            continue
        finally:
            plt.close("all")
        print(f"{net:20s} traité")
 
    if not t_static or not t_adaptive:
        raise SystemExit("Aucun réseau traité.")
 
    means = [np.mean(t_static), np.mean(t_adaptive)]
    stds = [np.std(t_static), np.std(t_adaptive)]
    print(f"\nMoyenne sur {len(networks)} réseaux :")
    print(f"  musrank           {means[0]:.4f}s (écart-type {stds[0]:.4f}, variance {stds[0] ** 2:.3e})")
    print(f"  musrank adaptatif {means[1]:.4f}s (écart-type {stds[1]:.4f}, variance {stds[1] ** 2:.3e})")
 
 
    lower = np.minimum(stds, 0.9 * np.array(means))        # reste positif en échelle log
    plt.figure(figsize=(6, 4.5))
    plt.bar(["musrank", "musrank adaptatif"], means, yerr=[lower, stds], capsize=5,
            color=["tab:blue", "tab:orange"])
    plt.yscale("log")
    plt.ylabel("Temps de classement moyen (s, échelle log)")
    plt.title(f"Temps d'exécution de MusRank sur {len(networks)} réseaux (barres d'erreur = écart-type)")
    plt.grid(True, axis="y", alpha=0.3)
 
 
    plt.tight_layout()
    Path("results").mkdir(exist_ok=True)
    plt.savefig("results/musrank_times.png", dpi=300)
    print("figure écrite dans results/musrank_times.png")
 
 
if __name__ == "__main__":
    main()