import numpy as np


def simulate(c1_dist: np.ndarray, c2_dist: np.ndarray,
             rho: float = 0.0, n: int = 10000,
             seed: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Simule n paires (C1, C2) via Monte Carlo.

    c1_dist[k] = P(C1 = k)
    c2_dist[k] = P(C2 = k)
    rho = corrélation entre C1 et C2 (copule gaussienne)
    """
    from cfcx.models.copula import sample_joint
    return sample_joint(c1_dist, c2_dist, rho, n, seed=seed)


def total_distribution(c1_samples: np.ndarray,
                       c2_samples: np.ndarray) -> dict:
    """Calcule les statistiques de C_T = C1 + C2 à partir des échantillons."""
    total = c1_samples + c2_samples

    return {
        "mean_c1": float(c1_samples.mean()),
        "mean_c2": float(c2_samples.mean()),
        "mean_total": float(total.mean()),
        "std_c1": float(c1_samples.std()),
        "std_c2": float(c2_samples.std()),
        "std_total": float(total.std()),
        "p_c1_ge": _p_ge_table(c1_samples),
        "p_c2_ge": _p_ge_table(c2_samples),
        "p_total_ge": _p_ge_table(total),
    }


def _p_ge_table(samples: np.ndarray, kmax: int = 30) -> dict[int, float]:
    """Probabilités P(C >= k) pour k = 0..kmax."""
    n = len(samples)
    out = {}
    for k in range(kmax + 1):
        out[k] = float((samples >= k).sum() / n)
    return out


def joint_table(c1_samples: np.ndarray, c2_samples: np.ndarray,
                kmax: int = 20) -> np.ndarray:
    """Table jointe P(C1 = i, C2 = j) pour i, j dans [0, kmax]."""
    table = np.zeros((kmax + 1, kmax + 1))
    n = len(c1_samples)
    for i, j in zip(c1_samples, c2_samples):
        if i <= kmax and j <= kmax:
            table[i, j] += 1
    return table / n if n > 0 else table


def p_event(c1_samples: np.ndarray, c2_samples: np.ndarray,
            c1_op: str | None = None, c1_line: int | None = None,
            c2_op: str | None = None, c2_line: int | None = None,
            total_op: str | None = None, total_line: int | None = None) -> float:
    """Probabilité d'un événement combiné sur C1, C2, ou C1+C2."""
    n = len(c1_samples)
    if n == 0:
        return 0.0

    mask = np.ones(n, dtype=bool)

    if c1_op and c1_line is not None:
        if c1_op == "ge":
            mask &= c1_samples >= c1_line
        elif c1_op == "le":
            mask &= c1_samples <= c1_line

    if c2_op and c2_line is not None:
        if c2_op == "ge":
            mask &= c2_samples >= c2_line
        elif c2_op == "le":
            mask &= c2_samples <= c2_line

    if total_op and total_line is not None:
        total = c1_samples + c2_samples
        if total_op == "ge":
            mask &= total >= total_line
        elif total_op == "le":
            mask &= total <= total_line

    return float(mask.sum() / n)
