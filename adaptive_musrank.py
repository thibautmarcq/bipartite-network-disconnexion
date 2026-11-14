from time import time
from tools import *
from strategies import *
from constants import *

# ------ POUR L'ANALYSE DES RESULTATS DU MUSRANK ADAPTIF ------

def adaptive_musrank_result(graph: Dict[int, List[int]],actives: Set[int], passives: Set[int],affichage: bool, graph_name: str) -> Tuple[float, float]:
    """
    Donne l'aire du graphique d'extinction pour la stratégie MusRank adaptative
    et enregistre le graphique correspondant.

    Le classement MusRank est recalculé après chaque suppression d'un noeud actif.
    """

    nb_actives = len(actives)
    nb_passives = len(passives)

    if nb_actives == 0 or nb_passives == 0:
        raise ValueError("Le graphe doit contenir des noeuds actifs et passifs.")

    # Définition des paliers de suppression
    if nb_actives < 10:
        cibles_actives_supprimees = list(range(1, nb_actives + 1))
    else:
        cibles_actives_supprimees = [
            math.ceil(palier * nb_actives / 10)
            for palier in range(1, 11)
        ]

    proportion_actives_supp = [0.0] + [
        cible / nb_actives for cible in cibles_actives_supprimees
    ]

    # Proportion initiale de passives déjà éteintes
    proportion_passives_eteintes = [
        sum(not graph.get(node) for node in passives) / nb_passives
    ]
    copie = copy.deepcopy(graph)

    temps_classement = 0.0
    nb_actives_supprimees = 0

    # Suppression adaptative
    for cible in cibles_actives_supprimees:

        while nb_actives_supprimees < cible:

            actives_restantes = {
                node for node in actives if node in copie
            }

            passives_restantes = {
                node for node in passives if node in copie
            }

            if not actives_restantes:
                break

            debut = time()

            # Recalcul de MusRank sur le graphe actuel
            ranking = get_strategy_ranking(
                "musrank",
                copie,
                actives_restantes,
                passives_restantes
            )

            temps_classement += time() - debut # Addition du temps de classement pour chaque recalcul

            if not ranking:
                break

            # Suppression du noeud actif le mieux classé
            noeud = ranking[0]

            delete_node_from_graph(copie, noeud)
            nb_actives_supprimees += 1

            clear_graph(copie)

        # Mesure de l'extinction des noeuds passifs
        passives_left = count_passives(copie, passives)

        proportion_passives_eteintes.append(
            1 - (passives_left / nb_passives)
        )

    # Calcul de l'aire sous la courbe (méthode des trapèzes)
    aire_totale = 0.0

    for i in range(len(proportion_actives_supp) - 1):
        largeur = (
            proportion_actives_supp[i + 1]
            - proportion_actives_supp[i]
        )

        hauteur_moyenne = (
            proportion_passives_eteintes[i]
            + proportion_passives_eteintes[i + 1]
        ) / 2

        aire_totale += largeur * hauteur_moyenne

    # Affichage et sauvegarde du graphique
    # plt.figure(figsize=(8, 5))

    # plt.plot(
    #     proportion_actives_supp,
    #     proportion_passives_eteintes,
    #     marker='.',
    #     color='blue'
    # )

    # plt.xlabel("Proportion de noeuds actifs supprimés")
    # plt.ylabel("Proportion d'espèces passives éteintes")

    # plt.title(
    #     "Extinction des espèces passives selon MusRank adaptatif"
    # )

    # plt.grid(True)

    # filename = "results/" + graph_name + "_musrank_adaptive"

    # plt.savefig(filename, dpi=300, bbox_inches='tight')

    # if affichage:
    #     plt.show()

    # plt.close()

    return aire_totale, temps_classement
