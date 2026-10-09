import argparse
from datetime import date

from cfcx.data.store import session as make_session
from cfcx.backtest.walk_forward import run_walk_forward
from cfcx.calibration.trainer import (
    collect_pairs,
    train_and_evaluate,
    save_calibrator,
    save_beta_calibrator,
)
from cfcx.calibration.isotonic import fit_isotonic
from cfcx.calibration.beta import fit_beta


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

        if "error" in report:
            print(f"ERREUR : {report['error']}")
            return

        print()
        print("=" * 60)
        print("COMPARAISON DES MÉTHODES DE CALIBRATION")
        print("=" * 60)
        print(f"  n_samples: {report['n_samples']}")
        print(f"  n_train:   {report['n_train']}")
        print(f"  n_test:    {report['n_test']}")
        print()
        print(f"  {'Métrique':<18} {'Raw':<12} {'Isotonic':<12} {'Beta':<12}")
        print(f"  {'-' * 54}")

        iso = report["isotonic"]
        beta = report["beta"]

        print(f"  {'ECE':<18} {iso['ece_raw']:<12.4f} "
              f"{iso['ece']:<12.4f} {beta['ece']:<12.4f}")
        print(f"  {'Brier':<18} {iso['brier_raw']:<12.4f} "
              f"{iso['brier']:<12.4f} {beta['brier']:<12.4f}")
        print(f"  {'LogLoss':<18} {iso['logloss_raw']:<12.4f} "
              f"{iso['logloss']:<12.4f} {beta['logloss']:<12.4f}")

        print()
        print(f"  MEILLEURE MÉTHODE : {report['best_method'].upper()}")

        # Sauvegarder la meilleure
        if report["best_method"] == "beta":
            params = fit_beta(probs, outcomes)
            save_beta_calibrator(params, args.output)
        else:
            iso_model = fit_isotonic(probs, outcomes)
            save_calibrator(iso_model, args.output)

        print(f"  Calibrateur sauvegardé dans : {args.output}")
    finally:
        s.close()


if __name__ == "__main__":
    main()
