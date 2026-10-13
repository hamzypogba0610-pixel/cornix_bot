import sys

from cfcx.data.ingest import ingest_all, update_goals


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "insert"

    if mode == "update_goals":
        print("Mode : mise à jour des buts uniquement")
        n = update_goals()
        print(f"Updated {n} matches with goals")
    else:
        print("Mode : ingestion complète")
        n = ingest_all()
        print(f"Inserted {n} matches")


if __name__ == "__main__":
    main()
