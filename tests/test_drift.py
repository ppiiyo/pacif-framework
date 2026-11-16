"""Unit tests for pacif_core.drift detectors."""
from __future__ import annotations

import numpy as np
import pytest

from pacif_core.drift import DriftDetector, PageHinkleyDetector


def test_warmup_period():
    det = DriftDetector(threshold=0.15)
    for _ in range(49):
        out = det.update(0.3)
        assert out["drift"] is False
        assert out.get("reason") == "warming_up"


def test_no_false_positive_on_stationary():
    det = DriftDetector(threshold=0.2, slack=0.01)
    rng = np.random.default_rng(0)
    drift_count = 0
    for _ in range(500):
        val = 0.4 + rng.normal(0, 0.02)
        out = det.update(float(val))
        if out.get("drift"):
            drift_count += 1
    assert drift_count <= 3


def test_detects_step_change_within_30():
    det = DriftDetector(threshold=0.12, slack=0.005)
    for _ in range(60):
        det.update(0.25)
    detected_at = None
    for i in range(80):
        out = det.update(0.55)
        if out.get("drift"):
            detected_at = i
            break
    assert detected_at is not None
    assert detected_at < 30


def test_detects_downward_shift_within_30():
    det = DriftDetector(threshold=0.12, slack=0.005)
    for _ in range(60):
        det.update(0.6)
    detected_at = None
    for i in range(80):
        out = det.update(0.25)
        if out.get("drift"):
            detected_at = i
            break
    assert detected_at is not None
    assert detected_at < 30


def test_alarm_returns_pre_drift_baseline():
    det = DriftDetector(threshold=0.1, slack=0.002)
    for _ in range(50):
        det.update(0.2)
    alarm = None
    for _ in range(100):
        out = det.update(0.6)
        if out.get("drift"):
            alarm = out
            break
    assert alarm is not None
    assert alarm["baseline"] == pytest.approx(0.2, abs=0.02)
    assert alarm["baseline"] != pytest.approx(alarm["value"], abs=0.05)


def test_rebaselining_phase_after_alarm():
    det = DriftDetector(threshold=0.1, slack=0.002, rebaseline_window=50)
    for _ in range(50):
        det.update(0.2)
    for _ in range(100):
        out = det.update(0.7)
        if out.get("drift"):
            break
    else:
        pytest.fail("expected drift alarm")
    rebaseline_count = 0
    for _ in range(50):
        out = det.update(0.7)
        assert out["drift"] is False
        assert out.get("reason") == "rebaselining"
        rebaseline_count += 1
    assert rebaseline_count == 50


def test_history_bounded_after_10000_updates():
    det = DriftDetector(threshold=1.0, slack=0.01)
    for i in range(10000):
        det.update(0.3 + (0.001 if i % 100 == 0 else 0.0))
    assert len(det.history) <= 50


def test_ph_stationary_sigma_005_zero_alarms():
    """Defaults: sigma=0.005 → no alarms on 10 seeds × 500 steps."""
    for seed in range(10):
        det = PageHinkleyDetector(delta=0.005, lambda_=0.15)
        rng = np.random.default_rng(seed)
        for _ in range(500):
            out = det.update(float(0.4 + rng.normal(0, 0.005)))
            assert out.get("drift") is False, f"false alarm seed={seed}"


def test_ph_stationary_sigma_02_arl_lambda():
    """sigma=0.02, lambda_=0.8 (ARL≈200): at most 3 alarms in 500 steps."""
    det = PageHinkleyDetector(delta=0.005, lambda_=0.8)
    rng = np.random.default_rng(1)
    drift_count = 0
    for _ in range(500):
        if det.update(float(0.4 + rng.normal(0, 0.02))).get("drift"):
            drift_count += 1
    assert drift_count <= 3


def test_ph_detects_step_up_and_rebaselines():
    det = PageHinkleyDetector(delta=0.005, lambda_=0.15)
    for _ in range(60):
        det.update(0.2)
    detected_at = None
    alarm = None
    for i in range(80):
        out = det.update(0.6)
        if out.get("drift"):
            detected_at = i
            alarm = out
            break
    assert detected_at is not None and detected_at < 30
    assert alarm["baseline"] == pytest.approx(0.2, abs=0.02)
    for _ in range(50):
        out = det.update(0.6)
        assert out.get("reason") == "rebaselining"


def test_ph_detects_step_down():
    det = PageHinkleyDetector(delta=0.005, lambda_=0.15)
    for _ in range(60):
        det.update(0.6)
    detected_at = None
    alarm = None
    for i in range(80):
        out = det.update(0.2)
        if out.get("drift"):
            detected_at = i
            alarm = out
            break
    assert detected_at is not None and detected_at < 30
    assert alarm["baseline"] == pytest.approx(0.6, abs=0.02)


def test_ph_history_bounded():
    det = PageHinkleyDetector()
    for _ in range(10000):
        det.update(0.4)
    assert len(det.history) <= 50


def test_ph_and_cusum_differ_on_ramp():
    """Slow ramp: classic PH (running mean) vs CUSUM (fixed baseline) diverge."""
    cusum = DriftDetector(threshold=0.12, slack=0.005)
    ph = PageHinkleyDetector(delta=0.005, lambda_=0.15)
    cusum_alarms = []
    ph_alarms = []
    # warmup flat
    for _ in range(60):
        cusum.update(0.3)
        ph.update(0.3)
    # linear ramp
    for i in range(120):
        x = 0.3 + 0.004 * i
        if cusum.update(x).get("drift"):
            cusum_alarms.append(i)
        if ph.update(x).get("drift"):
            ph_alarms.append(i)
    assert cusum_alarms != ph_alarms, (
        f"expected different alarm sequences; both={cusum_alarms}"
    )
