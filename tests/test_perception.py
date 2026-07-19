from __future__ import annotations

import pytest

from living_entity_firstperson.models import (
    ObservationPacket,
    ObserverState,
    Stimulus,
    Vec3,
)
from living_entity_firstperson.perception import (
    AttentionSelector,
    ObserverMismatch,
    PerceptionFilter,
)


def observer(**overrides):
    values = {
        "character_id": "ada",
        "position": Vec3(0, 0, 0),
        "forward": Vec3(1, 0, 0),
        "attention_capacity": 1,
    }
    values.update(overrides)
    return ObserverState(**values)


def packet(*stimuli, observer_id="ada"):
    return ObservationPacket("snapshot", observer_id, tuple(stimuli))


def stimulus(
    stimulus_id,
    *,
    modality="vision",
    position=Vec3(5, 0, 0),
    intensity=0.8,
    occluded=False,
    tags=frozenset(),
    urgent=False,
):
    return Stimulus(
        stimulus_id=stimulus_id,
        modality=modality,
        position=position,
        content=stimulus_id,
        intensity=intensity,
        occluded=occluded,
        tags=tags,
        metadata={"urgent": urgent},
    )


def test_vision_is_limited_by_orientation_and_occlusion():
    visible = stimulus("visible")
    behind = stimulus("behind", position=Vec3(-5, 0, 0))
    hidden = stimulus("hidden", occluded=True)

    result = PerceptionFilter().filter(packet(visible, behind, hidden), observer())

    assert [item.stimulus_id for item in result] == ["visible"]


def test_occluded_sound_is_attenuated_not_promoted_to_vision():
    clear = stimulus("clear", modality="sound")
    muffled = stimulus("muffled", modality="sound", occluded=True)

    result = PerceptionFilter().filter(packet(clear, muffled), observer())

    by_id = {item.stimulus_id: item for item in result}
    assert by_id["muffled"].confidence < by_id["clear"].confidence
    assert by_id["muffled"].modality == "sound"


def test_touch_is_proximal():
    near = stimulus("near", modality="touch", position=Vec3(0.5, 0, 0))
    far = stimulus("far", modality="touch", position=Vec3(2, 0, 0))

    result = PerceptionFilter().filter(packet(near, far), observer())

    assert [item.stimulus_id for item in result] == ["near"]


def test_packet_cannot_cross_private_perspectives():
    with pytest.raises(ObserverMismatch):
        PerceptionFilter().filter(packet(observer_id="barry"), observer())


def test_attention_capacity_makes_some_accessible_inputs_unnoticed():
    percepts = PerceptionFilter().filter(
        packet(
            stimulus("loud", intensity=1.0),
            stimulus("quiet", intensity=0.2),
        ),
        observer(),
    )

    attended, state = AttentionSelector().select(percepts, observer())

    assert [item.stimulus_id for item in attended] == ["loud"]
    assert state.missed_ids == ("quiet",)


def test_goal_relevance_can_redirect_attention():
    percepts = PerceptionFilter().filter(
        packet(
            stimulus("bright", intensity=0.9, tags=frozenset({"light"})),
            stimulus("door", intensity=0.7, tags=frozenset({"exit"})),
        ),
        observer(goals=frozenset({"escape"})),
    )

    attended, _ = AttentionSelector().select(
        percepts,
        observer(goals=frozenset({"escape"})),
        {"escape": frozenset({"exit"})},
    )

    assert attended[0].stimulus_id == "door"
