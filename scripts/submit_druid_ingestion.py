#!/usr/bin/env python3
"""Submit a native batch ingestion spec (engines/druid/ingestion/*.json) to the
Druid coordinator/overlord, substituting ${SCALE} with the dataset scale tier.

Usage:
    python scripts/submit_druid_ingestion.py --scale tiny --spec fact_events
    python scripts/submit_druid_ingestion.py --scale tiny --spec sales
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from string import Template

import requests

SPEC_DIR = Path(__file__).resolve().parent.parent / "engines" / "druid" / "ingestion"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", required=True)
    parser.add_argument("--spec", required=True, choices=["fact_events", "sales"])
    parser.add_argument("--coordinator", default="http://localhost:8081")
    args = parser.parse_args()

    raw = (SPEC_DIR / f"{args.spec}.json").read_text()
    spec = json.loads(Template(raw).substitute(SCALE=args.scale))

    resp = requests.post(f"{args.coordinator}/druid/indexer/v1/task", json=spec, timeout=30)
    resp.raise_for_status()
    task_id = resp.json().get("task")
    print(f"Submitted task {task_id} for {args.spec} (scale={args.scale})")
    print(f"Track progress at {args.coordinator}/druid/indexer/v1/task/{task_id}/status")


if __name__ == "__main__":
    main()
