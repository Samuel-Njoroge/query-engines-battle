"""Loads benchmark/config.yaml and discovers query definitions from queries/."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "benchmark" / "config.yaml"
QUERIES_ROOT = REPO_ROOT / "queries"

ENGINES = ["trino", "doris", "drill", "pinot", "druid"]


@dataclass(frozen=True)
class EngineConfig:
    name: str
    containers: list[str]
    options: dict


@dataclass(frozen=True)
class RunConfig:
    warmup_runs: int
    measured_runs: int
    engines: dict[str, EngineConfig]


@dataclass(frozen=True)
class QuerySpec:
    id: str
    category: str
    dir: Path
    meta: dict

    def sql_path(self, engine: str) -> Path | None:
        path = self.dir / f"{engine}.sql"
        return path if path.exists() else None

    def supports(self, engine: str) -> bool:
        return engine in self.meta.get("supported_engines", []) and self.sql_path(engine) is not None


def load_run_config(path: Path = DEFAULT_CONFIG_PATH) -> RunConfig:
    raw = yaml.safe_load(path.read_text())
    engines = {}
    for name, options in raw.get("engines", {}).items():
        options = dict(options)
        containers = options.pop("containers", [])
        engines[name] = EngineConfig(name=name, containers=containers, options=options)
    return RunConfig(
        warmup_runs=raw.get("warmup_runs", 2),
        measured_runs=raw.get("measured_runs", 5),
        engines=engines,
    )


def discover_queries(category: str | None = None) -> list[QuerySpec]:
    """Walk queries/<category>/<query_id>/meta.yaml and return QuerySpecs."""
    specs: list[QuerySpec] = []
    categories = [category] if category else sorted(p.name for p in QUERIES_ROOT.iterdir() if p.is_dir())
    for cat in categories:
        cat_dir = QUERIES_ROOT / cat
        if not cat_dir.is_dir():
            continue
        for query_dir in sorted(cat_dir.iterdir()):
            meta_path = query_dir / "meta.yaml"
            if not meta_path.exists():
                continue
            meta = yaml.safe_load(meta_path.read_text())
            specs.append(QuerySpec(id=meta["id"], category=cat, dir=query_dir, meta=meta))
    return specs
