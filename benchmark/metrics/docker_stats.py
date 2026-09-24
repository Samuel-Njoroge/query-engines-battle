"""Background `docker stats` polling for CPU/memory during a single query's
measured execution window.

Uses the `docker` CLI via subprocess rather than the Docker SDK, so the
runner's only dependency is having `docker` on PATH - the same thing running
docker-compose already requires.
"""

from __future__ import annotations

import re
import subprocess
import threading

MEM_UNIT_MULTIPLIERS = {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3, "TiB": 1024**4}
POLL_INTERVAL_SECONDS = 0.25


def _parse_mem_mb(mem_usage: str) -> float:
    """`docker stats` MemUsage looks like '512MiB / 4GiB' - take the used side."""
    used = mem_usage.split("/")[0].strip()
    match = re.match(r"([0-9.]+)\s*([A-Za-z]+)", used)
    if not match:
        return 0.0
    value, unit = match.groups()
    return float(value) * MEM_UNIT_MULTIPLIERS.get(unit, 1) / (1024**2)


def _parse_cpu_percent(cpu_perc: str) -> float:
    cpu_perc = cpu_perc.strip().rstrip("%")
    return float(cpu_perc) if cpu_perc else 0.0


def _sample(containers: list[str]) -> tuple[float, float] | None:
    if not containers:
        return None
    try:
        proc = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{.CPUPerc}}\t{{.MemUsage}}", *containers],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None

    total_cpu = 0.0
    total_mem_mb = 0.0
    for line in proc.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        cpu_str, mem_str = parts
        total_cpu += _parse_cpu_percent(cpu_str)
        total_mem_mb += _parse_mem_mb(mem_str)
    return total_cpu, total_mem_mb


class ResourceMonitor:
    """Polls the given containers on a background thread while a query runs.

    Multi-container engines (Doris FE+BE, Druid broker+historical, ...) get
    their per-sample CPU%/memory summed across containers, so the summary
    reflects the engine's total footprint for that query rather than one
    arbitrary component.
    """

    def __init__(self, containers: list[str]):
        self.containers = containers
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._samples: list[tuple[float, float]] = []

    def __enter__(self) -> "ResourceMonitor":
        self._samples = []
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc_info) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def _run(self) -> None:
        while not self._stop.is_set():
            sample = _sample(self.containers)
            if sample is not None:
                self._samples.append(sample)
            self._stop.wait(POLL_INTERVAL_SECONDS)

    def summary(self) -> dict:
        if not self._samples:
            return {"cpu_percent_avg": None, "peak_memory_mb": None, "avg_memory_mb": None}
        cpu_values = [s[0] for s in self._samples]
        mem_values = [s[1] for s in self._samples]
        return {
            "cpu_percent_avg": sum(cpu_values) / len(cpu_values),
            "peak_memory_mb": max(mem_values),
            "avg_memory_mb": sum(mem_values) / len(mem_values),
        }
