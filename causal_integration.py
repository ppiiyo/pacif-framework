"""Illustrative Doubly Robust (DR) integration pattern using synthetic PACIF-like features.

IMPORTANT
---------
The features produced by ``generate_pacif_features`` are **synthetic** and are
predictive of the treatment effect **by construction** in this simulation.
Results demonstrate an integration *pattern*, not empirical evidence that PACIF
reduces bias on real observational data.

Run::

    python causal_integration.py
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split


def generate_pacif_features(n: int, seed: int = 42):
    """Synthetic stand-ins for MI / reliability / drift (not real PACIF output)."""
    rng = np.random.default_rng(seed)
    mi = np.abs(rng.normal(0.28, 0.12, n))
    reliable = (rng.random(n) > 0.25).astype(int)
    drift = (rng.random(n) > 0.85).astype(int)
    return mi, reliable, drift


def synthetic_causal_dataset(n: int = 5000, seed: int = 42):
    rng = np.random.default_rng(seed)
    X_base = rng.standard_normal((n, 5))
    mi, reliable, drift = generate_pacif_features(n, seed=seed)
    X = np.column_stack([X_base, mi, reliable, drift])
    logit = 0.6 * X_base[:, 0] - 0.4 * X_base[:, 1]
    e = 1 / (1 + np.exp(-logit))
    T = (rng.random(n) < e).astype(float)
    true_effect = 0.4 + 0.35 * mi * reliable - 0.25 * drift
    Y = (
        1.8 * X_base[:, 0]
        + 1.2 * X_base[:, 2]
        + T * true_effect
        + rng.normal(0, 0.6, n)
    )
    return X, Y, T, e, float(true_effect.mean())


def doubly_robust_ate(X, Y, T, e, use_pacif: bool = True, split_seed: int = 42):
    cols = slice(0, 8) if use_pacif else slice(0, 5)
    X_train, X_test, Y_train, Y_test, T_train, T_test, e_train, e_test = train_test_split(
        X[:, cols], Y, T, e, test_size=0.3, random_state=split_seed
    )
    mu0 = Ridge(alpha=1.0).fit(X_train[T_train == 0], Y_train[T_train == 0])
    mu1 = Ridge(alpha=1.0).fit(X_train[T_train == 1], Y_train[T_train == 1])
    mu_hat = np.where(T_test == 1, mu1.predict(X_test), mu0.predict(X_test))
    weights = T_test / np.clip(e_test, 1e-3, 1 - 1e-3) - (1 - T_test) / np.clip(
        1 - e_test, 1e-3, 1 - 1e-3
    )
    dr_values = mu_hat + weights * (Y_test - mu_hat)
    return float(np.mean(dr_values)), float(np.std(dr_values) / np.sqrt(len(Y_test)))


def monte_carlo(n_seeds: int = 100, n: int = 5000):
    """Bias of DR with and without synthetic PACIF features across seeds."""
    bias_std = []
    bias_pacif = []
    for seed in range(n_seeds):
        X, Y, T, e, true_ate = synthetic_causal_dataset(n=n, seed=seed)
        ate_std, _ = doubly_robust_ate(X, Y, T, e, use_pacif=False, split_seed=seed)
        ate_pacif, _ = doubly_robust_ate(X, Y, T, e, use_pacif=True, split_seed=seed)
        bias_std.append(abs(ate_std - true_ate))
        bias_pacif.append(abs(ate_pacif - true_ate))
    return {
        "n_seeds": n_seeds,
        "bias_std_mean": float(np.mean(bias_std)),
        "bias_std_std": float(np.std(bias_std)),
        "bias_pacif_mean": float(np.mean(bias_pacif)),
        "bias_pacif_std": float(np.std(bias_pacif)),
    }


if __name__ == "__main__":
    X, Y, T, e, true_ate = synthetic_causal_dataset(seed=42)
    ate_std, se_std = doubly_robust_ate(X, Y, T, e, use_pacif=False)
    ate_pacif, se_pacif = doubly_robust_ate(X, Y, T, e, use_pacif=True)
    print(f"True ATE: {true_ate:.4f}")
    print(
        f"Standard DR: {ate_std:.4f} ± {se_std:.4f} | Bias: {abs(ate_std - true_ate):.4f}"
    )
    print(
        f"PACIF-feature DR: {ate_pacif:.4f} ± {se_pacif:.4f} | "
        f"Bias: {abs(ate_pacif - true_ate):.4f}"
    )
    print("\nMonte Carlo (100 seeds; synthetic features predictive by construction):")
    mc = monte_carlo(n_seeds=100)
    print(
        f"  |bias| without features: {mc['bias_std_mean']:.4f} ± {mc['bias_std_std']:.4f}"
    )
    print(
        f"  |bias| with features:    {mc['bias_pacif_mean']:.4f} ± {mc['bias_pacif_std']:.4f}"
    )
