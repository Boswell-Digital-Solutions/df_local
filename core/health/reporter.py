"""DF Local Foundation — Health reporter.

Produces health responses conforming to contracts/health.schema.json.
Enforces the privacy boundary: no customer data, no table contents,
no domain metadata may appear in the response.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from ..lifecycle.manager import LifecycleManager, LifecycleState
from .service_status_reporter import build_service_status_envelope

# Load the contract schema for validation
_SCHEMA_PATH = Path(__file__).parent.parent.parent / "contracts" / "health.schema.json"


def _load_health_schema() -> dict[str, Any]:
    with open(_SCHEMA_PATH) as f:
        return json.load(f)


_HEALTH_SCHEMA: dict[str, Any] = _load_health_schema()

# Fields that must never appear in a health response.
# If any of these appear in the response dict, it is a privacy violation.
_BANNED_FIELDS = frozenset({
    "table_contents",
    "record_counts",
    "project_names",
    "manuscript_names",
    "domain_metadata",
    "query_surface",
    "table_list",
    "customer_data",
})


class HealthResponse:
    """A validated health response ready for serialization.

    Validates against the JSON schema contract before construction.
    Raises PrivacyViolationError if banned fields are detected.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        _assert_no_banned_fields(data)
        _validate_against_schema(data)
        self._data = data

    @property
    def status(self) -> str:
        return self._data["status"]

    @property
    def is_ready(self) -> bool:
        return self._data["status"] == "ready"

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def to_json(self, indent: int | None = None) -> str:
        import json
        return json.dumps(self._data, indent=indent)


class HealthReporter:
    """Produces validated health responses from lifecycle state.

    This is the only surface through which lifecycle state is serialized
    for external consumption. It enforces the privacy boundary at the
    serialization layer — not just at the data layer.
    """

    def __init__(self, lifecycle: LifecycleManager) -> None:
        self._lifecycle = lifecycle

    async def get_health(self) -> HealthResponse:
        """Return the current health response.

        Queries current lifecycle state and serializes it.
        Validates against the health schema contract.
        """
        state = await self._lifecycle.status()
        raw = state.to_health_dict()
        return HealthResponse(raw)

    @staticmethod
    def from_state(state: LifecycleState) -> HealthResponse:
        """Produce a HealthResponse directly from a LifecycleState snapshot."""
        raw = state.to_health_dict()
        return HealthResponse(raw)

    async def get_service_status(self) -> dict[str, Any]:
        """Return the current state as a Forge_Command FC-LTA-P007 envelope.

        A separate contract from `get_health()` (`forge-local-systems-runtime`'s
        accepted `service-status.schema.json`, not `contracts/health.schema.json`)
        derived from the same real lifecycle state. This is still the sole
        serialization surface -- no consumer reaches lifecycle state directly.
        """
        state = await self._lifecycle.status()
        return build_service_status_envelope(state)


class PrivacyViolationError(Exception):
    """Raised when a health response contains banned fields.

    This is a system fault, not a user error. Log as security event.
    """
    pass


def _assert_no_banned_fields(data: dict[str, Any]) -> None:
    violations = set(data.keys()) & _BANNED_FIELDS
    if violations:
        raise PrivacyViolationError(
            f"Health response contains banned fields: {sorted(violations)}. "
            "This is a privacy boundary violation and a system fault."
        )


def _validate_against_schema(data: dict[str, Any]) -> None:
    try:
        jsonschema.validate(instance=data, schema=_HEALTH_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise ValueError(f"Health response does not conform to contract schema: {exc.message}") from exc
