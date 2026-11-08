from tools import *
from strategies import *
from constants import *
from analyse_resultats import *

# dans ce fichier, uniquement mettre le code qui 
# permet de tester les résultats des différentes stratégies, par exemple les plots 

affichage = True
graph, actives, passives = read_unoriented_from_csv("data/fichiers_csv/du papier/mosquin")
delete_nodes_result(graph, actives, passives, "closeness", affichage)
delete_nodes_result(graph, actives, passives, "eigenvector", affichage)
delete_nodes_result(graph, actives, passives, "betweenness", affichage)
delete_nodes_result(graph, actives, passives, "degree", affichage)
delete_nodes_result(graph, actives, passives, "pagerank", affichage)
