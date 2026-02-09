"""Shared data models for the engine layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


@dataclass(frozen=True)
class AccountState:
    cash: float
    positions: Mapping[str, float] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        return {"cash": self.cash, "positions": dict(self.positions)}


@dataclass(frozen=True)
class Order:
    symbol: str
    side: str
    quantity: float
    limit_price: Optional[float] = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "limit_price": self.limit_price,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ExecutableOrder:
    order: Order
    adjusted_quantity: float
    accepted: bool
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order": self.order.to_dict(),
            "adjusted_quantity": self.adjusted_quantity,
            "accepted": self.accepted,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class Trade:
    symbol: str
    side: str
    quantity: float
    price: float
    datetime: Any
    status: str = "filled"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "datetime": self.datetime,
            "status": self.status,
        }


@dataclass(frozen=True)
class Fee:
    commission: float = 0.0
    tax: float = 0.0
    slippage: float = 0.0
    total: float = 0.0
    cash_delta: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commission": self.commission,
            "tax": self.tax,
            "slippage": self.slippage,
            "total": self.total,
            "cash_delta": self.cash_delta,
        }


@dataclass(frozen=True)
class AccountSnapshot:
    datetime: Any
    cash: float
    positions: Mapping[str, float]
    equity: float
    returns: float
    pnl: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "datetime": self.datetime,
            "cash": self.cash,
            "positions": dict(self.positions),
            "equity": self.equity,
            "returns": self.returns,
            "pnl": self.pnl,
        }
