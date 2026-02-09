"""Execution model interfaces."""

from __future__ import annotations

from typing import Iterable, Mapping

from balancewheel.data.model import Bar

from .models import ExecutableOrder, Trade


class ExecutionModel:
    """Convert executable orders into trades."""

    def execute(
        self,
        orders: Iterable[ExecutableOrder],
        bar: Bar | Mapping[str, Bar],
    ) -> Iterable[Trade]:
        """Return trades based on timing and pricing logic."""

        raise NotImplementedError
