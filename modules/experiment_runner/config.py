from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

from modules.strategies.base import Strategy


@dataclass
class ExperimentConfig:
    symbol: str
    start: date
    end: date
    strategies: List[Strategy] = field(default_factory=list)
    engine_config: Dict[str, object] = field(default_factory=dict)
