from __future__ import annotations

import time

import trino

from .base import EngineClient, ExecutionResult


class TrinoClient(EngineClient):
    name = "trino"

    def connect(self) -> None:
        self.conn = trino.dbapi.connect(
            host=self.options.get("host", "localhost"),
            port=self.options.get("port", 8080),
            user=self.options.get("user", "benchmark"),
            catalog=self.options.get("catalog", "hive"),
            schema=self.options.get("schema", "benchmark"),
        )

    def execute(self, sql: str) -> ExecutionResult:
        cur = self.conn.cursor()
        start = time.perf_counter()
        cur.execute(sql)
        rows = cur.fetchall()
        elapsed_ms = (time.perf_counter() - start) * 1000

        stats = cur.stats or {}
        return ExecutionResult(
            rows_returned=len(rows),
            execution_time_ms=stats.get("elapsedTimeMillis", elapsed_ms),
            planning_time_ms=stats.get("queuedTimeMillis"),
            rows_processed=stats.get("processedRows"),
            bytes_scanned=stats.get("processedBytes"),
        )

    def close(self) -> None:
        self.conn.close()
