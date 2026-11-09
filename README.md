# PACIF v3.0

**Predictive Alignment & Causal Information Flow**

> Measures how strongly algorithms shape user behavior — and whether that signal is reliable.

[![Streamlit Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pacif-demo.streamlit.app)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.19902776-blue)](https://doi.org/10.5281/zenodo.19902776)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/ppiiyo/pacif-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/ppiiyo/pacif-framework/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/badge/PyPI-coming%20soon-lightgrey.svg)](https://pypi.org/)

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

- **Bias-corrected Mutual Information** — Miller-Madow correction reduces finite-sample bias by 40–65%.
- **Strict reliability diagnostics** — automatically flags unstable estimates via confidence-interval width thresholds.
- **Cumulative drift detection** — CUSUM + Page-Hinkley for non-stationary behavioral shifts.
- **Regulator-ready audit reports** — YAML output with exclusion-rate, category-inflation, skew, and drift flags.
- **Causal integration pattern** — PACIF features reduce Doubly Robust (DR) estimator bias by ~89% in controlled simulations.

**Performance (reference):** >1,900 sessions/sec, p95 latency <1 ms (`examples/benchmark_throughput.py`).

---

## Explicit boundaries (important)

PACIF measures **statistical predictability**, not causality and not wellbeing.

- High mutual information indicates strong *association / coupling*, not that the algorithm *caused* the behavior.
- Normative or causal claims require intervention data, experimental design, or stronger identification assumptions.
- The framework is designed to be honest about uncertainty: unreliable estimates are explicitly marked.

Full practitioner guide: **[docs/INTERPRETATION.md](docs/INTERPRETATION.md)**  
Outreach one-pager: **[docs/POSITIONING.md](docs/POSITIONING.md)**

---

## Quick start

### Live demo (no install)

👉 **[Launch PACIF Demo](https://pacif-demo.streamlit.app)**

### Install

```bash
pip install -e .                       # core
pip install -e ".[demo,causal,dev]"    # demo + causal example + tests
```

Or from the repository:

```bash
git clone https://github.com/ppiiyo/pacif-framework.git
cd pacif-framework
pip install -e ".[demo,dev]"
pytest tests/ -v
```

### Minimal usage

```python
from pacif_core import estimate_alignment, DriftDetector, AuditReporter
import numpy as np

events   = np.array([0, 1, 0, 2, 1, 0, 2, 1] * 20)
contexts = np.array([0, 1, 0, 1, 1, 0, 2, 1] * 20)

result = estimate_alignment(events, contexts)

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
│   ├── estimator.py      # Bias-corrected MI + reliability
│   ├── drift.py          # CUSUM-style drift detector
│   └── audit.py          # YAML audit reporter (schema 1.1)
├── tests/                # pytest suite
├── docs/
│   ├── INTERPRETATION.md
│   └── POSITIONING.md
├── examples/
│   ├── basic_usage.py
│   └── benchmark_throughput.py
├── app.py                # Streamlit demo
├── causal_integration.py # DR estimator illustration
└── .github/workflows/ci.yml
```

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
  title        = {PACIF v3.0: Predictive Alignment \& Causal Information Flow},
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
