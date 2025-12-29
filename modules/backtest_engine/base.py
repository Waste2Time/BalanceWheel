from __future__ import annotations

from abc import ABC, abstractmethod

from .result import BacktestResult


class IBacktestEngine(ABC):
    @abstractmethod
    def run(self, strategy, data, config) -> BacktestResult:
        raise NotImplementedError
