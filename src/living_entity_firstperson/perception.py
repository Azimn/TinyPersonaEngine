"""Character-relative perceptual access and bounded attention."""

from __future__ import annotations

from dataclasses import replace
from math import cos, radians

from .models import AttentionState, ObservationPacket, ObserverState, Percept, Stimulus


class ObserverMismatch(ValueError):
    """Raised when a packet is delivered to the wrong private perspective."""


class PerceptionFilter:
    """Filter candidate stimuli by embodiment and spatial access.

    Occlusion is supplied by the authoritative game adapter. This package does
    not pretend it can infer collision geometry from text.
    """

    _PROXIMAL_MODALITIES = frozenset({"touch", "taste", "pain", "interoception"})

    def filter(
        self, packet: ObservationPacket, observer: ObserverState
    ) -> tuple[Percept, ...]:
        if packet.observer_id != observer.character_id:
            raise ObserverMismatch(
                f"packet for {packet.observer_id!r} cannot be read by "
                f"{observer.character_id!r}"
            )
        accessible: list[Percept] = []
        for stimulus in packet.stimuli:
            confidence = self._access_confidence(stimulus, observer)
            if confidence <= 0:
                continue
            sensitivity = max(0.0, observer.sensitivities.get(stimulus.modality, 1.0))
            confidence = min(1.0, confidence * sensitivity)
            if confidence <= 0:
                continue
            salience = min(
                1.0,
                0.65 * stimulus.intensity
                + 0.25 * confidence
                + 0.10 * float(bool(stimulus.metadata.get("urgent", False))),
            )
            accessible.append(
                Percept(
                    stimulus_id=stimulus.stimulus_id,
                    modality=stimulus.modality,
                    content=stimulus.content,
                    confidence=confidence,
                    salience=salience,
                    tags=stimulus.tags,
                    world_fact_ids=stimulus.world_fact_ids,
                    observer_id=observer.character_id,
                )
            )
        return tuple(accessible)

    def _access_confidence(
        self, stimulus: Stimulus, observer: ObserverState
    ) -> float:
        distance = observer.position.distance_to(stimulus.position)
        modality = stimulus.modality.lower()
        if modality in self._PROXIMAL_MODALITIES:
            return stimulus.intensity if distance <= 0.75 else 0.0
        if modality in {"vision", "sight"}:
            if stimulus.occluded or distance > observer.visual_range:
                return 0.0
            if distance > 0:
                direction = stimulus.position.minus(observer.position).normalized()
                threshold = cos(radians(observer.fov_degrees / 2.0))
                if observer.forward.normalized().dot(direction) < threshold:
                    return 0.0
            return stimulus.intensity * max(0.1, 1.0 - distance / observer.visual_range)
        if modality in {"hearing", "sound"}:
            if distance > observer.hearing_range:
                return 0.0
            occlusion_factor = 0.45 if stimulus.occluded else 1.0
            return (
                stimulus.intensity
                * occlusion_factor
                * max(0.1, 1.0 - distance / observer.hearing_range)
            )
        if modality == "smell":
            if distance > observer.smell_range:
                return 0.0
            occlusion_factor = 0.7 if stimulus.occluded else 1.0
            return (
                stimulus.intensity
                * occlusion_factor
                * max(0.1, 1.0 - distance / observer.smell_range)
            )
        return 0.0


class AttentionSelector:
    """Select only a bounded fraction of accessible perceptions."""

    def select(
        self,
        percepts: tuple[Percept, ...],
        observer: ObserverState,
        goal_tags: dict[str, frozenset[str]] | None = None,
    ) -> tuple[tuple[Percept, ...], AttentionState]:
        relevant_tags: set[str] = set()
        for goal in observer.goals:
            relevant_tags.update((goal_tags or {}).get(goal, ()))

        rescored: list[Percept] = []
        for percept in percepts:
            goal_boost = 0.2 if relevant_tags.intersection(percept.tags) else 0.0
            rescored.append(
                replace(percept, salience=min(1.0, percept.salience + goal_boost))
            )
        ranked = sorted(rescored, key=lambda item: (-item.salience, item.stimulus_id))
        attended = tuple(ranked[: observer.attention_capacity])
        missed = tuple(item.stimulus_id for item in ranked[observer.attention_capacity :])
        state = AttentionState(
            attended_ids=tuple(item.stimulus_id for item in attended),
            missed_ids=missed,
            focus=attended[0].content if attended else None,
        )
        return attended, state
