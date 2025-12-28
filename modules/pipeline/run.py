from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from modules.data_sources import (
    CacheMetadata,
    SyntheticSource,
    build_cache_path,
    load_cache,
    save_cache,
    validate_ohlcv,
)
from modules.experiment_runner import ExperimentRunner
from modules.reporting_ui import build_report, plot_equity_curves, save_report
from modules.strategies import MovingAverageCross


def prepare_data(symbol: str, start: date, end: date) -> pd.DataFrame:
    cache_path = build_cache_path(symbol, start, end)
    cached = load_cache(cache_path)
    if cached is not None:
        cached.index = pd.to_datetime(cached.index)
        return cached

    source = SyntheticSource(seed=42)
    df = source.fetch(symbol, start=start, end=end)
    validated = validate_ohlcv(df)
    clean_df = validated["data"]
    save_cache(
        clean_df,
        cache_path,
        CacheMetadata(symbol=symbol, start=start.isoformat(), end=end.isoformat(), source="SyntheticSource"),
    )
    return clean_df


def run_pipeline(
    symbol: str = "SYNTH",
    start: date = date(2022, 1, 1),
    end: date = date(2022, 12, 31),
    report_dir: Path = Path("data/reports"),
):
    data = prepare_data(symbol, start, end)

    baseline = MovingAverageCross(fast=10, slow=30)
    variant = MovingAverageCross(fast=5, slow=20)

    runner = ExperimentRunner()
    results = runner.run_strategies(data, [baseline, variant], engine_config={"position_fraction": 0.3})

    report_text = build_report(results)
    report_path = report_dir / "report.txt"
    save_report(report_text, report_path)

    equity_curves = {name: res.equity_curve for name, res in results.items()}
    plot_equity_curves(equity_curves, report_dir / "equity.png")

    return {"data": data, "results": results, "report_path": report_path}


if __name__ == "__main__":
    run_pipeline()
