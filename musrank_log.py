"""
MusRank calculé en échelle logarithmique.

Pourquoi : l'itération MusRank (famille « fitness-complexity ») fait décroître vers 0 la valeur de
nombreux noeuds. Avec des flottants ordinaires, ces valeurs finissent par sous-dépasser (1e-308 -> 0.0)
et `1.0 / importance[a]` lève ZeroDivisionError. En travaillant sur log(importance) et log(vulnérabilité),
plus aucune valeur ne peut atteindre 0 : pas d'erreur, et l'ordre entre noeuds « minuscules » est conservé.

Remplace `musrank_centrality` dans strategies.py (même signature, mêmes deux dictionnaires en sortie).
ATTENTION : les valeurs retournées sont des LOGARITHMES. Le tri (croissant ou décroissant) donne le même
ordre que sur les valeurs brutes, donc `order_musrank_centrality` n'a pas à changer.
Les noeuds sans voisin vivant reçoivent -inf.
"""
from typing import Dict, List, Set, Tuple
import numpy as np


def _lse(x: np.ndarray, axis: int) -> np.ndarray:
    """log(sum(exp(x))) stable ; renvoie -inf pour une tranche entièrement à -inf."""
    m = np.max(x, axis=axis, keepdims=True)
    m_safe = np.where(np.isfinite(m), m, 0.0)
    with np.errstate(divide="ignore"):
        return np.log(np.sum(np.exp(x - m_safe), axis=axis)) + np.squeeze(m_safe, axis=axis)


def musrank_centrality(graph: Dict[int, List[int]], actives: Set[int], passives: Set[int],
                       max_iter: int = 2000, stable_iters: int = 30
                       ) -> Tuple[Dict[int, float], Dict[int, float]]:
    """Retourne (log_importance des actifs, log_vulnérabilité des passifs).

    Arrêt : quand le classement n'a pas changé pendant `stable_iters` itérations consécutives
    (et non quand les valeurs se stabilisent : les valeurs des noeuds qui tendent vers 0 ne se
    stabilisent jamais, seul leur classement converge).
    """
    log_I = {a: -np.inf for a in actives}
    log_V = {p: -np.inf for p in passives}

    # noeuds ayant au moins un voisin vivant
    A = [a for a in actives if any(p in passives for p in graph[a])]
    P = [p for p in passives if any(a in actives for a in graph[p])]
    if not A or not P:
        return log_I, log_V

    ia = {a: i for i, a in enumerate(A)}
    ip = {p: j for j, p in enumerate(P)}
    M = np.full((len(A), len(P)), -np.inf)      # 0 s'il y a une arête, -inf sinon
    for a in A:
        for p in graph[a]:
            if p in ip:
                M[ia[a], ip[p]] = 0.0

    lI = np.zeros(len(A))
    lV = np.zeros(len(P))
    prev_rank, stable = None, 0
    for _ in range(max_iter):
        new_lI = _lse(M + lV[None, :], axis=1)              # importance = somme des vulnérabilités
        new_lV = -_lse(M.T - new_lI[None, :], axis=1)       # vulnérabilité = 1 / somme des 1/importance
        # normalisation par la moyenne (constante additive en log)
        new_lI -= _lse(new_lI, axis=0) - np.log(len(A))
        new_lV -= _lse(new_lV, axis=0) - np.log(len(P))
        lI, lV = new_lI, new_lV

        # arrondi : deux noeuds équivalents ont le même score ; sans arrondi, le bruit flottant (~1e-16)
        # changerait leur ordre à chaque itération
        rank = (tuple(np.argsort(-np.round(lI, 8), kind="stable")),
                tuple(np.argsort(-np.round(lV, 8), kind="stable")))
        stable = stable + 1 if rank == prev_rank else 0
        prev_rank = rank
        if stable >= stable_iters:
            break

    for a in A:
        log_I[a] = float(np.round(lI[ia[a]], 8))
    for p in P:
        log_V[p] = float(np.round(lV[ip[p]], 8))
    return log_I, log_V