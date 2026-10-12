from datetime import date

from sqlalchemy import select

from cfcx.data.store import Match
from cfcx.pipeline import run as run_pipeline


def select_test_matches(s, league: str,
                        start_date: date,
                        end_date: date,
                        limit: int | None = None) -> list[Match]:
    """Sélectionne les matchs à tester entre deux dates."""
    stmt = (
        select(Match)
        .where(Match.league == league)
        .where(Match.date >= start_date)
        .where(Match.date <= end_date)
        .order_by(Match.date.asc())
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    return s.execute(stmt).scalars().all()


def _check_market(market_id: str, match: Match) -> int | None:
    """Vérifie un marché générique à partir de son ID."""
    real_total = match.home_corners + match.away_corners

    try:
        if market_id.startswith("T1_"):
            return _check_team(match.home_corners, market_id)
        if market_id.startswith("T2_"):
            return _check_team(match.away_corners, market_id)
        if market_id.startswith("TT_"):
            return _check_team(real_total, market_id)
        if market_id.startswith("MC_"):
            return _check_multicorner(
                match.home_corners, match.away_corners, real_total, market_id
            )
    except (ValueError, IndexError):
        return None
    return None


def _line_to_int(line_str: str) -> int:
    return int(float(line_str) + 0.5)


def _check_team(value: int, market_id: str) -> int:
    parts = market_id.split("_")
    direction = parts[1][0]
    line = parts[1][1:]
    threshold = _line_to_int(line)
    if direction == "O":
        return int(value >= threshold)
    return int(value < threshold)


def _check_multicorner(c1: int, c2: int, total: int,
                       market_id: str) -> int:
    parts = market_id.split("_")
    team = parts[1]
    team_part = parts[2]
    total_part = parts[3]

    team_value = c1 if team == "T1" else c2

    team_dir = team_part[0]
    team_line = _line_to_int(team_part[1:])
    total_dir = total_part[1]
    total_line = _line_to_int(total_part[2:])

    if team_dir == "O":
        ok_team = team_value >= team_line
    else:
        ok_team = team_value < team_line

    if total_dir == "O":
        ok_total = total >= total_line
    else:
        ok_total = total < total_line

    return int(ok_team and ok_total)


def evaluate_match(s, match: Match,
                   n_simulations: int = 5000) -> dict:
    """Évalue un match et collecte TOUS les marchés avec leurs résultats."""
    result = run_pipeline(
        s,
        team1=match.home_team,
        team2=match.away_team,
        league=match.league,
        match_date=match.date,
        n_simulations=n_simulations,
    )

    top = result["top"]
    top_outcome = _check_market(top["market_id"], match) if top else None

    # Collecter TOUS les marchés avec leurs outcomes
    all_market_outcomes = []
    for mk in result.get("all_markets", []):
        outcome = _check_market(mk["market_id"], match)
        all_market_outcomes.append({
            "market_id": mk["market_id"],
            "prob": mk.get("prob"),
            "prob_raw": mk.get("prob_raw"),
            "score": mk.get("score"),
            "outcome": outcome,
        })

    return {
        "match_id": match.match_id,
        "date": match.date.isoformat(),
        "home_team": match.home_team,
        "away_team": match.away_team,
        "decision": result["decision"],
        "top_market_id": top["market_id"] if top else None,
        "top_prob": top["prob"] if top else None,
        "top_prob_raw": top.get("prob_raw") if top else None,
        "top_score": top["score"] if top else None,
        "real_c1": match.home_corners,
        "real_c2": match.away_corners,
        "real_total": match.home_corners + match.away_corners,
        "outcome": top_outcome,
        "reason": result["reason"],
        "all_markets": all_market_outcomes,
    }


def check_outcome(top_market: dict | None, match: Match) -> int | None:
    """Compatibilité avec l'ancienne API."""
    if top_market is None:
        return None
    return _check_market(top_market["market_id"], match)


def run_walk_forward(s, league: str,
                     start_date: date,
                     end_date: date,
                     limit: int | None = None,
                     n_simulations: int = 5000,
                     verbose: bool = True) -> list[dict]:
    """Lance un backtest walk-forward."""
    matches = select_test_matches(s, league, start_date, end_date, limit)
    results = []

    for i, m in enumerate(matches):
        try:
            r = evaluate_match(s, m, n_simulations=n_simulations)
            results.append(r)

            if verbose:
                top_id = r["top_market_id"] or "-"
                p_cal = r["top_prob"]
                p_raw = r["top_prob_raw"]
                p_cal_str = f"{p_cal:.3f}" if p_cal is not None else "-"
                p_raw_str = f"{p_raw:.3f}" if p_raw is not None else "-"
                outcome_str = (
                    "WIN" if r["outcome"] == 1
                    else ("LOSS" if r["outcome"] == 0 else "-")
                )
                n_markets = len(r.get("all_markets", []))
                print(
                    f"[{i+1}/{len(matches)}] "
                    f"{m.home_team} vs {m.away_team} "
                    f"| C1={r['real_c1']} C2={r['real_c2']} T={r['real_total']} "
                    f"| {r['decision']:6s} | top={top_id:22s} | "
                    f"raw={p_raw_str} cal={p_cal_str} | {outcome_str} | "
                    f"markets={n_markets}"
                )
        except Exception as e:
            if verbose:
                print(f"[{i+1}/{len(matches)}] "
                      f"{m.home_team} vs {m.away_team} | ERROR : {e}")
            results.append({
                "match_id": m.match_id,
                "date": m.date.isoformat(),
                "decision": "ERROR",
                "outcome": None,
                "reason": str(e),
            })

    return results
