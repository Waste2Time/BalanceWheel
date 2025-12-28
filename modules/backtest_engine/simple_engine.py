from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from modules.data_sources.models import Bar, DataSet
from modules.portfolio_risk import PositionSizer, RiskLimits, check_drawdown

from .base import IBacktestEngine
from .result import BacktestResult, EquityPoint, Trade


@dataclass(frozen=True)
class BacktestConfig:
    initial_capital: float = 1_000_000.0
    commission_rate: float = 0.0
    position_sizer: PositionSizer | None = None
    risk_limits: RiskLimits | None = None


class SimpleBacktestEngine(IBacktestEngine):
    """轻量回测引擎（单标的），用于早期验证与单元测试。"""

    def run(self, strategy, data: DataSet, config: BacktestConfig) -> BacktestResult:
        cash = config.initial_capital
        position = 0.0
        trades: list[Trade] = []
        equity_curve: list[EquityPoint] = []
        history: list[Bar] = []
        position_sizer = config.position_sizer or PositionSizer()
        risk_limits = config.risk_limits

        for bar in data.bars:
            history.append(bar)
            target_position = position_sizer.size(strategy.on_bar(bar, history))
            if target_position != position:
                trade_size = target_position - position
                trade_cost = trade_size * bar.close
                commission = abs(trade_cost) * config.commission_rate
                cash -= trade_cost + commission
                position = target_position
                trades.append(Trade(datetime=bar.datetime, price=bar.close, size=trade_size))
            equity = cash + position * bar.close
            equity_curve.append(EquityPoint(datetime=bar.datetime, equity=equity))
            if risk_limits is not None:
                drawdown = _latest_drawdown(equity_curve)
                if not check_drawdown(drawdown, risk_limits):
                    flatten_size = -position
                    trade_cost = flatten_size * bar.close
                    commission = abs(trade_cost) * config.commission_rate
                    cash -= trade_cost + commission
                    position = 0.0
                    equity_curve[-1] = EquityPoint(datetime=bar.datetime, equity=cash)
                    trades.append(Trade(datetime=bar.datetime, price=bar.close, size=flatten_size))
                    break

        performance = _calculate_performance(equity_curve)
        return BacktestResult(
            equity_curve=tuple(equity_curve),
            trades=tuple(trades),
            performance_metrics=performance,
        )


def _calculate_performance(equity_curve: Iterable[EquityPoint]) -> dict[str, float]:
    points = list(equity_curve)
    if not points:
        return {
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "annualized_return": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
        }
    start = points[0].equity
    end = points[-1].equity
    total_return = (end - start) / start if start else 0.0
    max_drawdown = max((_drawdown_at(points, i) for i in range(len(points))), default=0.0)
    returns = _period_returns(points)
    volatility = _stdev(returns) * (len(points) ** 0.5) if returns else 0.0
    annualized_return = ((1 + total_return) ** (252 / len(points)) - 1) if len(points) else 0.0
    sharpe = (annualized_return / volatility) if volatility else 0.0
    return {
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "annualized_return": annualized_return,
        "volatility": volatility,
        "sharpe": sharpe,
    }


def _drawdown_at(points: list[EquityPoint], index: int) -> float:
    current = points[index].equity
    peak = max(point.equity for point in points[: index + 1])
    return (peak - current) / peak if peak else 0.0


def _period_returns(points: list[EquityPoint]) -> list[float]:
    returns: list[float] = []
    for prev, curr in zip(points, points[1:]):
        returns.append((curr.equity - prev.equity) / prev.equity if prev.equity else 0.0)
    return returns


def _stdev(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((val - mean) ** 2 for val in values) / len(values)
    return variance ** 0.5


def _latest_drawdown(equity_curve: list[EquityPoint]) -> float:
    if not equity_curve:
        return 0.0
    return _drawdown_at(equity_curve, len(equity_curve) - 1)
