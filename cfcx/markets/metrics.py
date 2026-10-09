import numpy as np


def mdi(probabilities: list[float]) -> float:
    """Model Disagreement Index.

    Écart-type des probabilités fournies par plusieurs modèles.
    Plus il est élevé, plus les modèles sont en désaccord.
    """
    if len(probabilities) < 2:
        return 0.0
    arr = np.array(probabilities, dtype=float)
    return float(arr.std())


def fi(probabilities_perturbed: list[float]) -> float:
    """Fragility Index.

    Écart-type des probabilités sous perturbations des entrées.
    Plus il est élevé, plus le marché est fragile.
    """
    if len(probabilities_perturbed) < 2:
        return 0.0
    arr = np.array(probabilities_perturbed, dtype=float)
    return float(arr.std())


def robustness(probabilities_perturbed: list[float],
               base_prob: float,
               tolerance: float = 0.05) -> float:
    """Robustesse d'un marché.

    Proportion de scénarios où la probabilité reste proche de la valeur de base
    (écart < tolerance).
    """
    if not probabilities_perturbed:
        return 0.0
    arr = np.array(probabilities_perturbed, dtype=float)
    ok = np.abs(arr - base_prob) <= tolerance
    return float(ok.sum() / len(arr))


def data_quality(matches_played: int,
                 freshness_days: float,
                 completeness: float,
                 target_matches: int = 10,
                 target_freshness: float = 14.0) -> float:
    """Data Quality score (0 à 1).

    Combine :
    - quantité de matchs disponibles (vs cible)
    - fraîcheur des données (jours depuis dernier match)
    - complétude (0 à 1, fournie en amont)
    """
    q = min(1.0, matches_played / target_matches) if target_matches > 0 else 0.0
    f = max(0.0, 1.0 - freshness_days / target_freshness) if target_freshness > 0 else 0.0
    c = max(0.0, min(1.0, completeness))

    return float((q + f + c) / 3.0)


def line_stability(dist: np.ndarray, line: float) -> float:
    """Line Stability autour d'une ligne.

    dist[k] = P(C = k)
    Retourne 1 - |P(C >= L+1) - P(C >= L)| pour L = int(line - 0.5).

    Une valeur proche de 1 indique une zone stable.
    """
    threshold = int(line + 0.5)
    total = dist.sum()
    if total <= 0:
        return 0.0
    cdf = np.cumsum(dist) / total
    if threshold >= len(cdf) or threshold <= 0:
        return 0.0
    p_ge_thr = 1.0 - cdf[threshold - 1]
    p_ge_next = 1.0 - cdf[threshold] if threshold < len(cdf) else 0.0
    return float(1.0 - abs(p_ge_thr - p_ge_next))


def consensus(probabilities: list[float], kappa: float = 3.0) -> float:
    """Score de consensus entre modèles, dans [0, 1].

    Formule : exp(-kappa * MDI)
    """
    m = mdi(probabilities)
    return float(np.exp(-kappa * m))
