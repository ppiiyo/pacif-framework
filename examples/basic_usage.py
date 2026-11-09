"""
Basic usage example for PACIF Framework.

Demonstrates:
- Estimating predictive alignment (bias-corrected mutual information)
- Reliability diagnostics
- Drift detection over a sequence of sessions
- Generating a regulator-ready audit report
"""

from __future__ import annotations

import numpy as np

from pacif_core import AuditReporter, DriftDetector, estimate_alignment


def generate_session(
    n_events: int = 80,
    coupling: float = 0.7,
    n_categories: int = 5,
    seed: int | None = None,
):
    """Generate a synthetic user-action / system-context session."""
    rng = np.random.default_rng(seed)
    events = rng.integers(0, n_categories, size=n_events)
    contexts = events.copy()
    # Inject noise according to coupling strength
    noise_mask = rng.random(n_events) > coupling
    contexts[noise_mask] = rng.integers(0, n_categories, size=int(noise_mask.sum()))
    return events, contexts


def main():
    print("PACIF v3.0 — Basic Usage Example\n" + "=" * 50)

    # --- Single session estimation ---
    events, contexts = generate_session(n_events=100, coupling=0.85, seed=42)
    result = estimate_alignment(events, contexts)

    print("\n1. Single-session alignment estimate")
    print(f"   Status      : {result['status']}")
    if result["status"] == "success":
        print(f"   MI estimate : {result['mi_estimate']:.4f} nats")
        print(f"   95% CI      : [{result['ci_95'][0]:.4f}, {result['ci_95'][1]:.4f}]")
        print(f"   Reliable    : {result['reliable']}")
        print(f"   n_events    : {result['n_events']}")

    # --- Multi-session analysis with drift ---
    print("\n2. Multi-session analysis + drift detection")
    detector = DriftDetector(threshold=0.15)
    results = []

    for i in range(120):
        # Simulate a gradual increase in coupling (potential lock-in)
        coupling = 0.55 + 0.003 * i
        ev, ctx = generate_session(n_events=70, coupling=min(coupling, 0.95), seed=100 + i)
        res = estimate_alignment(ev, ctx)
        if res["status"] == "success":
            drift_info = detector.update(res["mi_estimate"])
            res["drift"] = drift_info.get("drift", False)
        results.append(res)

    successful = [r for r in results if r.get("status") == "success"]
    reliable = [r for r in successful if r.get("reliable")]
    drift_events = sum(1 for r in successful if r.get("drift"))

    print(f"   Sessions processed : {len(results)}")
    print(f"   Successful         : {len(successful)}")
    print(f"   Reliable           : {len(reliable)} ({100 * len(reliable) / max(len(successful), 1):.1f}%)")
    print(f"   Drift detections   : {drift_events}")

    if reliable:
        mi_values = [r["mi_estimate"] for r in reliable]
        print(f"   Mean MI            : {np.mean(mi_values):.4f} nats")
        print(f"   Median MI          : {np.median(mi_values):.4f} nats")

    # --- Audit report ---
    print("\n3. Regulator-ready audit report (YAML excerpt)")
    report = AuditReporter.generate_report(results)
    print(report[:600] + ("..." if len(report) > 600 else ""))

    print("\nDone. For interactive exploration see the Streamlit demo:")
    print("https://pacif-demo.streamlit.app")


if __name__ == "__main__":
    main()
