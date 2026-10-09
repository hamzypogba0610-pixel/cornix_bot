import argparse
from datetime import date

from cfcx.data.store import session as make_session
from cfcx.backtest.walk_forward import run_walk_forward
from cfcx.backtest.evaluator import full_report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--league", required=True,
                    help="Code ligue : E0, SP1, I1, D1, F1")
    ap.add_argument("--start", required=True,
                    help="Date de début (YYYY-MM-DD)")
    ap.add_argument("--end", required=True,
                    help="Date de fin (YYYY-MM-DD)")
    ap.add_argument("--limit", type=int, default=None,
                    help="Nombre maximum de matchs à tester")
    ap.add_argument("--sims", type=int, default=3000,
                    help="Nombre de simulations Monte Carlo par match")
    args = ap.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    s = make_session()
    try:
        print(f"Backtest {args.league} du {start} au {end}")
        print(f"Simulations par match : {args.sims}")
        if args.limit:
            print(f"Limite : {args.limit} matchs")
        print("---")

        results = run_walk_forward(
            s,
            league=args.league,
            start_date=start,
            end_date=end,
            limit=args.limit,
            n_simulations=args.sims,
            verbose=True,
        )

        report = full_report(results)

        print()
        print("=" * 50)
        print("RÉSUMÉ")
        print("=" * 50)
        for k, v in report["summary"].items():
            print(f"  {k}: {v}")

        print()
        print("ROI")
        for k, v in report["roi"].items():
            print(f"  {k}: {v}")

        print()
        print("CALIBRATION")
        print(f"  ECE: {report['calibration']['ece']:.4f}")
    finally:
        s.close()


if __name__ == "__main__":
    main()
