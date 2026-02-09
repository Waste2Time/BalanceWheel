"""Cost model interfaces."""

from __future__ import annotations

from typing import Iterable, Mapping

from .models import Fee, Trade


class CostModel:
    """Calculate costs and cash changes for trades."""

    def calculate(
        self,
        trades: Iterable[Trade],
        market_state: Mapping[str, object],
    ) -> Iterable[Fee]:
        """Return fees for each trade."""

        raise NotImplementedError
