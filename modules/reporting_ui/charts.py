from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from modules.backtest_engine import BacktestResult, EquityPoint


@dataclass(frozen=True)
class ChartPaths:
    equity_curve: Path | None = None
    overlay_curve: Path | None = None


def _try_import_matplotlib():
    try:
        import matplotlib.pyplot as plt

        return plt
    except Exception:
        return None


def _extract_xy(equity_curve: tuple[EquityPoint, ...]):
    xs = [point.datetime for point in equity_curve]
    ys = [point.equity for point in equity_curve]
    return xs, ys


def render_equity_curve(result: BacktestResult, output_dir: Path) -> ChartPaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    plt = _try_import_matplotlib()
    chart_paths = ChartPaths()
    if plt:
        xs, ys = _extract_xy(result.equity_curve)
        plt.figure(figsize=(10, 4))
        plt.plot(xs, ys, label="equity")
        plt.title("Equity Curve")
        plt.legend()
        path = output_dir / "equity.png"
        plt.savefig(path)
        plt.close()
        chart_paths = ChartPaths(equity_curve=path)
    else:
        csv_path = output_dir / "equity.csv"
        lines = ["datetime,equity\n"]
        for point in result.equity_curve:
            lines.append(f"{point.datetime},{point.equity}\n")
        csv_path.write_text("".join(lines))
        chart_paths = ChartPaths(equity_curve=csv_path)
    return chart_paths


def render_overlay_curves(results: Dict[str, BacktestResult], output_dir: Path) -> Path | None:
    plt = _try_import_matplotlib()
    output_dir.mkdir(parents=True, exist_ok=True)
    if plt:
        plt.figure(figsize=(10, 5))
        for name, result in results.items():
            xs, ys = _extract_xy(result.equity_curve)
            plt.plot(xs, ys, label=name)
        plt.title("Strategy Overlay")
        plt.legend()
        overlay_path = output_dir / "overlay.png"
        plt.savefig(overlay_path)
        plt.close()
        return overlay_path
    overlay_path = output_dir / "overlay.csv"
    headers = ["datetime"] + list(results.keys())
    lines = [",".join(headers) + "\n"]
    # assume same length
    length = min(len(r.equity_curve) for r in results.values()) if results else 0
    for idx in range(length):
        row = [str(list(results.values())[0].equity_curve[idx].datetime)]
        for res in results.values():
            row.append(str(res.equity_curve[idx].equity))
        lines.append(",".join(row) + "\n")
    overlay_path.write_text("".join(lines))
    return overlay_path
