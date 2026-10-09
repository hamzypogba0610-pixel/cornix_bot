import numpy as np


DEFAULT_LINES = [3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5]


def _line_to_int(line: float) -> int:
    """Convertit une ligne 'X.5' en entier 'X+1' (Over = C >= X+1)."""
    return int(line + 0.5)


def team_markets(c1_samples: np.ndarray, c2_samples: np.ndarray,
                 lines: list[float] | None = None) -> list[dict]:
    """Génère tous les marchés Équipe 1 et Équipe 2 (Over/Under)."""
    if lines is None:
        lines = DEFAULT_LINES

    markets = []
    n = len(c1_samples)

    for line in lines:
        threshold = _line_to_int(line)

        # Équipe 1
        p1_over = float((c1_samples >= threshold).sum() / n)
        p1_under = 1.0 - p1_over
        if 0.05 < p1_over < 0.95:
            markets.append({
                "market_id": f"T1_O{line}",
                "family": "team1",
                "direction": "over",
                "line": line,
                "prob": p1_over,
            })
        if 0.05 < p1_under < 0.95:
            markets.append({
                "market_id": f"T1_U{line}",
                "family": "team1",
                "direction": "under",
                "line": line,
                "prob": p1_under,
            })

        # Équipe 2
        p2_over = float((c2_samples >= threshold).sum() / n)
        p2_under = 1.0 - p2_over
        if 0.05 < p2_over < 0.95:
            markets.append({
                "market_id": f"T2_O{line}",
                "family": "team2",
                "direction": "over",
                "line": line,
                "prob": p2_over,
            })
        if 0.05 < p2_under < 0.95:
            markets.append({
                "market_id": f"T2_U{line}",
                "family": "team2",
                "direction": "under",
                "line": line,
                "prob": p2_under,
            })

    return markets


def total_markets(c1_samples: np.ndarray, c2_samples: np.ndarray,
                  lines: list[float] | None = None) -> list[dict]:
    """Génère tous les marchés Total (Over/Under)."""
    if lines is None:
        lines = [l + 2.0 for l in DEFAULT_LINES]  # total plus élevé

    markets = []
    n = len(c1_samples)
    total = c1_samples + c2_samples

    for line in lines:
        threshold = _line_to_int(line)

        p_over = float((total >= threshold).sum() / n)
        p_under = 1.0 - p_over

        if 0.05 < p_over < 0.95:
            markets.append({
                "market_id": f"TT_O{line}",
                "family": "total",
                "direction": "over",
                "line": line,
                "prob": p_over,
            })
        if 0.05 < p_under < 0.95:
            markets.append({
                "market_id": f"TT_U{line}",
                "family": "total",
                "direction": "under",
                "line": line,
                "prob": p_under,
            })

    return markets


def multicorner_markets(c1_samples: np.ndarray, c2_samples: np.ndarray,
                        team_lines: list[float] | None = None,
                        total_lines: list[float] | None = None) -> list[dict]:
    """Génère les marchés Multicorner (Équipe + Total combinés).

    Exemple : Équipe1 Over 5.5 ET Total Over 9.5.
    """
    if team_lines is None:
        team_lines = [4.5, 5.5, 6.5]
    if total_lines is None:
        total_lines = [8.5, 9.5, 10.5, 11.5]

    markets = []
    n = len(c1_samples)
    total = c1_samples + c2_samples

    for team_name, team_samples in [("T1", c1_samples), ("T2", c2_samples)]:
        for t_line in team_lines:
            t_thr = _line_to_int(t_line)
            for tt_line in total_lines:
                tt_thr = _line_to_int(tt_line)

                # Over équipe ET Over total
                p_oo = float(
                    ((team_samples >= t_thr) & (total >= tt_thr)).sum() / n
                )
                if 0.05 < p_oo < 0.95:
                    markets.append({
                        "market_id": f"MC_{team_name}_O{t_line}_TO{tt_line}",
                        "family": "multicorner",
                        "team": team_name,
                        "team_direction": "over",
                        "team_line": t_line,
                        "total_direction": "over",
                        "total_line": tt_line,
                        "prob": p_oo,
                    })

                # Under équipe ET Under total
                p_uu = float(
                    ((team_samples < t_thr) & (total < tt_thr)).sum() / n
                )
                if 0.05 < p_uu < 0.95:
                    markets.append({
                        "market_id": f"MC_{team_name}_U{t_line}_TU{tt_line}",
                        "family": "multicorner",
                        "team": team_name,
                        "team_direction": "under",
                        "team_line": t_line,
                        "total_direction": "under",
                        "total_line": tt_line,
                        "prob": p_uu,
                    })

    return markets


def generate_all(c1_samples: np.ndarray, c2_samples: np.ndarray) -> list[dict]:
    """Génère TOUS les marchés candidats (team1 + team2 + total + multicorner)."""
    markets = []
    markets.extend(team_markets(c1_samples, c2_samples))
    markets.extend(total_markets(c1_samples, c2_samples))
    markets.extend(multicorner_markets(c1_samples, c2_samples))
    return markets
