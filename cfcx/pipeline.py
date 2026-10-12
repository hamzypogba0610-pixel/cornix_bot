from datetime import date
from pathlib import Path

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
from cfcx.calibration.isotonic import apply_isotonic
from cfcx.calibration.trainer import load_calibrator


DEFAULT_RHO = 0.10
DEFAULT_DISPERSION = 1.2
DEFAULT_SEED = 42
CALIBRATOR_PATH = "configs/calibrator.json"

# Avantage domicile
HOME_BOOST = 1.10
AWAY_FACTOR = 0.91


_CALIBRATOR_CACHE = None


def _load_calibrator():
    """Charge le calibrateur une seule fois (cache)."""
    global _CALIBRATOR_CACHE
    if _CALIBRATOR_CACHE is not None:
        return _CALIBRATOR_CACHE

    path = Path(CALIBRATOR_PATH)
    if not path.exists():
        _CALIBRATOR_CACHE = {"type": "none"}
        return _CALIBRATOR_CACHE

    try:
        _CALIBRATOR_CACHE = load_calibrator(str(path))
    except Exception:
        _CALIBRATOR_CACHE = {"type": "none"}
    return _CALIBRATOR_CACHE


def _apply_calibration(prob: float) -> float:
    """Applique le calibrateur à une probabilité brute."""
    cal = _load_calibrator()
    if cal.get("type") == "isotonic":
        return apply_isotonic(cal["model"], prob)
    if cal.get("type") == "beta":
        from cfcx.calibration.beta import apply_beta
        return apply_beta(cal, prob)
    return prob


def run(s, team1: str, team2: str, league: str,
        match_date: date,
        n_simulations: int = 10000,
        seed: int | None = DEFAULT_SEED) -> dict:
    """Pipeline complet pour un match.

    team1 = équipe à domicile
    team2 = équipe à l'extérieur
    seed : 42 par défaut -> reproductibilité. None -> aléatoire.
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

    # 5b. Avantage domicile
    lam1 = lam1 * HOME_BOOST
    lam2 = lam2 * AWAY_FACTOR

    # 6. Distribution jointe (reproductible)
    jd = joint_distribution(
        lam1=lam1, lam2=lam2,
        dispersion1=DEFAULT_DISPERSION,
        dispersion2=DEFAULT_DISPERSION,
        rho=DEFAULT_RHO,
        n_simulations=n_simulations,
        seed=seed,
    )
    c1_samples = jd["c1_samples"]
    c2_samples = jd["c2_samples"]

    # 7. Marchés (probabilités brutes)
    markets = generate_all(c1_samples, c2_samples)

    # 8. Calibration
    for mk in markets:
        mk["prob_raw"] = mk["prob"]
        mk["prob"] = _apply_calibration(mk["prob_raw"])

    # 9. Scoring
    scored = []
    for mk in markets:
        p = mk["prob"]
        models_probs = [p, max(0.0, p - 0.02), min(1.0, p + 0.02)]
        perturbed = [p, max(0.0, p - 0.03), min(1.0, p + 0.03)]

        scored.append(score_market(
            market=mk,
            probabilities_by_model=models_probs,
            probabilities_perturbed=perturbed,
            matches_played=min(
                lat1["matches_played"], lat2["matches_played"]
            ),
            freshness_days=5.0,
            completeness=0.8,
        ))
        # 9b. Exposer tous les marchés scorés pour le calibrateur
all_markets = scored

    # 10. Décision
    result = judge(scored)

    # 11. Garde-fou NO BET
    abstain, reason = should_abstain(
        result["top"] if result["top"] else {},
        data_quality=(result["top"]["dq"] if result["top"] else 0.0),
    )
    if abstain:
        result["decision"] = "NO_BET"
        result["reason"] = reason

    # 12. Métadonnées
    result["team1"] = team1
    result["team2"] = team2
    result["league"] = league
    result["date"] = match_date.isoformat()
    result["lam1"] = lam1
    result["lam2"] = lam2
    result["seed"] = seed

    return result


def run_simple(team1: str, team2: str, league: str,
               match_date: date,
               n_simulations: int = 10000,
               seed: int | None = DEFAULT_SEED) -> dict:
    """Version qui ouvre sa propre session."""
    s = make_session()
    try:
        return run(s, team1, team2, league, match_date,
                   n_simulations=n_simulations, seed=seed)
    finally:
        s.close()
