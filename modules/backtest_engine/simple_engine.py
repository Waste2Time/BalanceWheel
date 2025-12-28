from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd

from modules.portfolio_risk.risk import compute_metrics
from modules.portfolio_risk.sizing import fixed_fractional_size
from modules.strategies.base import Strategy
from .base import BacktestEngine
from .result import BacktestResult, Trade


class SimpleBacktestEngine(BacktestEngine):
    """Lightweight backtester for single-asset strategies."""

    def run(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        config: Optional[Dict[str, object]] = None,
    ) -> BacktestResult:
        cfg = {
            "initial_capital": 100_000.0,
            "fee_rate": 0.0005,
            "slippage": 0.0,
            "position_fraction": 0.2,
            "min_qty": 1,
            "max_drawdown_stop": 0.2,
        }
        if config:
            cfg.update(config)

        price = data["close"]
        signals = strategy.generate_signals(data.copy())
        signals["signal"] = signals["signal"].fillna(0).astype(float)
        position = signals["signal"].copy()
        position = position.ffill().fillna(0)

        equity = []
        cash = cfg["initial_capital"]
        qty = 0.0
        trades = []
        peak_equity = cfg["initial_capital"]

        for dt, sig in position.iteritems():
            px = price.loc[dt]
            target_qty = 0
            if sig != 0:
                target_qty = fixed_fractional_size(
                    capital=cash + qty * px,
                    price=px,
                    fraction=cfg["position_fraction"],
                    min_qty=cfg["min_qty"],
                )
                if sig < 0:
                    target_qty *= -1
            trade_qty = target_qty - qty
            if trade_qty != 0:
                fee = abs(trade_qty) * px * cfg["fee_rate"]
                cash -= trade_qty * (px + np.sign(trade_qty) * cfg["slippage"]) + fee
                trades.append(
                    Trade(
                        entry_date=dt,
                        entry_price=px,
                        exit_date=None,
                        exit_price=None,
                        quantity=trade_qty,
                        pnl=0.0,
                    )
                )
                qty = target_qty
            equity_value = cash + qty * px
            peak_equity = max(peak_equity, equity_value)
            drawdown = (peak_equity - equity_value) / peak_equity
            if drawdown > cfg["max_drawdown_stop"]:
                if qty != 0:
                    fee = abs(qty) * px * cfg["fee_rate"]
                    cash -= qty * px + fee
                    trades.append(
                        Trade(
                            entry_date=dt,
                            entry_price=px,
                            exit_date=dt,
                            exit_price=px,
                            quantity=-qty,
                            pnl=0.0,
                        )
                    )
                    qty = 0
                equity_value = cash
            equity.append((dt, equity_value))

        equity_series = pd.Series({dt: val for dt, val in equity})
        metrics = compute_metrics(equity_series)
        return BacktestResult(equity_curve=equity_series, metrics=metrics, trades=trades, signals=signals)
