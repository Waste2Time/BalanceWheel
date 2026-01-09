"""Persistence for normalized data."""

from __future__ import annotations

import json
from datetime import datetime
from hashlib import sha256
from pathlib import Path

import pandas as pd


class CsvRepository:
    """Save normalized data to CSV files."""

    def __init__(self, root: str | Path = "data") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.meta_root = self.root / "_meta"
        self.meta_root.mkdir(parents=True, exist_ok=True)

    def save(self, symbol: str, asset_type: str, data: pd.DataFrame) -> Path:
        filename = f"{asset_type}_{symbol}.csv"
        path = self.root / filename
        data.to_csv(path, index=False)
        return path

    def write_meta(self, record: dict, batch: dict) -> None:
        manifest_path = self.meta_root / "manifest.jsonl"
        with manifest_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

        current_path = self.meta_root / "current.json"
        current_path.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")


def build_meta(
    symbol: str,
    path: Path,
    source: str,
    adjust: str,
    start: str,
    end: str,
    data: pd.DataFrame,
) -> dict:
    timestamp = datetime.utcnow().isoformat()
    last_date = data["datetime"].iloc[-1].isoformat()
    fingerprint = file_fingerprint(path)
    return {
        "timestamp": timestamp,
        "symbol": symbol,
        "path": str(path),
        "source": source,
        "adjust": adjust,
        "start": start,
        "end": end,
        "rows": int(len(data)),
        "last_date": last_date,
        "fingerprint": fingerprint,
    }


def file_fingerprint(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()
