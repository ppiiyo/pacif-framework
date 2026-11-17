#!/usr/bin/env python3
"""
Case study: did a ranking change tighten user↔context coupling?

Simulates pre-release vs post-release sessions (synthetic, seeded).
Prints median MI, reliability ratio, and drift alarms — the triad a
Trust & Safety or ranking team would read after a personalization ship.

Run:
    pip install pacif-framework
    python examples/ranking_release_monitor.py
"""
from __future__ import annotations

import numpy as np

from pacif_core import AuditReporter, DriftDetector, estimate_alignment


def _session(
    n_events: int,
    coupling: float,
    n_cat: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    u = rng.integers(0, n_cat, size=n_events)
    s = u.copy()
    flip = rng.random(n_events) > coupling
    s[flip] = rng.integers(0, n_cat, size=int(flip.sum()))
    return u, s


def _phase(
    name: str,
    n_sessions: int,
    coupling: float,
    seed: int,
    n_events: int = 120,
    n_cat: int = 4,
) -> list[dict]:
    rng = np.random.default_rng(seed)
    out: list[dict] = []
    for _ in range(n_sessions):
        u, s = _session(n_events, coupling, n_cat, rng)
        # Max events off so small demos are not subsampled away
        out.append(estimate_alignment(u, s, max_events=None))
    ok = [r for r in out if r.get("status") == "success"]
    rel = [r for r in ok if r.get("reliable")]
    mi = [r["mi_estimate"] for r in rel]
    print(f"\n=== {name} (coupling={coupling:.2f}) ===")
    print(f"  sessions     : {n_sessions}")
    print(f"  successful   : {len(ok)}")
    print(f"  reliable     : {len(rel)} ({100 * len(rel) / max(len(ok), 1):.0f}% of successful)")
    if mi:
        print(f"  median MI    : {float(np.median(mi)):.3f} nats")
        print(f"  mean MI      : {float(np.mean(mi)):.3f} nats")
    else:
        print("  median MI    : n/a (no reliable estimates)")
    return out


def main() -> None:
    print("PACIF case study: ranking release monitor")
    print("Synthetic data only — illustrates the reporting pattern, not a real A/B.")

    pre = _phase("PRE-release (weaker personalization)", n_sessions=40, coupling=0.55, seed=1)
    post = _phase("POST-release (stronger personalization)", n_sessions=40, coupling=0.88, seed=2)

    # Stream POST MI into CUSUM as if sessions arrive over time
    det = DriftDetector(threshold=0.12, slack=0.005)
    alarms = 0
    for r in post:
        if r.get("status") == "success" and r.get("reliable"):
            if det.update(float(r["mi_estimate"])).get("drift"):
                alarms += 1
    print("\n=== Drift on POST stream ===")
    print(f"  CUSUM alarms : {alarms}")

    report = AuditReporter.generate_report(
        pre + post, context={"scenario": "ranking_release_synthetic"}
    )
    print("\n=== Audit report (head) ===")
    print("\n".join(report.splitlines()[:25]))
    print("...")
    print("\nInterpretation: higher POST MI with good reliability → stronger")
    print("statistical coupling after the ship. Investigate lock-in on real logs;")
    print("do not claim causality from PACIF alone. See docs/INTERPRETATION.md")


if __name__ == "__main__":
    main()
