# Robustesse des réseaux bipartis

## Introduction

Ce projet a pour but d'étudier la **robustesse des réseaux bipartis** en analysant leur connectivité lorsque des nœuds sont progressivement retirés.

Pour ce, on compare différentes méthodes de classement de nœuds et évaluons leur impact sur un graphe.

## Méthodologie

Un graphe est représenté avec des listes d'adjacences :

```python
Dict[int, List[int]]
```

Chaque nœud est associé à la liste de ses nœuds voisins.

## Stratégies implémentées

Pour le moments, les stratégies que nous avons implémenté sont:

- **Aléatoire :** Nœuds choisis aléatoirement.
- **Centralité de degré :** Nœuds avec degrés décroissants.
- **Centralité de proximité (Closeness) :** Nœuds avec centralité de proximité décroissantes.
- **Centralité d'intermediarité (Betweenness) :** Nœuds avec centralité de intermediarité décroissantes.
- **MusRank :** Classement de nœuds en utilisant l'algorithme Musrank conçu pour les graphes bipartis.
- **MusRank inversé :** Variante appliquée sur la partition passive pour évaluer le classement opposé de la même centralité.
- **Eigenvector :** Classement de nœud relatif à l'importance de ses voisins.

## Exp
