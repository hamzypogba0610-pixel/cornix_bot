# 🎯 Cornix — CFC-X

**Pre-match corner prediction engine with calibrated probabilities and automatic market selection.**

Bot de prédiction de corners **pré-match**. Analyse un match, produit une distribution jointe des corners, génère automatiquement tous les marchés candidats, calibre les probabilités, et choisit le marché optimal — ou s'abstient.

---

## 🎯 Philosophie

Le bot ne dit pas *« je prédis 8 corners »*.

Il dit *« voici la distribution complète, voici les marchés possibles, voici leurs probabilités calibrées, leur robustesse, leur fragilité, et voici lequel domine réellement — ou je m'abstiens »*.

**L'abstention (NO BET) est une fonctionnalité centrale, pas un échec.**

---

## 🚀 Utilisation

### 1. Formulaire web (le plus simple)

Ouvre : **https://cornix-bot.onrender.com/**

Remplis :
- Équipe 1 (domicile)
- Équipe 2 (extérieur)
- Championnat
- Date

Clique sur **Analyser le match**.

### 2. API HTTP

```bash
curl -X POST https://cornix-bot.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "home": "Liverpool",
    "away": "Arsenal",
    "league": "E0",
    "date": "2026-10-15",
    "n_simulations": 5000
  }'

{
  "team1": "Liverpool",
  "team2": "Arsenal",
  "decision": "BET",
  "top": {"market_id": "T1_U10.5", "prob": 0.943, "edge": 0.099},
  "top_per_family": {
    "team1": {...},
    "team2": {...},
    "total": {...},
    "multicorner": {...}
  }
}

Endpoint Description
GET / Formulaire web
GET /health État du service
GET /stats Statistiques base de données
POST /predict Prédiction d'un match
GET /docs Documentation Swagger

DONNÉES (football-data.co.uk)
   ↓
ANTI-LEAKAGE FIREWALL
   ↓
CORNER DNA (features par équipe)
   ↓
NORMALISATION PAR CHAMPIONNAT
   ↓
FORCES LATENTES (shrinkage bayésien)
   ↓
AJUSTEMENT ADVERSAIRE + AVANTAGE DOMICILE
   ↓
MATCHUP → λ1, λ2
   ↓
POISSON + NB + COMPOUND POISSON
   ↓
COPULE GAUSSIENNE → P(C1, C2)
   ↓
MONTE CARLO (5000 simulations, seed fixe)
   ↓
GÉNÉRATEUR DE MARCHÉS (~60 candidats)
   ↓
CALIBRATION ISOTONIC
   ↓
SCORING (7 métriques + edge)
   ↓
META-JUDGE + MDS
   ↓
BET / NO BET

cornix_bot/
├── cfcx/
│   ├── data/          # ingestion + anti-leakage
│   ├── features/      # Corner DNA, forces latentes
│   ├── models/        # Poisson, NB, copule, Monte Carlo
│   ├── markets/       # générateur, métriques, scoring
│   ├── calibration/   # isotonic, beta
│   ├── decision/      # meta-judge, no-bet
│   ├── backtest/      # walk-forward, évaluateur
│   └── serving/       # API FastAPI + formulaire
├── configs/
│   ├── leagues.yaml
│   ├── data.yaml
│   └── calibrator.json
├── scripts/
│   ├── ingest.py
│   ├── predict.py
│   ├── backtest.py
│   └── calibrate.py
└── .github/workflows/
    ├── ci.yml
    ├── ingest.yml
    ├── backtest.yml
    └── calibrate.yml

 Stack technique

· Python 3.11
· FastAPI + Uvicorn (API)
· SQLAlchemy + PostgreSQL (données)
· pandas, NumPy, SciPy (calcul)
· scikit-learn (calibration isotonic)
· Render (hébergement)
· GitHub Actions (CI + cron)

---

🧪 Workflows GitHub Actions

Workflow Rôle
CI Tests + lint à chaque push
Ingest Ingestion quotidienne (6h UTC)
Backtest Lancer un backtest manuel
Calibrate Entraîner le calibrateur

Lancer un workflow manuellement :

1. Aller dans Actions
2. Cliquer sur le workflow
3. Cliquer sur Run workflow
4. Remplir les paramètres
5. Cliquer sur le bouton vert

---

🎯 Championnats supportés

· Premier League (E0)
· La Liga (SP1)
· Serie A (I1)
· Bundesliga (D1)
· Ligue 1 (F1)

Extension future : Ligue des Champions, Europa League, Ligue des Nations, MLS, Saudi Pro League.

---

📊 Marchés générés

· Équipe 1 : Over/Under 3.5 à 12.5
· Équipe 2 : Over/Under 3.5 à 12.5
· Total : Over/Under 5.5 à 14.5
· Multi Corner : combinaisons Équipe + Total

---

⚠️ Limites connues

1. Pré-match uniquement (pas de live).
2. Zone de calibration étroite : le calibrateur est entraîné sur une plage restreinte de probabilités.
3. Pas de vraies cotes corners historiques : le ROI backtest est théorique.
4. Facteur domicile simple (+10% / -9%) — pas encore affiné par équipe.
5. Base Render gratuite expire le 8 novembre 2026.

---

🔧 Installation locale (développement)

```bash
# Cloner
git clone https://github.com/hamzypogba0610-pixel/cornix_bot.git
cd cornix_bot

# Environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer
pip install -e ".[dev]"

# Variables d'environnement
cp .env.example .env
# Éditer .env avec DATABASE_URL

# Ingestion
python scripts/ingest.py

# Tests
pytest -q

# Lancer l'API
uvicorn cfcx.serving.api:app --reload
```

---

📌 Roadmap

☑ J1 — Socle, ingestion, CI
☑ J2 — Corner DNA + forces latentes
☑ J3 — Modèles + copule + Monte Carlo
☑ J4 — Générateur + scoring marchés
☑ J5 — Calibration + décision
☑ J6 — Pipeline + backtest
☑ J7 — Calibration apprise
☑ J7.5 — Edge au scoring
☑ J8 — Interface (formulaire + API)
☑ J8.5 — Avantage domicile
☑ J9 — Finalisation (seed + monitoring + doc)
☐ J10 — Extensions (UEFA, MLS, live)
☐ J11+ — Marchés buts (1X2, O/U buts, handicap)

---

📄 License

Projet privé — usage personnel.

---

📬 Contact

GitHub : @hamzypogba0610-pixel

```

**Commit message :**

```

J9: README complet

```

---

## 🎯 Après ce fichier

**J9 sera terminé.**

On aura :
- ✅ Bot **complet** (pipeline, calibration, décision)
- ✅ **Interface web** utilisable
- ✅ **API** documentée
- ✅ **Monitoring** basique (`/stats`)
- ✅ **Reproductibilité** (seed fixe)
- ✅ **Documentation** complète

---
