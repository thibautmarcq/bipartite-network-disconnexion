from tools import *
from strategies import *
from constants import *

# ------  POUR L'ANALYSE DES RESULTATS ------

def delete_nodes_result(graph : Dict[int, List[int]], actives : Set[int], passives : Set[int], strategie : str, affichage : bool, graph_name : str) -> float :
    """ Donne l'aire du graphique d'extinction d'un graphe donné pour une certaine stratégie, et enregistre le graphique correspondant à la courbe d'exctinction. """
    nb_actives = len(actives)
    nb_passives = len(passives)

    if nb_actives == 0 or nb_passives == 0:
        raise ValueError("Le graphe doit contenir des noeuds actifs et passifs.")

    if nb_actives < 10:
        # si le graphe est trop petit (moins de 10 noeufs actifs), on fait un palier par noeud
        cibles_actives_supprimees = list(range(1, nb_actives + 1))
    else:
        # sinon, on se donne 10 paliers en incluant la suppression totale
        cibles_actives_supprimees = [
            math.ceil(palier * nb_actives / 10) for palier in range(1, 11)
        ]
    proportion_actives_supp = [0.0] + [
        cible / nb_actives for cible in cibles_actives_supprimees
    ]
    proportion_passives_restants = [
        sum(not graph.get(node) for node in passives) / nb_passives
    ]

    copie = copy.deepcopy(graph) # graphe qu'on va peu à pau modifier sur place, pour éviter de multiplier les calculs en recommençant à chaque fois
    sorted_nodes = get_strategy_ranking(strategie, graph, actives, passives) # l'ordre des noeuds obtenu pour la stratégie donnée

    index = 0 # l'index représentant l'avancement des noeuds consommés dans la suppression par incréments 
    nb_actives_supprimees = 0
    for cible in cibles_actives_supprimees:
        # Pour tous les incréments de pas décidés, on augmente la population d'espèces actives supprimées
        index += delete_active_nodes_fast_incremental(copie, cible - nb_actives_supprimees, sorted_nodes[index:], actives)
        nb_actives_supprimees = cible
        clear_graph(copie) # On s'assure que le graphe soit proprement modifié
        passives_left = count_passives(copie, passives)
        proportion_passives_restants.append(1 - (passives_left/nb_passives))

    aire_totale = 0
    for i in range(len(proportion_actives_supp) - 1):
        largeur = proportion_actives_supp[i+1] - proportion_actives_supp[i]
        hauteur_moyenne = (proportion_passives_restants[i] + proportion_passives_restants[i+1]) / 2
        aire_totale += largeur * hauteur_moyenne


    # print(aire_totale)

    plt.figure(figsize=(8, 5))
    plt.plot(proportion_actives_supp, proportion_passives_restants, marker='.', color='blue')
    plt.xlabel("Proportion de noeuds actifs supprimés")
    plt.ylabel("Proportion d'espèces passives éteintes")
    plt.title(f"Extinction des espèces passives selon la stratégie {strategie}")
    plt.grid(True)
    filename = "results/"+graph_name+"_"+strategie
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    if affichage : 
        plt.show()

    return aire_totale
