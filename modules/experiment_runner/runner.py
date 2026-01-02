from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from modules.backtest_engine.base import IBacktestEngine
from modules.backtest_engine.result import BacktestResult

from .analysis import SignificanceResult, aggregate_metrics, compute_significance
from .config import ExperimentConfig


@dataclass(frozen=True)
class ExperimentSummary:
    metrics_table: list[dict[str, float | str]]
    significance: list[SignificanceResult]
    metrics_path: Path | None = None
    significance_path: Path | None = None


@dataclass(frozen=True)
class ExperimentResult:
    name: str
    results: dict[str, BacktestResult]
    summary: ExperimentSummary | None = None


class ExperimentRunner:
    def __init__(self, engine: IBacktestEngine) -> None:
        self._engine = engine

    def run(self, config: ExperimentConfig, dataset, strategies: dict[str, object]) -> ExperimentResult:
        results: dict[str, BacktestResult] = {}
        for name, strategy in strategies.items():
            results[name] = self._engine.run(strategy, dataset, config.engine_config)

        metrics_table = aggregate_metrics(results)
        significance = compute_significance(results)
        summary = ExperimentSummary(metrics_table=metrics_table, significance=significance)
        return ExperimentResult(name=config.name, results=results, summary=summary)

    def save_summary(self, summary: ExperimentSummary, output_dir: Path) -> ExperimentSummary:
        output_dir.mkdir(parents=True, exist_ok=True)
        metrics_path = output_dir / "metrics.csv"
        if summary.metrics_table:
            headers = list(summary.metrics_table[0].keys())
            lines = [",".join(headers) + "\n"]
            for row in summary.metrics_table:
                lines.append(",".join(str(row.get(h, "")) for h in headers) + "\n")
            metrics_path.write_text("".join(lines))
        sig_path = output_dir / "significance.csv"
        if summary.significance:
            lines = ["baseline,variant,t_stat,p_value,baseline_mean,variant_mean\n"]
            for item in summary.significance:
                lines.append(
                    f"{item.baseline},{item.variant},{item.t_stat},{item.p_value},{item.baseline_mean},{item.variant_mean}\n"
                )
            sig_path.write_text("".join(lines))
        return ExperimentSummary(
            metrics_table=summary.metrics_table,
            significance=summary.significance,
            metrics_path=metrics_path if summary.metrics_table else None,
            significance_path=sig_path if summary.significance else None,
        )
