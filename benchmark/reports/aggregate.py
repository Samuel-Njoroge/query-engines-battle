"""Aggregates results/*.jsonl into per (engine, query, dataset_size) statistics,
per README section 7.3: min, max, mean, median, p95, standard deviation.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "results"


def load_records(results_dir: Path = RESULTS_DIR) -> list[dict]:
    records: list[dict] = []
    for path in sorted(results_dir.glob("*.jsonl")):
        with path.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def _percentile(values: list[float], pct: float) -> float:
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    k = (len(values) - 1) * pct
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    if lo == hi:
        return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


def aggregate(records: list[dict]) -> list[dict]:
    """Groups measured (non-warmup, non-error) runs and computes summary stats."""
    groups: dict[tuple, list[float]] = {}
    rows_by_group: dict[tuple, list[int | None]] = {}

    for r in records:
        if r.get("is_warmup") or r.get("error"):
            continue
        key = (r["engine"], r["query"], r["query_category"], r["dataset_size"])
        groups.setdefault(key, []).append(r["execution_time_ms"])
        rows_by_group.setdefault(key, []).append(r.get("rows_returned"))

    summary = []
    for (engine, query, category, dataset_size), times in sorted(groups.items()):
        summary.append(
            {
                "engine": engine,
                "query": query,
                "query_category": category,
                "dataset_size": dataset_size,
                "runs": len(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "mean_ms": statistics.fmean(times),
                "median_ms": statistics.median(times),
                "p95_ms": _percentile(times, 0.95),
                "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
            }
        )
    return summary


def main() -> None:
    records = load_records()
    if not records:
        print(f"No result files found in {RESULTS_DIR}")
        return
    for row in aggregate(records):
        print(
            f"{row['engine']:8s} {row['query']:28s} {row['dataset_size']:8s} "
            f"n={row['runs']} mean={row['mean_ms']:.1f}ms p95={row['p95_ms']:.1f}ms "
            f"stdev={row['stdev_ms']:.1f}ms"
        )


if __name__ == "__main__":
    main()
