"""Corner Fusion Latent Model — intégration du facteur latent U.

Modèle : les 4 comptes (H1, H2, A1, A2) sont liés par un facteur latent U
qui représente l'intensité globale du match.

  log(mu_k(U)) = log(mu_k) + a * U
  U ~ N(0, 1)

Les coefficients a_k sont fixés à une valeur heuristique (0.20) en V1.
L'estimation bayésienne des a_k est reportée en V2 (nécessite plus de données).
"""

import numpy as np


A_COEFF_DEFAULT = 0.20
N_SIMS_DEFAULT = 10000
SEED_DEFAULT = 42


def simulate_latent_fusion(lam_H1: float, lam_H2: float,
                            lam_A1: float, lam_A2: float,
                            a: float = A_COEFF_DEFAULT,
                            n_sims: int = N_SIMS_DEFAULT,
                            seed: int | None = SEED_DEFAULT) -> dict:
    """Simule (H1, H2, A1, A2) avec un facteur latent commun U.

    Étapes :
    1. Tirer U ~ N(0,1)
    2. Ajuster les moyennes : mu_k_adj = mu_k * exp(a * U)
    3. Tirer les comptes : C_k ~ Poisson(mu_k_adj)
    4. Calculer MC1 = H1*H2, MC2 = A1*A2, MC_global = MC1+MC2
    """
    rng = np.random.default_rng(seed)
    U = rng.normal(0, 1, n_sims)
    factor = np.exp(a * U)

    H1 = rng.poisson(np.maximum(lam_H1 * factor, 0))
    H2 = rng.poisson(np.maximum(lam_H2 * factor, 0))
    A1 = rng.poisson(np.maximum(lam_A1 * factor, 0))
    A2 = rng.poisson(np.maximum(lam_A2 * factor, 0))

    MC1 = H1 * H2
    MC2 = A1 * A2
    MC_global = MC1 + MC2

    return {
        "H1": H1, "H2": H2, "A1": A1, "A2": A2,
        "MC1": MC1, "MC2": MC2, "MC_global": MC_global,
        "a_coeff": a,
    }


def analytical_E_MC(lam_H1: float, lam_H2: float,
                     lam_A1: float, lam_A2: float,
                     a: float = A_COEFF_DEFAULT) -> dict:
    """Calcule E[MC] analytiquement via la formule fermée.

    E[C_k | U] = mu_k * exp(a*U)
    E[exp(a*U)] = exp(a²/2)
    E[exp(2a*U)] = exp(2a²)

    E[H1*H2] = E[E[H1|U]*E[H2|U]]
             = mu_H1 * mu_H2 * E[exp(2a*U)]
             = mu_H1 * mu_H2 * exp(2a²)
    """
    factor = np.exp(2 * a * a)
    E_MC1 = lam_H1 * lam_H2 * factor
    E_MC2 = lam_A1 * lam_A2 * factor
    return {
        "E_MC1": float(E_MC1),
        "E_MC2": float(E_MC2),
        "E_MC_global": float(E_MC1 + E_MC2),
        "factor": float(factor),
        "a_coeff": a,
    }


def analytical_covariance(lam_X: float, lam_Y: float,
                           a: float = A_COEFF_DEFAULT) -> float:
    """Cov(X, Y) induite par le facteur latent U.

    Cov(X, Y) = E[X*Y] - E[X]*E[Y]
              = mu_X * mu_Y * exp(2a²) - mu_X * exp(a²/2) * mu_Y * exp(a²/2)
              = mu_X * mu_Y * (exp(2a²) - exp(a²))
    """
    return float(lam_X * lam_Y * (np.exp(2 * a * a) - np.exp(a * a)))
