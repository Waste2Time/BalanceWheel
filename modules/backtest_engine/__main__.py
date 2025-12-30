"""Entry point helpers for running lightweight backtests."""

import argparse
from datetime import datetime

from modules.data_sources.synthetic import SyntheticSource
from modules.strategies import MovingAverageCrossStrategy

from .simple_engine import BacktestConfig, SimpleBacktestEngine


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest engine helper")
    parser.add_argument("--demo", action="store_true", help="运行简单示例回测")
    parser.add_argument("--capital", type=float, default=1_000_000.0, help="初始资金")
    parser.add_argument("--commission", type=float, default=0.0, help="手续费率")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if not args.demo:
        print("可用引擎：simple（内置）、vnpy（需额外安装）。运行 --demo 体验内置回测。")
        return

    source = SyntheticSource()
    dataset = source.fetch(
        symbol="SYNTH",
        start=datetime(2020, 1, 1),
        end=datetime(2020, 6, 30),
        frequency="1d",
    )
    strategy = MovingAverageCrossStrategy(short_window=5, long_window=20, position_size=1.0)
    engine = SimpleBacktestEngine()
    result = engine.run(strategy, dataset, BacktestConfig(args.capital, args.commission))

    print("示例回测完成：")
    print(f"总权益点数: {len(result.equity_curve)}")
    for key, value in result.performance_metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
