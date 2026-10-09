import numpy as np

from cfcx.models import poisson, neg_binomial
from cfcx.models.monte_carlo import simulate, total_distribution


def build_marginal(lam: float, dispersion: float = 1.0,
                   kmax: int = 30) -> np.ndarray:
    """Construit une distribution marginale P(C = k) pour k = 0..kmax.

    Si dispersion <= 1 -> Poisson.
    Sinon -> Negative Binomial (surdispersion).
    """
    if dispersion <= 1.0:
        return poisson.pmf_vector(lam, kmax)
    return neg_binomial.pmf_vector(lam, dispersion, kmax)


def joint_distribution(lam1: float, lam2: float,
                       dispersion1: float = 1.0,
                       dispersion2: float = 1.0,
                       rho: float = 0.0,
                       n_simulations: int = 10000,
                       seed: int | None = None) -> dict:
    """Construit la distribution jointe P(C1, C2) complète.

    Étapes :
    1. Construire les marginales P(C1) et P(C2).
    2. Simuler n paires via copule + Monte Carlo.
    3. Calculer les statistiques et tables de probabilités.
    """
    dist1 = build_marginal(lam1, dispersion1)
    dist2 = build_marginal(lam2, dispersion2)

    c1_samples, c2_samples = simulate(
        dist1, dist2, rho=rho, n=n_simulations, seed=seed
    )

    stats = total_distribution(c1_samples, c2_samples)

    return {
        "lam1": lam1,
        "lam2": lam2,
        "rho": rho,
        "n_simulations": n_simulations,
        "c1_samples": c1_samples,
        "c2_samples": c2_samples,
        "dist1": dist1,
        "dist2": dist2,
        "stats": stats,
    }


def estimate_rho_from_data(c1_hist: list[float],
                           c2_hist: list[float]) -> float:
    """Estime la corrélation rho entre C1 et C2 à partir de données historiques."""
    if len(c1_hist) < 3 or len(c1_hist) != len(c2_hist):
        return 0.0
    a = np.array(c1_hist, dtype=float)
    b = np.array(c2_hist, dtype=float)
    if a.std() == 0 or b.std() == 0:
        return 0.0
    rho = float(np.corrcoef(a, b)[0, 1])
    return max(-0.99, min(0.99, rho))
