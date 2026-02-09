"""Intent outputs from strategies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Optional


@dataclass(frozen=True)
class SingleAssetIntent:
    """Target position intent for a single asset strategy."""

    target_exposure: float
    reason: Optional[str] = None
    meta: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "single",
            "target_exposure": self.target_exposure,
            "reason": self.reason,
            "meta": dict(self.meta),
        }


@dataclass(frozen=True)
class PortfolioIntent:
    """Target weight intent for a portfolio strategy."""

    target_weights: Mapping[str, float]
    reason: Optional[str] = None
    meta: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "portfolio",
            "target_weights": dict(self.target_weights),
            "reason": self.reason,
            "meta": dict(self.meta),
        }


Intent = SingleAssetIntent | PortfolioIntent
IntentPayload = Dict[str, Any]
