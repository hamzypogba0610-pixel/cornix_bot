from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="CFC-X API", version="0.1.0")


class PredictRequest(BaseModel):
    home: str
    away: str
    league: str


class PredictResponse(BaseModel):
    home: str
    away: str
    league: str
    p_home_ge5: float
    p_away_ge5: float
    p_total_ge9: float
    note: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    return PredictResponse(
        home=req.home, away=req.away, league=req.league,
        p_home_ge5=0.62, p_away_ge5=0.48, p_total_ge9=0.55,
        note="placeholder J1",
  )
