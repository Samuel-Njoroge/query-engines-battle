from __future__ import annotations

import time

import pymysql

from .base import EngineClient, ExecutionResult


class DorisClient(EngineClient):
    """Doris FE speaks the MySQL wire protocol, so we reuse pymysql rather than
    a Doris-specific driver. Doris doesn't expose processed-rows/bytes over
    this protocol (only via SHOW PROFILE, which needs profiling enabled per
    session and is left out to keep every measured run identical) - so this
    client falls back to wall-clock timing only.
    """

    name = "doris"

    def connect(self) -> None:
        self.conn = pymysql.connect(
            host=self.options.get("host", "localhost"),
            port=self.options.get("port", 9030),
            user=self.options.get("user", "root"),
            password=self.options.get("password", ""),
            database=self.options.get("database", "benchmark"),
        )

    def execute(self, sql: str) -> ExecutionResult:
        with self.conn.cursor() as cur:
            start = time.perf_counter()
            cur.execute(sql)
            rows = cur.fetchall()
            elapsed_ms = (time.perf_counter() - start) * 1000
        return ExecutionResult(rows_returned=len(rows), execution_time_ms=elapsed_ms)

    def close(self) -> None:
        self.conn.close()
