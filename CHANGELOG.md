# Changelog

All notable changes to PACIF are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.1] - 2026-11-09

### Added
- Full unit test suite (`tests/`) for estimator, drift detector, and audit reporter
- GitHub Actions CI (pytest + ruff on Python 3.9–3.12, package build check)
- `docs/INTERPRETATION.md` — practitioner decision framework and communication guide
- Enhanced `AuditReporter` (schema 1.1): category inflation, distribution skew, high-coupling cluster, drift flags, interpretation block
- `CHANGELOG.md`, `SECURITY.md`, `CITATION.cff`
- `examples/benchmark_throughput.py`
- `docs/POSITIONING.md` one-pager for outreach

### Changed
- Professional README positioning (predictive alignment, explicit boundaries, audiences)
- Packaging via `pyproject.toml` with optional extras: `demo`, `causal`, `dev`

## [3.0.0] - 2026-11

### Added
- Bias-corrected mutual information estimator (Miller-Madow)
- Reliability diagnostics via CI width thresholds
- CUSUM-style drift detector
- YAML audit reporter
- Streamlit demo (`app.py`)
- Causal integration illustration with Doubly Robust estimator
