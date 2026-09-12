"""FC-LTA-P007 service-status API tests.

Mirrors test_health_api.py's pattern: a no-op lifespan plus a stub reporter,
hermetic but flowing through the real HealthReporter.get_service_status() so
the accepted-schema validation and privacy boundary are genuinely exercised.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app, get_reporter
from core.config.settings import AppMode
from core.lifecycle.manager import ErrorClass, LifecycleState, LifecycleStatus

BANNED_FIELDS = {
    "table_contents",
    "record_counts",
    "project_names",
    "manuscript_names",
    "domain_metadata",
    "query_surface",
    "table_list",
    "customer_data",
}


@asynccontextmanager
async def _noop_lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield


def _state(status: LifecycleStatus, **overrides: object) -> LifecycleState:
    base: dict[str, object] = {
        "status": status,
        "schema_version": "0002",
        "expected_schema_version": "0002",
        "migration_required": False,
        "started_at": datetime.now(UTC),
        "app_mode": AppMode.LOCAL,
    }
    base.update(overrides)
    return LifecycleState(**base)  # type: ignore[arg-type]


def _client(status: LifecycleStatus, **overrides: object) -> TestClient:
    app = create_app(lifespan_factory=_noop_lifespan)
    state = _state(status, **overrides)

    class _StubReporter:
        async def get_service_status(self) -> object:
            from core.health.service_status_reporter import build_service_status_envelope

            return build_service_status_envelope(state)

    app.dependency_overrides[get_reporter] = lambda: _StubReporter()
    return TestClient(app)


def test_service_status_reports_ready() -> None:
    res = _client(LifecycleStatus.READY).get("/health/service-status")
    assert res.status_code == 200
    body = res.json()
    assert body["service_id"] == "df-local-foundation"
    assert body["service_class"] == "substrate"
    assert body["state"] == "ready"
    assert "degraded_subtype" not in body
    assert body["readiness_summary"]["readiness_class"] == "ready"


def test_service_status_reports_degraded_migration_blocked_when_lock_contended() -> None:
    res = _client(
        LifecycleStatus.MIGRATING,
        schema_version="unknown",
        migration_required=True,
    ).get("/health/service-status")
    assert res.status_code == 200
    body = res.json()
    assert body["state"] == "degraded"
    assert body["degraded_subtype"] == "migration_blocked"
    assert body["readiness_summary"]["readiness_class"] == "degraded"


def test_service_status_reports_unavailable_when_db_down() -> None:
    res = _client(
        LifecycleStatus.UNAVAILABLE,
        schema_version="unknown",
        migration_required=True,
        last_error_class=ErrorClass.CONNECTION_FAILURE,
    ).get("/health/service-status")
    assert res.status_code == 200
    body = res.json()
    assert body["state"] == "unavailable"
    assert "degraded_subtype" not in body
    assert body["readiness_summary"]["readiness_class"] == "not_ready"


@pytest.mark.parametrize("status", list(LifecycleStatus))
def test_service_status_never_leaks_domain_fields(status: LifecycleStatus) -> None:
    extra = (
        {"schema_version": "unknown", "migration_required": True}
        if status is LifecycleStatus.UNAVAILABLE
        else {}
    )
    res = _client(status, **extra).get("/health/service-status")
    assert res.status_code == 200
    assert BANNED_FIELDS.isdisjoint(res.json().keys())


def test_service_status_never_carries_the_legacy_health_fields() -> None:
    # additionalProperties: false on the accepted schema -- this must never
    # carry schema_version/expected_schema_version/migration_required/
    # last_error_class/db_engine/ownership/app_mode, the /health-only fields.
    res = _client(LifecycleStatus.READY).get("/health/service-status")
    body = res.json()
    legacy_only_fields = {
        "schema_version",
        "expected_schema_version",
        "migration_required",
        "last_error_class",
        "db_engine",
        "ownership",
        "app_mode",
    }
    assert legacy_only_fields.isdisjoint(body.keys())
