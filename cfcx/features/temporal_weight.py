import math


def exponential_weights(deltas_days: list[float], lam: float) -> list[float]:
    return [math.exp(-lam * d) for d in deltas_days]


def weighted_mean(values: list[float], weights: list[float]) -> float:
    s = sum(weights)
    if s == 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / s
