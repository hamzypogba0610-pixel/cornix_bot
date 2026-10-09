def adjust_attack(attack_latent: float, opponent_defense_latent: float,
                  league_avg: float) -> float:
    """Ajuste l'attaque d'une équipe selon la défense de l'adversaire.

    Si l'adversaire concède plus que la moyenne de la ligue,
    l'attaque ajustée augmente. Sinon, elle diminue.
    """
    if league_avg <= 0:
        return attack_latent
    ratio = opponent_defense_latent / league_avg
    return attack_latent * ratio


def adjust_defense(defense_latent: float, opponent_attack_latent: float,
                   league_avg: float) -> float:
    """Ajuste la défense d'une équipe selon l'attaque de l'adversaire."""
    if league_avg <= 0:
        return defense_latent
    ratio = opponent_attack_latent / league_avg
    return defense_latent * ratio


def matchup(team1_latent: dict, team2_latent: dict, league_avg: float) -> dict:
    """Calcule les forces ajustées de chaque équipe face à son adversaire."""
    a1_adj = adjust_attack(
        team1_latent["attack_latent"],
        team2_latent["defense_latent"],
        league_avg,
    )
    a2_adj = adjust_attack(
        team2_latent["attack_latent"],
        team1_latent["defense_latent"],
        league_avg,
    )
    d1_adj = adjust_defense(
        team1_latent["defense_latent"],
        team2_latent["attack_latent"],
        league_avg,
    )
    d2_adj = adjust_defense(
        team2_latent["defense_latent"],
        team1_latent["attack_latent"],
        league_avg,
    )

    return {
        "attack_1_adj": a1_adj,
        "attack_2_adj": a2_adj,
        "defense_1_adj": d1_adj,
        "defense_2_adj": d2_adj,
        "expected_c1": (a1_adj + d2_adj) / 2.0,
        "expected_c2": (a2_adj + d1_adj) / 2.0,
            }
