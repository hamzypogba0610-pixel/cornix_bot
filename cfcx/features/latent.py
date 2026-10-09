from datetime import date
from sqlalchemy import select
from cfcx.data.store import Match


def league_prior(s, league: str, as_of: date) -> dict:
    """Estime le prior bayésien de la ligue (moyenne et variance des corners)."""
    stmt = (
        select(Match.home_corners, Match.away_corners)
        .where(Match.league == league)
        .where(Match.date < as_of)
    )
    rows = s.execute(stmt).all()

    if not rows:
        return {"mu": 5.0, "sigma2": 4.0, "n": 0}

    totals = [float(r[0] + r[1]) for r in rows]
    n = len(totals)
    mu = sum(totals) / n

    if n < 2:
        return {"mu": mu, "sigma2": 4.0, "n": n}

    var = sum((t - mu) ** 2 for t in totals) / (n - 1)
    return {"mu": mu / 2.0, "sigma2": var / 4.0, "n": n}


def shrink(observed: float, n_matches: int, prior_mu: float, prior_strength: float = 5.0) -> float:
    """Shrinkage bayésien : mélange l'observation avec le prior selon n_matches.

    Formule : (n * observed + k * prior_mu) / (n + k)
    où k = prior_strength (poids du prior en nombre de matchs équivalents).
    """
    if observed is None or n_matches == 0:
        return prior_mu
    return (n_matches * observed + prior_strength * prior_mu) / (n_matches + prior_strength)


def latent_force(dna: dict, prior: dict) -> dict:
    """Transforme les features brutes en forces latentes (shrinkage bayésien)."""
    out = dict(dna)
    n = dna.get("matches_played", 0) or 0

    out["attack_latent"] = shrink(
        dna.get("attack"), n, prior["mu"], prior_strength=5.0
    )
    out["defense_latent"] = shrink(
        dna.get("defense"), n, prior["mu"], prior_strength=5.0
    )
    out["attack_recent_latent"] = shrink(
        dna.get("attack_recent"), min(n, 5), prior["mu"], prior_strength=3.0
    )
    out["defense_recent_latent"] = shrink(
        dna.get("defense_recent"), min(n, 5), prior["mu"], prior_strength=3.0
    )

    return out
