import sys

from sqlalchemy import text

from cfcx.data.ingest import ingest_all, update_goals
from cfcx.data.store import engine


def reset_matches_table():
    """Supprime la table matches pour repartir sur le bon schéma."""
    eng = engine()
    with eng.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS matches CASCADE"))
        conn.commit()
    print("Table matches supprimee")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "insert"

    if mode == "reset":
        print("Mode : reset (drop + ingest complete)")
        reset_matches_table()
        n = ingest_all()
        print(f"Inserted {n} matches (apres reset)")

    elif mode == "update_goals":
        print("Mode : mise a jour des buts uniquement")
        n = update_goals()
        print(f"Updated {n} matches with goals")

    else:
        print("Mode : ingestion complete")
        n = ingest_all()
        print(f"Inserted {n} matches")


if __name__ == "__main__":
    main()
