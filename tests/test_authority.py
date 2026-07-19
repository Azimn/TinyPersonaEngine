from __future__ import annotations

import pytest

from living_entity_firstperson.authority import (
    AuthoritativeFact,
    Authority,
    AuthorityViolation,
    WorldLedger,
)
from living_entity_firstperson.models import Belief


def test_world_ledger_accepts_world_facts_and_keeps_history():
    ledger = WorldLedger()
    ledger.record(AuthoritativeFact("1", "door", "locked", "game"))
    ledger.record(AuthoritativeFact("2", "door", "unlocked", "game"))

    assert ledger.current["door"].value == "unlocked"
    assert [fact.value for fact in ledger.history] == ["locked", "unlocked"]


@pytest.mark.parametrize(
    "authority",
    [Authority.PERCEPTION, Authority.BELIEF, Authority.EXPERIENCE, Authority.SUBJECTIVE_COMPLETION],
)
def test_private_records_cannot_write_world_facts(authority):
    with pytest.raises(AuthorityViolation):
        WorldLedger().propose_private(
            authority=authority,
            key="door",
            value="unlocked",
            source="private",
        )


def test_belief_requires_perception_provenance():
    with pytest.raises(ValueError):
        Belief(
            belief_id="belief-1",
            observer_id="ada",
            content="I think the door is unlocked.",
            confidence=0.5,
            source_percept_ids=(),
        )


def test_heard_testimony_is_not_a_world_fact():
    belief = Belief(
        belief_id="belief-1",
        observer_id="ada",
        content="I think the door is unlocked.",
        confidence=0.5,
        source_percept_ids=("heard-jay-1",),
    )
    assert belief.authority is Authority.BELIEF
    assert belief.source_percept_ids == ("heard-jay-1",)
