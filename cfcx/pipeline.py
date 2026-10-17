from datetime import date
from pathlib import Path

from cfcx.data.store import session as make_session
from cfcx.features.corner_dna import corner_dna
from cfcx.features.goal_dna import goal_dna
from cfcx.features.latent import league_prior, latent_force
from cfcx.features.matchup import matchup
from cfcx.features.normalize import league_stats, normalize_team
from cfcx.models.joint import joint_distribution
from cfcx.models.goal_joint import joint_distribution_goals
from cfcx.markets.generator import generate_all
from cfcx.markets.goal_generator import generate_all_goals
from cfcx.markets.scorer import score_market
from cfcx.decision.meta_judge import judge
from cfcx.decision.no_bet import should_abstain
from cfcx.calibration.isotonic import apply_isotonic
from cfcx.calibration.trainer import load_calibrator


DEFAULT_RHO = 0.10
DEFAULT_DISPERSION = 1.2
DEFAULT_SEED = 42

CALIBRATOR_CORNERS_PATH = "configs/calibrator.json"
CALIBRATOR_GOALS_PATH = "configs/calibrator_goals.json"

HOME_BOOST = 1.10
AWAY_FACTOR = 0.91

FAVORITE_AMPLITUDE = 0.30
H2H_WEIGHT = 0.30

LEAGUE_GOALS_AVG = 1.35

SHRINK_CORNERS = 0.5
SHRINK_GOALS = 0.5


_CALIBRATOR_CORNERS_CACHE = None
_CALIBRATOR_GOALS_CACHE = None


def _load_calibrator(path: str, cache_key: str):
    global _CALIBRATOR_CORNERS_CACHE, _CALIBRATOR_GOALS_CACHE
    if cache_key == "corners":
        if _CALIBRATOR_CORNERS_CACHE is not None:
            return _CALIBRATOR_CORNERS_CACHE
    elif cache_key == "goals":
        if _CALIBRATOR_GOALS_CACHE is not None:
            return _CALIBRATOR_GOALS_CACHE

    p = Path(path)
    if not p.exists():
        result = {"type": "none"}
    else:
        try:
            result = load_calibrator(str(p))
        except Exception:
            result = {"type": "none"}

    if cache_key == "corners":
        _CALIBRATOR_CORNERS_CACHE = result
    elif cache_key == "goals":
        _CALIBRATOR_GOALS_CACHE = result
    return result


def _apply_calibration(prob: float, sport: str = "corners") -> float:
    if sport == "corners":
        cal = _load_calibrator(CALIBRATOR_CORNERS_PATH, "corners")
        shrink = SHRINK_CORNERS
    elif sport == "goals":
        cal = _load_calibrator(CALIBRATOR_GOALS_PATH, "goals")
        shrink = SHRINK_GOALS
    else:
        return prob

    if cal.get("type") == "isotonic":
        return apply_isotonic(cal["model"], prob, shrink=shrink)
    if cal.get("type") == "beta":
        from cfcx.calibration.beta import apply_beta
        return apply_beta(cal, prob)
    return prob


def _fair_probs_from_1x2(odds_1: float, odds_x: float, odds_2: float):
    try:
        inv_1 = 1.0 / odds_1
        inv_x = 1.0 / odds_x
        inv_2 = 1.0 / odds_2
        total = inv_1 + inv_x + inv_2
        if total <= 0:
            return None
        return (inv_1 / total, inv_x / total, inv_2 / total)
    except (ZeroDivisionError, TypeError):
        return None


def _compute_favorite_boost(odds_1x2: dict | None) -> tuple[float, float]:
    if odds_1x2 is None:
        return (HOME_BOOST, AWAY_FACTOR)

    try:
        o1 = float(odds_1x2["odds_1"])
        ox = float(odds_1x2["odds_x"])
        o2 = float(odds_1x2["odds_2"])
    except (KeyError, ValueError, TypeError):
        return (HOME_BOOST, AWAY_FACTOR)

    probs = _fair_probs_from_1x2(o1, ox, o2)
    if probs is None:
        return (HOME_BOOST, AWAY_FACTOR)

    p1, _px, p2 = probs
    diff = p1 - p2

    boost1 = 1.0 + FAVORITE_AMPLITUDE * diff
    boost2 = 1.0 - FAVORITE_AMPLITUDE * diff

    boost1 = max(0.70, min(1.40, boost1))
    boost2 = max(0.70, min(1.40, boost2))

    boost1 *= 1.03
    boost2 *= 0.97

    return (boost1, boost2)


def _compute_h2h_adjustment(h2h: dict | None):
    if not h2h or not h2h.get("matches"):
        return None

    matches = h2h["matches"]
    n = len(matches)
    if n == 0:
        return None

    mc1_list = []
    mc2_list = []
    goals1_list = []
    goals2_list = []
    corners1_total = []
    corners2_total = []

    for m in matches:
        try:
            c1_mt1 = int(m.get("c1mt_1", 0))
            c1_mt2 = int(m.get("c1mt_2", 0))
            c2_mt1 = int(m.get("c2mt_1", 0))
            c2_mt2 = int(m.get("c2mt_2", 0))
            b1_mt1 = int(m.get("b1mt_1", 0))
            b1_mt2 = int(m.get("b1mt_2", 0))
            b2_mt1 = int(m.get("b2mt_1", 0))
            b2_mt2 = int(m.get("b2mt_2", 0))
        except (ValueError, TypeError):
            continue

        mc1_list.append(c1_mt1 * c1_mt2)
        mc2_list.append(c2_mt1 * c2_mt2)
        corners1_total.append(c1_mt1 + c1_mt2)
        corners2_total.append(c2_mt1 + c2_mt2)
        goals1_list.append(b1_mt1 + b1_mt2)
        goals2_list.append(b2_mt1 + b2_mt2)

    if not mc1_list:
        return None

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    mc1_avg = avg(mc1_list)
    mc2_avg = avg(mc2_list)

    corners1_avg = avg(corners1_total)
    corners2_avg = avg(corners2_total)

    goals1_avg = avg(goals1_list)
    goals2_avg = avg(goals2_list)

    return {
        "n_matches": len(mc1_list),
        "mc1_avg": mc1_avg,
        "mc2_avg": mc2_avg,
        "mc_global_avg": mc1_avg + mc2_avg,
        "corners1_avg": corners1_avg,
        "corners2_avg": corners2_avg,
        "goals1_avg": goals1_avg,
        "goals2_avg": goals2_avg,
    }


def _blend_lambdas(lam_model: float, lam_h2h: float | None) -> float:
    if lam_h2h is None or lam_h2h <= 0:
        return lam_model
    return (1.0 - H2H_WEIGHT) * lam_model + H2H_WEIGHT * lam_h2h


def _adjust_goals_intensity(atk_for: float, def_against: float,
                            league_avg: float) -> float:
    if league_avg <= 0:
        return 1.35
    return max(0.3, (atk_for + def_against) / 2.0 * (league_avg / 1.35))


def run(s, team1: str, team2: str, league: str,
        match_date: date,
        n_simulations: int = 10000,
        seed: int | None = DEFAULT_SEED,
        odds_1x2: dict | None = None,
        h2h: dict | None = None) -> dict:
    prior = league_prior(s, league, match_date)
    lg_stats = league_stats(s, league, match_date)
    lg_avg = prior["mu"]

    dna1 = corner_dna(s, team1, league, match_date)
    dna2 = corner_dna(s, team2, league, match_date)

    dna1 = normalize_team(dna1, lg_stats["mean"], lg_stats["std"])
    dna2 = normalize_team(dna2, lg_stats["mean"], lg_stats["std"])

    lat1 = latent_force(dna1, prior)
    lat2 = latent_force(dna2, prior)

    m = matchup(lat1, lat2, lg_avg)
    lam1_base = m["expected_c1"]
    lam2_base = m["expected_c2"]

    boost1, boost2 = _compute_favorite_boost(odds_1x2)
    lam1 = lam1_base * boost1
    lam2 = lam2_base * boost2

    h2h_stats = _compute_h2h_adjustment(h2h)
    if h2h_stats is not None:
        lam1 = _blend_lambdas(lam1, h2h_stats["corners1_avg"])
        lam2 = _blend_lambdas(lam2, h2h_stats["corners2_avg"])

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

    markets_corners = generate_all(c1_samples, c2_samples)
    for mk in markets_corners:
        mk["sport"] = "corners"

    gdna1 = goal_dna(s, team1, league, match_date)
    gdna2 = goal_dna(s, team2, league, match_date)

    atk1 = gdna1["attack_goals"] or LEAGUE_GOALS_AVG
    def1 = gdna1["defense_goals"] or LEAGUE_GOALS_AVG
    atk2 = gdna2["attack_goals"] or LEAGUE_GOALS_AVG
    def2 = gdna2["defense_goals"] or LEAGUE_GOALS_AVG

    lam_h_goals_base = _adjust_goals_intensity(atk1, def2, LEAGUE_GOALS_AVG)
    lam_a_goals_base = _adjust_goals_intensity(atk2, def1, LEAGUE_GOALS_AVG)

    lam_h_goals = lam_h_goals_base * boost1
    lam_a_goals = lam_a_goals_base * boost2

    if h2h_stats is not None:
        lam_h_goals = _blend_lambdas(lam_h_goals, h2h_stats["goals1_avg"])
        lam_a_goals = _blend_lambdas(lam_a_goals, h2h_stats["goals2_avg"])

    jg = joint_distribution_goals(
        lam_h=lam_h_goals, lam_a=lam_a_goals,
        rho=-0.05,
        n_simulations=n_simulations,
        seed=seed,
    )
    h_samples = jg["h_samples"]
    a_samples = jg["a_samples"]

    markets_goals = generate_all_goals(h_samples, a_samples)
    for mk in markets_goals:
        mk["sport"] = "goals"

    all_markets_raw = markets_corners + markets_goals

    for mk in all_markets_raw:
        mk["prob_raw"] = mk["prob"]
        mk["prob"] = _apply_calibration(mk["prob_raw"], sport=mk["sport"])

    scored = []
    for mk in all_markets_raw:
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

    all_markets = scored

    result = judge(scored)

    abstain, reason = should_abstain(
        result["top"] if result["top"] else {},
        data_quality=(result["top"]["dq"] if result["top"] else 0.0),
    )
    if abstain:
        result["decision"] = "NO_BET"
        result["reason"] = reason

    result["team1"] = team1
    result["team2"] = team2
    result["league"] = league
    result["date"] = match_date.isoformat()
    result["lam1"] = lam1
    result["lam2"] = lam2
    result["lam_h_goals"] = lam_h_goals
    result["lam_a_goals"] = lam_a_goals
    result["goals_outcomes"] = jg["outcomes"]
    result["seed"] = seed
    result["all_markets"] = all_markets
    result["boost1"] = boost1
    result["boost2"] = boost2
    result["h2h_stats"] = h2h_stats

    return result


def run_simple(team1: str, team2: str, league: str,
               match_date: date,
               n_simulations: int = 10000,
               seed: int | None = DEFAULT_SEED,
               odds_1x2: dict | None = None,
               h2h: dict | None = None) -> dict:
    s = make_session()
    try:
        return run(s, team1, team2, league, match_date,
                   n_simulations=n_simulations, seed=seed,
                   odds_1x2=odds_1x2, h2h=h2h)
    finally:
        s.close()
