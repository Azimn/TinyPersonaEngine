"""Event-driven first-person pipeline."""

from __future__ import annotations

from .memory import MemoryPort
from .models import (
    FirstPersonFrame,
    ObservationPacket,
    ObserverState,
    SensoryProfile,
)
from .perception import AttentionSelector, PerceptionFilter
from .transducer import SubjectiveTransducer


class FirstPersonPipeline:
    def __init__(self, *, memory: MemoryPort | None = None) -> None:
        self._filter = PerceptionFilter()
        self._attention = AttentionSelector()
        self._transducer = SubjectiveTransducer(memory)

    def process(
        self,
        packet: ObservationPacket,
        observer: ObserverState,
        profile: SensoryProfile,
    ) -> FirstPersonFrame:
        perceivable = self._filter.filter(packet, observer)
        attended, attention = self._attention.select(
            perceivable,
            observer,
            dict(profile.goal_tags),
        )
        experience = self._transducer.transduce(attended, observer, profile)
        return FirstPersonFrame(
            snapshot_id=packet.snapshot_id,
            observer_id=observer.character_id,
            perceivable=perceivable,
            attention=attention,
            experience=experience,
        )
