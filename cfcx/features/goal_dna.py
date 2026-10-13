from datetime import date
from sqlalchemy import select
from cfcx.data.store import Match


def team_matches_goals(s, team: str, league: str, as_of: date,
                       limit: int = 20):
    """Récupère les derniers matchs d'une équipe STRICTEMENT avant as_of."""
    stmt = (
        select(Match)
        .where(Match.league == league)
        .where(Match.date < as_of)
        .where((Match.home_team == team) | (Match.away_team == team))
        .where(Match.home_goals.isnot(None))
        .order_by(Match.date.desc())
        .limit(limit)
    )
    return s.execute(stmt).scalars().all()


def extract_goals(match: Match, team: str) -> tuple[int, int]:
    """Retourne (buts_pour, buts_contre) pour l'équipe dans ce match."""
    if match.home_team == team:
        return match.home_goals, match.away_goals
    return match.away_goals, match.home_goals


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return var ** 0.5


def goal_dna(s, team: str, league: str, as_of: date,
             window: int = 10) -> dict:
    """Calcule les features buts pour une équipe."""
    matches = team_matches_goals(s, team, league, as_of, limit=window)

    if not matches:
        return {
            "team": team,
            "league": league,
            "matches_played": 0,
            "attack_goals": None,
            "defense_goals": None,
            "attack_recent_goals": None,
            "defense_recent_goals": None,
            "home_attack_goals": None,
            "away_attack_goals": None,
            "goals_for_std": None,
            "goals_against_std": None,
        }

    for_, against = [], []
    home_for, away_for = [], []

    for m in matches:
        f, a = extract_goals(m, team)
        for_.append(f)
        against.append(a)
        if m.home_team == team:
            home_for.append(f)
        else:
            away_for.append(f)

    n = len(matches)
    recent_n = min(5, n)

    return {
        "team": team,
        "league": league,
        "matches_played": n,
        "attack_goals": sum(for_) / n,
        "defense_goals": sum(against) / n,
        "attack_recent_goals": sum(for_[:recent_n]) / recent_n,
        "defense_recent_goals": sum(against[:recent_n]) / recent_n,
        "home_attack_goals": (
            sum(home_for) / len(home_for) if home_for else None
        ),
        "away_attack_goals": (
            sum(away_for) / len(away_for) if away_for else None
        ),
        "goals_for_std": _std(for_),
        "goals_against_std": _std(against),
                         }
