#!/usr/bin/env python3
"""Benchmark runner CLI.

Examples:
    python -m benchmark.runner.main --engine trino --dataset-size tiny
    python -m benchmark.runner.main --engine trino --category aggregations --dataset-size small
    python -m benchmark.runner.main --engine trino --engine doris --dataset-size tiny
    python -m benchmark.runner.main --all-engines --dataset-size tiny

Assumes the relevant `docker compose --profile <engine> up` is already running
and reachable at the hosts/ports in benchmark/config.yaml.
"""

from __future__ import annotations

import argparse

from benchmark.runner.config import ENGINES, discover_queries, load_run_config
from benchmark.runner.executor import run_query, write_records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--engine", action="append", choices=ENGINES, dest="engines", help="Repeatable; defaults to all engines")
    parser.add_argument("--all-engines", action="store_true")
    parser.add_argument("--category", help="Only run queries in this queries/ subdirectory (default: all)")
    parser.add_argument("--query", help="Only run this single query id")
    parser.add_argument("--dataset-size", required=True, help="Scale tier the dataset was generated/loaded at (e.g. tiny)")
    args = parser.parse_args()

    engines = args.engines if args.engines and not args.all_engines else ENGINES
    run_config = load_run_config()
    queries = discover_queries(args.category)
    if args.query:
        queries = [q for q in queries if q.id == args.query]
        if not queries:
            raise SystemExit(f"No query with id '{args.query}' found under queries/")

    for engine in engines:
        if engine not in run_config.engines:
            print(f"Skipping {engine}: no entry in benchmark/config.yaml")
            continue
        engine_config = run_config.engines[engine]
        print(f"\n=== {engine} ===")
        for query in queries:
            if not query.supports(engine):
                continue
            records = run_query(engine_config, query, args.dataset_size, run_config)
            path = write_records(records, engine, query.id, args.dataset_size)
            if path:
                print(f"  wrote {path.relative_to(path.parents[1])}")


if __name__ == "__main__":
    main()
