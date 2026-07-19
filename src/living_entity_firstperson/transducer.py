"""Turn noticed evidence into private, consequential experience."""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256

from .memory import MemoryPort
from .models import (
    ActionPressure,
    CompletionRule,
    Experience,
    MemoryAssociation,
    MicroDetail,
    ObserverState,
    Percept,
    SensoryProfile,
)


class SubjectiveTransducer:
    def __init__(self, memory: MemoryPort | None = None) -> None:
        self._memory = memory

    def transduce(
        self,
        percepts: tuple[Percept, ...],
        observer: ObserverState,
        profile: SensoryProfile,
    ) -> Experience:
        total_weight = sum(percept.salience for percept in percepts) or 1.0
        valence = sum(
            percept.salience
            * self._mean(
                tuple(profile.valence_by_tag[tag] for tag in percept.tags if tag in profile.valence_by_tag)
            )
            for percept in percepts
        ) / total_weight
        familiarity = sum(
            percept.salience
            * self._mean(
                tuple(
                    profile.familiarity_by_tag[tag]
                    for tag in percept.tags
                    if tag in profile.familiarity_by_tag
                )
            )
            for percept in percepts
        ) / total_weight
        arousal = min(
            1.0,
            sum(percept.salience * percept.confidence for percept in percepts)
            / total_weight,
        )

        associations: dict[str, MemoryAssociation] = {}
        memory_cues: list[str] = []
        micro_details: list[MicroDetail] = []
        pressure_values: dict[str, float] = defaultdict(float)
        pressure_sources: dict[str, list[str]] = defaultdict(list)
        pressure_reasons: dict[str, list[str]] = defaultdict(list)

        for percept in percepts:
            for rule in self._matching_rules(percept, profile):
                consequence_parts: list[str] = []
                if rule.memory_query:
                    memory_cues.append(rule.memory_query)
                    consequence_parts.append(f"memory cue: {rule.memory_query}")
                    if self._memory:
                        recalled = self._memory.recall(
                            character_id=observer.character_id,
                            query=rule.memory_query,
                            tags=percept.tags,
                            limit=3,
                        )
                        for memory in recalled:
                            associations[memory.memory_id] = memory
                if rule.pressure_name:
                    contribution = min(
                        1.0, rule.pressure_utility * percept.salience
                    )
                    pressure_values[rule.pressure_name] = min(
                        1.0, pressure_values[rule.pressure_name] + contribution
                    )
                    pressure_sources[rule.pressure_name].append(percept.stimulus_id)
                    pressure_reasons[rule.pressure_name].append(rule.detail)
                    consequence_parts.append(f"pressure: {rule.pressure_name}")
                micro_details.append(
                    MicroDetail(
                        detail=rule.detail,
                        confidence=min(
                            1.0, rule.confidence * percept.confidence
                        ),
                        trigger_percept_id=percept.stimulus_id,
                        consequence="; ".join(consequence_parts),
                    )
                )

        pressures = tuple(
            ActionPressure(
                name=name,
                utility=value,
                reason="; ".join(dict.fromkeys(pressure_reasons[name])),
                source_percept_ids=tuple(dict.fromkeys(pressure_sources[name])),
            )
            for name, value in sorted(
                pressure_values.items(), key=lambda item: (-item[1], item[0])
            )
        )
        experience = Experience(
            observer_id=observer.character_id,
            percept_ids=tuple(percept.stimulus_id for percept in percepts),
            focus=percepts[0].content if percepts else None,
            valence=max(-1.0, min(1.0, valence)),
            arousal=arousal,
            familiarity=max(0.0, min(1.0, familiarity)),
            memory_cues=tuple(dict.fromkeys(memory_cues)),
            associations=tuple(associations.values()),
            micro_details=tuple(micro_details),
            pressures=pressures,
        )
        if self._memory:
            self._memory.record_percepts(
                character_id=observer.character_id, percepts=percepts
            )
            self._memory.record_experience(experience)
        return experience

    @staticmethod
    def _matching_rules(
        percept: Percept, profile: SensoryProfile
    ) -> tuple[CompletionRule, ...]:
        matches = [
            rule
            for rule in profile.completion_rules
            if rule.trigger_tag in percept.tags
        ]
        # Stable ordering makes private completion reproducible for saves/replays.
        return tuple(
            sorted(
                matches,
                key=lambda rule: sha256(
                    f"{percept.stimulus_id}:{rule.trigger_tag}:{rule.detail}".encode()
                ).hexdigest(),
            )
        )

    @staticmethod
    def _mean(values: tuple[float, ...]) -> float:
        return sum(values) / len(values) if values else 0.0
