import numpy as np
from scipy.stats import poisson


DEFAULT_RHO = -0.05
DEFAULT_N_SIMULATIONS = 10000
DEFAULT_SEED = 42


def _dixon_coles_tau(h: int, a: int, lam_h: float, lam_a: float,
                     rho: float) -> float:
    """Facteur correctif Dixon-Coles pour les petits scores."""
    if h == 0 and a == 0:
        return 1.0 - lam_h * lam_a * rho
    if h == 0 and a == 1:
        return 1.0 + lam_h * rho
    if h == 1 and a == 0:
        return 1.0 + lam_a * rho
    if h == 1 and a == 1:
        return 1.0 - rho
    return 1.0


def score_matrix(lam_h: float, lam_a: float,
                 rho: float = DEFAULT_RHO,
                 kmax: int = 8) -> np.ndarray:
    """Construit la matrice P(score exact) pour tous les scores 0..kmax.

    Retourne une matrice (kmax+1) x (kmax+1).
    """
    h_vals = np.arange(kmax + 1)
    a_vals = np.arange(kmax + 1)

    p_h = poisson.pmf(h_vals, lam_h)
    p_a = poisson.pmf(a_vals, lam_a)

    mat = np.outer(p_h, p_a)

    # Correction Dixon-Coles sur les petits scores
    for h in range(2):
        for a in range(2):
            mat[h, a] *= _dixon_coles_tau(h, a, lam_h, lam_a, rho)

    # Renormaliser
    total = mat.sum()
    if total > 0:
        mat = mat / total
    return mat


def simulate_scores(lam_h: float, lam_a: float,
                    rho: float = DEFAULT_RHO,
                    n: int = DEFAULT_N_SIMULATIONS,
                    kmax: int = 8,
                    seed: int | None = DEFAULT_SEED) -> tuple[np.ndarray, np.ndarray]:
    """Simule n scores (buts domicile, buts extérieur) via la matrice."""
    mat = score_matrix(lam_h, lam_a, rho, kmax)

    # Aplatir la matrice en probabilités
    flat = mat.flatten()

    rng = np.random.default_rng(seed)
    idx = rng.choice(len(flat), size=n, p=flat)

    h = idx // (kmax + 1)
    a = idx % (kmax + 1)
    return h.astype(int), a.astype(int)


def match_outcomes(h_samples: np.ndarray, a_samples: np.ndarray) -> dict:
    """Calcule les probabilités 1X2 à partir des échantillons."""
    n = len(h_samples)
    if n == 0:
        return {"home_win": 0.0, "draw": 0.0, "away_win": 0.0}

    home_win = int((h_samples > a_samples).sum())
    draw = int((h_samples == a_samples).sum())
    away_win = int((h_samples < a_samples).sum())

    return {
        "home_win": float(home_win / n),
        "draw": float(draw / n),
        "away_win": float(away_win / n),
    }


def goals_over_under(h_samples: np.ndarray, a_samples: np.ndarray,
                     line: float) -> dict:
    """Probabilités Over/Under pour une ligne de buts (ex: 2.5)."""
    n = len(h_samples)
    if n == 0:
        return {"over": 0.0, "under": 0.0}

    total = h_samples + a_samples
    threshold = int(line + 0.5)
    over = int((total >= threshold).sum())
    under = int((total < threshold).sum())

    return {
        "over": float(over / n),
        "under": float(under / n),
    }


def handicap(h_samples: np.ndarray, a_samples: np.ndarray,
             line: float) -> dict:
    """Probabilités Handicap pour une ligne (ex: -1, +1).

    Convention :
    - line = -1 (domicile doit gagner par 2 buts ou plus)
    - line = +1 (extérieur peut perdre par 1 but)
    """
    n = len(h_samples)
    if n == 0:
        return {"home_cover": 0.0, "away_cover": 0.0}

    diff = h_samples - a_samples
    threshold = line

    home_cover = int((diff > threshold).sum())
    away_cover = int((diff < threshold).sum())

    return {
        "home_cover": float(home_cover / n),
        "away_cover": float(away_cover / n),
    }


def joint_distribution_goals(lam_h: float, lam_a: float,
                             rho: float = DEFAULT_RHO,
                             n_simulations: int = DEFAULT_N_SIMULATIONS,
                             seed: int | None = DEFAULT_SEED) -> dict:
    """Distribution jointe complète des buts."""
    h_samples, a_samples = simulate_scores(
        lam_h, lam_a, rho=rho,
        n=n_simulations, seed=seed,
    )

    return {
        "lam_h": lam_h,
        "lam_a": lam_a,
        "rho": rho,
        "n_simulations": n_simulations,
        "seed": seed,
        "h_samples": h_samples,
        "a_samples": a_samples,
        "outcomes": match_outcomes(h_samples, a_samples),
        "mean_h": float(h_samples.mean()),
        "mean_a": float(a_samples.mean()),
        "mean_total": float((h_samples + a_samples).mean()),
                       }
