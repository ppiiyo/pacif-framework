"""Rough throughput benchmark for estimate_alignment."""
from __future__ import annotations

import time

import numpy as np

from pacif_core import estimate_alignment


def make_batch(n_sessions: int, n_events: int = 60, seed: int = 0):
    rng = np.random.default_rng(seed)
    batch = []
    for _ in range(n_sessions):
        ev = rng.integers(0, 5, size=n_events)
        ctx = ev.copy()
        mask = rng.random(n_events) < 0.25
        ctx[mask] = rng.integers(0, 5, size=int(mask.sum()))
        batch.append((ev, ctx))
    return batch


def main():
    batch = make_batch(2000, n_events=60, seed=42)
    # Warmup (Numba JIT)
    estimate_alignment(*batch[0])

    t0 = time.perf_counter()
    ok = 0
    for ev, ctx in batch:
        r = estimate_alignment(ev, ctx)
        if r.get("status") == "success":
            ok += 1
    elapsed = time.perf_counter() - t0
    rate = len(batch) / elapsed
    print(f"Sessions: {len(batch)}")
    print(f"Successful: {ok}")
    print(f"Elapsed: {elapsed:.3f}s")
    print(f"Throughput: {rate:.0f} sessions/sec")


if __name__ == "__main__":
    main()
