"""Experiment runner CLI helper."""

import argparse
from datetime import datetime

from modules.backtest_engine import BacktestConfig, SimpleBacktestEngine
from modules.data_sources.synthetic import SyntheticSource
from modules.strategies import MovingAverageCrossStrategy

from .config import ExperimentConfig
from .runner import ExperimentRunner


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Experiment runner helper")
    parser.add_argument("--demo", action="store_true", help="运行基线/变体对比示例")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if not args.demo:
        print("使用 --demo 运行内置示例，或参考 README 集成自定义实验。")
        return

    dataset = SyntheticSource().fetch(
        symbol="SYNTH",
        start=datetime(2020, 1, 1),
        end=datetime(2020, 6, 30),
        frequency="1d",
    )
    engine = SimpleBacktestEngine()
    engine_config = BacktestConfig(initial_capital=1_000_000.0, commission_rate=0.0)
    strategies = {
        "baseline": MovingAverageCrossStrategy(short_window=5, long_window=20, position_size=1.0),
        "variant": MovingAverageCrossStrategy(short_window=10, long_window=30, position_size=1.0),
    }
    exp_config = ExperimentConfig(
        name="demo",
        symbol=dataset.symbol,
        start=dataset.start() or datetime(2020, 1, 1),
        end=dataset.end() or datetime(2020, 6, 30),
        frequency=dataset.frequency,
        engine_config=engine_config,
    )
    runner = ExperimentRunner(engine)
    result = runner.run(exp_config, dataset, strategies)
    print("实验完成，策略指标：")
    for strategy_name, backtest_result in result.results.items():
        print(f"- {strategy_name}: {backtest_result.performance_metrics}")


if __name__ == "__main__":
    main()
