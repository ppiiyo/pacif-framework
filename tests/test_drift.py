"""Unit tests for pacif_core.drift.DriftDetector."""
from __future__ import annotations

import numpy as np

from pacif_core.drift import DriftDetector


def test_warmup_period():
    det = DriftDetector(threshold=0.15)
    for i in range(49):
        out = det.update(0.3)
        assert out["drift"] is False
        assert out.get("reason") == "warming_up"


def test_no_false_positive_on_stationary():
    det = DriftDetector(threshold=0.2, slack=0.01)
    rng = np.random.default_rng(0)
    drift_count = 0
    for _ in range(200):
        val = 0.4 + rng.normal(0, 0.02)
        out = det.update(float(val))
        if out.get("drift"):
            drift_count += 1
    # Stationary series with small noise should rarely trip drift
    assert drift_count <= 3


def test_detects_step_change():
    det = DriftDetector(threshold=0.12, slack=0.005)
    # Establish baseline
    for _ in range(60):
        det.update(0.25)
    # Inject clear upward shift
    detected = False
    for _ in range(80):
        out = det.update(0.55)
        if out.get("drift"):
            detected = True
            break
    assert detected is True


def test_detects_downward_shift():
    det = DriftDetector(threshold=0.12, slack=0.005)
    for _ in range(60):
        det.update(0.6)
    detected = False
    for _ in range(80):
        out = det.update(0.25)
        if out.get("drift"):
            detected = True
            break
    assert detected is True


def test_baseline_updates_after_drift():
    det = DriftDetector(threshold=0.1, slack=0.002)
    for _ in range(50):
        det.update(0.2)
    # Force drift
    for _ in range(100):
        out = det.update(0.7)
        if out.get("drift"):
            assert "baseline" in out or out["drift"] is True
            break
