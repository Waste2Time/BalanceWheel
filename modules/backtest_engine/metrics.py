from __future__ import annotations

import math
from typing import Iterable, Sequence

from .result import EquityPoint, ReturnPoint

TRADING_DAYS = 252


def _extract_returns(equity_curve: Sequence[EquityPoint]) -> list[ReturnPoint]:
    returns: list[ReturnPoint] = []
    for prev, curr in zip(equity_curve, equity_curve[1:]):
        ret = 0.0
        if prev.equity:
            ret = (curr.equity - prev.equity) / prev.equity
        returns.append(ReturnPoint(datetime=curr.datetime, return_pct=ret))
    return returns


def _annualize_return(total_return: float, periods: int) -> float:
    if periods <= 0:
        return 0.0
    return (1 + total_return) ** (TRADING_DAYS / periods) - 1


def _volatility(returns: Iterable[float]) -> float:
    values = list(returns)
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((r - mean) ** 2 for r in values) / (len(values) - 1)
    return math.sqrt(variance) * math.sqrt(TRADING_DAYS)


def _downside_volatility(returns: Iterable[float]) -> float:
    negatives = [r for r in returns if r < 0]
    if len(negatives) < 1:
        return 0.0
    mean = sum(negatives) / len(negatives)
    variance = sum((r - mean) ** 2 for r in negatives) / len(negatives)
    return math.sqrt(variance) * math.sqrt(TRADING_DAYS)


def compute_performance(equity_curve: Sequence[EquityPoint]) -> tuple[dict[str, float], tuple[ReturnPoint, ...]]:
    points = list(equity_curve)
    if not points:
        return {
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "annualized_return": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "win_rate": 0.0,
        }, tuple()

    returns = _extract_returns(points)
    return_values = [r.return_pct for r in returns]

    start = points[0].equity
    end = points[-1].equity
    total_return = (end - start) / start if start else 0.0

    peak = points[0].equity
    max_drawdown = 0.0
    for point in points:
        peak = max(peak, point.equity)
        drawdown = (peak - point.equity) / peak if peak else 0.0
        max_drawdown = max(max_drawdown, drawdown)

    annualized = _annualize_return(total_return, len(points))
    vol = _volatility(return_values)
    downside = _downside_volatility(return_values)
    sharpe = annualized / vol if vol else 0.0
    sortino = annualized / downside if downside else 0.0
    calmar = annualized / max_drawdown if max_drawdown else 0.0
    win_rate = sum(1 for r in return_values if r > 0) / len(return_values) if return_values else 0.0

    metrics = {
        "total_return": total_return,
        "annualized_return": annualized,
        "max_drawdown": max_drawdown,
        "volatility": vol,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "calmar_ratio": calmar,
        "win_rate": win_rate,
    }

    return metrics, tuple(returns)
