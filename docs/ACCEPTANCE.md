# Acceptance criteria and unproven claims

## Automated acceptance criteria

The bundled suite verifies:

- a visual stimulus outside field of view is not perceived;
- an occluded visual stimulus is not perceived;
- an occluded sound may be heard with reduced confidence;
- a proximal sensation is unavailable at a distance;
- packets cannot cross character perspectives;
- attention retains only the configured number of percepts;
- goal-relevant input can redirect attention;
- heard testimony remains a perception rather than a world fact;
- beliefs require perception provenance;
- subjective completions carry private authority;
- every completion has a memory or pressure consequence;
- the same observation can produce different experience under different
  character profiles;
- private memories never leak across character IDs;
- the world ledger rejects belief, experience, and completion writes;
- unknown or malformed actions never reach the game adapter;
- the pipeline is deterministic for identical state and input.

These tests establish software behavior, not player experience.

## Experiential acceptance study

Before claiming improved NPC quality, compare the same model and encounters:

1. strong persona + recent dialogue + concise relationship + retrieved memory;
2. condition 1 plus spatially limited observations;
3. condition 2 plus bounded attention;
4. condition 3 plus subjective transduction;
5. condition 4 plus persistent private memory and bounded actions.

Blind transcript/video labels and keep prompt/token budgets comparable. Evaluate:

- whether observers can infer where the NPC was and what it could access;
- whether observers can identify what it noticed and missed;
- whether two characters react differently for legible reasons;
- whether a private sensory detail causes later memory or behavior;
- whether false omniscience decreases;
- whether interaction quality, latency, or repetition degrades;
- whether the full system beats the strong baseline.

Pre-register removal criteria. A layer that does not create a reliable,
user-perceptible benefit should not be retained merely because its internal
state is elegant.

## Claims that remain unproven

This release does **not** claim:

- consciousness, continuous mentality, or a cognitive architecture;
- human-like attention, affect, perception, or autobiographical memory;
- greater aliveness, immersion, voice quality, or emotional coherence;
- superiority to a strong persona-and-memory baseline;
- robust semantic truth verification;
- a sensory simulation beyond authored/private completion rules;
- production performance inside a particular game engine;
- compatibility with the named external projects without an adapter project.

The package provides boundaries and deterministic mechanisms with which those
claims can be tested.
