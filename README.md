# Living Entity: First-Person Bridge

This package converts authoritative game observations into a limited, private,
and consequential first-person frame for one character.

It implements this narrow pipeline:

```text
candidate observations
-> character-relative perceptual access
-> bounded attention
-> subjective experience
-> memory cues and action pressures
-> validated action proposals
```

The package deliberately does **not** implement a world simulation, language
model, semantic memory database, continuous mind, or proof that players find a
character more alive. Those are external systems or unproven product claims.

## Why the boundaries matter

The following records are different and cannot be silently promoted:

| Record | Example | Authority |
|---|---|---|
| World fact | The door is unlocked. | Game/world adapter only |
| Perception | I heard Jay say the door was unlocked. | Perception pipeline |
| Belief | I think the door is unlocked. | Character cognition |
| Experience | His certainty makes me less cautious. | Subjective transducer |
| Completion | The room has a faint iron smell. | Private, non-canonical texture |

`WorldLedger` rejects every record that is not explicitly marked
`world_fact`. A subjective completion can influence private pressure or cue
memory, but it cannot change collision, inventory, quest state, or objective
history.

## Quick example

```python
from living_entity_firstperson import (
    CompletionRule,
    FirstPersonPipeline,
    ObservationPacket,
    ObserverState,
    SensoryProfile,
    Stimulus,
    Vec3,
)

observer = ObserverState(
    character_id="npc-ada",
    position=Vec3(0, 0, 0),
    forward=Vec3(1, 0, 0),
    goals=frozenset({"find_shelter"}),
)
packet = ObservationPacket(
    snapshot_id="rain-1",
    observer_id="npc-ada",
    stimuli=(
        Stimulus(
            stimulus_id="rain-on-cuff",
            modality="touch",
            position=Vec3(0, 0, 0),
            content="Cold rain reaches the character's cuffs.",
            tags=frozenset({"cold", "rain", "wet_clothing"}),
            intensity=0.8,
            world_fact_ids=("weather:rain",),
        ),
    ),
)
profile = SensoryProfile(
    valence_by_tag={"cold": -0.4},
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

frame = FirstPersonPipeline().process(packet, observer, profile)
print(frame.experience)
```

Run the deterministic demonstration:

```text
living-entity-firstperson demo
```

## Integration points

- `ObservationSource` accepts game-specific sensor adapters.
- `MemoryPort` keeps semantic retrieval, lifecycle, provenance, and rollback in
  an external memory service.
- `PerspectiveBlackboard` holds a bounded per-character working history without
  masquerading as durable memory.
- `ActionRegistry` validates bounded game actions before an engine sees them.
- `ExpressionPort` accepts structured gaze, posture, gesture, and facial cues.

The bundled `InMemoryPerspectiveMemory` is intentionally a test/reference
backend. It performs exact tag-scoped recall, not semantic search, and makes no
cognitive claims.

See [ARCHITECTURE.md](docs/ARCHITECTURE.md),
[ACCEPTANCE.md](docs/ACCEPTANCE.md), and
[REUSE_MAP.md](docs/REUSE_MAP.md).

## Current evidence

Automated tests establish boundary and deterministic behavior: spatial access,
occlusion, attention capacity, private scoping, completion provenance,
consequence requirements, world-ledger rejection, and action validation.

They do not establish improved character quality, aliveness, immersion,
emotional realism, or superiority to a strong persona-plus-memory baseline.
Those remain evaluation questions.
