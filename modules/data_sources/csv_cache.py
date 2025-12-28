from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .models import Bar, DataSet

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _parse_datetime(value: str) -> datetime:
    return datetime.strptime(value, DATETIME_FORMAT)


def load_csv(path: Path, symbol: str, frequency: str) -> DataSet:
    bars: list[Bar] = []
    with path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            bars.append(
                Bar(
                    symbol=symbol,
                    datetime=_parse_datetime(row["datetime"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume", 0.0)),
                )
            )
    return DataSet.from_iterable(symbol=symbol, frequency=frequency, bars=bars)


def save_csv(path: Path, dataset: DataSet) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        fieldnames = ["datetime", "open", "high", "low", "close", "volume"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for bar in dataset.bars:
            row = asdict(bar)
            row["datetime"] = bar.datetime.strftime(DATETIME_FORMAT)
            writer.writerow({key: row[key] for key in fieldnames})
