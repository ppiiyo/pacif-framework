# PACIF v3.1

**Predictive Alignment & Causal Information Flow**

> Measures statistical coupling between user behavior and system context, and assesses the reliability of that estimate.

[![Streamlit Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pacif-demo.streamlit.app)
[![PyPI](https://img.shields.io/pypi/v/pacif-framework.svg)](https://pypi.org/project/pacif-framework/)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.19902776-blue)](https://doi.org/10.5281/zenodo.19902776)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/ppiiyo/pacif-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/ppiiyo/pacif-framework/actions/workflows/ci.yml)

**60-second path:** [Demo](https://pacif-demo.streamlit.app) → `pip install pacif-framework` → run the [ranking-release case study](#case-study-ranking-release).

---

## Why PACIF exists

Recommendation systems form **feedback loops**: behavior updates the model, the model changes future exposure. Platforms lack a small, honest metric for *how tightly* actions and context are coupled — with explicit reliability and an audit trail.

> *How tightly is user behavior coupled to what the system shows — and can we trust that number?*

PACIF answers that with bias-corrected mutual information, reliability gates, drift detectors, and machine-readable audits. It does **not** claim causality or wellbeing.

---

## Case study: ranking release

Typical Trust & Safety / ranking workflow after a personalization ship:

```bash
pip install pacif-framework
# from a clone:
python examples/ranking_release_monitor.py
```

Compares synthetic **pre** vs **post** phases: median MI, reliability ratio, CUSUM drift, audit YAML head. Write-up: **[docs/CASE_STUDY_RANKING.md](docs/CASE_STUDY_RANKING.md)**.

```python
from pacif_core import estimate_alignment, DriftDetector, AuditReporter
import numpy as np

# U = user actions, S = system context (integer categories)
rng = np.random.default_rng(0)
U = rng.integers(0, 4, size=200)
S = U.copy()
S[rng.random(200) > 0.7] = rng.integers(0, 4, size=int((rng.random(200) > 0.7).sum()))

out = estimate_alignment(U, S, max_events=None)
print(out["status"], out.get("mi_estimate"), out.get("reliable"))
```

---

## What PACIF measures

| Signal | What it tells you |
|--------|-------------------|
| **Signal Strength (MI)** | Intensity of statistical coupling (nats) |
| **Reliability** | Whether the estimate is statistically stable |
| **Drift** | Whether the relationship has shifted over time |
| **Audit Report** | YAML schema 1.2 with anti-gaming flags |

### Core capabilities

- **Bias-corrected MI** — Miller–Madow in nats (observed joint cells).
- **Cardinality guard** — high unique-label / small-N → `unreliable`, not overconfident MI.
- **Reliability diagnostics** — CI width; degenerate variance → `reliable=False`.
- **Drift** — CUSUM + classic Page–Hinkley (pre-drift baseline, rebaseline window).
- **Audit reports** — schema 1.2 `parameters` + context metadata.
- **Causal pattern only** — synthetic DR illustration in `causal_integration.py` (not real-data evidence).

**Reference throughput:** >1,900 sessions/sec (`examples/benchmark_throughput.py`).

---

## Explicit boundaries

- High MI ⇒ strong *association*, not *cause*.
- Unreliable estimates are marked; do not promote them as evidence.
- Normative claims need experiments or stronger identification.

**[docs/INTERPRETATION.md](docs/INTERPRETATION.md)** · **[docs/POSITIONING.md](docs/POSITIONING.md)** · **[docs/RELEASING.md](docs/RELEASING.md)**

---

## Install

```bash
pip install pacif-framework
```

Dev:

```bash
git clone https://github.com/ppiiyo/pacif-framework.git
cd pacif-framework
pip install -e ".[demo,dev]"
pytest tests/ -q
```

Live demo (no install): **[pacif-demo.streamlit.app](https://pacif-demo.streamlit.app)**

---

## Interpreting results

| Metric | Reading | Suggested action |
|--------|---------|------------------|
| **MI (nats)** | Coupling intensity | Domain-calibrate; very high → investigate lock-in *risk* |
| **Reliability ratio** | Share of trustworthy windows | Low → more data / fewer categories |
| **Drift** | Non-stationarity in the relationship | Correlate with ranking/UI releases |

---

## Who this is for

- **Trust & Safety / Responsible AI** — monitor personalization strength after ships
- **Ranking / product** — continuous coupling diagnostic next to engagement KPIs
- **Auditors & compliance** — reproducible YAML with reliability and flags
- **Researchers** — open metric + explicit non-causal boundaries (DOI on Zenodo)

---

## Project structure

```
pacif_core/     estimator, drift (CUSUM + Page–Hinkley), audit (schema 1.2)
examples/       ranking_release_monitor.py · basic_usage.py · benchmark_throughput.py
docs/           INTERPRETATION · CASE_STUDY_RANKING · POSITIONING · RELEASING
app.py          Streamlit demo
```

---

## Citation

```bibtex
@software{pacif_v3_2026,
  author  = {ppiiyo},
  title   = {PACIF v3.1: Predictive Alignment \& Causal Information Flow},
  year    = {2026},
  url     = {https://github.com/ppiiyo/pacif-framework},
  doi     = {10.5281/zenodo.19902776},
  license = {Apache-2.0}
}
```

[`CITATION.cff`](CITATION.cff) · Contact for pilots: **for.smirnov.maks@gmail.com**

---

*Built for transparency, reproducibility, and algorithmic accountability.*  
© 2026 PACIF Framework Contributors
