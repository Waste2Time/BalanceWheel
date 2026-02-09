"""Recorder interfaces."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .models import AccountSnapshot, ExecutableOrder, Order, Trade


class Recorder:
    """Record engine outputs for analysis."""

    def on_init(self) -> None:
        """Prepare recorder resources."""

    def record_snapshot(self, snapshot: AccountSnapshot) -> None:
        """Record daily account snapshot."""

    def record_trades(self, trades: Iterable[Trade]) -> None:
        """Record trade executions."""

    def record_rebalance(self, dt: object, intent: Mapping[str, Any]) -> None:
        """Record strategy intent and rebalance decision."""

    def record_orders(
        self,
        dt: object,
        orders: Iterable[Order],
        executable_orders: Iterable[ExecutableOrder],
    ) -> None:
        """Record order lifecycle and constraint adjustments."""

    def finalize(self) -> Mapping[str, Any]:
        """Return bundle of recorded outputs."""

        return {}
