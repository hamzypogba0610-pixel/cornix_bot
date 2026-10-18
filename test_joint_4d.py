"""Tests du module joint_4d (Couches E + G)."""
import numpy as np
from core.joint_4d import (
    joint_4d_latent, marges_depuis_joint_4d,
    estimer_force_latente, p_over_pmf, moy_pmf,
    comparer_independance_vs_latent,
)


def test_independance_somme_a_un():
    mu = [3.0, 3.5, 2.5, 3.0]
    joint = joint_4d_latent(mu, [0.0] * 4, kmax=15, n_quad=1)
    s = joint.sum()
    assert abs(s - 1.0) < 1e-6, f"somme={s}"
    print(f"  OK : independance somme=1")


def test_dependance_somme_a_un():
    mu = [3.0, 3.5, 2.5, 3.0]
    joint = joint_4d_latent(mu, [0.5] * 4, kmax=15, n_quad=15)
    s = joint.sum()
    assert abs(s - 1.0) < 1e-6, f"somme={s}"
    print(f"  OK : dependance somme=1")


def test_independance_egale_produit_poisson():
    """a=0 doit egaler le produit des Poissons marginales."""
    from scipy.stats import poisson
    mu = [3.0, 2.0, 2.5, 3.0]
    joint = joint_4d_latent(mu, [0.0] * 4, kmax=10, n_quad=1)
    # Verifier P(2, 3, 1, 4) = prod des Poissons
    attendu = (poisson.pmf(2, mu[0]) * poisson.pmf(3, mu[1])
               * poisson.pmf(1, mu[2]) * poisson.pmf(4, mu[3]))
    assert abs(joint[2, 3, 1, 4] - attendu) < 1e-8, (
        f"joint={joint[2, 3, 1, 4]}, attendu={attendu}"
    )
    print(f"  OK : a=0 redonne produit de Poissons")


def test_dependance_positive_augmente_diagonale():
    """a>0 doit concentrer la masse sur les coordonnees concordantes."""
    mu = [3.0, 3.0, 3.0, 3.0]
    joint_ind = joint_4d_latent(mu, [0.0] * 4, kmax=15, n_quad=1)
    joint_dep = joint_4d_latent(mu, [0.6] * 4, kmax=15, n_quad=15)
    # Diagonale : P(C=C pour tous)
    diag_ind = sum(joint_ind[k, k, k, k] for k in range(16))
    diag_dep = sum(joint_dep[k, k, k, k] for k in range(16))
    assert diag_dep > diag_ind, (
        f"diagonale dep ({diag_dep}) devrait > ind ({diag_ind})"
    )
    print(f"  OK : diagonale {diag_ind:.4f} -> {diag_dep:.4f}")


def test_marges_somment_a_un():
    mu = [3.0, 3.5, 2.5, 3.0]
    joint = joint_4d_latent(mu, [0.3] * 4, kmax=15, n_quad=10)
    marges = marges_depuis_joint_4d(joint)
    for nom in ("H1", "H2", "A1", "A2"):
        s = marges[nom]["pmf"].sum()
        assert abs(s - 1.0) < 1e-6, f"{nom} somme={s}"
    for nom in ("T", "MC", "MC1", "MC2"):
        s = sum(marges[nom]["pmf"].values())
        assert abs(s - 1.0) < 1e-6, f"{nom} somme={s}"
    print(f"  OK : toutes les marges somment a 1")


def test_moyenne_mc_coherente():
    """E[MC] doit approximer le calcul direct via les marges."""
    mu = [3.0, 3.5, 2.5, 3.0]
    joint = joint_4d_latent(mu, [0.4] * 4, kmax=15, n_quad=10)
    marges = marges_depuis_joint_4d(joint)
    mc_mean = moy_pmf(marges["MC"]["pmf"])
    # E[MC] = E[H1*H2] + E[A1*A2], approxime par marges H et A
    h1 = marges["H1"]["mean"]
    h2 = marges["H2"]["mean"]
    a1 = marges["A1"]["mean"]
    a2 = marges["A2"]["mean"]
    # Avec dependance, E[H1*H2] > E[H1]*E[H2]
    attendu_min = h1 * h2 + a1 * a2
    assert mc_mean >= attendu_min - 1e-6, (
        f"E[MC]={mc_mean} devrait >= {attendu_min}"
    )
    print(f"  OK : E[MC]={mc_mean:.3f} >= prod={attendu_min:.3f}")


def test_p_over_coherent():
    pmf = {0: 0.2, 5: 0.3, 10: 0.3, 20: 0.2}
    assert abs(p_over_pmf(pmf, 12.5) - 0.2) < 1e-9
    assert abs(p_over_pmf(pmf, 4.5) - 0.8) < 1e-9
    assert p_over_pmf(pmf, 100.5) == 0.0
    print("  OK : P_over")


def test_estimer_force_latente_independance():
    a = estimer_force_latente(0.05, seuil=0.10)
    assert a == 0.0
    print("  OK : rho faible -> a=0")


def test_estimer_force_latente_moderee():
    a = estimer_force_latente(0.25, seuil=0.10)
    assert 0.2 <= a <= 1.0
    print(f"  OK : rho=0.25 -> a={a:.2f}")


def test_comparer_produit_utilisable():
    mu = [3.0, 3.0, 3.0, 3.0]
    r = comparer_independance_vs_latent(mu, kmax=15)
    assert "independance" in r
    assert "dependance_forte" in r
    assert r["dependance_forte"]["MC_mean"] > r["independance"]["MC_mean"]
    print(f"  OK : MC_mean ind={r['independance']['MC_mean']:.2f} "
          f"-> dep={r['dependance_forte']['MC_mean']:.2f}")


def test_p_over_augmente_avec_dependance():
    """A queue lourde, la dependance positive augmente les extremes."""
    mu = [3.0, 3.0, 3.0, 3.0]
    r = comparer_independance_vs_latent(mu, kmax=15)
    p_ind = r["independance"]["MC_p_over_20_5"]
    p_dep = r["dependance_forte"]["MC_p_over_20_5"]
    assert p_dep > p_ind, f"P(>20.5) dep={p_dep} devrait > ind={p_ind}"
    print(f"  OK : P(MC>20.5) {p_ind:.4f} -> {p_dep:.4f}")


if __name__ == "__main__":
    tests = [
        test_independance_somme_a_un,
        test_dependance_somme_a_un,
        test_independance_egale_produit_poisson,
        test_dependance_positive_augmente_diagonale,
        test_marges_somment_a_un,
        test_moyenne_mc_coherente,
        test_p_over_coherent,
        test_estimer_force_latente_independance,
        test_estimer_force_latente_moderee,
        test_comparer_produit_utilisable,
        test_p_over_augmente_avec_dependance,
    ]
    print("=== Tests joint_4d (Couches E + G) ===\n")
    r = 0
    for t in tests:
        try:
            t(); r += 1
        except Exception as e:
            print(f"  ECHEC : {t.__name__} -> {e}")
    print(f"\n=== {r}/{len(tests)} tests reussis ===")
    if r != len(tests):
        raise SystemExit(1)
