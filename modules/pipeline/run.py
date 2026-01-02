from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict

from modules.backtest_engine import (
    BacktestConfig,
    RotationBacktestEngine,
    RotationConfig,
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
from modules.reporting_ui import build_experiment_reports
from modules.strategies import (
    AfternoonEtfRotationStrategy,
    AfternoonEtfRule,
    MovingAverageCrossStrategy,
)


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
    preset: str = "ma_demo"
    strategy_config_path: Path | None = None
    chinext_symbol: str = "159915"
    nasdaq_symbol: str = "159941"
    index_symbol: str = "000001"


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


def _target_csv(base_path: Path, symbol: str, frequency: str) -> Path:
    if base_path.suffix:
        return base_path
    return base_path / f"{symbol}_{frequency}.csv"


def _load_or_fetch_dataset(config: PipelineConfig, symbol: str | None = None) -> DataSet:
    target_symbol = symbol or config.symbol
    csv_path = _target_csv(config.csv_path, target_symbol, config.frequency)
    if csv_path.exists():
        dataset = load_csv(csv_path, target_symbol, config.frequency)
    else:
        source = _resolve_data_source(config)
        dataset = source.fetch(target_symbol, config.start, config.end, config.frequency)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        save_csv(csv_path, dataset)

    validation = validate_ordering(dataset)
    if not validation.is_sorted or validation.has_duplicates:
        raise ValueError("数据集验证失败：时间戳无序或存在重复。")
    _write_validation_report(validation, config.output_dir)
    return dataset


def _load_strategies_from_file(path: Path) -> dict[str, object]:
    content = path.read_text()
    data = json.loads(content) if path.suffix.lower() == ".json" else None
    if data is None:
        try:
            import yaml

            data = yaml.safe_load(content)
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(f"无法解析策略配置文件 {path}: {exc}")
    strategies: dict[str, object] = {}
    for name, cfg in data.items():
        kind = cfg.get("type", "ma_cross")
        if kind == "ma_cross":
            strategies[name] = MovingAverageCrossStrategy(
                short_window=int(cfg.get("short_window", 5)),
                long_window=int(cfg.get("long_window", 20)),
                position_size=float(cfg.get("position_size", 1.0)),
            )
    return strategies or {
        "baseline": MovingAverageCrossStrategy(short_window=5, long_window=20, position_size=1.0)
    }


def _build_strategies(config: PipelineConfig) -> dict[str, object]:
    if config.strategy_config_path and config.strategy_config_path.exists():
        return _load_strategies_from_file(config.strategy_config_path)
    return {
        "baseline": MovingAverageCrossStrategy(short_window=5, long_window=20, position_size=1.0),
        "variant_slow": MovingAverageCrossStrategy(short_window=10, long_window=30, position_size=1.0),
    }


def _run_ma_pipeline(config: PipelineConfig) -> Dict[str, Path]:
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

    strategies = _build_strategies(config)

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
    summary = runner.save_summary(result.summary, config.output_dir)
    result = result.__class__(name=result.name, results=result.results, summary=summary)
    reports = build_experiment_reports(result, config.output_dir)
    return {name: bundle.metrics_path for name, bundle in reports.items()}


def _run_afternoon_rotation(config: PipelineConfig) -> Dict[str, Path]:
    symbols = [config.chinext_symbol, config.nasdaq_symbol]
    datasets = {symbol: _load_or_fetch_dataset(config, symbol) for symbol in symbols}
    engine = RotationBacktestEngine()
    engine_config = RotationConfig(
        initial_capital=config.initial_capital,
        commission_rate=config.commission_rate,
    )
    rule = AfternoonEtfRule(
        chinext_symbol=config.chinext_symbol,
        nasdaq_symbol=config.nasdaq_symbol,
        index_symbol=config.index_symbol,
    )
    strategies = {"afternoon_etf": AfternoonEtfRotationStrategy(rule)}
    exp_config = ExperimentConfig(
        name="afternoon_etf",
        symbol=",".join(symbols),
        start=config.start,
        end=config.end,
        frequency=config.frequency,
        engine_config=engine_config,
    )
    runner = ExperimentRunner(engine)
    result = runner.run(exp_config, datasets, strategies)
    summary = runner.save_summary(result.summary, config.output_dir)
    result = result.__class__(name=result.name, results=result.results, summary=summary)
    reports = build_experiment_reports(result, config.output_dir)
    return {name: bundle.metrics_path for name, bundle in reports.items()}


def run_pipeline(config: PipelineConfig) -> Dict[str, Path]:
    if config.preset == "afternoon_etf":
        return _run_afternoon_rotation(config)
    return _run_ma_pipeline(config)


def _parse_args() -> PipelineConfig:
    parser = argparse.ArgumentParser(description="Run BalanceWheel MVP pipeline")
    parser.add_argument("--symbol", required=False, default="SYNTH", help="标的代码，例如 sh.600000 或 000001")
    parser.add_argument("--frequency", default="1d", help="频率，默认 1d")
    parser.add_argument("--start", default="2020-01-01", help="起始日期，格式 YYYY-MM-DD")
    parser.add_argument("--end", default="2020-06-30", help="结束日期，格式 YYYY-MM-DD")
    parser.add_argument("--data-source", dest="data_source", default="synthetic", help="数据源：synthetic/baostock/akshare")
    parser.add_argument("--engine", default="simple", help="回测引擎：simple/vnpy")
    parser.add_argument("--csv-path", default="data/synth", help="CSV 缓存路径或目录")
    parser.add_argument("--output-dir", default="reports/demo", help="输出目录")
    parser.add_argument("--capital", type=float, default=1_000_000.0, help="初始资金")
    parser.add_argument("--commission", type=float, default=0.0, help="手续费率，例如 0.0005")
    parser.add_argument("--preset", default="ma_demo", choices=["ma_demo", "afternoon_etf"], help="预设策略集")
    parser.add_argument("--strategy-config", dest="strategy_config", help="JSON/YAML 策略配置文件")
    parser.add_argument("--chinext-symbol", default="159915", help="创业板ETF 代码")
    parser.add_argument("--nasdaq-symbol", default="159941", help="纳指ETF 代码")
    parser.add_argument("--index-symbol", default="000001", help="上证指数代码（参考用）")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    strategy_path = Path(args.strategy_config) if args.strategy_config else None

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
        preset=args.preset,
        strategy_config_path=strategy_path,
        chinext_symbol=args.chinext_symbol,
        nasdaq_symbol=args.nasdaq_symbol,
        index_symbol=args.index_symbol,
    )


if __name__ == "__main__":
    run_pipeline(_parse_args())
