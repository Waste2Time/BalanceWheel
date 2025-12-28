from __future__ import annotations

from dataclasses import dataclass

from modules.backtest_engine.base import IBacktestEngine
from modules.backtest_engine.result import BacktestResult

from .config import ExperimentConfig


@dataclass(frozen=True)
class ExperimentResult:
    name: str
    results: dict[str, BacktestResult]


class ExperimentRunner:
    def __init__(self, engine: IBacktestEngine) -> None:
        self._engine = engine

    def run(self, config: ExperimentConfig, dataset, strategies: dict[str, object]) -> ExperimentResult:
        results: dict[str, BacktestResult] = {}
        for name, strategy in strategies.items():
            results[name] = self._engine.run(strategy, dataset, config.engine_config)
        return ExperimentResult(name=config.name, results=results)
