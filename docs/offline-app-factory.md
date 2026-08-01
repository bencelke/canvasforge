# Offline App Factory

## Product definition

CanvasForge is a **local AI-assisted, manifest-driven frontend compiler and visual app builder** for Microsoft Power Apps Canvas applications.

It generates **tenant-neutral** frontend structures, Power Fx candidates, local previews, and portable **Deployment Kits**. An authorized Power Apps maker later imports or pastes those artifacts into Power Apps Studio and connects SharePoint Lists and Power Automate.

CanvasForge must remain useful without AVD, Power Apps login, military tenant access, Microsoft authentication, Environment Maker rights, or direct Microsoft API access.

Power Apps Studio remains the final compatibility and rendering authority. Connected Microsoft tooling is a **future optional adapter**, not the core architecture.

## Normal pipeline

```
Natural-language prompt or Cursor instruction
        │
        ▼
CanvasForge manifest (YAML)
        │
        ▼
Validation (schema + semantic)
        │
        ▼
Normalized internal representation (AppIR)
        │
        ▼
Local visual preview (advisory)
        │
        ▼
Canvas-compatible frontend output (Candidate Code View)
        │
        ▼
Portable CanvasForge Deployment Kit (.cforge.zip)
        │
        ▼
Approved transfer to work environment
        │
        ▼
Import or Code View paste by authorized maker
        │
        ▼
Connect SharePoint Lists
        │
        ▼
Configure permissions and Power Automate
        │
        ▼
Power Apps Studio validation and publishing
```

## CanvasForge Studio (home / local product)

**CanvasForge Studio** is the local development product. In the near term it is the Python CLI plus Cursor-assisted workflows; later it includes the graphical local preview shell.

### Responsibilities

| Responsibility | Status |
|----------------|--------|
| Project creation | Planned (Phase 3B+) |
| Manifest editing | Done (YAML + Cursor) |
| AI-assisted development through Cursor | Done (workflow) |
| Local validation | Done (CLI) |
| Local visual preview | Planned (Phase 4) |
| Mock data | Partial (examples); expand later |
| Power Fx generation | Partial / expand (Phase 6) |
| Canvas frontend generation | Done (Candidate Code View) |
| Deployment Kit packaging | Planned (Phase 3B) |
| Build diff and reports | Partial (generation reports); expand with kits |

### Non-responsibilities

- Publishing apps to any tenant
- Handling CAC, OAuth, cookies, or tokens
- Connecting production SharePoint or Dataverse
- Claiming local preview equals Power Apps runtime
- Fabricating `.msapp` packages from undocumented assumptions

## Two products, one compiler core

| Product | Where it runs | AI | Network | Role |
|---------|---------------|----|---------|------|
| **CanvasForge Studio** | Home / local PC | Yes (via Cursor / future UI) | Not required | Author, validate, preview, package |
| **CanvasForge Runner** | Work-side offline PC | No | Not required | Open kits, verify checksums, guide paste/import |

Both share the same deterministic compiler foundation: manifest → validation → IR → adapters → reports.

## Preserved compiler foundation

The offline App Factory builds on the existing Phase 1–2 core without rewriting it:

- Manifest loader
- Schema validation
- Semantic validation
- Deterministic planner
- Internal representation (AppIR)
- Control registry and evidence model
- Candidate Code View adapter
- CLI
- Tests

## Tenant neutrality

Outputs must not embed:

- Real military or operational data
- User identities
- Tenant IDs or environment IDs
- Internal URLs
- Credentials, tokens, or CAC material

Examples and mock schemas use **fictional** data only.

## Related documents

- [deployment-kit-architecture.md](deployment-kit-architecture.md)
- [local-preview-architecture.md](local-preview-architecture.md)
- [work-side-runner.md](work-side-runner.md)
- [msapp-experimental-roadmap.md](msapp-experimental-roadmap.md)
- [oroom-reference-strategy.md](oroom-reference-strategy.md)
- [development-roadmap.md](development-roadmap.md)
- [architecture.md](architecture.md)
