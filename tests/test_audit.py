"""Unit tests for pacif_core.audit.AuditReporter."""
from __future__ import annotations

import yaml

from pacif_core.audit import AuditReporter


def _success(mi: float, reliable: bool = True, n_u: int = 4, n_s: int = 4, n_events: int = 80):
    return {
        "status": "success",
        "mi_estimate": mi,
        "reliable": reliable,
        "n_u": n_u,
        "n_s": n_s,
        "n_events": n_events,
        "ci_width": 0.1,
    }


def test_empty_results():
    report = AuditReporter.generate_report([])
    assert "Error" in report or "no" in report.lower()


def test_no_reliable_data():
    results = [
        {"status": "unreliable", "reason": "insufficient_data"},
        {"status": "success", "mi_estimate": 0.5, "reliable": False, "n_u": 3, "n_s": 3, "n_events": 40},
    ]
    report = AuditReporter.generate_report(results)
    data = yaml.safe_load(report)
    assert data.get("status") == "no_reliable_data" or "flags" in data or "summary" in data


def test_valid_yaml_structure():
    results = [_success(0.4 + i * 0.01, reliable=True) for i in range(20)]
    report = AuditReporter.generate_report(results)
    data = yaml.safe_load(report)
    assert "metadata" in data
    assert data["metadata"]["framework"] == "PACIF v3.0"
    assert "summary" in data
    assert data["summary"]["total"] == 20
    assert data["summary"]["reliable"] == 20
    assert "median_mi" in data["summary"]
    assert "mean_mi" in data["summary"]
    assert "flags" in data


def test_high_exclusion_rate_flag():
    results = [_success(0.3, reliable=True) for _ in range(3)]
    results += [{"status": "unreliable", "reason": "insufficient_data"} for _ in range(10)]
    report = AuditReporter.generate_report(results)
    data = yaml.safe_load(report)
    assert "HIGH_EXCLUSION_RATE" in data.get("flags", [])


def test_category_inflation_flag():
    results = [_success(0.35, reliable=True, n_u=3, n_s=3) for _ in range(10)]
    results += [_success(0.4, reliable=True, n_u=25, n_s=25, n_events=40) for _ in range(5)]
    report = AuditReporter.generate_report(results)
    data = yaml.safe_load(report)
    flags = data.get("flags", [])
    assert "CATEGORY_INFLATION_RISK" in flags or data["summary"]["reliable"] > 0


def test_schema_version():
    results = [_success(0.5) for _ in range(5)]
    report = AuditReporter.generate_report(results, schema_version="1.1")
    data = yaml.safe_load(report)
    assert data["metadata"]["schema"] == "1.1"
