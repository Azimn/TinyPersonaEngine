"""Small deterministic demonstration."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from enum import Enum
from typing import Any

from .models import (
    CompletionRule,
    ObservationPacket,
    ObserverState,
    SensoryProfile,
    Stimulus,
    Vec3,
)
from .pipeline import FirstPersonPipeline


def _json_default(value: Any) -> Any:
    if isinstance(value, (frozenset, set, tuple)):
        return list(value)
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"cannot serialize {type(value).__name__}")


def demo() -> dict[str, Any]:
    observer = ObserverState(
        character_id="npc-ada",
        position=Vec3(0, 0, 0),
        forward=Vec3(1, 0, 0),
        goals=frozenset({"find_shelter"}),
    )
    packet = ObservationPacket(
        snapshot_id="rain-1",
        observer_id=observer.character_id,
        stimuli=(
            Stimulus(
                stimulus_id="rain-on-cuff",
                modality="touch",
                position=observer.position,
                content="Cold rain reaches the character's cuffs.",
                tags=frozenset({"cold", "rain", "wet_clothing"}),
                intensity=0.8,
                world_fact_ids=("weather:rain",),
            ),
            Stimulus(
                stimulus_id="hidden-lantern",
                modality="vision",
                position=Vec3(-5, 0, 0),
                content="A lantern burns behind the character.",
                tags=frozenset({"light"}),
                intensity=0.7,
                world_fact_ids=("lantern:lit",),
            ),
        ),
    )
    profile = SensoryProfile(
        valence_by_tag={"cold": -0.4},
        familiarity_by_tag={"rain": 0.6},
        goal_tags={"find_shelter": frozenset({"cold", "rain", "wet_clothing"})},
        completion_rules=(
            CompletionRule(
                trigger_tag="rain",
                detail="a faint iron smell",
                confidence=0.34,
                pressure_name="seek_shelter",
                pressure_utility=0.35,
                memory_query="academy courtyard rain",
            ),
        ),
    )
    return asdict(FirstPersonPipeline().process(packet, observer, profile))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("demo",), default="demo")
    parser.parse_args(argv)
    print(json.dumps(demo(), indent=2, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
