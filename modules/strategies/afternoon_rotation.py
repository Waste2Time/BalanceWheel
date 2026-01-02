from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from modules.backtest_engine.rotation_engine import MultiAssetRotationStrategy


@dataclass(frozen=True)
class AfternoonEtfRule:
    chinext_symbol: str
    nasdaq_symbol: str
    index_symbol: str | None = None
    threshold: float = 0.001
    lookback: int = 21


class AfternoonEtfRotationStrategy(MultiAssetRotationStrategy):
    """根据近一月涨幅在 14:50 做出择时决策：

    - 如果创业板ETF涨幅最大且 > threshold，满仓创业板ETF
    - 否则如果纳指ETF涨幅最大且 > threshold，满仓纳指ETF
    - 其他情况空仓（模拟持有逆回购）
    """

    def __init__(self, rule: AfternoonEtfRule) -> None:
        self.rule = rule

    def _monthly_return(self, prices: List[float]) -> float:
        if len(prices) < self.rule.lookback:
            return 0.0
        start = prices[-self.rule.lookback]
        end = prices[-1]
        return (end - start) / start if start else 0.0

    def select_target(self, current_date: datetime, price_history: Dict[str, List[float]]) -> str | None:
        chinext_ret = self._monthly_return(price_history.get(self.rule.chinext_symbol, []))
        nasdaq_ret = self._monthly_return(price_history.get(self.rule.nasdaq_symbol, []))

        if chinext_ret >= nasdaq_ret and chinext_ret > self.rule.threshold:
            return self.rule.chinext_symbol
        if nasdaq_ret > chinext_ret and nasdaq_ret > self.rule.threshold:
            return self.rule.nasdaq_symbol
        return None
