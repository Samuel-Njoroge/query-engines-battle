#!/usr/bin/env python3
"""Register the fact_events and sales schemas/table configs with the Pinot
controller. Run once after the `pinot` compose profile is up, before launching
the ingestion jobs under engines/pinot/ingestion/.

Usage:
    python scripts/setup_pinot.py --controller http://localhost:9000
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests

ENGINE_DIR = Path(__file__).resolve().parent.parent / "engines" / "pinot"
TABLES = ["fact_events", "sales"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller", default="http://localhost:9000")
    args = parser.parse_args()

    for table in TABLES:
        schema = json.loads((ENGINE_DIR / "schemas" / f"{table}.schema.json").read_text())
        resp = requests.post(f"{args.controller}/schemas", json=schema, timeout=30)
        print(f"schema {table}: {resp.status_code} {resp.text[:200]}")

        table_config = json.loads((ENGINE_DIR / "tableconfigs" / f"{table}.table.json").read_text())
        resp = requests.post(f"{args.controller}/tables", json=table_config, timeout=30)
        print(f"table {table}: {resp.status_code} {resp.text[:200]}")


if __name__ == "__main__":
    main()
