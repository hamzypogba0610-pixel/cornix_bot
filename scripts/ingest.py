from cfcx.data.ingest import ingest_all

if __name__ == "__main__":
    n = ingest_all()
    print(f"Inserted {n} matches")
