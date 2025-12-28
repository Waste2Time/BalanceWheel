from __future__ import annotations

import pandas as pd

from .base import Strategy


class MovingAverageCross(Strategy):
    def __init__(self, fast: int = 10, slow: int = 30, smooth: int = 1):
        super().__init__(name="moving_average_cross")
        self.fast = fast
        self.slow = slow
        self.smooth = smooth

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df["fast_ma"] = df["close"].rolling(self.fast).mean()
        df["slow_ma"] = df["close"].rolling(self.slow).mean()
        signal = (df["fast_ma"] > df["slow_ma"]).astype(int) * 2 - 1
        if self.smooth > 1:
            signal = signal.rolling(self.smooth).mean().round()
        df["signal"] = signal
        return df[["signal"]]
