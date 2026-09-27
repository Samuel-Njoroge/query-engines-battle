#!/usr/bin/env python3
"""Upload a generated dataset (see datagen/generate.py) into the Garage
(S3-compatible) bucket that Trino, Drill, Doris, Pinot and Druid all
ingest/query from.

Usage:
    python scripts/upload_to_s3.py --scale tiny --dataset-dir datasets/

Requires the `garage` docker-compose service (profile `data`) to be running -
it self-bootstraps the `benchmark-data` bucket and access key on first start,
see infra/garage/entrypoint.sh.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import boto3
from botocore.client import Config

BUCKET = "benchmark-data"
DEFAULT_ACCESS_KEY = "GK86b64fdb0310ad7397228be5"
DEFAULT_SECRET_KEY = "4d1395f9529c8e8b9a7f61d1d31bf46714e30fa1a03ee1600c5b1ba599c131b2"


def get_client(endpoint: str, access_key: str, secret_key: str):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def upload_dir(client, local_dir: Path, bucket: str, prefix: str) -> int:
    count = 0
    for path in local_dir.rglob("*.parquet"):
        key = f"{prefix}/{path.relative_to(local_dir).as_posix()}"
        client.upload_file(str(path), bucket, key)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scale", required=True, help="Scale tier under --dataset-dir to upload (e.g. tiny)")
    parser.add_argument("--dataset-dir", type=Path, default=Path("datasets"))
    parser.add_argument("--endpoint", default=os.environ.get("S3_ENDPOINT", "http://localhost:9000"))
    parser.add_argument("--access-key", default=os.environ.get("S3_ACCESS_KEY", DEFAULT_ACCESS_KEY))
    parser.add_argument("--secret-key", default=os.environ.get("S3_SECRET_KEY", DEFAULT_SECRET_KEY))
    args = parser.parse_args()

    local_dir = args.dataset_dir / args.scale
    if not local_dir.exists():
        raise SystemExit(f"{local_dir} does not exist - run datagen/generate.py --scale {args.scale} first")

    client = get_client(args.endpoint, args.access_key, args.secret_key)

    total = upload_dir(client, local_dir, BUCKET, args.scale)
    print(f"Uploaded {total} Parquet files to s3://{BUCKET}/{args.scale}/")


if __name__ == "__main__":
    main()
