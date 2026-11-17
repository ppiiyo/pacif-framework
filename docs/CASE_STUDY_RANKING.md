# Case study: ranking release monitor

**Job-to-be-done:** After shipping a ranking or personalization change, check whether **user actions became more predictable from system context** — and whether those estimates are trustworthy.

## One command

```bash
pip install pacif-framework
python examples/ranking_release_monitor.py
```

Uses **synthetic** sessions (seeded). Replace generators with your `(U, S)` event streams.

## What you read

| Output | Meaning |
|--------|---------|
| **Median MI (nats)** | Typical coupling strength in the phase |
| **Reliability %** | Share of estimates that passed CI / cardinality checks |
| **Drift alarms** | CUSUM trips on the post-release MI stream |
| **Audit YAML** | Flags (exclusion rate, high-coupling cluster, …) + schema 1.2 `parameters` |

## How to talk about it

Preferred:

> “Post-release median MI rose while reliability stayed high — user actions are more statistically predictable from context.”

Avoid:

> “The new ranker causes addiction / manipulation.”

Causal claims need experiments or stronger identification. PACIF is the **continuous diagnostic**, not the verdict.

## Production sketch

1. Log discrete user action `U` and exposure/context `S` per session (stable category vocab).
2. Nightly: `estimate_alignment` per session or window → store MI + `reliable`.
3. Stream reliable MI into `DriftDetector` / `PageHinkleyDetector`.
4. File `AuditReporter.generate_report(...)` into your risk or observability store.
5. Alert if reliability collapses or median MI jumps past a **domain-calibrated** band.

Full language and flags: [INTERPRETATION.md](INTERPRETATION.md).
