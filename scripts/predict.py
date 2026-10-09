import argparse
from cfcx.models.baseline import naive_lambda, p_ge


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", required=True)
    ap.add_argument("--away", required=True)
    ap.add_argument("--league", required=True)
    ap.add_argument("--home-for", type=float, default=5.5)
    ap.add_argument("--away-against", type=float, default=5.0)
    args = ap.parse_args()

    lam1 = naive_lambda(args.home_for, args.away_against)
    lam2 = naive_lambda(args.away_against, args.home_for)
    lam_t = lam1 + lam2

    print(f"Match : {args.home} vs {args.away} ({args.league})")
    print(f"P(C1 >= 5) = {p_ge(lam1, 5):.2f} (naïf)")
    print(f"P(C2 >= 5) = {p_ge(lam2, 5):.2f} (naïf)")
    print(f"P(Total >= 9) = {p_ge(lam_t, 9):.2f} (naïf)")
    print("[PLACEHOLDER J1 — modèle complet en J3]")


if __name__ == "__main__":
    main()
