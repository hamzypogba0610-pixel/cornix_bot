import io
from datetime import datetime
import pandas as pd
import requests
from cfcx.config import data_config, leagues, seasons
from cfcx.data.schema import make_match_id
from cfcx.data.store import Match, init_db, session


def _parse_date(val) -> datetime | None:
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(str(val).strip(), fmt)
        except (ValueError, TypeError):
            continue
    return None


def fetch_csv(league_code: str, season: str, season_codes: dict) -> pd.DataFrame:
    code = season_codes[season]
    url = f"{data_config()['base_url']}/{code}/{league_code}.csv"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text), on_bad_lines="skip")


def parse_matches(df: pd.DataFrame, league_code: str, season: str) -> list[Match]:
    out = []
    for _, row in df.iterrows():
        d = _parse_date(row.get("Date"))
        if d is None:
            continue
        if pd.isna(row.get("HC")) or pd.isna(row.get("AC")):
            continue
        home = str(row["HomeTeam"]).strip()
        away = str(row["AwayTeam"]).strip()
        out.append(Match(
            match_id=make_match_id(league_code, d, home, away),
            league=league_code,
            season=season,
            date=d,
            home_team=home,
            away_team=away,
            home_corners=int(row["HC"]),
            away_corners=int(row["AC"]),
        ))
    return out


def ingest_all() -> int:
    init_db()
    s = session()
    inserted = 0
    season_codes = data_config()["season_codes"]
    for lg in leagues():
        for season in seasons():
            df = fetch_csv(lg["code"], season, season_codes)
            for m in parse_matches(df, lg["code"], season):
                if not s.get(Match, m.match_id):
                    s.add(m)
                    inserted += 1
            s.commit()
    s.close()
    return inserted
