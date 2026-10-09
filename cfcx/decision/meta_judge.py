from cfcx.markets.scorer import (
    rank_markets, market_dominance, best_per_family,
)


DEFAULT_THRESHOLDS = {
    "min_prob": 0.55,
    "min_rob": 0.40,
    "max_mdi": 0.20,
    "min_mds": 0.01,
}


def judge(scored_markets: list[dict],
          thresholds: dict | None = None) -> dict:
    """Prend la décision finale sur l'ensemble des marchés scorés."""
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    if not scored_markets:
        return {
            "decision": "NO_BET",
            "reason": "aucun marché candidat",
            "top": None,
            "top_per_family": {},
            "dominance": {},
        }

    ranked = rank_markets(scored_markets)
    top = ranked[0]
    dominance = market_dominance(ranked)
    per_family = best_per_family(ranked)

    reasons = _check_constraints(top, dominance, thresholds)

    if reasons:
        return {
            "decision": "NO_BET",
            "reason": "; ".join(reasons),
            "top": top,
            "top_per_family": per_family,
            "dominance": dominance,
        }

    return {
        "decision": "BET",
        "reason": "toutes les contraintes satisfaites",
        "top": top,
        "top_per_family": per_family,
        "dominance": dominance,
    }


def _check_constraints(top: dict, dominance: dict,
                       thresholds: dict) -> list[str]:
    """Retourne la liste des contraintes non satisfaites."""
    reasons = []

    if top.get("prob", 0.0) < thresholds["min_prob"]:
        reasons.append(
            f"probabilité {top['prob']:.2f} < {thresholds['min_prob']}"
        )
    if top.get("rob", 0.0) < thresholds["min_rob"]:
        reasons.append(
            f"robustesse {top['rob']:.2f} < {thresholds['min_rob']}"
        )
    if top.get("mdi", 0.0) > thresholds["max_mdi"]:
        reasons.append(
            f"MDI {top['mdi']:.2f} > {thresholds['max_mdi']}"
        )
    if dominance.get("mds", 0.0) < thresholds["min_mds"]:
        reasons.append(
            f"MDS {dominance['mds']:.3f} < {thresholds['min_mds']}"
        )

    return reasons
