#!/usr/bin/env python3
"""Renders a Markdown comparison report (with bar charts) from results/*.jsonl.

Usage:
    python -m benchmark.reports.generate_report --dataset-size tiny
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tabulate import tabulate

from benchmark.reports.aggregate import aggregate, load_records

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def _bar_chart(rows: list[dict], metric: str, ylabel: str, title: str, out_path: Path) -> None:
    by_query: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        by_query[row["query"]][row["engine"]] = row[metric]

    queries = sorted(by_query)
    engines = sorted({e for v in by_query.values() for e in v})
    width = 0.8 / max(len(engines), 1)

    fig, ax = plt.subplots(figsize=(max(6, len(queries) * 1.2), 5))
    for i, engine in enumerate(engines):
        values = [by_query[q].get(engine) for q in queries]
        positions = [j + i * width for j in range(len(queries))]
        ax.bar(positions, [v if v is not None else 0 for v in values], width=width, label=engine)

    ax.set_xticks([j + width * (len(engines) - 1) / 2 for j in range(len(queries))])
    ax.set_xticklabels(queries, rotation=30, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def render_markdown(rows: list[dict], dataset_size: str) -> str:
    lines = [f"# Query Engines Battle - Report ({dataset_size})", ""]

    by_category: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_category[row["query_category"]].append(row)

    for category in sorted(by_category):
        lines.append(f"## {category}")
        lines.append("")
        table_rows = [
            [r["engine"], r["query"], r["runs"], f"{r['mean_ms']:.1f}", f"{r['median_ms']:.1f}", f"{r['p95_ms']:.1f}", f"{r['stdev_ms']:.1f}"]
            for r in sorted(by_category[category], key=lambda r: (r["query"], r["engine"]))
        ]
        lines.append(
            tabulate(
                table_rows,
                headers=["engine", "query", "runs", "mean (ms)", "median (ms)", "p95 (ms)", "stdev (ms)"],
                tablefmt="github",
            )
        )
        lines.append("")

    lines.append("## Charts")
    lines.append("")
    lines.append("![Execution time by engine](execution_time_ms.png)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-size", required=True)
    args = parser.parse_args()

    records = [r for r in load_records() if r["dataset_size"] == args.dataset_size]
    if not records:
        print(f"No results found for dataset_size='{args.dataset_size}'")
        return

    rows = aggregate(records)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    _bar_chart(
        rows,
        metric="mean_ms",
        ylabel="Mean execution time (ms)",
        title=f"Execution time by engine ({args.dataset_size})",
        out_path=OUTPUT_DIR / "execution_time_ms.png",
    )

    report_md = render_markdown(rows, args.dataset_size)
    report_path = OUTPUT_DIR / f"report_{args.dataset_size}.md"
    report_path.write_text(report_md)
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
