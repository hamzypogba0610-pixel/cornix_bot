"""Script de test pour vérifier que SoccerData fonctionne et fournit les corners."""

import sys


def main():
    print("=" * 60)
    print("TEST SOCCERDATA — Vérification de la disponibilité des corners")
    print("=" * 60)

    # 1. Import
    try:
        import soccerdata as sd
        print(f"✅ soccerdata importé (version: {getattr(sd, '__version__', '?')})")
    except ImportError as e:
        print(f"❌ Impossible d'importer soccerdata : {e}")
        sys.exit(1)

    # 2. Ligues disponibles
    print()
    print("--- Ligues FBref disponibles ---")
    try:
        leagues = sd.FBref.available_leagues()
        for lg in leagues:
            print(f"  • {lg}")
    except Exception as e:
        print(f"⚠️  Erreur available_leagues: {e}")

    # 3. Test sur Premier League 2023-2024
    print()
    print("--- Test sur Premier League 2023-2024 ---")
    try:
        fbref = sd.FBref(
            leagues="ENG-Premier League",
            seasons="2023-2024",
        )
        print("✅ Instance FBref créée")
    except Exception as e:
        print(f"❌ Erreur création FBref : {e}")
        sys.exit(1)

    # 4. Schedule
    print()
    print("--- Récupération du calendrier ---")
    try:
        schedule = fbref.read_schedule()
        print(f"✅ {len(schedule)} matchs récupérés")
        print(f"  Colonnes : {list(schedule.columns)[:10]}...")
    except Exception as e:
        print(f"❌ Erreur read_schedule : {e}")

    # 5. Team match stats — tester plusieurs stat_type
    print()
    print("--- Test read_team_match_stats ---")

    stat_types_to_try = ["passing", "passing_types", "possession", "misc", "standard"]

    for st in stat_types_to_try:
        print()
        print(f"  stat_type = '{st}'")
        try:
            stats = fbref.read_team_match_stats(stat_type=st)
            print(f"    ✅ {len(stats)} lignes")
            cols = list(stats.columns)
            print(f"    Colonnes ({len(cols)}) : {cols[:8]}...")

            # Chercher des colonnes contenant "corner"
            corner_cols = [c for c in cols if "corner" in c.lower()]
            if corner_cols:
                print(f"    🎯 COLONNES CORNERS TROUVÉES : {corner_cols}")
        except Exception as e:
            print(f"    ❌ Erreur : {e}")

    print()
    print("=" * 60)
    print("FIN DU TEST")
    print("=" * 60)


if __name__ == "__main__":
    main()
