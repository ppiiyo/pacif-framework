# PACIF Interpretation Guide

This guide helps practitioners **read**, **communicate**, and **act on** PACIF outputs without overclaiming.

PACIF measures **predictive alignment** (statistical coupling) between user actions and system context. It does **not** measure causality, intent, harm, or wellbeing.

---

## 1. Core metrics

### Signal Strength (Mutual Information, nats)

| Range (nats) | Practical reading | Suggested stance |
|--------------|-------------------|------------------|
| < 0.1 | Weak / noisy coupling | Do not over-interpret; check sample size |
| 0.1 – 0.3 | Mild personalization-level coupling | Typical for many healthy systems |
| 0.3 – 0.8 | Moderate to strong coupling | Monitor segments and trends |
| > 0.8 | Very strong coupling | Investigate lock-in / filter-bubble risk |

These thresholds are **decision heuristics**, not universal laws. Calibrate against your domain baselines.

### Reliability

An estimate is marked **reliable** when confidence-interval diagnostics pass internal thresholds (CI width and relative width).

- **Reliability ratio < 70%** → increase window size, sample size, or reduce category cardinality before drawing conclusions.
- Never average or promote unreliable estimates as if they were solid evidence.

### Drift

Drift means the **relationship** between user actions and system context has shifted enough to trip CUSUM-style detectors.

- Drift ≠ “users are worse off”.
- Drift ⇒ re-check model calibration, content mix, policy changes, or data pipeline breaks.

---

## 2. Decision framework

```
1. Is the estimate reliable?
   └─ No  → Collect more data / widen window. Stop.
   └─ Yes → Continue.

2. What is the signal level?
   └─ Low      → Optional monitoring.
   └─ Moderate → Segment analysis; track trends.
   └─ High     → Deep dive: cohorts, content types, time-of-day.

3. Is there drift?
   └─ Yes → Correlate with releases, ranking changes, incidents.

4. Audit flags present?
   └─ HIGH_EXCLUSION_RATE, CATEGORY_INFLATION_RISK, etc.
      → Fix measurement process before policy conclusions.
```

---

## 3. How to communicate results

### Preferred language

- “User actions are **statistically predictable** from system context at MI ≈ X nats.”
- “The coupling estimate is **reliable** on Y% of sessions.”
- “We detected **non-stationarity** in the alignment signal after date Z.”

### Avoid

- “The algorithm **causes** addiction / harm.”
- “PACIF **proves** manipulation.”
- “Users are **trapped**” (unless you have separate causal/intervention evidence).

Normative or causal claims require experiments, interventions, or stronger identification — not PACIF alone.

---

## 4. Audit report flags

| Flag | Meaning | Typical response |
|------|---------|------------------|
| `HIGH_EXCLUSION_RATE` | Too many unreliable windows | Larger samples / fewer categories |
| `CATEGORY_INFLATION_RISK` | Suspicious category growth on small windows | Review encoding / anti-gaming |
| `DISTRIBUTION_SKEW_REVIEW` | Mean–median MI gap | Check selective windowing |
| `HIGH_COUPLING_CLUSTER` | Many sessions above 0.8 nats | Segment investigation |
| `DRIFT_DETECTED` | Alignment shifted over time | Change management review |
| `NO_RELIABLE_ESTIMATES` | Nothing trustworthy in the batch | Do not report headline MI |

---

## 5. Recommended operational policy (starting point)

1. **Never** ship a compliance narrative on unreliable estimates.
2. Track **median MI + reliability ratio + drift** as a triad, not MI alone.
3. Re-baseline after major ranking or UI changes.
4. Keep category vocabularies stable across audit periods when comparing trends.
5. Pair high-MI findings with qualitative review and, where needed, A/B or holdout designs.

---

## 6. One-paragraph summary for stakeholders

> PACIF quantifies how tightly user behavior aligns with what the system shows, and whether that measurement is statistically trustworthy. High values flag strong coupling worth investigating; they do not by themselves prove harm or causal manipulation. Reliability and drift diagnostics exist specifically so teams and auditors do not over-interpret noise.
