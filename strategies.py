from tools import*

# ------------------------------------------------------- 
# -------------- Stratégies de suppression --------------

# ------ RANDOM ------
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


# ------ CENTRALITE D'INTERMEDIARITE -----
def betweenness_centrality(graph : Dict[int, List[int]]) -> Dict[int, int] :
    """ Calcule les centralités d'intermédiarité de chaque noeud du graphe """
    cb = dict() # le dictionnaire des centralités pour chaque noeud, résultat renvoyé
    nb_sommets = len(graph)
    for node in graph : #initialisation du dictionnaire des betwenness centrality de chaque noeud 
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


def order_betwenness_centrality(graph : Dict[int, List[int]]) -> List[int] :
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
    nodes = order_betwenness_centrality(graph)
    for i in range(n) :
        delete_node_from_graph(copie, nodes[i])
    return copie