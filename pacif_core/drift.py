"""Drift detectors for sequential MI (or other scalar) streams.

CUSUM uses a fixed post-warmup baseline. Page–Hinkley uses a running mean.
Calibrate thresholds via average run length (ARL) under stationary noise —
see :class:`PageHinkleyDetector` docstring for a simulation table.
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
    """Classic two-sided Page–Hinkley detector (running mean).

    After warmup the detector maintains a running mean ``mu_t``. Cumulative
    sums use the previous-step mean (standard sequential update)::

        m_t += (x_t - mu_{t-1} - delta);   M_t = min(M, m_t)
        w_t += (mu_{t-1} - x_t - delta);   Wm_t = min(Wm, w_t)

    Alarm when ``m_t - M_t > lambda_`` (up) or ``w_t - Wm_t > lambda_`` (down).
    On alarm returns the **pre-drift** baseline (mean of the last completed
    warmup / rebaseline window), then spends ``rebaseline_window`` steps
    rebuilding the baseline before statistics resume.

    This is **not** the same as :class:`DriftDetector` (CUSUM with a fixed
    baseline and reflected max-0 recursions).

    **ARL calibration** (stationary N(level, σ²), delta=0.005, warmup=50,
    20 seeds × 2000 steps, first-alarm time censored at 2000):

    =======  =========  ==============
    σ        lambda_    mean ARL
    =======  =========  ==============
    0.005    0.15       > 500 (0 alarms / 500 steps, 10 seeds)
    0.02     0.15       ≈ 80
    0.02     0.40       ≈ 130
    0.02     0.80       ≈ 200
    0.02     1.20       ≈ 300
    =======  =========  ==============

    Choose ``lambda_`` for a target ARL under the noise level of the upstream
    MI series; do not use a fixed multiple of SE alone.
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
        self._n = 0
        self._m = 0.0
        self._m_min = 0.0
        self._w = 0.0
        self._w_min = 0.0
        self._rebaselining = False
        self._rebase_buf: List[float] = []

    def _reset_ph(self) -> None:
        self._mean = 0.0
        self._n = 0
        self._m = 0.0
        self._m_min = 0.0
        self._w = 0.0
        self._w_min = 0.0

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

        if self._n == 0:
            prev_mean = float(self.baseline)
            self._mean = float(self.baseline)
            self._n = 1
        else:
            prev_mean = self._mean
            self._n += 1
            self._mean = self._mean + (value - self._mean) / float(self._n)

        self._m += value - prev_mean - self.delta
        if self._m < self._m_min:
            self._m_min = self._m

        self._w += prev_mean - value - self.delta
        if self._w < self._w_min:
            self._w_min = self._w

        up = self._m - self._m_min > self.lambda_
        down = self._w - self._w_min > self.lambda_
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
