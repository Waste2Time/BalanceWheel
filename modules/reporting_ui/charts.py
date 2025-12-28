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

    try:
        import matplotlib.pyplot as plt
    except Exception:
        # 回退为文本输出，保证在无 matplotlib 时仍可用
        path = output_dir / "equity_curve.csv"
        with path.open("w") as handle:
            handle.write("datetime,equity\\n")
            for ts, eq in zip(timestamps, equities):
                handle.write(f"{ts.isoformat()},{eq}\\n")
        return ChartPaths(equity_curve=path)

    fig, ax = plt.subplots()
    ax.plot(timestamps, equities, label="Equity")
    ax.set_title("Equity Curve")
    ax.legend()
    path = output_dir / "equity_curve.png"
    fig.autofmt_xdate()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ChartPaths(equity_curve=path)
