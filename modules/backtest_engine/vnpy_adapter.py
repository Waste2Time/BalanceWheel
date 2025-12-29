from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import importlib.util
from typing import Iterable, Type

from modules.data_sources.models import Bar, DataSet
from modules.strategies.base import Strategy

from .base import IBacktestEngine
from .result import BacktestResult, EquityPoint, Trade


@dataclass(frozen=True)
class VnpyBacktestConfig:
    """vn.py 回测所需的核心参数。"""

    vt_symbol: str | None = None
    rate: float = 0.0
    slippage: float = 0.0
    size: int = 1
    price_tick: float = 0.01
    capital: float = 1_000_000.0
    strategy_settings: dict = field(default_factory=dict)


class VnpyBacktestEngine(IBacktestEngine):
    """vn.py 回测引擎适配器，将自定义 Strategy 委托到 vn.py CTA 引擎。"""

    def _require_dependency(self) -> None:
        missing = [
            name
            for name in ("vnpy", "vnpy_ctastrategy")
            if importlib.util.find_spec(name) is None
        ]
        if missing:
            hint = "、".join(missing)
            raise ImportError(f"缺少依赖 {hint}，请先执行 `pip install vnpy vnpy_ctastrategy`。")

    def _map_interval(self, frequency: str):
        from vnpy.trader.constant import Interval

        mapping = {"1d": Interval.DAILY}
        if frequency not in mapping:
            raise ValueError("vn.py 适配器目前仅支持日线频率 '1d'")
        return mapping[frequency]

    def _build_delegate_strategy(
        self, strategy: Strategy
    ) -> Type["DelegatingCtaStrategy"]:
        from vnpy.app.cta_strategy import CtaTemplate

        class DelegatingCtaStrategy(CtaTemplate):
            author = "BalanceWheel"
            parameters: list[str] = []
            variables: list[str] = ["pos"]

            def __init__(self, cta_engine, strategy_name: str, setting: dict) -> None:
                super().__init__(cta_engine, strategy_name, setting)
                self._delegate = strategy
                self._history: list[Bar] = []

            def on_init(self) -> None:
                self.write_log("策略初始化完成")
                self.load_bar(0)

            def on_start(self) -> None:
                self.write_log("策略启动")
                self.put_event()

            def on_stop(self) -> None:
                self.write_log("策略停止")
                self.put_event()

            def on_bar(self, bar) -> None:  # bar: BarData
                from modules.data_sources.models import Bar as SimpleBar

                converted = SimpleBar(
                    symbol=bar.symbol,
                    datetime=bar.datetime,
                    open=bar.open_price,
                    high=bar.high_price,
                    low=bar.low_price,
                    close=bar.close_price,
                    volume=bar.volume,
                )
                self._history.append(converted)
                target = self._delegate.on_bar(converted, self._history)
                delta = target - self.pos
                if delta > 0:
                    self.buy(price=bar.close_price, volume=delta)
                elif delta < 0:
                    self.sell(price=bar.close_price, volume=abs(delta))
                self.put_event()

        return DelegatingCtaStrategy

    def _convert_bars(self, dataset: DataSet) -> Iterable:
        from vnpy.trader.constant import Interval, Exchange
        from vnpy.trader.object import BarData

        interval = self._map_interval(dataset.frequency)
        exchange = Exchange.LOCAL
        return [
            BarData(
                symbol=bar.symbol,
                exchange=exchange,
                datetime=bar.datetime,
                interval=interval,
                volume=bar.volume,
                open_price=bar.open,
                high_price=bar.high,
                low_price=bar.low,
                close_price=bar.close,
                gateway_name="BACKTEST",
            )
            for bar in dataset.bars
        ]

    def run(self, strategy: Strategy, data: DataSet, config: VnpyBacktestConfig) -> BacktestResult:
        self._require_dependency()
        from vnpy.app.cta_strategy.backtesting import BacktestingEngine, BacktestingMode
        from vnpy.trader.constant import Interval

        interval = self._map_interval(data.frequency)
        bars = self._convert_bars(data)
        delegate_strategy = self._build_delegate_strategy(strategy)

        engine = BacktestingEngine()
        engine.set_parameters(
            vt_symbol=config.vt_symbol or data.symbol,
            interval=interval,
            start=data.start() or datetime.utcnow(),
            end=data.end() or datetime.utcnow(),
            rate=config.rate,
            slippage=config.slippage,
            size=config.size,
            price_tick=config.price_tick,
            capital=config.capital,
            mode=BacktestingMode.BAR,
        )
        engine.add_strategy(delegate_strategy, config.strategy_settings)
        engine.history_data = list(bars)
        engine.data = list(bars)
        engine.run_backtesting()
        result_df = engine.calculate_result()
        stats = engine.calculate_statistics(output=False)

        equity_curve: list[EquityPoint] = []
        if not result_df.empty and "balance" in result_df.columns:
            for row in result_df.itertuples():
                timestamp = getattr(row, "Index", None) or getattr(row, "datetime")
                equity_curve.append(
                    EquityPoint(datetime=timestamp, equity=float(getattr(row, "balance")))
                )

        trades: list[Trade] = []
        for trade in engine.trades.values():
            trades.append(Trade(datetime=trade.datetime, price=trade.price, size=trade.volume))

        performance = {
            "total_return": float(stats.get("total_return", 0.0)),
            "max_drawdown": float(stats.get("max_drawdown", 0.0)),
            "sharpe_ratio": float(stats.get("sharpe_ratio", 0.0)),
        }
        if not equity_curve:
            performance.setdefault("total_return", 0.0)
            performance.setdefault("max_drawdown", 0.0)

        return BacktestResult(
            equity_curve=tuple(equity_curve),
            trades=tuple(trades),
            performance_metrics=performance,
        )
