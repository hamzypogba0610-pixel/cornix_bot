from datetime import datetime
from pydantic import BaseModel


class RawMatch(BaseModel):
    match_id: str
    league: str
    season: str
    date: datetime
    home_team: str
    away_team: str
    home_corners: int | None = None
    away_corners: int | None = None


def make_match_id(league: str, date: datetime, home: str, away: str) -> str:
    return f"{league}_{date:%Y%m%d}_{home}_{away}".replace(" ", "_")
