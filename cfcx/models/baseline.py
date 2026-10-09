from scipy.stats import poisson


def naive_lambda(attack: float, defense: float) -> float:
    return max(1.0, (attack + defense) / 2.0)


def p_ge(lam: float, k: int) -> float:
    return float(1 - poisson.cdf(k - 1, lam))
