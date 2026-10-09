import numpy as np
from scipy.stats import poisson


def pmf(lam: float, k: int) -> float:
    """Probabilité P(C = k) pour une loi de Poisson de paramètre lambda."""
    return float(poisson.pmf(k, lam))


def cdf(lam: float, k: int) -> float:
    """Probabilité P(C <= k)."""
    return float(poisson.cdf(k, lam))


def p_ge(lam: float, k: int) -> float:
    """Probabilité P(C >= k)."""
    if k <= 0:
        return 1.0
    return float(1.0 - poisson.cdf(k - 1, lam))


def sample(lam: float, n: int, seed: int | None = None) -> np.ndarray:
    """Génère n échantillons d'une loi de Poisson."""
    rng = np.random.default_rng(seed)
    return rng.poisson(lam, size=n)


def pmf_vector(lam: float, kmax: int = 30) -> np.ndarray:
    """Retourne P(C = 0), P(C = 1), ..., P(C = kmax) sous forme de vecteur."""
    return poisson.pmf(np.arange(kmax + 1), lam)
