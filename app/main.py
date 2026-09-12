"""DF Local Foundation — read-only HTTP health API.

A thin ASGI surface over the existing lifecycle/health layer. It serves ONLY the declared
control-plane health surface (contracts/health.schema.json) — never customer data, table
contents, or domain metadata. The foundation is the sole process that touches its own
database; this endpoint lets control-plane consumers (e.g. ForgeCommand) read coarse health
without any direct database access of their own.

Endpoints:
  GET /live                     Process liveness (never touches the database).
  GET /health                   Database-aware foundation health (DFLocalHealthStatus contract).
  GET /health/service-status    Forge_Command FC-LTA-P007 envelope (forge-local-systems-runtime's
                                 accepted service-status contract). A separate surface from
                                 /health: that contract is load-bearing elsewhere and cannot carry
                                 this one's fields (additionalProperties: false on both sides).
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request

from core.config.settings import FOUNDATION_VERSION, load_settings
from core.health.reporter import HealthReporter
from core.lifecycle.manager import LifecycleManager, LifecycleStartError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Connect the lifecycle once at startup; fail closed (not crash) if the database is down.

    A connection failure is caught here so `/health` can honestly report `unavailable` rather
    than the process failing to boot. Configuration errors (invalid settings) remain a hard stop.
    """
    settings = load_settings()
    lifecycle = LifecycleManager(settings)
    try:
        await lifecycle.start()
    except LifecycleStartError as exc:
        logger.warning("df_local.api.start_degraded error_class=%s", exc.error_class.value)
    app.state.lifecycle = lifecycle
    app.state.reporter = HealthReporter(lifecycle)
    try:
        yield
    finally:
        await lifecycle.stop()


def get_reporter(request: Request) -> HealthReporter:
    """Resolve the request-scoped health reporter. Overridable in tests."""
    return request.app.state.reporter


def create_app(
    lifespan_factory: Callable[[FastAPI], AbstractAsyncContextManager[None]] = lifespan,
) -> FastAPI:
    """Build the FastAPI app. `lifespan_factory` is injectable so tests can avoid the database."""
    app = FastAPI(
        title="DF Local Foundation",
        version=FOUNDATION_VERSION,
        summary="Read-only control-plane health surface. No customer or domain data is exposed.",
        lifespan=lifespan_factory,
    )

    @app.get("/live")
    async def live() -> dict[str, Any]:
        # Pure process liveness — deliberately does not touch the database.
        return {"service": "df-local-foundation", "version": FOUNDATION_VERSION, "status": "live"}

    @app.get("/health")
    async def health(reporter: Annotated[HealthReporter, Depends(get_reporter)]) -> dict[str, Any]:
        # DB-aware foundation health, validated against contracts/health.schema.json by the reporter.
        response = await reporter.get_health()
        return response.to_dict()

    @app.get("/health/service-status")
    async def service_status(reporter: Annotated[HealthReporter, Depends(get_reporter)]) -> dict[str, Any]:
        # Forge_Command FC-LTA-P007 envelope, validated against
        # contracts/forge_local_runtime/service-status.schema.json by the reporter.
        # Separate from /health -- see the module docstring.
        return await reporter.get_service_status()

    return app


app = create_app()
