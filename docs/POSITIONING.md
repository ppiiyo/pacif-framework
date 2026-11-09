# PACIF Positioning One-Pager

**For outreach, partnerships, and internal alignment.**

---

## One sentence

PACIF quantifies how tightly recommendation systems couple user behavior to algorithmic context — with bias-corrected mutual information, reliability diagnostics, and regulator-ready audit reports.

---

## Problem

Recommendation systems are closed loops. Platforms and regulators lack a transparent, statistically rigorous metric of human–algorithm coupling that is honest about uncertainty and resistant to naive misuse as a “causality” claim.

## Solution

Open-source diagnostic layer:

- Bias-corrected MI (Miller-Madow)
- Reliability gates (CI-based)
- Drift detection (CUSUM-style)
- YAML audits with anti-gaming flags
- Optional features for causal estimators (DR bias reduction in simulations)

## What we are **not**

- Not a wellbeing score
- Not a proof of manipulation
- Not a substitute for experiments when causal claims are required

## Who cares

| Audience | Job-to-be-done |
|----------|----------------|
| Responsible AI / Trust & Safety | Monitor personalization strength and lock-in risk |
| Platforms | Production diagnostics on feedback loops |
| Regulators / auditors | Audit-ready, machine-readable evidence |
| Researchers | Reproducible metric + DR integration pattern |

## Differentiation

| Alternative | Gap |
|-------------|-----|
| Naive correlation / MI | Finite-sample bias, no reliability, no audit |
| Pure explainability (SHAP/LIME) | Different question (feature attribution ≠ coupling over time) |
| Only A/B tests | Expensive; PACIF is continuous monitoring layer |
| Opaque vendor “risk scores” | Not transparent, not reproducible |

## Proof points

- Bias reduction 40–65% vs naive MI (Miller-Madow)
- DR bias reduction ~89% in controlled simulations when PACIF features are included
- Throughput >1,900 sessions/sec, p95 latency <1 ms (reference)
- Apache-2.0, DOI on Zenodo, explicit statistical boundaries

## Ask (pick one)

1. **Pilot** on historical session logs (read-only metric)
2. **Design partner** for audit report schema
3. **Citation / workshop** collaboration in accountability research

Contact: for.smirnov.maks@gmail.com  
Repo: https://github.com/ppiiyo/pacif-framework  
Demo: https://pacif-demo.streamlit.app
