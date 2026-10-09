import numpy as np


def implied_odds(prob: float, margin: float = 0.05) -> float:
    """Cote bookmaker réaliste dérivée d'une probabilité.

    Fair odds = 1 / p
    Bookmaker odds = fair odds * (1 - margin)
    """
    if prob <= 0 or prob >= 1:
        return 1.0
    fair = 1.0 / prob
    return max(1.01, fair * (1.0 - margin))


def summary(results: list[dict]) -> dict:
    """Calcule les métriques globales du backtest."""
    if not results:
        return _empty_summary()

    total = len(results)
    bet_results = [r for r in results if r.get("decision") == "BET"]
    no_bet_results = [r for r in results if r.get("decision") == "NO_BET"]

    bets_with_outcome = [r for r in bet_results if r.get("outcome") is not None]
    wins = [r for r in bets_with_outcome if r["outcome"] == 1]
    losses = [r for r in bets_with_outcome if r["outcome"] == 0]

    win_rate = len(wins) / len(bets_with_outcome) if bets_with_outcome else 0.0
    no_bet_rate = len(no_bet_results) / total if total else 0.0
    error_rate = (
        sum(1 for r in results if r.get("decision") == "ERROR") / total
        if total else 0.0
    )

    return {
        "total_matches": total,
        "bet_count": len(bet_results),
        "no_bet_count": len(no_bet_results),
        "error_count": sum(1 for r in results if r.get("decision") == "ERROR"),
        "no_bet_rate": no_bet_rate,
        "error_rate": error_rate,
        "win_rate_on_bets": win_rate,
        "wins": len(wins),
        "losses": len(losses),
    }


def roi(results: list[dict], margin: float = 0.05) -> dict:
    """ROI réaliste : la cote de chaque pari est dérivée de sa probabilité."""
    bets = [r for r in results if r.get("decision") == "BET"
            and r.get("outcome") is not None
            and r.get("top_prob") is not None]
    if not bets:
        return {
            "roi": 0.0, "profit": 0.0, "n_bets": 0,
            "avg_odds": 0.0, "margin": margin,
        }

    stake = 1.0
    profit = 0.0
    total_odds = 0.0

    for r in bets:
        p = r["top_prob"]
        odds = implied_odds(p, margin)
        total_odds += odds
        if r["outcome"] == 1:
            profit += (odds - 1.0) * stake
        else:
            profit -= stake

    total_staked = len(bets) * stake
    roi_val = profit / total_staked if total_staked > 0 else 0.0

    return {
        "roi": float(roi_val),
        "profit": float(profit),
        "n_bets": len(bets),
        "avg_odds": float(total_odds / len(bets)),
        "margin": margin,
    }


def calibration_report(results: list[dict], n_bins: int = 10) -> dict:
    """Vérifie la calibration des probabilités prédites."""
    bets = [r for r in results if r.get("decision") == "BET"
            and r.get("outcome") is not None
            and r.get("top_prob") is not None]
    if not bets:
        return {"ece": 0.0, "bins": []}

    probs = np.array([r["top_prob"] for r in bets], dtype=float)
    outs = np.array([r["outcome"] for r in bets], dtype=float)

    bins = np.linspace(0, 1, n_bins + 1)
    report = []
    ece_val = 0.0
    n = len(probs)

    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = (probs >= lo) & (probs < hi if i < n_bins - 1 else probs <= hi)
        if mask.sum() == 0:
            continue
        avg_p = float(probs[mask].mean())
        avg_o = float(outs[mask].mean())
        weight = mask.sum() / n
        ece_val += weight * abs(avg_p - avg_o)
        report.append({
            "bin": f"{lo:.1f}-{hi:.1f}",
            "count": int(mask.sum()),
            "avg_predicted": avg_p,
            "avg_realized": avg_o,
            "gap": avg_p - avg_o,
        })

    return {"ece": float(ece_val), "bins": report}


def _empty_summary() -> dict:
    return {
        "total_matches": 0, "bet_count": 0, "no_bet_count": 0,
        "error_count": 0, "no_bet_rate": 0.0, "error_rate": 0.0,
        "win_rate_on_bets": 0.0, "wins": 0, "losses": 0,
    }


def full_report(results: list[dict]) -> dict:
    """Rapport complet : summary + ROI + calibration."""
    return {
        "summary": summary(results),
        "roi": roi(results),
        "calibration": calibration_report(results),
    }
