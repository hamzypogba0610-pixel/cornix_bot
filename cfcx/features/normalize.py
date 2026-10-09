from sqlalchemy import select, func
from cfcx.data.store import Match


def league_stats(s, league: str, as_of):
    """Calcule la moyenne et l'écart-type des corners totaux d'une ligue
    STRICTEMENT avant as_of."""
    stmt = (
        select(
            func.avg(Match.home_corners + Match.away_corners),
            func.count(Match.match_id),
        )
        .where(Match.league == league)
        .where(Match.date < as_of)
    )
    row = s.execute(stmt).first()
    mean_total = float(row[0]) if row[0] is not None else 0.0
    n = int(row[1]) if row[1] is not None else 0

    if n < 2:
        return {"mean": mean_total, "std": 1.0, "n": n}

    stmt2 = (
        select(Match.home_corners + Match.away_corners)
        .where(Match.league == league)
        .where(Match.date < as_of)
    )
    values = [float(v) for v in s.execute(stmt2).scalars().all()]
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    std = var ** 0.5 if var > 0 else 1.0

    return {"mean": mean, "std": std, "n": n}


def z_score(value: float, mean: float, std: float) -> float:
    """Normalisation z-score classique."""
    if std == 0:
        return 0.0
    return (value - mean) / std


def normalize_team(dna: dict, league_mean: float, league_std: float) -> dict:
    """Normalise les features d'une équipe par rapport à sa ligue."""
    out = dict(dna)

    if dna.get("attack") is not None:
        out["attack_z"] = z_score(dna["attack"], league_mean, league_std)
    else:
        out["attack_z"] = None

    if dna.get("defense") is not None:
        out["defense_z"] = z_score(dna["defense"], league_mean, league_std)
    else:
        out["defense_z"] = None

    if dna.get("attack_recent") is not None:
        out["attack_recent_z"] = z_score(
            dna["attack_recent"], league_mean, league_std
        )
    else:
        out["attack_recent_z"] = None

    if dna.get("defense_recent") is not None:
        out["defense_recent_z"] = z_score(
            dna["defense_recent"], league_mean, league_std
        )
    else:
        out["defense_recent_z"] = None

    return out
