"""Runs the warmup + measured execution loop for one (engine, query) pair,
per README section 7.1/7.3, and writes one JSON-lines file per run to results/.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from benchmark.metrics.collector import build_record
from benchmark.metrics.docker_stats import ResourceMonitor
from benchmark.runner.config import EngineConfig, QuerySpec, RunConfig
from benchmark.runner.engines import CLIENTS

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "results"


def run_query(engine_config: EngineConfig, query: QuerySpec, dataset_size: str, run_config: RunConfig) -> list[dict]:
    engine = engine_config.name
    sql_path = query.sql_path(engine)
    if sql_path is None:
        reason = query.meta.get("notes", {}).get(engine, "not applicable to this engine")
        print(f"  skip: {engine}/{query.id} - {reason}")
        return []

    sql = sql_path.read_text()
    client_cls = CLIENTS[engine]
    records: list[dict] = []
    total_runs = run_config.warmup_runs + run_config.measured_runs

    with client_cls(engine_config.options) as client:
        for run in range(1, total_runs + 1):
            is_warmup = run <= run_config.warmup_runs
            monitor = ResourceMonitor(engine_config.containers)
            result = None
            error = None
            try:
                with monitor:
                    result = client.execute(sql)
            except Exception as exc:  # noqa: BLE001 - record the failure and keep benchmarking
                error = str(exc)

            record = build_record(
                engine=engine,
                query_id=query.id,
                query_category=query.category,
                dataset_size=dataset_size,
                run=run,
                is_warmup=is_warmup,
                result=result,
                resource_summary=monitor.summary(),
                error=error,
            )
            records.append(record)

            label = "warmup" if is_warmup else "measured"
            status = "ERROR: " + error if error else f"{result.execution_time_ms:.1f}ms"
            print(f"  {engine}/{query.id} run {run}/{total_runs} ({label}): {status}")

    return records


def write_records(records: list[dict], engine: str, query_id: str, dataset_size: str) -> Path:
    if not records:
        return None
    RESULTS_DIR.mkdir(exist_ok=True)
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RESULTS_DIR / f"{engine}_{query_id}_{dataset_size}_{ts}.jsonl"
    with path.open("w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    return path
