from __future__ import annotations

import requests

from .base import EngineClient, ExecutionResult


class PinotClient(EngineClient):
    """Uses the Pinot Broker's SQL REST endpoint. Pinot's response already
    includes real server-side timing and scan stats (timeUsedMs,
    numDocsScanned), so - unlike Doris/Drill - this client doesn't need to
    fall back to wall-clock measurement.
    """

    name = "pinot"

    def connect(self) -> None:
        self.base_url = self.options.get("broker_url", "http://localhost:8099").rstrip("/")
        self.session = requests.Session()

    def execute(self, sql: str) -> ExecutionResult:
        resp = self.session.post(f"{self.base_url}/query/sql", json={"sql": sql}, timeout=600)
        resp.raise_for_status()
        body = resp.json()

        if body.get("exceptions"):
            raise RuntimeError(f"Pinot query failed: {body['exceptions']}")

        rows = body.get("resultTable", {}).get("rows", [])
        return ExecutionResult(
            rows_returned=len(rows),
            execution_time_ms=body.get("timeUsedMs", 0),
            rows_processed=body.get("numDocsScanned"),
        )

    def close(self) -> None:
        self.session.close()
