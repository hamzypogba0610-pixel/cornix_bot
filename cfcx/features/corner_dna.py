from datetime import date
from sqlalchemy import select
from cfcx.data.store import Match


def team_matches(s, team: str, league: str, as_of: date, limit: int = 20):
    """Récupère les derniers matchs d'une équipe STRICTEMENT avant as_of."""
    stmt = (
        select(Match)
        .where(Match.league == league)
        .where(Match.date < as_of)
        .where((Match.home_team == team) | (Match.away_team == team))
        .order_by(Match.date.desc())
        .limit(limit)
    )
    return s.execute(stmt).scalars().all()


def extract_corners(match: Match, team: str) -> tuple[int, int]:
    """Retourne (corners_pour, corners_contre) pour l'équipe dans ce match."""
    if match.home_team == team:
        return match.home_corners, match.away_corners
    return match.away_corners, match.home_corners


def corner_dna(s, team: str, league: str, as_of: date, window: int = 10) -> dict:
    """Calcule les features de base pour une équipe."""
    matches = team_matches(s, team, league, as_of, limit=window)

    if not matches:
        return {
            "team": team,
            "league": league,
            "matches_played": 0,
            "attack": None,
            "defense": None,
            "attack_recent": None,
            "defense_recent": None,
            "corners_for_std": None,
            "corners_against_std": None,
            "home_attack": None,
            "away_attack": None,
        }

    for_, against = [], []
    home_for, away_for = [], []

    for m in matches:
        f, a = extract_corners(m, team)
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
        "attack": sum(for_) / n,
        "defense": sum(against) / n,
        "attack_recent": sum(for_[:recent_n]) / recent_n,
        "defense_recent": sum(against[:recent_n]) / recent_n,
        "corners_for_std": _std(for_),
        "corners_against_std": _std(against),
        "home_attack": sum(home_for) / len(home_for) if home_for else None,
        "away_attack": sum(away_for) / len(away_for) if away_for else None,
    }


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return var ** 0.5
