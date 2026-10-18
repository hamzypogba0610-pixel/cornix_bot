"""
Loi jointe 4D via facteur latent.
CORNER FUSION LAB v1.0, Couches E (dependance) + G (probabilites exactes).

P(H1, H2, A1, A2) = integral de [prod P(C_k | U)] * phi(U) dU
avec log(lambda_k(U)) = log(mu_k) + a_k * U, U ~ N(0,1).
"""
import numpy as np
from scipy.stats import poisson, nbinom
from scipy.special import roots_hermite


SEUIL_DEPENDANCE = 0.10
N_QUAD_DEFAUT = 15
KMAX_DEFAUT = 20


def _poisson_pmf(kmax, mu):
    return poisson.pmf(np.arange(kmax + 1), max(float(mu), 1e-9))


def _nbinom_pmf(kmax, mu, r):
    r = max(float(r), 1e-6)
    mu = max(float(mu), 1e-9)
    p = r / (r + mu)
    return nbinom.pmf(np.arange(kmax + 1), r, p)


def _pmf(kmax, mu, distribution, r):
    if distribution == "poisson":
        return _poisson_pmf(kmax, mu)
    if distribution == "nbinom":
        return _nbinom_pmf(kmax, mu, r)
    raise ValueError(f"Unknown distribution: {distribution}")


def _joint_given_U(mu_vec, a_vec, U, kmax, distribution, r_vec):
    lambdas = np.asarray(mu_vec, dtype=float) * np.exp(
        np.asarray(a_vec, dtype=float) * U
    )
    pmfs = [
        _pmf(kmax, lambdas[k], distribution,
             r_vec[k] if r_vec is not None else None)
        for k in range(4)
    ]
    return np.einsum("i,j,k,l->ijkl", pmfs[0], pmfs[1], pmfs[2], pmfs[3])


def joint_4d_latent(mu_vec, a_vec, kmax=KMAX_DEFAUT,
                    n_quad=N_QUAD_DEFAUT, distribution="poisson",
                    r_vec=None):
    """
    P(H1, H2, A1, A2) par integration sur U (Gauss-Hermite).
    mu_vec : [mu_H1, mu_H2, mu_A1, mu_A2]
    a_vec  : [a_H1, a_H2, a_A1, a_A2] (forces du facteur latent)
    """
    nodes, weights = roots_hermite(n_quad)
    U_pts = nodes * np.sqrt(2.0)
    w_pts = weights / np.sqrt(np.pi)

    joint = np.zeros((kmax + 1,) * 4)
    for U, w in zip(U_pts, w_pts):
        joint += w * _joint_given_U(mu_vec, a_vec, U, kmax,
                                    distribution, r_vec)

    total = joint.sum()
    if total > 0:
        joint = joint / total
    return joint


def _bincount_pmf(values_arr, weights_arr):
    """Distribution via bincount (rapide et exacte)."""
    if values_arr.size == 0:
        return {}
    vmax = int(values_arr.max())
    arr = np.bincount(values_arr.astype(int),
                      weights=weights_arr,
                      minlength=vmax + 1)
    return {i: float(arr[i]) for i in range(len(arr))
            if arr[i] > 1e-15}


def marges_depuis_joint_4d(joint_4d):
    """Toutes les marginelles utiles depuis la loi jointe 4D."""
    kmax = joint_4d.shape[0] - 1
    r = np.arange(kmax + 1)

    m_H1 = joint_4d.sum(axis=(1, 2, 3))
    m_H2 = joint_4d.sum(axis=(0, 2, 3))
    m_A1 = joint_4d.sum(axis=(0, 1, 3))
    m_A2 = joint_4d.sum(axis=(0, 1, 2))

    h1, h2, a1, a2 = np.meshgrid(r, r, r, r, indexing="ij")
    T_vals = (h1 + h2 + a1 + a2).ravel()
    MC_vals = (h1 * h2 + a1 * a2).ravel()
    weights = joint_4d.ravel()

    T_pmf = _bincount_pmf(T_vals, weights)
    MC_pmf = _bincount_pmf(MC_vals, weights)

    joint_12 = joint_4d.sum(axis=(2, 3))
    h1_2d, h2_2d = np.meshgrid(r, r, indexing="ij")
    MC1_vals = (h1_2d * h2_2d).ravel()
    MC1_pmf = _bincount_pmf(MC1_vals, joint_12.ravel())

    joint_34 = joint_4d.sum(axis=(0, 1))
    a1_2d, a2_2d = np.meshgrid(r, r, indexing="ij")
    MC2_vals = (a1_2d * a2_2d).ravel()
    MC2_pmf = _bincount_pmf(MC2_vals, joint_34.ravel())

    return {
        "H1": {"pmf": m_H1, "mean": float((r * m_H1).sum())},
        "H2": {"pmf": m_H2, "mean": float((r * m_H2).sum())},
        "A1": {"pmf": m_A1, "mean": float((r * m_A1).sum())},
        "A2": {"pmf": m_A2, "mean": float((r * m_A2).sum())},
        "T": {"pmf": T_pmf},
        "MC": {"pmf": MC_pmf},
        "MC1": {"pmf": MC1_pmf},
        "MC2": {"pmf": MC2_pmf},
    }


def estimer_force_latente(rho_obs, seuil=SEUIL_DEPENDANCE, plafond=1.0):
    """
    Estime la force a du facteur latent depuis la correlation observee.
    |rho| < seuil -> a = 0 (independance).
    Sinon map |rho| vers a dans [0.2, plafond].
    """
    if abs(rho_obs) < seuil:
        return 0.0
    a = min(plafond, max(0.2, abs(rho_obs) * 2.0))
    return a if rho_obs > 0 else -a


def p_over_pmf(pmf_dict, ligne):
    """P(X > ligne) depuis un dict {valeur: proba}."""
    return float(sum(p for m, p in pmf_dict.items() if m > ligne))


def moy_pmf(pmf_dict):
    """Esperance depuis un dict {valeur: proba}."""
    return float(sum(k * v for k, v in pmf_dict.items()))


def comparer_independance_vs_latent(mu_vec, kmax=KMAX_DEFAUT):
    """
    Compare a=0 (independance) vs a=0.8 (dependance forte).
    Utile pour diagnostiquer l'impact du facteur latent.
    """
    joint_ind = joint_4d_latent(mu_vec, [0.0] * 4, kmax, n_quad=1)
    joint_dep = joint_4d_latent(mu_vec, [0.8] * 4, kmax, n_quad=15)

    m_ind = marges_depuis_joint_4d(joint_ind)
    m_dep = marges_depuis_joint_4d(joint_dep)

    return {
        "independance": {
            "MC_mean": moy_pmf(m_ind["MC"]["pmf"]),
            "MC_p_over_15_5": p_over_pmf(m_ind["MC"]["pmf"], 15.5),
            "MC_p_over_20_5": p_over_pmf(m_ind["MC"]["pmf"], 20.5),
        },
        "dependance_forte": {
            "MC_mean": moy_pmf(m_dep["MC"]["pmf"]),
            "MC_p_over_15_5": p_over_pmf(m_dep["MC"]["pmf"], 15.5),
            "MC_p_over_20_5": p_over_pmf(m_dep["MC"]["pmf"], 20.5),
        },
  }
