"""Strategy context definitions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, MutableMapping, Union, List

from balancewheel.data.model import Bar

Bars = Mapping[str, Bar]
HistoryView = Mapping[str, List[Bar]]
ExtraView = Mapping[str, Any]


@dataclass(frozen=True)
class AccountState:
    """Read-only account snapshot for strategy consumption."""

    cash: float
    equity: Mapping[str, float] = field(default_factory=dict)
    positions: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyContext:
    """Context passed from engine to strategy."""

    datetime: Any
    bars: Union[Bar, Bars]
    history: HistoryView = field(default_factory=dict)
    state: AccountState = field(default_factory=lambda: AccountState(cash=0.0))
    extra: ExtraView = field(default_factory=dict)

    def to_dict(self) -> MutableMapping[str, Any]:
        """Return a shallow-serializable view for logging."""

        return {
            "datetime": self.datetime,
            "bars": self._serialize_bars(),
            "history": self.history,
            "state": {
                "cash": self.state.cash,
                "equity": dict(self.state.equity),
                "positions": dict(self.state.positions),
            },
            "extra": self.extra,
        }

    def _serialize_bars(self) -> Any:
        # 如果 bars 是单个 Bar
        if isinstance(self.bars, Bar):
            return asdict(self.bars)

        # 如果 bars 是字典/Mapping
        if isinstance(self.bars, dict) or hasattr(self.bars, 'items'):
            result = {}
            for symbol, bar in self.bars.items():
                # 如果是 Bar 列表
                if isinstance(bar, list):
                    result[symbol] = [asdict(b) for b in bar if isinstance(b, Bar)]
                # 如果是单个 Bar
                elif isinstance(bar, Bar):
                    result[symbol] = asdict(bar)
                # 其他情况（应该是异常情况）
                else:
                    result[symbol] = bar
            return result

        # 其他无法处理的情况
        return self.bars
