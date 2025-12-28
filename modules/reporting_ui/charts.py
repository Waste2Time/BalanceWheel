from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path

from modules.backtest_engine.result import BacktestResult


@dataclass(frozen=True)
class ChartPaths:
    equity_curve: Path | None
    drawdown_curve: Path | None = None


def render_equity_curve(result: BacktestResult, output_dir: Path) -> ChartPaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamps = [point.datetime for point in result.equity_curve]
    equities = [point.equity for point in result.equity_curve]

    plt = _require_matplotlib(optional=True)
    if plt is None:
        return ChartPaths(equity_curve=None, drawdown_curve=None)

    fig, ax = plt.subplots()
    ax.plot(timestamps, equities, label="Equity")
    ax.set_title("Equity Curve")
    ax.legend()
    path = output_dir / "equity_curve.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    drawdown_path = _render_drawdown(timestamps, equities, output_dir, plt)
    return ChartPaths(equity_curve=path, drawdown_curve=drawdown_path)


def _render_drawdown(timestamps, equities, output_dir: Path, plt) -> Path:
    peak = equities[0] if equities else 0.0
    drawdowns = []
    for eq in equities:
        peak = max(peak, eq)
        drawdowns.append((eq - peak) / peak if peak else 0.0)

    fig, ax = plt.subplots()
    ax.plot(timestamps, drawdowns, label="Drawdown", color="red")
    ax.set_title("Drawdown")
    ax.legend()
    path = output_dir / "drawdown.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _require_matplotlib(optional: bool = False):
    if importlib.util.find_spec("matplotlib") is None:
        if optional:
            return None
        raise RuntimeError("matplotlib 未安装，无法生成图表。请先安装 matplotlib。")
    import matplotlib.pyplot as plt  # type: ignore

    return plt
