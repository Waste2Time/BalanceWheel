from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from modules.backtest_engine.result import BacktestResult

from .charts import ChartPaths, render_equity_curve


@dataclass(frozen=True)
class ReportBundle:
    charts: ChartPaths
    metrics_path: Path


def build_report(result: BacktestResult, output_dir: Path) -> ReportBundle:
    charts = render_equity_curve(result, output_dir)
    metrics_path = output_dir / "metrics.txt"
    metrics_lines = ["Performance Metrics\n", "-------------------\n"]
    for key, value in sorted(result.performance_metrics.items()):
        metrics_lines.append(f"{key}: {value:.4f}\n")
    metrics_path.write_text("".join(metrics_lines))
    return ReportBundle(charts=charts, metrics_path=metrics_path)
