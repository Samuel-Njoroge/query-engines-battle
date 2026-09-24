from __future__ import annotations

from .base import EngineClient, ExecutionResult
from .doris_client import DorisClient
from .drill_client import DrillClient
from .druid_client import DruidClient
from .pinot_client import PinotClient
from .trino_client import TrinoClient

CLIENTS: dict[str, type[EngineClient]] = {
    "trino": TrinoClient,
    "doris": DorisClient,
    "drill": DrillClient,
    "pinot": PinotClient,
    "druid": DruidClient,
}

__all__ = ["EngineClient", "ExecutionResult", "CLIENTS"]
