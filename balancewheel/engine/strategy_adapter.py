"""Strategy adapter interfaces."""

from __future__ import annotations

from enum import IntEnum
from typing import Any, Dict, Optional

from balancewheel.strategy import SingleAssetIntent, StrategyContext


class Signal(IntEnum):
    BUY = 1
    SELL = -1
    HOLD = 0


class StrategyAdapter:
    """Bridge engine context to strategy intent."""

    def __init__(self, strategy: Any) -> None:
        self.strategy = strategy

    def on_bar(self, context: StrategyContext) -> Optional[Dict[str, Any]]:
        """Return intent payload from strategy layer."""

        raise NotImplementedError


class SignalStrategyAdapter(StrategyAdapter):
    """Adapter for signal-based strategies."""

    def on_bar(self, context: StrategyContext) -> Optional[Dict[str, Any]]:
        signal = self.strategy.on_bar(context)
        if signal == Signal.BUY:
            return SingleAssetIntent(target_exposure=1.0, reason="ma_cross_buy").to_dict()
        if signal == Signal.SELL:
            return SingleAssetIntent(target_exposure=0.0, reason="ma_cross_sell").to_dict()
        if signal == Signal.HOLD:
            return None
        raise ValueError(f"Unknown signal: {signal}")
