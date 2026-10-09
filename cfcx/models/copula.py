import numpy as np
from scipy.stats import norm, multivariate_normal


def sample_gaussian_copula(rho: float, n: int,
                           seed: int | None = None) -> np.ndarray:
    """Génère n paires (u, v) uniformes [0,1] selon une copule gaussienne
    de paramètre rho."""
    rho = max(-0.999, min(0.999, rho))
    cov = np.array([[1.0, rho], [rho, 1.0]])
    rng = np.random.default_rng(seed)
    z = rng.multivariate_normal([0, 0], cov, size=n)
    u = norm.cdf(z[:, 0])
    v = norm.cdf(z[:, 1])
    return np.column_stack([u, v])


def copula_prob(rho: float, f1_ge: float, f2_ge: float) -> float:
    """Probabilité jointe P(C1 >= a AND C2 >= b) via copule gaussienne.

    f1_ge = P(C1 >= a) marginal
    f2_ge = P(C2 >= b) marginal
    On utilise l'approximation : seuil sur la normale inverse.
    """
    rho = max(-0.999, min(0.999, rho))
    if f1_ge <= 0 or f2_ge <= 0:
        return 0.0
    if f1_ge >= 1:
        return f2_ge
    if f2_ge >= 1:
        return f1_ge

    z1 = norm.ppf(1 - f1_ge)
    z2 = norm.ppf(1 - f2_ge)

    cov = np.array([[1.0, rho], [rho, 1.0]])
    mvn = multivariate_normal(mean=[0, 0], cov=cov)
    return float(mvn.cdf([-z1, -z2]))


def sample_joint(c1_dist: np.ndarray, c2_dist: np.ndarray,
                 rho: float, n: int,
                 seed: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Échantillonne (C1, C2) à partir des distributions marginales et d'une
    copule gaussienne.

    c1_dist[k] = P(C1 = k)
    c2_dist[k] = P(C2 = k)
    """
    uv = sample_gaussian_copula(rho, n, seed=seed)
    u = uv[:, 0]
    v = uv[:, 1]

    c1_vals = _inv_cdf(c1_dist, u)
    c2_vals = _inv_cdf(c2_dist, v)
    return c1_vals, c2_vals


def _inv_cdf(dist: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Inverse la CDF discrète : transforme des uniforms en valeurs entières."""
    cdf = np.cumsum(dist)
    cdf = cdf / cdf[-1] if cdf[-1] > 0 else cdf
    out = np.searchsorted(cdf, u, side="right")
    return out.astype(int)
