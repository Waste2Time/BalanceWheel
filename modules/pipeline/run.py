from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
from typing import Callable

from modules.backtest_engine.simple_engine import BacktestConfig, SimpleBacktestEngine
from modules.data_sources import (
    AkshareSource,
    BaostockSource,
    CacheMetadata,
    load_csv,
    random_walk_fetcher,
    save_csv,
    validate_pair,
)
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
    primary_fetcher: Callable | None = None
    secondary_fetcher: Callable | None = None
    use_synthetic_on_missing: bool = True
    commission_rate: float = 0.0
    initial_capital: float = 1_000_000.0


def run_pipeline(config: PipelineConfig) -> None:
    dataset = _load_or_fetch_dataset(config)
    engine = SimpleBacktestEngine()
    baseline = MovingAverageCrossStrategy()
    variant = MovingAverageCrossStrategy(short_window=10, long_window=30, position_size=2.0)
    exp_config = ExperimentConfig(
        name="baseline",
        symbol=config.symbol,
        start=config.start,
        end=config.end,
        frequency=config.frequency,
        engine_config=BacktestConfig(
            initial_capital=config.initial_capital,
            commission_rate=config.commission_rate,
        ),
        output_dir=config.output_dir,
    )
    runner = ExperimentRunner(engine)
    result = runner.run(exp_config, dataset, {"baseline": baseline, "variant": variant})
    for name, backtest_result in result.results.items():
        build_report(backtest_result, config.output_dir / name)


def _load_or_fetch_dataset(config: PipelineConfig):
    if config.csv_path.exists():
        return load_csv(config.csv_path, config.symbol, config.frequency)

    fetcher = config.primary_fetcher
    if fetcher is None and config.use_synthetic_on_missing:
        fetcher = random_walk_fetcher()
    if fetcher is None:
        raise FileNotFoundError(f"CSV not found and no fetcher provided: {config.csv_path}")

    primary = BaostockSource(fetcher)
    dataset = primary.fetch(config.symbol, config.start, config.end, config.frequency)

    validation_report = None
    if config.secondary_fetcher:
        secondary = AkshareSource(config.secondary_fetcher)
        secondary_dataset = secondary.fetch(config.symbol, config.start, config.end, config.frequency)
        validation_report = validate_pair(dataset, secondary_dataset)
        _write_validation(config.csv_path.parent / "validation.json", validation_report)

    metadata = CacheMetadata(
        source="baostock",
        symbol=config.symbol,
        frequency=config.frequency,
        start=config.start.isoformat(),
        end=config.end.isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )
    save_csv(config.csv_path, dataset, metadata=metadata)
    return dataset


def _write_validation(path: Path, report) -> None:
    if report is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
