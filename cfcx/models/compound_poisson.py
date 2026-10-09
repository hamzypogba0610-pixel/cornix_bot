import numpy as np


def pmf(lam: float, cluster_mean: float, kmax: int = 30) -> np.ndarray:
    """Probabilité P(C = k) sous un Compound Poisson.

    Modèle : C = somme de N clusters, N ~ Poisson(lam),
    chaque cluster apporte en moyenne `cluster_mean` corners.

    Approximation : on utilise une Negative Binomial équivalente.
    """
    from cfcx.models.neg_binomial import pmf_vector

    if lam <= 0:
        out = np.zeros(kmax + 1)
        out[0] = 1.0
        return out

    if cluster_mean <= 0:
        cluster_mean = 1.0

    mean = lam * cluster_mean
    dispersion = lam

    return pmf_vector(mean, dispersion, kmax)


def p_ge(lam: float, cluster_mean: float, k: int) -> float:
    """Probabilité P(C >= k) sous un Compound Poisson."""
    if k <= 0:
        return 1.0
    vec = pmf(lam, cluster_mean, kmax=max(k, 50))
    total = float(vec.sum())
    if total <= 0:
        return 0.0
    return float(vec[k:].sum() / total)


def mean(lam: float, cluster_mean: float) -> float:
    """Espérance du Compound Poisson."""
    return lam * cluster_mean


def variance(lam: float, cluster_mean: float) -> float:
    """Variance du Compound Poisson (approx. NB équivalente)."""
    mean_val = lam * cluster_mean
    return mean_val + (mean_val ** 2) / lam if lam > 0 else 0.0


def sample(lam: float, cluster_mean: float, n: int,
           seed: int | None = None) -> np.ndarray:
    """Génère n échantillons d'un Compound Poisson."""
    if lam <= 0 or cluster_mean <= 0:
        return np.zeros(n, dtype=int)
    rng = np.random.default_rng(seed)
    n_clusters = rng.poisson(lam, size=n)
    out = np.zeros(n, dtype=int)
    for i, nc in enumerate(n_clusters):
        if nc > 0:
            out[i] = int(rng.poisson(cluster_mean * nc))
    return out
