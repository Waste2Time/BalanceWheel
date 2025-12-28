from __future__ import annotations

from typing import Dict, List

import pandas as pd

from modules.backtest_engine.simple_engine import SimpleBacktestEngine
from modules.backtest_engine.result import BacktestResult
from modules.strategies.base import Strategy


class ExperimentRunner:
    def __init__(self):
        self.engine = SimpleBacktestEngine()

    def run_strategies(
        self, data: pd.DataFrame, strategies: List[Strategy], engine_config: Dict[str, object]
    ) -> Dict[str, BacktestResult]:
        results: Dict[str, BacktestResult] = {}
        for strategy in strategies:
            result = self.engine.run(strategy=strategy, data=data, config=engine_config)
            results[strategy.name] = result
        return results
