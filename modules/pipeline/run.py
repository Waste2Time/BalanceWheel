from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from modules.backtest_engine.simple_engine import BacktestConfig, SimpleBacktestEngine
from modules.data_sources.csv_cache import load_csv
from modules.experiment_runner import ExperimentConfig, ExperimentRunner
from modules.reporting_ui import build_report
from modules.strategies import MovingAverageCrossStrategy


@dataclass(frozen=True)
class PipelineConfig:
    symbol: str
    frequency: str
    csv_path: Path
    output_dir: Path
    start: datetime
    end: datetime


def run_pipeline(config: PipelineConfig) -> None:
    dataset = load_csv(config.csv_path, config.symbol, config.frequency)
    engine = SimpleBacktestEngine()
    strategy = MovingAverageCrossStrategy()
    exp_config = ExperimentConfig(
        name="baseline",
        symbol=config.symbol,
        start=config.start,
        end=config.end,
        frequency=config.frequency,
        engine_config=BacktestConfig(),
    )
    runner = ExperimentRunner(engine)
    result = runner.run(exp_config, dataset, {"baseline": strategy})
    baseline_result = result.results["baseline"]
    build_report(baseline_result, config.output_dir)
