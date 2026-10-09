from datetime import date
from sqlalchemy import select
from cfcx.data.store import Match


class LeakageError(Exception):
    pass


def assert_no_leakage(feature_date: date, match_date: date) -> None:
    if feature_date >= match_date:
        raise LeakageError(
            f"Feature computed at {feature_date} >= match date {match_date}"
        )


def features_as_of(s, team: str, league: str, as_of: date, window: int = 10) -> dict:
    """Compute features using ONLY matches strictly before as_of."""
    stmt = (
        select(Match)
        .where(Match.league == league)
        .where(Match.date < as_of)
        .where((Match.home_team == team) | (Match.away_team == team))
        .order_by(Match.date.desc())
        .limit(window)
    )
    rows = s.execute(stmt).scalars().all()
    if not rows:
        return {"matches_played": 0, "corners_for_avg": None, "corners_against_avg": None}

    for_, against = [], []
    for m in rows:
        if m.home_team == team:
            for_.append(m.home_corners)
            against.append(m.away_corners)
        else:
            for_.append(m.away_corners)
            against.append(m.home_corners)

    return {
        "matches_played": len(rows),
        "corners_for_avg": sum(for_) / len(for_),
        "corners_against_avg": sum(against) / len(against),
  }
