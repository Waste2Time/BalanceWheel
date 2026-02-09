"""Rebalancer interfaces."""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, Mapping, Optional

from .models import Order


class Rebalancer:
    """Generate orders from target intent."""

    def generate(
        self,
        intent: Dict[str, Any],
        positions: Mapping[str, float],
        cash: float,
        prices: Mapping[str, float],
    ) -> Iterable[Order]:
        """Return order list to reach target state."""

        raise NotImplementedError


class SimpleRebalancer(Rebalancer):
    """Deterministic rebalancer with sell-first ordering."""

    def __init__(self, lot_size: int = 100) -> None:
        self.lot_size = lot_size

    def generate(
        self,
        intent: Dict[str, Any],
        positions: Mapping[str, float],
        cash: float,
        prices: Mapping[str, float],
    ) -> Iterable[Order]:
        targets = self._build_target_shares(intent, positions, cash, prices)
        sells: list[Order] = []
        buys: list[Order] = []
        for symbol in sorted(targets.keys()):
            target = targets[symbol]
            current = float(positions.get(symbol, 0.0))
            delta = target - current
            if delta < 0:
                sells.append(Order(symbol=symbol, side="sell", quantity=abs(delta)))
            elif delta > 0:
                buys.append(Order(symbol=symbol, side="buy", quantity=delta))
        return sells + buys

    def _build_target_shares(
        self,
        intent: Dict[str, Any],
        positions: Mapping[str, float],
        cash: float,
        prices: Mapping[str, float],
    ) -> Dict[str, float]:
        if not intent:
            return {symbol: float(positions.get(symbol, 0.0)) for symbol in positions}

        equity = self._estimate_equity(positions, cash, prices)
        intent_type = intent.get("type")
        if intent_type == "single":
            return self._single_target(intent, positions, prices, equity)
        if intent_type == "portfolio":
            return self._portfolio_targets(intent, positions, prices, equity)
        raise ValueError(f"Unknown intent type: {intent_type}")

    def _single_target(
        self,
        intent: Dict[str, Any],
        positions: Mapping[str, float],
        prices: Mapping[str, float],
        equity: float,
    ) -> Dict[str, float]:
        symbol = intent.get("symbol")
        if not symbol:
            if len(prices) == 1:
                symbol = next(iter(prices.keys()))
            elif len(positions) == 1:
                symbol = next(iter(positions.keys()))
            else:
                raise ValueError("Single-asset intent requires a symbol.")
        price = self._require_price(symbol, prices)
        target_pos = intent.get("target_pos")
        if target_pos is not None:
            target_shares = float(target_pos)
        else:
            target_exposure = float(intent.get("target_exposure", 0.0))
            target_shares = self._target_shares_from_exposure(equity, target_exposure, price)
        return {symbol: target_shares}

    def _portfolio_targets(
        self,
        intent: Dict[str, Any],
        positions: Mapping[str, float],
        prices: Mapping[str, float],
        equity: float,
    ) -> Dict[str, float]:
        weights: Mapping[str, float] = intent.get("target_weights", {})
        targets: Dict[str, float] = {}
        symbols = set(positions.keys()) | set(weights.keys())
        for symbol in symbols:
            weight = float(weights.get(symbol, 0.0))
            price = self._require_price(symbol, prices)
            targets[symbol] = self._target_shares_from_exposure(equity, weight, price)
        return targets

    def _estimate_equity(
        self, positions: Mapping[str, float], cash: float, prices: Mapping[str, float]
    ) -> float:
        equity = float(cash)
        for symbol, shares in positions.items():
            price = prices.get(symbol)
            if price is not None:
                equity += float(shares) * float(price)
        return equity

    def _target_shares_from_exposure(
        self, equity: float, exposure: float, price: float
    ) -> float:
        if price <= 0:
            return 0.0
        target_value: float = equity * exposure
        target_shares: float = math.floor(target_value / price / self.lot_size) * self.lot_size
        return float(max(target_shares, 0.0))

    @staticmethod
    def _require_price(symbol: str, prices: Mapping[str, float]) -> float:
        if symbol not in prices:
            raise ValueError(f"Missing price for {symbol}")
        return float(prices[symbol])
