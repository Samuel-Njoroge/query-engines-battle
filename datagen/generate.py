#!/usr/bin/env python3
"""Generate the shared synthetic benchmark dataset as partitioned Parquet.

Usage:
    python datagen/generate.py --scale tiny --out datasets/
    python datagen/generate.py --scale small --tables sales,fact_events --out datasets/

All generation is vectorized with numpy/pandas (no per-row Python loops) and fact
tables are written in chunks so the "large" (1B+ row) tier stays feasible without
holding the whole table in memory at once.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))

from schemas import (  # noqa: E402
    COUNTRIES,
    CUSTOMER_SEGMENTS,
    CUSTOMERS,
    DATASET_END_DATE,
    DATASET_START_DATE,
    EVENT_TYPES,
    FACT_EVENTS,
    PRODUCT_CATEGORIES,
    PRODUCTS,
    PRODUCTS_ROW_COUNT,
    SALES,
    SCALE_TIERS,
    customers_row_count,
    fact_row_count,
)

CHUNK_SIZE = 2_000_000
DEFAULT_SEED = 42


def _rng(seed: int, salt: str) -> np.random.Generator:
    # Distinct-but-reproducible stream per table/chunk.
    return np.random.default_rng(seed=abs(hash((seed, salt))) % (2**32))


def _write_table(df: pd.DataFrame, out_dir: Path, table_name: str, partition_column: str | None) -> None:
    table = pa.Table.from_pandas(df, preserve_index=False)
    dest = out_dir / table_name
    if partition_column:
        pq.write_to_dataset(
            table,
            root_path=str(dest),
            partition_cols=[partition_column],
            compression="snappy",
            existing_data_behavior="overwrite_or_ignore",
        )
    else:
        dest.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, dest / "part-0.parquet", compression="snappy")


def generate_customers(scale: str, out_dir: Path, seed: int = DEFAULT_SEED) -> int:
    n = customers_row_count(scale)
    rng = _rng(seed, "customers")
    df = pd.DataFrame(
        {
            "customer_id": np.arange(1, n + 1, dtype=np.int64),
            "name": [f"customer_{i}" for i in range(1, n + 1)],
            "country": rng.choice(COUNTRIES, size=n),
            "segment": rng.choice(CUSTOMER_SEGMENTS, size=n, p=[0.7, 0.25, 0.05]),
            "signup_date": pd.to_datetime(
                rng.integers(
                    pd.Timestamp(DATASET_START_DATE).value // 10**9 - 3 * 365 * 86400,
                    pd.Timestamp(DATASET_START_DATE).value // 10**9,
                    size=n,
                ),
                unit="s",
            ).date,
        }
    )
    _write_table(df, out_dir, CUSTOMERS.name, CUSTOMERS.partition_column)
    return n


def generate_products(out_dir: Path, seed: int = DEFAULT_SEED) -> int:
    n = PRODUCTS_ROW_COUNT
    rng = _rng(seed, "products")
    categories = list(PRODUCT_CATEGORIES.keys())
    cat_choices = rng.choice(categories, size=n)
    sub_choices = [rng.choice(PRODUCT_CATEGORIES[c]) for c in cat_choices]
    df = pd.DataFrame(
        {
            "product_id": np.arange(1, n + 1, dtype=np.int64),
            "name": [f"product_{i}" for i in range(1, n + 1)],
            "category": cat_choices,
            "sub_category": sub_choices,
            "unit_price": rng.gamma(shape=2.0, scale=25.0, size=n).round(2),
        }
    )
    _write_table(df, out_dir, PRODUCTS.name, PRODUCTS.partition_column)
    return n


def _date_range_seconds() -> tuple[int, int]:
    start = pd.Timestamp(DATASET_START_DATE).value // 10**9
    end = pd.Timestamp(DATASET_END_DATE).value // 10**9
    return int(start), int(end)


def generate_sales(scale: str, out_dir: Path, n_customers: int, seed: int = DEFAULT_SEED) -> int:
    total = fact_row_count(scale)
    start_s, end_s = _date_range_seconds()
    written = 0
    next_id = 1
    while written < total:
        chunk_n = min(CHUNK_SIZE, total - written)
        rng = _rng(seed, f"sales-{written}")
        ts = rng.integers(start_s, end_s, size=chunk_n)
        df = pd.DataFrame(
            {
                "sale_id": np.arange(next_id, next_id + chunk_n, dtype=np.int64),
                "customer_id": rng.integers(1, n_customers + 1, size=chunk_n, dtype=np.int64),
                "product_id": rng.integers(1, PRODUCTS_ROW_COUNT + 1, size=chunk_n, dtype=np.int64),
                "sale_timestamp": pd.to_datetime(ts, unit="s"),
                "quantity": rng.integers(1, 10, size=chunk_n, dtype=np.int32),
                "amount": rng.gamma(shape=2.0, scale=40.0, size=chunk_n).round(2),
            }
        )
        df["sale_date"] = df["sale_timestamp"].dt.date
        _write_table(df, out_dir, SALES.name, SALES.partition_column)
        written += chunk_n
        next_id += chunk_n
    return written


def generate_fact_events(scale: str, out_dir: Path, n_customers: int, seed: int = DEFAULT_SEED) -> int:
    total = fact_row_count(scale)
    start_s, end_s = _date_range_seconds()
    written = 0
    next_id = 1
    while written < total:
        chunk_n = min(CHUNK_SIZE, total - written)
        rng = _rng(seed, f"events-{written}")
        ts = rng.integers(start_s, end_s, size=chunk_n)
        event_types = rng.choice(EVENT_TYPES, size=chunk_n)
        is_purchase = event_types == "purchase"
        amount = np.where(
            is_purchase,
            rng.gamma(shape=2.0, scale=40.0, size=chunk_n).round(2),
            0.0,
        )
        df = pd.DataFrame(
            {
                "event_id": np.arange(next_id, next_id + chunk_n, dtype=np.int64),
                "customer_id": rng.integers(1, n_customers + 1, size=chunk_n, dtype=np.int64),
                "event_time": pd.to_datetime(ts, unit="s"),
                "country": rng.choice(COUNTRIES, size=chunk_n),
                "event_type": event_types,
                "amount": amount,
            }
        )
        df["event_date"] = df["event_time"].dt.date
        _write_table(df, out_dir, FACT_EVENTS.name, FACT_EVENTS.partition_column)
        written += chunk_n
        next_id += chunk_n
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scale", choices=sorted(SCALE_TIERS), default="tiny", help="Named scale tier (default: tiny)")
    parser.add_argument("--rows", type=int, default=None, help="Override the fact-table row count instead of using --scale's tier")
    parser.add_argument("--out", type=Path, default=Path("datasets"), help="Output root directory (default: datasets/)")
    parser.add_argument(
        "--tables",
        default="customers,products,sales,fact_events",
        help="Comma-separated subset of tables to generate",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--overwrite", action="store_true", help="Delete the destination scale directory first")
    args = parser.parse_args()

    if args.rows is not None:
        SCALE_TIERS[args.scale] = args.rows

    tables = {t.strip() for t in args.tables.split(",") if t.strip()}
    out_dir = args.out / args.scale

    if args.overwrite and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating scale='{args.scale}' ({fact_row_count(args.scale):,} fact rows) into {out_dir}")

    n_customers = customers_row_count(args.scale)
    if "customers" in tables:
        n = generate_customers(args.scale, out_dir, args.seed)
        print(f"  customers: {n:,} rows")
    if "products" in tables:
        n = generate_products(out_dir, args.seed)
        print(f"  products: {n:,} rows")
    if "sales" in tables:
        n = generate_sales(args.scale, out_dir, n_customers, args.seed)
        print(f"  sales: {n:,} rows")
    if "fact_events" in tables:
        n = generate_fact_events(args.scale, out_dir, n_customers, args.seed)
        print(f"  fact_events: {n:,} rows")

    print("Done.")


if __name__ == "__main__":
    main()
