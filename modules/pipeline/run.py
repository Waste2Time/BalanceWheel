from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict

from modules.backtest_engine.simple_engine import BacktestConfig, SimpleBacktestEngine
from modules.data_sources import (
    IDataSource,
    SyntheticSource,
    load_csv,
    save_csv,
    validate_ordering,
)
from modules.data_sources.models import DataSet
from modules.data_sources.validation import OrderingValidation
from modules.experiment_runner import ExperimentConfig, ExperimentRunner
from modules.reporting_ui import ReportBundle, build_report
from modules.strategies import MovingAverageCrossStrategy


@dataclass(frozen=True)
class PipelineConfig:
    symbol: str
    frequency: str
    csv_path: Path
    output_dir: Path
    start: datetime
    end: datetime
    data_source: IDataSource | None = None


def _write_validation_report(validation: OrderingValidation, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "validation.txt"
    lines = [
        "Ordering Validation\n",
        "------------------\n",
        f"symbol: {validation.symbol}\n",
        f"is_sorted: {validation.is_sorted}\n",
        f"has_duplicates: {validation.has_duplicates}\n",
    ]
    report_path.write_text("".join(lines))


def _load_or_fetch_dataset(config: PipelineConfig) -> DataSet:
    if config.csv_path.exists():
        dataset = load_csv(config.csv_path, config.symbol, config.frequency)
    else:
        source = config.data_source or SyntheticSource()
        dataset = source.fetch(config.symbol, config.start, config.end, config.frequency)
        save_csv(config.csv_path, dataset)

    validation = validate_ordering(dataset)
    if not validation.is_sorted or validation.has_duplicates:
        raise ValueError("数据集验证失败：时间戳无序或存在重复。")
    _write_validation_report(validation, config.output_dir)
    return dataset


def run_pipeline(config: PipelineConfig) -> Dict[str, ReportBundle]:
    dataset = _load_or_fetch_dataset(config)
    engine = SimpleBacktestEngine()

    strategies = {
        "baseline": MovingAverageCrossStrategy(short_window=5, long_window=20, position_size=1.0),
        "variant_slow": MovingAverageCrossStrategy(short_window=10, long_window=30, position_size=1.0),
    }

    exp_config = ExperimentConfig(
        name="ma_cross_demo",
        symbol=config.symbol,
        start=config.start,
        end=config.end,
        frequency=config.frequency,
        engine_config=BacktestConfig(),
    )
    runner = ExperimentRunner(engine)
    result = runner.run(exp_config, dataset, strategies)

    reports: Dict[str, ReportBundle] = {}
    for strategy_name, backtest_result in result.results.items():
        reports[strategy_name] = build_report(
            backtest_result, config.output_dir / strategy_name
        )
    return reports


if __name__ == "__main__":
    demo_config = PipelineConfig(
        symbol="SYNTH",
        frequency="1d",
        csv_path=Path("data/synth/SYNTH_1d.csv"),
        output_dir=Path("reports/demo"),
        start=datetime(2020, 1, 1),
        end=datetime(2020, 6, 30),
    )
    run_pipeline(demo_config)
