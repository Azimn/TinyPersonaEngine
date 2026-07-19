# Repository-first reuse map

Research was performed against the upstream repositories on 2026-07-19. This
package is a clean-room implementation: no third-party source was copied.

| Project | Pattern evaluated | Decision | Upstream license signal |
|---|---|---|---|
| [SkyrimNet](https://github.com/MinLL/SkyrimNet-GamePlugin) | Spatially plausible NPC perception and private per-NPC memory | Adopt the first-person boundary as a clean-room contract; no source reuse | GitHub did not report an SPDX license |
| [Sonorus](https://github.com/KevinAHM/sonorus) | Per-NPC perspective, private graph memory, contextual recall | Keep memory character-scoped and context-addressed; no source reuse | GitHub did not report an SPDX license |
| [Ori Mnemos](https://github.com/aayoawoyemi/Ori-Mnemos) | ACT-R-inspired decay, spreading activation, Hebbian co-occurrence | Expose a memory port; do not recreate these algorithms here | Apache-2.0 |
| [Remnic](https://github.com/joshuaswarren/remnic) | Scoped hybrid retrieval, provenance, correction, boundaries, lifecycle | Shape `MemoryPort` around scope, provenance, and derived-from data | MIT |
| [Memoria](https://github.com/matrixorigin/Memoria) | Snapshots, branches, rollback, quarantine, hybrid search | Leave versioning/rollback behind the memory port | Apache-2.0 |
| [MetaDrive](https://github.com/metadriverse/metadrive) | Pluggable sensor/observation types separated from environment truth | Use a modality-neutral `ObservationPacket` and source protocol | Apache-2.0 |
| [Greta](https://github.com/isir/greta) | Modular nonverbal socio-emotional behavior realization | Define expression cues/port only; copy no GPL code | GPL-3.0 on current `master`; historical `master-lgpl` exists |
| [Gigax](https://github.com/GigaxGames/gigax) | Schema-constrained NPC action generation | Validate named actions and typed parameters through a registry | GitHub did not report an SPDX license |

## Why these projects are not dependencies

The upstream systems span Papyrus, Python, TypeScript, Rust, and Java and solve
substantially larger problems. Making them hard runtime dependencies would
destroy the small integration-layer thesis. The package instead defines ports
that can be implemented against a selected memory, sensor, or expression system.

Repositories for which GitHub reported no SPDX license were treated as
all-rights-reserved for code-reuse purposes. Only high-level behavior visible in
public documentation informed the clean-room interfaces.
