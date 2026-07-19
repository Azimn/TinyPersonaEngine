"""Authority types and the canonical-world write boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class Authority(StrEnum):
    WORLD_FACT = "world_fact"
    PERCEPTION = "perception"
    BELIEF = "belief"
    EXPERIENCE = "experience"
    SUBJECTIVE_COMPLETION = "subjective_completion"


class AuthorityViolation(ValueError):
    """Raised when private or inferred state is promoted to world truth."""


@dataclass(frozen=True, slots=True)
class AuthoritativeFact:
    fact_id: str
    key: str
    value: Any
    source: str
    authority: Authority = Authority.WORLD_FACT


@dataclass(slots=True)
class WorldLedger:
    """Minimal canonical fact ledger.

    This is deliberately not called a world model. It only enforces who may
    write canonical facts and preserves prior versions for audit.
    """

    _current: dict[str, AuthoritativeFact] = field(default_factory=dict)
    _history: list[AuthoritativeFact] = field(default_factory=list)

    def record(self, fact: AuthoritativeFact) -> None:
        if fact.authority is not Authority.WORLD_FACT:
            raise AuthorityViolation(
                f"canonical facts require world_fact authority, got {fact.authority}"
            )
        if not fact.fact_id or not fact.key or not fact.source:
            raise ValueError("fact_id, key, and source are required")
        self._current[fact.key] = fact
        self._history.append(fact)

    def propose_private(
        self, *, authority: Authority, key: str, value: Any, source: str
    ) -> None:
        """Explicitly reject a private record at the canonical boundary."""
        raise AuthorityViolation(
            f"{authority} from {source!r} cannot set canonical fact {key!r}={value!r}"
        )

    @property
    def current(self) -> Mapping[str, AuthoritativeFact]:
        return MappingProxyType(self._current)

    @property
    def history(self) -> tuple[AuthoritativeFact, ...]:
        return tuple(self._history)
