import numpy as np
from scipy.stats import nbinom


def _params(mean: float, dispersion: float) -> tuple[float, float]:
    """Convertit (moyenne, dispersion) en paramètres (n, p) de scipy.

    dispersion > 1 => surdispersion (variance > moyenne).
    dispersion = 1 => équivalent à Poisson.
    """
    if dispersion <= 0:
        dispersion = 1.0
    p = dispersion / (dispersion + mean)
    n = dispersion
    return n, p


def pmf(mean: float, dispersion: float, k: int) -> float:
    """Probabilité P(C = k) sous une Negative Binomial."""
    n, p = _params(mean, dispersion)
    return float(nbinom.pmf(k, n, p))


def cdf(mean: float, dispersion: float, k: int) -> float:
    """Probabilité P(C <= k)."""
    n, p = _params(mean, dispersion)
    return float(nbinom.cdf(k, n, p))


def p_ge(mean: float, dispersion: float, k: int) -> float:
    """Probabilité P(C >= k)."""
    if k <= 0:
        return 1.0
    n, p = _params(mean, dispersion)
    return float(1.0 - nbinom.cdf(k - 1, n, p))


def sample(mean: float, dispersion: float, n: int,
           seed: int | None = None) -> np.ndarray:
    """Génère n échantillons d'une Negative Binomial."""
    n_param, p = _params(mean, dispersion)
    rng = np.random.default_rng(seed)
    return rng.negative_binomial(n_param, p, size=n)


def pmf_vector(mean: float, dispersion: float, kmax: int = 30) -> np.ndarray:
    """Retourne toute la distribution de 0 à kmax."""
    n, p = _params(mean, dispersion)
    return nbinom.pmf(np.arange(kmax + 1), n, p)
