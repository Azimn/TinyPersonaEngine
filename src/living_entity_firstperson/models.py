"""Dependency-free records for first-person perception."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Any, Mapping

from .authority import Authority


def _unit_interval(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class Vec3:
    x: float
    y: float
    z: float

    def distance_to(self, other: "Vec3") -> float:
        return sqrt(
            (self.x - other.x) ** 2
            + (self.y - other.y) ** 2
            + (self.z - other.z) ** 2
        )

    def normalized(self) -> "Vec3":
        length = sqrt(self.x**2 + self.y**2 + self.z**2)
        if length == 0:
            raise ValueError("direction vector cannot be zero")
        return Vec3(self.x / length, self.y / length, self.z / length)

    def dot(self, other: "Vec3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def minus(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)


@dataclass(frozen=True, slots=True)
class Stimulus:
    stimulus_id: str
    modality: str
    position: Vec3
    content: str
    tags: frozenset[str] = frozenset()
    intensity: float = 0.5
    world_fact_ids: tuple[str, ...] = ()
    occluded: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.stimulus_id or not self.modality or not self.content:
            raise ValueError("stimulus_id, modality, and content are required")
        _unit_interval("intensity", self.intensity)


@dataclass(frozen=True, slots=True)
class ObservationPacket:
    snapshot_id: str
    observer_id: str
    stimuli: tuple[Stimulus, ...]

    def __post_init__(self) -> None:
        if not self.snapshot_id or not self.observer_id:
            raise ValueError("snapshot_id and observer_id are required")


@dataclass(frozen=True, slots=True)
class ObserverState:
    character_id: str
    position: Vec3
    forward: Vec3
    visual_range: float = 25.0
    fov_degrees: float = 100.0
    hearing_range: float = 18.0
    smell_range: float = 4.0
    attention_capacity: int = 3
    goals: frozenset[str] = frozenset()
    sensitivities: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.forward.normalized()
        if self.visual_range <= 0 or self.hearing_range <= 0 or self.smell_range <= 0:
            raise ValueError("sensory ranges must be positive")
        if not 0 < self.fov_degrees <= 360:
            raise ValueError("fov_degrees must be in (0, 360]")
        if self.attention_capacity < 1:
            raise ValueError("attention_capacity must be at least 1")


@dataclass(frozen=True, slots=True)
class Percept:
    stimulus_id: str
    modality: str
    content: str
    confidence: float
    salience: float
    tags: frozenset[str]
    world_fact_ids: tuple[str, ...]
    observer_id: str
    authority: Authority = Authority.PERCEPTION

    def __post_init__(self) -> None:
        _unit_interval("confidence", self.confidence)
        _unit_interval("salience", self.salience)
        if self.authority is not Authority.PERCEPTION:
            raise ValueError("percepts must have perception authority")


@dataclass(frozen=True, slots=True)
class AttentionState:
    attended_ids: tuple[str, ...]
    missed_ids: tuple[str, ...]
    focus: str | None


@dataclass(frozen=True, slots=True)
class MemoryAssociation:
    memory_id: str
    summary: str
    confidence: float
    provenance: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MicroDetail:
    detail: str
    confidence: float
    trigger_percept_id: str
    consequence: str
    authority: Authority = Authority.SUBJECTIVE_COMPLETION

    def __post_init__(self) -> None:
        _unit_interval("confidence", self.confidence)
        if self.authority is not Authority.SUBJECTIVE_COMPLETION:
            raise ValueError("micro-details must remain subjective completions")
        if not self.consequence:
            raise ValueError("decorative micro-details without consequences are forbidden")


@dataclass(frozen=True, slots=True)
class ActionPressure:
    name: str
    utility: float
    reason: str
    source_percept_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _unit_interval("utility", self.utility)


@dataclass(frozen=True, slots=True)
class Experience:
    observer_id: str
    percept_ids: tuple[str, ...]
    focus: str | None
    valence: float
    arousal: float
    familiarity: float
    memory_cues: tuple[str, ...]
    associations: tuple[MemoryAssociation, ...]
    micro_details: tuple[MicroDetail, ...]
    pressures: tuple[ActionPressure, ...]
    authority: Authority = Authority.EXPERIENCE

    def __post_init__(self) -> None:
        if not -1.0 <= self.valence <= 1.0:
            raise ValueError("valence must be between -1 and 1")
        _unit_interval("arousal", self.arousal)
        _unit_interval("familiarity", self.familiarity)


@dataclass(frozen=True, slots=True)
class Belief:
    belief_id: str
    observer_id: str
    content: str
    confidence: float
    source_percept_ids: tuple[str, ...]
    authority: Authority = Authority.BELIEF

    def __post_init__(self) -> None:
        _unit_interval("confidence", self.confidence)
        if not self.source_percept_ids:
            raise ValueError("beliefs require perception provenance")
        if self.authority is not Authority.BELIEF:
            raise ValueError("beliefs must have belief authority")


@dataclass(frozen=True, slots=True)
class CompletionRule:
    trigger_tag: str
    detail: str
    confidence: float
    pressure_name: str | None = None
    pressure_utility: float = 0.0
    memory_query: str | None = None

    def __post_init__(self) -> None:
        _unit_interval("confidence", self.confidence)
        _unit_interval("pressure_utility", self.pressure_utility)
        if not self.pressure_name and not self.memory_query:
            raise ValueError(
                "a subjective completion must cue memory, create pressure, or both"
            )
        if self.pressure_name is None and self.pressure_utility:
            raise ValueError("pressure_utility requires pressure_name")


@dataclass(frozen=True, slots=True)
class SensoryProfile:
    valence_by_tag: Mapping[str, float] = field(default_factory=dict)
    familiarity_by_tag: Mapping[str, float] = field(default_factory=dict)
    goal_tags: Mapping[str, frozenset[str]] = field(default_factory=dict)
    completion_rules: tuple[CompletionRule, ...] = ()

    def __post_init__(self) -> None:
        for value in self.valence_by_tag.values():
            if not -1.0 <= value <= 1.0:
                raise ValueError("tag valence must be between -1 and 1")
        for value in self.familiarity_by_tag.values():
            _unit_interval("tag familiarity", value)


@dataclass(frozen=True, slots=True)
class StructuredAction:
    name: str
    parameters: Mapping[str, Any]
    utility: float
    source_pressure: str

    def __post_init__(self) -> None:
        _unit_interval("utility", self.utility)


@dataclass(frozen=True, slots=True)
class FirstPersonFrame:
    snapshot_id: str
    observer_id: str
    perceivable: tuple[Percept, ...]
    attention: AttentionState
    experience: Experience
