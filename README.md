# 🎯 Cornix

Bot de prédiction de corners pré-match.

## Utilisation

Ouvre : **https://cornix-bot.onrender.com/**

Remplis le formulaire (Équipe 1, Équipe 2, Championnat, Date) et clique sur "Analyser le match".

## Endpoints

- `GET /` — Formulaire web
- `GET /health` — État du service
- `GET /stats` — Stats base de données
- `POST /predict` — Prédiction d'un match
- `GET /docs` — Documentation API

## Stack

Python 3.11, FastAPI, PostgreSQL, Render, GitHub Actions.

## Structure

- `cfcx/data/` — Ingestion + anti-leakage
- `cfcx/features/` — Corner DNA, forces latentes
- `cfcx/models/` — Poisson, NB, copule, Monte Carlo
- `cfcx/markets/` — Générateur, scoring
- `cfcx/calibration/` — Isotonic
- `cfcx/decision/` — Meta-judge, NO BET
- `cfcx/serving/` — API + formulaire

## Championnats supportés

Premier League, La Liga, Serie A, Bundesliga, Ligue 1.

## Roadmap

- [x] J1-J9 — Pipeline complet + interface
- [ ] J10 — Extensions (UEFA, MLS, live)
- [ ] J11+ — Marchés buts (1X2, O/U buts)
