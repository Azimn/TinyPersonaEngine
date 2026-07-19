"""Bounded structured actions; freeform commands never reach the game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .models import StructuredAction


class ActionValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    kind: type
    required: bool = True
    choices: frozenset[Any] | None = None
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True, slots=True)
class ActionSpec:
    name: str
    parameters: Mapping[str, ParameterSpec] = field(default_factory=dict)
    minimum_utility: float = 0.0


@dataclass(slots=True)
class ActionRegistry:
    _specs: dict[str, ActionSpec] = field(default_factory=dict)

    def register(self, spec: ActionSpec) -> None:
        if not spec.name:
            raise ValueError("action name is required")
        self._specs[spec.name] = spec

    def validate(self, action: StructuredAction) -> StructuredAction:
        spec = self._specs.get(action.name)
        if spec is None:
            raise ActionValidationError(f"unknown action {action.name!r}")
        if action.utility < spec.minimum_utility:
            raise ActionValidationError(
                f"{action.name!r} requires utility >= {spec.minimum_utility}"
            )
        unknown = set(action.parameters).difference(spec.parameters)
        if unknown:
            raise ActionValidationError(
                f"unknown parameters for {action.name!r}: {sorted(unknown)}"
            )
        for name, parameter in spec.parameters.items():
            if name not in action.parameters:
                if parameter.required:
                    raise ActionValidationError(f"missing required parameter {name!r}")
                continue
            value = action.parameters[name]
            if not isinstance(value, parameter.kind):
                raise ActionValidationError(
                    f"{name!r} must be {parameter.kind.__name__}"
                )
            if parameter.choices is not None and value not in parameter.choices:
                raise ActionValidationError(f"{name!r} is outside allowed choices")
            if parameter.minimum is not None and value < parameter.minimum:
                raise ActionValidationError(f"{name!r} is below minimum")
            if parameter.maximum is not None and value > parameter.maximum:
                raise ActionValidationError(f"{name!r} is above maximum")
        return action
