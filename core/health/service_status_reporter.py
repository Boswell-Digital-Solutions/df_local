"""DF Local Foundation — Forge Local Runtime service-status reporter.

Produces a `service_id: "df-local-foundation"` envelope conforming to
`forge-local-systems-runtime`'s accepted `service-status.schema.json`
(vendored at `contracts/forge_local_runtime/`), for Forge_Command's
FC-LTA-P007 (`runtime-envelope-schema-valid`).

This is a SEPARATE surface from `GET /health` (`contracts/health.schema.json`)
-- that contract is load-bearing (Forge_Command's AuthorForge operator panel
renders `schema_version`/`migration_required`/`last_error_class` from it
directly), and the two schemas cannot be merged: `service-status.schema.json`
is `additionalProperties: false` and does not define those fields. Both
surfaces are derived from the same real `LifecycleState`; neither invents a
signal the other doesn't already have.

Enforces the same privacy boundary as `reporter.py`: no customer data, no
table contents, no domain metadata.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import jsonschema

from ..lifecycle.manager import ErrorClass, LifecycleState, LifecycleStatus

_SCHEMA_PATH = (
    Path(__file__).parent.parent.parent / "contracts" / "forge_local_runtime" / "service-status.schema.json"
)


def _load_service_status_schema() -> dict[str, Any]:
    with open(_SCHEMA_PATH) as f:
        return json.load(f)


_SERVICE_STATUS_SCHEMA: dict[str, Any] = _load_service_status_schema()

SERVICE_ID = "df-local-foundation"
SERVICE_CLASS = "substrate"

# Same banned-fields boundary as reporter.py -- this surface must never carry
# customer data, table contents, or domain metadata either.
_BANNED_FIELDS = frozenset(
    {
        "table_contents",
        "record_counts",
        "project_names",
        "manuscript_names",
        "domain_metadata",
        "query_surface",
        "table_list",
        "customer_data",
    }
)

# LifecycleStatus.MIGRATING means "another process holds the migration
# advisory lock" (_locked_check_and_migrate) -- this instance is blocked
# waiting for that other migration, not failing. "migration_blocked" is the
# accepted degraded_subtype that honestly names this, not a generic fallback.
_MIGRATING_SUBTYPE = "migration_blocked"


def _state_and_subtype(status: LifecycleStatus) -> tuple[str, str | None]:
    """Map LifecycleStatus (this repo's own vocabulary) to the accepted
    schema's `state` (+ `degraded_subtype` when state == "degraded"). Never
    invents a status this repo doesn't already report on `/health`."""
    if status == LifecycleStatus.READY:
        return "ready", None
    if status == LifecycleStatus.UNAVAILABLE:
        return "unavailable", None
    if status == LifecycleStatus.MIGRATING:
        return "degraded", _MIGRATING_SUBTYPE
    if status == LifecycleStatus.DEGRADED:
        return "degraded", "degraded"
    raise ValueError(f"Unmapped LifecycleStatus: {status!r}")


def _readiness_class_for(state: str) -> str:
    if state == "ready":
        return "ready"
    if state == "degraded":
        return "degraded"
    return "not_ready"


def _operator_message(state: LifecycleState, mapped_state: str, subtype: str | None) -> str:
    if mapped_state == "ready":
        return f"Database ready; schema version {state.schema_version} matches expected {state.expected_schema_version}."
    if subtype == _MIGRATING_SUBTYPE:
        return "Migration in progress by another process; waiting for the migration lock."
    if state.last_error_class == ErrorClass.CONNECTION_FAILURE:
        return "Database connection unavailable."
    if state.last_error_class == ErrorClass.MIGRATION_FAILURE:
        return "Migration version check failed; database unavailable."
    if mapped_state == "unavailable":
        return "Database unavailable."
    return "Database degraded."


class ServiceStatusReportError(Exception):
    """Raised when a service-status envelope fails schema or privacy validation.

    A system fault, not a user error -- the envelope must never ship
    non-conforming or privacy-violating data.
    """


def _assert_no_banned_fields(data: dict[str, Any]) -> None:
    violations = set(data.keys()) & _BANNED_FIELDS
    if violations:
        raise ServiceStatusReportError(
            f"service-status response contains banned fields: {sorted(violations)}. "
            "This is a privacy boundary violation and a system fault."
        )


def build_service_status_envelope(state: LifecycleState) -> dict[str, Any]:
    """Build and validate a service-status envelope from a real LifecycleState.

    Raises ServiceStatusReportError if the built envelope fails schema or
    privacy validation -- never ships a non-conforming or unsafe envelope.
    """
    mapped_state, subtype = _state_and_subtype(state.status)
    readiness_class = _readiness_class_for(mapped_state)
    message = _operator_message(state, mapped_state, subtype)

    envelope: dict[str, Any] = {
        "service_id": SERVICE_ID,
        "service_class": SERVICE_CLASS,
        "state": mapped_state,
        "operator_visible_message": message,
        "readiness_summary": {
            "readiness_class": readiness_class,
            "summary": message,
        },
        # `status()` re-checks migration state on every call (never caches
        # stale status as ready) -- "now" is the honest observation time,
        # not this process's boot time.
        "last_updated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if subtype is not None:
        envelope["degraded_subtype"] = subtype

    _assert_no_banned_fields(envelope)
    try:
        jsonschema.validate(instance=envelope, schema=_SERVICE_STATUS_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise ServiceStatusReportError(
            f"service-status envelope does not conform to the accepted schema: {exc.message}"
        ) from exc
    return envelope
