from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable

from modules.data_sources.models import DataSet

from .metrics import compute_performance
from .result import BacktestResult, EquityPoint, Trade


@dataclass(frozen=True)
class RotationConfig:
    initial_capital: float = 1_000_000.0
    commission_rate: float = 0.0


class MultiAssetRotationStrategy:
    def select_target(self, current_date: datetime, price_history: dict[str, list[float]]) -> str | None:
        raise NotImplementedError


class RotationBacktestEngine:
    """基于多标的的轮动回测引擎，允许策略在每个交易日切换持仓。"""

    def __init__(self) -> None:
        self._price_history: dict[str, list[float]] = {}

    def _align_dates(self, datasets: Dict[str, DataSet]) -> list[datetime]:
        date_sets = [set(bar.datetime for bar in ds.bars) for ds in datasets.values() if ds.bars]
        if not date_sets:
            return []
        return sorted(set.intersection(*date_sets))

    def run(
        self,
        strategy: MultiAssetRotationStrategy,
        datasets: Dict[str, DataSet],
        config: RotationConfig,
    ) -> BacktestResult:
        dates = self._align_dates(datasets)
        if not dates:
            return BacktestResult(tuple(), tuple(), {"total_return": 0.0}, tuple())

        price_lookup = {symbol: {bar.datetime: bar for bar in ds.bars} for symbol, ds in datasets.items()}
        for symbol in datasets:
            self._price_history[symbol] = []

        cash = config.initial_capital
        current_symbol: str | None = None
        equity_curve: list[EquityPoint] = []
        trades: list[Trade] = []

        prev_price: float | None = None
        for date in dates:
            closes = {symbol: price_lookup[symbol][date].close for symbol in datasets}
            for symbol, price in closes.items():
                self._price_history[symbol].append(price)

            if current_symbol and prev_price is not None:
                today_price = closes[current_symbol]
                ret = (today_price - prev_price) / prev_price if prev_price else 0.0
                cash *= 1 + ret
                prev_price = today_price
            equity_curve.append(EquityPoint(datetime=date, equity=cash))

            next_symbol = strategy.select_target(date, self._price_history)
            if next_symbol != current_symbol:
                trades.append(
                    Trade(
                        datetime=date,
                        price=closes.get(next_symbol, 0.0) if next_symbol else 0.0,
                        size=1.0 if next_symbol else 0.0,
                    )
                )
                current_symbol = next_symbol
                prev_price = closes.get(current_symbol) if current_symbol else None

        performance, returns = compute_performance(equity_curve)
        return BacktestResult(
            equity_curve=tuple(equity_curve),
            trades=tuple(trades),
            performance_metrics=performance,
            daily_returns=returns,
        )
