from __future__ import annotations

from .base import IBacktestEngine
from .result import BacktestResult


class VnpyBacktestEngine(IBacktestEngine):
    """vn.py 回测引擎适配器（待接入 vn.py 实现）。"""

    def run(self, strategy, data, config) -> BacktestResult:
        raise NotImplementedError("vn.py 适配器尚未实现。")
