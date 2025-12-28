from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from modules.backtest_engine.base import IBacktestEngine
from modules.backtest_engine.result import BacktestResult

from .config import ExperimentConfig


@dataclass(frozen=True)
class ExperimentResult:
    name: str
    results: dict[str, BacktestResult]
    summary: dict[str, dict[str, float]]


class ExperimentRunner:
    def __init__(self, engine: IBacktestEngine) -> None:
        self._engine = engine

    def run(self, config: ExperimentConfig, dataset, strategies: dict[str, object]) -> ExperimentResult:
        results: dict[str, BacktestResult] = {}
        for name, strategy in strategies.items():
            results[name] = self._engine.run(strategy, dataset, config.engine_config)
        summary = {name: result.performance_metrics for name, result in results.items()}
        if config.output_dir:
            _persist_summary(config.output_dir, config, summary)
        return ExperimentResult(name=config.name, results=results, summary=summary)


def _persist_summary(output_dir: Path, config: ExperimentConfig, summary: dict[str, dict[str, float]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = asdict(config)
    metadata["output_dir"] = str(config.output_dir)
    metadata["start"] = config.start.isoformat()
    metadata["end"] = config.end.isoformat()
    metadata["engine_config"] = repr(config.engine_config)
    (output_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
