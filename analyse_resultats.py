from tools import *
from strategies import *
from constants import *

# ------  POUR L'ANALYSE DES RESULTATS ------

def delete_nodes_result(graph : Dict[int, List[int]], actives : Set[int], passives : Set[int], strategie : str, affichage : bool) -> float :
    """ Donne l'aire du graphique d'extinction d'un graphe donné pour une certaine stratégie. """
    nb_actives = len(actives)
    nb_passives = len(passives)

    if nb_actives < 10:
        # si le graphe est trop petit (moins de 10 noeufs actifs), on fait un palier par noeud
        pas = 1
        proportion_actives_supp = [i / nb_actives for i in range(nb_actives + 1)]
    else:
        # sinon, on se donne 10 paliers 
        pas = math.floor(nb_actives / 10)
        proportion_actives_supp = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    proportion_passives_restants = [0.0] # liste où on va stocker les résultats qui nous intéressent, la proportion de noeuds actifs restants après suppression

    copie = copy.deepcopy(graph) # graphe qu'on va peu à pau modifier sur place, pour éviter de multiplier les calculs en recommençant à chaque fois
    sorted_nodes = get_strategy_ranking(strategie, graph, actives, passives) # l'ordre des noeuds obtenu pour la stratégie donnée

    index = 0 # l'index représentant l'avancement des noeuds consommés dans la suppression par incréments 
    for i in proportion_actives_supp[1:] :
        # Pour tous les incréments de pas décidés, on augmente la population d'espèces actives supprimées
        index += delete_active_nodes_fast_incremental(copie, pas, sorted_nodes[index:], actives, passives)
        clear_graph(copie) # On s'assure que le graphe soit proprement modifié
        passives_left = count_passives(copie, passives)
        proportion_passives_restants.append(1 - (passives_left/nb_passives))

    aire_totale = 0
    for i in range(len(proportion_actives_supp) - 1):
        largeur = proportion_actives_supp[i+1] - proportion_actives_supp[i]
        hauteur_moyenne = (proportion_passives_restants[i] + proportion_passives_restants[i+1]) / 2
        aire_totale += largeur * hauteur_moyenne

    print(aire_totale)

    if affichage : 
        plt.figure(figsize=(8, 5))
        plt.plot(proportion_actives_supp, proportion_passives_restants, marker='.', color='blue')

        plt.xlabel("Proportion de noeuds actifs supprimés")
        plt.ylabel("Proportion de noeuds passifs restants ")
        plt.title(("Evolution de la proportion d'espèces passives restantes en fonction de la proportion d'espèces actives supprimées selon la stratégie", strategie))
        plt.legend()
        plt.grid(True)
        plt.show()

    return aire_totale
