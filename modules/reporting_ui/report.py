from __future__ import annotations

from pathlib import Path
from typing import Dict

from modules.backtest_engine.result import BacktestResult


def format_metrics(metrics: Dict[str, float]) -> str:
    lines = ["指标:"]
    for key, value in metrics.items():
        lines.append(f"- {key}: {value:.4f}")
    return "\n".join(lines)


def build_report(results: Dict[str, BacktestResult]) -> str:
    report_lines = []
    for name, res in results.items():
        report_lines.append(f"策略: {name}")
        report_lines.append(format_metrics(res.metrics))
        report_lines.append("")
    return "\n".join(report_lines)


def save_report(text: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
