DEFAULT_NO_BET_RULES = {
    "min_data_quality": 0.30,
    "max_fragility": 0.20,
    "min_consensus": 0.40,
}


def should_abstain(top_market: dict,
                   data_quality: float,
                   rules: dict | None = None) -> tuple[bool, str]:
    """Vérifie les conditions d'abstention indépendantes du scoring.

    Retourne (True, raison) si le bot doit s'abstenir,
    (False, "") sinon.
    """
    if rules is None:
        rules = DEFAULT_NO_BET_RULES

    if data_quality < rules["min_data_quality"]:
        return True, f"qualité des données trop faible ({data_quality:.2f})"

    if top_market.get("fi", 0.0) > rules["max_fragility"]:
        return True, f"marché trop fragile (FI={top_market['fi']:.3f})"

    if top_market.get("cons", 1.0) < rules["min_consensus"]:
        return True, f"consensus insuffisant (Cons={top_market['cons']:.2f})"

    return False, ""


def summarize_abstention(reasons: list[str]) -> str:
    """Formate la liste des raisons d'abstention."""
    if not reasons:
        return "aucune"
    return " | ".join(reasons)
