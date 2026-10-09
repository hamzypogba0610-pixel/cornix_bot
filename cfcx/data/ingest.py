import io
from datetime import datetime
import pandas as pd
import requests
from sqlalchemy import select
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


def parse_matches(df: pd.DataFrame, league_code: str, season: str) -> list[dict]:
    out = []
    for _, row in df.iterrows():
        d = _parse_date(row.get("Date"))
        if d is None:
            continue
        if pd.isna(row.get("HC")) or pd.isna(row.get("AC")):
            continue
        home = str(row["HomeTeam"]).strip()
        away = str(row["AwayTeam"]).strip()
        out.append({
            "match_id": make_match_id(league_code, d, home, away),
            "league": league_code,
            "season": season,
            "date": d,
            "home_team": home,
            "away_team": away,
            "home_corners": int(row["HC"]),
            "away_corners": int(row["AC"]),
        })
    return out


def ingest_all() -> int:
    init_db()
    s = session()

    existing = set(s.execute(select(Match.match_id)).scalars().all())

    season_codes = data_config()["season_codes"]
    all_rows = []
    for lg in leagues():
        for season in seasons():
            print(f"Fetching {lg['code']} {season}...")
            df = fetch_csv(lg["code"], season, season_codes)
            rows = parse_matches(df, lg["code"], season)
            new_rows = [r for r in rows if r["match_id"] not in existing]
            print(f"  -> {len(new_rows)} new matches")
            all_rows.extend(new_rows)

    if all_rows:
        print(f"Bulk inserting {len(all_rows)} matches...")
        s.bulk_insert_mappings(Match, all_rows)
        s.commit()

    total = len(all_rows)
    s.close()
    return total
