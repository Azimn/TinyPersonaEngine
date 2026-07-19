"""Private memory ports; semantic retrieval belongs behind this boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol

from .models import Experience, MemoryAssociation, Percept


@dataclass(frozen=True, slots=True)
class MemoryItem:
    memory_id: str
    character_id: str
    summary: str
    tags: frozenset[str]
    derived_from: tuple[str, ...]
    confidence: float = 1.0
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class MemoryPort(Protocol):
    """Adapter contract for Remnic-, Memoria-, Ori-, or custom storage."""

    def recall(
        self,
        *,
        character_id: str,
        query: str,
        tags: frozenset[str],
        limit: int = 3,
    ) -> tuple[MemoryAssociation, ...]: ...

    def record_percepts(
        self, *, character_id: str, percepts: tuple[Percept, ...]
    ) -> None: ...

    def record_experience(self, experience: Experience) -> None: ...


@dataclass(slots=True)
class InMemoryPerspectiveMemory:
    """Exact-tag reference backend for tests and demos.

    This is intentionally not a semantic retriever. Production integrations
    should provide hybrid retrieval, lifecycle, provenance, and rollback.
    """

    items: list[MemoryItem] = field(default_factory=list)
    recorded_percepts: dict[str, list[Percept]] = field(default_factory=dict)
    recorded_experiences: dict[str, list[Experience]] = field(default_factory=dict)

    def add(self, item: MemoryItem) -> None:
        self.items.append(item)

    def recall(
        self,
        *,
        character_id: str,
        query: str,
        tags: frozenset[str],
        limit: int = 3,
    ) -> tuple[MemoryAssociation, ...]:
        del query
        matches = [
            item
            for item in self.items
            if item.character_id == character_id and item.tags.intersection(tags)
        ]
        matches.sort(key=lambda item: (item.created_at, item.memory_id), reverse=True)
        return tuple(
            MemoryAssociation(
                memory_id=item.memory_id,
                summary=item.summary,
                confidence=item.confidence,
                provenance=item.derived_from,
            )
            for item in matches[:limit]
        )

    def record_percepts(
        self, *, character_id: str, percepts: tuple[Percept, ...]
    ) -> None:
        self.recorded_percepts.setdefault(character_id, []).extend(percepts)

    def record_experience(self, experience: Experience) -> None:
        self.recorded_experiences.setdefault(experience.observer_id, []).append(
            experience
        )
