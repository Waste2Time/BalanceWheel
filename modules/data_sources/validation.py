from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Bar, DataSet


@dataclass(frozen=True)
class ValidationReport:
    symbol: str
    missing_ratio: float
    close_diff_mean: float
    close_diff_max: float


@dataclass(frozen=True)
class OrderingValidation:
    symbol: str
    is_sorted: bool
    has_duplicates: bool


def _close_diffs(left: Iterable[Bar], right: Iterable[Bar]) -> list[float]:
    right_map = {bar.datetime: bar.close for bar in right}
    diffs: list[float] = []
    for bar in left:
        if bar.datetime in right_map:
            diffs.append(abs(bar.close - right_map[bar.datetime]))
    return diffs


def validate_pair(primary: DataSet, secondary: DataSet) -> ValidationReport:
    primary_times = {bar.datetime for bar in primary.bars}
    secondary_times = {bar.datetime for bar in secondary.bars}
    missing = primary_times.symmetric_difference(secondary_times)
    total = len(primary_times.union(secondary_times))
    missing_ratio = len(missing) / total if total else 0.0
    diffs = _close_diffs(primary.bars, secondary.bars)
    close_diff_mean = sum(diffs) / len(diffs) if diffs else 0.0
    close_diff_max = max(diffs) if diffs else 0.0
    return ValidationReport(
        symbol=primary.symbol,
        missing_ratio=missing_ratio,
        close_diff_mean=close_diff_mean,
        close_diff_max=close_diff_max,
    )


def validate_ordering(dataset: DataSet) -> OrderingValidation:
    """检查时间序列是否有序且无重复时间戳。"""

    timestamps = [bar.datetime for bar in dataset.bars]
    is_sorted = all(earlier <= later for earlier, later in zip(timestamps, timestamps[1:]))
    has_duplicates = len(timestamps) != len(set(timestamps))
    return OrderingValidation(
        symbol=dataset.symbol,
        is_sorted=is_sorted,
        has_duplicates=has_duplicates,
    )
