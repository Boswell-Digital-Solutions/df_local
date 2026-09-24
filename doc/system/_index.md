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
