# Product Vision

## What CanvasForge is

CanvasForge is a **local, manifest-driven compiler and validation tool** for AI-assisted Microsoft Power Apps Canvas frontend generation.

It helps developers and AI coding agents describe administrative Canvas applications as structured manifests, then produce deterministic, inspectable plans and (in later phases) Studio-compatible frontend artifacts.

CanvasForge is **not** a replacement for Power Apps Studio. Studio remains the final rendering and validation authority.

## Problem

Building responsive administrative Canvas apps in Studio is slow and repetitive:

- Sidebar/header shells
- Dashboards and galleries
- Status badges and workflow progress
- Role-aware navigation
- Form and detail layouts
- Consistent Power Fx patterns

AI assistants can draft layouts and formulas, but unconstrained improvisation risks unsupported controls, invalid properties, unsafe formulas, and non-reviewable packaging.

## Solution

Use a structured intermediate **application manifest** as the source of truth:

1. Describe the app (human or AI-assisted).
2. Validate the manifest (schema + semantic rules).
3. Produce a deterministic generation plan.
4. Later: adapt the plan to supported Power Apps authoring surfaces.
5. Validate and polish in Power Apps Studio.
6. Connect data and workflows only with explicit, reviewed steps.

## V1 focus

- Offline manifest authoring
- Typed validation
- Deterministic planning
- Administrative app layouts
- Responsive frontend structures
- Power Fx generation later
- Code View output later
- Connected Microsoft Canvas tooling later

## V1 non-goals (summary)

- Production data connectors
- Publishing or sharing apps
- Credential handling
- Power Automate flow creation
- SharePoint permission management
- Guaranteeing every Canvas control
- Replacing Studio validation
- Generating arbitrary `.msapp` files without a validated Microsoft-supported path

See [non-goals.md](non-goals.md) for the full list.

## Reference implementation

**O-Room Actions** is the first reference application. It lives under `examples/oroom-actions/` and must not hard-code domain terminology into CanvasForge core packages.

## Principles

1. Manifest first, generation second.
2. Deterministic output from the same manifest.
3. Separate generic UI design from tenant-specific data.
4. Offline by default; connected operations are explicit and approved.
5. Never fabricate unsupported Power Apps behavior.
6. Never handle authentication secrets.
7. Generated artifacts must be inspectable and diffable.
8. Power Apps Studio has the final say.
