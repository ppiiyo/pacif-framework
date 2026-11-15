"""Bias-corrected mutual information estimator for predictive alignment.

The asymptotic CI assumes i.i.d. samples; autocorrelated logs yield
overconfident intervals. Use method='bootstrap' for dependent sequences.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Union

import numpy as np
from numba import njit


@njit(cache=True)
def _calculate_mi_and_stats(events, contexts, n_u, n_s, N):
    """Return mi_corrected, se, ci_low, ci_high, mi_raw, var_est, m_hat."""
    joint = np.zeros((n_u, n_s), dtype=np.float64)
    for i in range(N):
        joint[events[i], contexts[i]] += 1.0
    p_joint = joint / N
    p_u = np.sum(p_joint, axis=1)
    p_s = np.sum(p_joint, axis=0)

    mi_raw = 0.0
    var_sum = 0.0
    eps = 1e-12
    m_hat = 0
    for u in range(n_u):
        if p_u[u] < eps:
            continue
        for s in range(n_s):
            p = p_joint[u, s]
            if p > eps:
                m_hat += 1
                log_ratio = np.log(p / (p_u[u] * p_s[s] + eps))
                mi_raw += p * log_ratio
                var_sum += p * (log_ratio ** 2)

    # Miller-Madow bias in nats using observed non-zero cells
    bias = (m_hat - 1.0) / (2.0 * N) if m_hat >= 1 else 0.0
    mi_corrected = mi_raw + bias

    # Variance of the uncorrected estimator (asymptotic, i.i.d.)
    var_est = (var_sum / N) - (mi_raw * mi_raw / N)
    if var_est < 0.0:
        var_est = 0.0
        se = 0.0
    else:
        se = np.sqrt(var_est)

    ci_low = mi_corrected - 1.96 * se
    if ci_low < 0.0:
        ci_low = 0.0
    ci_high = mi_corrected + 1.96 * se
    return mi_corrected, se, ci_low, ci_high, mi_raw, var_est, m_hat


# JIT warmup
_warmup_e = np.array([0, 1, 2], dtype=np.int64)
_warmup_c = np.array([0, 1, 0], dtype=np.int64)
_calculate_mi_and_stats(_warmup_e, _warmup_c, 3, 2, 3)


def _as_1d(name: str, arr) -> Union[np.ndarray, Dict[str, Any]]:
    try:
        out = np.asarray(arr)
    except (TypeError, ValueError):
        return {"status": "error", "reason": "invalid_shape"}
    if out.ndim != 1:
        return {"status": "error", "reason": "invalid_shape"}
    return out


def _moving_block_bootstrap_ci(
    me: np.ndarray,
    mc: np.ndarray,
    n_u: int,
    n_s: int,
    N: int,
    block_length: int,
    n_resamples: int,
    seed: int,
):
    """Percentile CI via moving-block bootstrap of the MI estimate."""
    rng = np.random.default_rng(seed)
    bl = max(1, min(block_length, N))
    n_blocks = int(np.ceil(N / float(bl)))
    samples = np.empty(n_resamples, dtype=np.float64)
    for b in range(n_resamples):
        starts = rng.integers(0, N - bl + 1, size=n_blocks)
        idx_list = []
        for s in starts:
            idx_list.append(np.arange(s, s + bl))
        idx = np.concatenate(idx_list)[:N]
        mi_c, _, _, _, _, _, _ = _calculate_mi_and_stats(
            me[idx], mc[idx], n_u, n_s, N
        )
        samples[b] = mi_c
    low = float(np.percentile(samples, 2.5))
    high = float(np.percentile(samples, 97.5))
    if low < 0.0:
        low = 0.0
    return low, high


def estimate_alignment(
    events,
    contexts,
    min_events: int = 30,
    max_events: Optional[int] = 500,
    min_expected_cell_count: float = 5.0,
    sample_seed: int = 0,
    method: str = "asymptotic",
    block_length: int = 20,
    n_resamples: int = 200,
):
    """Estimate predictive alignment via bias-corrected mutual information.

    Parameters
    ----------
    events, contexts:
        1-d array-likes of equal length (categorical user actions / system context).
    min_events:
        Minimum sample size after subsampling.
    max_events:
        Cap on sample size. ``None`` disables subsampling.
    min_expected_cell_count:
        Cardinality guard: require N >= min_expected_cell_count * n_u * n_s.
    sample_seed:
        Seed for random subsampling (and bootstrap when method='bootstrap').
    method:
        ``"asymptotic"`` (default) or ``"bootstrap"`` (moving-block percentile CI).
    block_length, n_resamples:
        Bootstrap controls (only used when method='bootstrap').

    Notes
    -----
    The asymptotic CI assumes i.i.d. samples; autocorrelated logs yield
    overconfident intervals.
    """
    events_arr = _as_1d("events", events)
    if isinstance(events_arr, dict):
        return events_arr
    contexts_arr = _as_1d("contexts", contexts)
    if isinstance(contexts_arr, dict):
        return contexts_arr

    if len(events_arr) != len(contexts_arr):
        return {"status": "error", "reason": "length_mismatch"}

    N = int(len(events_arr))
    if N == 0:
        return {"status": "error", "reason": "empty_input"}

    if max_events is not None and N > max_events:
        rng = np.random.default_rng(sample_seed)
        idx = np.sort(rng.choice(N, size=int(max_events), replace=False))
        events_arr = events_arr[idx]
        contexts_arr = contexts_arr[idx]
        N = int(max_events)

    if N < min_events:
        return {"status": "unreliable", "reason": "insufficient_data", "n_events": N}

    u_unique, s_unique = np.unique(events_arr), np.unique(contexts_arr)
    n_u = int(len(u_unique))
    n_s = int(len(s_unique))
    if n_u < 2 or n_s < 2:
        return {"status": "unreliable", "reason": "degenerate_distribution"}

    if N < min_expected_cell_count * n_u * n_s:
        return {
            "status": "unreliable",
            "reason": "high_cardinality",
            "n_events": N,
            "n_u": n_u,
            "n_s": n_s,
        }

    u_map = {v: i for i, v in enumerate(u_unique)}
    s_map = {v: i for i, v in enumerate(s_unique)}
    me = np.array([u_map[e] for e in events_arr], dtype=np.int64)
    mc = np.array([s_map[c] for c in contexts_arr], dtype=np.int64)

    mi, se, ci_l, ci_u, mi_raw, var_est, m_hat = _calculate_mi_and_stats(
        me, mc, n_u, n_s, N
    )

    variance_degenerate = bool(var_est <= 0.0)

    if method == "bootstrap":
        ci_l, ci_u = _moving_block_bootstrap_ci(
            me, mc, n_u, n_s, N, block_length, n_resamples, sample_seed
        )

    ci_w = float(ci_u - ci_l)
    rel_ci = ci_w / (abs(float(mi)) + 1e-8)

    reliable = bool(
        (not variance_degenerate)
        and (ci_w < 0.30)
        and (rel_ci < 0.50)
    )

    out: Dict[str, Any] = {
        "status": "success",
        "mi_estimate": float(mi),
        "ci_95": [float(ci_l), float(ci_u)],
        "ci_width": float(ci_w),
        "reliable": reliable,
        "n_events": int(N),
        "n_u": n_u,
        "n_s": n_s,
    }
    if variance_degenerate:
        out["variance_degenerate"] = True
    return out
