# PACIF v3.1

**Predictive Alignment & Causal Information Flow**

> Measures statistical coupling between user behavior and system context, and assesses the reliability of that estimate.

[![Streamlit Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pacif-demo.streamlit.app)
[![PyPI](https://img.shields.io/pypi/v/pacif-framework.svg)](https://pypi.org/project/pacif-framework/)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.19902776-blue)](https://doi.org/10.5281/zenodo.19902776)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/ppiiyo/pacif-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/ppiiyo/pacif-framework/actions/workflows/ci.yml)

---

## Why PACIF exists

Modern recommendation systems are **closed-loop controllers**: user actions train the model, and the model shapes future exposure. These feedback loops can produce behavioral lock-in, filter bubbles, and algorithmic influence that is hard to observe from the outside.

Platforms, regulators, auditors, and researchers currently lack a **transparent, statistically rigorous, and audit-ready metric** that answers a simple question:

> *How tightly is user behavior coupled to the system’s recommendations — and can we trust that measurement?*

Existing approaches suffer from finite-sample bias, provide no reliability diagnostics, and are frequently misinterpreted as causal claims. PACIF was built to close that gap.

---

## What PACIF measures

PACIF quantifies **predictive alignment** between user actions (`U`) and system context / recommendations (`S`), with optional control for observed confounders (`C`).

It is deliberately **not** a measure of causality, user wellbeing, or “manipulation”. It is a production-ready diagnostic layer that tells you:

| Signal | What it tells you |
|--------|-------------------|
| **Signal Strength (MI)** | Intensity of statistical coupling (nats) |
| **Reliability** | Whether the estimate is statistically stable |
| **Drift** | Whether the relationship has shifted over time |
| **Audit Report** | Machine-readable YAML with anti-gaming flags |

### Core capabilities

- **Bias-corrected Mutual Information** — Miller–Madow correction removes first-order finite-sample bias (nats; observed joint cells).
- **Cardinality guard** — high unique-label / small-N regimes return `unreliable` instead of overconfident MI.
- **Strict reliability diagnostics** — CI width thresholds; zero/degenerate variance forces `reliable=False`.
- **Drift detection** — CUSUM and Page–Hinkley with pre-drift baseline and rebaselining window.
- **Regulator-ready audit reports** — YAML schema 1.2 with parameters block, exclusion-rate, category-inflation, skew, and drift flags.
- **Causal integration pattern** — synthetic PACIF-like features in an illustrative DR simulation; see `causal_integration.py` (not evidence on real data).

**Performance (reference):** >1,900 sessions/sec, p95 latency <1 ms (`examples/benchmark_throughput.py`).

---

## Explicit boundaries (important)

PACIF measures **statistical predictability**, not causality and not wellbeing.

- High mutual information indicates strong *association / coupling*, not that the algorithm *caused* the behavior.
- Normative or causal claims require intervention data, experimental design, or stronger identification assumptions.
- The framework is designed to be honest about uncertainty: unreliable estimates are explicitly marked.

Full practitioner guide: **[docs/INTERPRETATION.md](docs/INTERPRETATION.md)**  
Outreach one-pager: **[docs/POSITIONING.md](docs/POSITIONING.md)**  
Release process: **[docs/RELEASING.md](docs/RELEASING.md)**

---

## Quick start

### Live demo (no install)

👉 **[Launch PACIF Demo](https://pacif-demo.streamlit.app)**

### Install

```bash
pip install pacif-framework
```

From source (development):

```bash
git clone https://github.com/ppiiyo/pacif-framework.git
cd pacif-framework
pip install -e ".[demo,dev]"
pytest tests/ -v
mypy pacif_core
```

### Minimal usage

```python
from pacif_core import estimate_alignment, DriftDetector, PageHinkleyDetector, AuditReporter
import numpy as np

events   = np.array([0, 1, 0, 2, 1, 0, 2, 1] * 20)
contexts = np.array([0, 1, 0, 1, 1, 0, 2, 1] * 20)

result = estimate_alignment(events, contexts, max_events=None)

if result["status"] == "success":
    print(f"MI: {result['mi_estimate']:.3f} nats")
    print(f"95% CI: {result['ci_95']}")
    print(f"Reliable: {result['reliable']}")
```

See `examples/basic_usage.py` for multi-session + drift + audit.

---

## Interpreting results

| Metric | Interpretation | Suggested action |
|--------|----------------|------------------|
| **Signal Strength (MI)** | Intensity of coupling | > 0.8 nats → investigate lock-in risk |
| **Reliability Ratio** | % of sessions with statistically valid estimates | < 70% → increase sample size or window |
| **Drift Status** | Significant change in the relationship over time | Drift detected → consider model recalibration |

Deep dive: [docs/INTERPRETATION.md](docs/INTERPRETATION.md)

---

## Who this is for

- **Responsible AI / Trust & Safety teams** — internal monitoring of recommendation influence and feedback loops.
- **Platforms** (social, e-commerce, content, news) — diagnostics for personalization strength and stability.
- **Regulators & compliance** — audit-ready, machine-readable reports with explicit reliability and anti-gaming signals.
- **Researchers** in algorithmic accountability, fairness, and causal inference — reproducible metric + integration path with DR estimators.
- **Auditors & third-party assessors** — independent quantification of human–algorithm coupling.

---

## Project structure

```
pacif-framework/
├── pacif_core/
│   ├── _version.py       # single version source (3.1.x)
│   ├── estimator.py      # Bias-corrected MI + reliability
│   ├── drift.py          # CUSUM + Page-Hinkley detectors
│   └── audit.py          # YAML audit reporter (schema 1.2)
├── tests/
├── docs/
│   ├── INTERPRETATION.md
│   ├── POSITIONING.md
│   └── RELEASING.md
├── examples/
├── app.py
├── causal_integration.py
└── .github/workflows/
    ├── ci.yml            # ruff + mypy + pytest-cov (3.9–3.12)
    └── publish.yml       # tag v* → GitHub Release + PyPI
```

---

## Releasing

Version lives in `pacif_core/_version.py`. Tag must match:

```bash
git tag -a v3.1.0 -m "PACIF v3.1.0"
git push origin v3.1.0
```

Details: [docs/RELEASING.md](docs/RELEASING.md).

**Note:** Numeric MI outputs differ from 3.0.x (Miller–Madow units, cardinality guard, sampling). Re-baseline thresholds calibrated on 3.0.x.

---

## Enterprise & audit integration

For production deployments, multi-tenant audit pipelines, custom connectors, or compliance reporting support, contact:

**for.smirnov.maks@gmail.com**

---

## Contributing

We welcome contributions. Algorithmic transparency should be a public good.

- 🐛 [Open an issue](https://github.com/ppiiyo/pacif-framework/issues)
- 💡 Pull requests are welcome (see [CONTRIBUTING.md](CONTRIBUTING.md))
- 📜 Please follow the [Code of Conduct](CODE_OF_CONDUCT.md)
- 🔒 [Security policy](SECURITY.md)

---

## Citation

If you use PACIF in research, audits, or product workflows, please cite:

```bibtex
@software{pacif_v3_2026,
  author       = {ppiiyo},
  title        = {PACIF v3.1: Predictive Alignment \& Causal Information Flow},
  year         = {2026},
  url          = {https://github.com/ppiiyo/pacif-framework},
  doi          = {10.5281/zenodo.19902776},
  license      = {Apache-2.0}
}
```

Also available as [`CITATION.cff`](CITATION.cff).

---

*Built for transparency, reproducibility, and algorithmic accountability.*  
© 2026 PACIF Framework Contributors
