from __future__ import annotations

import time

import requests

from .base import EngineClient, ExecutionResult


class DrillClient(EngineClient):
    """Uses Drill's REST API (POST /query.json) rather than JDBC/ODBC to avoid
    a JVM driver dependency in the runner. Drill's REST response doesn't carry
    processed-rows/bytes, only the result set itself, so those fields stay
    None; wall-clock timing (including the plan phase) is what's measured.
    """

    name = "drill"

    def connect(self) -> None:
        self.base_url = self.options.get("rest_url", "http://localhost:8047").rstrip("/")
        self.session = requests.Session()

    def execute(self, sql: str) -> ExecutionResult:
        start = time.perf_counter()
        resp = self.session.post(
            f"{self.base_url}/query.json",
            json={"queryType": "SQL", "query": sql},
            timeout=600,
        )
        resp.raise_for_status()
        elapsed_ms = (time.perf_counter() - start) * 1000
        body = resp.json()
        rows = body.get("rows", [])
        return ExecutionResult(rows_returned=len(rows), execution_time_ms=elapsed_ms)

    def close(self) -> None:
        self.session.close()
