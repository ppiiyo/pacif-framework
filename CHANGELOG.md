# Changelog

All notable changes to PACIF are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - Unreleased

### Fixed
- Miller–Madow bias now in **nats** using observed non-zero joint cells `(m_hat - 1) / (2N)` (was bits-scale full grid `(Ku-1)(Ks-1)/(2N ln 2)`, overstating bias by ~1.44× and on sparse tables).
- Cardinality guard: `N < min_expected_cell_count * n_u * n_s` → `unreliable` / `high_cardinality` (default cell count 5).
- Asymptotic variance uses `mi_raw`; zero/negative variance sets `variance_degenerate=True` and forces `reliable=False`.
- CI lower bound clipped at 0; docstring notes i.i.d. assumption for asymptotic intervals.
- Input validation: 1-d equal-length arrays (`length_mismatch` / `invalid_shape`).
- Subsampling via seeded `rng.choice` (was deterministic `linspace`, aliasing period-8 patterns); `max_events=None` disables the cap.
- Drift alarm now returns the **pre-drift** baseline (was overwritten with the triggering value).
- Drift history bounded with `deque(maxlen=50)` (was unbounded list).
- Audit median uses `statistics.median` (even-length half-sum; was lower middle index only).

### Added
- Optional `method="bootstrap"` (moving-block bootstrap CI, seeded).
- Parameters: `min_expected_cell_count`, `sample_seed`, `method`, `block_length`, `n_resamples`.
- `PageHinkleyDetector` (two-sided Page–Hinkley) with the same warmup/rebaseline protocol as CUSUM.
- Post-alarm rebaselining window (50 observations) before baseline is reset to the new regime mean.
- Audit schema **1.2**: `parameters` block (all thresholds), optional `context` merged into `metadata`.
- Single version source: `pacif_core/_version.py` (`3.1.0`); dynamic version in `pyproject.toml`.

### Changed
- **Numeric estimates differ from 3.0.x** due to MM unit fix, cardinality guard, and sampling change. Re-baseline any thresholds calibrated on 3.0.x outputs.
- Audit report `framework` string follows package version (`PACIF v3.1.0`); default schema `1.1` → `1.2`.

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
