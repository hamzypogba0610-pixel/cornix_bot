from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import func, select

from cfcx.data.store import Match, session as make_session
from cfcx.pipeline import run as run_pipeline
from cfcx.serving.templates import FORM_HTML


app = FastAPI(title="CFC-X API", version="0.4.0")
START_TIME = datetime.now(UTC)

_STATIC_DIR = Path(__file__).parent / "static"
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


class PredictRequest(BaseModel):
    home: str
    away: str
    league: str
    date: str | None = None
    n_simulations: int = 5000
    seed: int | None = 42
    odds_1: float | None = None
    odds_x: float | None = None
    odds_2: float | None = None
    h2h: dict[str, Any] | None = None


def _parse_date(s: str | None) -> date:
    if not s:
        return date.today()
    return date.fromisoformat(s)


def _market_to_dict(m: dict | None) -> dict | None:
    if m is None:
        return None
    return {
        "market_id": m.get("market_id"),
        "family": m.get("family"),
        "sport": m.get("sport"),
        "direction": m.get("direction"),
        "line": m.get("line"),
        "prob": m.get("prob"),
        "prob_raw": m.get("prob_raw"),
        "score": m.get("score"),
        "edge": m.get("edge"),
        "rob": m.get("rob"),
        "mdi": m.get("mdi"),
        "fi": m.get("fi"),
    }


@app.get("/", response_class=HTMLResponse)
def home():
    return FORM_HTML


@app.get("/health")
def health():
    now = datetime.now(UTC)
    return {
        "status": "ok",
        "uptime_seconds": (now - START_TIME).total_seconds(),
        "timestamp": now.isoformat(),
    }


@app.get("/stats")
def stats():
    s = make_session()
    try:
        total = s.execute(select(func.count(Match.match_id))).scalar() or 0
        with_goals = s.execute(
            select(func.count(Match.match_id))
            .where(Match.home_goals.isnot(None))
        ).scalar() or 0
        leagues = s.execute(
            select(Match.league, func.count(Match.match_id))
            .group_by(Match.league)
        ).all()
        return {
            "total_matches": int(total),
            "with_goals": int(with_goals),
            "by_league": {lg: int(cnt) for lg, cnt in leagues},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        s.close()


@app.post("/predict")
def predict(req: PredictRequest):
    try:
        match_date = _parse_date(req.date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Format de date invalide (attendu YYYY-MM-DD)",
        )

    odds_1x2 = None
    if req.odds_1 and req.odds_x and req.odds_2:
        if req.odds_1 > 1 and req.odds_x > 1 and req.odds_2 > 1:
            odds_1x2 = {
                "odds_1": req.odds_1,
                "odds_x": req.odds_x,
                "odds_2": req.odds_2,
            }

    h2h_data = None
    if req.h2h and isinstance(req.h2h, dict) and req.h2h.get("matches"):
        h2h_data = req.h2h

    s = make_session()
    try:
        result = run_pipeline(
            s,
            team1=req.home,
            team2=req.away,
            league=req.league,
            match_date=match_date,
            n_simulations=req.n_simulations,
            seed=req.seed,
            odds_1x2=odds_1x2,
            h2h=h2h_data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        s.close()

    return {
        "team1": result["team1"],
        "team2": result["team2"],
        "league": result["league"],
        "date": result["date"],
        "decision": result["decision"],
        "reason": result["reason"],
        "top": _market_to_dict(result.get("top")),
        "top_per_family": {
            fam: _market_to_dict(m)
            for fam, m in result.get("top_per_family", {}).items()
        },
        "lam1": result.get("lam1"),
        "lam2": result.get("lam2"),
        "lam_h_goals": result.get("lam_h_goals"),
        "lam_a_goals": result.get("lam_a_goals"),
        "goals_outcomes": result.get("goals_outcomes", {}),
        "seed": result.get("seed"),
        "dominance": result.get("dominance", {}),
        "boost1": result.get("boost1", 1.0),
        "boost2": result.get("boost2", 1.0),
        "h2h_stats": result.get("h2h_stats"),
        }
