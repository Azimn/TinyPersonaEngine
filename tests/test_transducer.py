from __future__ import annotations

import pytest

from living_entity_firstperson.authority import Authority
from living_entity_firstperson.memory import InMemoryPerspectiveMemory, MemoryItem
from living_entity_firstperson.models import (
    CompletionRule,
    ObservationPacket,
    ObserverState,
    SensoryProfile,
    Stimulus,
    Vec3,
)
from living_entity_firstperson.pipeline import FirstPersonPipeline


def observer(character_id="ada"):
    return ObserverState(
        character_id=character_id,
        position=Vec3(0, 0, 0),
        forward=Vec3(1, 0, 0),
    )


def rain_packet(character_id="ada"):
    return ObservationPacket(
        "rain-1",
        character_id,
        (
            Stimulus(
                "rain-cuff",
                "touch",
                Vec3(0, 0, 0),
                "Cold water reaches the cuffs.",
                frozenset({"rain", "cold"}),
                0.8,
                ("weather:rain",),
            ),
        ),
    )


def rain_profile(valence=-0.4):
    return SensoryProfile(
        valence_by_tag={"cold": valence},
        familiarity_by_tag={"rain": 0.6},
        completion_rules=(
            CompletionRule(
                trigger_tag="rain",
                detail="a faint iron smell",
                confidence=0.5,
                pressure_name="seek_shelter",
                pressure_utility=0.4,
                memory_query="academy rain",
            ),
        ),
    )


def test_completion_must_have_a_consequence():
    with pytest.raises(ValueError):
        CompletionRule(
            trigger_tag="rain",
            detail="pretty droplets",
            confidence=0.5,
        )


def test_subjective_completion_remains_private_and_consequential():
    frame = FirstPersonPipeline().process(
        rain_packet(), observer(), rain_profile()
    )

    detail = frame.experience.micro_details[0]
    assert detail.authority is Authority.SUBJECTIVE_COMPLETION
    assert "pressure: seek_shelter" in detail.consequence
    assert frame.experience.memory_cues == ("academy rain",)
    assert frame.experience.pressures[0].name == "seek_shelter"
    assert frame.experience.pressures[0].utility > 0


def test_same_world_observation_can_be_experienced_differently():
    disliked = FirstPersonPipeline().process(
        rain_packet(), observer(), rain_profile(-0.8)
    )
    welcomed = FirstPersonPipeline().process(
        rain_packet(), observer(), rain_profile(0.5)
    )

    assert disliked.perceivable == welcomed.perceivable
    assert disliked.experience.valence < welcomed.experience.valence


def test_memory_recall_is_scoped_to_character():
    memory = InMemoryPerspectiveMemory()
    memory.add(
        MemoryItem(
            "ada-rain",
            "ada",
            "The academy courtyard in rain.",
            frozenset({"rain"}),
            ("event:old-rain",),
        )
    )
    memory.add(
        MemoryItem(
            "barry-rain",
            "barry",
            "A different person's rain memory.",
            frozenset({"rain"}),
            ("event:other-rain",),
        )
    )

    frame = FirstPersonPipeline(memory=memory).process(
        rain_packet("ada"), observer("ada"), rain_profile()
    )

    assert [item.memory_id for item in frame.experience.associations] == ["ada-rain"]
    assert "barry" not in memory.recorded_percepts


def test_pipeline_is_deterministic_for_same_input():
    pipeline = FirstPersonPipeline()
    first = pipeline.process(rain_packet(), observer(), rain_profile())
    second = pipeline.process(rain_packet(), observer(), rain_profile())

    assert first == second
