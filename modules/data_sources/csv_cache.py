from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from modules import DATA_DIR


@dataclass
class CacheMetadata:
    symbol: str
    start: Optional[str]
    end: Optional[str]
    source: str


def build_cache_path(symbol: str, start: Optional[date], end: Optional[date]) -> Path:
    safe_symbol = symbol.replace("/", "_").replace(" ", "_")
    start_str = start.isoformat() if start else "start"
    end_str = end.isoformat() if end else "end"
    filename = f"{safe_symbol}_{start_str}_{end_str}.csv"
    return DATA_DIR / "cache" / filename


def ensure_cache_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_cache(df: pd.DataFrame, path: Path, metadata: CacheMetadata) -> None:
    ensure_cache_dir(path)
    df.to_csv(path, index=True)
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(asdict(metadata), ensure_ascii=False, indent=2))


def load_cache(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    return pd.read_csv(path, index_col=0, parse_dates=True)
