from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    symbol: str
    start: datetime
    end: datetime
    frequency: str
    engine_config: Any
    output_dir: Path | None = None
