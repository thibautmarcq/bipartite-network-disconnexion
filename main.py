from tools import *
from strategies import *
from constants import *
from analyse_resultats import *

# dans ce fichier, uniquement mettre le code qui 
# permet de tester les résultats des différentes stratégies, par exemple les plots 

affichage = False
dataset_name = "woodland"
graph, actives, passives = read_unoriented_from_csv("data/fichiers_csv/du papier/"+dataset_name)
delete_nodes_result(graph, actives, passives, "closeness", affichage, dataset_name)
# for dataset in all_paper_datasets :
#     print("")
#     for strat in all_strategies :
#         copie = copy.deepcopy(graph)
#         delete_nodes_result(copie, actives, passives, strat, affichage, dataset)
delete_nodes_result(graph, actives, passives, "eigenvector", affichage, dataset_name)
delete_nodes_result(graph, actives, passives, "betweenness", affichage, dataset_name)
delete_nodes_result(graph, actives, passives, "degree", affichage, dataset_name)
delete_nodes_result(graph, actives, passives, "pagerank", affichage, dataset_name)
delete_nodes_result(graph, actives, passives, "musrank", affichage, dataset_name)
