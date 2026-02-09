"""Engine lifecycle controller."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Optional

from balancewheel.data.interfaces import DataProvider
from balancewheel.data.model import Bar
from balancewheel.strategy import AccountState as StrategyAccountState
from balancewheel.strategy import StrategyContext

from .accounting import Accounting
from .constraints import Constraints
from .cost import CostModel
from .execution import ExecutionModel
from .models import AccountSnapshot, AccountState
from .rebalancer import Rebalancer
from .recorder import Recorder
from .strategy_adapter import StrategyAdapter


@dataclass
class EngineLifecycle:
    """Main controller for engine lifecycle."""

    strategy_adapter: StrategyAdapter
    rebalancer: Rebalancer
    constraints: Constraints
    execution_model: ExecutionModel
    cost_model: CostModel
    accounting: Accounting
    recorder: Recorder
    data_provider: DataProvider
    initial_cash: float = 0.0
    run_meta: Dict[str, Any] = field(default_factory=dict)
    account_state: Optional[AccountState] = field(default=None, init=False)

    def configure(self, **kwargs: Any) -> None:
        """Persist run metadata for reproducibility."""

        self.run_meta = dict(kwargs)

    def init(self) -> None:
        """Initialize account and recorder."""

        self.account_state = AccountState(cash=self.initial_cash, positions={})
        self.recorder.on_init()

    def run(self) -> Iterable[AccountSnapshot]:
        """Run the backtest loop and yield snapshots."""

        if self.account_state is None:
            self.init()

        snapshots: list[AccountSnapshot] = []

        for dt, bars in self.data_provider.iter_bars():
            prices = self._extract_prices(bars)
            equity = self._estimate_equity(self.account_state, prices)
            context = StrategyContext(
                datetime=dt,
                bars=bars,
                history={},
                state=self._strategy_account_state(equity),
                extra={},
            )
            intent = self.strategy_adapter.on_bar(context)
            if intent is None:
                intent = {}
            self.recorder.record_rebalance(dt, intent)

            orders = list(
                self.rebalancer.generate(
                    intent=intent,
                    positions=self.account_state.positions,
                    cash=self.account_state.cash,
                    prices=prices,
                )
            )
            executable_orders = list(
                self.constraints.apply(
                    orders=orders,
                    account=self.account_state,
                    market_state={},
                )
            )
            self.recorder.record_orders(dt, orders, executable_orders)

            trades = list(self.execution_model.execute(executable_orders, bars))
            fees = list(self.cost_model.calculate(trades, market_state={}))
            snapshot = self.accounting.apply(
                account=self.account_state,
                trades=trades,
                fees=fees,
                prices=prices,
                dt=dt,
            )
            self.account_state = AccountState(
                cash=snapshot.cash,
                positions=snapshot.positions,
            )
            self.recorder.record_trades(trades)
            self.recorder.record_snapshot(snapshot)
            snapshots.append(snapshot)

        return snapshots

    def finalize(self) -> Dict[str, Any]:
        """Finalize and return result bundle."""

        bundle = dict(self.recorder.finalize())
        bundle["meta"] = dict(self.run_meta)
        return bundle

    def _strategy_account_state(self, equity: Mapping[str, float]) -> StrategyAccountState:
        if self.account_state is None:
            return StrategyAccountState(cash=self.initial_cash, equity=equity, positions={})
        return StrategyAccountState(
            cash=self.account_state.cash,
            equity=equity,
            positions=self.account_state.positions,
        )

    @staticmethod
    def _extract_prices(bars: Any) -> Mapping[str, float]:
        if isinstance(bars, Mapping):
            prices = {}
            for symbol, bar in bars.items():
                if isinstance(bar, Bar):
                    prices[symbol] = float(bar.close)
            return prices
        if isinstance(bars, Bar):
            return {"single": float(bars.close)}
        return {}

    @staticmethod
    def _estimate_equity(
        account: AccountState, prices: Mapping[str, float]
    ) -> Mapping[str, float]:
        equity: Dict[str, float] = {}
        for symbol, shares in account.positions.items():
            price = prices.get(symbol)
            if price is not None:
                equity[symbol] = float(shares) * float(price)
        return equity
