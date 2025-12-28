from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from modules.backtest_engine.result import BacktestResult

from .charts import ChartPaths, render_equity_curve


@dataclass(frozen=True)
class ReportBundle:
    charts: ChartPaths


def build_report(result: BacktestResult, output_dir: Path) -> ReportBundle:
    charts = render_equity_curve(result, output_dir)
    return ReportBundle(charts=charts)
