from collections import deque
from typing import Dict, List, Set, Tuple
import matplotlib.pyplot as plt
import numpy as np
import random
import copy
import math

# Fonctions outils utiles, dans ce fichier pour ne pas encombrer les fichiers de fonctions principales


def read_unoriented(file : str) -> Dict[int, List[int]] :
    dict = {}
    with open(file) as f:
        for line in f:
            if line[0] == "%" :
                continue
            (key, val) = line.split()[0:2] #
            key = int(key)
            val = int(val)
            if key not in dict:
                dict[key] = list()
            dict[key].append(val)
            if val not in dict:
                dict[val] = list()
            dict[val].append(key)
    return dict


def read_unoriented_from_csv(filename : str) -> Tuple[Dict[int, List[int]], Set[int], Set[int]] :
    """ Produit un graphe ainsi que les listes de ses composantes passives et passives à partir d'un fichier csv au format particulier """
    dict = {}
    passives = set()
    actives = set()
    with open(filename+"_edges.csv") as f:
        next(f)
        for line in f:
            if line[0] == "#" :
                continue
            (key, val) = line.split(",")[0:2] #
            key = int(key)
            val = int(val)
            if key not in dict:
                dict[key] = list()
            dict[key].append(val)
            if val not in dict:
                dict[val] = list()
            dict[val].append(key)

    with open(filename+"_nodes.csv") as f2 :
        next(f2)
        for line in f2 :
            if line[0] == "#" :
                continue
            termes = line.split(",") [0:4]
            node = int(termes[0])
            is_active = int(termes[1])
            if is_active > 0 :
                actives.add(node)
            else :
                passives.add(node)

    return dict, passives, actives

# ------------------------------------------------------- 

def composante_connexe(graphe: Dict[int, List[int]], sommet: int) -> set[int]:
    """Renvoie les sommets de la composante connexe de 'sommet'."""
    if sommet not in graphe:
        raise ValueError(f"Le sommet {sommet} n'appartient pas au graphe")

    visites = {sommet}
    file = deque([sommet])

    while file:
        courant = file.popleft()
        for voisin in graphe[courant]:
            if voisin not in visites:
                visites.add(voisin)
                file.append(voisin)

    return visites


def get_GCC(graphe : Dict[int, List[int]]) -> int:
    """Renvoie le plus grand composant connexe du graphe"""
    max_len = 0
    visited = set()
    for node in graphe.keys(): 
        if node not in visited :
            res = composante_connexe(graphe, node)
            length = len(res)
            if length >= max_len :
                max_len = length
            visited = visited.union(res)
            
    return max_len

# ------------------------------------------------------- 

def delete_node_from_graph(graph : Dict[int, List[int]], node) :
    """ Supprime un sommet donné d'un graphe, et retourne le graphe correspondant """
    for neighbor in graph[node] :
        graph[neighbor].remove(node)
    graph.pop(node)

def delete_centrality_nodes_fast(graph : Dict[int, List[int]], n : int, sorted_nodes : List[int]) -> Dict[int, List[int]] :
    """ Supprime n noeuds d'un graphe dans l'ordre de centralité donné par sorted_nodes 
        et retourne un graphe correspondant.
    """
    copie = copy.deepcopy(graph)
    # On prend  les n premiers noeuds du classement 
    nodes_to_remove = sorted_nodes[:n]
    for node in nodes_to_remove :
        delete_node_from_graph(copie, node)
    return copie

def delete_centrality_nodes_fast_incremental(graph : Dict[int, List[int]], n : int, sorted_nodes : List[int]) -> Dict[int, List[int]] :
    """ Supprime n noeuds d'un graphe dans l'ordre de centralité donné par sorted_nodes.
    """
    # On prend  les n premiers noeuds du classement 
    nodes_to_remove = sorted_nodes[:n]
    for node in nodes_to_remove :
        delete_node_from_graph(graph, node)
    return graph

def delete_active_nodes_fast_incremental(graph : Dict[int, List[int]], n : int, sorted_nodes : List[int], actives : Set[int], passives : Set[int]) -> Dict[int, List[int]] :
    """ Supprime de graph les n noeuds actifs les plus hauts dans le classement sorted_nodes """
    i = 0 
    # l'indice dans la liste des noeuds triés 
    for j in range(n): # boucle permettant de supprimer n noeuds actifs
        while sorted_nodes[i] not in actives : # on attend de trouver un noeud actif
            i+=1
        delete_node_from_graph(graph, sorted_nodes[i])
        i += 1
    return i


# -------------------------------------------------------

#utile pour differencier les noeuds "passifs" et "actifs" dans les graphes bipartis pour la stratégie MusRank
def get_partitions(graph: Dict[int, List[int]]) -> Tuple[Set[int], Set[int]]:
    A = set()
    B = set()

    color = {}

    for node in graph:
        if node in color:
            continue

        # Start a new connected component
        color[node] = 0
        queue = deque([node])

        while queue:
            u = queue.popleft()

            for v in graph[u]:
                if v not in color:
                    color[v] = 1 - color[u]
                    queue.append(v)

                elif color[v] == color[u]:
                    raise ValueError("Graph is not bipartite!")

    for node, c in color.items():
        if c == 0:
            A.add(node)
        else:
            B.add(node)

    return A, B


def clear_graph(graph : Dict[int, List[int]]) -> None :
    """ Supprime du graphe les noeuds qui n'ont aucun voisin (extinction)"""
    nodes = [node for node in graph]
    for node in nodes : 
        if len(graph[node])<1 :
            graph.pop(node)


def count_passives(graph : Dict[int, List[int]], passives : Set[int]) -> int :
    """ Retourne le nombre de noeuds passifs contenus dans le graph """
    i = 0
    for node in graph :
        if node in passives : 
            i+=1
    return i

