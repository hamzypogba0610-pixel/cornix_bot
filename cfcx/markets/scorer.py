import numpy as np

from cfcx.markets.metrics import (
    mdi, fi, robustness, data_quality, line_stability, consensus,
)


DEFAULT_WEIGHTS = {
    "w_p": 0.40,
    "w_edge": 1.00,
    "w_rob": 0.50,
    "w_cons": 0.30,
    "w_dq": 0.20,
    "w_ls": 0.20,
    "w_fi": 0.50,
    "w_mdi": 0.40,
}


def _edge(prob_calibrated: float, prob_raw: float) -> float:
    """Edge = différence entre notre estimation calibrée et la brute.

    Positif : on pense mieux que le bookmaker.
    Négatif : le bookmaker est meilleur que nous.
    """
    return float(prob_calibrated - prob_raw)


def score_market(market: dict,
                 probabilities_by_model: list[float],
                 probabilities_perturbed: list[float],
                 matches_played: int,
                 freshness_days: float,
                 completeness: float,
                 line_dist: np.ndarray | None = None,
                 weights: dict | None = None) -> dict:
    """Calcule le score complet d'un marché."""
    if weights is None:
        weights = DEFAULT_WEIGHTS

    p_cal = market["prob"]
    p_raw = market.get("prob_raw", p_cal)

    edge_val = _edge(p_cal, p_raw)

    mdi_val = mdi(probabilities_by_model)
    fi_val = fi(probabilities_perturbed)
    rob_val = robustness(probabilities_perturbed, p_cal)
    cons_val = consensus(probabilities_by_model)
    dq_val = data_quality(matches_played, freshness_days, completeness)
    ls_val = (
        line_stability(line_dist, market["line"])
        if line_dist is not None and "line" in market
        else 0.5
    )

    score = (
        weights["w_p"] * p_cal
        + weights["w_edge"] * max(0.0, edge_val)
        + weights["w_rob"] * rob_val
        + weights["w_cons"] * cons_val
        + weights["w_dq"] * dq_val
        + weights["w_ls"] * ls_val
        - weights["w_fi"] * fi_val
        - weights["w_mdi"] * mdi_val
    )

    out = dict(market)
    out.update({
        "score": float(score),
        "edge": float(edge_val),
        "mdi": float(mdi_val),
        "fi": float(fi_val),
        "rob": float(rob_val),
        "cons": float(cons_val),
        "dq": float(dq_val),
        "ls": float(ls_val),
    })
    return out


def rank_markets(scored_markets: list[dict]) -> list[dict]:
    """Trie les marchés par score décroissant."""
    return sorted(scored_markets, key=lambda m: m["score"], reverse=True)


def market_dominance(ranked: list[dict]) -> dict:
    """Calcule MDS et MDR entre le top 1 et le top 2."""
    if len(ranked) < 2:
        return {"mds": 0.0, "mdr": 0.0, "top1": None, "top2": None}

    s1 = ranked[0]["score"]
    s2 = ranked[1]["score"]

    mds = s1 - s2
    mdr = (s1 - s2) / (abs(s1) + 1e-9)

    return {
        "mds": float(mds),
        "mdr": float(mdr),
        "top1": ranked[0]["market_id"],
        "top2": ranked[1]["market_id"],
    }


def group_by_family(ranked: list[dict]) -> dict:
    """Regroupe les marchés par famille."""
    groups = {"team1": [], "team2": [], "total": [], "multicorner": []}
    for m in ranked:
        fam = m.get("family")
        if fam in groups:
            groups[fam].append(m)
    return groups


def best_per_family(ranked: list[dict]) -> dict:
    """Retourne le meilleur marché de chaque famille."""
    groups = group_by_family(ranked)
    return {fam: (lst[0] if lst else None) for fam, lst in groups.items()}
