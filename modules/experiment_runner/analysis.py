from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable

from modules.backtest_engine import BacktestResult


@dataclass(frozen=True)
class SignificanceResult:
    baseline: str
    variant: str
    t_stat: float
    p_value: float
    baseline_mean: float
    variant_mean: float


def _mean_std(values: Iterable[float]) -> tuple[float, float]:
    vals = list(values)
    if not vals:
        return 0.0, 0.0
    mean = sum(vals) / len(vals)
    variance = sum((v - mean) ** 2 for v in vals) / max(len(vals) - 1, 1)
    return mean, math.sqrt(variance)


def welch_t_test(baseline: Iterable[float], variant: Iterable[float]) -> tuple[float, float]:
    a = list(baseline)
    b = list(variant)
    if len(a) < 2 or len(b) < 2:
        return 0.0, 1.0
    mean_a, std_a = _mean_std(a)
    mean_b, std_b = _mean_std(b)
    numerator = mean_a - mean_b
    denom = math.sqrt((std_a ** 2) / len(a) + (std_b ** 2) / len(b))
    if denom == 0:
        return 0.0, 1.0
    t_stat = numerator / denom
    # 简化 p 值估计（正态近似）
    p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(t_stat) / math.sqrt(2))))
    return t_stat, p_value


def aggregate_metrics(results: Dict[str, BacktestResult]) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for name, result in results.items():
        row = {"strategy": name}
        row.update(result.performance_metrics)
        rows.append(row)
    return rows


def compute_significance(results: Dict[str, BacktestResult]) -> list[SignificanceResult]:
    names = list(results.keys())
    if len(names) < 2:
        return []
    baseline_name = names[0]
    baseline_returns = [r.return_pct for r in results[baseline_name].daily_returns]
    output: list[SignificanceResult] = []
    for variant_name in names[1:]:
        variant_returns = [r.return_pct for r in results[variant_name].daily_returns]
        t_stat, p_value = welch_t_test(baseline_returns, variant_returns)
        base_mean, _ = _mean_std(baseline_returns)
        var_mean, _ = _mean_std(variant_returns)
        output.append(
            SignificanceResult(
                baseline=baseline_name,
                variant=variant_name,
                t_stat=t_stat,
                p_value=p_value,
                baseline_mean=base_mean,
                variant_mean=var_mean,
            )
        )
    return output
