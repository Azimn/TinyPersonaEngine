# Architecture and authority contract

## Scope

The package is an event-driven bridge between a game engine's candidate sensor
data and one character's private first-person frame. It is intentionally small
enough to embed beside an existing game, companion platform, or language-model
runtime.

## Stages

1. **Observation adapter** supplies a packet addressed to one character.
2. **Perceptual access** applies range, field of view, occlusion, modality, and
   embodiment sensitivity.
3. **Attention** ranks accessible percepts and retains only the character's
   configured capacity.
4. **Subjective transduction** computes appraisal, stable procedural
   completions, memory cues, and utility-like pressures.
5. **Memory port** stores first-person records and recalls only within the
   character's scope.
6. **Action registry** validates action names and parameters before an engine
   may execute them.
7. **Expression port** carries nonverbal cues to an external behavior realizer.

There is no frame loop or hidden background inference. The host calls
`FirstPersonPipeline.process()` when an observation event warrants processing.

## Authority matrix

| Type | Created by | May become a world fact automatically? |
|---|---|---|
| `world_fact` | Authoritative game adapter | Already canonical |
| `perception` | Spatial/sensory filter | No |
| `belief` | Character cognition | No |
| `experience` | Subjective transducer | No |
| `subjective_completion` | Authored completion rule | No |

`WorldLedger` accepts only `AuthoritativeFact` records carrying
`Authority.WORLD_FACT`. It stores current values and a complete in-process
history. It does not perform semantic contradiction detection, temporal
reasoning, or entity resolution and is documented as a ledger rather than a
world model.

## Objective occlusion

The host engine owns raycasts and portal/room topology. The packet carries the
result as `Stimulus.occluded`. This library does not infer geometry from prose.
For vision, occlusion blocks access. For hearing and smell it attenuates access,
which lets the host represent a muffled sound or partially blocked odor.

## Subjective completion

A `CompletionRule` is authored content, not a model hallucination. It:

- triggers only from an attended tag;
- is marked `subjective_completion`;
- is reproducible for the same percept;
- must create an action pressure, a memory query, or both;
- never exposes a world-write method.

This rule prevents attractive but causally inert sensory prose from accumulating
in prompts or memory.

## Memory

`MemoryPort` is a port rather than an embedded retrieval system. Production
adapters may provide semantic/full-text hybrid retrieval, ACT-R-like activation,
provenance, lifecycle, snapshots, quarantine, and rollback.

The reference in-memory adapter is intentionally limited to exact tag
intersection. It exists for tests, demos, and integration bring-up. It does not
claim semantic equivalence, human memory, or robust verification.

## Actions and expression

Private pressure is not an executable command. A model, utility selector, or
authored policy may turn pressure into a `StructuredAction`, but
`ActionRegistry` rejects unknown actions, unknown parameters, wrong parameter
types, out-of-range values, and actions below a configured utility threshold.

Nonverbal realization is similarly external. `ExpressionPort` and
`ExpressionCue` define a small integration boundary without copying Greta or
binding this package to its license or Java runtime.
