"""Common interface every engine client implements.

Each engine reports what it can: Trino and Pinot expose real processed-rows /
processed-bytes stats; Doris, Drill and Druid mostly don't over their simple
query APIs, so those fields stay None and the executor falls back to wall-clock
timing plus rows_returned - this asymmetry is recorded in the result rather
than papered over.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    rows_returned: int
    execution_time_ms: float
    planning_time_ms: float | None = None
    rows_processed: int | None = None
    bytes_scanned: int | None = None


class EngineClient(ABC):
    name: str

    def __init__(self, options: dict):
        self.options = options

    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod
    def execute(self, sql: str) -> ExecutionResult:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    def __enter__(self) -> "EngineClient":
        self.connect()
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
