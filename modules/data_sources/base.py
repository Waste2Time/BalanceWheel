from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from .models import DataSet


class IDataSource(ABC):
    """数据源统一接口。"""

    @abstractmethod
    def fetch(self, symbol: str, start: datetime, end: datetime, frequency: str) -> DataSet:
        raise NotImplementedError
