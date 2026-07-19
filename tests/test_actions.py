from __future__ import annotations

import pytest

from living_entity_firstperson.actions import (
    ActionRegistry,
    ActionSpec,
    ActionValidationError,
    ParameterSpec,
)
from living_entity_firstperson.models import StructuredAction


def registry():
    result = ActionRegistry()
    result.register(
        ActionSpec(
            "move",
            {
                "destination": ParameterSpec(str),
                "speed": ParameterSpec(float, minimum=0.0, maximum=1.0),
            },
            minimum_utility=0.2,
        )
    )
    return result


def test_known_bounded_action_is_accepted():
    action = StructuredAction(
        "move",
        {"destination": "shelter", "speed": 0.5},
        0.6,
        "seek_shelter",
    )
    assert registry().validate(action) is action


@pytest.mark.parametrize(
    "action",
    [
        StructuredAction("rewrite_world", {}, 1.0, "curiosity"),
        StructuredAction(
            "move",
            {"destination": "shelter", "speed": 2.0},
            0.8,
            "seek_shelter",
        ),
        StructuredAction(
            "move",
            {"destination": "shelter", "speed": 0.5, "quest_state": "done"},
            0.8,
            "seek_shelter",
        ),
        StructuredAction(
            "move",
            {"destination": "shelter", "speed": 0.5},
            0.1,
            "seek_shelter",
        ),
    ],
)
def test_unbounded_or_malformed_actions_are_rejected(action):
    with pytest.raises(ActionValidationError):
        registry().validate(action)
