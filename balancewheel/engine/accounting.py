"""Accounting interfaces."""

from __future__ import annotations

from typing import Iterable, Mapping

from .models import AccountSnapshot, AccountState, Fee, Trade


class Accounting:
    """Update account state from trades and market prices."""

    def apply(
        self,
        account: AccountState,
        trades: Iterable[Trade],
        fees: Iterable[Fee],
        prices: Mapping[str, float],
        dt: object,
    ) -> AccountSnapshot:
        """Return updated account snapshot."""

        raise NotImplementedError
