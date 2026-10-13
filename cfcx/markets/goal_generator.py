import numpy as np


MIN_PROB = 0.20
MAX_PROB = 0.90

DEFAULT_OU_LINES = [0.5, 1.5, 2.5, 3.5, 4.5]
DEFAULT_HANDICAP_LINES = [-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0]


def _keep(p: float) -> bool:
    return MIN_PROB < p < MAX_PROB


def outcome_markets(h_samples: np.ndarray, a_samples: np.ndarray) -> list[dict]:
    """Génère les 3 marchés 1X2 (résultat final)."""
    n = len(h_samples)
    if n == 0:
        return []

    markets = []

    p_home = float((h_samples > a_samples).sum() / n)
    p_draw = float((h_samples == a_samples).sum() / n)
    p_away = float((h_samples < a_samples).sum() / n)

    for label, prob, direction in [
        ("1", p_home, "home_win"),
        ("X", p_draw, "draw"),
        ("2", p_away, "away_win"),
    ]:
        if _keep(prob):
            markets.append({
                "market_id": f"1X2_{label}",
                "family": "result",
                "direction": direction,
                "prob": prob,
            })

    return markets


def ou_markets(h_samples: np.ndarray, a_samples: np.ndarray,
               lines: list[float] | None = None) -> list[dict]:
    """Génère les marchés Over/Under buts."""
    if lines is None:
        lines = DEFAULT_OU_LINES

    n = len(h_samples)
    if n == 0:
        return []

    total = h_samples + a_samples
    markets = []

    for line in lines:
        threshold = int(line + 0.5)
        p_over = float((total >= threshold).sum() / n)
        p_under = 1.0 - p_over

        if _keep(p_over):
            markets.append({
                "market_id": f"GB_O{line}",
                "family": "goals_total",
                "direction": "over",
                "line": line,
                "prob": p_over,
            })
        if _keep(p_under):
            markets.append({
                "market_id": f"GB_U{line}",
                "family": "goals_total",
                "direction": "under",
                "line": line,
                "prob": p_under,
            })

    return markets


def handicap_markets(h_samples: np.ndarray, a_samples: np.ndarray,
                     lines: list[float] | None = None) -> list[dict]:
    """Génère les marchés Handicap (asiatique style simple)."""
    if lines is None:
        lines = DEFAULT_HANDICAP_LINES

    n = len(h_samples)
    if n == 0:
        return []

    diff = h_samples - a_samples
    markets = []

    for line in lines:
        # Home cover : diff > line
        p_home = float((diff > line).sum() / n)
        p_away = float((diff < line).sum() / n)

        line_str = f"{line:+.1f}".replace("+", "P").replace("-", "M")

        if _keep(p_home):
            markets.append({
                "market_id": f"HC_{line_str}_H",
                "family": "handicap",
                "direction": "home",
                "line": line,
                "prob": p_home,
            })
        if _keep(p_away):
            markets.append({
                "market_id": f"HC_{line_str}_A",
                "family": "handicap",
                "direction": "away",
                "line": line,
                "prob": p_away,
            })

    return markets


def generate_all_goals(h_samples: np.ndarray, a_samples: np.ndarray) -> list[dict]:
    """Génère TOUS les marchés buts candidats."""
    markets = []
    markets.extend(outcome_markets(h_samples, a_samples))
    markets.extend(ou_markets(h_samples, a_samples))
    markets.extend(handicap_markets(h_samples, a_samples))
    return markets
