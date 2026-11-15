# Robustesse des réseaux bipartis

#### Projet réalisé par [@Inès BENAMER-BELKACEM](https://github.com/ines-benamer), [@Thibaut MARCQ](https://github.com/thibautmarcq) et [@Mélissa SETBEL](https://github.com/mSETBEL)

## Introduction

Ce projet a pour but d'étudier la **robustesse des réseaux bipartis** en analysant l'influence du retrait d'une partie des noeuds sur le reste.

Pour ce, on compare différentes méthodes de classement de nœuds et évaluons leur impact sur un graphe.


## Architecture du projet

Le code source est organisé de la manière suivante :
- **`main.py`** : Script principal qui exécute l'ensemble des stratégies sur les jeux de données, génère les grilles de courbes d'extinction et la heatmap des gains relatifs.
- **`strategies.py`** : Implémentation des différentes mesures de centralité et stratégies d'attaque.
- **`musrank_log.py`** : Implémentation de l'algorithme *MusRank* en échelle logarithmique (via `logsumexp`) pour éviter les erreurs d'underflow et de division par zéro.
- **`adaptive_musrank.py`** : Implémentation de la variante *MusRank adaptatif*, où le classement est recalculé dynamiquement après chaque suppression de nœud actif.
- **`analyse_resultats.py`** : Fonctions de simulation des suppressions par paliers et calcul de l'aire sous la courbe.
- **`tools.py`** : Fonctions utilitaires de manipulation des graphes (chargement de fichiers, composantes connexes, recherche de la GCC, nettoyage des nœuds isolés).
- **Scripts de benchmark** : `compare_exec_time.py`, `compare_musrank.py` et `compare_musrank_exec_time.py` pour l'analyse des performances temporelles.

## Structures de données

Un graphe est représenté avec des listes d'adjacences :

```python
Dict[int, List[int]]
```

où chaque nœud est associé à la liste de ses nœuds voisins.
On maintient de plus pour chaque noeud les ensembles des noeuds actifs et passifs, utiles pour l'étude des effets de la suppression d'une espèce.

## Stratégies implémentées

Nous implémentons plusieurs stratégies de classements des noeuds actifs à supprimer proposés par un papier :

- **Aléatoire :** Nœuds choisis aléatoirement.
- **Centralité de degré :** Nœuds avec degrés décroissants.
- **Centralité de proximité (Closeness) :** Nœuds avec centralité de proximité décroissantes.
- **Centralité d'intermediarité (Betweenness) :** Nœuds avec centralité de intermediarité décroissantes.
- **Vecteur propre (eigenvector) et PageRank:** Classements de nœuds relatifs à l'importance de ses voisins.
- **Imbrication (nestedness) :** Nœuds participant à la structure imbriquée du réseau.
- **MusRank :** Classement de nœuds en utilisant l'algorithme Musrank conçu pour les graphes bipartis.
- **MusRank inversé :** Variante appliquée sur la partition passive pour évaluer le classement opposé de la même centralité.

De plus, nous offrons une nouvelle stratégie **Nestedness** qui prend en compte les degrés des voisins d'un nœud afin de lui attribuer un score.

## Utilisation 

### Prérequis
Les bibliothèques Python suivantes sont nécessaires à l'utilisation du code de ce projet :
```bash
pip install numpy matplotlib
```

### Lancer l'analyse complète
Pour exécuter les simulations sur tous les jeux de données et générer les graphiques de résultats dans le dossier `results/` :
```bash
python main.py
```

### Lancer les benchmarks de performance
Pour analyser les temps de calcul des différentes stratégies :
```bash
python compare_exec_time.py
```
Pour comparer les variantes de l'algorithme MusRank :
```bash
python compare_musrank.py
python compare_musrank_exec_time.py
```