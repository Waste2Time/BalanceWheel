from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from modules.backtest_engine.result import BacktestResult


@dataclass(frozen=True)
class ChartPaths:
    equity_curve: Path


def render_equity_curve(result: BacktestResult, output_dir: Path) -> ChartPaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamps = [point.datetime for point in result.equity_curve]
    equities = [point.equity for point in result.equity_curve]

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot(timestamps, equities, label="Equity")
    ax.set_title("Equity Curve")
    ax.legend()
    path = output_dir / "equity_curve.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ChartPaths(equity_curve=path)
