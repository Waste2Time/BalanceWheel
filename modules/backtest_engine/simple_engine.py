from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from modules.data_sources.models import Bar, DataSet

from .base import IBacktestEngine
from .result import BacktestResult, EquityPoint, Trade


@dataclass(frozen=True)
class BacktestConfig:
    initial_capital: float = 1_000_000.0
    commission_rate: float = 0.0


class SimpleBacktestEngine(IBacktestEngine):
    """轻量回测引擎（单标的），用于早期验证与单元测试。"""

    def run(self, strategy, data: DataSet, config: BacktestConfig) -> BacktestResult:
        cash = config.initial_capital
        position = 0.0
        trades: list[Trade] = []
        equity_curve: list[EquityPoint] = []
        history: list[Bar] = []

        for bar in data.bars:
            history.append(bar)
            target_position = strategy.on_bar(bar, history)
            if target_position != position:
                trade_size = target_position - position
                trade_cost = trade_size * bar.close
                commission = abs(trade_cost) * config.commission_rate
                cash -= trade_cost + commission
                position = target_position
                trades.append(Trade(datetime=bar.datetime, price=bar.close, size=trade_size))
            equity = cash + position * bar.close
            equity_curve.append(EquityPoint(datetime=bar.datetime, equity=equity))

        performance = _calculate_performance(equity_curve)
        return BacktestResult(
            equity_curve=tuple(equity_curve),
            trades=tuple(trades),
            performance_metrics=performance,
        )


def _calculate_performance(equity_curve: Iterable[EquityPoint]) -> dict[str, float]:
    points = list(equity_curve)
    if not points:
        return {"total_return": 0.0, "max_drawdown": 0.0}
    start = points[0].equity
    end = points[-1].equity
    total_return = (end - start) / start if start else 0.0
    peak = points[0].equity
    max_drawdown = 0.0
    for point in points:
        peak = max(peak, point.equity)
        drawdown = (peak - point.equity) / peak if peak else 0.0
        max_drawdown = max(max_drawdown, drawdown)
    return {"total_return": total_return, "max_drawdown": max_drawdown}
