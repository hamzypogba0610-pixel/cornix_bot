import json
from pathlib import Path

import numpy as np

from cfcx.calibration.isotonic import (
    fit_isotonic,
    apply_isotonic,
    ece,
    brier_score,
    log_loss,
)
from cfcx.calibration.beta import (
    fit_beta,
    apply_beta_batch,
)


def collect_pairs(results: list[dict]) -> tuple[list[float], list[int]]:
    """Extrait les paires (probabilité prédite, résultat observé)."""
    probs, outcomes = [], []
    for r in results:
        if r.get("top_prob") is None:
            continue
        if r.get("outcome") is None:
            continue
        if r.get("decision") not in ("BET", "NO_BET"):
            continue
        probs.append(float(r["top_prob"]))
        outcomes.append(int(r["outcome"]))
    return probs, outcomes


def _eval_method(name: str, test_p: list[float], test_o: list[int],
                 calibrated: list[float]) -> dict:
    """Évalue une méthode de calibration sur le test set."""
    return {
        "method": name,
        "ece": ece(calibrated, test_o),
        "brier": brier_score(calibrated, test_o),
        "logloss": log_loss(calibrated, test_o),
        "ece_raw": ece(test_p, test_o),
        "brier_raw": brier_score(test_p, test_o),
        "logloss_raw": log_loss(test_p, test_o),
    }


def train_and_evaluate(raw_probs: list[float],
                       outcomes: list[int],
                       train_ratio: float = 0.7) -> dict:
    """Entraîne 2 calibrateurs (Isotonic + Beta) et compare leurs résultats."""
    if len(raw_probs) < 20:
        return {
            "error": "trop peu de données pour calibrer (minimum 20)",
            "n_samples": len(raw_probs),
        }

    split = int(len(raw_probs) * train_ratio)

    train_p = raw_probs[:split]
    train_o = outcomes[:split]
    test_p = raw_probs[split:]
    test_o = outcomes[split:]

    if len(train_p) < 10 or len(test_p) < 5:
        return {
            "error": "pas assez de données après split",
            "n_train": len(train_p),
            "n_test": len(test_p),
        }

    # --- Isotonique ---
    iso = fit_isotonic(train_p, train_o)
    iso_calibrated = [apply_isotonic(iso, p) for p in test_p]
    iso_report = _eval_method("isotonic", test_p, test_o, iso_calibrated)

    # --- Beta ---
    beta_params = fit_beta(train_p, train_o)
    beta_calibrated = apply_beta_batch(beta_params, test_p)
    beta_report = _eval_method("beta", test_p, test_o, beta_calibrated)

    # Choisir la meilleure méthode = LogLoss le plus bas
    best = min([iso_report, beta_report], key=lambda r: r["logloss"])

    return {
        "n_samples": len(raw_probs),
        "n_train": len(train_p),
        "n_test": len(test_p),
        "isotonic": iso_report,
        "beta": beta_report,
        "best_method": best["method"],
    }


def save_calibrator(iso, path: str) -> None:
    """Sauvegarde le calibrateur isotonique en JSON."""
    X = iso.X_thresholds_.tolist() if hasattr(iso, "X_thresholds_") else []
    y = iso.y_thresholds_.tolist() if hasattr(iso, "y_thresholds_") else []
    data = {"type": "isotonic", "x": X, "y": y}
    Path(path).write_text(json.dumps(data))


def save_beta_calibrator(params: dict, path: str) -> None:
    """Sauvegarde le calibrateur Beta en JSON."""
    data = {"type": "beta", **params}
    Path(path).write_text(json.dumps(data))


def load_calibrator(path: str):
    """Recharge un calibrateur (isotonic ou beta)."""
    data = json.loads(Path(path).read_text())
    if data.get("type") == "beta":
        return {"type": "beta", "a": data["a"], "b": data["b"], "c": data["c"]}

    from sklearn.isotonic import IsotonicRegression

    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    if data["x"] and data["y"]:
        iso.fit(data["x"], data["y"])
    return {"type": "isotonic", "model": iso}
