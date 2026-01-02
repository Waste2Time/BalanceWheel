from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from modules.backtest_engine.result import BacktestResult
from modules.experiment_runner import ExperimentResult, ExperimentSummary, ExperimentRunner

from .charts import ChartPaths, render_equity_curve, render_overlay_curves


@dataclass
class ReportBundle:
    charts: ChartPaths
    metrics_path: Path
    overlay_path: Path | None = None
    summary_paths: dict[str, Path] | None = None


def _write_metrics(result: BacktestResult, output_dir: Path) -> Path:
    metrics_path = output_dir / "metrics.txt"
    metrics_lines = ["Performance Metrics\n", "-------------------\n"]
    for key, value in sorted(result.performance_metrics.items()):
        metrics_lines.append(f"{key}: {value:.4f}\n")
    metrics_path.write_text("".join(metrics_lines))
    return metrics_path


def _write_significance(summary: ExperimentSummary | None, output_dir: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    if not summary:
        return paths
    if summary.metrics_table:
        metrics_path = output_dir / "metrics_table.csv"
        headers = list(summary.metrics_table[0].keys())
        lines = [",".join(headers) + "\n"]
        for row in summary.metrics_table:
            lines.append(",".join(str(row.get(h, "")) for h in headers) + "\n")
        metrics_path.write_text("".join(lines))
        paths["metrics_table"] = metrics_path
    if summary.significance:
        sig_path = output_dir / "significance.csv"
        lines = ["baseline,variant,t_stat,p_value,baseline_mean,variant_mean\n"]
        for item in summary.significance:
            lines.append(
                f"{item.baseline},{item.variant},{item.t_stat},{item.p_value},{item.baseline_mean},{item.variant_mean}\n"
            )
        sig_path.write_text("".join(lines))
        paths["significance"] = sig_path
    return paths


def build_report(result: BacktestResult, output_dir: Path) -> ReportBundle:
    charts = render_equity_curve(result, output_dir)
    metrics_path = _write_metrics(result, output_dir)
    return ReportBundle(charts=charts, metrics_path=metrics_path)


def build_experiment_reports(exp_result: ExperimentResult, output_dir: Path) -> dict[str, ReportBundle]:
    bundles: Dict[str, ReportBundle] = {}
    output_dir.mkdir(parents=True, exist_ok=True)
    for strategy_name, backtest_result in exp_result.results.items():
        bundles[strategy_name] = build_report(backtest_result, output_dir / strategy_name)
    overlay = render_overlay_curves(exp_result.results, output_dir)
    summary_paths = _write_significance(exp_result.summary, output_dir)
    for bundle in bundles.values():
        bundle.overlay_path = overlay
        bundle.summary_paths = summary_paths or None
    return bundles
