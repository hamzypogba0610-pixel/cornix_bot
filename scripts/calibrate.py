import argparse
from datetime import date
from pathlib import Path

from cfcx.data.store import session as make_session
from cfcx.backtest.walk_forward import run_walk_forward
from cfcx.calibration.trainer import (
    collect_all_pairs,
    train_and_evaluate,
    save_calibrator,
)
from cfcx.calibration.isotonic import fit_isotonic


def _print_report(label: str, report: dict) -> None:
    print()
    print("=" * 60)
    print(f"RAPPORT — {label}")
    print("=" * 60)
    if "error" in report:
        print(f"  ERREUR : {report['error']}")
        return

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--league", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--output-corners", default="calibrator.json")
    ap.add_argument("--output-goals", default="calibrator_goals.json")
    args = ap.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    s = make_session()
    try:
        print(f"Calibration {args.league} du {start} au {end}")
        print(f"Simulations : {args.sims}")
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

        # =====================================================
        # CALIBRATION CORNERS
        # =====================================================
        print()
        print(">>> CORNERS <<<")
        probs_c, outcomes_c = collect_all_pairs(results, sport="corners")
        print(f"Paires corners collectées : {len(probs_c)}")

        report_c = train_and_evaluate(probs_c, outcomes_c)
        _print_report("CORNERS", report_c)

        if "error" not in report_c and len(probs_c) >= 20:
            iso_c = fit_isotonic(probs_c, outcomes_c)
            save_calibrator(iso_c, args.output_corners)
            print(f"  -> Sauvegardé : {args.output_corners}")

        # =====================================================
        # CALIBRATION BUTS
        # =====================================================
        print()
        print(">>> BUTS <<<")
        probs_g, outcomes_g = collect_all_pairs(results, sport="goals")
        print(f"Paires buts collectées : {len(probs_g)}")

        report_g = train_and_evaluate(probs_g, outcomes_g)
        _print_report("BUTS", report_g)

        if "error" not in report_g and len(probs_g) >= 20:
            iso_g = fit_isotonic(probs_g, outcomes_g)
            save_calibrator(iso_g, args.output_goals)
            print(f"  -> Sauvegardé : {args.output_goals}")

        # =====================================================
        # CONTENU JSON POUR COPIE MANUELLE
        # =====================================================
        print()
        print("=" * 60)
        print("CONTENU JSON — CORNERS (configs/calibrator.json)")
        print("=" * 60)
        try:
            print(Path(args.output_corners).read_text())
        except Exception as e:
            print(f"Erreur lecture : {e}")

        print()
        print("=" * 60)
        print("CONTENU JSON — BUTS (configs/calibrator_goals.json)")
        print("=" * 60)
        try:
            print(Path(args.output_goals).read_text())
        except Exception as e:
            print(f"Erreur lecture : {e}")

    finally:
        s.close()


if __name__ == "__main__":
    main()
