from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict

from modules.backtest_engine import (
    BacktestConfig,
    SimpleBacktestEngine,
    VnpyBacktestConfig,
    VnpyBacktestEngine,
)
from modules.data_sources import (
    AkshareSource,
    BaostockSource,
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
    data_source_name: str = "synthetic"
    engine: str = "simple"
    initial_capital: float = 1_000_000.0
    commission_rate: float = 0.0


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


def _resolve_data_source(config: PipelineConfig) -> IDataSource:
    if config.data_source:
        return config.data_source

    name = config.data_source_name.lower()
    if name == "baostock":
        return BaostockSource()
    if name == "akshare":
        return AkshareSource()
    return SyntheticSource()


def _load_or_fetch_dataset(config: PipelineConfig) -> DataSet:
    if config.csv_path.exists():
        dataset = load_csv(config.csv_path, config.symbol, config.frequency)
    else:
        source = _resolve_data_source(config)
        dataset = source.fetch(config.symbol, config.start, config.end, config.frequency)
        save_csv(config.csv_path, dataset)

    validation = validate_ordering(dataset)
    if not validation.is_sorted or validation.has_duplicates:
        raise ValueError("数据集验证失败：时间戳无序或存在重复。")
    _write_validation_report(validation, config.output_dir)
    return dataset


def run_pipeline(config: PipelineConfig) -> Dict[str, ReportBundle]:
    dataset = _load_or_fetch_dataset(config)
    if config.engine == "vnpy":
        engine = VnpyBacktestEngine()
        engine_config = VnpyBacktestConfig(
            vt_symbol=config.symbol,
            capital=config.initial_capital,
            rate=config.commission_rate,
        )
    else:
        engine = SimpleBacktestEngine()
        engine_config = BacktestConfig(
            initial_capital=config.initial_capital,
            commission_rate=config.commission_rate,
        )

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
        engine_config=engine_config,
    )
    runner = ExperimentRunner(engine)
    result = runner.run(exp_config, dataset, strategies)

    reports: Dict[str, ReportBundle] = {}
    for strategy_name, backtest_result in result.results.items():
        reports[strategy_name] = build_report(
            backtest_result, config.output_dir / strategy_name
        )
    return reports


def _parse_args() -> PipelineConfig:
    parser = argparse.ArgumentParser(description="Run BalanceWheel MVP pipeline")
    parser.add_argument("--symbol", required=False, default="SYNTH", help="标的代码，例如 sh.600000 或 000001")
    parser.add_argument("--frequency", default="1d", help="频率，默认 1d")
    parser.add_argument("--start", default="2020-01-01", help="起始日期，格式 YYYY-MM-DD")
    parser.add_argument("--end", default="2020-06-30", help="结束日期，格式 YYYY-MM-DD")
    parser.add_argument("--data-source", dest="data_source", default="synthetic", help="数据源：synthetic/baostock/akshare")
    parser.add_argument("--engine", default="simple", help="回测引擎：simple/vnpy")
    parser.add_argument("--csv-path", default="data/synth/SYNTH_1d.csv", help="CSV 缓存路径")
    parser.add_argument("--output-dir", default="reports/demo", help="输出目录")
    parser.add_argument("--capital", type=float, default=1_000_000.0, help="初始资金")
    parser.add_argument("--commission", type=float, default=0.0, help="手续费率，例如 0.0005")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    return PipelineConfig(
        symbol=args.symbol,
        frequency=args.frequency,
        csv_path=Path(args.csv_path),
        output_dir=Path(args.output_dir),
        start=start,
        end=end,
        data_source_name=args.data_source,
        engine=args.engine,
        initial_capital=args.capital,
        commission_rate=args.commission,
    )


if __name__ == "__main__":
    run_pipeline(_parse_args())
