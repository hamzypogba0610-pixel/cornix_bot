from datetime import date

from cfcx.config import data_config
from cfcx.data.store import session as make_session
from cfcx.features.corner_dna import corner_dna
from cfcx.features.latent import league_prior, latent_force
from cfcx.features.matchup import matchup
from cfcx.features.normalize import league_stats, normalize_team
from cfcx.models.joint import joint_distribution
from cfcx.markets.generator import generate_all
from cfcx.markets.scorer import score_market
from cfcx.decision.meta_judge import judge
from cfcx.decision.no_bet import should_abstain


DEFAULT_RHO = 0.10
DEFAULT_DISPERSION = 1.2


def run(s, team1: str, team2: str, league: str,
        match_date: date, n_simulations: int = 10000) -> dict:
    """Pipeline complet pour un match.

    1. Features -> 2. Forces latentes -> 3. Matchup -> 4. Distribution jointe
    -> 5. Marchés -> 6. Scoring -> 7. Décision
    """
    # 1. Prior et stats de la ligue
    prior = league_prior(s, league, match_date)
    lg_stats = league_stats(s, league, match_date)
    lg_avg = prior["mu"]

    # 2. Corner DNA par équipe
    dna1 = corner_dna(s, team1, league, match_date)
    dna2 = corner_dna(s, team2, league, match_date)

    # 3. Normalisation
    dna1 = normalize_team(dna1, lg_stats["mean"], lg_stats["std"])
    dna2 = normalize_team(dna2, lg_stats["mean"], lg_stats["std"])

    # 4. Forces latentes
    lat1 = latent_force(dna1, prior)
    lat2 = latent_force(dna2, prior)

    # 5. Matchup
    m = matchup(lat1, lat2, lg_avg)
    lam1 = m["expected_c1"]
    lam2 = m["expected_c2"]

    # 6. Distribution jointe
    jd = joint_distribution(
        lam1=lam1, lam2=lam2,
        dispersion1=DEFAULT_DISPERSION,
        dispersion2=DEFAULT_DISPERSION,
        rho=DEFAULT_RHO,
        n_simulations=n_simulations,
    )
    c1_samples = jd["c1_samples"]
    c2_samples = jd["c2_samples"]

    # 7. Marchés
    markets = generate_all(c1_samples, c2_samples)

    # 8. Scoring (probabilités perturbées simplifiées par ±5%)
    scored = []
    for mk in markets:
        p = mk["prob"]
        # Modèles simplifiés : on simule un désaccord via un petit bruit
        models_probs = [p, max(0.0, p - 0.02), min(1.0, p + 0.02)]
        perturbed = [p, max(0.0, p - 0.03), min(1.0, p + 0.03)]

        scored.append(score_market(
            market=mk,
            probabilities_by_model=models_probs,
            probabilities_perturbed=perturbed,
            matches_played=min(lat1["matches_played"], lat2["matches_played"]),
            freshness_days=5.0,
            completeness=0.8,
        ))

    # 9. Décision
    result = judge(scored)

    # 10. Garde-fou NO BET
    abstain, reason = should_abstain(
        result["top"] if result["top"] else {},
        data_quality=(result["top"]["dq"] if result["top"] else 0.0),
    )
    if abstain:
        result["decision"] = "NO_BET"
        result["reason"] = reason

    # 11. Métadonnées
    result["team1"] = team1
    result["team2"] = team2
    result["league"] = league
    result["date"] = match_date.isoformat()
    result["lam1"] = lam1
    result["lam2"] = lam2

    return result


def run_simple(team1: str, team2: str, league: str,
               match_date: date, n_simulations: int = 10000) -> dict:
    """Version qui ouvre sa propre session (utile pour usage direct)."""
    s = make_session()
    try:
        return run(s, team1, team2, league, match_date,
                   n_simulations=n_simulations)
    finally:
        s.close()
