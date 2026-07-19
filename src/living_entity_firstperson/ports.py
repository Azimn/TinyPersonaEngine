"""Adapters for engines and expression systems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import ObservationPacket


class ObservationSource(Protocol):
    def observe(self, observer_id: str) -> ObservationPacket: ...


@dataclass(frozen=True, slots=True)
class ExpressionCue:
    channel: str
    value: str
    intensity: float
    source_pressure: str


class ExpressionPort(Protocol):
    def emit(self, observer_id: str, cues: tuple[ExpressionCue, ...]) -> None: ...
