from __future__ import annotations

import time

import requests

from .base import EngineClient, ExecutionResult


class DruidClient(EngineClient):
    """Uses Druid's synchronous SQL HTTP endpoint (POST /druid/v2/sql). Druid
    doesn't return processed-rows/bytes on this endpoint (that requires
    enabling query metrics emission and scraping them back out of the
    configured emitter), so this client measures wall-clock time only.
    """

    name = "druid"

    def connect(self) -> None:
        self.base_url = self.options.get("router_url", "http://localhost:8888").rstrip("/")
        self.session = requests.Session()

    def execute(self, sql: str) -> ExecutionResult:
        start = time.perf_counter()
        resp = self.session.post(f"{self.base_url}/druid/v2/sql", json={"query": sql}, timeout=600)
        resp.raise_for_status()
        elapsed_ms = (time.perf_counter() - start) * 1000
        rows = resp.json()
        return ExecutionResult(rows_returned=len(rows), execution_time_ms=elapsed_ms)

    def close(self) -> None:
        self.session.close()
