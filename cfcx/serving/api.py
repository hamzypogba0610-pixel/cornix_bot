from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from cfcx.data.store import session as make_session
from cfcx.pipeline import run as run_pipeline


app = FastAPI(title="CFC-X API", version="0.1.0")


class PredictRequest(BaseModel):
    home: str
    away: str
    league: str
    date: str | None = None
    n_simulations: int = 5000


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


@app.get("/health")
def health():
    return {"status": "ok"}


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
        "dominance": result.get("dominance", {}),
    }
