import argparse
from datetime import date

from cfcx.data.store import session as make_session
from cfcx.backtest.walk_forward import run_walk_forward
from cfcx.calibration.trainer import (
    collect_pairs,
    train_and_evaluate,
    save_calibrator,
)
from cfcx.calibration.isotonic import fit_isotonic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--league", required=True,
                    help="Code ligue : E0, SP1, I1, D1, F1")
    ap.add_argument("--start", required=True,
                    help="Date de début (YYYY-MM-DD)")
    ap.add_argument("--end", required=True,
                    help="Date de fin (YYYY-MM-DD)")
    ap.add_argument("--limit", type=int, default=None,
                    help="Nombre maximum de matchs")
    ap.add_argument("--sims", type=int, default=2000,
                    help="Simulations Monte Carlo par match")
    ap.add_argument("--output", default="calibrator.json",
                    help="Fichier de sortie du calibrateur")
    args = ap.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    s = make_session()
    try:
        print(f"Calibration {args.league} du {start} au {end}")
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
            verbose=False,
        )

        probs, outcomes = collect_pairs(results)
        print(f"Paires collectées : {len(probs)}")

        report = train_and_evaluate(probs, outcomes)

        print()
        print("=" * 50)
        print("RAPPORT DE CALIBRATION")
        print("=" * 50)
        for k, v in report.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.4f}")
            else:
                print(f"  {k}: {v}")

        if "error" not in report and len(probs) >= 20:
            iso = fit_isotonic(probs, outcomes)
            save_calibrator(iso, args.output)
            print()
            print(f"Calibrateur sauvegardé dans : {args.output}")
    finally:
        s.close()


if __name__ == "__main__":
    main()
