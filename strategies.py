import math

from tools import*
from musrank_log import *

# ------------------------------------------------------- 
# -------------- Stratégies de suppression --------------

# ----- CENTRALITE DE DEGRE -----
def degree_centrality(graph : Dict[int, List[int]]) -> List[int] :
    """ Renvoie une liste des sommets du graphe triés par ordre décroissant de leur degré. """
    brut = list(zip(graph.keys(), graph.values()))
    triees = sorted(brut, key=lambda x: len(x[1]), reverse=True)
    nodes, neighbors = zip(*triees)
    return nodes


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
    """ Retourne une liste de noeuds ordonnés par centralité de proximité décroissante """
    centralities = closeness_centrality(graph)
    brut = list(zip(centralities.keys(), centralities.values()))
    triees = sorted(brut, key=lambda x: x[1], reverse=True) # on trie par valeur de centralité décroissante
    nodes, centralities = zip(*triees)
    return nodes


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
                if distance[neighbor] == nb_sommets+1 : 
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


def logsumexp(values):
    """Numerically stable calculation of log(sum(exp(values)))."""
    values = list(values)

    if not values:
        return -math.inf

    maximum = max(values)

    if maximum == -math.inf:
        return -math.inf

    if maximum == math.inf:
        return math.inf

    return maximum + math.log(
        math.fsum(math.exp(x - maximum) for x in values)
    )


def normalize_log_scores(scores):
    """Normalize scores so their arithmetic mean is 1."""
    if not scores:
        return scores

    log_sum = logsumexp(scores.values())

    if log_sum == -math.inf:
        return scores

    log_mean = log_sum - math.log(len(scores))

    return {
        node: value - log_mean if value != -math.inf else -math.inf
        for node, value in scores.items()
    }


# ------ MUSRANK (papier référencé) -----


def order_musrank_centrality(graph : Dict[int, List[int]], actives : Set[int], passives : Set[int]) -> List[int] :
    """ Retourne les noeuds du graphe ordonnés par centralité de MusRank décroissante """
    importance, vulnerability = musrank_centrality(graph, actives, passives)
    brut = list(zip(importance.keys(), importance.values()))
    triees = sorted(brut, key=lambda x: x[1], reverse=True)
    return [node for node, score in triees]


def order_musrank_centrality_reversed(graph : Dict[int, List[int]], actives : Set[int], passives : Set[int]) -> List[int] :
    """ Retourne les noeuds passifs du graphe ordonnés par centralité de MusRank décroissante """
    importance, vulnerability = musrank_centrality(graph, passives, actives)
    brut = list(zip(importance.keys(), importance.values()))
    triees = sorted(brut, key=lambda x: x[1], reverse=True)
    return [node for node, score in triees]


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

# ----- NEIGHBORHOOD -----
def neighborhood_centrality(graph : Dict[int, List[int]]) -> Dict[int, Tuple[int, ...]] :
    """ Calcule les centralité de cette manière :
    Priorité aux noeuds avec le plus de voisins de degré 1, puis aux noeuds avec le plus de voisins de degré 2, etc.
    Le score d'un noeud est le tuple (c1, c2, ..., cK) où ck = nombre de voisins de degré k.
    """
    # Calcul du degré de chaque noeud
    degree = {node: len(neighbors) for node, neighbors in graph.items()}
    max_degree = max(degree.values(), default=0)
 
    scores = {}
    for node, neighbors in graph.items():
        profile = [0] * max_degree
        for neighbor in neighbors:
            profile[degree[neighbor] - 1] += 1
        scores[node] = tuple(profile)
    return scores


def order_neighborhood_centrality(graph : Dict[int, List[int]]) -> List[int] :
    """ Retourne les noeuds du graphe ordonnés par la centralité de voisinage décroissante 
        En cas d'égalité, on prend le noeud avec le plus de voisins, puis le plus petit indice.
    """ 
    scores = neighborhood_centrality(graph)
    brut = list(zip(scores.keys(), scores.values()))
    triees = sorted(brut, key=lambda x: (x[1], len(graph[x[0]]), -x[0]), reverse=True)
    return [node for node, score in triees]

# ----- NESTEDNESS -----
def nestedness_centrality(graph : Dict[int, List[int]], actives : Set[int], passives : Set[int]) -> Dict[int, float] :
    """ Retourne les scores des noeuds du graphe obtenus par la centralité d'emboitement (nestedness) 
    """
    degree = {node: len(neighbors) for node, neighbors in graph.items()}
    inverse_sum = {}
    for p in passives :
        inverse_sum[p] = sum(1.0 / degree[a] for a in graph[p] if a in actives)

    contributions = {}
    for a in actives :
        if degree[a] == 0 :
            contributions[a] = float("inf")
        else :
            contributions[a] = sum(inverse_sum[p] for p in graph[a]) / degree[a]
    return contributions


def order_nestedness_centrality(graph : Dict[int, List[int]], actives : Set[int], passives : Set[int]) -> List[int] :
    """ Retourne les noeuds actifs ordonnés par contribution à la nestedness CROISSANTE
        (on retire d'abord ceux qui contribuent le moins). En cas d'égalité, le plus petit indice.
    """
    contributions = nestedness_centrality(graph, actives, passives)
    triees = sorted(contributions.items(), key=lambda x: (x[1], x[0]))
    return [node for node, score in triees]

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
            return order_musrank_centrality(graph, actives, passives)

        case "musrank_reversed" :
            return order_musrank_centrality_reversed(graph, actives, passives)

        case "pagerank" :
            return order_pagerank_centrality(graph)

        case "eigenvector" :
            return order_eigenvector_centrality(graph)

        case "neighborhood" :
            return order_neighborhood_centrality(graph)
        
        case "nestedness" : 
            return order_nestedness_centrality(graph, actives, passives)