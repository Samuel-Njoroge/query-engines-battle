"""Builds one result record (README section 8's schema, extended) per query run."""

from __future__ import annotations

import datetime as dt
from dataclasses import asdict

from benchmark.runner.engines.base import ExecutionResult


def build_record(
    *,
    engine: str,
    query_id: str,
    query_category: str,
    dataset_size: str,
    run: int,
    is_warmup: bool,
    result: ExecutionResult | None,
    resource_summary: dict,
    error: str | None = None,
) -> dict:
    record = {
        "engine": engine,
        "query": query_id,
        "query_category": query_category,
        "dataset_size": dataset_size,
        "run": run,
        "is_warmup": is_warmup,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "error": error,
    }
    if result is not None:
        record.update(asdict(result))
    else:
        record.update(
            {
                "rows_returned": None,
                "execution_time_ms": None,
                "planning_time_ms": None,
                "rows_processed": None,
                "bytes_scanned": None,
            }
        )
    record.update(resource_summary)
    return record
