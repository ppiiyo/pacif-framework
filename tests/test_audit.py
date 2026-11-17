"""Unit tests for pacif_core.audit.AuditReporter."""
from __future__ import annotations

import re

import yaml

from pacif_core import __version__
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
    data = yaml.safe_load(report)
    assert data["status"] == "error"
    assert data["reason"] == "no_data"


def test_no_reliable_data():
    results = [
        {"status": "unreliable", "reason": "insufficient_data"},
        {
            "status": "success",
            "mi_estimate": 0.5,
            "reliable": False,
            "n_u": 3,
            "n_s": 3,
            "n_events": 40,
        },
    ]
    report = AuditReporter.generate_report(results)
    data = yaml.safe_load(report)
    assert data["status"] == "no_reliable_data"
    assert data["flags"] == ["NO_RELIABLE_ESTIMATES"]
    assert data["summary"]["reliable"] == 0
    assert "parameters" in data


def test_valid_yaml_structure():
    results = [_success(0.4 + i * 0.01, reliable=True) for i in range(20)]
    report = AuditReporter.generate_report(results)
    data = yaml.safe_load(report)
    assert "metadata" in data
    assert data["metadata"]["framework"] == f"PACIF v{__version__}"
    assert data["metadata"]["schema"] == "1.2"
    assert "summary" in data
    assert data["summary"]["total"] == 20
    assert data["summary"]["reliable"] == 20
    assert "median_mi" in data["summary"]
    assert "mean_mi" in data["summary"]
    assert "flags" in data
    assert "parameters" in data
    assert data["parameters"]["mi_high"] == 0.8
    assert data["parameters"]["mi_moderate"] == 0.3
    assert data["parameters"]["skew_factor"] == 0.25


def test_median_even_length():
    results = [
        _success(0.1),
        _success(0.2),
        _success(0.3),
        _success(0.4),
    ]
    report = AuditReporter.generate_report(results)
    data = yaml.safe_load(report)
    assert data["summary"]["median_mi"] == 0.25


def test_high_exclusion_rate_flag():
    results = [_success(0.3, reliable=True) for _ in range(3)]
    results += [{"status": "unreliable", "reason": "insufficient_data"} for _ in range(10)]
    report = AuditReporter.generate_report(results)
    data = yaml.safe_load(report)
    assert "HIGH_EXCLUSION_RATE" in data["flags"]


def test_category_inflation_flag():
    results = [_success(0.35, reliable=True, n_u=3, n_s=3, n_events=80) for _ in range(10)]
    results += [
        _success(0.4, reliable=True, n_u=25, n_s=25, n_events=40) for _ in range(5)
    ]
    report = AuditReporter.generate_report(results)
    data = yaml.safe_load(report)
    assert "CATEGORY_INFLATION_RISK" in data["flags"]


def test_schema_version_override():
    results = [_success(0.5) for _ in range(5)]
    report = AuditReporter.generate_report(results, schema_version="1.1")
    data = yaml.safe_load(report)
    assert data["metadata"]["schema"] == "1.1"


def test_context_merged_into_metadata():
    results = [_success(0.5) for _ in range(5)]
    report = AuditReporter.generate_report(
        results, context={"window": "2026-Q3", "fingerprint": "abc123"}
    )
    data = yaml.safe_load(report)
    assert data["metadata"]["window"] == "2026-Q3"
    assert data["metadata"]["fingerprint"] == "abc123"


def test_version_module():
    assert isinstance(__version__, str)
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__), __version__
