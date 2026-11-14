import numpy as np
from analyse_resultats import delete_nodes_result
from summary_plot import plot_curve_grid, plot_heatmap
from tools import read_unoriented_from_csv
from pathlib import Path

DATA_DIR = Path("data/fichiers_csv/du papier")

def list_datasets(folder=DATA_DIR):
    """Returns the sorted dataset names found in the folder (without extension)."""
    names = []
    for edges in folder.glob("*_edges.csv"):
        name = edges.name[: -len("_edges.csv")]
        if not (folder / f"{name}_nodes.csv").exists():
            print(f"skipped {name}: no matching _nodes.csv")
            continue
        names.append(name)
    names = sorted(names)
    return names

DATASETS = list_datasets()

N_RANDOM = 100
STRATEGIES = ("closeness", "eigenvector", "betweenness", "degree",
              "pagerank", "musrank", "musrank_reversed")


def run_random(graph, actives, passives, name):
    areas, ys, x = [], [], None
    for _ in range(N_RANDOM):
        area, _, x, y = delete_nodes_result(graph, actives, passives,
                                            "random", False, name)
        areas.append(area)
        ys.append(y)
    ys = np.array(ys)
    return float(np.mean(areas)), x, ys.mean(axis=0), ys.std(axis=0)


def main() -> None:
    show_plots = False
    curves = {s: {} for s in ("random",) + STRATEGIES}
    results = {s: {} for s in ("random",) + STRATEGIES}

    for name in DATASETS:
        path = f"data/fichiers_csv/du papier/{name}"
        graph, actives, passives = read_unoriented_from_csv(path)

        area, x, mean, std = run_random(graph, actives, passives, name)
        curves["random"][name] = (x, mean, std)
        results["random"][name] = (area, 0.0)

        for s in STRATEGIES:
            area, t, x, y = delete_nodes_result(graph, actives, passives,
                                                s, show_plots, name)
            curves[s][name] = (x, y)
            results[s][name] = (area, t)
            print(f"{name} | {s}: area = {area:.4f} | time = {t:.6f}s")

    # the grid shows a few representative networks; the heatmap shows all of them
    plot_curve_grid(curves, DATASETS[:4], "results/curves_grid.png")
    plot_heatmap(results, "results/heatmap.png")


if __name__ == "__main__":
    main()