"""Small per-character short-term state for game-loop integration."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .models import FirstPersonFrame


@dataclass(slots=True)
class PerspectiveBlackboard:
    """Bounded working state, not durable autobiographical memory."""

    capacity: int = 8
    _frames: dict[str, deque[FirstPersonFrame]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.capacity < 1:
            raise ValueError("blackboard capacity must be at least 1")

    def update(self, frame: FirstPersonFrame) -> None:
        frames = self._frames.setdefault(
            frame.observer_id, deque(maxlen=self.capacity)
        )
        frames.append(frame)

    def latest(self, character_id: str) -> FirstPersonFrame | None:
        frames = self._frames.get(character_id)
        return frames[-1] if frames else None

    def history(self, character_id: str) -> tuple[FirstPersonFrame, ...]:
        return tuple(self._frames.get(character_id, ()))

    def clear(self, character_id: str) -> None:
        self._frames.pop(character_id, None)
