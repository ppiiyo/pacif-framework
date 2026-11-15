"""Unit tests for pacif_core.estimator."""
from __future__ import annotations

import numpy as np
import pytest

from pacif_core.estimator import estimate_alignment


def _coupled_session(n: int = 100, coupling: float = 0.9, n_cat: int = 4, seed: int = 0):
    rng = np.random.default_rng(seed)
    events = rng.integers(0, n_cat, size=n)
    contexts = events.copy()
    noise = rng.random(n) > coupling
    contexts[noise] = rng.integers(0, n_cat, size=int(noise.sum()))
    return events, contexts


def test_empty_input():
    result = estimate_alignment(np.array([]), np.array([]))
    assert result["status"] == "error"
    assert result["reason"] == "empty_input"


def test_insufficient_data():
    events = np.array([0, 1, 0, 1, 0])
    contexts = np.array([0, 1, 0, 1, 0])
    result = estimate_alignment(events, contexts, min_events=30)
    assert result["status"] == "unreliable"
    assert result["reason"] == "insufficient_data"
    assert result["n_events"] == 5


def test_degenerate_single_category():
    events = np.zeros(50, dtype=int)
    contexts = np.zeros(50, dtype=int)
    result = estimate_alignment(events, contexts, min_events=30)
    assert result["status"] == "unreliable"
    assert result["reason"] == "degenerate_distribution"


def test_success_on_coupled_data():
    events, contexts = _coupled_session(n=120, coupling=0.95, seed=42)
    result = estimate_alignment(events, contexts)
    assert result["status"] == "success"
    assert result["mi_estimate"] > 0.3
    assert "ci_95" in result
    assert len(result["ci_95"]) == 2
    assert result["ci_95"][0] <= result["mi_estimate"] <= result["ci_95"][1]
    assert result["n_events"] == 120
    assert result["n_u"] >= 2
    assert result["n_s"] >= 2
    assert isinstance(result["reliable"], bool)


def test_weak_coupling_lower_mi():
    strong_ev, strong_ctx = _coupled_session(n=150, coupling=0.95, seed=1)
    weak_ev, weak_ctx = _coupled_session(n=150, coupling=0.2, seed=1)
    strong = estimate_alignment(strong_ev, strong_ctx)
    weak = estimate_alignment(weak_ev, weak_ctx)
    assert strong["status"] == "success" and weak["status"] == "success"
    assert strong["mi_estimate"] > weak["mi_estimate"]


def test_max_events_subsampling():
    events, contexts = _coupled_session(n=800, coupling=0.8, seed=7)
    result = estimate_alignment(events, contexts, max_events=100)
    assert result["status"] == "success"
    assert result["n_events"] == 100


def test_ci_width_and_reliability_fields():
    events, contexts = _coupled_session(n=200, coupling=0.85, seed=99)
    result = estimate_alignment(events, contexts)
    assert result["status"] == "success"
    assert result["ci_width"] >= 0
    assert result["ci_width"] == pytest.approx(
        result["ci_95"][1] - result["ci_95"][0], rel=1e-6
    )


def test_identical_perfect_coupling():
    # Enough mass per cell so cardinality guard passes (5 cats * 5 * 5 = 125).
    events = np.tile(np.arange(5), 40)  # N=200
    contexts = events.copy()
    result = estimate_alignment(events, contexts, min_expected_cell_count=5.0)
    assert result["status"] == "success"
    assert result["mi_estimate"] > 1.0
    # Deterministic U==S yields zero plug-in variance -> variance_degenerate
    assert result.get("variance_degenerate") is True
    assert result["reliable"] is False


def test_independence_large_n_near_zero():
    rng = np.random.default_rng(0)
    events = rng.integers(0, 2, size=2000)
    contexts = rng.integers(0, 3, size=2000)
    result = estimate_alignment(events, contexts, max_events=None)
    assert result["status"] == "success"
    assert abs(result["mi_estimate"]) < 0.05


def test_bsc_ground_truth():
    """Binary symmetric channel p=0.1: MI = ln2 - H_b(0.1) ≈ 0.3681 nats."""
    p = 0.1
    h = -p * np.log(p) - (1 - p) * np.log(1 - p)
    mi_true = np.log(2) - h
    assert mi_true == pytest.approx(0.3681, abs=1e-3)

    rng = np.random.default_rng(42)
    n = 5000
    x = rng.integers(0, 2, size=n)
    flips = rng.random(n) < p
    y = np.where(flips, 1 - x, x)
    result = estimate_alignment(x, y, max_events=None)
    assert result["status"] == "success"
    assert abs(result["mi_estimate"] - mi_true) < 0.05


def test_bsc_ci_coverage():
    p = 0.1
    h = -p * np.log(p) - (1 - p) * np.log(1 - p)
    mi_true = np.log(2) - h
    covered = 0
    n_seeds = 50
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        n = 5000
        x = rng.integers(0, 2, size=n)
        flips = rng.random(n) < p
        y = np.where(flips, 1 - x, x)
        result = estimate_alignment(x, y, max_events=None)
        assert result["status"] == "success"
        lo, hi = result["ci_95"]
        if lo <= mi_true <= hi:
            covered += 1
    assert covered / n_seeds >= 0.90


def test_high_cardinality_6x6_n30():
    rng = np.random.default_rng(0)
    events = rng.integers(0, 6, size=30)
    contexts = rng.integers(0, 6, size=30)
    result = estimate_alignment(events, contexts, min_events=30)
    assert result["status"] == "unreliable"
    assert result["reason"] == "high_cardinality"
    assert result["n_u"] == 6
    assert result["n_s"] == 6


def test_high_cardinality_many_unique():
    events = np.arange(500)
    contexts = np.arange(500)
    result = estimate_alignment(events, contexts, min_events=30, max_events=500)
    assert result["status"] == "unreliable"
    assert result["reason"] == "high_cardinality"


def test_length_mismatch():
    events = np.array([0, 1, 0, 1, 0, 1] * 10)
    contexts = np.array([0, 1, 0])
    result = estimate_alignment(events, contexts)
    assert result["status"] == "error"
    assert result["reason"] == "length_mismatch"


def test_invalid_shape():
    result = estimate_alignment(np.zeros((3, 3)), np.zeros((3, 3)))
    assert result["status"] == "error"
    assert result["reason"] == "invalid_shape"


def test_period8_subsampling_preserves_categories():
    n = 3993
    events = np.arange(n) % 8
    contexts = events.copy()
    full = estimate_alignment(events, contexts, max_events=None)
    sub = estimate_alignment(events, contexts, max_events=500, sample_seed=0)
    assert sub["status"] == "success"
    assert sub["n_u"] == 8
    assert sub["n_s"] == 8
    assert full["status"] == "success"
    assert abs(sub["mi_estimate"] - full["mi_estimate"]) < 0.1


def test_ci_lower_nonnegative():
    rng = np.random.default_rng(1)
    events = rng.integers(0, 2, size=200)
    contexts = rng.integers(0, 2, size=200)
    result = estimate_alignment(events, contexts, max_events=None)
    if result["status"] == "success":
        assert result["ci_95"][0] >= 0.0


def test_bootstrap_method_runs():
    events, contexts = _coupled_session(n=200, coupling=0.8, seed=3)
    result = estimate_alignment(
        events, contexts, max_events=None, method="bootstrap", n_resamples=50
    )
    assert result["status"] == "success"
    assert len(result["ci_95"]) == 2
    assert result["ci_95"][0] <= result["ci_95"][1]
