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
    events = np.tile(np.arange(5), 40)
    contexts = events.copy()
    result = estimate_alignment(events, contexts)
    assert result["status"] == "success"
    # Near-perfect dependence should yield relatively high MI
    assert result["mi_estimate"] > 1.0
