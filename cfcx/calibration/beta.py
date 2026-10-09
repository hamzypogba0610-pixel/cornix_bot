import numpy as np
from scipy.optimize import minimize


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))


def _nll(params: np.ndarray, p: np.ndarray, y: np.ndarray) -> float:
    """Negative log-likelihood pour la calibration Beta."""
    a, b, c = params
    eps = 1e-9
    logit = a * np.log(np.clip(p, eps, 1 - eps)) + b * np.log(np.clip(1 - p, eps, 1 - eps)) + c
    q = _sigmoid(logit)
    return -np.mean(y * np.log(q + eps) + (1 - y) * np.log(1 - q + eps))


def fit_beta(raw_probs: list[float], outcomes: list[int]) -> dict:
    """Entraîne un calibrateur Beta (3 paramètres)."""
    p = np.clip(np.array(raw_probs, dtype=float), 1e-9, 1 - 1e-9)
    y = np.array(outcomes, dtype=float)

    x0 = np.array([1.0, 1.0, 0.0])
    result = minimize(_nll, x0, args=(p, y), method="Nelder-Mead",
                      options={"xatol": 1e-6, "maxiter": 1000})

    a, b, c = result.x
    return {"a": float(a), "b": float(b), "c": float(c)}


def apply_beta(params: dict, raw_prob: float) -> float:
    """Applique un calibrateur Beta à une probabilité."""
    eps = 1e-9
    p = min(max(raw_prob, eps), 1 - eps)
    logit = (
        params["a"] * np.log(p)
        + params["b"] * np.log(1 - p)
        + params["c"]
    )
    return float(_sigmoid(np.array([logit]))[0])


def apply_beta_batch(params: dict, raw_probs: list[float]) -> list[float]:
    return [apply_beta(params, p) for p in raw_probs]
