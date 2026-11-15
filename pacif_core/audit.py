"""Regulator-ready audit report generation with anti-gaming checks."""
from __future__ import annotations

import statistics
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import yaml

from ._version import __version__

# Decision thresholds (also reported under parameters for audit transparency)
_MI_HIGH = 0.8
_MI_MODERATE = 0.3
_SKEW_FACTOR = 0.25


class AuditReporter:
    """Generate machine-readable YAML audit reports for PACIF runs."""

    @staticmethod
    def generate_report(
        results: list[dict[str, Any]],
        schema_version: str = "1.2",
        *,
        exclusion_rate_threshold: float = 0.4,
        category_inflation_ratio: float = 3.0,
        min_events_for_inflation: int = 30,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build an audit report from a list of estimate_alignment results.

        Parameters
        ----------
        results:
            List of dicts returned by ``estimate_alignment`` (and optionally
            enriched with drift flags).
        schema_version:
            Report schema version string (default ``"1.2"``).
        exclusion_rate_threshold:
            Flag ``HIGH_EXCLUSION_RATE`` when fraction of non-reliable results
            exceeds this value.
        category_inflation_ratio:
            Flag ``CATEGORY_INFLATION_RISK`` when max categories / median
            categories exceeds this ratio on small samples.
        min_events_for_inflation:
            Category-inflation heuristic uses ``ne < min_events_for_inflation * 2``.
        context:
            Optional dict merged into ``metadata`` (e.g. data fingerprint, window).
        """
        if not results:
            return yaml.dump({"status": "error", "reason": "no_data"}, default_flow_style=False)

        successful = [r for r in results if r.get("status") == "success"]
        reliable = [r for r in successful if r.get("reliable")]

        parameters = {
            "exclusion_rate_threshold": exclusion_rate_threshold,
            "category_inflation_ratio": category_inflation_ratio,
            "min_events_for_inflation": min_events_for_inflation,
            "mi_moderate": _MI_MODERATE,
            "mi_high": _MI_HIGH,
            "skew_factor": _SKEW_FACTOR,
        }

        metadata: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "framework": f"PACIF v{__version__}",
            "schema": schema_version,
        }
        if context:
            metadata.update(context)

        if not reliable:
            return yaml.dump(
                {
                    "status": "no_reliable_data",
                    "metadata": metadata,
                    "parameters": parameters,
                    "summary": {
                        "total": len(results),
                        "successful": len(successful),
                        "reliable": 0,
                    },
                    "flags": ["NO_RELIABLE_ESTIMATES"],
                },
                default_flow_style=False,
            )

        mi_vals = [float(r["mi_estimate"]) for r in reliable]
        n = len(mi_vals)
        median_mi = float(statistics.median(mi_vals))
        mean_mi = sum(mi_vals) / n
        min_mi = min(mi_vals)
        max_mi = max(mi_vals)

        exclusion_rate = 1.0 - (len(reliable) / len(results))

        flags: list[str] = []
        if exclusion_rate > exclusion_rate_threshold:
            flags.append("HIGH_EXCLUSION_RATE")

        cat_counts = []
        for r in reliable:
            nu = r.get("n_u") or 0
            ns = r.get("n_s") or 0
            ne = r.get("n_events") or 0
            cat_counts.append((max(nu, ns), ne))

        if cat_counts:
            cats = sorted(c for c, _ in cat_counts)
            median_cats = cats[len(cats) // 2] or 1
            suspicious = [
                c
                for c, ne in cat_counts
                if c >= category_inflation_ratio * median_cats
                and ne < min_events_for_inflation * 2
            ]
            if len(suspicious) >= max(1, len(cat_counts) // 5):
                flags.append("CATEGORY_INFLATION_RISK")

        if abs(mean_mi - median_mi) > _SKEW_FACTOR * max(abs(median_mi), 0.05):
            flags.append("DISTRIBUTION_SKEW_REVIEW")

        high_mi_share = sum(1 for m in mi_vals if m > _MI_HIGH) / n
        if high_mi_share > 0.5:
            flags.append("HIGH_COUPLING_CLUSTER")

        drift_hits = sum(1 for r in results if r.get("drift") is True)
        if drift_hits > 0:
            flags.append("DRIFT_DETECTED")

        rep = {
            "metadata": metadata,
            "parameters": parameters,
            "summary": {
                "total": len(results),
                "successful": len(successful),
                "reliable": len(reliable),
                "exclusion_rate": round(exclusion_rate, 4),
                "median_mi": round(median_mi, 6),
                "mean_mi": round(mean_mi, 6),
                "min_mi": round(min_mi, 6),
                "max_mi": round(max_mi, 6),
                "drift_events": drift_hits,
            },
            "flags": flags,
            "interpretation": {
                "signal": (
                    "high"
                    if median_mi > _MI_HIGH
                    else "moderate"
                    if median_mi > _MI_MODERATE
                    else "low"
                ),
                "reliability_ok": exclusion_rate <= exclusion_rate_threshold,
                "action_hint": (
                    "Investigate lock-in risk"
                    if median_mi > _MI_HIGH
                    else "Monitor"
                    if median_mi > _MI_MODERATE
                    else "Low coupling; increase sample if unexpected"
                ),
            },
        }
        return yaml.dump(rep, default_flow_style=False, sort_keys=False)
