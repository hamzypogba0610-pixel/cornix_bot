from datetime import date, datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import func, select

from cfcx.data.store import Match, session as make_session
from cfcx.pipeline import run as run_pipeline
from cfcx.serving.templates import FORM_HTML


app = FastAPI(title="CFC-X API", version="0.1.0")
START_TIME = datetime.utcnow()


class PredictRequest(BaseModel):
    home: str
    away: str
    league: str
    date: str | None = None
    n_simulations: int = 5000
    seed: int | None = 42


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
    return {
        "status": "ok",
        "uptime_seconds": (datetime.utcnow() - START_TIME).total_seconds(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/stats")
def stats():
    """Statistiques sur la base de données."""
    s = make_session()
    try:
        total = s.execute(select(func.count(Match.match_id))).scalar() or 0
        leagues = s.execute(
            select(Match.league, func.count(Match.match_id))
            .group_by(Match.league)
        ).all()
        return {
            "total_matches": int(total),
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
        "seed": result.get("seed"),
        "dominance": result.get("dominance", {}),
    }
