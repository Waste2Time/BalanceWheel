"""Strategy lifecycle controller."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .context import StrategyContext
from .intent import Intent, IntentPayload, PortfolioIntent, SingleAssetIntent


class BaseStrategy:
    """Minimal base strategy with lifecycle hooks."""

    name: str
    frequency: str

    def __init__(self, params: Optional[Dict[str, Any]] = None, frequency: str = "1d"):
        self.name = self.__class__.__name__
        self.frequency = frequency
        self.params: Dict[str, Any] = params or {}
        self.state: Dict[str, Any] = {}

    def on_init(self) -> None:
        """Initialize strategy state."""

    def on_bar(self, context: StrategyContext) -> Optional[Intent | IntentPayload]:
        """Return intent based on the latest context."""

        return {}

    def on_reset(self) -> None:
        """Reset strategy state between runs."""

        self.state.clear()


@dataclass
class StrategyLifecycle:
    """Controller that manages strategy lifecycle calls."""

    strategy: BaseStrategy
    initialized: bool = field(default=False, init=False)

    def init(self) -> None:
        if not self.initialized:
            self.strategy.on_init()
            self.initialized = True

    def on_bar(self, context: StrategyContext) -> IntentPayload:
        if not self.initialized:
            self.init()
        raw_intent = self.strategy.on_bar(context)
        return self._normalize_intent(raw_intent)

    def reset(self) -> None:
        self.strategy.on_reset()
        self.initialized = False

    def _normalize_intent(self, intent: Optional[Intent | IntentPayload]) -> IntentPayload:
        if intent is None:
            return {}
        if isinstance(intent, SingleAssetIntent):
            return intent.to_dict()
        if isinstance(intent, PortfolioIntent):
            return intent.to_dict()
        if isinstance(intent, dict):
            return intent
        raise TypeError(f"Unsupported intent type: {type(intent)!r}")
