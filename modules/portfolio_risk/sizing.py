from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PositionSizer:
    max_position: float = 1.0

    def size(self, target_position: float) -> float:
        return max(min(target_position, self.max_position), -self.max_position)
