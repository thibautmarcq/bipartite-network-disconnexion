from analyse_resultats import delete_nodes_result
from tools import read_unoriented_from_csv


def main() -> None:
    dataset_name = "alpine"
    show_plots = False
    dataset_path = f"data/fichiers_csv/du papier/{dataset_name}"
    strategies = (
        "closeness",
        "eigenvector",
        "betweenness",
        "degree",
        "pagerank",
        "musrank",
    )

    graph, active_species, passive_species = read_unoriented_from_csv(dataset_path)

    for strategy in strategies:
        extinction_area = delete_nodes_result(
            graph,
            active_species,
            passive_species,
            strategy,
            show_plots,
            dataset_name,
        )
        print(f"{strategy}: extinction curve area = {extinction_area:.4f}")


if __name__ == "__main__":
    main()
