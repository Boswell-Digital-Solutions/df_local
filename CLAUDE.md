# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DF Local Foundation is the shared local-first PostgreSQL control surface for Forge ecosystem
applications: disciplined DB lifecycle, canonical migration/schema-version reporting, coarse
health/readiness/status contracts, backup/export/restore doctrine and tooling, and app
registration/compatibility conventions. It is not DataForge (the cloud persistence service), not a
universal business-schema repository, and not a control-plane inspection backdoor.

Canonical reference: `doc/system/` → root `SYSTEM.md` (`bash doc/system/BUILD.sh`). `SYSTEM.md` is
a build artifact; edit the parts, never the artifact.

## Common Commands

```bash
python -m pytest              # run tests (testpaths = tests/, asyncio_mode = auto)
ruff check .                   # lint (target-version py311, line-length 100)
mypy .                          # strict type checking

tools/db-status                # report lifecycle status and migration state
tools/db-backup                 # create a versioned local backup
tools/db-restore                # restore with integrity and compatibility checks
tools/db-export                 # export with metadata envelope

./scripts/context-bundle.sh --list          # list context-bundle sections/presets
./scripts/context-bundle.sh --preset core   # generate a context bundle
```

## Architecture

```
df_local/
  docs/                          # Doctrine and contract documentation
  contracts/                     # JSON Schema contracts
  sql/core/                       # Shared core SQL migrations
  core/
    lifecycle/                   # DB start / stop / status / readiness
    config/                      # Env contract and connection conventions
    health/                      # Health reporting surface
    backup/                      # Backup utilities
    export/                      # Export utilities
  tools/                          # Operator CLI tools (db-status/backup/restore/export)
  tests/                          # Contract and boundary tests
```

## Notes

- **What it does not own:** app business schemas (manuscripts, lore, campaigns, watchlists, etc.),
  customer domain truth, billing/subscription authority, or any canonical AI-memory surface. See
  `docs/privacy-doctrine.md` for the full boundary definition.
- Invariants (see README for the full list): app-local domain truth stays app-owned; this repo
  stays minimal; ForgeCommand sees declared operational state only; NeuronForge Local is not the
  owner of canonical truth; restore/export/backups are versioned and integrity-checked; suspicious
  or ambiguous states fail closed.
- Treat `doc/system/` part files as canonical; rebuild root `SYSTEM.md` after any change, and keep
  this file current if a runtime contract changes.
- Do not invent undocumented APIs, tables, routes, or environment variables.
