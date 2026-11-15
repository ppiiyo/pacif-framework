"""Drift detectors for sequential MI (or other scalar) streams.

Thresholds are absolute and expressed in the same units as the input values
(typically nats). Recommended calibration: threshold ≈ 3 * median SE of the
upstream estimator.
"""
from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, List, Optional


class DriftDetector:
    """Two-sided CUSUM drift detector.

    On alarm returns the pre-drift baseline, resets CUSUM state, and enters a
    rebaselining window of ``rebaseline_window`` observations before resuming.
    History is bounded (``deque`` maxlen 50) for streaming use.
    """

    def __init__(
        self,
        threshold: float = 0.15,
        slack: float = 0.005,
        warmup: int = 50,
        rebaseline_window: int = 50,
    ) -> None:
        self.threshold = float(threshold)
        self.slack = float(slack)
        self.warmup = int(warmup)
        self.rebaseline_window = int(rebaseline_window)
        self.cus_pos = 0.0
        self.cus_neg = 0.0
        self.history: Deque[float] = deque(maxlen=50)
        self.n_obs = 0
        self.baseline: Optional[float] = None
        self._rebaselining = False
        self._rebase_buf: List[float] = []

    def update(self, value: float) -> Dict[str, Any]:
        value = float(value)
        self.history.append(value)
        self.n_obs += 1

        if self._rebaselining:
            self._rebase_buf.append(value)
            if len(self._rebase_buf) < self.rebaseline_window:
                return {"drift": False, "reason": "rebaselining"}
            self.baseline = sum(self._rebase_buf) / float(len(self._rebase_buf))
            self._rebase_buf = []
            self._rebaselining = False
            self.cus_pos = 0.0
            self.cus_neg = 0.0
            return {"drift": False, "reason": "rebaselining"}

        if self.n_obs < self.warmup:
            return {"drift": False, "reason": "warming_up"}

        if self.baseline is None:
            self.baseline = sum(self.history) / float(len(self.history))

        dev = value - self.baseline
        self.cus_pos = max(0.0, self.cus_pos + dev - self.slack)
        self.cus_neg = max(0.0, self.cus_neg - dev - self.slack)

        if self.cus_pos > self.threshold or self.cus_neg > self.threshold:
            pre_baseline = float(self.baseline)
            self.cus_pos = 0.0
            self.cus_neg = 0.0
            self._rebaselining = True
            self._rebase_buf = []
            return {
                "drift": True,
                "value": value,
                "baseline": pre_baseline,
            }

        return {"drift": False}


class PageHinkleyDetector:
    """Two-sided Page-Hinkley detector.

    Tracks cumulative deviations from a running mean. Alarms when
    ``m_t - min(m) > lambda_`` (upward) or ``max(m) - m_t > lambda_`` (downward).
    Same warmup / rebaseline protocol as :class:`DriftDetector`.

    Thresholds are absolute (nats when applied to MI). Recommended calibration:
    ``lambda_ ≈ 3 * median SE`` of the upstream estimator.
    """

    def __init__(
        self,
        delta: float = 0.005,
        lambda_: float = 0.15,
        warmup: int = 50,
        rebaseline_window: int = 50,
    ) -> None:
        self.delta = float(delta)
        self.lambda_ = float(lambda_)
        self.warmup = int(warmup)
        self.rebaseline_window = int(rebaseline_window)
        self.history: Deque[float] = deque(maxlen=50)
        self.n_obs = 0
        self.baseline: Optional[float] = None
        self._mean = 0.0
        self._count = 0
        self._m = 0.0
        self._m_min = 0.0
        self._m_max = 0.0
        self._rebaselining = False
        self._rebase_buf: List[float] = []

    def _reset_ph(self) -> None:
        self._mean = 0.0
        self._count = 0
        self._m = 0.0
        self._m_min = 0.0
        self._m_max = 0.0

    def update(self, value: float) -> Dict[str, Any]:
        value = float(value)
        self.history.append(value)
        self.n_obs += 1

        if self._rebaselining:
            self._rebase_buf.append(value)
            if len(self._rebase_buf) < self.rebaseline_window:
                return {"drift": False, "reason": "rebaselining"}
            self.baseline = sum(self._rebase_buf) / float(len(self._rebase_buf))
            self._rebase_buf = []
            self._rebaselining = False
            self._reset_ph()
            return {"drift": False, "reason": "rebaselining"}

        if self.n_obs < self.warmup:
            return {"drift": False, "reason": "warming_up"}

        if self.baseline is None:
            self.baseline = sum(self.history) / float(len(self.history))

        self._count += 1
        self._mean += (value - self._mean) / float(self._count)
        self._m += value - self._mean - self.delta
        if self._m < self._m_min:
            self._m_min = self._m
        if self._m > self._m_max:
            self._m_max = self._m

        up = self._m - self._m_min > self.lambda_
        down = self._m_max - self._m > self.lambda_
        if up or down:
            pre_baseline = float(self.baseline)
            self._reset_ph()
            self._rebaselining = True
            self._rebase_buf = []
            return {
                "drift": True,
                "value": value,
                "baseline": pre_baseline,
            }

        return {"drift": False}
