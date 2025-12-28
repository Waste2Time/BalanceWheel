from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass
class StrategyMetadata:
    name: str
    params: Dict[str, object]


class Strategy(abc.ABC):
    """Strategy generates trading signals based on OHLCV data."""

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        ...

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(name=self.name, params=self.__dict__)
