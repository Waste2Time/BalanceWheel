from __future__ import annotations

from abc import ABC, abstractmethod

from modules.data_sources.models import Bar


class Strategy(ABC):
    @abstractmethod
    def on_bar(self, bar: Bar, history: list[Bar]) -> float:
        """返回目标仓位（以标的数量表示）。"""
        raise NotImplementedError
