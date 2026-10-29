from collections import deque
from typing import Dict, List, Tuple
import random
import copy

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
# -------------- Stratégies de suppression --------------

def delete_random(graphe : Dict[int, List[int]], ns : int) -> Dict[int, List[int]]: 
    """Supprime 'ns' noeuds du graphe de manière aléatoire"""
    res = copy.deepcopy(graphe)
    for _ in range(ns) : 
        rdm = random.choice(list(res.keys())) #choix du node target à supprimer du graphe
        voisins = res[rdm]
        res.pop(rdm)
        for node in voisins : #on supprime le noeud target des listes de ses voisins
            res[node].remove(rdm)
    return res 
