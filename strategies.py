import math

from tools import*

# ------------------------------------------------------- 
# -------------- Stratégies de suppression --------------

# ------ RANDOM ------
def delete_random(graphe : Dict[int, List[int]], ns : int) -> Dict[int, List[int]]: 
    """Supprime 'ns' noeuds du graphe de manière aléatoire en renvoyant un graphe correspondant (pas de modification)"""
    res = copy.deepcopy(graphe)
    for _ in range(ns) : 
        rdm = random.choice(list(res.keys())) #choix du node target à supprimer du graphe
        voisins = res[rdm]
        res.pop(rdm)
        for node in voisins : #on supprime le noeud target des listes de ses voisins
            res[node].remove(rdm)
    return res 

def delete_random(graph : Dict[int, List[int]], ns : int) -> Dict[int, List[int]]: 
    """Supprime 'ns' noeuds du graphe de manière aléatoire"""
    for _ in range(ns) : 
        rdm = random.choice(list(graph.keys())) #choix du node target à supprimer du graphe
        voisins = graph[rdm]
        graph.pop(rdm)
        for node in voisins : #on supprime le noeud target des listes de ses voisins
            graph[node].remove(rdm)
    return graph 


# ----- CENTRALITE DE DEGRE -----
def degree_centrality(graph : Dict[int, List[int]]) -> List[int] :
    """ Renvoie une liste des sommets du graphe triés par ordre décroissant de leur degré. """
    brut = list(zip(graph.keys(), graph.values()))
    triees = sorted(brut, key=lambda x: len(x[1]), reverse=True)
    nodes, neighbors = zip(*triees)
    return nodes

def delete_degree_nodes(graph : Dict[int, List[int]], n : int) -> Dict[int, List[int]] :
    """ Renvoie un graphe corresponsant à graph où les n sommets de degré le plus élevé ont été supprimés. """
    nodes = degree_centrality(graph)
    copie = copy.deepcopy(graph)
    for i in range(n) :
        delete_node_from_graph(copie, nodes[i])
    return copie

def delete_degree_nodes_incremental(graph : Dict[int, List[int]], n : int) -> Dict[int, List[int]] :
    """ Renvoie graph modifié où les n sommets de degré le plus élevé ont été supprimés. """
    nodes = degree_centrality(graph)
    for i in range(n) :
        delete_node_from_graph(graph, nodes[i])
    return graph


# ------ CENTRALITE DE PROXIMITE ------
def closeness_centrality(graph : Dict[int, List[int]]) -> Dict[int, int]:
    """ Calcule la mesure de centralité de proximité de chaque noeuf du graphe """
    nb_sommets = len(graph)
    cc = dict()

    for node in graph :
        file = deque() # file pour le parcours des noeuds à partir de 'node'
        dist = dict()
        for v in graph :
            dist[v] = nb_sommets+1 # on utilise cette mesure pour simuler l'infini, c'est suffisant
        dist[node] = 0

        file.append(node)

        while len(file)!=0 :
            x = file.popleft()
            for neighbor in graph[x] : # on calcule la distance de chaque noeud au sommet origine
                if dist[neighbor] == nb_sommets+1 :
                    dist[neighbor] = dist[x] + 1
                    file.append(neighbor)

        # utilisation de la formule pour le calcul de la centralité de proximité du noeud origine
        somme = 0
        for v in graph :
            if v != node :
                somme += dist[v]
        cc[node] = 1/somme

    return cc


def order_closeness_centrality(graph : Dict[int, List[int]]) -> List[int]:
    """ Retourne une liste de noeuds ordonnés par centralité de proximité croissante """
    centralities = closeness_centrality(graph)
    brut = list(zip(centralities.keys(), centralities.values()))
    triees = sorted(brut, key=lambda x: x[1], reverse=True) # on trie par valeur de centralité décroissante
    nodes, centralities = zip(*triees)
    return nodes


def delete_closeness_nodes(graph : Dict[int, List[int]], n : int) -> Dict[int, List[int]] :
    """ Retourne un nouveau graphe (sous forme de matrice d'adjacence)
        à partir de graph dont les n noeuds à la plus grande centralité de proximité ont été supprimés
    """
    # ATTENTNION
    # Si cette opération est à réaliser plusieurs fois de suite sur le même graphe 
    # en faisant uniquement varier n mais sur le même graphe
    # utiliser la fonction 'delete_centrality_nodes_fast', plus rapide et efficace dans CE cas

    copie = copy.deepcopy(graph)
    nodes = order_closeness_centrality(graph) # les noeuds triés par ordre décroissant de centralité
    for i in range(n) :
        delete_node_from_graph(copie, nodes[i])
    return copie 

def delete_closeness_nodes_incremental(graph : Dict[int, List[int]], n : int) -> Dict[int, List[int]] :
    """ Supprime de graph les n noeuds à la plus grande centralité de proximité  """
    # ATTENTNION
    # Si cette opération est à réaliser plusieurs fois de suite sur le même graphe 
    # en faisant uniquement varier n mais sur le même graphe
    # utiliser la fonction 'delete_centrality_nodes_fast', plus rapide et efficace dans CE cas

    nodes = order_closeness_centrality(graph) # les noeuds triés par ordre décroissant de centralité
    for i in range(n) :
        delete_node_from_graph(graph, nodes[i])
    return graph 


# ------ CENTRALITE D'INTERMEDIARITE -----
def betweenness_centrality(graph : Dict[int, List[int]]) -> Dict[int, int] :
    """ Calcule les centralités d'intermédiarité de chaque noeud du graphe """
    cb = dict() # le dictionnaire des centralités pour chaque noeud, résultat renvoyé
    nb_sommets = len(graph)
    for node in graph : #initialisation du dictionnaire des betweenness centrality de chaque noeud 
        cb[node] = 0

    for node in graph :
        # ----- PHASE 1 : calcul du BFS et des sigma ----- 
        pile = deque()
        file = deque()

        distance = dict() # les degrés de chaque noeud
        sigma = dict()
        delta = dict()
        pre = dict()

        for v in graph : # initialisation des dictionnaires pour chaque sommet du graphe
            distance[v] = nb_sommets + 1 # on utilise sommet+1 pour représenter l'infini, c'est suffisant
            sigma[v] = 0
            delta[v] = 0
            pre[v] = set() 

        # initialisation des dictionnaires pour le sommet origine
        distance[node] = 0
        sigma[node] = 1

        file.append(node) # premier noeud à explorer

        while (len(file)!=0) :
            v = file.popleft() # on défile pour obtenir le noeud à étudier
            pile.append(v) # et on l'ajoute dans la pile

            for neighbor in graph[v] :
                if distance[neighbor] == nb_sommets : 
                    # maj de la distance au sommet origine 
                    distance[neighbor] = distance[v]+1
                    file.append(neighbor)

                if distance[neighbor] == distance[v]+1 :
                    # maj du nombre de plus courts chemins passant par le noeud
                    sigma[neighbor] += sigma[v]
                    pre[neighbor].add(v)

        # ----- PHASE 2 : remontée et calcul des delta ----- 
        
        while (len(pile)!=0) :
            w = pile.pop()
            for v in pre[w] :
                delta[v] += (sigma[v]/sigma[w]) * (1 + delta[w])
            if w != node :
                cb[w] += delta[w]

    for n in cb : 
        cb[n] = cb[n]/2 # graphe non-orienté chaque arrête est explorée 2 fois, on divise donc la centralité de chaque noeud par 2

    return cb 


def order_betweenness_centrality(graph : Dict[int, List[int]]) -> List[int] :
    """ Retourne les noeuds du graphe ordonnés par centralité d'intermédiarité décroissante """
    centralities = betweenness_centrality(graph)
    brut = list(zip(centralities.keys(), centralities.values()))
    triees = sorted(brut, key=lambda x: x[1], reverse=True)
    nodes, centralities = zip(*triees)
    return nodes


def delete_betweenness_nodes(graph : Dict[int, List[int]], n : int) -> Dict[int, List[int]]:
    """ Retourne un nouveau graphe (sous forme de matrice d'adjacence)
        à partir de graph dont les n noeuds à la plus grande centralité d'intermédiarité ont été supprimés
    """
    # ATTENTNION
    # Si cette opération est à réaliser plusieurs fois de suite sur le même graphe 
    # en faisant uniquement varier n mais pas le graphe, alors
    # utiliser la fonction 'delete_centrality_nodes_fast', plus rapide et efficace dans CE cas

    copie = copy.deepcopy(graph)
    nodes = order_betweenness_centrality(graph)
    for i in range(n) :
        delete_node_from_graph(copie, nodes[i])
    return copie

def delete_betweenness_nodes_incremental(graph : Dict[int, List[int]], n : int) -> Dict[int, List[int]]:
    """ Retourne un nouveau graphe (sous forme de matrice d'adjacence)
        à partir de graph dont les n noeuds à la plus grande centralité d'intermédiarité ont été supprimés
    """
    # ATTENTNION
    # Si cette opération est à réaliser plusieurs fois de suite sur le même graphe 
    # en faisant uniquement varier n mais pas le graphe, alors
    # utiliser la fonction 'delete_centrality_nodes_fast', plus rapide et efficace dans CE cas

    nodes = order_betweenness_centrality(graph)
    for i in range(n) :
        delete_node_from_graph(graph, nodes[i])
    return graph


# ------ MUSRANK (papier référencé) -----

def musrank_centrality(graph : Dict[int, List[int]], actives : Set[int], passives : Set[int], max_iter=1000, tol=1e-8) -> Tuple[Dict[int, float], Dict[int, float]]:
    """ Calcule les centralités de MusRank de chaque noeud du graphe """

    if not actives or not passives:
        raise ValueError("Both partitions must contain at least one node.")

    # initialisation
    importance = {u: 1.0 for u in actives}
    vulnerability = {v: 1.0 for v in passives}

    for _ in range(max_iter):
        # Mise à jour des centralités
        new_importance = {
            a: sum(vulnerability[p] for p in graph[a] if p in passives)
            for a in actives
        }
        new_vulnerability = {
            p: 1.0 / sum(
                1.0 / importance[a] for a in graph[p] if a in actives
            )
            if any(a in actives for a in graph[p]) else 0.0
            for p in passives
        }

        # Normalisation par la moyenne
        mean_I = sum(new_importance.values()) / len(actives)
        mean_V = sum(new_vulnerability.values()) / len(passives) 

        if mean_I > 0:
            new_importance = {a: I / mean_I for a, I in new_importance.items()}
        if mean_V > 0:
            new_vulnerability = {p: V / mean_V for p, V in new_vulnerability.items()}

        # Vérification de la convergence
        diff_I = max(
            (abs(new_importance[a] - importance[a]) for a in actives),
            default=0.0
        )

        diff_V = max(
            (abs(new_vulnerability[p] - vulnerability[p]) for p in passives),
            default=0.0
        )
        # si la différence maximale est inférieure à la tolérance, on arrête l'itération
        diff = max(diff_I, diff_V)

        importance = new_importance
        vulnerability = new_vulnerability

        if diff < tol:
            break
    
    return importance, vulnerability
    

def order_musrank_centrality(graph : Dict[int, List[int]]) -> List[int] :
    """ Retourne les noeuds du graphe ordonnés par centralité de MusRank décroissante """
    actives, passives = get_partitions(graph)
    importance, vulnerability = musrank_centrality(graph, actives, passives)
    brut = list(zip(importance.keys(), importance.values()))
    triees = sorted(brut, key=lambda x: x[1], reverse=True)
    return [node for node, score in triees]


def order_musrank_centrality_reversed(graph : Dict[int, List[int]]) -> List[int] :
    """ Retourne les noeuds passifs du graphe ordonnés par centralité de MusRank décroissante """
    actives, passives = get_partitions(graph)
    importance, vulnerability = musrank_centrality(graph, passives, actives)
    brut = list(zip(importance.keys(), importance.values()))
    triees = sorted(brut, key=lambda x: x[1], reverse=True)
    return [node for node, score in triees]


def delete_musrank_nodes_incremental( graph: Dict[int, List[int]], n: int) -> Dict[int, List[int]]:
    """
    Supprime les n noeudsayant la plus grande importance MusRank de graph. """

    copie = copy.deepcopy(graph)

    # Get nodes ordered by decreasing MusRank importance
    nodes = order_musrank_centrality(graph)

    for i in range(min(n, len(nodes))):
        delete_node_from_graph(copie, nodes[i])

    return copie


# ----- CENTRALITE DE PAGERANK -----
def pagerank_centrality(graph : Dict[int, List[int]], alpha=0.85, max_iter=100, tol=1e-6) -> Dict[int, float]:
    """ Calcule les centralités de PageRank de chaque noeud du graphe """
    n = len(graph)
    if n == 0:
        return {}

    # Initialisation
    pagerank = {node: 1.0 / n for node in graph}
    for _ in range(max_iter):
        new_pagerank = {}
        for node in graph:
            rank_sum = sum(pagerank[neighbor] / len(graph[neighbor]) for neighbor in graph if node in graph[neighbor])
            new_pagerank[node] = (1 - alpha) / n + alpha * rank_sum

        # Vérification de la convergence
        diff = sum(abs(new_pagerank[node] - pagerank[node]) for node in graph)
        pagerank = new_pagerank
        if diff < tol:
            break

    return pagerank

def order_pagerank_centrality(graph : Dict[int, List[int]]) -> List[int]:
    """ Retourne les noeuds du graphe ordonnés par centralité de PageRank décroissante """
    centralities = pagerank_centrality(graph)
    brut = list(zip(centralities.keys(), centralities.values()))
    triees = sorted(brut, key=lambda x: x[1], reverse=True)
    return [node for node, score in triees]

def delete_pagerank_nodes(graph : Dict[int, List[int]], n : int) -> Dict[int, List[int]]:
    """ Retourne un nouveau graphe (sous forme de matrice d'adjacence)
        à partir de graph dont les n noeuds à la plus grande centralité de PageRank ont été supprimés
    """
    copie = copy.deepcopy(graph)
    nodes = order_pagerank_centrality(graph)
    for i in range(min(n, len(nodes))):
        delete_node_from_graph(copie, nodes[i])
    return copie

def delete_pagerank_nodes_incremental(graph : Dict[int, List[int]], n : int) -> Dict[int, List[int]]:
    """ Supprime les n noeuds à la plus grande centralité de PageRank de graph
    """
    nodes = order_pagerank_centrality(graph)
    for i in range(min(n, len(nodes))):
        delete_node_from_graph(graph, nodes[i])
    return graph


# ----- CENTRALITE DE VECTEUR -----
def eigenvector_centrality(graph : Dict[int, List[int]], max_iter=100, tol=1e-6) -> Dict[int, float]:
    """ Calcule les centralités de vecteur propre de chaque noeud du graphe """
    n = len(graph)
    if n == 0:
        return {}
    # Initialisation
    centrality = {node : 1.0/len(graph) for node in graph}

    # Itération de la méthode de la puissance
    for _ in range(max_iter):
        new_centrality = {node : 0.0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                new_centrality[neighbor] += centrality[node]

        # Normalisation
        try:
            s = 1.0/math.sqrt(sum(v**2 for v in new_centrality.values()))
        except ZeroDivisionError:
            s = 1.0
        for n in new_centrality:
            new_centrality[n] *= s

        # verifier la convergence
        diff = sum(abs(new_centrality[n] - centrality[n]) for n in centrality)
        centrality = new_centrality
        if diff < tol:
            break
    return centrality

def order_eigenvector_centrality(graph : Dict[int, List[int]]) -> List[int]:
    """ Retourne les noeuds du graphe ordonnés par centralité de vecteur propre décroissante """
    centralities = eigenvector_centrality(graph)
    brut = list(zip(centralities.keys(), centralities.values()))
    triees = sorted(brut, key=lambda x: x[1], reverse=True)
    return [node for node, score in triees]

def delete_eigenvector_nodes(graph : Dict[int, List[int]], n : int) -> Dict[int, List[int]]:
    """ Supprime les n noeuds à la plus grande centralité de vecteur propre de graph
    """
    nodes = order_eigenvector_centrality(graph)
    for i in range(min(n, len(nodes))):
        delete_node_from_graph(graph, nodes[i])
    return graph



# ----- COMMUN A TOUTES LES STRATEGIES POUR LE CLASSEMENT -----


def get_strategy_ranking(strategie : str, graph : Dict[int, List[int]], actives : Set[int], passives : Set[int]) -> List[int] :
    """ Donne un classement des noeuds en fonction de la mesure recherchée """

    match strategie : 
        case "random" :
            nodes = list(graph.keys())
            random.shuffle(nodes)
            return nodes

        case "degree" :
            return degree_centrality(graph)

        case "closeness" :
            return order_closeness_centrality(graph)

        case "betweenness" :
            return order_betweenness_centrality(graph)

        case "musrank" :
            return order_musrank_centrality(graph)

        case "pagerank" :
            return order_pagerank_centrality(graph)

        case "eigenvector" :
            return order_eigenvector_centrality(graph)