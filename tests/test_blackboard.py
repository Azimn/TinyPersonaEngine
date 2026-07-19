from __future__ import annotations

from living_entity_firstperson.blackboard import PerspectiveBlackboard
from living_entity_firstperson.models import (
    Experience,
    FirstPersonFrame,
    AttentionState,
)


def frame(observer_id, snapshot_id):
    return FirstPersonFrame(
        snapshot_id=snapshot_id,
        observer_id=observer_id,
        perceivable=(),
        attention=AttentionState((), (), None),
        experience=Experience(
            observer_id=observer_id,
            percept_ids=(),
            focus=None,
            valence=0.0,
            arousal=0.0,
            familiarity=0.0,
            memory_cues=(),
            associations=(),
            micro_details=(),
            pressures=(),
        ),
    )


def test_blackboard_is_bounded_and_private_per_character():
    board = PerspectiveBlackboard(capacity=2)
    board.update(frame("ada", "a1"))
    board.update(frame("ada", "a2"))
    board.update(frame("ada", "a3"))
    board.update(frame("barry", "b1"))

    assert [item.snapshot_id for item in board.history("ada")] == ["a2", "a3"]
    assert board.latest("barry").snapshot_id == "b1"
    assert board.latest("missing") is None
