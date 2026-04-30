```markdown
# PACIF v3.0: Predictive Alignment & Causal Information Flow

> **Measures how strongly algorithms shape user behavior — and whether that signal is reliable.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19902776.svg)](https://doi.org/10.5281/zenodo.19902776)
[![Streamlit Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pacif-demo.streamlit.app)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)

---

## 🔍 The Problem

Modern recommendation systems operate as closed-loop controllers: user actions train the model, and the model shapes future exposure. This creates feedback loops that can lead to **behavioral lock-in**, **filter bubbles**, and **algorithmic manipulation**.

Yet, platforms, regulators, and researchers lack a **transparent, statistically rigorous, and audit-ready metric** to quantify how tightly user behavior is coupled to system context. Existing methods suffer from finite-sample bias, lack reliability diagnostics, and are often misinterpreted as causal claims.

## 🛠️ What PACIF Does

PACIF (Predictive Alignment & Causal Information Flow) is an open-source framework that measures **predictive alignment** between user actions (U) and system recommendations (S) while controlling for observed confounders (C).

It replaces naive correlation metrics with a production-ready diagnostic layer:

- ✅ **Bias-corrected Mutual Information** (reduces finite-sample bias by 40–65%)
- ✅ **Strict reliability diagnostics** (automatically flags statistically unstable estimates via CI width thresholds)
- ✅ **Cumulative drift detection** (CUSUM + Page-Hinkley for non-stationary behavioral streams)
- ✅ **Regulator-ready audit reports** (machine-readable YAML with anti-gaming checks)
- ✅ **Causal integration pattern** (PACIF features reduce DR-estimator bias by ~89% in simulations)

## 👥 Who Needs This?

| Audience | Primary Use Case |
|----------|------------------|
| **Product & RecSys Teams** | Monitor engagement vs. diversity trade-offs; detect over-optimization before churn drops |
| **Regulators & Auditors** | Verify platform compliance with AI Act/DSA using reproducible, uncertainty-bound metrics |
| **Researchers** | Run cross-domain studies on algorithmic influence with standardized, citation-ready tools |
| **Ethics & Safety Teams** | Quantify behavioral lock-in risk without relying on opaque engagement proxies or welfare assumptions |

## 🚀 Quick Start

### 🌐 Try the Live Demo

No installation required: **[Launch PACIF Demo](https://pacif-demo.streamlit.app)**
```

### 💻 Install Locally


```bash
pip install -r requirements.txt
streamlit run app.py

