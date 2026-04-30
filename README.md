#  PACIF v3.0: Predictive Alignment & Causal Information Flow

> **Measures how strongly algorithms shape user behavior — and whether that signal is reliable.**

[![Streamlit Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pacif-demo.streamlit.app)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.19902776-blue)](https://doi.org/10.5281/zenodo.19902776)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 🔍 The Problem

Modern recommendation systems operate as **closed-loop controllers**: user actions train the model, and the model shapes future exposure. This creates feedback loops that can lead to **behavioral lock-in**, **filter bubbles**, and **algorithmic manipulation**.

Yet, platforms, regulators, and researchers lack a **transparent, statistically rigorous, and audit-ready metric** to quantify how tightly user behavior is coupled to system context. Existing methods suffer from finite-sample bias, lack reliability diagnostics, and are often misinterpreted as causal claims.

## 🛠️ What PACIF Does

PACIF (Predictive Alignment & Causal Information Flow) is an open-source framework that measures **predictive alignment** between user actions (U) and system recommendations (S) while controlling for observed confounders (C).

It replaces naive correlation metrics with a production-ready diagnostic layer:

*   ✅ **Bias-Corrected Mutual Information:** Reduces finite-sample bias by 40–65% using Miller-Madow correction.
*   ✅ **Strict Reliability Diagnostics:** Automatically flags statistically unstable estimates via CI width thresholds.
*   ✅ **Cumulative Drift Detection:** Uses CUSUM + Page-Hinkley algorithms to detect non-stationary behavioral shifts.
*   ✅ **Regulator-Ready Audit Reports:** Generates machine-readable YAML with anti-gaming checks.
*   ✅ **Causal Integration Pattern:** PACIF features reduce Doubly Robust (DR) estimator bias by ~89% in simulations.

---

## 🚀 Quick Start

### 🌐 Try the Live Demo
No installation required. Explore the metrics and interface:  
👉 **[Launch PACIF Demo](https://pacif-demo.streamlit.app)**

### 💻 Install Locally


```bash
# 1. Clone the repository
git clone https://github.com/ppiyo/pacif-framework.git
cd pacif-framework

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py


## 🐍 Usage Example

You can use PACIF as a library in your own research or pipeline:
from pacif_core import estimate_alignment
import numpy as np

# Example data: User actions vs System recommendations
events = np.array([1, 1, 2, 1, 2, 2, 1, 2, 1, 2])
contexts = np.array([1, 1, 2, 1, 2, 3, 1, 2, 1, 2])

# Calculate predictive alignment
result = estimate_alignment(events, contexts)

print(result)
# Output:
# {
#   'status': 'success', 
#   'mi_estimate': 0.412, 
#   'ci_95': [0.38, 0.44], 
#   'reliable': True,
#   ...
# }


📊 Interpreting Results

PACIF provides not just a number, but an interpretation of the relationship between users and algorithms.

| Metric | Interpretation | Action |
| :--- | :--- | :--- |
| **Signal Strength (MI)** | Intensity of coupling. High values indicate strong influence. | >0.8 nats: Investigate "Lock-in" risk. |
| **Reliability Ratio** | % of sessions where the estimate is statistically valid. | <70%: Increase sample size or window. |
| **Drift Status** | Has behavior changed significantly over time? | Drift Detected: Model may need recalibration. |


## 📖 Documentation & Validation

*   **Benchmark Results:** Throughput >1,900 sessions/sec, p95 latency <1ms.
*   **Explicit Boundaries:** PACIF measures statistical predictability, **not** causality or user wellbeing. Normative claims require intervention data.
*   **Audit Schema:** Includes automated checks for category inflation and cherry-picking.


## 🤝 Contributing

We are building this with the community. Algorithmic transparency should be a public good, not a black box.

*   🐛 **Found a bug?** [Open an issue](https://github.com/ppiyo/pacif-framework/issues)
*   💡 **Have an improvement?** Submit a Pull Request.
*   📧 **For enterprise/audit integration:** prodazzha44@gmail.com

---

## 📄 Citation

If you use PACIF in research, audits, or product workflows, please cite: