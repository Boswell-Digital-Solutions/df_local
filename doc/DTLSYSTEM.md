# df-local-foundation — System Documentation

**Document version:** 1.1 — 2026-09-24 registered as `dtl` (was an unregistered `DFL`, colliding with `apps/public-app-local-support/forge-df-local-foundation`; see `PREFIX_REGISTRY.md` Migration History)
**Designation:** dtl
**Source:** `doc/system/`
**Build command:** `bash doc/system/BUILD.sh`
**Protocol:** BDS Documentation Protocol v2.0
**Documentation structure class:** `documentation`

> **Generated artifact warning:** `doc/DTLSYSTEM.md` is assembled output. Edit
> the source modules under `doc/system/` and rebuild. Hand edits to generated
> artifacts are overwritten by the next build.

This `doc/system/` tree is the canonical source of truth for df_local. It
uses explicit **truth classes**: canonical facts define role, authority
boundaries, and security invariants; snapshot facts are dated, audit-derived
observations. Chapters are assembled into a designation-bound canonical
artifact.

Assembly contract:

- Command: `bash doc/system/BUILD.sh`
- Validation: `bash doc/system/validate_snapshots.sh` runs during assembly
- Primary output: `doc/DTLSYSTEM.md`

| Part | File | Contents |
| --- | --- | --- |
| §1 | `00-overview.md` | System identity, role, and boundary with the rest of the Forge ecosystem. |
| §2 | `01-architecture.md` | High-level architecture, authority posture, and surface ownership. |
| §3 | `10-scope.md` | Scope and authority boundary of this documentation system. |
| §4 | `20-structure.md` | Module/chapter layout and cross-reference rules. |
| §5 | `30-governance.md` | Ownership, review, and change-authority boundaries. |
| §6 | `40-change-control.md` | Change-control workflow, proposal lifecycle, and audit. |
| §7 | `90-appendices.md` | Appendices, glossary, and cross-references. |

## Quick Assembly

```bash
bash doc/system/BUILD.sh
```

---

# Overview

**Document version:** 1.0 (bootstrap scaffold)

System identity, role, and boundary with the rest of the Forge ecosystem.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

# Architecture

**Document version:** 1.0 (bootstrap scaffold)

High-level architecture, authority posture, and surface ownership.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

## 1. Overview & Philosophy

DF Local Foundation is currently documented through a baseline protocol-adoption pass.
This section records only repository surfaces directly observable from the working tree.

### 1.1 Current Posture

| Topic | Current truth |
| --- | --- |
| Repo | `df-local-foundation` |
| Protocol status | Baseline adoption in progress |
| Canonical technical reference | `doc/system/` plus generated root `SYSTEM.md` |
| Current scope | Expand this section as product and service boundaries are cataloged |

---

## 2. Architecture

This baseline architecture section records the major repo surfaces present today.

### 2.1 Observed Top-Level Areas

```text
df-local-foundation/
├── contracts/
├── core/
├── doc/
├── docs/
├── sql/
├── tests/
├── tools/
```

---

## 3. Tech Stack

This baseline stack inventory is inferred from repository markers and directory layout.

### 3.1 Stack

| Layer | Technology |
| --- | --- |
| Language | Python ≥ 3.11 |
| Database driver | `asyncpg` (PostgreSQL) |
| Config / validation | `pydantic` v2 + `pydantic-settings`; `jsonschema` for contract validation |
| HTTP health API (optional, `app/`) | `fastapi` + `uvicorn` — install via `".[api]"` |
| Tests / lint / types | `pytest` + `pytest-asyncio`, `ruff`, `mypy` (dev extra) |

The core library and CLI tools require only the base dependencies; FastAPI/uvicorn are an optional
extra needed solely to run the health API (`python -m app`).

---

## 4. Project Structure

### 4.1 Directory Layout

```text
df-local-foundation/
├── app/          # read-only HTTP health API (FastAPI; see §8)
├── contracts/    # JSON Schema contracts (health, migration-status, app-registration)
├── core/         # lifecycle, health reporter, config, backup/export
├── doc/
├── docs/
├── sql/          # core.* migrations + per-app attach (sql/apps/<app>)
├── tests/
├── tools/        # db-status / db-backup / db-export / db-restore CLIs
```

### 4.2 Documentation Rule

- `doc/system/` is the canonical modular source for the root `SYSTEM.md`
- `scripts/context-bundle.sh` is the selective context assembly surface
- `CLAUDE.md` is the repo-local AI instruction file

---

## 5. Configuration & Environment

Configuration is the canonical contract in `core/config/settings.py` (`FoundationSettings`,
pydantic-settings). All attaching apps must use these env variable names — do not invent
alternatives. Config is a hard-fail surface: invalid combinations raise on construction
(fail-closed), and the `prod-local` profile forbids default credentials and wildcard host binds.

### 5.1 Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `DF_LOCAL_HOST` | `127.0.0.1` | PostgreSQL host. |
| `DF_LOCAL_PORT` | `5432` | PostgreSQL port. |
| `DF_LOCAL_DB` | _(required)_ | Database name. |
| `DF_LOCAL_USER` | _(required)_ | Database user. |
| `DF_LOCAL_PASSWORD` | _(required)_ | Database password. |
| `DF_LOCAL_DATA_DIR` | `/var/lib/df-local` | Data directory. |
| `DF_LOCAL_APP_ID` | _(required)_ | Owning app identifier (must not be `core`). |
| `DF_LOCAL_APP_MODE` | `local` | `local` \| `hybrid` \| `cloud-enabled`. |
| `DF_LOCAL_PROFILE` | `dev` | `dev` \| `test` \| `prod-local` (strict rules in prod-local). |
| `DF_LOCAL_API_HOST` | `127.0.0.1` | Bind host for the read-only health API (`app/`, §8). |
| `DF_LOCAL_API_PORT` | `8099` | Bind port for the health API. |

### 5.2 Notes

- `DF_LOCAL_API_HOST` / `DF_LOCAL_API_PORT` are consumed by `python -m app` (the health API).
  They are part of the canonical settings contract so the API surface is configured the same way
  as the rest of the foundation; `prod-local` host-binding rules apply to `DF_LOCAL_HOST`.
- Connection strings are derived in `FoundationSettings` (`connection_string` /
  `async_connection_string`); apps and tools must not assemble their own.

---

## 6. Design System

This section is a placeholder unless a UI surface is present in the current repo.

### 6.1 Current Status

| Surface | Status |
| --- | --- |
| Design tokens | Expand when UI tokens are inventoried |
| Component patterns | Expand when UI components are cataloged |
| Brand posture | Keep this section grounded in implemented UI reality only |

---

## 7. Frontend

No obvious frontend surface was detected from the current top-level directory layout.

### 7.1 Current Status

| Surface | Status |
| --- | --- |
| UI routing and component inventory | Expand from current source files as the repo is cataloged |
| Desktop shell / browser surface | Record here only if implemented in the repo |

---

## 8. API Layer

DF Local Foundation exposes a single **read-only HTTP health API** (`app/`, FastAPI). It is the
control-plane visibility surface for consumers such as ForgeCommand. It serves ONLY the declared
health surface (`contracts/health.schema.json`) — it never exposes customer data, table contents,
record counts, or any app's domain schema (e.g. `authorforge.*`).

The foundation is the **only** process permitted to connect to its database; the supporting
PostgreSQL instance is for the owning application's data. This API lets other services read coarse
foundation health without any direct database access of their own.

### 8.1 Endpoints

| Method | Path | DB? | Returns |
| --- | --- | --- | --- |
| GET | `/live` | no | Process liveness: `{ service, version, status: "live" }`. Never touches the database. |
| GET | `/health` | yes | `DFLocalHealthStatus` (per `contracts/health.schema.json`): `status` (ready/degraded/unavailable/migrating), `schema_version`, `expected_schema_version`, `migration_required`, `last_error_class`, `started_at`, `db_engine`, `ownership`, `app_mode`. Fails closed: reports `unavailable` when the database is unreachable. |

### 8.2 Implementation

- `app/main.py` — `create_app()` builds the FastAPI app; a lifespan connects the
  `LifecycleManager` once at startup and fails closed (logs, does not crash) if the database is
  down. `/health` flows through the existing `HealthReporter`, so the privacy boundary and JSON
  Schema contract validation are enforced at the serialization layer, not just the data layer.
- `app/__main__.py` — `python -m app` runs uvicorn on `DF_LOCAL_API_HOST:DF_LOCAL_API_PORT`.
- Optional dependency group: `pip install -e ".[api]"` (FastAPI + uvicorn). The core library and
  CLI tools do not require it.

### 8.3 Boundaries

- No mutation endpoints. No authentication is performed here — the surface carries no sensitive
  data and binds to a local address by configuration.
- The response shape is owned by `contracts/health.schema.json`; adding a field requires changing
  the contract first (see §6 Change Control).

---

## 9. Backend

This baseline section records the backend or core runtime surfaces detectable from the repo layout.

### 9.1 Observed Runtime Areas

| Surface | Current interpretation |
| --- | --- |
| Core runtime | Expand from `app/`, `service/`, `cortex_runtime/`, `crates/`, or `src-tauri/` as applicable |
| Delivery posture | Keep this section aligned with implemented code, not roadmap intent |

---

## 10. Ecosystem Integration

This baseline section should be expanded with concrete downstream and upstream dependencies as they are documented.

### 10.1 Current Status

| Surface | Status |
| --- | --- |
| Shared service integrations | Expand as concrete integrations are cataloged |
| Cross-repo boundaries | Keep explicit as this repo's authority boundary is clarified |

---

# Scope

**Document version:** 1.0 (bootstrap scaffold)

Scope and authority boundary of this documentation system.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

## 11. Database Schema

Database, schema, or migration surfaces are present in the repository tree.

### 11.1 Current Status

| Surface | Status |
| --- | --- |
| Table inventory | Expand with real table, column, and constraint definitions |
| Migration contract | Expand if this repo owns migrations or persistent schemas |

---

## 12. AI Integration

AI-adjacent, evaluation, or reasoning surfaces are present in the repo tree.

### 12.1 Current Status

| Surface | Status |
| --- | --- |
| Prompt or model routing docs | Expand as concrete AI surfaces are cataloged |
| Transparency and fallback posture | Record here when the current runtime contract is documented |

---

## 13. Error Handling Contract

Current error-handling documentation is a baseline only.

### 13.1 Baseline Law

- fail closed on missing documentation truth, malformed inputs, and unsupported runtime states
- document real error envelopes here as soon as they are cataloged from code or tests

---

## 14. Testing Infrastructure

This baseline section records only that testing surfaces exist in the repository tree.

### 14.1 Current Status

| Surface | Status |
| --- | --- |
| `tests/` directory | Present |
| QA expansion | Expand with concrete commands, suites, and pre-flight checks as they are cataloged |

---

## 15. Handover / Migration Notes

This repository entered a baseline documentation-protocol migration on 2026-04-03.

### 15.1 Current Migration Note

- modular `doc/system/` was established or normalized to support root `SYSTEM.md`
- further authored expansion is still required for exact APIs, schemas, and runtime contracts

---

# Structure

**Document version:** 1.0 (bootstrap scaffold)

Module/chapter layout and cross-reference rules.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

# Governance

**Document version:** 1.0 (bootstrap scaffold)

Ownership, review, and change-authority boundaries.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

# Change Control

**Document version:** 1.0 (bootstrap scaffold)

Change-control workflow, proposal lifecycle, and audit.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

# Appendices

**Document version:** 1.0 (carry-forward)

Appendices, glossary, and cross-references.

## Unmapped legacy chapters

The following legacy chapters were carried forward but could not be
deterministically mapped to a class-aware slot. Review and place them by
hand:

- `DF Local Foundation — Complete System Reference`
