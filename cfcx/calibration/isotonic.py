import numpy as np
from sklearn.isotonic import IsotonicRegression


def fit_isotonic(raw_probs: list[float],
                 outcomes: list[int]) -> IsotonicRegression:
    """Entraîne un calibrateur isotonique.

    raw_probs : probabilités brutes prédites par le modèle
    outcomes  : résultats observés (1 = gagné, 0 = perdu)
    """
    if len(raw_probs) != len(outcomes):
        raise ValueError("raw_probs et outcomes doivent avoir la même taille")
    if len(raw_probs) < 10:
        raise ValueError("Au moins 10 échantillons nécessaires")

    x = np.array(raw_probs, dtype=float)
    y = np.array(outcomes, dtype=float)

    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    iso.fit(x, y)
    return iso


def apply_isotonic(iso: IsotonicRegression, raw_prob: float) -> float:
    """Applique le calibrateur à une probabilité brute."""
    val = float(iso.predict([raw_prob])[0])
    return max(0.0, min(1.0, val))


def brier_score(probs: list[float], outcomes: list[int]) -> float:
    """Brier Score = MSE entre probas et résultats. Plus bas = mieux."""
    if not probs:
        return 0.0
    p = np.array(probs, dtype=float)
    o = np.array(outcomes, dtype=float)
    return float(((p - o) ** 2).mean())


def log_loss(probs: list[float], outcomes: list[int],
             eps: float = 1e-15) -> float:
    """Log Loss (cross-entropy). Plus bas = mieux."""
    if not probs:
        return 0.0
    p = np.clip(np.array(probs, dtype=float), eps, 1 - eps)
    o = np.array(outcomes, dtype=float)
    return float(-(o * np.log(p) + (1 - o) * np.log(1 - p)).mean())


def ece(probs: list[float], outcomes: list[int], n_bins: int = 10) -> float:
    """Expected Calibration Error.

    Divise [0,1] en n_bins intervalles, compare la proba moyenne prédite
    avec le taux de réussite observé dans chaque intervalle.
    """
    if not probs:
        return 0.0
    p = np.array(probs, dtype=float)
    o = np.array(outcomes, dtype=float)
    bins = np.linspace(0, 1, n_bins + 1)
    n = len(p)
    total = 0.0
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = (p >= lo) & (p < hi if i < n_bins - 1 else p <= hi)
        if mask.sum() == 0:
            continue
        avg_p = p[mask].mean()
        avg_o = o[mask].mean()
        total += (mask.sum() / n) * abs(avg_p - avg_o)
    return float(total)
