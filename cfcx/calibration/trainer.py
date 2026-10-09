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


def collect_pairs(results: list[dict]) -> tuple[list[float], list[int]]:
    """Extrait les paires (probabilité prédite, résultat observé)
    à partir des résultats d'un backtest."""
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


def train_and_evaluate(raw_probs: list[float],
                       outcomes: list[int],
                       train_ratio: float = 0.7) -> dict:
    """Entraîne un calibrateur et mesure son effet.

    Sépare les données en train / test de façon chronologique :
    - 70% pour entraîner le calibrateur
    - 30% pour mesurer l'amélioration
    """
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

    iso = fit_isotonic(train_p, train_o)

    calibrated_test = [apply_isotonic(iso, p) for p in test_p]

    ece_before = ece(test_p, test_o)
    ece_after = ece(calibrated_test, test_o)
    brier_before = brier_score(test_p, test_o)
    brier_after = brier_score(calibrated_test, test_o)
    ll_before = log_loss(test_p, test_o)
    ll_after = log_loss(calibrated_test, test_o)

    return {
        "n_samples": len(raw_probs),
        "n_train": len(train_p),
        "n_test": len(test_p),
        "ece_before": ece_before,
        "ece_after": ece_after,
        "ece_improvement": ece_before - ece_after,
        "brier_before": brier_before,
        "brier_after": brier_after,
        "logloss_before": ll_before,
        "logloss_after": ll_after,
    }


def save_calibrator(iso, path: str) -> None:
    """Sauvegarde le calibrateur en JSON (breakpoints isotoniques)."""
    X = iso.X_thresholds_.tolist() if hasattr(iso, "X_thresholds_") else []
    y = iso.y_thresholds_.tolist() if hasattr(iso, "y_thresholds_") else []
    data = {"x": X, "y": y}
    Path(path).write_text(json.dumps(data))


def load_calibrator(path: str):
    """Recharge un calibrateur depuis un fichier JSON."""
    from sklearn.isotonic import IsotonicRegression

    data = json.loads(Path(path).read_text())
    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    if data["x"] and data["y"]:
        iso.fit(data["x"], data["y"])
    return iso
