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
    metrics_path = _write_metrics_table(result, output_dir)
    return ReportBundle(charts=charts, metrics_path=metrics_path)


def _write_metrics_table(result: BacktestResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "metrics.txt"
    lines = ["Performance Metrics"]
    for key, value in sorted(result.performance_metrics.items()):
        lines.append(f"{key}: {value:.4f}")
    path.write_text("\n".join(lines))
    return path
